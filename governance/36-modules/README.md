# Module Roles & Capabilities

# 模組角色與能力

> **Purpose**: Define roles and capabilities for individual modules  
> **用途**: 定義個別模組的角色和能力

## 📋 Overview | 概述

This directory contains detailed module-level specifications that extend the
basic module mapping with behavioral intent and capability declarations.

本目錄包含詳細的模組級規範，通過行為意圖和能力聲明擴展基本模組映射。

## 📁 Structure | 結構

Each module can have a detailed specification file:

```
governance/36-modules/
├── README.md                          # This file
├── module-registry.yaml              # Registry & completeness tracker
├── core.contract_service.L1.yaml     # Example module spec
├── core.unified_integration.yaml     # Example module spec
└── {module-namespace-id}.yaml        # One file per module
```

## 📄 Module Specification Format | 模組規範格式

Each module specification file should follow this structure:

```yaml
module: 'core.contract_service.L1'
version: '1.0.0'
status: 'active'

# Role definition
role: 'domain-service'
role_description: 'Core business logic for contract management'

# Capabilities
capabilities:
  - id: 'read-contracts'
    description: 'Query and retrieve contract data'
  - id: 'write-contracts'
    description: 'Create and modify contracts'
  - id: 'validate-signatures'
    description: 'Verify contract signatures'

# Technical details
tech_stack:
  languages: ['typescript', 'python']
  frameworks: ['express', 'zod']
  databases: ['postgresql']

# Integration points
provides:
  - 'ContractManagement'
  - 'ProvenanceAttestation'

depends_on:
  - 'core.slsa_provenance'
  - 'infrastructure.database'

# Ownership
owner: '@core-platform-team'
lifecycle: 'active'
```

## 🎯 Role Types | 角色類型

### Standard Role Types

| Role             | Purpose                           | Examples                            |
| ---------------- | --------------------------------- | ----------------------------------- |
| `api-gateway`    | Entry point for external requests | API Gateway, Load Balancer          |
| `domain-service` | Core business logic               | Contract Service, Billing Service   |
| `adapter`        | External system integration       | Database Adapter, Cloud API Adapter |
| `policy-engine`  | Policy enforcement                | Access Control, Rate Limiter        |
| `orchestrator`   | Workflow coordination             | Task Scheduler, Workflow Engine     |
| `data-processor` | Data transformation               | ETL Pipeline, Analytics Engine      |
| `ui-component`   | User interface element            | Dashboard, Admin Panel              |

## 📊 Capability Model | 能力模型

### Capability Categories

1. **Data Operations**
   - `read-*`: Read/query capabilities
   - `write-*`: Create/update capabilities
   - `delete-*`: Delete/archive capabilities

2. **Processing**
   - `validate-*`: Validation logic
   - `transform-*`: Data transformation
   - `aggregate-*`: Data aggregation

3. **Integration**
   - `publish-*`: Event publishing
   - `subscribe-*`: Event consumption
   - `sync-*`: External system synchronization

4. **Governance**
   - `enforce-*`: Policy enforcement
   - `audit-*`: Audit logging
   - `monitor-*`: Monitoring/observability

## 🔗 Usage | 使用方式

### For Developers

1. **Finding Module Capabilities**

   ```bash
   # List all capabilities for a module
   cat governance/36-modules/core.contract_service.L1.yaml | yq '.capabilities'
   ```

2. **Understanding Dependencies**

   ```bash
   # Check what a module depends on
   cat governance/36-modules/core.contract_service.L1.yaml | yq '.depends_on'
   ```

### For AI Agents

When planning to use or modify a module:

1. Check the module's role to understand its purpose
2. Review its capabilities to see what it provides
3. Verify dependencies before making changes
4. Consult the owner for architectural questions

### For Architects

1. Use role definitions to plan system structure
2. Capability declarations help identify gaps
3. Dependency mappings reveal coupling issues
4. Owner information routes design decisions

## 📝 Creating New Module Specs | 創建新模組規範

When adding a new module or enhancing an existing one:

1. **Create the spec file**: `governance/36-modules/{namespace}.yaml`
2. **Define the role**: Choose appropriate role type
3. **List capabilities**: Be specific and action-oriented
4. **Document dependencies**: Include all runtime dependencies
5. **Assign ownership**: Specify team and lifecycle state
6. **Link behavior contract**: Reference the detailed contract in
   `governance/37-behavior-contracts/`
7. **Register the module**: Add or update the entry in
   `governance/36-modules/module-registry.yaml` to keep the completeness map
   accurate (spec status, behavior contract linkage, test/docs readiness).

## ✅ Validation | 驗證

Module specifications are validated as part of CI:

```bash
# Validate module specification format
make validate-governance

# Check for orphaned modules (spec but no code)
make check-module-mapping
```

## 🔗 Related Documentation | 相關文檔

- [Architecture Governance Matrix](../ARCHITECTURE_GOVERNANCE_MATRIX.md)
- [Module Mapping](../../config/system-module-map.yaml)
- [Behavior Contracts](../behavior-contracts/)
- [Ownership Map](../ownership-map.yaml)
- [Layers & Domains](../architecture/layers-domains.yaml)

---

**Owner**: Architecture Team  
**Last Updated**: 2025-12-07
