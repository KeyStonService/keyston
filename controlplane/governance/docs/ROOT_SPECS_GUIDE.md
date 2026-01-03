# 📚 Root Layer Specifications Guide

**Version:** 1.0.0  
**Last Updated:** 2025-12-21  
**Status:** Active

---

## 🎯 Overview

This guide provides comprehensive documentation for the Root Layer Specifications system - a machine-verifiable governance framework that ensures consistency, correctness, and compliance across all root layer configurations.

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Specification Files](#specification-files)
4. [Registry Files](#registry-files)
5. [Validation System](#validation-system)
6. [Usage Guide](#usage-guide)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## 🌟 Introduction

### What is the Root Specs System?

The Root Layer Specifications system is a comprehensive governance framework that:

- **Enforces naming conventions** across all root layer files
- **Validates references** to ensure all URNs and dependencies are resolvable
- **Checks mappings** between modules, files, and resources
- **Verifies logical consistency** including dependency cycles and state validity
- **Ensures context consistency** across multiple configuration files

### Why Machine-Verifiable?

Traditional documentation often becomes outdated and ignored. Our approach:

✅ **Automated Enforcement** - GitHub Actions automatically block non-compliant PRs  
✅ **Single Source of Truth** - Registries serve as authoritative sources  
✅ **Clear Error Messages** - Specific violations with fix suggestions  
✅ **Zero Ambiguity** - Regex patterns and algorithms define exact rules  

---

## 🏗️ Architecture

### System Components

```
Root Layer Specifications System
│
├── 📋 Specification Files (root.specs.*.yaml)
│   ├── root.specs.naming.yaml      - Naming conventions
│   ├── root.specs.references.yaml  - Reference formats
│   ├── root.specs.mapping.yaml     - Mapping rules
│   ├── root.specs.logic.yaml       - Logical consistency
│   └── root.specs.context.yaml     - Context consistency
│
├── 📦 Registry Files (root.registry.*.yaml)
│   ├── root.registry.modules.yaml  - Module SSOT
│   └── root.registry.urns.yaml     - URN SSOT
│
├── 🔍 Validation System
│   ├── scripts/validation/validate-root-specs.py
│   └── .github/workflows/gate-root-specs.yml
│
└── 🗺️ Gates Map
    └── gates.map.yaml              - Unified gate registry
```

### Data Flow

```
1. Developer creates/modifies root.*.yaml
2. Git commit triggers PR
3. GitHub Actions runs gate-root-specs.yml
4. Validation script checks all specifications
5. If violations found → PR blocked + detailed report
6. If all pass → PR can be merged
```

---

## 📋 Specification Files

### 1. Naming Specification (`root.specs.naming.yaml`)

**Purpose:** Defines naming conventions for files, keys, values, and identifiers.

**Key Rules:**

- **File Names:** `root.<category>.<ext>` format, lowercase only
- **YAML Keys:** `snake_case` format (e.g., `module_name`)
- **Module Names:** `kebab-case` format (e.g., `governance-engine`)
- **Versions:** Semantic Versioning 2.0.0 (e.g., `1.0.0`)
- **API Versions:** `domain/version` format (e.g., `machinenativeops.io/v1`)
- **Kind Names:** `PascalCase` with `Root` prefix (e.g., `RootModulesConfig`)

**Example Violations:**

```yaml
# ❌ WRONG
moduleName: "GovernanceEngine"  # camelCase, PascalCase
version: "1.0"                  # Incomplete version
apiVersion: "v1"                # Missing domain

# ✅ CORRECT
module_name: "governance-engine"
version: "1.0.0"
apiVersion: "machinenativeops.io/v1"
```

### 2. Reference Specification (`root.specs.references.yaml`)

**Purpose:** Defines reference formats and validation rules.

**URN Format:**

```
urn:machinenativeops:{type}:{identifier}[:version]

Examples:
- urn:machinenativeops:module:governance-engine:v1
- urn:machinenativeops:config:root-config:v1
- urn:machinenativeops:policy:rbac-policy:v1
```

**Key Rules:**

- All `*_ref` fields must use URN format
- All URNs must exist in `root.registry.urns.yaml`
- Dependencies must be resolvable
- No circular dependencies allowed

### 3. Mapping Specification (`root.specs.mapping.yaml`)

**Purpose:** Defines mapping relationships between resources.

**Key Mappings:**

1. **Module Mapping:** `module_name` → `file_path` → `config_file` → `log_file`
2. **URN Mapping:** `urn` → `resource_type` → `target_registry`
3. **Device Mapping:** `device_path` → `resource_type` → `resource_id`
4. **Filesystem Mapping:** `directory_path` → `purpose` → `description`

**Example:**

```yaml
# Module: governance-engine
name: "governance-engine"
entrypoint: "/opt/machinenativenops/modules/governance-engine/main.py"
config_file: "config/governance-engine.yaml"
log_file: "/var/log/machinenativenops/governance-engine.log"
```

### 4. Logic Specification (`root.specs.logic.yaml`)

**Purpose:** Defines logical consistency rules.

**Key Rules:**

- **Mutual Exclusion:** No conflicting states
- **Dependencies:** Must exist and be acyclic
- **State Consistency:** Enabled modules must have entrypoints
- **Resource Constraints:** Requests ≤ Limits
- **Temporal Logic:** Timeouts > Intervals

**Cycle Detection Algorithm:**

```python
def detect_cycle(graph):
    visited = set()
    rec_stack = set()
    
    for node in graph.nodes:
        if node not in visited:
            if dfs(node, visited, rec_stack):
                return True  # Cycle detected
    return False
```

### 5. Context Specification (`root.specs.context.yaml`)

**Purpose:** Ensures context consistency across files.

**Key Context Keys:**

- `module_id` - Immutable, global scope
- `name` - Per resource type scope
- `version` - Per module scope
- `namespace` - Per resource scope
- `apiVersion` - Per file scope
- `kind` - Per resource scope

**Consistency Rules:**

- Same module must have same name across all files
- Version labels must match spec versions
- Same resource type should use same namespace

---

## 📦 Registry Files

### Module Registry (`root.registry.modules.yaml`)

**Purpose:** Single Source of Truth for all modules.

**Structure:**

```yaml
spec:
  modules:
    - id: "governance-engine"
      name: "governance-engine"
      version: "1.0.0"
      urn: "urn:machinenativeops:module:governance-engine:v1"
      dependencies:
        - module_id: "config-manager"
          version: ">=1.0.0"
```

**Key Features:**

- Authoritative source for module information
- Dependency graph with topological sort
- Load order calculation
- Cycle detection

### URN Registry (`root.registry.urns.yaml`)

**Purpose:** Single Source of Truth for all URNs.

**Structure:**

```yaml
spec:
  module_urns:
    - urn: "urn:machinenativeops:module:governance-engine:v1"
      type: "module"
      target_registry: "root.registry.modules.yaml"
      target_path: "spec.modules[id=governance-engine]"
```

**Key Features:**

- Unique URN enforcement
- Target existence validation
- Type matching verification
- Resolution strategy definition

---

## 🔍 Validation System

### Python Validator (`validate-root-specs.py`)

**Features:**

- Loads all specifications and registries
- Validates naming conventions
- Checks reference formats and existence
- Verifies mapping consistency
- Detects logical violations
- Identifies context drift

**Usage:**

```bash
# Run validation
python scripts/validation/validate-root-specs.py

# Output: root-specs-validation-report.md
```

### GitHub Actions Gate (`gate-root-specs.yml`)

**Triggers:**

- Pull requests modifying `root.*.yaml`, `root.*.map`, `root.*.sh`
- Push to main branch

**Validation Steps:**

1. ✅ Naming Validation
2. ✅ Reference Validation
3. ✅ Mapping Validation
4. ✅ Logic Validation
5. ✅ Context Validation
6. ✅ Python Validator

**On Failure:**

- PR is blocked
- Detailed report added as comment
- Specific violations highlighted
- Fix suggestions provided

---

## 📖 Usage Guide

### For Developers

#### Adding a New Module

1. **Add to Module Registry:**

```yaml
# root.registry.modules.yaml
- id: "new-module"
  name: "new-module"
  version: "1.0.0"
  urn: "urn:machinenativeops:module:new-module:v1"
  dependencies: []
```

1. **Add URN to URN Registry:**

```yaml
# root.registry.urns.yaml
- urn: "urn:machinenativeops:module:new-module:v1"
  type: "module"
  target_registry: "root.registry.modules.yaml"
```

1. **Add to Modules Config:**

```yaml
# root.modules.yaml
- name: "new-module"
  version: "1.0.0"
  entrypoint: "/opt/machinenativenops/modules/new-module/main.py"
```

1. **Run Validation:**

```bash
python scripts/validation/validate-root-specs.py
```

#### Modifying Existing Configuration

1. Make changes to `root.*.yaml` files
2. Ensure consistency across related files
3. Run local validation
4. Create PR
5. Wait for automated validation
6. Fix any violations reported

### For Reviewers

#### Reviewing PRs

1. Check automated validation results
2. Review validation report
3. Verify fixes address root causes
4. Ensure no workarounds or hacks
5. Approve only if all gates pass

---

## 💡 Best Practices

### DO ✅

- **Use registries as SSOT** - Always reference registries for authoritative data
- **Run validation locally** - Catch issues before pushing
- **Follow naming conventions** - Use lowercase, kebab-case, snake_case appropriately
- **Document complex mappings** - Add comments for non-obvious relationships
- **Keep versions synchronized** - Update all references when bumping versions

### DON'T ❌

- **Don't bypass validation** - Never disable gates or force merge
- **Don't duplicate data** - Use references instead of copying
- **Don't use hardcoded paths** - Use configuration references
- **Don't create circular dependencies** - Design acyclic dependency graphs
- **Don't ignore warnings** - Address warnings before they become errors

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "File name does not match pattern"

**Cause:** File name contains uppercase, spaces, or wrong extension

**Fix:**

```bash
# Wrong
Root.Config.yaml
root config.yaml
root.config.yml

# Correct
root.config.yaml
```

#### Issue: "URN does not match pattern"

**Cause:** URN format incorrect

**Fix:**

```yaml
# Wrong
urn:machinenativeops:module:governance-engine
urn:machinenativeops:Module:governance-engine

# Correct
urn:machinenativeops:module:governance-engine:v1
```

#### Issue: "Circular dependency detected"

**Cause:** Module A depends on B, B depends on C, C depends on A

**Fix:** Redesign dependency graph to be acyclic

```yaml
# Wrong
A → B → C → A  # Cycle!

# Correct
A → B → C  # Acyclic
```

#### Issue: "Module name inconsistent across files"

**Cause:** Same module has different names in different files

**Fix:** Use exact same name everywhere

```yaml
# root.registry.modules.yaml
name: "governance-engine"

# root.modules.yaml
name: "governance-engine"  # Must match exactly

# root.bootstrap.yaml
modules: ["governance-engine"]  # Must match exactly
```

---

## 📞 Support

### Getting Help

- **Documentation:** This guide
- **Validation Reports:** Check `root-specs-validation-report.md`
- **GitHub Issues:** Create issue with `specs` label
- **Team Chat:** #governance-specs channel

### Contributing

To improve specifications:

1. Propose changes in issue
2. Update specification files
3. Update validation logic
4. Update documentation
5. Create PR with evidence

---

## 📊 Appendix

### Specification File Reference

| File | Purpose | Key Sections |
|------|---------|--------------|
| `root.specs.naming.yaml` | Naming conventions | naming_rules, value_formats, forbidden_patterns |
| `root.specs.references.yaml` | Reference formats | reference_formats, validation_rules, resolution_strategy |
| `root.specs.mapping.yaml` | Mapping rules | mapping_types, mapping_rules, integrity_checks |
| `root.specs.logic.yaml` | Logical consistency | logic_categories, compound_rules, validation_algorithms |
| `root.specs.context.yaml` | Context consistency | context_keys, consistency_rules, drift_detection |

### Registry File Reference

| File | Purpose | Key Sections |
|------|---------|--------------|
| `root.registry.modules.yaml` | Module SSOT | modules, dependency_graph, validation |
| `root.registry.urns.yaml` | URN SSOT | module_urns, config_urns, policy_urns, resolution_rules |

### Validation Tools Reference

| Tool | Purpose | Output |
|------|---------|--------|
| `validate-root-specs.py` | Python validator | `root-specs-validation-report.md` |
| `gate-root-specs.yml` | GitHub Actions gate | PR status check + comment |

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-12-21  
**Maintained By:** MachineNativeOps Governance Team
