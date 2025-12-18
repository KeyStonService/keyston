# Root Directory Restructuring and Standardized Subdirectory Framework

# 根層目錄重構與標準化子目錄框架

> **Version:** 1.0.0  
> **Created:** 2025-12-15  
> **Status:** Active  
> **Related Configs:**
>
> - `config/system-module-map.yaml`
> - `config/unified-config-index.yaml`
> - `docs/architecture/naming-conventions.md`

---

## 🔁 Addendum (2025-12-18) — machinenativeops-restructure-spec.json Alignment / 對齊補充

- **Canonical sources / 單一權威來源**
  - `machinenativeops-restructure-spec.json`（包含12個頂層模組定義，其中 microservicesArchitecture.services 定義6個微服務）
  - `machinenativeops.yaml`（單一真實來源，需含 `version`、`vision_version`、`name`、`description`、`entrypoint`、`configs`；現行檔案缺少頂層 `entrypoint`，需於後續補齊）
- **Naming / 命名規範**
  - 目錄與檔名：採 **kebab-case**
  - 顯示品牌：PascalCase（MachineNativeOps）；套件名稱：全小寫（machinenativeops）
  - 同義字合併：
    - `ai/`、`island-ai/` → `src/ai/`
    - `infra/`、`infrastructure/` → `src/autonomous/infrastructure/`
    - `deploy/`、`deployment/` → `src/autonomous/deployment/`
    - `NamespaceTutorial` → `examples/namespace-tutorial`
- **Target root layout / 目標根目錄佈局**
  - `src/{ai,core,governance,autonomous/{infrastructure,deployment,agents}}`
  - `config/{dev,staging,prod}`（合併 `.config/`、`config/`、`.devcontainer/`）
  - `scripts/{dev,ci,ops,governance}`, `docs/`, `examples/namespace-tutorial/`
  - `governance/{policies,strategies,docs,tools,assets}`, `tests/{unit,e2e}`（選配）, `.github/`
- **Versioning / 版本策略**
  - 採 SemVer `X.Y.Z`，Git tag `vX.Y.Z`，目前版本 `4.0.0`
  - 發版流程：更新 `machinenativeops.yaml` → commit → 建立對應 tag
- **Migration phases / 遷移階段**（對應 `migrationProcedure.phases`，保持規格中的 phase-0、phase-2.x 命名）
  1. `phase-0` 備份：建立 `refactor/phase2-directory-restructure` 分支並推送 `pre-restructure-*` tag。
  2. `phase-2.1` 骨架：建立標準目錄（`src/`、`config/`、`scripts/`、`governance/`、`examples/`）。
  3. `phase-2.2` 非相依移動：如 `NamespaceTutorial` → `examples/namespace-tutorial`，治理文檔移至 `governance/docs/`。
  4. `phase-2.3` 合併重複：`ai/`+`island-ai/`、`infra/`+`infrastructure/`、`deploy/`+`deployment/`、`.config/`+`config/`。
  5. `phase-2.4` 路徑修正：更新程式碼匯入與模組路徑。
  6. `phase-2.5` CI 更新：修正工作流程中的腳本路徑。
- **Verification / 驗證命令**
  - `tree -L 2 src config scripts governance examples`
  - `diff -qr <source_dir>/ <target_dir>/`（例如 `diff -qr ai/ src/ai/`、`diff -qr infra/ src/autonomous/infrastructure/`，保持來源與目標皆以尾隨斜線結尾）
  - `npm run build --noEmit`
  - `python -c 'import src.ai.core'`
  - `npm test -- --passWithNoTests`
  - `yamllint .github/workflows/`
- **Execution checklist / 執行檢查**
  - [ ] 不在 `main` 分支，且已建立備份 tag
  - [ ] 覆蓋率基線、依賴基線已保存
  - [ ] 驗證命令全部通過，建置成功、測試可被發現
  - [ ] `CONTRIBUTING.md` 與命名/目錄規範保持一致

---

## 📋 Table of Contents / 目錄

