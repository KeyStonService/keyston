# HLP Executor Core Plugin - 文件索引

## 📚 快速導覽

本目錄包含 HLP Executor Core Plugin 從 `_legacy_scratch/README.md`
解構並整合到 Unmanned Island 系統的完整規劃文件。

---

## 🗂️ 文件結構

```
docs/refactor_playbooks/
├── HLP_EXECUTOR_CORE_INDEX.md                    ← 📍 您在這裡
├── 01_deconstruction/
│   └── HLP_EXECUTOR_CORE_DECONSTRUCTION.md       ← ① 解構分析報告
├── 02_integration/
│   └── HLP_EXECUTOR_CORE_INTEGRATION_MAPPING.md  ← ② 整合映射表
├── 03_refactor/
│   ├── HLP_EXECUTOR_CORE_ACTION_PLAN.md          ← ③ 行動計畫 ⭐ 重點
│   ├── HLP_EXECUTOR_CORE_LEGACY_CLEANUP.md       ← ④ 清理計畫
│   ├── HLP_EXECUTOR_CORE_DIRECTORY_BLUEPRINT.md  ← ⑤ 目錄藍圖
│   └── HLP_EXECUTOR_CORE_INTEGRATION_SUMMARY.md  ← ⑥ 工作總結
└── _legacy_scratch/
    └── README.md                                  ← 原始規格 (548行)
```

---

## 📖 各文件說明

### ① 解構分析報告

**檔案**: `01_deconstruction/HLP_EXECUTOR_CORE_DECONSTRUCTION.md` (8.5 KB)

**用途**: 理解 HLP Executor Core 的完整架構與功能

**內容摘要**:

- ✅ 12個核心概念領域（插件身份、執行模型、狀態機、安全合規等）
- ✅ 5個功能模組解構（執行引擎、狀態管理、回滾、重試、錯誤處理）
- ✅ K8s部署規格（Deployment, RBAC, Storage, Network Policies）
- ✅ 安全與合規（SLSA L3, GDPR, SOC2, Quantum-Safe）
- ✅ 可觀測性（Prometheus, Grafana, OpenTelemetry）
- ✅ 整合點（Quantum Backend, Knowledge Graph）

**何時閱讀**:

- 需要了解 HLP Executor Core 完整功能時
- 開始整合前的背景知識準備

---

### ② 整合映射表

**檔案**: `02_integration/HLP_EXECUTOR_CORE_INTEGRATION_MAPPING.md` (13 KB)

**用途**: 精確了解每個邏輯元件應整合到哪個位置

**內容摘要**:

- ✅ **42項邏輯→目標位置對應表**（含邏輯名稱、說明、目標路徑、角色、優先級）
- ✅ **命名空間適配策略**（axiom-system → unmanned-island-system）
- ✅ **依賴適配方案**（6項核心依賴的映射規則）
- ✅ 引用關係分析（HLP ↔ 現有系統）
- ✅ 潛在衝突與解決方案
- ✅ 整合檢查清單

**何時閱讀**:

- 需要查找某個功能應該放在哪裡時
- 需要了解依賴關係時

---

### ③ P0/P1/P2 行動計畫 ⭐

**檔案**: `03_refactor/HLP_EXECUTOR_CORE_ACTION_PLAN.md` (25 KB)

**用途**: 執行整合的詳細指南（**最重要的文件**）

**內容摘要**:

- ✅ **P0行動清單（10項）**: 立即執行的關鍵任務（1-2天）
  - 插件註冊、模組映射、K8s清單、RBAC、網絡策略、存儲
  - SLSA證據、依賴配置、架構文件、回滾模組
- ✅ **P1行動清單（21項）**: 一週內完成的重要任務（3-7天）
  - Schema、安全政策、監控配置、運維手冊、整合配置、測試
- ✅ **P2行動清單（13項）**: 長期優化任務（2-4週）
  - Grafana、Canary、混沌工程、自動化工具、性能測試
- ✅ 每項任務包含：目標檔案路徑、動作類型、詳細理由、內容要點
- ✅ 3個驗證檢查點（階段一、二、三完成驗證）
- ✅ 整合順序建議

**何時閱讀**:

