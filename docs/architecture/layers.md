# SynergyMesh Architecture Layers

# 架構分層視圖

> 本文件定義了 SynergyMesh 平台的分層架構視圖，作為目錄結構與系統邊界的唯一參考來源。This
> document defines the layered architecture view for the SynergyMesh platform,
> serving as the single source of truth for directory structure and system
> boundaries.

## 📊 Architecture Layers Table 分層架構表

| 層級 Layer                  | 目錄 Directory                                               | 說明 Description                                                                       |
| --------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| **Experience / Interfaces** | `frontend/`, `bridges/`, `contracts/`                        | 人機介面與外部 API/語言接口。User interfaces and external API/language bindings.       |
| **Platform Core**           | `core/`, `runtime/`, `shared/`                               | 平台核心服務與共用能力。Core platform services and shared capabilities.                |
| **AI & Automation**         | `automation/`, `agent/`, `mcp-servers/`                      | AI workflow、智能代理、工具端點。AI workflows, intelligent agents, and tool endpoints. |
| **Enablement**              | `infrastructure/`, `.github/`, `tools/`, `tests/`, `config/` | 基礎設施 / CI / 測試 / 配置。Infrastructure, CI/CD, testing, and configuration.        |
| **Governance & Ops**        | `governance/`, `ops/`, `docs/`                               | 政策、運維、文件。Policies, operations, and documentation.                             |

## 🔷 Layer Descriptions 層級說明

### 1. Experience / Interfaces Layer 體驗/介面層

負責與外部世界的互動，包括用戶介面和外部系統整合。

**Directories 目錄:**

- `frontend/` - 前端 UI 應用程式
- `bridges/` - 跨語言整合橋接（Python、Go 等）
- `contracts/` - 外部 API 合約定義（schemas / OpenAPI specs）

**Responsibilities 職責:**

- 提供使用者互動介面
- 定義外部 API 規格
- 處理跨語言呼叫

**Does NOT include 不包含:**

- 業務邏輯實作
- 內部服務通訊協議

---

### 2. Platform Core Layer 平台核心層

平台的核心能力，提供決策引擎、執行環境和共用資源。

**Directories 目錄:**

- `core/` - 核心平台服務（AI 引擎、治理、安全機制、整合服務）
- `runtime/` - 實際運行時環境（Mind Matrix runtime）
- `shared/` - 共用工具、配置和常量

**Responsibilities 職責:**

- AI 決策引擎與上下文理解
- 執行架構與引擎
- 安全機制與信任管理
- 虛擬專家系統
- 訓練系統

**Does NOT include 不包含:**

- CI/CD 工作流程
- 監控基礎設施
- 產品級 pipeline 組合

---

### 3. AI & Automation Layer AI 與自動化層

AI 能力實作、智能代理和自動化流程。

**Directories 目錄:**

- `automation/` - 自動化能力（architect、autonomous、hyperautomation、intelligent）
- `agent/` - 長生命週期業務代理（auto-repair、code-analyzer、orchestrator）
- `mcp-servers/` - MCP（Model Context Protocol）工具端點，供 LLM 調用

**Responsibilities 職責:**

- 多代理 AI 代碼分析系統
- 自主系統框架（無人機、自動駕駛）
- 智能自動化 pipeline
- LLM 可調用的工具端點

**Does NOT include 不包含:**

- 平台級共用 AI 能力（這些在 `core/`）
- 前端 UI
- 基礎設施配置

---

### 4. Enablement Layer 賦能層

支援開發、測試和部署的基礎設施。

**Directories 目錄:**

- `infrastructure/` - IaC、Kubernetes、監控配置
- `.github/` - GitHub Actions 工作流程
- `tools/` - 開發工具和腳本
- `tests/` - 集中式測試套件
- `config/` - 集中式配置文件

**Responsibilities 職責:**

- 容器化和編排
- CI/CD 自動化
- 測試執行和品質保證
- 環境配置管理

**Does NOT include 不包含:**

- 業務邏輯
- AI 模型或代理實作

---

### 5. Governance & Ops Layer 治理與運維層

政策、文檔和運維資源。

**Directories 目錄:**

- `governance/` - 治理政策、規則、SBOM、schemas
- `ops/` - 運維手冊、報告、遷移腳本
- `docs/` - 完整文檔集合

**Responsibilities 職責:**

- 合規與審計
- 運維程序
- 知識文檔
- SLSA / supply chain security

**Does NOT include 不包含:**

- 可執行代碼（除腳本外）
- 配置文件（這些在 `config/`）

---

## 🔗 Dependency Rules 依賴規則

```
Experience/Interfaces → Platform Core → AI & Automation
                     ↘                ↙
                      ← Enablement ←
                      ← Governance ←
```

### Allowed Dependencies 允許的依賴

| From 來源             | Can depend on 可依賴                            |
| --------------------- | ----------------------------------------------- |
| Experience/Interfaces | Platform Core, Shared                           |
| Platform Core         | Shared, Runtime                                 |
| AI & Automation       | Platform Core, Shared                           |
| Enablement            | 無業務邏輯依賴 (No business logic dependencies) |
| Governance & Ops      | 僅文檔參考 (Documentation references only)      |

### Prohibited Dependencies 禁止的依賴

| From 來源     | Should NOT depend on 不應依賴 |
| ------------- | ----------------------------- |
| Platform Core | AI & Automation (避免循環)    |
| Enablement    | 直接依賴業務代碼              |
| contracts/    | 任何實作代碼                  |

---

## 📁 Directory Quick Reference 目錄快速參考

### By Programming Language 按語言分類

| Language 語言       | Directories 目錄                                                                |
| ------------------- | ------------------------------------------------------------------------------- |
| **TypeScript/Node** | 根目錄, `mcp-servers/`, `frontend/`, `core/contract_service/contract_service/`  |
| **Python**          | `automation/intelligent/`, `automation/autonomous/api-governance/`, `core/*.py` |
| **Go**              | `automation/autonomous/security-observability/`, `core/monitoring_system/`      |
| **C++**             | `automation/autonomous/architecture-stability/` (ROS 2)                         |
| **YAML/Config**     | `config/`, `infrastructure/`, `governance/`                                     |

### By Domain 按領域分類

| Domain 領域            | Primary Directories 主要目錄                                      |
| ---------------------- | ----------------------------------------------------------------- |
| **Autonomous Systems** | `automation/autonomous/`, `automation/hyperautomation/`           |
| **AI/ML**              | `core/ai_*`, `core/virtual_experts/`, `core/training_system/`     |
| **Security**           | `core/safety_mechanisms/`, `core/slsa_provenance/`, `governance/` |
| **Integration**        | `core/unified_integration/`, `bridges/`, `contracts/`             |
| **Monitoring**         | `infrastructure/monitoring/`, `core/monitoring_system/`           |

---

## 🔄 Change Guidelines 變更指南

當需要調整架構時：

1. **新增模組**：根據職責歸類到對應層級
2. **重構**：確保不違反依賴規則
3. **跨層調用**：透過明確定義的介面進行

### Before Adding New Code 新增代碼前

問自己：

- 這段代碼的主要職責是什麼？
- 它應該屬於哪一層？
- 它需要依賴哪些其他模組？
- 有沒有違反依賴規則？

---

## 📝 Document History 文檔歷史

| Date 日期  | Version 版本 | Changes 變更                          |
| ---------- | ------------ | ------------------------------------- |
| 2025-11-30 | 1.0.0        | Initial layered architecture document |

---

**Maintainer 維護者**: SynergyMesh Team  
**Last Updated 最後更新**: 2025-11-30
