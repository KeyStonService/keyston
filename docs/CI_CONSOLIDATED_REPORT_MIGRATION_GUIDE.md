# CI 整合報告遷移指南 | CI Consolidated Report Migration Guide

## 🎯 目標 | Objective

本指南幫助您將現有的 CI workflow 遷移到整合報告系統，避免在 PR 中產生多條分散的評論。

This guide helps you migrate existing CI workflows to the consolidated report system, avoiding scattered comments in PRs.

---

## 📋 遷移前檢查清單 | Pre-Migration Checklist

在開始遷移前，請確認：

- [ ] 您的 workflow 在 PR 上執行
- [ ] 您的 workflow 包含多個 jobs 或可能產生多條評論
- [ ] 您有權限修改 `.github/workflows/` 目錄
- [ ] 您了解現有 workflow 的結構和依賴關係

Before starting migration, ensure:

- [ ] Your workflow runs on PRs
- [ ] Your workflow contains multiple jobs or may create multiple comments
- [ ] You have permission to modify `.github/workflows/` directory
- [ ] You understand the structure and dependencies of your existing workflow

---

## 🔄 遷移步驟 | Migration Steps

### 步驟 1：分析現有 Workflow

1. 識別所有會失敗的步驟
2. 列出需要報告的 jobs
3. 找出現有的評論生成點

**範例分析**：

```yaml
# Before Migration
jobs:
  validate:
    steps:
      - name: Type check
        run: npm run typecheck
      
      - name: Lint
        run: npm run lint
      
      - name: Comment on failure
        if: failure()
        uses: actions/github-script@v7
        # Creates individual comment ❌
```

### 步驟 2：拆分 Jobs 並添加 Outputs

將單一 job 拆分為多個獨立 jobs，每個 job 輸出摘要：

```yaml
# After Migration - Split into multiple jobs
jobs:
  typecheck:
    name: 型別檢查
    outputs:
      summary: ${{ steps.summary.outputs.text }}
    steps:
      - name: Type check
        id: check
        continue-on-error: true
        run: npm run typecheck
      
      - name: Create summary
        id: summary
        if: always()
        run: |
          STATUS="success"
          MESSAGE="型別檢查: 通過"
          
          if [ "${{ steps.check.outcome }}" != "success" ]; then
            STATUS="failure"
            MESSAGE="型別檢查失敗"
          fi
          
          echo "text={\"status\":\"$STATUS\",\"message\":\"$MESSAGE\"}" >> $GITHUB_OUTPUT
  
  lint:
    name: 代碼檢查
    outputs:
      summary: ${{ steps.summary.outputs.text }}
    steps:
      # Similar structure...
```

**重點**：
- 使用 `continue-on-error: true` 讓 job 在失敗時繼續
- 使用 `if: always()` 確保 summary 步驟總是執行
- 輸出格式必須是 `{"status":"...","message":"..."}`

### 步驟 3：移除現有的評論生成邏輯

刪除或註解掉所有現有的評論生成步驟：

```yaml
# ❌ Remove these
- name: Comment on failure
  if: failure()
  uses: actions/github-script@v7

# ❌ Remove these
- name: Create comment
  uses: peter-evans/create-or-update-comment@v4
```

### 步驟 4：添加 Report Job

在 workflow 末尾添加整合報告 job：

```yaml
  report:
    name: 📊 整合報告
    runs-on: ubuntu-latest
    needs: [typecheck, lint, test]  # List all jobs
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
            "typecheck": ${{ needs.typecheck.outputs.summary || '{"status":"unknown","message":"無摘要"}' }},
            "lint": ${{ needs.lint.outputs.summary || '{"status":"unknown","message":"無摘要"}' }},
            "test": ${{ needs.test.outputs.summary || '{"status":"unknown","message":"無摘要"}' }}
          }
          EOF
          
          # Determine overall status
          OVERALL_STATUS="success"
          if [ "${{ needs.typecheck.result }}" == "failure" ] || \
             [ "${{ needs.lint.result }}" == "failure" ] || \
             [ "${{ needs.test.result }}" == "failure" ]; then
            OVERALL_STATUS="failure"
          fi
          
          echo "overall-status=$OVERALL_STATUS" >> $GITHUB_OUTPUT
          echo "job-summaries=$(cat job-summaries.json | jq -c .)" >> $GITHUB_OUTPUT
      
      - name: Call consolidated report workflow
        if: github.event_name == 'pull_request'
        uses: ./.github/workflows/ci-consolidated-report.yml
        with:
          ci-name: 'Your Workflow Name'  # 修改為您的 workflow 名稱
          job-summaries: ${{ steps.prepare.outputs.job-summaries }}
          workflow-run-id: ${{ github.run_id }}
          commit-sha: ${{ github.sha }}
          overall-status: ${{ steps.prepare.outputs.overall-status }}
          pr-number: ${{ github.event.pull_request.number }}
        secrets:
          token: ${{ secrets.GITHUB_TOKEN }}
```

### 步驟 5：更新權限

