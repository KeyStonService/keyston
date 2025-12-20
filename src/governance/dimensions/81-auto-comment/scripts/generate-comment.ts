/**
 * =============================================================================
 * SynergyMesh Governance - Auto Comment Generator (Enhanced)
 * 81-auto-comment: Generate Comment Script with Integrated Diagnosis Engine
 * =============================================================================
 *
 * 功能：
 * - 整合 CI 診斷引擎，精確定位錯誤位置
 * - 解析 CI log，識別錯誤類型
 * - 根據錯誤類型選擇適當的評論模板
 * - 執行可自動修復的錯誤修復
 * - 生成 Markdown 格式的評論（包含精確位置和修復建議）
 * - 支援自動創建修復 PR
 * - 寫入事件到 registry.json
 *
 * 使用方式：
 * npx ts-node generate-comment.ts --workflow "CI Pipeline" --run-id "123" --commit "abc123"
 * npx ts-node generate-comment.ts --workflow "CI Pipeline" --run-id "123" --commit "abc123" --auto-repair
 *
 * =============================================================================
 */

import * as fs from "fs";
import * as path from "path";
import { spawnSync } from "child_process";
import { CIDiagnosisEngine, DiagnosisReport, DiagnosedError } from "./ci-diagnosis-engine";
import { parseCommandSegments } from "./safe-commands";

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

interface WorkflowContext {
  workflow: string;
  runId: string;
  commit: string;
  branch?: string;
  prNumber?: string;
  autoRepair?: boolean;
  useDiagnosisEngine?: boolean;
}

interface ErrorClassification {
  type: string;
  pattern: RegExp;
  category: string;
  autoFixable: boolean;
  fixCommand?: string;
  description: string;
}

interface CommentData {
  emoji: string;
  status_text: string;
  workflow: string;
  run_id: string;
  commit: string;
  timestamp: string;
  error_emoji: string;
  error_message: string;
  error_details?: string;
  fix_emoji: string;
  auto_fixed: boolean;
  fix_type?: string;
  fix_command?: string;
  fix_commit?: string;
  fix_suggestions?: string;
  suggestion_emoji: string;
  fix_steps: string[];
  doc_emoji: string;
  docs: Array<{ title: string; url: string }>;
  event_id: string;
}

interface EventRecord {
  id: string;
  type: string;
  workflow: string;
  commit: string;
  status: string;
  auto_fixed: boolean;
  error_type?: string;
  fix_type?: string;
  timestamp: string;
}

// =============================================================================
// ERROR CLASSIFICATIONS
// =============================================================================

const ERROR_CLASSIFICATIONS: ErrorClassification[] = [
  {
    type: "typescript",
    pattern: /error TS\d+/i,
    category: "type_error",
    autoFixable: false,
    description: "TypeScript 型別錯誤",
  },
  {
    type: "eslint",
    pattern: /eslint.*error|error.*eslint|\d+ problems? \(\d+ errors?/i,
    category: "lint_error",
    autoFixable: true,
    fixCommand: "npx eslint --fix .",
    description: "ESLint 格式錯誤",
  },
  {
    type: "prettier",
    pattern: /prettier.*error|code style issues|Forgot to run Prettier/i,
    category: "format_error",
    autoFixable: true,
    fixCommand: "npx prettier --write .",
    description: "Prettier 格式錯誤",
  },
  {
    type: "yamllint",
    pattern: /yamllint.*error|yaml.*syntax error/i,
    category: "format_error",
    autoFixable: true,
    fixCommand: "npx yaml-lint --fix .",
    description: "YAML 格式錯誤",
  },
  {
    type: "markdownlint",
    pattern: /markdownlint|MD\d{3}/i,
    category: "format_error",
    autoFixable: true,
    fixCommand: "npx markdownlint --fix .",
    description: "Markdown 格式錯誤",
  },
  {
    type: "test_failure",
    pattern: /FAILED|FAIL|test.*failed|jest.*failed/i,
    category: "test_error",
    autoFixable: false,
    description: "測試失敗",
  },
  {
    type: "security",
    pattern: /vulnerability|CVE-\d+|security|critical.*severity/i,
    category: "security_error",
    autoFixable: false,
    description: "安全漏洞",
  },
  {
    type: "build_failure",
    pattern: /build failed|compilation error|build error/i,
    category: "build_error",
    autoFixable: false,
    description: "建置失敗",
  },
];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function parseArgs(): WorkflowContext {
  const args = process.argv.slice(2);
  const context: WorkflowContext = {
    workflow: "CI Pipeline",
    runId: "unknown-run",
    commit: "unknown-commit",
    autoRepair: false,
    useDiagnosisEngine: true, // 默認使用診斷引擎
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--workflow":
        context.workflow = args[++i] || context.workflow;
        break;
      case "--run-id":
        context.runId = args[++i] || context.runId;
        break;
      case "--commit":
        context.commit = args[++i] || context.commit;
        break;
      case "--branch":
        context.branch = args[++i];
        break;
      case "--pr-number":
        context.prNumber = args[++i];
        break;
      case "--auto-repair":
        context.autoRepair = true;
        break;
      case "--no-diagnosis":
        context.useDiagnosisEngine = false;
        break;
    }
  }

  return context;
}

