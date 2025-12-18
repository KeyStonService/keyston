/**
 * =============================================================================
 * SynergyMesh Governance - CI Diagnosis Engine
 * 智能 CI 診斷引擎 - 精確定位問題根源並提供一次性修復方案
 * =============================================================================
 *
 * 功能：
 * - 深度分析 CI 日誌，精確定位錯誤位置（文件、行號、列號）
 * - 智能分類錯誤類型並提供具體修復方案
 * - 生成可執行的修復指令，支援一次性解決問題
 * - 整合到 Auto-Fix Bot 系統，支援自動創建修復 PR
 *
 * =============================================================================
 */

import * as fs from "fs";
import * as path from "path";
import { execSync, spawnSync } from "child_process";

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

export interface ErrorLocation {
  file: string;
  line: number;
  column?: number;
  endLine?: number;
  endColumn?: number;
}

export interface DiagnosedError {
  id: string;
  type: ErrorType;
  severity: "critical" | "high" | "medium" | "low";
  category: ErrorCategory;
  location: ErrorLocation;
  message: string;
  rawOutput: string;
  suggestedFix: FixSuggestion;
  autoFixable: boolean;
  relatedErrors?: string[];
}

export interface FixSuggestion {
  description: string;
  commands: string[];
  codeChange?: CodeChange;
  verification: string[];
  estimatedImpact: "breaking" | "safe" | "review-required";
}

export interface CodeChange {
  file: string;
  lineStart: number;
  lineEnd: number;
  originalCode: string;
  fixedCode: string;
  explanation: string;
}

export interface DiagnosisReport {
  id: string;
  timestamp: string;
  workflow: string;
  commit: string;
  branch: string;
  status: "success" | "failure" | "partial";
  summary: DiagnosisSummary;
  errors: DiagnosedError[];
  autoFixPlan: AutoFixPlan;
  metadata: DiagnosisMetadata;
}

export interface DiagnosisSummary {
  totalErrors: number;
  criticalErrors: number;
  autoFixableErrors: number;
  manualFixRequired: number;
  estimatedFixTime: string;
  primaryIssue: string;
}

export interface AutoFixPlan {
  canAutoFix: boolean;
  steps: FixStep[];
  totalSteps: number;
  requiresReview: boolean;
  rollbackPlan: string[];
}

export interface FixStep {
  order: number;
  action: string;
  command: string;
  targetFiles: string[];
  description: string;
  rollback?: string;
}

export interface DiagnosisMetadata {
  engineVersion: string;
  analysisTime: number;
  logSize: number;
  patternsMatched: number;
}

type ErrorType =
  | "typescript"
  | "eslint"
  | "prettier"
  | "test"
  | "build"
  | "security"
  | "dependency"
  | "yaml"
  | "markdown"
  | "docker"
  | "permission"
  | "network"
  | "configuration"
  | "unknown";

type ErrorCategory =
  | "syntax"
  | "type"
  | "lint"
  | "format"
  | "test"
  | "build"
  | "security"
  | "runtime"
  | "configuration";

// =============================================================================
// ERROR PATTERNS DATABASE
// =============================================================================

interface ErrorPattern {
  type: ErrorType;
  category: ErrorCategory;
  patterns: RegExp[];
  severity: "critical" | "high" | "medium" | "low";
  autoFixable: boolean;
  fixStrategy: string;
  fixCommands?: string[];
  locationExtractor: (match: RegExpMatchArray, line: string) => ErrorLocation | null;
}

