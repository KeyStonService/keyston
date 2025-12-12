# Behavior Contracts

# 行為契約

> **Purpose**: Define expected behaviors, APIs, events, and invariants for
> modules  
> **用途**: 定義模組的預期行為、API、事件和不變條件

## 📋 Overview | 概述

Behavior contracts specify what happens when you call a module - not just "who
can call whom", but the complete behavioral specification including APIs,
events, invariants, and failure modes.

行為契約規定當您調用模組時會發生什麼 - 不僅僅是「誰可以調用誰」，而是包括 API、事件、不變條件和失敗模式的完整行為規範。

## 📁 Structure | 結構

```
governance/37-behavior-contracts/
├── README.md                           # This file
├── core.contract_service.L1.yaml      # Example contract
├── core.unified_integration.yaml      # Example contract
└── {module-namespace-id}.yaml         # One contract per module
```

## 📄 Contract Format | 契約格式

Each behavior contract file should include:

### 1. Module Identification | 模組識別

```yaml
contract:
  module: 'core.contract_service.L1'
  version: '1.0.0'
  status: 'active'
  owner: '@core-platform-team'
  description: 'Contract management with provenance'
```

### 2. API Contracts | API 契約

Define all public APIs with:

- Input/output schemas
- Guarantees (what will always be true)
- Error responses
- Performance expectations

```yaml
api:
  endpoints:
    - name: 'Create Contract'
      method: POST
      path: '/contracts'
      input_schema: { ... }
      output_schema: { ... }
      guarantees:
        - 'Contract ID is unique'
        - 'Signature is verified'
      error_responses: [...]
      performance:
        response_time_p99: '< 500ms'
```

### 3. Event Contracts | 事件契約

Define all events published/consumed:

- Event topics and payloads
- Delivery guarantees
- Ordering requirements
- Consumer list

```yaml
events:
  - name: 'contract.created'
    payload_schema: { ... }
    delivery_guarantee: 'at-least-once'
    ordering: 'per-contract'
    consumers:
      - 'services.billing'
      - 'services.audit'
```

### 4. Invariants | 不變條件

Conditions that must always hold:

- Business rules
- Data integrity constraints
- Security requirements

```yaml
invariants:
  - name: 'Signature Verification Required'
    description: 'All contracts must have verified signatures'
    rule: 'forall c in contracts: c.signature.verified = true'
    enforcement: 'pre-condition'
```

### 5. Failure Modes | 失敗模式

How the module behaves under failure:

- Error scenarios
- Recovery strategies
- Degraded mode behavior

```yaml
failure_modes:
  - scenario: 'Database Failure'
    triggers: ['Connection lost', 'Transaction timeout']
    recovery: ['Rollback', 'Return 500', 'Alert ops']
    error_code: 'ERR_DATABASE_FAILURE'
```

## 🎯 Why Behavior Contracts? | 為什麼需要行為契約？

### Benefits | 好處

1. **Clear Expectations**: Developers know exactly what to expect
2. **Safe Refactoring**: Changes that violate contracts are caught early
3. **Better Testing**: Contracts guide test case design
4. **Documentation**: Self-documenting system behavior
5. **Automation**: AI agents can reason about system behavior

### Use Cases | 使用場景

- **Development**: Understand API before implementation
- **Integration**: Know exactly how to call other modules
- **Refactoring**: Ensure backward compatibility
- **Testing**: Generate test cases from contracts
- **Monitoring**: Validate runtime behavior against contracts

## 📝 Creating a New Contract | 創建新契約

### Step-by-Step Guide

1. **Copy Template**

   ```bash
   cp governance/37-behavior-contracts/core.contract_service.L1.yaml \
      governance/37-behavior-contracts/your.module.yaml
   ```

2. **Fill in Module Info**
   - Module namespace ID
   - Version and status
   - Owner and description

3. **Define APIs**
   - List all public endpoints
   - Specify schemas (use JSON Schema)
   - Document guarantees and errors
   - Set performance expectations