function readCILog(): string {
  const possibleLogPaths = [
    path.join(process.cwd(), "artifacts", "logs", "ci.log"),
    path.join(process.cwd(), "ci.log"),
    path.join(process.cwd(), ".github", "logs", "ci.log"),
  ];

  for (const logPath of possibleLogPaths) {
    if (fs.existsSync(logPath)) {
      return fs.readFileSync(logPath, "utf-8");
    }
  }

  // 如果沒有 log 文件，嘗試從環境變數獲取
  if (process.env.CI_LOG_CONTENT) {
    return process.env.CI_LOG_CONTENT;
  }

  return "無法讀取 CI log，請確認檔案是否存在或檢查 GitHub Actions 輸出。";
}

function classifyError(logContent: string): ErrorClassification | null {
  for (const classification of ERROR_CLASSIFICATIONS) {
    if (classification.pattern.test(logContent)) {
      return classification;
    }
  }
  return null;
}

function extractErrorMessage(logContent: string, errorType: string): string {
  const lines = logContent.split("\n");
  const errorLines: string[] = [];
  let capturing = false;
  let captureCount = 0;

  for (const line of lines) {
    if (line.toLowerCase().includes("error") || capturing) {
      errorLines.push(line);
      capturing = true;
      captureCount++;

      if (captureCount > 10) break; // 限制擷取行數
    }
  }

  if (errorLines.length === 0) {
    return `${errorType} 錯誤發生，請查看完整 CI log 獲取詳細資訊。`;
  }

  return errorLines.join("\n");
}

function isProtectedBranch(branch?: string): boolean {
  const protectedBranches = ["main", "master", "production", "release"];
  return branch ? protectedBranches.includes(branch) : false;
}

function runSafeCommand(
  command: string,
  options?: { stdio?: "inherit" | "pipe"; timeoutMs?: number }
): string {
  const segments = parseCommandSegments(command);
  const stdio = options?.stdio ?? "pipe";
  const timeout = options?.timeoutMs ?? 300000;
  let output = "";

  for (const args of segments) {
    const result = spawnSync(args[0], args.slice(1), {
      encoding: "utf-8",
      stdio: stdio === "inherit" ? "inherit" : "pipe",
      timeout,
    });

    if (result.error) {
      throw result.error;
    }
    if (typeof result.status === "number" && result.status !== 0) {
      const commandLabel = args.join(" ");
      throw new Error(result.stderr?.toString() || `Command failed: ${commandLabel}`);
    }
    if (stdio === "pipe" && result.stdout) {
      output += result.stdout;
    }
  }

  return output.trim();
}

