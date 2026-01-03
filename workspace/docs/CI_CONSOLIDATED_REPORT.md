# CI 整合報告系統 | CI Consolidated Report System

## 📋 概述 | Overview

CI 整合報告系統將多個 CI job 的執行結果整合成單一評論，避免在 PR 中產生多條分散的評論。此系統遵循中文模板格式，提供清晰的錯誤診斷、修復建議和互動式客服。

The CI Consolidated Report System consolidates multiple CI job results into a single comment, preventing scattered comments in PRs. The system follows a Chinese template format, providing clear error diagnosis, fix suggestions, and interactive support.

---

## 🏗️ 系統架構 | Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Individual CI Jobs                          │
│  (Build, Test, Validate, etc.)                          │
├─────────────────────────────────────────────────────────┤
│  Each job exports:                                       │
│  - Status (success/failure/warning)                      │
│  - Summary message                                       │
│         ↓                                                │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│              Report Job                                  │
│  - Gathers all job outputs                               │
│  - Determines overall status                             │
│  - Calls consolidated report workflow                    │
│         ↓                                                │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│     ci-consolidated-report.yml                           │
│  - Generates consolidated comment                        │
│  - Uses Chinese template format                          │
│  - Updates single PR comment                             │
│         ↓                                                │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│              PR Comment                                  │
│  - Single consolidated report                            │
│  - Includes all job results                              │
│  - Provides fix suggestions                              │
│  - Interactive support commands                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 評論模板格式 | Comment Template Format

整合評論遵循以下格式（即時修復模式）：

```markdown
<!-- CI_REPORT:workflow-name -->

## ❌ Workflow Name - 客服報告

🔴 **狀態**：執行失敗

**執行 ID**：`123456`
**Commit**：`abc123`
**時間戳**：2024-12-15 01:00:00 UTC

---

### 🔍 問題診斷

**錯誤類型**：測試失敗  
**即時診斷**：已自動收集測試失敗日誌並分析根因

---

### ⚡ 即時修復

已執行修復動作：
\`\`\`bash
bash scripts/check-env.sh
npm test -- --verbose
bash scripts/auto-fix.sh
\`\`\`

**修復結果**：
- 測試環境檢查已完成
- 詳細測試日誌已收集
- 自動修復腳本已執行
- 待重新觸發 CI pipeline 驗證

---

### 📊 錯誤摘要

\`\`\`
- ❌ **setup-and-build**: 建置與型別檢查: 通過
- ✅ **validate-policies**: 策略驗證: 通過
- ❌ **validate-files**: 自我修復文檔缺失
\`\`\`

---

### 🤝 即時互動

需要更多即時操作？使用以下命令：
- `@copilot rerun Workflow Name` - 立即重新執行 CI
- `@copilot patch Workflow Name` - 立即套用修復補丁
- `@copilot logs Workflow Name` - 立即顯示完整日誌
- `@copilot sync Workflow Name` - 立即同步最新修復狀態

---

### 📚 相關資源

- [CI 故障排除文檔](./docs/ci-troubleshooting.md)
- [Workflow Name 特定文檔](./docs/README.md)
- [環境檢查工具](./scripts/check-env.sh)

---

_此評論由 Workflow Name 即時修復系統自動生成_
```

---

## 🚀 如何使用 | How to Use

### 步驟 1：修改現有 Workflow

將現有的單一 job 拆分為多個 jobs，每個 job 輸出狀態摘要：

```yaml
jobs:
  build:
    name: 建置
    runs-on: ubuntu-latest
    outputs:
      summary: ${{ steps.summary.outputs.text }}
    steps:
      - name: Build
        id: build
        continue-on-error: true
        run: npm run build
      
      - name: Create summary
        id: summary
        if: always()
        run: |
          STATUS="success"
          MESSAGE="建置: 通過"
          
          if [ "${{ steps.build.outcome }}" != "success" ]; then
            STATUS="failure"
            MESSAGE="建置失敗"
          fi
          
          echo "text={\"status\":\"$STATUS\",\"message\":\"$MESSAGE\"}" >> $GITHUB_OUTPUT
```

### 步驟 2：新增 Report Job

在 workflow 末尾新增彙總 job：

