# 🚀 治理系統實施指南

## 📋 概述

本指南將協助您在 **3 個階段**內完成整個治理系統的部署，從最基礎的證據驗證到完整的自動化閘門。

**總時間估計**: 1-2 小時（大部分是等待 GitHub 處理）

---

## 🎯 三階段實施策略

### 階段 1: 立即生效（10 分鐘）✅

**目標**: 讓 PR 模板強制要求證據

**步驟**:

1. 確認 `.github/pull_request_template.md` 已部署
2. 測試：開一個新 PR，確認模板自動載入
3. 驗證：四大證據欄位都出現在 PR 描述中

**驗收標準**:

- ✅ 新 PR 自動顯示模板
- ✅ 四大證據欄位清晰可見
- ✅ 第五證據（命名規範）欄位存在

---

### 階段 2: 自動化驗證（30 分鐘）🔄

**目標**: 啟用 GitHub Actions 自動檢查

**步驟**:

1. 確認以下檔案已部署：

   - `.github/workflows/gate-pr-evidence.yml`
   - `.github/workflows/gate-root-naming.yml`

2. 開一個測試 PR（故意留空證據欄位）

3. 觀察 GitHub Actions 執行：

   - 應該看到 ❌ 紅叉（檢查失敗）
   - PR 中應該有自動評論說明缺失項目

4. 修正 PR（填入正確證據）

5. 觀察 GitHub Actions 再次執行：

   - 應該看到 ✅ 綠勾（檢查通過）

**驗收標準**:

- ✅ Actions 能正確偵測缺失證據
- ✅ Actions 能正確偵測命名違規
- ✅ 通過檢查後顯示綠勾

---

### 階段 3: 強制執行（1 小時）🔒

**目標**: 讓不合規的 PR 無法合併

**前提條件**:

- 您必須是 repo 的 Owner 或 Admin
- 如果不是，請聯絡 Owner 協助設定

**步驟**:

1. 進入 GitHub repo 設定：

   ```
   Settings → Branches → Branch protection rules
   ```

2. 選擇或新增 `main` 分支的保護規則

3. 啟用以下選項：

   - ✅ **Require a pull request before merging**
   - ✅ **Require status checks to pass before merging**

4. 在「Status checks that are required」中搜尋並勾選：

   - ✅ `gate-pr-evidence / validate-pr-evidence`
   - ✅ `gate-root-naming / validate_root_naming`

5. 啟用以下額外保護（建議）：

   - ✅ **Require review from Code Owners** (需先設定 CODEOWNERS)
   - ✅ **Require linear history**
   - ✅ **Include administrators** (連管理員也要遵守)

6. 儲存設定

**驗收標準**:

- ✅ 嘗試合併一個檢查失敗的 PR → 應該被阻擋
- ✅ 只有檢查通過的 PR 才能合併
- ✅ 直接 push 到 main 被阻擋

---

## 🧪 測試計畫

### 測試案例 1: 正常流程 ✅

**目的**: 驗證正常的 PR 流程

**步驟**:

1. 創建新分支：`feature/test-normal-flow`
2. 新增一個簡單檔案：`test.md`
3. 提交並推送
4. 開 PR，填入完整的四大證據
5. 等待 Actions 執行完成
6. 確認所有檢查通過（綠勾）
7. 合併 PR

**預期結果**:

- ✅ PR 模板自動載入
- ✅ Actions 檢查通過
- ✅ 可以成功合併

---

### 測試案例 2: 缺失證據 ❌

**目的**: 驗證證據驗證機制

**步驟**:

1. 創建新分支：`feature/test-missing-evidence`
2. 新增一個簡單檔案
3. 開 PR，但**故意不填**四大證據
4. 等待 Actions 執行

**預期結果**:

- ❌ `gate-pr-evidence` 檢查失敗
- 📝 PR 中出現自動評論列出缺失項目
- 🚫 無法合併（如果已啟用分支保護）