4. **Define Events**
   - List events published
   - Specify payload schemas
   - Define delivery guarantees
   - List known consumers

5. **Document Invariants**
   - Business rules that never change
   - Data integrity constraints
   - Security requirements

6. **Describe Failure Modes**
   - Common error scenarios
   - Recovery strategies
   - Degraded mode behavior

7. **Add Dependencies**
   - Required modules
   - Optional modules
   - Failure behavior for each

8. **Testing Requirements**
   - Coverage expectations
   - Critical test scenarios
   - Performance benchmarks

## ✅ Validation | 驗證

### Automated Checks

Contracts are validated in CI:

```bash
# Validate contract syntax
make validate-contracts

# Check contract completeness
tools/governance/check-contract-coverage.py

# Verify contract compliance at runtime
make test-contracts
```

### Manual Review

Contracts require architecture team review when:

- Adding new public APIs
- Changing existing API contracts
- Modifying invariants
- Changing failure modes

## 🔧 Contract Evolution | 契約演化

### Versioning | 版本控制

- **Minor changes**: Same major version (1.1.0, 1.2.0)
  - Adding optional fields
  - New endpoints
  - Relaxing constraints

- **Breaking changes**: New major version (2.0.0)
  - Removing fields
  - Changing semantics
  - Tightening constraints

### Deprecation Process | 棄用流程

1. Mark feature as deprecated in contract
2. Provide migration path
3. Give 2 release cycles notice
4. Remove in next major version

```yaml
deprecated_features:
  - feature: 'Legacy signature algorithm'
    removed_in: '2.0.0'
    migration: 'Use RSA-SHA256 instead'
```

## 📊 Contract Coverage | 契約覆蓋率

Track which modules have behavior contracts:

| Layer      | Total Modules | With Contracts | Coverage |
| ---------- | ------------- | -------------- | -------- |
| Core       | 25            | 15             | 60%      |
| Services   | 12            | 8              | 67%      |
| Automation | 8             | 3              | 38%      |
| Apps       | 5             | 2              | 40%      |

**Goal**: 100% coverage for active modules by Q2 2026

## 🔗 Integration with Other Governance | 與其他治理的整合

### Links to Other Dimensions

- **Module Mapping**: Contracts reference modules in
  `config/system-module-map.yaml`
- **Ownership**: Owner field links to `governance/34-config/ownership-map.yaml`
- **Layers**: API patterns follow layer rules in
  `governance/01-architecture/config/layers-domains.yaml`
- **Policies**: Contracts are validated by
  `governance/23-policies/architecture-rules.yaml`
- **Health Metrics**: Coverage tracked in
  `governance/34-config/architecture-health.yaml`

## 🔍 Examples | 範例

### Complete Example

See [`core.contract_service.L1.yaml`](./core.contract_service.L1.yaml) for a
complete example covering:

- CRUD APIs
- Event publishing
- Invariants
- Failure modes
- Testing requirements
- Monitoring

### Quick Reference

```yaml
# Minimal contract
contract:
  module: 'services.example'
  version: '1.0.0'

api:
  endpoints:
    - name: 'Get Resource'
      method: GET
      path: '/resources/{id}'
      guarantees: ['Returns 404 if not found']

events:
  - name: 'resource.created'
    delivery_guarantee: 'at-least-once'

invariants:
  - name: 'IDs are unique'
    rule: 'forall r in resources: unique(r.id)'

failure_modes:
  - scenario: 'Not Found'
    error_code: 'ERR_NOT_FOUND'
```

## 🔗 Related Documentation | 相關文檔

- [Architecture Governance Matrix](../ARCHITECTURE_GOVERNANCE_MATRIX.md)
- [Module Roles & Capabilities](../modules/)
- [Ownership Map](../ownership-map.yaml)
- [Architecture Policies](../policies/architecture-rules.yaml)

---

**Owner**: Architecture Team  
**Last Updated**: 2025-12-07
