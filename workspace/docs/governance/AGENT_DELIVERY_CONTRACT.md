# 🤖 AI 代理人交付合約

## 📋 合約目的

本合約建立 AI 代理人在 MachineNativeOps 專案中交付工作的**強制性要求**，確保所有交付物都可被驗證、追溯和審核。

---

## 🔗 證據鏈驗證

### 📋 必要證據項目

每個任務交付**必須**包含以下完整證據鏈：

#### 1. 🚀 Pull Request 證據

```yaml
pr_evidence:
  required: true
  format: 
    - pr_url: "https://github.com/MachineNativeOps/MachineNativeOps/pull/[NUMBER]"
    - pr_title: "[具體的 PR 標題]"
    - pr_description: "[詳細的變更描述]"
  validation:
    - URL 必須可訪問
    - PR 必須處於可合併狀態
    - 描述必須包含具體變更內容
```

#### 2. 🔍 Commit SHA 證據

```yaml
commit_evidence:
  required: true
  format:
    - commit_sha: "[40 字元完整 SHA]"
    - commit_message: "[具體的提交訊息]"
    - branch: "[來源分支名稱]"
  validation:
    - SHA 必須為 40 字元
    - 必須存在於專案歷史中
    - 提交訊息必須具體明確
```

#### 3. 📁 檔案變更證據

```yaml
file_evidence:
  required: true
  format:
    - modified_files: ["檔案路徑列表"]
    - new_files: ["新增檔案路徑列表"]
    - deleted_files: ["刪除檔案路徑列表"]
  validation:
    - 所有檔案路徑必須有效
    - 變更內容必須與任務描述一致
    - 不允許未授權的檔案修改
```

---

## 📋 任務交付要求

### ✅ 完成狀態標準

#### 🎯 可完成任務

```yaml
completion_criteria:
  status: "可完成"
  requirements:
    - 功能完全實現
    - 所有測試通過
    - 文檔完整更新
    - 無已知的 bug 或問題
  deliverables:
    - 完整的程式碼
    - 詳細的實作說明
    - 測試結果報告
    - 部署指引（如適用）
```

#### ❌ 不可完成任務

```yaml
incompletion_criteria:
  status: "不可完成"
  requirements:
    - 明確列出具體阻礙
    - 提供缺失資源清單
    - 不使用模糊語言
    - 給出具體的解決方案建議
  blocking_factors:
    - 缺少的檔案或權限
    - 技術限制或依賴問題
    - 資訊不足或需求不明確
```

---

## 🔍 二元回應機制

### 📊 強制回應格式

所有任務**必須**使用以下嚴格格式：

```yaml
# 🎯 任務狀態回應
task_status:
  type: "[可完成 | 不可完成]"
  
# 若為可完成
completion_deliverable:
  - "[具體的交付物描述]"
  - "[檔案路徑或實作細節]"
  - "[驗證方法或測試結果]"

# 若為不可完成
blocking_factors:
  - factor: "[具體阻礙因素]"
    file_required: "[需要的具體檔案路徑]"
    information_needed: "[需要的具體資訊]"
    solution_suggestion: "[建議的解決方案]"
```

---

## 🚫 禁止行為

### ❌ 絕對禁止的行為

1. **模糊語言使用**
   - "似乎"、"可能"、"看起來像"
   - "大概"、"差不多"、"或許"
   - 任何不確定的陳述

2. **責任推卸**
   - "檔案似乎被截斷了"
   - "可能沒有權限存取"
   - "內容看起來不完整"

3. **不完整交付**
   - 只提供部分解決方案
   - 缺少關鍵實作細節
   - 未提供驗證方法

4. **未經授權的修改**
   - 修改與任務無關的檔案
   - 未經確認直接覆寫現有內容
   - 繞過審核流程

---

## 📝 證據驗證清單

### ✅ 交付前自我檢查

每個任務交付前，AI 代理人**必須**完成以下檢查：

```yaml
pre_delivery_checklist:
  evidence_chain:
    - [ ] PR URL 有效且可訪問
    - [ ] Commit SHA 為完整 40 字元
    - [ ] 所有檔案變更都有記錄
    - [ ] 變更內容與任務描述一致
    
  compliance_check:
    - [ ] 無使用模糊語言
    - [ ] 提供二元回應（可完成/不可完成）
    - [ ] 若不可完成，列出具體缺失
    - [ ] 所有證據都可驗證
    
  quality_assurance:
    - [ ] 程式碼無語法錯誤
    - [ ] 測試覆蓋率達標
    - [ ] 文檔完整且準確
    - [ ] 遵循專案編碼規範
```

---

## ⚖️ 違規處理

### 🚨 合約違規後果

1. **第一次違規**
   - PR 自動被阻擋
   - 要求重新提交並修正
   - 記錄違規行為

2. **第二次違規**
   - 暫停提交權限 24 小時
   - 要求重新審閱合約
   - 增加驗證層級

3. **嚴重違規**
   - 永久取消協作權限
   - 移除所有未合併的變更
   - 通知專案管理團隊

---

## 📞 合約執行支援

### 🔍 驗證工具

- **GitHub Actions 自動驗證**: [`gate-pr-evidence.yml`](../.github/workflows/gate-pr-evidence.yml)
- **PR 模板檢查**: [`pull_request_template.md`](../.github/pull_request_template.md)
- **手動驗證清單**: [`VALIDATION_CHECKLIST.md`](./VALIDATION_CHECKLIST.md)

### 📞 問題回報

如發現合約違規行為：

1. 在 PR 中標註具體違規項目
2. 引用本合約的相關章節
3. 要求代理人修正並重新提交

---

## 📈 合約演進

### 🔄 版本控制

- **當前版本**: v1.0.0
- **更新機制**: 每月審查，必要時即時更新
- **變更通知**: 所有更新都會透過 GitHub Issues 公告

### 📋 改進建議

歡迎提出合約改進建議：

1. 創建 GitHub Issue 標註 "合約改進"
2. 詳細說明建議內容和理由
3. 治理委員會將在下次會議審討

---

**合約狀態**: 🟢 **ACTIVE**  
**執行單位**: MachineNativeOps 治理委員會  
**生效日期**: 2025-12-20  
**審查週期**: 每月一次

---

*本合約確保所有 AI 代理人的交付都符合專案治理要求，維護高品標準和透明度。*