```yaml
  report:
    name: 📊 整合報告
    runs-on: ubuntu-latest
    needs: [build, test, lint]
    if: always()
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Prepare job summaries
        id: prepare
        run: |
          # Build JSON with all job summaries
          cat > job-summaries.json <<EOF
          {
            "build": ${{ needs.build.outputs.summary || '{"status":"unknown","message":"無摘要"}' }},
            "test": ${{ needs.test.outputs.summary || '{"status":"unknown","message":"無摘要"}' }},
            "lint": ${{ needs.lint.outputs.summary || '{"status":"unknown","message":"無摘要"}' }}
          }
          EOF
          
          # Determine overall status
          OVERALL_STATUS="success"
          if [ "${{ needs.build.result }}" == "failure" ] || \
             [ "${{ needs.test.result }}" == "failure" ] || \
             [ "${{ needs.lint.result }}" == "failure" ]; then
            OVERALL_STATUS="failure"
          fi
          
          echo "overall-status=$OVERALL_STATUS" >> $GITHUB_OUTPUT
          echo "job-summaries=$(cat job-summaries.json | jq -c .)" >> $GITHUB_OUTPUT
      
      - name: Call consolidated report workflow
        if: github.event_name == 'pull_request'
        uses: ./.github/workflows/ci-consolidated-report.yml
        with:
          ci-name: 'Your CI Name'
          job-summaries: ${{ steps.prepare.outputs.job-summaries }}
          workflow-run-id: ${{ github.run_id }}
          commit-sha: ${{ github.sha }}
          overall-status: ${{ steps.prepare.outputs.overall-status }}
          pr-number: ${{ github.event.pull_request.number }}
        secrets:
          token: ${{ secrets.GITHUB_TOKEN }}
```

### 步驟 3：設定權限

確保 workflow 有正確的權限：

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

---

## 🔧 核心組件 | Core Components

### 1. 可重用 Workflow

**檔案**：`.github/workflows/ci-consolidated-report.yml`

接受以下輸入：

- `ci-name`：CI workflow 名稱
- `job-summaries`：JSON 格式的 job 摘要
- `workflow-run-id`：GitHub workflow run ID
- `commit-sha`：Git commit SHA
- `overall-status`：整體狀態 (success/failure/warning)
- `pr-number`：PR 編號

### 2. 評論生成腳本

**檔案**：`.github/scripts/generate-consolidated-comment.py`

功能：

- 解析 job 摘要 JSON
- 分析錯誤類型
- 生成修復建議
- 選擇快速修復命令
- 格式化中文評論模板

### 3. 評論更新機制

使用 `peter-evans/create-or-update-comment@v4` 和 `peter-evans/find-comment@v3`：

1. 搜尋現有評論（透過 HTML 註解標記）
2. 如果找到，更新現有評論
3. 如果沒有找到，建立新評論

避免在 PR 中產生多條重複評論。

---

## 📊 錯誤類型識別 | Error Type Detection

系統會分析 job 訊息並自動識別錯誤類型：

| 錯誤類型 | 關鍵字 | 建議命令 |
|---------|--------|----------|
| TypeScript 型別錯誤 | type, typescript | `npm run typecheck` |
| 測試失敗 | test, jest | `npm test` |
| Lint 錯誤 | lint, eslint | `npm run lint:fix` |
| 建置失敗 | build | `npm run build` |
| CI 執行錯誤 | 其他 | `bash scripts/check-env.sh` |

---

## 🎯 範例：Self-Healing Validation

參考 `.github/workflows/self-healing-validation.yml` 的實作：

```yaml
jobs:
  setup-and-build:
    outputs:
      summary: ${{ steps.summary.outputs.text }}
    # ... job steps ...
  
  validate-policies:
    outputs:
      summary: ${{ steps.summary.outputs.text }}
    # ... job steps ...
  
  validate-files:
    outputs:
      summary: ${{ steps.summary.outputs.text }}
    # ... job steps ...
  
  report:
    needs: [setup-and-build, validate-policies, validate-files]
    if: always()
    # ... calls ci-consolidated-report.yml ...
```

---

## 🔍 故障排除 | Troubleshooting

### 評論未出現

1. 檢查權限設定
2. 確認 `pr-number` 正確傳遞
3. 查看 workflow logs

### 評論重複

1. 確認使用 `find-comment` 步驟
2. 檢查 HTML 註解標記是否一致
3. 驗證 `ci-name` 參數

### JSON 解析錯誤

1. 驗證 job outputs 格式
2. 確保 JSON 正確轉義
3. 使用 `jq` 驗證 JSON 語法

---

## 📚 相關文檔 | Related Documentation

- [CI 互動式客服升級指南](./INTERACTIVE_CI_UPGRADE_GUIDE.md)
- [CI 全局狀態修復](./CI_GLOBAL_STATUS_FIX.md)
- [GitHub Actions 文檔](https://docs.github.com/en/actions)
- [peter-evans/create-or-update-comment](https://github.com/peter-evans/create-or-update-comment)

---

## 🎉 優勢 | Benefits

✅ **單一評論**：避免 PR 評論區混亂  
✅ **整合視圖**：一次查看所有 job 結果  
✅ **智能建議**：根據錯誤類型提供修復建議  
✅ **互動式客服**：支援 @copilot 命令  
✅ **中文友善**：完整中文模板支援  
✅ **可更新**：同一評論會被更新而非建立新的  

---

**維護者**：SynergyMesh Team  
**最後更新**：2024-12-15