- **開始執行整合前必讀**
- 需要知道具體要做什麼時
- 需要檢查進度時

**使用方式**:

```bash
# 按照 P0 → P1 → P2 順序執行
# 每完成一個階段，運行對應的驗證腳本
```

---

### ④ 清理計畫

**檔案**: `03_refactor/HLP_EXECUTOR_CORE_LEGACY_CLEANUP.md` (16 KB)

**用途**: 了解何時以及如何清理 legacy_scratch 內容

**內容摘要**:

- ✅ **5階段清理流程**（備份→驗證→標記→存檔→最終清理）
- ✅ **清理前提條件**（必須滿足的檢查項）
- ✅ **Pre-Cleanup Checklist**（25項檢查）
- ✅ **Post-Cleanup Checklist**（6項檢查）
- ✅ 回滾計畫（如果出現問題）
- ✅ 清理時間表（推薦與保守兩種）
- ✅ 特殊情況處理（4種情況）
- ✅ 2個自動化腳本模板
- ✅ 清理決策樹

**何時閱讀**:

- P0 和 P1 完成後，準備清理時
- 需要確認是否可以刪除 legacy_scratch 時

**重要提醒**: ⚠️ 不要在整合完成並驗證前刪除 legacy_scratch 內容

---

### ⑤ 目錄藍圖

**檔案**: `03_refactor/HLP_EXECUTOR_CORE_DIRECTORY_BLUEPRINT.md` (26 KB)

**用途**: 視覺化了解整合後的目錄結構變化

**內容摘要**:

- ✅ **完整目錄樹**（只涵蓋受影響範圍）
- ✅ **按階段劃分的目錄變化**（P0/P1/P2）
- ✅ **檔案統計**:
  - 50個新檔案（10 P0, 23 P1, 17 P2）
  - 9個更新檔案
  - 25個新目錄
- ✅ 目錄所有權與維護責任
- ✅ 整合影響範圍分析
- ✅ 系統架構視圖
- ✅ 3個驗證腳本（目錄、檔案、YAML）
- ✅ 回滾指引（快速/完全回滾）
- ✅ 後續維護指引

**何時閱讀**:

- 需要了解整體變化範圍時
- 需要知道某個目錄是否會受影響時
- 需要執行驗證腳本時

---

### ⑥ 工作總結

**檔案**: `03_refactor/HLP_EXECUTOR_CORE_INTEGRATION_SUMMARY.md` (10.5 KB)

**用途**: 快速了解整個整合工作的概況

**內容摘要**:

- ✅ 執行總覽（6份文件清單）
- ✅ 核心成果統計
- ✅ 命名空間適配完成說明
- ✅ 關鍵特性整合（8項）
- ✅ 執行流程（P0/P1/P2）
- ✅ 驗證標準
- ✅ 清理流程
- ✅ 文件索引
- ✅ 後續建議

**何時閱讀**:

- 需要向他人簡報整合工作時
- 需要快速回顧整體狀況時
- 新加入團隊成員的入門文件

---

## 🚀 快速開始

### 如果你是

#### 📋 專案經理 / Tech Lead

**推薦閱讀順序**:

1. ⑥ 工作總結（了解全貌）
2. ③ 行動計畫（P0部分，了解關鍵任務）
3. ⑤ 目錄藍圖（了解影響範圍）

#### 👨‍💻 實施工程師

**推薦閱讀順序**:

1. ① 解構分析（理解系統）
2. ③ 行動計畫（**必讀**，逐項執行）
3. ② 整合映射（查找具體位置）
4. ⑤ 目錄藍圖（驗證腳本）

#### 🔧 SRE / DevOps

**推薦閱讀順序**:

1. ③ 行動計畫（P0 K8s 部分）
2. ⑤ 目錄藍圖（K8s 清單位置）
3. ④ 清理計畫（清理流程）

#### 📖 文件維護者

**推薦閱讀順序**:

1. ⑥ 工作總結
2. ④ 清理計畫（何時清理 legacy_scratch）
3. 本檔案（索引結構）

---

## 📊 關鍵數據

