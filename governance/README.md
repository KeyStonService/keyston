# Governance

# 治理

> 治理政策、規則、安全配置和合規資源。Governance policies, rules, security
> configurations, and compliance resources.

## 📋 Overview 概述

本目錄包含 SynergyMesh 項目的治理配置和文檔，確保模組間的責任清晰、依賴管理合理、語言邊界明確。

This directory contains governance configurations and documentation for the
SynergyMesh project, ensuring clear module responsibilities, reasonable
dependency management, and explicit language boundaries.

## 🎯 Governance Architecture | 治理架構 ⭐

### 核心文檔 (Core Documentation)

- **[📖 Architecture Governance Matrix](./ARCHITECTURE_GOVERNANCE_MATRIX.md)** - 九維度治理矩陣
- **[🏗️ Governance Integration Architecture](./GOVERNANCE_INTEGRATION_ARCHITECTURE.md)** - 完整整合架構
- **[📂 Deep Analysis: Governance Structure](./DEEP_ANALYSIS_GOVERNANCE_STRUCTURE.md)** - 目錄結構深度分析
- **[📄 File Content Structure Analysis](./FILE_CONTENT_STRUCTURE_ANALYSIS.md)** - 檔案內容結構分析
- **[🆕 Missing Dimensions Analysis](./MISSING_DIMENSIONS_ANALYSIS.md)** - 缺失維度分析與擴展建議
- **[🔄 CI Refactoring Guide](./CI_REFACTORING_GUIDE.md)** - CI 管線重構指南 (NEW!)

> **⚡ 更新 (2025-12-12)**: 已實施完整 81 個治理維度 (00-80)，達成 100% 完整覆蓋率！

### 分層閉環治理架構 (Layered Closed-Loop Governance)

SynergyMesh 採用分層閉環治理架構，整合 GitOps、Policy as Code、Intent-based
Orchestration、AI Agent Governance 與 Feedback Loop：

```
策略層 (Strategy)     → 10-policy: Policy as Code Framework
協調層 (Orchestration) → 20-intent: Intent-based Orchestration
執行層 (Execution)    → 30-agents, 39-automation, 40-self-healing
觀測層 (Observability) → 60-contracts, 70-audit
回饋層 (Feedback)     → 80-feedback: Closed-Loop Optimization
```

詳見
[Governance Integration Architecture](./GOVERNANCE_INTEGRATION_ARCHITECTURE.md)

### Core Structural Contracts | 核心結構契約

1. **Namespace** - Logical naming and boundaries
2. **Module Mapping** - Logical ID to physical path mapping
3. **Dependency Rules** - Who can call whom

### Extended Governance Dimensions | 延伸治理維度

1. **Layers & Domains** - Semantic definitions and responsibilities
2. **Roles & Capabilities** - Module behavioral intent
3. **Behavior Contracts** - API, events, invariants, failure modes
4. **Lifecycle & Ownership** - Team ownership and module state
5. **Policies & Constraints** - Executable architectural policies
6. **Quality & Metrics** - Measurable architecture health

This framework makes architecture governance **explicit, measurable, and
automatable**.

## 📁 Directory Structure 目錄結構

> **⚠️ RESTRUCTURING NOTICE** (2025-12-12): Directory structure has been cleaned
> up to resolve duplicates and conflicts. See
> [RESTRUCTURING_GUIDE.md](./RESTRUCTURING_GUIDE.md) for migration details.

