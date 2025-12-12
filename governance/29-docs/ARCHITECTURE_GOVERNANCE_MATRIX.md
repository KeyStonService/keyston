# Architecture Governance Matrix

# 架構治理矩陣

> **Version**: 1.0.0  
> **Status**: Active  
> **Owner**: Architecture Team  
> **Last Updated**: 2025-12-07

## 📋 Overview | 概述

The Architecture Governance Matrix is a comprehensive framework that defines how
the SynergyMesh system is structured, managed, and evolved. It extends beyond
simple directory mapping to include behavioral contracts, ownership, policies,
and quality metrics.

架構治理矩陣是一個全面的框架，定義了 SynergyMesh 系統如何被構建、管理和演化。它超越了簡單的目錄映射，包含了行為契約、所有權、策略和品質指標。

---

## 🎯 The Nine Governance Dimensions | 九個治理維度

This matrix consists of **three core structural contracts** and **six extended
governance dimensions**:

本矩陣由 **三個核心結構契約** 和 **六個延伸治理維度** 組成：

### Core Structural Contracts | 核心結構契約

1. **[Namespace](#1-namespace--命名空間)** - Define logical boundaries and
   layers
2. **[Module Mapping](#2-module-mapping--模組映射)** - Map logical IDs to
   physical paths
3. **[Dependency Rules](#3-dependency-rules--引用規則)** - Control who can call
   whom

### Extended Governance Dimensions | 延伸治理維度

1. **[Layers & Domains](#4-layers--domains--層級與領域)** - Semantic definitions
   for each layer
2. **[Roles & Capabilities](#5-roles--capabilities--模組角色與能力)** - What
   each module does
3. **[Behavior Contracts](#6-behavior-contracts--行為契約)** - Expected
   behaviors (API/events)
4. **[Lifecycle & Ownership](#7-lifecycle--ownership--生命週期與所有權)** -
   Responsibility and state
5. **[Policies & Constraints](#8-policies--constraints--策略與約束)** -
   Executable governance rules
6. **[Quality & Metrics](#9-quality--metrics--品質與指標)** - Health and
   evolution tracking

---

## 1. Namespace | 命名空間

**Purpose**: Define the logical naming scheme that tells everyone "which
layer/domain does this belong to".

**用途**: 定義邏輯命名方案，告訴大家「這個東西屬於哪一層/哪個域」。

### Location | 位置

- **Primary**: `synergymesh.yaml` - System-wide namespace definitions
- **Module-level**: `config/system-module-map.yaml` - Module namespace
  assignments

### Namespace Structure | 命名空間結構

```yaml
# Standard namespaces
core.*                 # Core platform modules
services.*             # Service layer
apps.*                 # Application layer
automation.*           # Automation modules
governance.*           # Governance definitions
infrastructure.*       # Infrastructure components
runtime.*              # Runtime components
```

### Examples | 範例

- `core.contract_service.L1` → Core layer, contract service, Level 1
- `services.mcp.code_analyzer` → Service layer, MCP protocol, code analyzer
- `apps.web.ui` → Application layer, web app, UI component

### Related Files | 相關檔案

- [`synergymesh.yaml`](../synergymesh.yaml)
- [`config/system-module-map.yaml`](../config/system-module-map.yaml)

---

## 2. Module Mapping | 模組映射

**Purpose**: Map logical module IDs to actual physical paths/subprojects.

**用途**: 把「邏輯模組 ID」跟「實際路徑/子專案」對上。

### Location | 位置

- **Primary**: `config/system-module-map.yaml`

### Mapping Structure | 映射結構

Each module mapping includes:

- **Logical ID**: Namespace-based identifier
- **Physical Path**: Actual directory location
- **Description**: What the module does
- **Components**: Sub-components provided

### Example | 範例

```yaml
core_platform:
  unified_integration:
    path: 'core/unified_integration/'
    description: '統一系統整合層'
    components:
      - id: 'service_registry'
        file: 'service_registry.py'
        provides: ['ServiceDiscovery', 'HealthMonitoring']
```

### Related Files | 相關檔案

- [`config/system-module-map.yaml`](../config/system-module-map.yaml)

---

## 3. Dependency Rules | 引用規則

**Purpose**: Control dependency relationships - who can call whom, preventing
circular dependencies and layering violations.

**用途**: 限制「誰可以叫誰」，避免亂引用和循環依賴。

### Location | 位置

- **Rules**: `governance/23-policies/` - OPA/Rego policies
- **Configuration**: `config/system-module-map.yaml` - Module-level constraints

### Dependency Principles | 依賴原則

1. **Layer Rules**: Higher layers can depend on lower layers, not vice versa
2. **Domain Isolation**: Cross-domain dependencies must go through well-defined
   interfaces
3. **No Circular Dependencies**: Strictly prohibited at all levels

### Example Rules | 規則範例

```yaml
architecture_constraints:
  allowed_dependencies:
    - 'core/*'
    - 'runtime/*'
  banned_dependencies:
    - 'apps/**'
    - 'services/**'
  dependency_direction: 'downstream_only'
```

### Related Files | 相關檔案

- [`governance/23-policies/`](./policies/)
- [`config/system-module-map.yaml`](../config/system-module-map.yaml)

---

## 4. Layers & Domains | 層級與領域

**Purpose**: Give semantic meaning to namespaces - not just strings, but clear
responsibilities and boundaries.

**用途**: 讓「命名空間」不只是字串，而是有明確語意、責任與邊界。

### Location | 位置

- **Primary**: `governance/01-architecture/config/layers-domains.yaml`

### Layer Definitions | 層級定義

| Layer              | Responsibility             | Can Depend On           | Cannot Depend On     |
| ------------------ | -------------------------- | ----------------------- | -------------------- |
| **core**           | Platform fundamentals      | runtime, infrastructure | apps, services       |
| **runtime**        | Execution environment      | infrastructure          | core, apps, services |
| **services**       | Business services          | core, runtime           | apps                 |
| **apps**           | User-facing applications   | services, core, runtime | -                    |
| **automation**     | Automation & orchestration | core, services, runtime | apps                 |
| **governance**     | Policies & rules           | None (config only)      | All                  |
| **infrastructure** | Infrastructure primitives  | None                    | All                  |

### Domain Definitions | 領域定義

Domains are orthogonal to layers and represent functional areas:

- **billing**: Billing and financial operations
- **contract**: Contract management
- **autonomous**: Autonomous systems (drone/UAV)
- **language-governance**: Multi-language policy
- **security**: Security & compliance

### Related Files | 相關檔案

- [`governance/01-architecture/config/layers-domains.yaml`](./01-architecture/config/layers-domains.yaml)

---

## 5. Roles & Capabilities | 模組角色與能力

**Purpose**: Extend module mapping with behavioral intent - what is this module
for?

**用途**: 在「映射名稱」上再加一層：這個模組是幹嘛的？有什麼能力？

### Location | 位置

- **Inline**: Extended fields in `config/system-module-map.yaml`
- **Detailed**: `governance/36-modules/{module-id}.yaml`

### Role Types | 角色類型

- `api-gateway`: API entry point
- `domain-service`: Core business logic
- `adapter`: External system integration
- `policy-engine`: Policy enforcement
- `orchestrator`: Workflow coordination
- `data-processor`: Data transformation

### Capability Model | 能力模型

Each module declares its capabilities:

```yaml
module: core.contract_service.L1
role: domain-service
capabilities:
  - read-contracts
  - write-contracts
  - validate-signatures
  - issue-attestations
```

### Related Files | 相關檔案

- [`config/system-module-map.yaml`](../config/system-module-map.yaml)
  (capability_matrix section)
- [`governance/36-modules/`](./modules/) (detailed specs)

---

## 6. Behavior Contracts | 行為契約

**Purpose**: Define expected behaviors - not just "who can call whom", but "what
happens when you call it".

**用途**: 讓「引用規則」不只是誰可以叫誰，而是：「叫了之後、可以期待什麼行為」。

### Location | 位置

- **Primary**: `governance/37-behavior-contracts/{module-id}.yaml`

### Contract Components | 契約組成

1. **API Contracts**: Input/output schemas, endpoints
2. **Event Contracts**: Event topics, payloads, guarantees
3. **Invariants**: Conditions that must always hold
4. **Failure Modes**: Error codes, failure scenarios

### Example Contract | 契約範例

```yaml
module: core.contract_service.L1
version: '1.0.0'

api:
  - endpoint: POST /contracts
    input_schema: ContractCreateRequest
    output_schema: ContractCreateResponse
    guarantees:
      - 'Contract ID is unique'
      - 'Timestamp is monotonic'

events:
  - topic: contract.created
    payload_schema: ContractCreatedEvent
    delivery: at-least-once

invariants:
  - 'Never modifies final settlement state'
  - 'Always validates signatures before storage'

failure_modes:
  - code: ERR_INVALID_SIGNATURE
    condition: 'Signature verification fails'
    recovery: 'Return 400 with details'
```

### Related Files | 相關檔案

- [`governance/37-behavior-contracts/`](./behavior-contracts/)

---

## 7. Lifecycle & Ownership | 生命週期與所有權

**Purpose**: Associate modules with responsible teams and track their lifecycle
state.

**用途**: 讓命名空間/模組，不只是技術物件，而是有「責任人與狀態」。

### Location | 位置

- **Primary**: `governance/34-config/ownership-map.yaml`
- **Inline**: Extended fields in `config/system-module-map.yaml`

### Lifecycle States | 生命週期狀態

- `experimental`: Under development, API may change
- `active`: Production-ready, stable API
- `maintenance`: Stable but not actively developed
- `legacy`: Deprecated, use alternatives
- `deprecated`: Will be removed in future

### Ownership Model | 所有權模型

```yaml
module: core.contract_service.L1
owner: '@core-platform-team'
backup_owner: '@security-team'
lifecycle: active
sla:
  availability: '99.9%'
  response_time: '< 100ms p99'
  upgrade_cadence: 'quarterly'
```

### Related Files | 相關檔案

- [`governance/34-config/ownership-map.yaml`](./ownership-map.yaml)
- [`config/system-module-map.yaml`](../config/system-module-map.yaml)

---

## 8. Policies & Constraints | 策略與約束

**Purpose**: Make dependency rules and architecture constraints
machine-checkable.

**用途**: 把「命名空間+映射+引用規則」上升為「可執行/可驗證的架構 policy」。

### Location | 位置

- **OPA Policies**: `governance/23-policies/architecture/*.rego`
- **YAML Rules**: `governance/23-policies/architecture-rules.yaml`

### Policy Categories | 策略類別

1. **Language Boundaries**: Which languages allowed in which layers
2. **Security Boundaries**: Network access, secret handling
3. **Data Flow Constraints**: Cross-layer data restrictions
4. **Anti-patterns**: Prohibited dependency patterns

### Example Policy | 策略範例

```rego
# governance/23-policies/architecture/layer-dependencies.rego
package architecture.layers

violation[msg] {
    module := input.modules[_]
    dependency := module.dependencies[_]

    # Apps cannot depend on core directly
    startswith(module.id, "apps.")
    startswith(dependency, "core.")

    msg := sprintf("Module %s cannot directly depend on %s", [module.id, dependency])
}
```

### Related Files | 相關檔案

- [`governance/23-policies/`](./policies/)
- OPA policy documentation

---

## 9. Quality & Metrics | 品質與指標

**Purpose**: Make architecture and governance measurable and trackable.

**用途**: 把結構治理→上升為「可量測、可演化」的架構健康度。

### Location | 位置

- **Metrics**: `governance/34-config/architecture-health.yaml`
- **Reports**: `docs/ARCHITECTURE_HEALTH_REPORT.md`

### Key Metrics | 關鍵指標

1. **Governance Compliance**
   - Dependency rule violations
   - Undefined namespace usage
   - Missing behavior contracts
   - Modules without owners

2. **Code Quality**
   - Test coverage by module
   - Cyclomatic complexity
   - Security vulnerabilities
   - Language policy violations

3. **Architecture Health**
   - Circular dependency count
   - Layer violation count
   - Cross-domain coupling
   - Technical debt score

### Health Thresholds | 健康門檻

```yaml
thresholds:
  dependency_violations: 0 # Zero tolerance
  undefined_namespaces: 0 # All must be defined
  missing_contracts: 10 # Gradual improvement
  missing_owners: 5 # Critical modules first
  test_coverage_min: 70 # 70% minimum
  complexity_max: 15 # Per function
```

### Related Files | 相關檔案

- [`governance/34-config/architecture-health.yaml`](./architecture-health.yaml)
- [`docs/ARCHITECTURE_HEALTH_REPORT.md`](../docs/ARCHITECTURE_HEALTH_REPORT.md)

---

## 🔄 Integration & Workflow | 整合與工作流程

### How the Dimensions Work Together | 各維度如何協同工作

1. **Development Time**
   - Developer uses **Namespace** to locate module
   - Checks **Module Mapping** for physical path
   - Reviews **Behavior Contract** to understand API
   - Verifies **Dependency Rules** before adding imports

2. **Review Time**
   - CI validates **Policies & Constraints**
   - Checks **Lifecycle & Ownership** for approval routing
   - Measures **Quality & Metrics** against thresholds
   - Verifies **Roles & Capabilities** alignment

3. **Evolution Time**
   - **Quality Metrics** identify refactoring candidates
   - **Ownership Map** determines who decides
   - **Layers & Domains** guide restructuring
   - **Behavior Contracts** ensure backward compatibility

### Automated Validation | 自動化驗證

```bash
# Validate governance matrix completeness
make validate-governance

# Check architecture health
make architecture-health

# Run policy checks
make policy-check
```

---

## 📚 Related Documentation | 相關文檔

- [System Module Map](../config/system-module-map.yaml)
- [Governance Policies](./policies/)
- [Architecture Layers](./architecture/layers-domains.yaml)
- [Documentation Index](../DOCUMENTATION_INDEX.md)

---

## 🎯 Strategic Value | 戰略價值

### Benefits | 好處

✅ **Clarity**: Architecture governance is explicit, not implicit  
✅ **Onboarding**: New AI agents/developers understand the system quickly  
✅ **Evolution**: Automated decision-making for refactoring  
✅ **Quality**: Measurable architecture health

### Trade-offs | 代價

⚠️ **Upfront Cost**: More specs, READMEs, and YAML files to write  
⚠️ **Maintenance**: Must keep governance artifacts synchronized  
⚠️ **Discipline**: Requires team commitment to governance

### Mitigation | 緩解策略

- Integrate governance checks into CI/CD
- Auto-generate reports and dashboards
- Make governance violations visible and actionable

---

## 📝 Version History | 版本歷史

| Date       | Version | Changes                                |
| ---------- | ------- | -------------------------------------- |
| 2025-12-07 | 1.0.0   | Initial Architecture Governance Matrix |

---

**Owner**: Architecture Team  
**Maintainers**: @core-owners, @architecture-team  
**Review Cycle**: Quarterly