---

### 測試案例 3: 命名違規 ❌

**目的**: 驗證命名規範檢查

**步驟**:

1. 創建新分支：`feature/test-naming-violation`
2. 在 `root/` 下新增違規檔案：`root/Root.Config.yaml`（大寫）
3. 開 PR，填入完整證據
4. 等待 Actions 執行

**預期結果**:

- ❌ `gate-root-naming` 檢查失敗
- 📝 PR 中出現自動評論說明違規項目
- 🚫 無法合併

---

## 📱 行動裝置驗證流程

### 在手機上快速驗證 PR（3 分鐘）

1. **打開 PR 頁面**

   - 在 GitHub App 或瀏覽器中打開 PR

2. **檢查證據區塊**（30 秒）

   - 向下滑動到 PR 描述
   - 確認四大證據都有填寫
   - 長按 commit SHA，複製並驗證格式

3. **檢查 Checks 狀態**（30 秒）

   - 在 PR 頂部查看狀態圖示
   - ✅ 綠勾 = 通過
   - ❌ 紅叉 = 失敗（退回）

4. **快速瀏覽 Files Changed**（1 分鐘）

   - 點擊「Files changed」標籤
   - 確認變更檔案與描述一致
   - 確認沒有意外的檔案被修改

5. **決策**（1 分鐘）

   - 通過 → 批准並合併
   - 失敗 → 在 PR 中留言要求修正
   - 疑問 → 標註需要討論

---

## 📊 成功指標

### 短期指標（1 週內）

- ✅ 所有新 PR 都使用模板
- ✅ 90% 的 PR 第一次就填寫完整證據
- ✅ 命名違規能被自動偵測

### 中期指標（1 個月內）

- ✅ 不合規 PR 數量降低 80%
- ✅ PR 審核時間縮短 50%
- ✅ 「找不到交付成果」的情況歸零

### 長期指標（3 個月內）

- ✅ 治理系統成為團隊習慣
- ✅ 新協作者能快速適應流程
- ✅ 架構穩定性顯著提升

---

## 🎓 培訓材料

### 給 AI 代理的指令模板

```markdown
# AI 代理交付指令

當您完成任務後，必須提供以下證據：

1. **repo**: https://github.com/MachineNativeOps/MachineNativeOps
2. **branch**: [您的分支名稱]
3. **commit**: [完整 40 字元 SHA]
4. **PR**: [PR URL]

請在 PR 描述中填入這四項資訊，並確保：

- 所有欄位都填寫真實值（不要留 placeholder）
- commit SHA 是完整的 40 字元
- 如果變更了 root/ 目錄，請勾選第五證據

範例：

- repo: https://github.com/MachineNativeOps/MachineNativeOps
- branch: feature/add-new-module
- commit: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
- PR: https://github.com/MachineNativeOps/MachineNativeOps/pull/123
```

---

## 📞 支援資源

### 文檔連結

- [Root 治理層 README](./root/README.md)
- [代理人交付合約](./root/AGENT_DELIVERY_CONTRACT.md)
- [驗證清單](./root/VALIDATION_CHECKLIST.md)
- [命名規範政策](./root/root.naming-policy.yaml)

### 自動化工具

- [PR 證據驗證](./.github/workflows/gate-pr-evidence.yml)
- [命名規範驗證](./.github/workflows/gate-root-naming.yml)

### 聯絡方式

- **GitHub Issues**: 標註 `治理` 標籤
- **緊急問題**: 標註 `治理緊急` 標籤

---

**實施狀態追蹤**

- [ ] 階段 1: PR 模板部署
- [ ] 階段 2: Actions 自動化
- [ ] 階段 3: 分支保護啟用
- [ ] 測試案例 1-3 全部通過
- [ ] 團隊培訓完成

**版本**: v1.0.0  
**最後更新**: 2025-12-20  
**維護者**: MachineNativeOps 治理委員會
