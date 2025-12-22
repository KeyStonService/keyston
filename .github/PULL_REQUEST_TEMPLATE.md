<!-- 
🚪 MachineNativeOps PR 閘門模板
遵循此模板確保通過所有驗證閘門
-->

## 📋 任務描述

### 🎯 任務目標
<!-- 請簡要描述這個 PR 的主要目標 -->
[描述任務目標...]

### 📊 變更範圍
<!-- 列出所有變更的檔案和影響範圍 -->
```yaml
modified_files:
  - path/to/modified/file.ext
  - 其他變更檔案...

new_files:
  - 新增檔案...

deleted_files:
  - 刪除檔案...
```

### ⚡ 實作方法
<!-- 簡要說明實作方式和技術決策 -->
[說明實作方法...]

---

## 🔗 證據連結 **[必填 - 缺一不可]**

### 📋 四大核心證據
```yaml
- repo: https://github.com/MachineNativeOps/machine-native-ops-aaps
- branch: [分支名稱]
- commit: [完整40字元Commit SHA]
- PR: https://github.com/MachineNativeOps/machine-native-ops-aaps/pull/[PR編號]
```

### 🏛️ 第五證據：命名規範遵循 **[若變更根層檔案則必填]**

- [ ] N/A - 無根層檔案變更
- [ ] ✅ 已遵循 `root.naming-policy.yaml` 規範
- [ ] ❌ 未遵循命名規範（請說明原因）

---

## 📝 AI 行為合約遵循 **[必填]**

### ✅ 二元回應遵循

- [ ] ✅ **可完成 / 不可完成** 二元回應
- [ ] ✅ **具體缺失資源清單**
- [ ] ✅ **無模糊語言**
- [ ] ✅ **草稿模式遵循**

### 🔍 證據鏈驗證

- [ ] ✅ **PR URL 可驗證且可訪問**
- [ ] ✅ **Commit SHA 為完整 40 字元**
- [ ] ✅ **所有檔案變更都有記錄**
- [ ] ✅ **變更內容與任務描述一致**

### 📱 行動裝置友善性

- [ ] ✅ **檔案結構易於在手機上驗證**
- [ ] ✅ **重要配置檔案可及性**
- [ ] ✅ **目錄深度合理化**

---

## 🔄 治理合約檢查

### 📋 根層治理遵循

- [ ] ✅ 遵循 [`docs/governance/AGENT_DELIVERY_CONTRACT.md`](./docs/governance/AGENT_DELIVERY_CONTRACT.md)
- [ ] ✅ 符合 [`ROOT_ARCHITECTURE.md`](./ROOT_ARCHITECTURE.md) 架構要求
- [ ] ✅ 相容 [`root.governance.yaml`](./root.governance.yaml) 規則

### 🤖 AI 行為合約遵循
- [ ] ✅ 遵循 [`.github/AI-BEHAVIOR-CONTRACT.md`](./.github/AI-BEHAVIOR-CONTRACT.md)
- [ ] ✅ 無合約第 1 節違規 (模糊語言)
- [ ] ✅ 無合約第 2 節違規 (二元回應)
- [ ] ✅ 無合約第 3 節違規 (任務拆解)
- [ ] ✅ 無合約第 4 節違規 (草稿模式)

---

## ✅ 完成狀態

### 🎯 任務完成度

- [ ] ✅ **功能完全實現**
- [ ] ✅ **所有測試通過**
- [ ] ✅ **文檔完整更新**
- [ ] ✅ **無已知 bug 或問題**

### 📊 品質指標
- **程式碼覆蓋率**: [數字]%
- **效能測試**: [通過/失敗]
- **安全掃描**: [通過/失敗]
- **文檔完整性**: [完整/部分/缺失]

---

## 🔍 審核者檢查清單

### ✅ 技術審核
- [ ] ✅ 程式碼品質符合專案標準
- [ ] ✅ 架構設計合理
- [ ] ✅ 測試覆蓋率足夠
- [ ] ✅ 效能表現符合預期

### 📋 治理審核

- [ ] ✅ 證據鏈完整且可驗證
- [ ] ✅ AI 合約遵循無違規
- [ ] ✅ 文檔更新完整
- [ ] ✅ 行動裝置友善性確認

### 🔒 安全審核

- [ ] ✅ 無安全漏洞引入
- [ ] ✅ 權限控制適當
- [ ] ✅ 敏感資訊處理正確
- [ ] ✅ 合規性要求滿足

---

## 📞 聯絡資訊

**主要負責人**: [負責人名稱]  
**審核者**: @MachineNativeOps  
**相關 Issue**: #[Issue編號]  
**預計合併時間**: [日期時間]

---

## 🚨 注意事項

⚠️ **重要提醒**: 
1. 提交前請確保所有必填項目已完整填寫
2. 所有證據連結必須可訪問且有效
3. 遵循機率性開發原則，接受失敗的可能性
4. 如遇問題可聯絡治理委員會

📱 **行動裝置使用者**: 
- 可使用長按複製連結快速驗證
- 建議在 WiFi 環境下進行證據驗證
- 如遇問題可聯絡治理委員會

---

## 🔄 狀態說明

### 狀態標記規範

- ✅ **已完成**: 該項目已完成並驗證
- ⏸️ **受阻中**: 該項目因外部因素暫停
- 🔄 **進行中**: 該項目正在處理
- ❌ **失敗**: 該項目失敗需要修正
- ⏭️ **跳過**: 該項目不適用當前情境

### 邏輯一致性規則

1. **受阻狀態**: 若任務受阻，所有相關審核項目都應標記為 ⏸️
2. **進行中狀態**: 若任務進行中，相關審核項目可標記為 🔄 或空白
3. **完成狀態**: 若任務完成，所有相關審核項目都應標記為 ✅
4. **失敗狀態**: 若任務失敗，相關審核項目都應標記為 ❌

---

*提交此 PR 即表示您同意遵循 MachineNativeOps 治理合約和 AI 行為合約的所有規定。*

<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instructions, customizing your development environment and configuring Model Context Protocol (MCP) servers. Learn more [Copilot coding agent tips](https://gh.io/copilot-coding-agent-tips) in the docs.