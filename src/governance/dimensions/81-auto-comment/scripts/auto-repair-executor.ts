/**
 * =============================================================================
 * SynergyMesh Governance - Auto Repair Executor
 * 自動修復執行器 - 基於診斷報告自動執行修復並創建 PR
 * =============================================================================
 *
 * 功能：
 * - 讀取診斷報告並執行自動修復計劃
 * - 驗證修復是否成功
 * - 自動創建修復提交和 PR
 * - 支援回滾機制
 *
 * =============================================================================
 */

import * as fs from "fs";
import * as path from "path";
import { execSync, spawnSync, SpawnSyncReturns } from "child_process";
import {
  CIDiagnosisEngine,
  DiagnosisReport,
  DiagnosedError,
  FixStep,
} from "./ci-diagnosis-engine";
import { parseCommandSegments } from "./safe-commands";

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

export interface RepairResult {
  success: boolean;
  stepResults: StepResult[];
  totalFixed: number;
  totalFailed: number;
  commitSha?: string;
  prUrl?: string;
  rollbackRequired: boolean;
  summary: string;
}

export interface StepResult {
  step: FixStep;
  success: boolean;
  output: string;
  error?: string;
  duration: number;
}

export interface RepairConfig {
  dryRun: boolean;
  autoCommit: boolean;
  createPR: boolean;
  targetBranch: string;
  maxRetries: number;
  verifyAfterFix: boolean;
  enableRollback: boolean;
}

// =============================================================================
// AUTO REPAIR EXECUTOR CLASS
// =============================================================================

export class AutoRepairExecutor {
  private config: RepairConfig;
  private report: DiagnosisReport | null = null;
  private backupCommit: string | null = null;
  private originalBranch: string | null = null;

  constructor(config?: Partial<RepairConfig>) {
    this.config = {
      dryRun: config?.dryRun ?? false,
      autoCommit: config?.autoCommit ?? true,
      createPR: config?.createPR ?? true,
      targetBranch: config?.targetBranch ?? "main",
      maxRetries: config?.maxRetries ?? 3,
      verifyAfterFix: config?.verifyAfterFix ?? true,
      enableRollback: config?.enableRollback ?? true,
    };
  }

  /**
   * 載入診斷報告
   */
  loadReport(reportPath?: string): DiagnosisReport {
    const possiblePaths = [
      reportPath,
      path.join(process.cwd(), "governance", "dimensions", "81-auto-comment", "output", "diagnosis-report.json"),
      path.join(process.cwd(), "diagnosis-report.json"),
    ].filter(Boolean) as string[];

    for (const p of possiblePaths) {
      if (fs.existsSync(p)) {
        const content = fs.readFileSync(p, "utf-8");
        this.report = JSON.parse(content) as DiagnosisReport;
        console.log(`✅ 載入診斷報告: ${p}`);
        return this.report;
      }
    }

    throw new Error("找不到診斷報告，請先執行 CI 診斷引擎");
  }

  /**
   * 從日誌直接診斷並修復
   */
  async diagnoseAndRepair(logPath?: string): Promise<RepairResult> {
    console.log("=== 開始診斷並修復 ===\n");

    // 執行診斷
    const engine = new CIDiagnosisEngine();
    engine.loadLog(logPath);
    this.report = engine.diagnose();

    // 執行修復
    return this.executeRepair();
  }