| 指標               | 數值                          |
| ------------------ | ----------------------------- |
| **原始規格大小**   | 548 行 (Quantum-YAML)         |
| **提取的邏輯元件** | 53 項                         |
| **生成的規劃文件** | 6 份                          |
| **文件總容量**     | ~104 KB                       |
| **新增檔案計畫**   | 50 個 (10 P0 + 23 P1 + 17 P2) |
| **更新檔案計畫**   | 9 個                          |
| **新增目錄計畫**   | 25 個                         |
| **影響的系統模組** | 9 個                          |
| **需適配的依賴**   | 6 項                          |

---

## 🎯 里程碑

### ✅ 已完成

- [x] 完整解構 legacy_scratch README (548 行)
- [x] 提取 53 項邏輯元件
- [x] 創建 6 份專業規劃文件
- [x] 設計 50 個新檔案 + 9 個更新檔案
- [x] 命名空間適配（axiom-system → unmanned-island-system）
- [x] 依賴適配策略（6 項依賴）

### 🔄 進行中

- [ ] 執行 P0 行動（10 項，預計 1-2 天）
- [ ] 執行 P1 行動（21 項，預計 3-7 天）
- [ ] 執行 P2 行動（13 項，預計 2-4 週）

### 📅 計劃中

- [ ] 整合驗證與測試
- [ ] 清理 legacy_scratch
- [ ] 系統穩定性監控

---

## 🔗 相關連結

### 內部文件

- [專案 README](../../../README.md)
- [重構劇本總覽](../README.md)
- [系統架構文件](../../architecture/SYSTEM_ARCHITECTURE.md)
- [配置索引](../../../config/unified-config-index.yaml)

### 外部資源

- [SLSA Framework](https://slsa.dev/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Prometheus Operator](https://prometheus-operator.dev/)

---

## 💡 使用建議

### ✅ Do（推薦做法）

1. ✅ 按照 P0 → P1 → P2 順序執行
2. ✅ 每完成一個階段都要驗證
3. ✅ 參考行動計畫中的內容要點
4. ✅ 遇到問題時查閱整合映射表
5. ✅ 完成 P0+P1 後再考慮清理

### ❌ Don't（避免做法）

1. ❌ 跳過 P0 直接做 P1 或 P2
2. ❌ 不驗證就繼續下一階段
3. ❌ 在整合完成前刪除 legacy_scratch
4. ❌ 偏離既有目錄結構創建新頂層目錄
5. ❌ 修改 business 邏輯

---

## 📞 問題與支援

### 遇到問題時

1. **查閱對應文件**
   - 不知道做什麼？→ 看 ③ 行動計畫
   - 不知道放哪裡？→ 看 ② 整合映射
   - 不知道如何驗證？→ 看 ⑤ 目錄藍圖
   - 不知道如何清理？→ 看 ④ 清理計畫

2. **檢查相關章節**
   - 命名空間問題？→ 看 ② 整合映射 3.1 節
   - 依賴問題？→ 看 ② 整合映射 3.1 節依賴適配表
   - 衝突問題？→ 看 ② 整合映射 3.2 節

3. **參考原始規格**
   - 需要更多細節？→ 查閱 `_legacy_scratch/README.md`

---

## 📝 維護與更新

### 文件維護責任

- **Platform Team**: 整體協調與進度追蹤
- **Architecture Team**: 架構文件更新
- **DevOps Team**: K8s 清單實施
- **Safety Team**: 安全機制實現
- **Documentation Team**: 文件品質保證

### 更新頻率

- **行動計畫**: 每完成一個階段更新進度
- **清理計畫**: 整合完成後更新清理狀態
- **工作總結**: 主要里程碑更新
- **本索引**: 結構變化時更新

---

## 🎉 總結

本套文件從 legacy_scratch 的 548 行規格中完整提取了 HLP Executor Core
Plugin 的所有邏輯，並設計了詳細的整合方案。所有檔案、目錄、依賴、命名空間都已經過仔細規劃，可立即開始執行。

**下一步**: 打開
`03_refactor/HLP_EXECUTOR_CORE_ACTION_PLAN.md`，從 P0-1 開始執行！

---

**版本**: 1.0.0  
**最後更新**: 2025-12-07  
**狀態**: ✅ 規劃完成，可開始實施