確保 workflow 有正確的權限：

```yaml
# At the top of the workflow file
permissions:
  contents: read
  pull-requests: write  # Required for commenting
  issues: write         # Required for commenting
```

### 步驟 6：測試

1. 創建測試 PR
2. 觸發 workflow
3. 驗證：
   - [ ] 只生成一條評論
   - [ ] 評論包含所有 job 的結果
   - [ ] 評論格式正確（中文模板）
   - [ ] 再次推送時，評論被更新而非創建新的

---

## 📝 完整範例 | Complete Example

參考以下檔案：

1. **實際應用**：`.github/workflows/self-healing-validation.yml`
2. **範例模板**：`docs/examples/ci-consolidated-report-example.yml`
3. **詳細文檔**：`docs/CI_CONSOLIDATED_REPORT.md`

---

## 🔧 常見場景 | Common Scenarios

### 場景 1：單一 Job 執行多個檢查

**Before**:
```yaml
jobs:
  validate:
    steps:
      - name: Typecheck
        run: npm run typecheck
      - name: Lint
        run: npm run lint
      - name: Test
        run: npm test
```

**After**:
Split into 3 jobs (typecheck, lint, test) with outputs + report job

### 場景 2：Job 之間有依賴關係

保持依賴關係，只在 report job 使用 `needs` 列出所有 jobs：

```yaml
jobs:
  build:
    # ...
  
  test:
    needs: build  # Keep dependency
    # ...
  
  deploy:
    needs: [build, test]  # Keep dependencies
    # ...
  
  report:
    needs: [build, test, deploy]  # Depends on all
    if: always()
    # ...
```

### 場景 3：Job 在不同條件下執行

使用條件表達式處理可能跳過的 jobs：

```yaml
  report:
    steps:
      - name: Prepare job summaries
        run: |
          cat > job-summaries.json <<EOF
          {
            "build": ${{ needs.build.result != 'skipped' && needs.build.outputs.summary || '{"status":"skipped","message":"已跳過"}' }},
            "test": ${{ needs.test.result != 'skipped' && needs.test.outputs.summary || '{"status":"skipped","message":"已跳過"}' }}
          }
          EOF
```

---

## ⚠️ 注意事項 | Important Notes

### 1. Job Output 限制

GitHub Actions job outputs 有大小限制（~1MB）。如果 summary 太大：

- 只輸出關鍵資訊
- 將詳細日誌存為 artifact
- 在評論中提供 artifact 連結

### 2. 失敗處理

使用 `continue-on-error: true` 確保後續步驟執行，但要在 summary 中正確反映狀態。

### 3. Report Job 總是執行

使用 `if: always()` 確保 report job 即使前面的 jobs 失敗也會執行。

### 4. JSON 格式驗證

在本地測試時，使用 `jq` 驗證 JSON 格式：

```bash
echo '{"status":"success","message":"測試"}' | jq .
```

---

## 🐛 故障排除 | Troubleshooting

### 問題：Report job 沒有執行

**解決方案**：
- 檢查 `if: always()` 是否存在
- 確認 `needs` 列表包含所有 jobs

### 問題：Job summary 為空

**解決方案**：
- 檢查 `steps.summary.outputs.text` 格式
- 確認使用 `$GITHUB_OUTPUT` 而非已棄用的 `set-output`

### 問題：JSON 解析錯誤

**解決方案**：
- 確保 JSON 中的雙引號正確轉義
- 使用 `jq -c` 壓縮 JSON
- 檢查特殊字符（如換行符）

### 問題：評論未更新

**解決方案**：
- 檢查 HTML 註解標記 `<!-- CI_REPORT:name -->` 是否一致
- 確認 `ci-name` 參數與之前相同
- 驗證權限設定

---

## 📊 遷移檢查清單 | Migration Checklist

完成遷移後，請驗證：

- [ ] Workflow 可以成功執行
- [ ] 所有 jobs 的結果都在報告中
- [ ] 評論使用中文模板格式
- [ ] 失敗時顯示正確的錯誤類型和建議
- [ ] 成功時顯示成功訊息
- [ ] 評論被更新而非重複創建
- [ ] 互動式客服命令正確顯示
- [ ] 相關資源連結有效

---

## 🆘 尋求協助 | Getting Help

如果遇到問題：

1. 查看 [CI_CONSOLIDATED_REPORT.md](./CI_CONSOLIDATED_REPORT.md) 詳細文檔
2. 參考 [ci-consolidated-report-example.yml](./examples/ci-consolidated-report-example.yml) 範例
3. 檢查 [self-healing-validation.yml](../.github/workflows/self-healing-validation.yml) 實際應用
4. 在 GitHub Issues 中尋求協助

---

## 📚 延伸閱讀 | Further Reading

- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Reusing Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Job Outputs](https://docs.github.com/en/actions/using-jobs/defining-outputs-for-jobs)

---

**版本**：1.0.0  
**最後更新**：2024-12-15  
**維護者**：SynergyMesh Team