  /**
   * 執行修復計劃
   */
  async executeRepair(): Promise<RepairResult> {
    if (!this.report) {
      throw new Error("請先載入診斷報告或執行診斷");
    }

    const { autoFixPlan, errors, summary } = this.report;

    console.log("=== 自動修復執行器 v2.0 ===\n");
    console.log(`診斷報告: ${this.report.id}`);
    console.log(`總錯誤數: ${summary.totalErrors}`);
    console.log(`可自動修復: ${summary.autoFixableErrors}`);
    console.log(`主要問題: ${summary.primaryIssue}\n`);

    // 檢查是否可以自動修復
    if (!autoFixPlan.canAutoFix) {
      console.log("❌ 此問題無法自動修復，需要人工介入\n");
      return this.generateManualFixGuidance(errors);
    }

    // 創建備份點
    if (this.config.enableRollback) {
      this.createBackupPoint();
    }

    // 執行修復步驟
    const stepResults: StepResult[] = [];
    let allSuccess = true;

    for (const step of autoFixPlan.steps) {
      console.log(`\n[步驟 ${step.order}/${autoFixPlan.totalSteps}] ${step.description}`);

      const result = await this.executeStep(step);
      stepResults.push(result);

      if (!result.success) {
        console.log(`❌ 步驟失敗: ${result.error}`);
        allSuccess = false;

        if (step.action !== "verify") {
          // 非驗證步驟失敗，可能需要回滾
          if (this.config.enableRollback && this.backupCommit) {
            console.log("\n⚠️ 執行回滾...");
            this.rollback();
          }
          break;
        }
      } else {
        console.log(`✅ 步驟完成`);
      }
    }

    // 計算結果
    const successfulSteps = stepResults.filter(r => r.success).length;
    const failedSteps = stepResults.filter(r => !r.success).length;

    // 獲取提交信息
    let commitSha: string | undefined;
    let prUrl: string | undefined;

    if (allSuccess && this.config.autoCommit) {
      commitSha = this.getLatestCommitSha();

      if (this.config.createPR) {
        prUrl = await this.createPullRequest();
      }
    }

    // 生成結果
    const result: RepairResult = {
      success: allSuccess,
      stepResults,
      totalFixed: successfulSteps,
      totalFailed: failedSteps,
      commitSha,
      prUrl,
      rollbackRequired: !allSuccess && this.config.enableRollback,
      summary: this.generateSummary(allSuccess, successfulSteps, failedSteps, commitSha, prUrl),
    };

    // 保存結果
    this.saveResult(result);

    return result;
  }

  /**
   * 安全地執行命令，避免 shell 注入
   */
  private runCommandSafely(command: string): { output: string; status: number } {
    const segments = parseCommandSegments(command);
    const outputs: string[] = [];
    let lastStatus = 0;

    for (const args of segments) {
      const result: SpawnSyncReturns<string> = spawnSync(args[0], args.slice(1), {
        encoding: "utf-8",
        timeout: 300000,
        stdio: "pipe",
        cwd: process.cwd(),
      });

      lastStatus = result.status ?? 0;
      if (result.error) {
        throw result.error;
      }
      if (lastStatus !== 0) {
        const commandLabel = args.join(" ");
        const error = new Error(result.stderr || `Command failed: ${commandLabel}`);
        (error as any).status = lastStatus;
        throw error;
      }
      if (result.stdout) {
        outputs.push(result.stdout);
      }
    }

    return { output: outputs.join("\n"), status: lastStatus };
  }

  /**
   * 執行單個修復步驟
   */
  private async executeStep(step: FixStep): Promise<StepResult> {
    const startTime = Date.now();

    if (this.config.dryRun) {
      console.log(`  [DRY RUN] 將執行: ${step.command}`);
      return {
        step,
        success: true,
        output: "[DRY RUN] 跳過執行",
        duration: 0,
      };
    }

    let retries = 0;
    let lastError: string | undefined;

    while (retries < this.config.maxRetries) {
      try {
        const result = this.runCommandSafely(step.command);

        return {
          step,
          success: true,
          output: result.output || "命令執行成功",
          duration: Date.now() - startTime,
        };
      } catch (error: unknown) {
        lastError = error instanceof Error ? error.message : String(error);

        // 某些命令失敗但實際上是成功的（如 eslint --fix 可能返回非零）
        const status = (error as { status?: number }).status;
        if (step.action.includes("fix") && status === 1) {
          // 檢查是否實際有修改
          const gitStatus = execSync("git status --porcelain", { encoding: "utf-8" });
          if (gitStatus.trim()) {
            return {
              step,
              success: true,
              output: "修復命令已執行，有文件被修改",
              duration: Date.now() - startTime,
            };
          }
        }

        retries++;
        if (retries < this.config.maxRetries) {
          console.log(`  ⚠️ 重試 (${retries}/${this.config.maxRetries})...`);
          await this.sleep(1000 * retries);
        }
      }
    }

    return {
      step,
      success: false,
      output: "",
      error: lastError,
      duration: Date.now() - startTime,
    };
  }

