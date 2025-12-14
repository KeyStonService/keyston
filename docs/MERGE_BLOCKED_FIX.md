# 🔓 修復 PR 合併被阻擋問題

## 問題描述

PR #16 所有 CI 檢查都通過了（包括 CodeQL Code Scanning），但仍然顯示：

```
Merging is blocked
Waiting for Code Scanning results. Code Scanning may not be configured for the target branch.
```

## 根本原因

這是因為 GitHub Repository Rules（新版規則系統）要求 Code Scanning 結果，但規則配置可能不正確或過於嚴格。

## ✅ 解決方案

### 方案 1：調整 Repository Rules（推薦）

1. **前往 Repository Settings**

   ```
   https://github.com/we-can-fix/synergymesh/settings/rules
   ```

2. **檢查並編輯 Rulesets**
   - 點擊應用於 `main` 分支的 Ruleset
   - 找到 **"Require code scanning results"** 或類似設定
   - 選項：
     - **移除此要求**（如果不需要）
     - **調整為 "Advisory" 模式**而非 "Enforced"
     - **確保 Code Scanning 工具已正確配置**

3. **保存變更**

### 方案 2：調整舊版分支保護規則

如果使用的是舊版 Branch Protection Rules：

1. **前往 Branch Protection**

   ```
   https://github.com/we-can-fix/synergymesh/settings/branches
   ```

2. **編輯 `main` 分支規則**
   - 取消勾選 "Require status checks to pass before merging" 中的 Code Scanning 相關項目
   - 或確保所需的狀態檢查名稱正確匹配實際的 workflow

3. **保存變更**

### 方案 3：使用管理員權限合併（臨時方案）

如果您有 Repository Admin 權限：

```bash
# 在 GitHub Web UI 中
# 1. 打開 PR: https://github.com/we-can-fix/synergymesh/pull/16
# 2. 點擊合併按鈕旁的下拉選單
# 3. 選擇 "Merge without waiting for requirements to be met (administrators only)"
# 4. 確認合併
```

或使用 CLI（需要特殊權限）：

```bash
gh pr merge 16 --squash --admin
```

## 🔍 驗證檢查狀態

使用以下命令確認所有檢查都通過：

```bash
gh pr view 16 --json statusCheckRollup --jq '[.statusCheckRollup[] | {name: .name, status: .status, conclusion: .conclusion}]'
```

預期輸出：所有檢查的 `conclusion` 都應該是 `"SUCCESS"`。

## 📝 已完成的修復

以下修改已經完成：

1. ✅ 添加了 Code Scanning workflow (`.github/workflows/code-scanning.yml`)
2. ✅ 格式化了 Auto Review and Merge workflow
3. ✅ 添加了 `auto-merge` 標籤到 PR #16
4. ✅ 所有 CI 檢查都通過

## 🎯 下一步

需要 **Repository 管理員**執行以下操作之一：

- [ ] 調整 Repository Rules 移除或放寬 Code Scanning 要求
- [ ] 或使用管理員權限直接合併 PR

## 📚 相關資源

- [GitHub Repository Rules Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Code Scanning Setup](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/setting-up-code-scanning-for-a-repository)