```
governance/
├── ARCHITECTURE_GOVERNANCE_MATRIX.md     # 🎯 架構治理矩陣（核心文檔）
├── GOVERNANCE_INTEGRATION_ARCHITECTURE.md # 🏗️ 完整整合架構
├── RESTRUCTURING_GUIDE.md                # 📋 重組指南 (NEW!)
│
├── 分層治理框架 (Layered Governance Framework) ⭐ PRIMARY ARCHITECTURE
│   ├── 10-policy/                        # Policy as Code Framework
│   │   ├── README.md
│   │   ├── framework.yaml
│   │   ├── base-policies/
│   │   ├── domain-policies/
│   │   ├── policy-gates/
│   │   └── opa-policies/
│   │
│   ├── 20-intent/                        # Intent-based Orchestration
│   │   ├── README.md
│   │   ├── framework.yaml
│   │   ├── intent-dsl/
│   │   ├── semantic-mapping/
│   │   ├── lifecycle/
│   │   └── closed-loop/
│   │
│   ├── 30-agents/                        # AI Agent Governance
│   │   ├── README.md
│   │   ├── framework.yaml
│   │   ├── lifecycle/
│   │   ├── permissions/
│   │   ├── monitoring/
│   │   └── compliance/
│   │
│   ├── 60-contracts/                     # Contract Registry
│   │   ├── README.md
│   │   ├── framework.yaml
│   │   ├── registry/
│   │   ├── versioning/
│   │   └── validation/
│   │
│   ├── 70-audit/                         # Audit & Traceability (Observability Layer)
│   │   ├── README.md
│   │   ├── framework.yaml
│   │   ├── audit-logs/
│   │   ├── traceability/
│   │   └── compliance/
│   │
│   └── 80-feedback/                      # Closed-Loop Feedback
│       ├── README.md
│       ├── framework.yaml
│       ├── collection/
│       ├── analysis/
│       └── optimization/
│
├── 原有治理維度 (Original Governance Dimensions) 00-09
│   ├── 00-vision-strategy/               # 願景與策略
│   ├── 01-architecture/                  # 架構治理
│   ├── 02-decision/                      # 決策管理
│   ├── 03-change/                        # 變更管理
│   ├── 04-risk/                          # 風險管理
│   ├── 05-compliance/                    # 合規管理
│   ├── 06-security/                      # 安全管理
│   ├── 07-audit/                         # 審計 (Strategy Layer - Policy Definition)
│   ├── 08-process/                       # 流程管理
│   └── 09-performance/                   # 性能管理
│
├── 支援與工具維度 (Support & Tool Dimensions) 11-40
│   ├── 11-tools-systems/                 # 工具系統
│   ├── 12-culture-capability/            # 文化能力
│   ├── 13-metrics-reporting/             # 指標報告
│   ├── 14-improvement/                   # 持續改進
│   ├── ...
│   ├── 23-policies/                      # 策略定義 (Consolidated from root policies/)
│   ├── 24-registry/                      # 模組註冊表
│   ├── 31-schemas/                       # Schema 定義 (Consolidated from root schemas/)
│   ├── 35-scripts/                       # 腳本工具 (Consolidated from root scripts/)
│   ├── 39-automation/                    # 自動化引擎
│   └── 40-self-healing/                  # 自我修復框架
│
├── 已棄用目錄 (Deprecated Directories) ⚠️
│   ├── _legacy/                          # 已遷移的舊維度
│   │   ├── 10-stakeholder/               # → 功能已整合到其他維度
│   │   ├── 20-information/               # → 內容已整合
│   │   └── 30-integration/               # → 已整合到 30-agents
│   ├── policies/ → 23-policies/          # 已整合 (See README_DEPRECATED.md)
│   ├── schemas/ → 31-schemas/            # 已整合 (See README_DEPRECATED.md)
│   └── scripts/ → 35-scripts/            # 已整合 (See README_DEPRECATED.md)
│
└── 跨維度共享資源 (Cross-Dimensional Shared Resources)
    ├── dimensions/                       # 完整維度索引 (80+ dimensions)
    ├── index/                            # 索引與事件
    ├── packages/                         # 共享套件
    └── ci/                               # CI/CD 整合
```

### 🔄 Recent Changes (2025-12-12)

**問題解決 (Problems Resolved)**:

1. ✅ 移除目錄編號衝突 (10, 20, 30)
2. ✅ 統一共享資源位置 (policies, schemas, scripts)
3. ✅ 釐清審計職責 (07-audit vs 70-audit)
4. ✅ 建立單一真相來源

**遷移影響 (Migration Impact)**:

