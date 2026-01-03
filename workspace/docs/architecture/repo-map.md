# SynergyMesh Repository Map

# 倉庫地圖與語義邊界

> 本文件為智能體和開發者提供「世界觀」參考：整個系統的架構與互動都以此 monorepo 及其內部結構為唯一真相與唯一操作介面。
> This document provides the "worldview" for agents and developers: the entire system's architecture and interactions use this monorepo and its internal structure as the single source of truth and operation interface.

## 🌍 System Worldview 系統世界觀

### 1. Single Source of Truth 單一真相來源

整個 SynergyMesh 平台的架構、模組邊界、能力定義，全部以本 monorepo 的以下內容為唯一來源：

- **目錄結構** Directory structure
- **源碼文件** Source code files
- **配置文件** Configuration files (`config/*.yml`, `*.json`, etc.)
- **架構/治理文檔** Architecture/governance docs (`docs/**`, `governance/**`)

**Important 重要**: 不得假設 repo 外還存在其他隱形系統架構。

### 2. Actual Repository Surface Snapshot 實際目錄快照

> 來源: repository root 的目錄列表（例如 `ls` 或 `dir`）  
> 作用: 提供 AI 代理與開發者快速對照「真實存在的目錄」與上層語義邊界

| 分類 / Category | 主要目錄 / Key directories                              | 備註 / Notes                                                                                                                                             |
| --------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 核心平台        | `core/`, `runtime/`, `shared/`                          | AI 決策、整合層、運行時、共用資源                                                                                                                        |
| 自動化          | `automation/`                                           | 智能/超自動化、架構骨架、零接觸部署（含 `automation/pipelines/` 子模組）                                                                                 |
| 自主/無人       | `autonomous/`, `v1-python-drones/`, `v2-multi-islands/` | 無人機與多島嶼框架                                                                                                                                       |
| 服務/代理       | `services/`, `agent/`, `mcp-servers/`                   | 長生命週期代理、MCP 工具端點                                                                                                                             |
| 前端/應用       | `frontend/`, `apps/`                                    | UI 套件與 Web 應用                                                                                                                                       |
| 治理/政策       | `governance/`, `config/`                                | 23 維治理矩陣（涵蓋 00-40 等治理維度，詳見 `governance/` 子目錄與 `config/system-module-map.yaml`）與統一配置/模組映射 (`config/system-module-map.yaml`) |
| 基礎設施        | `infrastructure/`, `infra/`, `deployment/`              | K8s、監控、canary、部署腳本                                                                                                                              |
| 測試/質量       | `tests/`, `scripts/`, `tools/`                          | 單元/性能測試、輔助腳本、CI 工具                                                                                                                         |
| 文檔            | `docs/`, `knowledge/`                                   | 文件、索引、報告；生成文件集中於 `docs/generated/`                                                                                                       |
| 其他歷史資產    | `legacy/`, `experiments/`, `supply-chain/`, `bridges/`  | 歷史遺留與橋接實驗                                                                                                                                       |

> ⚠️ 如需完整樹狀結構（含檔案層級），請參考已存在的
> `docs/DIRECTORY_TREE.md`。若需語義對應與治理邊界，請依此文檔與
> `config/system-module-map.yaml`。

---

## 🎯 Semantic Boundaries 語義邊界

### AI/Agent Module Boundaries AI/代理模組邊界

這是最常見的混淆區域。以下是明確的語義分工：

#### `core/` - Platform-Level AI Capabilities 平台級 AI 能力

**負責 Responsible for:**

- AI 決策引擎 (`ai_decision_engine.py`)
- 上下文理解引擎 (`context_understanding_engine.py`)
- 虛擬專家系統 (`virtual_experts/`)
- 訓練系統 (`training_system/`)
- 幻覺檢測 (`hallucination_detector.py`)

**不負責 NOT responsible for:**

- 具體業務 pipeline（這些在 `automation/intelligent/`）
- LLM 工具端點（這些在 `mcp-servers/`）
- 業務代理編排（這些在 `agent/`）

**應依賴 Should depend on:**

- `shared/`
- `runtime/`

**不應依賴 Should NOT depend on:**

- `automation/`
- `agent/`
- `mcp-servers/`

---

#### `mcp-servers/` - LLM Tool Endpoints LLM 工具端點

**負責 Responsible for:**

- 提供 LLM 可調用的工具（MCP 協議）
- 代碼分析端點 (`code-analyzer.js`)
- SLSA 驗證端點 (`slsa-validator.js`)
- 安全掃描端點 (`security-scanner.js`)
- 文檔生成端點 (`doc-generator.js`)