1. [Executive Summary / 執行摘要](#-executive-summary--執行摘要)
2. [Current State Analysis / 現狀分析](#-current-state-analysis--現狀分析)
3. [Restructuring Principles / 重構原則](#-restructuring-principles--重構原則)
4. [Root Directory Restructuring Plan / 根層目錄重構方案](#-root-directory-restructuring-plan--根層目錄重構方案)
5. [Standardized Subdirectory Framework / 標準化子目錄框架](#-standardized-subdirectory-framework--標準化子目錄框架)
6. [Implementation Guide / 實施指南](#-implementation-guide--實施指南)
7. [Migration Checklist / 遷移檢查清單](#-migration-checklist--遷移檢查清單)

---

## 📊 Executive Summary / 執行摘要

This document defines the root-level directory restructuring strategy and standardized subdirectory framework for the Unmanned Island System. It addresses the following key objectives:

本文件定義無人島系統的根層目錄重構策略與標準化子目錄框架，解決以下關鍵目標：

| Objective 目標                          | Description 說明                                          |
| --------------------------------------- | --------------------------------------------------------- |
| **Naming Conflict Resolution 命名衝突解決** | Eliminate ambiguity between `config/` and `.config/`       |
| **Clear Semantic Boundaries 明確語義邊界** | Distinguish technical configs from functional modules      |
| **Consistent Module Structure 一致模組結構** | Standard subdirectory skeleton for all major modules       |
| **Maintainability 可維護性**               | Reduce cognitive load and improve discoverability          |

---

## 🔍 Current State Analysis / 現狀分析

### Root Directory Categories / 根層目錄分類

The current root directory structure consists of multiple entity types:

當前根層目錄結構由多種類型的實體構成：

#### 1. Hidden Configuration Directories / 隱藏配置目錄 (以 `.` 開頭)

| Directory 目錄      | Purpose 用途                          | Status 狀態  |
| ------------------- | ------------------------------------- | ------------ |
| `.config/`          | Configuration test files (conftest)   | **Keep 保留** |
| `.devcontainer/`    | VS Code Dev Container configuration   | **Keep 保留** |
| `.github/`          | GitHub Actions workflows and configs  | **Keep 保留** |
| `.github-private/`  | Private GitHub configurations         | **Keep 保留** |
| `.vscode/`          | VS Code workspace settings            | **Keep 保留** |
| `.refactor-backups/`| Refactoring backup files              | **Keep 保留** |

#### 2. Functional Module Directories / 功能模組目錄

| Directory 目錄   | Purpose 用途                    | Category 類別       |
| ---------------- | ------------------------------- | ------------------- |
| `core/`          | Core platform services          | Platform Core       |
| `automation/`    | Automation capabilities         | AI & Automation     |
| `agent/`         | Long-lifecycle business agents  | AI & Automation     |
| `mcp-servers/`   | MCP tool endpoints              | AI & Automation     |
| `services/`      | Service implementations         | Platform Core       |
| `runtime/`       | Runtime environments            | Platform Core       |
| `frontend/`      | Frontend UI applications        | Experience Layer    |
| `governance/`    | Governance and policies         | Governance & Ops    |
| `apps/`          | Application packages            | Experience Layer    |
| `bridges/`       | Cross-language integrations     | Experience Layer    |

#### 3. Configuration Directories / 配置目錄

| Directory 目錄   | Current State 現狀          | Issue 問題                    |
| ---------------- | --------------------------- | ----------------------------- |
| `config/`        | Application configurations  | Conflicts with `.config/`     |
| `.config/`       | Test configurations         | Naming overlap                |

#### 4. Infrastructure & Support Directories / 基礎設施與支援目錄

| Directory 目錄      | Purpose 用途             |
| ------------------- | ------------------------ |
| `infrastructure/`   | IaC, K8s, monitoring     |
| `infra/`            | Infrastructure configs   |
| `deployment/`       | Deployment scripts       |
| `docker-templates/` | Docker template files    |
| `scripts/`          | Automation scripts       |
| `tools/`            | Development tools        |
| `tests/`            | Test suites              |
| `docs/`             | Documentation            |
| `ops/`              | Operations management    |

### Identified Issues / 已識別問題

1. **Naming Conflict / 命名衝突**: `config/` vs `.config/` causes confusion
2. **Redundant Directories / 冗餘目錄**: `infra/` and `infrastructure/` overlap
3. **Inconsistent Module Structure / 不一致的模組結構**: Modules lack standard subdirectories
4. **Missing Standard Skeletons / 缺少標準骨架**: No unified `src/`, `tests/`, `docs/`, `config/` pattern

---

## 🎯 Restructuring Principles / 重構原則

### Principle 1: Clear Hierarchy Distinction / 清晰的層次區分

Separate **system-level/tool-level configurations** from **application-level/domain-logic configurations**:

區分**系統級/工具級配置**與**應用級/領域邏輯配置**：

```
Hidden Directories (.)     →  System/Tool configurations
│                              (開發環境、CI/CD、IDE)
├── .config/
├── .devcontainer/
├── .github/
├── .vscode/
└── .refactor-backups/

Visible Directories        →  Application/Domain configurations
│                              (應用配置、業務邏輯)
├── app-configs/           →  NEW: Renamed from config/
├── core/
├── automation/
└── services/
```

### Principle 2: Name Clarity and Consistency / 名稱的明確性與一致性

All root-level directory names should:

所有根層目錄名稱應：

- **Be Self-Descriptive / 自我描述性**: Clearly reflect content
- **Follow Consistent Plurality / 統一複數規則**: Use plural form (`configs`, `tests`, `docs`)
- **Avoid Abbreviation Ambiguity / 避免縮寫歧義**: `infrastructure` over `infra`

### Principle 3: Standard Industry Names / 標準化行業名稱

Adopt industry-standard naming conventions:

採納業界標準名稱：

| Standard Name | Purpose                    |
| ------------- | -------------------------- |
| `src/`        | Source code                |
| `tests/`      | Test suites                |
| `docs/`       | Documentation              |
| `config/`     | Module-specific configs    |

---

## 📁 Root Directory Restructuring Plan / 根層目錄重構方案

### Recommended Directory Renaming / 推薦目錄重命名

| Current 現有             | Recommended 推薦           | Rationale 理由                                              |
| ------------------------ | -------------------------- | ----------------------------------------------------------- |
| `config/`                | `app-configs/`             | Distinguish from `.config/`; clarify application scope      |
| `infra/`                 | Keep or merge              | Merge with `infrastructure/` if overlapping                 |
| `infrastructure/`        | Keep                       | Clear name for IaC                                          |
| `frontend/ui/`           | `frontend/`                | Flatten structure; `ui/` as subdirectory                    |

### Hidden Directory Policy / 隱藏目錄策略

Hidden directories (`.` prefix) represent **technical/tool configurations**:

隱藏目錄（`.` 前綴）代表**技術/工具配置**：

| Directory            | Category               | Content                              |
| -------------------- | ---------------------- | ------------------------------------ |
| `.config/`           | Test Configuration     | `conftest/` for pytest configs       |
| `.devcontainer/`     | Development Container  | VS Code remote container setup       |
| `.github/`           | CI/CD Workflows        | GitHub Actions, templates            |
| `.github-private/`   | Private CI Configs     | Sensitive workflow configurations    |
| `.vscode/`           | IDE Settings           | VS Code workspace settings           |
| `.refactor-backups/` | Backup Storage         | Refactoring safety backups           |

### Final Recommended Root Structure / 最終推薦根層結構

```
unmanned-island/
│
├── 📁 Hidden Configurations (隱藏配置)
│   ├── .config/              # Configuration tests (conftest)
│   ├── .devcontainer/        # Dev Container setup
│   ├── .github/              # GitHub workflows
│   ├── .github-private/      # Private CI configs
│   ├── .vscode/              # VS Code settings
│   └── .refactor-backups/    # Refactoring backups
│
├── 📁 Core Functional Modules (核心功能模組)
│   ├── core/                 # 🏛️ Platform core services
│   ├── automation/           # 🤖 Automation capabilities
│   ├── agent/                # 🤖 Business agents
│   ├── services/             # 🔧 Service implementations
│   ├── runtime/              # ⚡ Runtime environments
│   └── mcp-servers/          # 🖥️ MCP tool endpoints
│
├── 📁 Experience Layer (體驗層)
│   ├── frontend/             # 🎨 Frontend UI applications
│   ├── apps/                 # 📱 Application packages
│   ├── bridges/              # 🌉 Cross-language bridges
│   └── contracts/            # 📝 External API contracts
│
├── 📁 Configuration (配置)
│   └── app-configs/          # ⚙️ Application configurations (renamed)
│
├── 📁 Infrastructure (基礎設施)
│   ├── infrastructure/       # 🏗️ IaC, K8s, monitoring
│   ├── deployment/           # 🚀 Deployment scripts
│   └── docker-templates/     # 🐳 Docker templates
│
├── 📁 Governance & Operations (治理與運維)
│   ├── governance/           # ⚖️ Governance policies
│   ├── ops/                  # 📋 Operations
│   └── docs/                 # 📚 Documentation
│
├── 📁 Development Support (開發支援)
│   ├── tests/                # 🧪 Test suites
│   ├── scripts/              # 📜 Automation scripts
│   ├── tools/                # 🔧 Development tools
│   └── shared/               # 📦 Shared resources
│
└── 📁 Legacy & Experiments (遺留與實驗)
    ├── legacy/               # 📦 Legacy code
    └── experiments/          # 🔬 Experimental features
```

---

## 🏗️ Standardized Subdirectory Framework / 標準化子目錄框架

### Consistency Principle / 一致性原則

For large projects containing multiple functional modules, establishing a **standard, fixed, mandatory** subdirectory structure for each module is key to achieving high consistency and predictability.

對於包含多個功能模組的大型項目，為每個模組建立一套**標準、固定、必有**的子目錄結構，是實現高度一致性和可預測性的關鍵。

### Standard Module Skeleton / 標準模組骨架

The following subdirectories are **highly recommended** for every major root-level functional module:

以下子目錄**高度推薦**存在於每個主要的根層功能模組中：

```
module_name/
├── src/                    # 📝 Source Code (Required)
│   ├── index.ts            # Entry point
│   └── components/         # Module components
├── tests/                  # 🧪 Test Suite (Required)
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── docs/                   # 📚 Documentation (Required)
│   ├── README.md           # Module overview
│   ├── API.md              # API documentation
│   └── DESIGN.md           # Design decisions
├── config/                 # ⚙️ Configuration (Recommended)
│   ├── defaults.yaml       # Default settings
│   └── schemas/            # Config schemas
└── README.md               # Module entry documentation
```

### Subdirectory Specifications / 子目錄規格

#### 1. `src/` - Source Code (High Priority) / 源代碼（高優先級）

| Attribute 屬性       | Specification 規格                                     |
| -------------------- | ------------------------------------------------------ |
| **Purpose 目的**     | Store core application source code                     |
| **Mandatory Level**  | **HIGH** (Required for all functional modules)         |
| **Contents 內容**    | Core logic, business components, entry points          |
| **Rule 規則**        | No source code should reside directly in module root   |

```
src/
├── index.ts              # Module entry point
├── types.ts              # Type definitions
├── utils/                # Utility functions
├── services/             # Service classes
└── components/           # UI components (if applicable)
```

#### 2. `tests/` - Test Suite (High Priority) / 測試套件（高優先級）

| Attribute 屬性       | Specification 規格                                     |
| -------------------- | ------------------------------------------------------ |
| **Purpose 目的**     | Store all module-related tests                         |
| **Mandatory Level**  | **HIGH** (Required for all functional modules)         |
| **Contents 內容**    | Unit tests, integration tests, E2E tests               |
| **Alignment**        | Mirrors `src/` structure                               |

```
tests/
├── unit/                 # Unit tests
│   ├── services/         # Service unit tests
│   └── utils/            # Utility unit tests
├── integration/          # Integration tests
│   └── api/              # API integration tests
└── e2e/                  # End-to-end tests
    └── scenarios/        # E2E test scenarios
```

#### 3. `docs/` - Documentation (High Priority) / 文檔（高優先級）

| Attribute 屬性       | Specification 規格                                     |
| -------------------- | ------------------------------------------------------ |
| **Purpose 目的**     | Store module-specific documentation                    |
| **Mandatory Level**  | **HIGH** (Required for all major modules)              |
| **Contents 內容**    | API docs, architecture diagrams, design decisions      |
| **Note 備註**        | Root `docs/` stores global cross-module documentation  |

```
docs/
├── README.md             # Module overview
├── API.md                # API reference
├── DESIGN.md             # Design decisions (ADR)
├── CHANGELOG.md          # Module changelog
└── diagrams/             # Architecture diagrams
    └── architecture.png
```

#### 4. `config/` - Module Configuration (Medium-High Priority) / 模組配置（中高優先級）

| Attribute 屬性       | Specification 規格                                     |
| -------------------- | ------------------------------------------------------ |
| **Purpose 目的**     | Store module-specific configurations                   |
| **Mandatory Level**  | **MEDIUM-HIGH** (Recommended for most modules)         |
| **Contents 內容**    | Default configs, environment templates, schemas        |
| **Distinction**      | Different from root `app-configs/` (global configs)    |

```
config/
├── defaults.yaml         # Default configuration
├── development.yaml      # Development settings
├── production.yaml       # Production settings
└── schemas/              # Config validation schemas
    └── config.schema.json
```

### Module Skeleton Template / 模組骨架模板

#### Full Module Structure / 完整模組結構

```
{module_name}/
├── README.md                 # Module entry documentation
├── package.json              # Node.js (if applicable)
├── pyproject.toml            # Python (if applicable)
├── tsconfig.json             # TypeScript config (if applicable)
│
├── src/                      # 📝 Source Code [HIGH]
│   ├── index.ts              # Entry point
│   ├── types.ts              # Type definitions
│   ├── constants.ts          # Constants
│   ├── services/             # Service layer
│   │   └── core-service.ts
│   ├── utils/                # Utility functions
│   │   └── helpers.ts
│   └── components/           # Components (if UI module)
│       └── main-component.tsx
│
├── tests/                    # 🧪 Tests [HIGH]
│   ├── unit/                 # Unit tests
│   │   └── core-service.test.ts
│   ├── integration/          # Integration tests
│   │   └── api.test.ts
│   ├── e2e/                  # End-to-end tests
│   │   └── scenarios.test.ts
│   ├── fixtures/             # Test fixtures
│   │   └── sample-data.json
│   └── mocks/                # Mock implementations
│       └── mock-service.ts
│
├── docs/                     # 📚 Documentation [HIGH]
│   ├── README.md             # Module overview
│   ├── API.md                # API reference
│   ├── DESIGN.md             # Design decisions
│   ├── CONTRIBUTING.md       # Contribution guide
│   └── diagrams/
│       └── architecture.png
│
└── config/                   # ⚙️ Configuration [MEDIUM-HIGH]
    ├── defaults.yaml         # Default settings
    ├── development.yaml      # Dev environment
    ├── production.yaml       # Prod environment
    └── schemas/
        └── config.schema.json
```

### Application Examples / 應用示例

#### Example 1: `agent/` Module Restructure / `agent/` 模組重構示例

**Before (Current) / 之前（現狀）:**

```
agent/
├── README.md
├── auto-repair/
├── code-analyzer/
├── dependency-manager/
├── orchestrator/
├── runbook-executor.sh
└── vulnerability-detector/
```

**After (Recommended) / 之後（推薦）:**

```
agent/
├── README.md                 # Module entry documentation
│
├── src/                      # Core agent logic
│   ├── index.ts              # Agent system entry point
│   ├── auto-repair/          # Auto repair agent
│   │   ├── index.ts
│   │   └── strategies/
│   ├── code-analyzer/        # Code analyzer agent
│   │   ├── index.ts
│   │   └── analyzers/
│   ├── dependency-manager/   # Dependency manager agent
│   │   ├── index.ts
│   │   └── scanners/
│   ├── orchestrator/         # Agent orchestrator
│   │   ├── index.ts
│   │   └── scheduler.ts
│   └── vulnerability-detector/
│       ├── index.ts
│       └── detectors/
│
├── tests/                    # Agent test suite
│   ├── unit/
│   │   ├── auto-repair.test.ts
│   │   ├── code-analyzer.test.ts
│   │   └── orchestrator.test.ts
│   ├── integration/
│   │   └── agent-system.test.ts
│   └── fixtures/
│       └── sample-code-snippets.json
│
├── docs/                     # Agent documentation
│   ├── README.md             # Agent system overview
│   ├── API.md                # Agent API reference
│   ├── DESIGN.md             # Agent architecture decisions
│   └── diagrams/
│       └── agent-flow.png
│
├── config/                   # Agent-specific configurations
│   ├── defaults.yaml         # Default agent settings
│   └── schemas/
│       └── agent-config.schema.json
│
└── scripts/                  # Agent scripts
    └── runbook-executor.sh   # Runbook execution script
```

#### Example 2: `core/` Module Enhancement / `core/` 模組增強示例

**After (Recommended) / 之後（推薦）:**

```
core/
├── README.md                 # Core module documentation
│
├── src/                      # Core source code
│   ├── __init__.py           # Python module init
│   ├── ai_decision_engine.py
│   ├── auto_bug_detector.py
│   ├── auto_governance_hub.py
│   ├── autonomous_trust_engine.py
│   ├── context_understanding_engine.py
│   ├── contract_engine.py
│   ├── hallucination_detector.py
│   └── plugin_system.py
│
├── unified_integration/      # Integration subsystem
│   ├── src/                  # Nested src for subsystem
│   │   ├── __init__.py
│   │   ├── cognitive_processor.py
│   │   └── service_registry.py
│   ├── tests/
│   └── docs/
│
├── safety_mechanisms/        # Safety subsystem
│   ├── src/
│   ├── tests/
│   └── docs/
│
├── tests/                    # Core test suite
│   ├── unit/
│   │   ├── test_ai_decision_engine.py
│   │   └── test_context_understanding.py
│   ├── integration/
│   │   └── test_unified_integration.py
│   └── fixtures/
│
├── docs/                     # Core documentation
│   ├── README.md             # Core module overview
│   ├── API.md                # Core API reference
│   ├── DESIGN.md             # Core architecture decisions
│   └── diagrams/
│       └── core-architecture.png
│
└── config/                   # Core-specific configurations
    ├── defaults.yaml
    └── schemas/
```

---

## 📋 Implementation Guide / 實施指南

### Phase 1: Documentation and Planning / 第一階段：文檔與規劃

1. **Update `config/system-module-map.yaml`** to reflect new structure
2. **Update `config/unified-config-index.yaml`** with restructuring plan
3. **Create module skeleton templates** for new modules
4. **Update `docs/architecture/naming-conventions.md`** with directory conventions

### Phase 2: Root Directory Restructure / 第二階段：根層目錄重構

1. **Rename `config/` to `app-configs/`** (if proceeding with rename)
2. **Review and consolidate `infra/` and `infrastructure/`**
3. **Flatten `frontend/ui/` structure** if needed
4. **Update all import paths and references**

### Phase 3: Module Skeleton Implementation / 第三階段：模組骨架實施

Apply standard skeleton to major modules in order of priority:

依優先級順序將標準骨架應用於主要模組：

| Priority | Module            | Reason                                |
| -------- | ----------------- | ------------------------------------- |
| 1        | `core/`           | Central platform, highest impact      |
| 2        | `agent/`          | Active development, clear boundaries  |
| 3        | `automation/`     | Multiple submodules need structure    |
| 4        | `services/`       | Service implementations need standard |
| 5        | `mcp-servers/`    | Tool endpoints need consistency       |
| 6        | `frontend/`       | UI components need structure          |

### Phase 4: Validation and Migration / 第四階段：驗證與遷移

1. **Run linting and build verification**
2. **Update CI/CD workflows** for new paths
3. **Update documentation references**
4. **Verify all tests pass**

---

## ✅ Migration Checklist / 遷移檢查清單

### Pre-Migration / 遷移前

- [ ] Review and approve restructuring plan
- [ ] Backup current directory structure
- [ ] Identify all path references (imports, configs, CI)
- [ ] Plan incremental migration approach

### Root Directory Changes / 根層目錄變更

- [ ] Rename `config/` to `app-configs/` (if applicable)
- [ ] Update all references to `config/` in code
- [ ] Update all references in CI workflows
- [ ] Verify `.config/` remains for test configurations

### Module Skeleton Implementation / 模組骨架實施

For each module (`agent/`, `core/`, `automation/`, `services/`, `mcp-servers/`, `frontend/`):

- [ ] Create `src/` directory and move source files
- [ ] Create `tests/` directory with unit/integration/e2e structure
- [ ] Create `docs/` directory with README.md, API.md, DESIGN.md
- [ ] Create `config/` directory for module-specific configs
- [ ] Update module README.md with new structure

### Post-Migration / 遷移後

- [ ] Run full test suite
- [ ] Run linting and build
- [ ] Update `DOCUMENTATION_INDEX.md`
- [ ] Update `docs/architecture/DIRECTORY_STRUCTURE.md`
- [ ] Update `config/system-module-map.yaml`
- [ ] Verify CI/CD pipelines work correctly
- [ ] Archive old structure documentation

---

## 🔗 Related Documentation / 相關文檔

- [Naming Conventions](./naming-conventions.md) - 命名規範
- [Language Stack](./language-stack.md) - 語言堆疊決策
- [Directory Structure](./DIRECTORY_STRUCTURE.md) - 目錄結構說明
- [System Module Map](../../config/system-module-map.yaml) - 系統模組映射
- [Unified Config Index](../../config/unified-config-index.yaml) - 統一配置索引

---

**Document Owner:** Unmanned Island System Team  
**Review Cycle:** Quarterly  
**Next Review:** 2026-03-15
