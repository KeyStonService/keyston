# 🏗️ 系統架構說明 (System Architecture)

> **版本**: 1.0.0  
> **最後更新**: 2025-12-21 02:13:25
> **狀態**: 🟢 Active  
> **自動更新**: 啟用

---

## 📋 目錄

1. [總覽](#總覽)
2. [Root Layer 架構](#root-layer-架構)
3. [檔案結構](#檔案結構)
4. [資料流程](#資料流程)
5. [模組關係](#模組關係)
6. [驗證系統](#驗證系統)
7. [自動化系統](#自動化系統)

---

## 🎯 總覽

### 系統定位

MachineNativeOps 是一個**企業級治理框架**，專注於 Root Layer 的配置管理、驗證和自動化。

### 核心價值

- ✅ **機器可驗證** - 所有規則都可自動執行
- ✅ **單一事實來源** - 註冊表作為權威資料
- ✅ **自動化執行** - GitHub Actions 自動驗證
- ✅ **持續記憶** - 自動更新專案知識

### 設計原則

1. **配置即代碼** (Configuration as Code)
2. **驗證優先** (Validation First)
3. **自動化一切** (Automate Everything)
4. **記憶持續** (Continuous Memory)

---

## 🏛️ Root Layer 架構

### 三層架構設計

```
┌─────────────────────────────────────────────────────────┐
│                    應用層 (Application)                   │
│  - 業務邏輯                                               │
│  - 用戶介面                                               │
│  - API 服務                                               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   治理層 (Governance)                     │
│  - 規範定義 (root.specs.*.yaml)                          │
│  - 驗證系統 (validate-root-specs.py)                     │
│  - 閘門控制 (gate-root-specs.yml)                        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Root Layer (基礎層)                     │
│  - 全域配置 (root.config.yaml)                           │
│  - 模組註冊 (root.registry.modules.yaml)                 │
│  - 信任鏈 (root.trust.yaml)                              │
│  - 完整性驗證 (root.integrity.yaml)                      │
└─────────────────────────────────────────────────────────┘
```

### Root Layer 組成

#### 1. 配置檔案層 (Configuration Files)

```yaml
root.config.yaml          # 全域配置
root.governance.yaml      # 治理規則
root.modules.yaml         # 模組配置
root.trust.yaml           # 信任鏈
root.provenance.yaml      # 來源追溯
root.integrity.yaml       # 完整性驗證
root.bootstrap.yaml       # 啟動配置
root.naming-policy.yaml   # 命名政策
```

**職責**: 定義系統行為和配置
**更新頻率**: 低 (架構變更時)
**驗證**: 所有變更必須通過 gate-root-specs

#### 2. 規範檔案層 (Specification Files)

```yaml
root.specs.naming.yaml      # 命名規範
root.specs.references.yaml  # 引用規範
root.specs.mapping.yaml     # 映射規範
root.specs.logic.yaml       # 邏輯規範
root.specs.context.yaml     # 上下文規範
```

**職責**: 定義驗證規則
**更新頻率**: 中 (規則調整時)
**驗證**: 規範變更需要治理委員會審核

#### 3. 註冊表層 (Registry Files - SSOT)

```yaml
root.registry.modules.yaml  # 模組註冊表
root.registry.urns.yaml     # URN 註冊表
```

**職責**: 作為唯一事實來源
**更新頻率**: 高 (新增/修改模組時)
**驗證**: 嚴格的一致性檢查

#### 4. 映射檔案層 (Mapping Files)

```
root.devices.map    # 設備映射
root.fs.map         # 檔案系統映射
root.kernel.map     # 核心模組映射
```

**職責**: 定義資源映射關係
**更新頻率**: 低 (系統架構變更時)
**驗證**: 映射完整性檢查

#### 5. 環境檔案層 (Environment Files)

```bash
root.env.sh         # Shell 環境設定
```

**職責**: 定義執行環境
**更新頻率**: 低 (環境變更時)
**驗證**: Shell 語法檢查

---

## 📂 檔案結構

### 完整目錄樹

```
MachineNativeOps/
│
├── 📋 Root Layer 配置 (13 files)
│   ├── root.config.yaml
│   ├── root.governance.yaml
│   ├── root.modules.yaml
│   ├── root.trust.yaml
│   ├── root.provenance.yaml
│   ├── root.integrity.yaml
│   ├── root.bootstrap.yaml
│   ├── root.naming-policy.yaml
│   ├── root.devices.map
│   ├── root.fs.map
│   ├── root.kernel.map
│   ├── root.env.sh
│   └── gates.map.yaml
│
├── 📋 規範檔案 (5 files)
│   ├── root.specs.naming.yaml
│   ├── root.specs.references.yaml
│   ├── root.specs.mapping.yaml
│   ├── root.specs.logic.yaml
│   └── root.specs.context.yaml
│
├── 📦 註冊表 (2 files - SSOT)
│   ├── root.registry.modules.yaml
│   └── root.registry.urns.yaml
│
├── 🧠 記憶系統 (4 files)
│   ├── PROJECT_MEMORY.md
│   ├── ARCHITECTURE.md (本檔案)
│   ├── CONVERSATION_LOG.md
│   └── ACCEPTANCE_CHECKLIST.md
│
├── 📚 文檔 (3 files)
│   ├── ROOT_SPECS_GUIDE.md
│   ├── ROOT_ARCHITECTURE.md
│   └── ROOT_SPECS_IMPLEMENTATION_REPORT.md
│
├── 🔍 驗證系統
│   ├── scripts/validation/
│   │   └── validate-root-specs.py
│   └── .github/workflows/
│       ├── gate-root-specs.yml
│       ├── gate-pr-evidence.yml
│       └── gate-root-naming.yml
│
├── 🚀 初始化系統
│   └── init.d/
│       ├── 00-init.sh
│       ├── 01-governance-init.sh
│       ├── 02-modules-init.sh
│       ├── 03-super-execution-init.sh
│       ├── 04-trust-init.sh
│       ├── 05-provenance-init.sh
│       ├── 06-database-init.sh
│       ├── 07-config-init.sh
│       ├── 08-dependencies-init.sh
│       ├── 09-logging-init.sh
│       ├── 10-security-init.sh
│       ├── 11-multiplatform-init.sh
│       ├── 12-api-gateway-init.sh
│       ├── 13-services-init.sh
│       └── 99-finalize.sh
│
└── 🗂️ FHS 標準目錄
    ├── bin/
    ├── sbin/
    ├── etc/
    ├── lib/
    ├── var/
    ├── usr/
    ├── home/
    ├── tmp/
    ├── opt/
    └── srv/
```

### 檔案命名規範

#### Root Layer 檔案

- **格式**: `root.<category>.<ext>`
- **範例**: `root.config.yaml`, `root.devices.map`
- **規則**:
  - 必須小寫
  - 使用 `.yaml` 而非 `.yml`
  - 不可包含空白或大寫

#### 規範檔案

- **格式**: `root.specs.<category>.yaml`
- **範例**: `root.specs.naming.yaml`
- **規則**:
  - 必須在 root.specs. 命名空間下
  - category 使用 kebab-case

#### 註冊表檔案

- **格式**: `root.registry.<type>.yaml`
- **範例**: `root.registry.modules.yaml`
- **規則**:
  - 必須在 root.registry. 命名空間下
  - 作為 SSOT，不可重複定義

---

## 🔄 資料流程

### 1. 開發流程

```
┌─────────────┐
│ 開發者修改   │
│ root.*.yaml │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  創建 PR    │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│     GitHub Actions 自動觸發          │
│  1. gate-pr-evidence.yml            │
│  2. gate-root-naming.yml            │
│  3. gate-root-specs.yml             │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│        執行驗證                      │
│  - 命名規範檢查                      │
│  - 引用格式檢查                      │
│  - 映射一致性檢查                    │
│  - 邏輯完整性檢查                    │
│  - 上下文一致性檢查                  │
└──────┬──────────────────────────────┘
       │
       ↓
    通過？
    /    \
   是     否
   │      │
   │      ↓
   │   ┌─────────────┐
   │   │ PR 被阻擋   │
   │   │ 顯示錯誤    │
   │   └─────────────┘
   │
   ↓
┌─────────────┐
│  可以合併   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 合併到 main │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│      自動更新記憶系統                │
│  - PROJECT_MEMORY.md                │
│  - CONVERSATION_LOG.md              │
│  - ARCHITECTURE.md                  │
└─────────────────────────────────────┘
```

### 2. 驗證流程

```
┌─────────────────┐
│  PR 觸發驗證    │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      載入規範檔案                    │
│  - root.specs.naming.yaml           │
│  - root.specs.references.yaml       │
│  - root.specs.mapping.yaml          │
│  - root.specs.logic.yaml            │
│  - root.specs.context.yaml          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      載入註冊表                      │
│  - root.registry.modules.yaml       │
│  - root.registry.urns.yaml          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      載入 Root 檔案                  │
│  - root.*.yaml (9 files)            │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      執行 5 類驗證                   │
│  1. 命名規範驗證                     │
│  2. 引用格式驗證                     │
│  3. 映射一致性驗證                   │
│  4. 邏輯完整性驗證                   │
│  5. 上下文一致性驗證                 │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      生成驗證報告                    │
│  - root-specs-validation-report.md  │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      更新 PR 狀態                    │
│  - 通過: ✅ 綠色勾勾                 │
│  - 失敗: ❌ 紅色叉叉 + 詳細報告      │
└─────────────────────────────────────┘
```

### 3. 記憶更新流程 (自動化)

```
┌─────────────────┐
│  代碼合併到 main │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      分析變更內容                    │
│  - 新增了哪些檔案？                  │
│  - 修改了哪些配置？                  │
│  - 刪除了哪些內容？                  │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      提取關鍵資訊                    │
│  - 功能變更                          │
│  - 架構調整                          │
│  - 決策記錄                          │
│  - 問題修復                          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      更新記憶文檔                    │
│  - PROJECT_MEMORY.md                │
│    * 更新功能清單                    │
│    * 記錄已知問題                    │
│    * 更新下一步計劃                  │
│  - CONVERSATION_LOG.md              │
│    * 記錄變更摘要                    │
│    * 記錄決策原因                    │
│  - ARCHITECTURE.md                  │
│    * 更新架構圖                      │
│    * 更新檔案結構                    │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────┐
│  自動提交變更   │
└─────────────────┘
```

---

## 🔗 模組關係

### 模組依賴圖

```
config-manager (核心)
    ↓
    ├─→ logging-service
    │       ↓
    │       ├─→ governance-engine
    │       │       ↓
    │       │       └─→ super-execution-engine
    │       │
    │       ├─→ provenance-tracker
    │       │
    │       └─→ monitoring-service
    │
    ├─→ trust-manager
    │       ↓
    │       └─→ integrity-validator
    │
    └─→ (其他模組)
```

### 模組載入順序

1. **config-manager** (優先級: 100)
   - 無依賴
   - 提供: 配置驗證、載入、監控

2. **logging-service** (優先級: 90)
   - 依賴: config-manager
   - 提供: 結構化日誌、聚合、輪轉

3. **trust-manager** (優先級: 90)
   - 依賴: config-manager, crypto-provider, storage-backend
   - 提供: 證書管理、信任鏈驗證、金鑰輪轉

4. **governance-engine** (優先級: 80)
   - 依賴: config-manager, logging-service, database-connector
   - 提供: 政策執行、RBAC 管理、審計日誌

5. **provenance-tracker** (優先級: 70)
   - 依賴: config-manager, logging-service, database-connector
   - 提供: 審計軌跡、來源追溯、事件溯源

6. **integrity-validator** (優先級: 70)
   - 依賴: config-manager, crypto-provider
   - 提供: 雜湊驗證、完整性檢查、篡改檢測

7. **super-execution-engine** (優先級: 60)
   - 依賴: config-manager, logging-service, governance-engine
   - 提供: 工作流編排、任務調度、執行監控

8. **monitoring-service** (優先級: 50)
   - 依賴: config-manager, logging-service
   - 提供: 指標收集、健康監控、告警

### 模組通訊

```
┌─────────────────┐
│ Application     │
└────────┬────────┘
         │ API Calls
         ↓
┌─────────────────────────────────────┐
│     super-execution-engine          │
│  (工作流編排)                        │
└────────┬────────────────────────────┘
         │
         ├─→ governance-engine (政策檢查)
         │
         ├─→ provenance-tracker (記錄追溯)
         │
         ├─→ integrity-validator (完整性驗證)
         │
         └─→ monitoring-service (監控)
                 │
                 ↓
         ┌─────────────────┐
         │ logging-service │
         │  (集中日誌)      │
         └─────────────────┘
```

---

## 🔍 驗證系統

### 驗證層級

#### Level 1: 語法驗證

- **檢查項目**: YAML 語法、檔案格式
- **工具**: Python yaml.safe_load()
- **執行時機**: PR 創建時
- **失敗處理**: 立即阻擋

#### Level 2: 命名驗證

- **檢查項目**: 檔名、鍵名、值名
- **工具**: Regex 模式匹配
- **執行時機**: PR 創建時
- **失敗處理**: 阻擋 + 提供修復建議

#### Level 3: 引用驗證

- **檢查項目**: URN 格式、引用存在性
- **工具**: 註冊表查詢
- **執行時機**: PR 創建時
- **失敗處理**: 阻擋 + 列出缺失引用

#### Level 4: 邏輯驗證

- **檢查項目**: 循環依賴、狀態一致性
- **工具**: DFS 算法、拓撲排序
- **執行時機**: PR 創建時
- **失敗處理**: 阻擋 + 顯示循環路徑

#### Level 5: 上下文驗證

- **檢查項目**: 跨檔案一致性、漂移檢測
- **工具**: 相似度分析
- **執行時機**: PR 創建時
- **失敗處理**: 警告或阻擋 (視嚴重程度)

### 驗證工具鏈

```
┌─────────────────────────────────────┐
│     validate-root-specs.py          │
│  (Python 驗證器)                     │
│                                      │
│  ├─ load_specifications()           │
│  ├─ load_registries()               │
│  ├─ load_root_files()               │
│  ├─ validate_naming_spec()          │
│  ├─ validate_references_spec()      │
│  ├─ validate_mapping_spec()         │
│  ├─ validate_logic_spec()           │
│  ├─ validate_context_spec()         │
│  └─ generate_report()               │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│     gate-root-specs.yml             │
│  (GitHub Actions 工作流)             │
│                                      │
│  ├─ Naming Validation               │
│  ├─ Reference Validation            │
│  ├─ Mapping Validation              │
│  ├─ Logic Validation                │
│  ├─ Context Validation              │
│  └─ Python Validator                │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  root-specs-validation-report.md    │
│  (驗證報告)                          │
└─────────────────────────────────────┘
```

---

## 🤖 自動化系統

### 自動化層級

#### Level 1: 自動驗證

- **觸發**: PR 創建/更新
- **執行**: GitHub Actions
- **結果**: 通過/失敗 + 報告

#### Level 2: 自動記憶更新

- **觸發**: 合併到 main
- **執行**: GitHub Actions
- **結果**: 更新 PROJECT_MEMORY.md

#### Level 3: 自動架構同步

- **觸發**: 檔案結構變更
- **執行**: GitHub Actions
- **結果**: 更新 ARCHITECTURE.md

#### Level 4: 自動對話記錄

- **觸發**: PR 合併
- **執行**: GitHub Actions
- **結果**: 更新 CONVERSATION_LOG.md

#### Level 5: 自動知識萃取

- **觸發**: 重大變更
- **執行**: AI 分析
- **結果**: 更新知識圖譜

### 自動化工作流

```yaml
# .github/workflows/auto-memory-update.yml
name: Auto Memory Update

on:
  push:
    branches: [main]

jobs:
  update-memory:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
      - name: Analyze Changes
      - name: Update PROJECT_MEMORY.md
      - name: Update CONVERSATION_LOG.md
      - name: Update ARCHITECTURE.md
      - name: Commit Changes
```

---

## 📊 架構決策記錄 (ADR)

### ADR-001: 採用 YAML 作為配置格式

- **日期**: 2024-12-20
- **狀態**: ✅ 已採用
- **決策**: 使用 YAML 作為所有配置檔案格式
- **理由**: 人類可讀、支援註解、工具豐富
- **影響**: 所有配置必須是有效的 YAML

### ADR-002: 建立 SSOT 註冊表

- **日期**: 2024-12-21
- **狀態**: ✅ 已採用
- **決策**: 創建 root.registry.*.yaml 作為唯一事實來源
- **理由**: 避免資料重複和不一致
- **影響**: 所有模組資訊必須先在註冊表定義

### ADR-003: 使用 URN 作為引用格式

- **日期**: 2024-12-21
- **狀態**: ✅ 已採用
- **決策**: 採用 URN 格式作為主要引用方式
- **理由**: 全域唯一、版本控制、類型安全
- **影響**: 所有引用必須使用 URN 格式

### ADR-004: 自動化 PR 阻擋

- **日期**: 2024-12-21
- **狀態**: ✅ 已採用
- **決策**: 使用 GitHub Actions 自動阻擋不合規 PR
- **理由**: 即時反饋、防止錯誤、減少人工負擔
- **影響**: 所有 PR 必須通過驗證

### ADR-005: 建立自動記憶系統

- **日期**: 2024-12-21
- **狀態**: 🔄 實施中
- **決策**: 建立自動更新的記憶系統
- **理由**: 防止知識碎片化、維持上下文連續性
- **影響**: 每次變更都會更新記憶文檔

---

## 🔄 版本歷史

### v1.0.0 (2024-12-21)

- ✅ 完成 Root Layer 規範系統
- ✅ 建立 5 個規範檔案
- ✅ 建立 2 個註冊表檔案
- ✅ 實現自動化驗證系統
- ✅ 創建統一閘門映射
- ✅ 完成完整文檔系統

- 🔄 修復 monitoring-service 不一致問題 (2025-12-21 02:13:25)

### v1.1.0 (計劃中)

- 📋 實現自動記憶更新
- 📋 建立知識圖譜
- 📋 增強驗證覆蓋率
- 📋 優化自動化流程

---

## 📞 維護資訊

### 文檔維護

- **負責人**: MachineNativeOps Governance Team
- **更新頻率**: 自動更新 (每次 commit)
- **手動審查**: 每月一次

### 架構審查

- **頻率**: 每季度
- **參與者**: 技術委員會
- **輸出**: 架構改進建議

---

**文檔版本**: 1.0.0  
**最後更新**: 2024-12-21  
**自動更新**: 🟢 啟用  
**維護者**: AI Agent + Automation System