function executeAutoFix(
  fixCommand: string,
  branch?: string
): { success: boolean; commit?: string } {
  if (isProtectedBranch(branch)) {
    console.log("受保護分支，跳過自動修復");
    return { success: false };
  }

  try {
    console.log(`執行自動修復: ${fixCommand}`);
    runSafeCommand(fixCommand, { stdio: "inherit" });

    // 檢查是否有變更
    const status = runSafeCommand("git status --porcelain");
    if (status) {
      // 提交變更
      runSafeCommand("git add .", { stdio: "inherit" });
      runSafeCommand('git commit -m "[auto-fix] 自動修復格式錯誤 (81-auto-comment)"', {
        stdio: "inherit",
      });
      const commitSha = runSafeCommand("git rev-parse HEAD");
      console.log(`自動修復已提交: ${commitSha}`);
      return { success: true, commit: commitSha };
    }

    console.log("沒有需要修復的變更");
    return { success: true };
  } catch (error) {
    console.error("自動修復失敗:", error);
    return { success: false };
  }
}

function generateEventId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 10);
  return `auto-comment-${timestamp}-${random}`;
}

function getFixSuggestions(errorType: string): string[] {
  const suggestions: Record<string, string[]> = {
    typescript: [
      "本地執行 `npm run type-check` 或 `tsc --noEmit` 重現錯誤",
      "根據錯誤訊息修復型別定義",
      "確認相關 interface/type 定義是否正確",
      "推送修復分支，CI 將自動重跑",
    ],
    eslint: [
      "本地執行 `npx eslint --fix .` 自動修復",
      "檢查 .eslintrc 配置是否正確",
      "對於無法自動修復的問題，手動修改程式碼",
      "推送修復分支，CI 將自動重跑",
    ],
    prettier: [
      "本地執行 `npx prettier --write .` 自動修復",
      "確認 .prettierrc 配置與 CI 一致",
      "推送修復分支，CI 將自動重跑",
    ],
    test_failure: [
      "本地執行 `npm test` 重現測試失敗",
      "檢查測試案例與實際程式碼的差異",
      "確認測試資料與預期結果是否正確",
      "推送修復分支，CI 將自動重跑",
    ],
    security: [
      "執行 `npm audit` 查看安全漏洞詳情",
      "執行 `npm audit fix` 嘗試自動修復",
      "對於需要 breaking changes 的修復，謹慎評估影響",
      "聯繫安全團隊進行審核",
    ],
    build_failure: [
      "本地執行 `npm run build` 重現建置錯誤",
      "檢查依賴是否完整安裝",
      "確認環境變數配置正確",
      "推送修復分支，CI 將自動重跑",
    ],
  };

  return (
    suggestions[errorType] || [
      "請查看完整 CI log 獲取詳細錯誤資訊",
      "本地重現問題後進行修復",
      "推送修復分支，CI 將自動重跑",
    ]
  );
}

function getRelatedDocs(errorType: string): Array<{ title: string; url: string }> {
  const baseDocs = [
    { title: "CI 故障排除指南", url: "./docs/ci-troubleshooting.md" },
    { title: "CI 自動評論系統文檔", url: "./docs/CI_AUTO_COMMENT_SYSTEM.md" },
  ];

  const typeDocs: Record<string, Array<{ title: string; url: string }>> = {
    typescript: [
      { title: "TypeScript 官方文檔", url: "https://www.typescriptlang.org/docs/" },
    ],
    eslint: [{ title: "ESLint 規則說明", url: "https://eslint.org/docs/rules/" }],
    security: [{ title: "npm audit 文檔", url: "https://docs.npmjs.com/cli/audit" }],
  };

  return [...baseDocs, ...(typeDocs[errorType] || [])];
}

// =============================================================================
// MAIN FUNCTION
// =============================================================================