  /**
   * 創建備份點
   */
  private createBackupPoint(): void {
    try {
      // 保存當前分支
      this.originalBranch = execSync("git rev-parse --abbrev-ref HEAD", {
        encoding: "utf-8",
      }).trim();

      // 保存當前提交
      this.backupCommit = execSync("git rev-parse HEAD", {
        encoding: "utf-8",
      }).trim();

      // 暫存未提交的更改
      const status = execSync("git status --porcelain", { encoding: "utf-8" });
      if (status.trim()) {
        execSync("git stash push -m 'auto-repair-backup'", { stdio: "pipe" });
        console.log("✅ 已創建備份點並暫存未提交更改");
      } else {
        console.log("✅ 已創建備份點");
      }
    } catch (error) {
      console.log("⚠️ 無法創建備份點，繼續執行...");
    }
  }

  /**
   * 執行回滾
   */
  private rollback(): void {
    if (!this.backupCommit) {
      console.log("⚠️ 無備份點，無法回滾");
      return;
    }

    try {
      // 重置到備份點
      execSync(`git reset --hard ${this.backupCommit}`, { stdio: "pipe" });

      // 恢復暫存的更改
      try {
        execSync("git stash pop", { stdio: "pipe" });
      } catch {
        // 沒有暫存的更改
      }

      console.log("✅ 回滾成功");
    } catch (error) {
      console.log("❌ 回滾失敗:", error);
    }
  }

  /**
   * 獲取最新提交 SHA
   */
  private getLatestCommitSha(): string | undefined {
    try {
      return execSync("git rev-parse HEAD", { encoding: "utf-8" }).trim();
    } catch {
      return undefined;
    }
  }

  /**
   * 創建 Pull Request
   */
  private async createPullRequest(): Promise<string | undefined> {
    if (this.config.dryRun) {
      console.log("[DRY RUN] 將創建 PR");
      return undefined;
    }

    try {
      // 檢查 gh CLI 是否可用
      const ghCheck = spawnSync("gh", ["--version"], { encoding: "utf-8" });
      if (ghCheck.status !== 0) {
        console.log("⚠️ GitHub CLI 不可用，跳過 PR 創建");
        return undefined;
      }

      // 獲取當前分支名
      const currentBranch = execSync("git rev-parse --abbrev-ref HEAD", {
        encoding: "utf-8",
      }).trim();

      // 推送分支
      console.log(`📤 推送分支 ${currentBranch}...`);
      execSync(`git push -u origin ${currentBranch}`, { stdio: "pipe" });

      // 創建 PR
      const prTitle = `[Auto-Fix] 自動修復 CI 錯誤 - ${this.report?.summary.primaryIssue || "多個問題"}`;
      const prBody = this.generatePRBody();

      const prResult = execSync(
        `gh pr create --title "${prTitle}" --body "${prBody}" --base ${this.config.targetBranch}`,
        { encoding: "utf-8" }
      );

      const prUrl = prResult.trim();
      console.log(`✅ PR 已創建: ${prUrl}`);
      return prUrl;
    } catch (error: any) {
      console.log("⚠️ PR 創建失敗:", error.message);
      return undefined;
    }
  }

