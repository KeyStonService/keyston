# 🔧 Common Governance Resources

> Shared governance policies, schemas, and tools used across all 14 governance
> dimensions and 9 meta-governance domains

## 📋 Overview

The Common Governance Resources directory provides shared infrastructure that:

- Defines reusable governance policies (OPA/Conftest rules)
- Provides common JSON schemas for governance configuration
- Supplies shared validation and analysis tools
- Enables consistent governance enforcement across all dimensions
- Prevents duplication and ensures consistency

## 📁 Structure

```
common/
├── policies/
│   ├── governance_base.rego             # Base OPA Rego policies
│   ├── policy_validation.rego           # Policy structure validation
│   ├── schema_validation.rego           # Schema validation rules
│   ├── configuration_rules.rego         # Configuration governance rules
│   └── security_baseline.rego           # Security governance baseline
├── schemas/
│   ├── policy.schema.json               # Standard governance policy schema
│   ├── config.schema.json               # Configuration schema
│   ├── framework.schema.json            # Framework definition schema
│   ├── docs-index.schema.json           # Documentation index schema
│   └── dependency.schema.json           # Dependency definition schema
├── tools/
│   ├── validate_governance_matrix.py    # Master validation tool
│   ├── governance_policy_checker.py     # Policy compliance checker
│   ├── schema_validator.py              # Schema validation tool
│   ├── dependency_analyzer.py           # Dependency graph analyzer
│   └── governance_report_generator.py   # Cross-dimension reporting
└── __init__.py
```

## 🎯 Core Governance Resources

### 1. Shared OPA Policies

**governance_base.rego**

- Base policies for all governance validations
- Common denial rules
- Standard decision-making rules
- Reusable functions

**policy_validation.rego**

- Validates policy YAML structure
- Checks required fields
- Enforces naming conventions
- Ensures no circular dependencies

**schema_validation.rego**

- Validates JSON schema definitions
- Checks schema completeness
- Enforces schema naming standards
- Validates schema references

**configuration_rules.rego**

- Configuration file validation
- Environment-specific rules
- Deployment validation rules
- Runtime policy enforcement

**security_baseline.rego**

- Baseline security policies
- Compliance requirements
- Audit requirements
- Encryption standards

### 2. Common Schemas

**policy.schema.json**

```json
{
  "type": "object",
  "required": ["name", "description", "rules"],
  "properties": {
    "name": { "type": "string" },
    "description": { "type": "string" },
    "version": { "type": "string" },
    "rules": { "type": "array" },
    "dependencies": { "type": "array" },
    "enforcement": { "enum": ["strict", "warning", "advisory"] }
  }
}
```

**config.schema.json**

- Configuration file structure
- Environment variable requirements
- Secret management
- Override mechanisms

**framework.schema.json**

- Governance framework definitions
- Component specifications
- Responsibility mappings
- Evolution tracking

**docs-index.schema.json**

- Documentation metadata
- Navigation structure
- Language support
- Version tracking

**dependency.schema.json**

- Dependency declarations
- Version constraints
- Initialization order
- Health check definitions

### 3. Shared Tools

**validate_governance_matrix.py**

- Master validator ensuring all 14 dimensions comply with all 9 meta-governance
  domains
- Generates comprehensive compliance matrix
- Identifies gaps and conflicts
- Produces cross-dimensional reports

**governance_policy_checker.py**

- Checks OPA policies across all domains
- Validates policy compliance
- Reports violations
- Suggests corrections

**schema_validator.py**

- Validates all configuration files against schemas
- Checks schema definitions
- Ensures schema compatibility
- Reports schema issues

**dependency_analyzer.py**

- Analyzes dependency graphs
- Detects circular dependencies
- Validates initialization order
- Reports bottlenecks

**governance_report_generator.py**

- Generates cross-dimensional governance reports
- Aggregates metrics from all dimensions
- Produces compliance dashboards
- Exports governance status

## 🔗 Integration Points

### Used By All 14 Governance Dimensions

- Each dimension uses common policy schemas
- All dimensions validate against common schemas
- Shared tools provide consistent governance

### Used By All 9 Meta-Governance Domains

- Each domain leverages common policies
- Shared tools enable cross-domain validation
- Common schemas ensure data compatibility

### Dependency Graph

```
common/ (foundation)
├── policies/ ← Used by all domains for validation
├── schemas/ ← Used by all domains for configuration
└── tools/ ← Used by all domains for analysis
    ↓
14 dimensions + 9 meta-domains
```

## 📊 Governance Matrix

This resource enables the master governance matrix:

| Dimension               | Arch | API | Data | Testing | Identity | Perf/Rel | Cost | Docs | Common |
| ----------------------- | ---- | --- | ---- | ------- | -------- | -------- | ---- | ---- | ------ |
| governance-architecture | ✅   | ✅  | ✅   | ✅      | ✅       | ✅       | ✅   | ✅   | ✅     |
| decision-governance     | ✅   | ✅  | ✅   | ✅      | ✅       | ✅       | ✅   | ✅   | ✅     |
| change-governance       | ✅   | ✅  | ✅   | ✅      | ✅       | ✅       | ✅   | ✅   | ✅     |
| ... (all 14 dimensions) | ✅   | ✅  | ✅   | ✅      | ✅       | ✅       | ✅   | ✅   | ✅     |

Legend: ✅ = Uses common resources and must comply with governance

## 🛠️ Usage Examples

### Validating Configuration Against Schema

```bash
python3 schema_validator.py path/to/config.yaml policy.schema.json
```

### Running Governance Policy Checks

```bash
python3 governance_policy_checker.py --policy-dir ./policies --target-dir ../governance-*
```

### Generating Governance Matrix Report

```bash
python3 validate_governance_matrix.py --output report.html
```

### Analyzing Dependencies

```bash
python3 dependency_analyzer.py --governance-root ../
```

## 📈 Governance Metrics Tracked

- Total policies across all domains
- Schema validation compliance
- Configuration correctness rate
- Dependency graph health
- Cross-dimensional compliance percentage
- Policy violation trends
- Tool execution statistics

---

**Status**: Foundation Governance Resources **Last Updated**: 2025-12-09 **Used
By**: 14 dimensions + 9 meta-governance domains