**不負責 NOT responsible for:**

- 核心業務邏輯實作
- 長生命週期代理狀態管理
- 複雜工作流編排

**應依賴 Should depend on:**

- 可調用 `core/` 提供的能力

**不應依賴 Should NOT depend on:**

- `agent/` 的業務代理
- `automation/intelligent/` 的 pipeline

---

#### `agent/` - Business Agents 業務代理

**負責 Responsible for:**

- 長生命週期業務代理
- 自動修復代理 (`auto-repair/`)
- 代碼分析代理 (`code-analyzer/`)
- 編排器 (`orchestrator/`)
- 漏洞檢測代理 (`vulnerability-detector/`)

**不負責 NOT responsible for:**

- LLM 工具端點（使用 `mcp-servers/`）
- 平台級 AI 能力（使用 `core/`）
- Pipeline 組合（使用 `automation/intelligent/`）

**應依賴 Should depend on:**

- `core/` 的平台能力
- `mcp-servers/` 的工具端點

**不應依賴 Should NOT depend on:**

- 直接實作 LLM 協議

---

#### `automation/intelligent/` - Product Pipelines 產品級 Pipeline

**負責 Responsible for:**

- 多代理 AI 代碼分析系統
- 具體 pipeline 組合（code pipeline、review pipeline）
- SynergyMesh Core 自主協同系統
- 產品級工作流

**不負責 NOT responsible for:**

- 平台級 AI 引擎（使用 `core/`）
- LLM 端點實作（使用 `mcp-servers/`）
- 單一代理實作（使用 `agent/`）

**應依賴 Should depend on:**

- `core/`
- `mcp-servers/`
- `agent/`

---

### Contract/Schema Boundaries 合約/Schema 邊界

#### `core/contract_service/` (原 `core/contract_service/`)

**負責 Responsible for:**

- 合約管理微服務的程式碼
- L1 合約服務實作
- AI 聊天服務整合

**不負責 NOT responsible for:**

- 外部 API 合約定義（這些在 `contracts/`）

---

#### `contracts/`

**負責 Responsible for:**

- 外部 API 合約定義（OpenAPI specs）
- Schema 資料文件
- 介面規格定義

**不負責 NOT responsible for:**

- 實作代碼
- 服務邏輯

---

### Execution/Runtime Boundaries 執行/運行時邊界

#### `runtime/`

**負責 Responsible for:**

- 實際運行時環境
- Mind Matrix runtime
- 部署時啟動的組件

**與 `core/execution_*` 的關係:**

- `runtime/` = 實際部署、啟動、承載 execution 的環境
- `core/execution_engine/` = 提供執行邏輯的抽象
- `core/execution_architecture/` = 定義執行拓撲/設計

---

## 📋 Quick Decision Guide 快速決策指南

### "我要改一個 agent 邏輯，要去哪裡？"

| 情境 Scenario | 目錄 Directory |
|--------------|----------------|
| 改 LLM 工具的輸入/輸出格式 | `mcp-servers/` |
| 改業務代理的行為邏輯 | `agent/` |
| 改平台級 AI 決策規則 | `core/` |
| 改 pipeline 編排流程 | `automation/intelligent/` |

### "我要加一個新功能，放哪裡？"

1. **是 LLM 可調用的工具嗎？** → `mcp-servers/`
2. **是長生命週期的業務代理嗎？** → `agent/`
3. **是平台級共用 AI 能力嗎？** → `core/`
4. **是產品級 pipeline 組合嗎？** → `automation/intelligent/`

---

## 🔒 Invariants 不變量規則

### 變更限制 Change Constraints

1. **不得刪除任何檔案**，只能移動或標記為 deprecated
2. **不得修改函式對外介面**（API 參數/回傳值/HTTP path），除非明確要求
3. **任何目錄重命名**，必須同步修正所有引用（import, include, path）
4. **所有變更必須表現為 repo 變更**，可用 `git diff` 表示

### 驗證方式 Validation

所有變更完成後，必須：

- 通過專案測試命令（`npm test`, `npm run lint`）
- 更新相關文檔，使 repo 自身能解釋新結構

---

## 📝 Document History 文檔歷史

| Date 日期 | Version 版本 | Changes 變更 |
|-----------|-------------|--------------|
| 2025-11-30 | 1.0.0 | Initial repository map document |

---

**Maintainer 維護者**: SynergyMesh Team  
**Last Updated 最後更新**: 2025-11-30