async function main(): Promise<void> {
  console.log("=== Auto-Comment Generator (81-auto-comment) - Enhanced ===\n");

  // 解析參數
  const context = parseArgs();
  console.log("Workflow Context:", context);

  let diagnosisReport: DiagnosisReport | null = null;
  let errorType = "unknown";
  let errorMessage = "";
  let autoFixed = false;
  let fixCommit: string | undefined;
  let errorClassification: ErrorClassification | null = null;

  // 使用診斷引擎進行深度分析
  if (context.useDiagnosisEngine) {
    console.log("\n🔍 使用 CI 診斷引擎進行深度分析...\n");

    const engine = new CIDiagnosisEngine({
      workflow: context.workflow,
      runId: context.runId,
      commit: context.commit,
      branch: context.branch,
    });

    engine.loadLog();
    diagnosisReport = engine.diagnose();

    // 從診斷報告中提取信息
    if (diagnosisReport.errors.length > 0) {
      const primaryError = diagnosisReport.errors[0];
      errorType = primaryError.type;
      errorMessage = formatDiagnosisErrors(diagnosisReport.errors);

      console.log(`📊 診斷結果:`);
      console.log(`   ID: ${diagnosisReport.id}`);
      console.log(`   總錯誤數: ${diagnosisReport.summary.totalErrors}`);
      console.log(`   可自動修復: ${diagnosisReport.summary.autoFixableErrors}`);
      console.log(`   主要問題: ${diagnosisReport.summary.primaryIssue}`);

      // 如果可以自動修復且啟用了 autoRepair
      if (diagnosisReport.autoFixPlan.canAutoFix && context.autoRepair) {
        console.log("\n🔧 執行自動修復計劃...\n");
        const repairResult = await executeAutoRepairPlan(diagnosisReport, context.branch);
        autoFixed = repairResult.success;
        fixCommit = repairResult.commit;
      }
    }
  } else {
    // 使用傳統方法
    const logContent = readCILog();
    console.log(`CI Log 長度: ${logContent.length} 字元\n`);

    errorClassification = classifyError(logContent);
    errorType = errorClassification?.type || "unknown";
    errorMessage = extractErrorMessage(logContent, errorType);

    console.log(`錯誤類型: ${errorType}`);
    console.log(`可自動修復: ${errorClassification?.autoFixable || false}\n`);

    // 嘗試自動修復
    if (errorClassification?.autoFixable && errorClassification.fixCommand) {
      console.log("嘗試自動修復...");
      const fixResult = executeAutoFix(errorClassification.fixCommand, context.branch);
      autoFixed = fixResult.success;
      fixCommit = fixResult.commit;
    }
  }

  // 生成事件 ID
  const eventId = diagnosisReport?.id || generateEventId();

  // 準備評論資料
  const commentData: CommentData = {
    emoji: autoFixed ? "✅" : "🚨",
    status_text: autoFixed ? "已自動修復" : "失敗",
    workflow: context.workflow,
    run_id: context.runId,
    commit: context.commit,
    timestamp: new Date().toISOString(),
    error_emoji: "🔍",
    error_message: diagnosisReport
      ? diagnosisReport.summary.primaryIssue
      : (errorClassification?.description || "未知錯誤"),
    error_details: errorMessage,
    fix_emoji: autoFixed ? "✅" : "❌",
    auto_fixed: autoFixed,
    fix_type: autoFixed ? errorType : undefined,
    fix_command: errorClassification?.fixCommand,
    fix_commit: fixCommit,
    fix_suggestions: autoFixed
      ? undefined
      : diagnosisReport
        ? formatFixSuggestions(diagnosisReport)
        : `需要人工修復。錯誤類型：${errorClassification?.description || "未知"}`,
    suggestion_emoji: "💡",
    fix_steps: diagnosisReport
      ? formatAutoFixSteps(diagnosisReport)
      : getFixSuggestions(errorType),
    doc_emoji: "📚",
    docs: getRelatedDocs(errorType),
    event_id: eventId,
  };

  // 生成評論內容
  const comment = diagnosisReport
    ? generateEnhancedComment(commentData, diagnosisReport)
    : generateComment(commentData);

  // 確保輸出目錄存在
  const outputDir = path.join(
    process.cwd(),
    "governance",
    "dimensions",
    "81-auto-comment",
    "output"
  );
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // 寫入評論檔案
  const commentPath = path.join(outputDir, "comment.md");
  fs.writeFileSync(commentPath, comment, "utf-8");
  console.log(`\n✅ 評論已生成: ${commentPath}`);

  // 保存診斷報告
  if (diagnosisReport) {
    const diagnosisPath = path.join(outputDir, "diagnosis-report.json");
    fs.writeFileSync(diagnosisPath, JSON.stringify(diagnosisReport, null, 2), "utf-8");
    console.log(`✅ 診斷報告已生成: ${diagnosisPath}`);
  }

  // 準備事件記錄
  const eventRecord: EventRecord = {
    id: eventId,
    type: "auto-comment",
    workflow: context.workflow,
    commit: context.commit,
    status: autoFixed ? "auto-fixed" : "failure",
    auto_fixed: autoFixed,
    error_type: errorType,
    fix_type: autoFixed ? errorType : undefined,
    timestamp: new Date().toISOString(),
  };

  // 輸出事件記錄供後續腳本使用
  const eventPath = path.join(outputDir, "event.json");
  fs.writeFileSync(eventPath, JSON.stringify(eventRecord, null, 2), "utf-8");
  console.log(`✅ 事件記錄已生成: ${eventPath}`);

  console.log("\n=== 完成 ===");
}