  /**
   * 生成 PR 描述
   */
  private generatePRBody(): string {
    if (!this.report) return "自動修復 CI 錯誤";

    const { summary, errors, autoFixPlan } = this.report;

    const fixedErrors = errors
      .filter(e => e.autoFixable)
      .map(e => `- \`${e.location.file}:${e.location.line}\`: ${e.message}`)
      .slice(0, 10)
      .join("\\n");

    return `## 🔧 自動修復摘要

**診斷 ID**: \`${this.report.id}\`
**時間**: ${this.report.timestamp}
**主要問題**: ${summary.primaryIssue}

### 📊 統計
- 總錯誤數: ${summary.totalErrors}
- 已自動修復: ${summary.autoFixableErrors}
- 需人工處理: ${summary.manualFixRequired}

### ✅ 已修復的問題
${fixedErrors}

### 🔄 執行的修復步驟
${autoFixPlan.steps.map(s => `${s.order}. ${s.description}`).join("\\n")}

### ⚠️ 驗證清單
- [ ] 確認修復符合預期
- [ ] 檢查相關測試通過
- [ ] 審查代碼變更

---
*此 PR 由 [Auto-Repair Executor](./governance/dimensions/81-auto-comment) 自動生成*`;
  }

  /**
   * 生成人工修復指導
   */
  private generateManualFixGuidance(errors: DiagnosedError[]): RepairResult {
    console.log("\n=== 人工修復指導 ===\n");

    const manualErrors = errors.filter(e => !e.autoFixable);

    manualErrors.forEach((error, index) => {
      console.log(`[${index + 1}] ${error.type.toUpperCase()} 錯誤`);
      console.log(`    位置: ${error.location.file}:${error.location.line}`);
      console.log(`    訊息: ${error.message}`);
      console.log(`    建議: ${error.suggestedFix.description}`);

      if (error.suggestedFix.codeChange) {
        console.log(`    原始代碼: ${error.suggestedFix.codeChange.originalCode}`);
        console.log(`    建議修改: ${error.suggestedFix.codeChange.fixedCode}`);
      }

      console.log(`    驗證命令: ${error.suggestedFix.verification.join(", ")}`);
      console.log("");
    });

    // 生成人工修復報告
    const guidanceReport = {
      type: "manual-fix-guidance",
      timestamp: new Date().toISOString(),
      errors: manualErrors.map(e => ({
        file: e.location.file,
        line: e.location.line,
        type: e.type,
        message: e.message,
        suggestion: e.suggestedFix.description,
        verification: e.suggestedFix.verification,
      })),
    };

    // 保存指導報告
    const outputPath = path.join(
      process.cwd(),
      "governance",
      "dimensions",
      "81-auto-comment",
      "output",
      "manual-fix-guidance.json"
    );
    fs.writeFileSync(outputPath, JSON.stringify(guidanceReport, null, 2));
    console.log(`📋 人工修復指導已保存: ${outputPath}`);

    return {
      success: false,
      stepResults: [],
      totalFixed: 0,
      totalFailed: manualErrors.length,
      rollbackRequired: false,
      summary: `需要人工修復 ${manualErrors.length} 個錯誤，詳見 ${outputPath}`,
    };
  }

  /**
   * 生成結果摘要
   */
  private generateSummary(
    success: boolean,
    fixed: number,
    failed: number,
    commitSha?: string,
    prUrl?: string
  ): string {
    const lines = [
      success ? "✅ 自動修復成功完成" : "❌ 自動修復部分失敗",
      `   成功步驟: ${fixed}`,
      `   失敗步驟: ${failed}`,
    ];

    if (commitSha) {
      lines.push(`   提交 SHA: ${commitSha}`);
    }

    if (prUrl) {
      lines.push(`   PR URL: ${prUrl}`);
    }

    return lines.join("\n");
  }

  /**
   * 保存修復結果
   */
  private saveResult(result: RepairResult): void {
    const outputPath = path.join(
      process.cwd(),
      "governance",
      "dimensions",
      "81-auto-comment",
      "output",
      "repair-result.json"
    );

    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    console.log(`\n📄 修復結果已保存: ${outputPath}`);
  }