- Legacy dimensions moved to `_legacy/`
- Shared resources consolidated into numbered dimensions
- All changes tracked in `governance-map.yaml`
- Migration deadline: 2026-03-31

## 🎯 What This Directory Does 本目錄負責什麼

### ✅ Responsibilities 職責

#### 1. **分層治理框架 (Layered Governance Framework)** ⭐ NEW

**10-policy: Policy as Code**

- 治理規則、合規政策以程式碼形式定義
- 自動化策略閘 (CI/CD/Runtime)
- Suppress 機制與審計追蹤

**20-intent: Intent-based Orchestration**

- 意圖驅動編排，語意一致性保障
- 高階意圖轉譯為具體操作
- 閉環保障與數位分身模擬

**30-agents: AI Agent Governance**

- AI Agent 全生命週期管理
- 權限與安全控管
- 合規 (ISO/IEC 42001, NIST AI RMF, EU AI Act)

**60-contracts: Contract Registry**

- 契約驅動模組化設計
- 接口標準化與版本控管
- 契約測試與向後兼容

**70-audit: Audit & Traceability**

- 全鏈路審計日誌與追蹤
- 資料血緣與模型溯源
- 合規報告自動化

**80-feedback: Closed-Loop Feedback**

- 策略—執行—監控—回饋閉環
- AI/ML 驅動異常預測與優化
- A/B 測試與持續改進

#### 2. **原有治理職責 (Existing Governance)**

**Policy Definitions 策略定義** (`23-policies/`)

- 安全策略
- 存取控制策略
- 代碼品質策略
- Conftest/OPA 策略

**Audit Configurations 審計配置** (`07-audit/`)

- 審計日誌配置
- 合規檢查規則
- 審計報告模板

**Governance Rules 治理規則** (`32-rules/`)

- 依賴管理規則
- 版本控制規則
- 發布流程規則

**Software Bill of Materials 軟體物料清單** (`38-sbom/`)

- 依賴清單
- 授權資訊
- 簽章策略

**Schema Definitions Schema 定義** (`31-schemas/`)

- 配置文件 schema
- API schema
- Data model definitions / 資料模型定義

**Environment Matrix 環境映射** (`environment-matrix/`)

- 模組環境需求映射
- 語言維度映射
- 條件式部署配置

**Deployment Configuration 部署配置** (`deployment/`)

- 服務部署配置
- Kubernetes 清單

**Module Registry 模組註冊表** (`24-registry/`)

- 服務治理元數據
- 模組依賴關係

### ❌ What This Directory Does NOT Do 本目錄不負責什麼

- **No executable code** - Except validation scripts / 除驗證腳本外
- **No business logic** - Only policy and rule definitions / 僅政策和規則定義
- **No runtime configuration** - Use `config/` instead / 使用 `config/`

## 🔗 Dependencies 依賴關係

### ✅ Who Should Depend on This 誰應該依賴本目錄

| Consumer 使用者 | Purpose 用途                                                 |
| --------------- | ------------------------------------------------------------ |
| CI/CD workflows | Policy validation and compliance checks / 策略驗證和合規檢查 |
| `core/`         | 讀取 AI 憲法和倫理規則                                       |
| Security tools  | SBOM 和安全策略                                              |

### ❌ This Directory Should NOT Depend on 本目錄不應依賴

| 不應依賴     | Reason 原因            |
| ------------ | ---------------------- |
| 任何實作代碼 | 治理應獨立於實作       |
| `runtime/`   | 治理定義不應依賴運行時 |

## 🔧 Governance Tools & Validation 治理工具與驗證

### Scanner & Validation Tools 掃描器與驗證工具

SynergyMesh provides comprehensive governance tooling for structure validation, scanning, and maintenance:

#### **Governance Directory Scanner** ⭐ NEW

Comprehensive scanner for governance directory structure analysis:

```bash
# Interactive scan with summary
make scan-governance

# Generate detailed YAML report
make scan-governance-report

# Generate JSON report
make scan-governance-json

# Full governance validation + scan
make governance-full-check
```