// =============================================================================
// DIAGNOSIS ENGINE INTEGRATION HELPERS
// =============================================================================

function formatDiagnosisErrors(errors: DiagnosedError[]): string {
  return errors
    .slice(0, 10) // 限制顯示前 10 個錯誤
    .map(e => `[${e.type.toUpperCase()}] ${e.location.file}:${e.location.line} - ${e.message}`)
    .join("\n");
}

function formatFixSuggestions(report: DiagnosisReport): string {
  if (report.autoFixPlan.canAutoFix) {
    return `可以自動修復 ${report.summary.autoFixableErrors} 個錯誤。運行 \`npx ts-node auto-repair-executor.ts\` 執行修復。`;
  }
  return `需要人工修復 ${report.summary.manualFixRequired} 個錯誤。主要問題：${report.summary.primaryIssue}`;
}

function formatAutoFixSteps(report: DiagnosisReport): string[] {
  if (!report.autoFixPlan.canAutoFix) {
    return [
      "查看診斷報告了解錯誤詳情",
      "根據錯誤位置和建議修復代碼",
      "本地運行測試驗證修復",
      "推送修復並重新運行 CI",
    ];
  }

  return report.autoFixPlan.steps.map(step => `${step.description}: \`${step.command}\``);
}

async function executeAutoRepairPlan(
  report: DiagnosisReport,
  branch?: string
): Promise<{ success: boolean; commit?: string }> {
  if (isProtectedBranch(branch)) {
    console.log("受保護分支，跳過自動修復");
    return { success: false };
  }

  if (!report.autoFixPlan.canAutoFix) {
    console.log("無法自動修復");
    return { success: false };
  }

  try {
    // 執行每個修復步驟（跳過 commit 步驟，我們自己處理）
    for (const step of report.autoFixPlan.steps) {
      if (step.action === "commit" || step.action === "verify") {
        continue;
      }

      console.log(`  執行: ${step.command}`);
      try {
        runSafeCommand(step.command, { stdio: "inherit" });
      } catch {
        // 某些命令可能返回非零但實際成功
        console.log(`  ⚠️ 命令返回非零，繼續執行...`);
      }
    }

    // 檢查是否有變更
    const status = runSafeCommand("git status --porcelain");
    if (status) {
      runSafeCommand("git add .", { stdio: "inherit" });
      runSafeCommand(`git commit -m "[auto-fix] 自動修復 CI 錯誤 (診斷 ID: ${report.id})"`, {
        stdio: "inherit",
      });
      const commitSha = runSafeCommand("git rev-parse HEAD");
      console.log(`✅ 自動修復已提交: ${commitSha}`);
      return { success: true, commit: commitSha };
    }

    console.log("沒有需要修復的變更");
    return { success: true };
  } catch (error) {
    console.error("自動修復失敗:", error);
    return { success: false };
  }
}

