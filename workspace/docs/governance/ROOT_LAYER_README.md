# 🏛️ MachineNativeOps 治理層級

## 📋 治理結構概述

本目錄作為 MachineNativeOps 專案的**治理層級入口點**，採用明確的 `root/` 目錄結構而非隱藏檔案，確保：

- 📱 **行動裝置友善**: 易於在移動設備上管理和驗證
- 🔍 **透明度高**: 所有人都能清楚看到治理結構
- 🚀 **可執行性強**: 具體的執行規則和驗證機制
- 🤖 **AI 友好**: 為第三方 AI 代理提供明確的行為指引

---

## 🗂️ 治理核心檔案

### 📋 配置檔案

- **[`.root.governance.yaml`](../.root.governance.yaml)** - 治理/權限/策略配置
- **[`.root.config.yaml`](../.root.config.yaml)** - 全域基本配置
- **[`.root.modules.yaml`](../.root.modules.yaml)** - 模組註冊管理與相依

### 🔒 安全與信任

- **[`.root.trust.yaml`](../.root.trust.yaml)** - 信任/憑證/安全配置
- **[`.root.integrity.yaml`](../.root.integrity.yaml)** - 整體性驗證規則
- **[`.root.provenance.yaml`](../.root.provenance.yaml)** - 來源追溯與元資料

### ⚡ 執行系統

- **[`.root.super-execution.yaml`](../.root.super-execution.yaml)** - 超級執行/流程定義
- **[`.root.bootstrap.yaml`](../.root.bootstrap.yaml)** - 開機與初始化設定

### 🔧 環境映射

- **[`.root.env.sh`](../.root.env.sh)** - root 使用者殼層環境
- **[`.root.devices.map`](../.root.devices.map)** - 裝置檔案對應表
- **[`.root.fs.map`](../.root.fs.map)** - 系統層級目錄映射
- **[`.root.kernel.map`](../.root.kernel.map)** - 核心模組/函式庫對應

---

## 🤖 AI 代理人治理

### 📝 必讀合約

- **[`AGENT_DELIVERY_CONTRACT.md`](./AGENT_DELIVERY_CONTRACT.md)** - 代理人交付合約
- **[`.github/AI-BEHAVIOR-CONTRACT.md`](../.github/AI-BEHAVIOR-CONTRACT.md)** - AI 行為合約

### 🔄 工作流程

1. **任務接收** → 檢查是否在能力範圍內
2. **二元回應** → 可完成/不可完成 + 具體缺失
3. **證據提供** → 必須提供可驗證的證據鏈
4. **合約遵循** → 嚴格遵守 AI 行為合約

---

## 🚪 PR 閘門機制

### ✅ 必要條件

所有 Pull Request 必須通過以下閘門：

1. **🔍 證據驗證閘門**
   - 必須提供完整的證據連結
   - 包含有效的 PR URL 和 Commit SHA
   - 驗證所有連結的可訪問性

2. **🤖 AI 合約遵循閘門**
   - 檢查是否遵循 AI 行為合約
   - 驗證二元回應機制
   - 確認無模糊語言使用

3. **📱 行動友善性閘門**
   - 檔案結構易於在手機上驗證
   - 重要的配置檔案可及性
   - 目錄深度合理化

---

## 📊 治理指標

### 🔍 監控指標

- **PR 通過率**: 目標 > 95%
- **合約遵循率**: 目標 100%
- **證據完整性**: 目標 100%
- **移動驗證效率**: 目標 < 3 分鐘

### 📈 持續改進

- 每月審查治理效能
- 根據實際使用情況調整規則
- 收集使用者回饋優化體驗

---

## 🆘 快速協助

### 📞 治理支援

- **問題回報**: 創建 GitHub Issue
- **規則詮釋**: 查看對應配置檔案註解
- **緊急聯絡**: 透過系統管理員

### 🔧 常見問題

1. **Q**: 為什麼選擇 `root/` 而不是 `.` 開頭的隱藏檔案？
   **A**: 行動裝置上更容易查看和管理，提高透明度。

2. **Q**: AI 代理人不遵守合約怎麼辦？
   **A**: PR 閘門會自動阻擋不合規的變更。

3. **Q**: 如何在行動裝置上快速驗證證據？
   **A**: 使用 PR 模板中的連結直接跳轉驗證。

---

## 📞 聯絡資訊

**維護團隊**: MachineNativeOps 治理委員會  
**更新頻率**: 每月審查，必要時即時更新  
**版本**: v1.0.0  
**最後更新**: 2025-12-20

---

*本治理層級確保 MachineNativeOps 專案在多協作者環境下保持高品質、透明度和可執行性。*