**Features**:
- ✅ Full 00-80 dimension scan
- ✅ File completeness verification (dimension.yaml, README.md, framework.yaml)
- ✅ Naming convention validation
- ✅ Orphaned directory detection
- ✅ Dependency graph analysis
- ✅ Coverage reporting (100% dimension coverage)
- ✅ Detailed statistics and recommendations

**Documentation**: See [35-scripts/README-SCANNER.md](./35-scripts/README-SCANNER.md)

#### **Structure Validator**

Validates governance structure against `governance-map.yaml`:

```bash
make validate-governance-structure
```

#### **Governance Matrix Validator**

Validates architecture governance matrix completeness:

```bash
make validate-governance
```

### Available Make Targets 可用的 Make 目標

| Target                           | Purpose 目的                |
| -------------------------------- | -------------------------- |
| `make scan-governance`           | 治理目錄掃描                |
| `make scan-governance-report`    | 生成 YAML 掃描報告          |
| `make scan-governance-json`      | 生成 JSON 掃描報告          |
| `make validate-governance-structure` | 結構驗證                |
| `make validate-governance`       | 矩陣驗證                   |
| `make governance-full-check`     | 完整治理驗證與掃描          |

### Script Documentation 腳本文檔

All governance scripts are documented in [35-scripts/README.md](./35-scripts/README.md):

- **scan-governance-directory.py** - Comprehensive governance scanner
- **validate-governance-structure.py** - Structure validation
- **intelligent-file-router.py** - Content-based file routing
- **logical-consistency-engine.py** - Logical consistency analysis
- **extreme-problem-identifier.py** - Multi-dimensional problem detection

## 📖 Related Documentation 相關文檔

- [Architecture Layers](../docs/architecture/layers.md) - 架構分層視圖
- [Repository Map](../docs/architecture/repo-map.md) - 倉庫語義邊界
- [Security Training](../docs/SECURITY_TRAINING.md) - 安全培訓
- [Vulnerability Management](../docs/VULNERABILITY_MANAGEMENT.md) - 漏洞管理

## 📝 Document History 文檔歷史

| Date 日期  | Version 版本 | Changes 變更   |
| ---------- | ------------ | -------------- |
| 2025-11-30 | 1.0.0        | Initial README |

---

**Owner 負責人**: Governance Team  
**Last Updated 最後更新**: 2025-11-30

# Supply Chain Directory

This directory contains supply chain security artifacts for SynergyMesh.

## Structure

```
supply-chain/
├── sbom/          # Software Bill of Materials
├── attestations/  # SLSA/L3 evidence
└── registry/      # Component registry (optional)
```

## Components

### SBOM (`sbom/`)

Software Bill of Materials containing:

- SPDX format SBOMs
- Provenance information
- Signing policies

### Attestations (`attestations/`)

SLSA Level 3 attestation evidence:

- Build attestations
- Provenance records
- Verification artifacts

### Registry (`registry/`)

Optional component registry for:

- Module versions
- Service definitions
- Contract schemas

## SLSA Compliance

SynergyMesh follows SLSA (Supply-chain Levels for Software Artifacts) framework:

- Level 1: Documentation of build process
- Level 2: Tamper resistance through hosted build
- Level 3: Security against specific threats

## See Also

- [SLSA Framework](https://slsa.dev/)
- [Migration Guide](../docs/MIGRATION.md)
- [Sigstore Documentation](https://docs.sigstore.dev/)

## Directory Structure

### Canonical Directories (Use These)

- `23-policies/` - Governance policies (consolidated)
- `26-tools/` - Governance tools
- `28-tests/` - Test suites
- `31-schemas/` - JSON/YAML schemas (consolidated)
- `33-common/` - Common utilities
- `35-scripts/` - Automation scripts (consolidated)

### Deprecated Directories (Do Not Use)

- ~~`policies/`~~ → Use `23-policies/`
- ~~`schemas/`~~ → Use `31-schemas/`
- ~~`scripts/`~~ → Use `35-scripts/`

Last updated: 2025-12-12