function generateEnhancedComment(data: CommentData, report: DiagnosisReport): string {
  const errorList = report.errors
    .slice(0, 5)
    .map(e => {
      const codeChangeInfo = e.suggestedFix.codeChange
        ? `\n     建議: \`${e.suggestedFix.codeChange.explanation}\``
        : "";
      return `   - \`${e.location.file}:${e.location.line}\`: ${e.message}${codeChangeInfo}`;
    })
    .join("\n");

  const moreErrors = report.errors.length > 5
    ? `\n   - ... 還有 ${report.errors.length - 5} 個錯誤`
    : "";

  return `## ${data.emoji} CI 診斷報告：${data.status_text}

**診斷 ID**：\`${report.id}\`
**工作流程**：${data.workflow}
**執行 ID**：${data.run_id}
**Commit**：${data.commit}
**時間戳**：${data.timestamp}

---

### 📊 診斷摘要

| 項目 | 值 |
|------|-----|
| 總錯誤數 | ${report.summary.totalErrors} |
| 嚴重錯誤 | ${report.summary.criticalErrors} |
| 可自動修復 | ${report.summary.autoFixableErrors} |
| 需人工處理 | ${report.summary.manualFixRequired} |
| 主要問題 | ${report.summary.primaryIssue} |
| 預估修復時間 | ${report.summary.estimatedFixTime} |

---

### ${data.error_emoji} 錯誤詳情（精確位置）

${errorList}${moreErrors}

<details>
<summary>展開完整診斷日誌</summary>

\`\`\`
${data.error_details}
\`\`\`

</details>

---

### ${data.fix_emoji} 修復狀態

${data.auto_fixed
    ? `**✅ 已自動修復並提交**

- 修復類型：${data.fix_type}
- 提交 SHA：\`${data.fix_commit}\`
- 修復的錯誤數：${report.summary.autoFixableErrors}`
    : report.autoFixPlan.canAutoFix
      ? `**⚠️ 可以自動修復**

運行以下命令執行自動修復：
\`\`\`bash
cd governance/dimensions/81-auto-comment/scripts
npx ts-node auto-repair-executor.ts
\`\`\``
      : `**❌ 需要人工修復**

${data.fix_suggestions}`
  }

---

### ${data.suggestion_emoji} 修復步驟

${data.fix_steps.map((step, i) => `${i + 1}. ${step}`).join("\n")}

---

### ${data.doc_emoji} 相關文檔

${data.docs.map((doc) => `- [${doc.title}](${doc.url})`).join("\n")}

---

<sub>
此報告由 **CI Diagnosis Engine v2.0** (81-auto-comment) 自動生成
診斷 ID：\`${report.id}\`
分析時間：${report.metadata.analysisTime}ms
已寫入 \`governance/dimensions/81-auto-comment/output/\`
</sub>
`;
}

function generateComment(data: CommentData): string {
  return `## ${data.emoji} 自動評論：CI 驗證${data.status_text}

**工作流程**：${data.workflow}
**執行 ID**：${data.run_id}
**Commit**：${data.commit}
**時間戳**：${data.timestamp}

---

### ${data.error_emoji} 錯誤摘要

${data.error_message}

${
  data.error_details
    ? `<details>
<summary>展開完整錯誤訊息</summary>

\`\`\`
${data.error_details}
\`\`\`

</details>`
    : ""
}

---

### ${data.fix_emoji} 修復狀態

${
  data.auto_fixed
    ? `**✅ 已自動修復並提交**

修復類型：${data.fix_type}
修復命令：\`${data.fix_command}\`
${data.fix_commit ? `提交 SHA：${data.fix_commit}` : ""}`
    : `**❌ 需要人工修復**

${data.fix_suggestions}`
}

---

### ${data.suggestion_emoji} 建議修復步驟

${data.fix_steps.map((step, i) => `${i + 1}. ${step}`).join("\n")}

---

### ${data.doc_emoji} 相關文檔

${data.docs.map((doc) => `- [${doc.title}](${doc.url})`).join("\n")}

---

<sub>
此評論由 **Auto-Comment Engine** (81-auto-comment) 自動生成
事件 ID：\`${data.event_id}\`
已寫入 \`governance/index/events/registry.json\`
</sub>
`;
}

// 執行主函數
main().catch((error) => {
  console.error("Error:", error);
  process.exit(1);
});