const ERROR_PATTERNS: ErrorPattern[] = [
  // TypeScript Errors
  {
    type: "typescript",
    category: "type",
    patterns: [
      /(.+\.tsx?)\((\d+),(\d+)\): error (TS\d+): (.+)/,
      /(.+\.tsx?):(\d+):(\d+) - error (TS\d+): (.+)/,
      /error (TS\d+): (.+) in (.+\.tsx?):(\d+):(\d+)/,
    ],
    severity: "high",
    autoFixable: false,
    fixStrategy: "manual-type-fix",
    locationExtractor: (match, line) => {
      if (match[1] && match[2]) {
        return {
          file: match[1],
          line: parseInt(match[2]),
          column: match[3] ? parseInt(match[3]) : undefined,
        };
      }
      return null;
    },
  },
  // ESLint Errors
  {
    type: "eslint",
    category: "lint",
    patterns: [
      /(.+\.(?:js|jsx|ts|tsx)):(\d+):(\d+): (.+) \[(.+)\]/,
      /✖ (\d+) problems? \((\d+) errors?, (\d+) warnings?\)/,
      /(.+\.(?:js|jsx|ts|tsx))\s+(\d+):(\d+)\s+error\s+(.+?)\s+(\S+)$/m,
    ],
    severity: "medium",
    autoFixable: true,
    fixStrategy: "eslint-fix",
    fixCommands: ["npx eslint --fix .", "npx eslint --fix --ext .ts,.tsx,.js,.jsx ."],
    locationExtractor: (match, line) => {
      if (match[1] && match[2]) {
        return {
          file: match[1],
          line: parseInt(match[2]),
          column: match[3] ? parseInt(match[3]) : undefined,
        };
      }
      return null;
    },
  },
  // Prettier Errors
  {
    type: "prettier",
    category: "format",
    patterns: [
      /\[warn\] (.+\.(?:js|jsx|ts|tsx|json|yaml|yml|md))/,
      /Code style issues found in (.+)/,
      /Forgot to run Prettier/i,
      /checking formatting\.+\[warn\]/,
    ],
    severity: "low",
    autoFixable: true,
    fixStrategy: "prettier-fix",
    fixCommands: ["npx prettier --write .", 'npx prettier --write "**/*.{ts,tsx,js,jsx,json,yaml,yml,md}"'],
    locationExtractor: (match, line) => {
      if (match[1]) {
        return { file: match[1], line: 1 };
      }
      return null;
    },
  },
  // Test Failures
  {
    type: "test",
    category: "test",
    patterns: [
      /FAIL\s+(.+\.(?:test|spec)\.(?:js|jsx|ts|tsx))/,
      /✕\s+(.+?) \((\d+) ms\)/,
      /● (.+?) › (.+)/,
      /Expected: (.+)\s+Received: (.+)/,
      /at (.+\.(?:test|spec)\.(?:js|jsx|ts|tsx)):(\d+):(\d+)/,
    ],
    severity: "high",
    autoFixable: false,
    fixStrategy: "manual-test-fix",
    locationExtractor: (match, line) => {
      if (match[1] && match[1].includes(".")) {
        const lineMatch = line.match(/:(\d+):(\d+)/);
        return {
          file: match[1],
          line: lineMatch ? parseInt(lineMatch[1]) : 1,
          column: lineMatch ? parseInt(lineMatch[2]) : undefined,
        };
      }
      return null;
    },
  },
  // Build Errors
  {
    type: "build",
    category: "build",
    patterns: [
      /error: build failed/i,
      /Build error occurred/,
      /Module not found: Error: Can't resolve '(.+)'/,
      /Failed to compile/,
      /ERROR in (.+\.(?:js|jsx|ts|tsx))/,
    ],
    severity: "critical",
    autoFixable: false,
    fixStrategy: "manual-build-fix",
    locationExtractor: (match, line) => {
      const fileMatch = line.match(/in (.+\.(?:js|jsx|ts|tsx|json)):?(\d+)?/);
      if (fileMatch) {
        return {
          file: fileMatch[1],
          line: fileMatch[2] ? parseInt(fileMatch[2]) : 1,
        };
      }
      return null;
    },
  },
  // Dependency Errors
  {
    type: "dependency",
    category: "runtime",
    patterns: [
      /npm ERR! (.+)/,
      /Module not found/,
      /Cannot find module '(.+)'/,
      /peer dep missing: (.+)/,
      /ERESOLVE unable to resolve dependency tree/,
    ],
    severity: "high",
    autoFixable: true,
    fixStrategy: "dependency-fix",
    fixCommands: ["npm ci", "npm install", "npm audit fix"],
    locationExtractor: () => ({ file: "package.json", line: 1 }),
  },
  // YAML Errors
  {
    type: "yaml",
    category: "syntax",
    patterns: [
      /yaml: (.+) at line (\d+)/i,
      /YAMLException: (.+) at line (\d+)/,
      /(.+\.ya?ml):\s*(\d+):\s*error/i,
    ],
    severity: "medium",
    autoFixable: true,
    fixStrategy: "yaml-fix",
    fixCommands: ["npx yaml-lint --fix .", "npx prettier --write '**/*.{yaml,yml}'"],
    locationExtractor: (match, line) => {
      const fileMatch = line.match(/(.+\.ya?ml)/);
      const lineMatch = line.match(/line (\d+)/i);
      return {
        file: fileMatch ? fileMatch[1] : "unknown.yaml",
        line: lineMatch ? parseInt(lineMatch[1]) : 1,
      };
    },
  },
  // Security Vulnerabilities
  {
    type: "security",
    category: "security",
    patterns: [
      /(\d+) vulnerabilities? \((\d+) (critical|high|moderate|low)/,
      /CVE-\d{4}-\d+/,
      /GHSA-\w+-\w+-\w+/,
      /Security vulnerability found/i,
    ],
    severity: "critical",
    autoFixable: true,
    fixStrategy: "security-fix",
    fixCommands: ["npm audit fix", "npm audit fix --force"],
    locationExtractor: () => ({ file: "package-lock.json", line: 1 }),
  },
  // Permission Errors
  {
    type: "permission",
    category: "runtime",
    patterns: [
      /EACCES: permission denied/,
      /Permission denied/i,
      /Error: EACCES/,
    ],
    severity: "high",
    autoFixable: false,
    fixStrategy: "permission-fix",
    locationExtractor: (match, line) => {
      const fileMatch = line.match(/'(.+)'/);
      return { file: fileMatch ? fileMatch[1] : "unknown", line: 1 };
    },
  },
  // Docker Errors
  {
    type: "docker",
    category: "build",
    patterns: [
      /docker: Error/i,
      /failed to solve: (.+)/,
      /ERROR \[.+\] (.+)/,
      /Dockerfile:(\d+)/,
    ],
    severity: "high",
    autoFixable: false,
    fixStrategy: "docker-fix",
    locationExtractor: (match, line) => {
      const lineMatch = line.match(/Dockerfile:(\d+)/);
      return {
        file: "Dockerfile",
        line: lineMatch ? parseInt(lineMatch[1]) : 1,
      };
    },
  },
  // Markdown Lint Errors
  {
    type: "markdown",
    category: "format",
    patterns: [
      /(.+\.md):(\d+):?(\d+)? (MD\d{3})/,
      /(.+\.md):(\d+) (MD\d{3})\/\w+/,
    ],
    severity: "low",
    autoFixable: true,
    fixStrategy: "markdown-fix",
    fixCommands: ["npx markdownlint --fix '**/*.md'", "npx markdownlint-cli2-fix '**/*.md'"],
    locationExtractor: (match, line) => ({
      file: match[1],
      line: parseInt(match[2]),
      column: match[3] ? parseInt(match[3]) : undefined,
    }),
  },
];

// =============================================================================
// CI DIAGNOSIS ENGINE CLASS
// =============================================================================

export class CIDiagnosisEngine {
  private logContent: string = "";
  private workflowContext: {
    workflow: string;
    runId: string;
    commit: string;
    branch: string;
  };

  constructor(context?: { workflow?: string; runId?: string; commit?: string; branch?: string }) {
    this.workflowContext = {
      workflow: context?.workflow || process.env.GITHUB_WORKFLOW || "Unknown",
      runId: context?.runId || process.env.GITHUB_RUN_ID || "unknown",
      commit: context?.commit || process.env.GITHUB_SHA || "unknown",
      branch: context?.branch || process.env.GITHUB_REF_NAME || "unknown",
    };
  }

  /**
   * 載入 CI 日誌
   */
  loadLog(logPath?: string): void {
    const possiblePaths = [
      logPath,
      path.join(process.cwd(), "ci.log"),
      path.join(process.cwd(), "artifacts", "logs", "ci.log"),
      path.join(process.cwd(), ".github", "logs", "ci.log"),
    ].filter(Boolean) as string[];

    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        this.logContent = fs.readFileSync(p, "utf-8");
        console.log(`✅ 載入 CI 日誌: ${p} (${this.logContent.length} bytes)`);
        return;
      }
    }

    // 嘗試從 GitHub Actions 環境變數獲取
    if (process.env.CI_LOG_CONTENT) {
      this.logContent = process.env.CI_LOG_CONTENT;
      return;
    }

    // 嘗試捕獲最近的 CI 輸出
    this.logContent = this.captureRecentCIOutput();
  }

  /**
   * 捕獲最近的 CI 輸出（用於即時診斷）
   */
  private captureRecentCIOutput(): string {
    try {
      // 嘗試獲取 git 相關的錯誤信息
      const gitStatus = spawnSync("git", ["status", "--porcelain"], { encoding: "utf-8" });

      // 嘗試運行 npm/yarn 檢查
      const npmCheck = spawnSync("npm", ["run", "lint", "--", "--quiet"], {
        encoding: "utf-8",
        timeout: 30000,
      });

      const output = [
        "=== CI Output Capture ===",
        gitStatus.stdout || "",
        gitStatus.stderr || "",
        npmCheck.stdout || "",
        npmCheck.stderr || "",
      ].join("\n");

      return output || "無法獲取 CI 輸出，請提供 ci.log 文件。";
    } catch {
      return "CI 輸出捕獲失敗。";
    }
  }

  /**
   * 設置日誌內容（用於直接傳入日誌）
   */
  setLogContent(content: string): void {
    this.logContent = content;
  }

  /**
   * 執行完整診斷
   */
  diagnose(): DiagnosisReport {
    const startTime = Date.now();
    const errors: DiagnosedError[] = [];
    let patternsMatched = 0;

    // 逐行分析日誌
    const lines = this.logContent.split("\n");

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const context = lines.slice(Math.max(0, i - 3), Math.min(lines.length, i + 4)).join("\n");

      for (const pattern of ERROR_PATTERNS) {
        for (const regex of pattern.patterns) {
          const match = line.match(regex);
          if (match) {
            patternsMatched++;
            const location = pattern.locationExtractor(match, line);

            if (location) {
              const errorId = `err-${errors.length + 1}-${pattern.type}`;
              const error = this.createDiagnosedError(
                errorId,
                pattern,
                location,
                line,
                context,
                match
              );

              // 避免重複錯誤
              if (!errors.some(e =>
                e.location.file === error.location.file &&
                e.location.line === error.location.line &&
                e.type === error.type
              )) {
                errors.push(error);
              }
            }
          }
        }
      }
    }

    // 生成診斷報告
    const report = this.generateReport(errors, startTime, patternsMatched);
    return report;
  }

  /**
   * 創建診斷錯誤對象
   */
  private createDiagnosedError(
    id: string,
    pattern: ErrorPattern,
    location: ErrorLocation,
    line: string,
    context: string,
    match: RegExpMatchArray
  ): DiagnosedError {
    const suggestedFix = this.generateFixSuggestion(pattern, location, line, context);

    return {
      id,
      type: pattern.type,
      severity: pattern.severity,
      category: pattern.category,
      location,
      message: this.extractErrorMessage(line, pattern.type),
      rawOutput: context,
      suggestedFix,
      autoFixable: pattern.autoFixable,
    };
  }

  /**
   * 提取錯誤消息
   */
  private extractErrorMessage(line: string, type: ErrorType): string {
    // 移除 ANSI 顏色代碼
    const cleanLine = line.replace(/\x1B\[[0-9;]*m/g, "").trim();

    // 根據類型提取關鍵信息
    switch (type) {
      case "typescript":
        const tsMatch = cleanLine.match(/error (TS\d+): (.+)/);
        return tsMatch ? `${tsMatch[1]}: ${tsMatch[2]}` : cleanLine;

      case "eslint":
        const eslintMatch = cleanLine.match(/error\s+(.+?)\s+(\S+)$/);
        return eslintMatch ? `${eslintMatch[2]}: ${eslintMatch[1]}` : cleanLine;

      case "test":
        return cleanLine.includes("●") ? cleanLine.split("●")[1]?.trim() || cleanLine : cleanLine;

      default:
        return cleanLine.substring(0, 200);
    }
  }

  /**
   * 生成修復建議
   */
  private generateFixSuggestion(
    pattern: ErrorPattern,
    location: ErrorLocation,
    line: string,
    context: string
  ): FixSuggestion {
    const baseCommands = pattern.fixCommands || [];
    const commands: string[] = [];
    const verification: string[] = [];

    switch (pattern.fixStrategy) {
      case "eslint-fix":
        commands.push(`npx eslint --fix "${location.file}"`);
        verification.push(`npx eslint "${location.file}"`);
        break;

      case "prettier-fix":
        commands.push(`npx prettier --write "${location.file}"`);
        verification.push(`npx prettier --check "${location.file}"`);
        break;

      case "yaml-fix":
        commands.push(`npx prettier --write "${location.file}"`);
        verification.push(`npx yaml-lint "${location.file}"`);
        break;

      case "markdown-fix":
        commands.push(`npx markdownlint --fix "${location.file}"`);
        verification.push(`npx markdownlint "${location.file}"`);
        break;

      case "dependency-fix":
        commands.push("rm -rf node_modules package-lock.json");
        commands.push("npm install");
        verification.push("npm ci");
        break;

      case "security-fix":
        commands.push("npm audit fix");
        verification.push("npm audit");
        break;

      default:
        commands.push(...baseCommands);
        verification.push("npm run lint", "npm run build", "npm test");
    }

    // 嘗試生成代碼修改建議
    let codeChange: CodeChange | undefined;
    if (pattern.type === "typescript" || pattern.type === "eslint") {
      codeChange = this.suggestCodeChange(location, line, context, pattern.type);
    }

    return {
      description: this.getFixDescription(pattern.type, location),
      commands,
      codeChange,
      verification,
      estimatedImpact: pattern.autoFixable ? "safe" : "review-required",
    };
  }

  /**
   * 建議代碼修改
   */
  private suggestCodeChange(
    location: ErrorLocation,
    errorLine: string,
    context: string,
    type: ErrorType
  ): CodeChange | undefined {
    if (!fs.existsSync(location.file)) {
      return undefined;
    }

    try {
      const fileContent = fs.readFileSync(location.file, "utf-8");
      const lines = fileContent.split("\n");
      const targetLine = lines[location.line - 1];

      if (!targetLine) return undefined;

      let fixedCode = targetLine;
      let explanation = "";

      // 根據錯誤類型建議修復
      if (type === "eslint") {
        // 常見 ESLint 修復
        if (errorLine.includes("no-unused-vars")) {
          fixedCode = `// eslint-disable-next-line @typescript-eslint/no-unused-vars\n${targetLine}`;
          explanation = "添加 ESLint 禁用註釋（建議刪除未使用的變數）";
        } else if (errorLine.includes("prefer-const")) {
          fixedCode = targetLine.replace(/\blet\b/, "const");
          explanation = "將 let 改為 const（變數未被重新賦值）";
        } else if (errorLine.includes("semi")) {
          fixedCode = targetLine.endsWith(";") ? targetLine.slice(0, -1) : `${targetLine};`;
          explanation = "修正分號問題";
        }
      } else if (type === "typescript") {
        // TypeScript 類型建議
        if (errorLine.includes("TS2345") || errorLine.includes("TS2339")) {
          explanation = "類型不匹配，需要檢查函數參數或屬性類型";
        } else if (errorLine.includes("TS7006")) {
          // 隱式 any
          fixedCode = targetLine.replace(/\((\w+)\)/, "(param: unknown)");
          explanation = "添加明確的類型註釋以避免隱式 any";
        }
      }

      if (fixedCode !== targetLine) {
        return {
          file: location.file,
          lineStart: location.line,
          lineEnd: location.line,
          originalCode: targetLine,
          fixedCode,
          explanation,
        };
      }
    } catch {
      // 忽略文件讀取錯誤
    }

    return undefined;
  }

  /**
   * 獲取修復描述
   */
  private getFixDescription(type: ErrorType, location: ErrorLocation): string {
    const descriptions: Record<ErrorType, string> = {
      typescript: `修復 ${location.file}:${location.line} 的 TypeScript 類型錯誤`,
      eslint: `修復 ${location.file}:${location.line} 的 ESLint 錯誤`,
      prettier: `格式化 ${location.file} 以符合 Prettier 規範`,
      test: `修復 ${location.file} 中失敗的測試案例`,
      build: `解決 ${location.file} 的建置錯誤`,
      security: "修復安全漏洞",
      dependency: "解決依賴問題",
      yaml: `修復 ${location.file} 的 YAML 語法錯誤`,
      markdown: `修復 ${location.file} 的 Markdown 格式問題`,
      docker: `修復 Dockerfile 第 ${location.line} 行的錯誤`,
      permission: `解決 ${location.file} 的權限問題`,
      network: "解決網絡連接問題",
      configuration: "修復配置錯誤",
      unknown: "診斷並修復未知錯誤",
    };

    return descriptions[type];
  }

  /**
   * 生成診斷報告
   */
  private generateReport(
    errors: DiagnosedError[],
    startTime: number,
    patternsMatched: number
  ): DiagnosisReport {
    const criticalErrors = errors.filter(e => e.severity === "critical").length;
    const autoFixableErrors = errors.filter(e => e.autoFixable).length;

    // 生成自動修復計劃
    const autoFixPlan = this.generateAutoFixPlan(errors);

    // 確定主要問題
    const primaryIssue = this.determinePrimaryIssue(errors);

    return {
      id: `diag-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
      timestamp: new Date().toISOString(),
      workflow: this.workflowContext.workflow,
      commit: this.workflowContext.commit,
      branch: this.workflowContext.branch,
      status: errors.length === 0 ? "success" : autoFixableErrors === errors.length ? "partial" : "failure",
      summary: {
        totalErrors: errors.length,
        criticalErrors,
        autoFixableErrors,
        manualFixRequired: errors.length - autoFixableErrors,
        estimatedFixTime: this.estimateFixTime(errors),
        primaryIssue,
      },
      errors,
      autoFixPlan,
      metadata: {
        engineVersion: "2.0.0",
        analysisTime: Date.now() - startTime,
        logSize: this.logContent.length,
        patternsMatched,
      },
    };
  }

  /**
   * 生成自動修復計劃
   */
  private generateAutoFixPlan(errors: DiagnosedError[]): AutoFixPlan {
    const autoFixableErrors = errors.filter(e => e.autoFixable);

    if (autoFixableErrors.length === 0) {
      return {
        canAutoFix: false,
        steps: [],
        totalSteps: 0,
        requiresReview: true,
        rollbackPlan: ["git reset --hard HEAD"],
      };
    }

    // 按優先級排序並生成步驟
    const sortedErrors = [...autoFixableErrors].sort((a, b) => {
      const priority: Record<string, number> = {
        critical: 0,
        high: 1,
        medium: 2,
        low: 3,
      };
      return priority[a.severity] - priority[b.severity];
    });

    // 合併相同類型的修復
    const fixStepsByType = new Map<ErrorType, FixStep>();

    sortedErrors.forEach((error, index) => {
      const existing = fixStepsByType.get(error.type);
      if (existing) {
        existing.targetFiles.push(error.location.file);
      } else {
        fixStepsByType.set(error.type, {
          order: index + 1,
          action: `fix-${error.type}`,
          command: error.suggestedFix.commands[0] || "",
          targetFiles: [error.location.file],
          description: `修復所有 ${error.type} 錯誤`,
          rollback: `git checkout -- ${error.location.file}`,
        });
      }
    });

    const steps = Array.from(fixStepsByType.values())
      .map((step, index) => ({ ...step, order: index + 1 }));

    // 添加驗證步驟
    steps.push({
      order: steps.length + 1,
      action: "verify",
      command: "npm run lint && npm run build && npm test",
      targetFiles: [],
      description: "驗證所有修復是否成功",
    });

    // 添加提交步驟
    steps.push({
      order: steps.length + 1,
      action: "commit",
      command: 'git add . && git commit -m "[auto-fix] 自動修復 CI 錯誤 (81-auto-comment)"',
      targetFiles: [],
      description: "提交所有修復",
      rollback: "git reset --soft HEAD~1",
    });

    return {
      canAutoFix: true,
      steps,
      totalSteps: steps.length,
      requiresReview: autoFixableErrors.some(e => e.severity === "critical"),
      rollbackPlan: [
        "git stash push -m 'auto-fix-backup'",
        "git reset --hard HEAD~1",
        "git stash pop (如需恢復修改)",
      ],
    };
  }

  /**
   * 確定主要問題
   */
  private determinePrimaryIssue(errors: DiagnosedError[]): string {
    if (errors.length === 0) return "無錯誤";

    // 優先顯示最嚴重的錯誤
    const criticalError = errors.find(e => e.severity === "critical");
    if (criticalError) {
      return `${criticalError.type}: ${criticalError.message}`;
    }

    // 統計錯誤類型
    const typeCounts = new Map<ErrorType, number>();
    errors.forEach(e => {
      typeCounts.set(e.type, (typeCounts.get(e.type) || 0) + 1);
    });

    // 找出最常見的錯誤類型
    let maxType: ErrorType = "unknown";
    let maxCount = 0;
    typeCounts.forEach((count, type) => {
      if (count > maxCount) {
        maxCount = count;
        maxType = type;
      }
    });

    return `${maxCount} 個 ${maxType} 錯誤`;
  }

  /**
   * 估算修復時間
   */
  private estimateFixTime(errors: DiagnosedError[]): string {
    const autoFixable = errors.filter(e => e.autoFixable).length;
    const manual = errors.length - autoFixable;

    if (errors.length === 0) return "0 分鐘";

    // 自動修復約 1 分鐘，手動修復約 10-30 分鐘
    const autoTime = autoFixable * 1;
    const manualTime = manual * 15;
    const total = autoTime + manualTime;

    if (total < 5) return "< 5 分鐘";
    if (total < 30) return `約 ${Math.ceil(total / 5) * 5} 分鐘`;
    if (total < 60) return `約 ${Math.ceil(total / 10) * 10} 分鐘`;
    return `約 ${Math.ceil(total / 60)} 小時`;
  }
}

// =============================================================================
// CLI INTERFACE
// =============================================================================

function parseArgs(): { logPath?: string; outputPath?: string; format?: string } {
  const args = process.argv.slice(2);
  const result: { logPath?: string; outputPath?: string; format?: string } = {};

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--log":
      case "-l":
        result.logPath = args[++i];
        break;
      case "--output":
      case "-o":
        result.outputPath = args[++i];
        break;
      case "--format":
      case "-f":
        result.format = args[++i];
        break;
    }
  }

  return result;
}

async function main(): Promise<void> {
  console.log("=== CI Diagnosis Engine v2.0 ===\n");

  const args = parseArgs();

  const engine = new CIDiagnosisEngine();
  engine.loadLog(args.logPath);

  const report = engine.diagnose();

  // 輸出報告
  const outputPath = args.outputPath || path.join(
    process.cwd(),
    "governance",
    "dimensions",
    "81-auto-comment",
    "output",
    "diagnosis-report.json"
  );

  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2), "utf-8");
  console.log(`\n✅ 診斷報告已生成: ${outputPath}`);

  // 輸出摘要
  console.log("\n=== 診斷摘要 ===");
  console.log(`狀態: ${report.status}`);
  console.log(`總錯誤數: ${report.summary.totalErrors}`);
  console.log(`嚴重錯誤: ${report.summary.criticalErrors}`);
  console.log(`可自動修復: ${report.summary.autoFixableErrors}`);
  console.log(`需手動修復: ${report.summary.manualFixRequired}`);
  console.log(`主要問題: ${report.summary.primaryIssue}`);
  console.log(`預估修復時間: ${report.summary.estimatedFixTime}`);

  if (report.autoFixPlan.canAutoFix) {
    console.log("\n=== 自動修復計劃 ===");
    report.autoFixPlan.steps.forEach(step => {
      console.log(`${step.order}. ${step.description}`);
      console.log(`   命令: ${step.command}`);
    });
  }

  // 設置退出碼
  process.exit(report.summary.totalErrors > 0 ? 1 : 0);
}

// 如果直接運行則執行 main
if (require.main === module) {
  main().catch(error => {
    console.error("診斷失敗:", error);
    process.exit(1);
  });
}