  /**
   * 睡眠輔助函數
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// =============================================================================
// QUICK FIX FUNCTIONS (直接修復特定類型的錯誤)
// =============================================================================

export async function quickFixLint(): Promise<boolean> {
  console.log("🔧 快速修復 Lint 錯誤...");
  try {
    execSync("npx eslint --fix .", { stdio: "inherit" });
    execSync("npx prettier --write .", { stdio: "inherit" });
    console.log("✅ Lint 修復完成");
    return true;
  } catch {
    console.log("⚠️ 部分 Lint 錯誤需要手動修復");
    return false;
  }
}

export async function quickFixFormat(): Promise<boolean> {
  console.log("🔧 快速修復格式問題...");
  try {
    execSync("npx prettier --write .", { stdio: "inherit" });
    console.log("✅ 格式修復完成");
    return true;
  } catch (error) {
    console.log("❌ 格式修復失敗:", error);
    return false;
  }
}

export async function quickFixDependencies(): Promise<boolean> {
  console.log("🔧 快速修復依賴問題...");
  try {
    execSync("rm -rf node_modules package-lock.json", { stdio: "pipe" });
    execSync("npm install", { stdio: "inherit" });
    console.log("✅ 依賴修復完成");
    return true;
  } catch (error) {
    console.log("❌ 依賴修復失敗:", error);
    return false;
  }
}

export async function quickFixSecurity(): Promise<boolean> {
  console.log("🔧 快速修復安全漏洞...");
  try {
    execSync("npm audit fix", { stdio: "inherit" });
    console.log("✅ 安全修復完成");
    return true;
  } catch {
    console.log("⚠️ 部分安全漏洞需要手動修復");
    return false;
  }
}

// =============================================================================
// CLI INTERFACE
// =============================================================================

function parseArgs(): {
  reportPath?: string;
  logPath?: string;
  dryRun: boolean;
  noPR: boolean;
  quickFix?: string;
} {
  const args = process.argv.slice(2);
  const result: {
    reportPath?: string;
    logPath?: string;
    dryRun: boolean;
    noPR: boolean;
    quickFix?: string;
  } = { dryRun: false, noPR: false };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--report":
      case "-r":
        result.reportPath = args[++i];
        break;
      case "--log":
      case "-l":
        result.logPath = args[++i];
        break;
      case "--dry-run":
        result.dryRun = true;
        break;
      case "--no-pr":
        result.noPR = true;
        break;
      case "--quick-fix":
      case "-q":
        result.quickFix = args[++i];
        break;
    }
  }

  return result;
}

async function main(): Promise<void> {
  const args = parseArgs();

  // 快速修復模式
  if (args.quickFix) {
    let success = false;
    switch (args.quickFix) {
      case "lint":
        success = await quickFixLint();
        break;
      case "format":
        success = await quickFixFormat();
        break;
      case "deps":
      case "dependencies":
        success = await quickFixDependencies();
        break;
      case "security":
        success = await quickFixSecurity();
        break;
      default:
        console.log(`未知的快速修復類型: ${args.quickFix}`);
        console.log("可用類型: lint, format, deps, security");
        process.exit(1);
    }
    process.exit(success ? 0 : 1);
  }

  // 完整修復模式
  const executor = new AutoRepairExecutor({
    dryRun: args.dryRun,
    createPR: !args.noPR,
  });

  let result: RepairResult;

  if (args.logPath) {
    // 從日誌直接診斷並修復
    result = await executor.diagnoseAndRepair(args.logPath);
  } else {
    // 從報告修復
    executor.loadReport(args.reportPath);
    result = await executor.executeRepair();
  }

  console.log("\n" + result.summary);
  process.exit(result.success ? 0 : 1);
}

// 如果直接運行則執行 main
if (require.main === module) {
  main().catch(error => {
    console.error("修復執行失敗:", error);
    process.exit(1);
  });
}
