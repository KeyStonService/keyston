# 23-policies - Policies Governance

> **Dimension**: 23  
> **Status**: ACTIVE  
> **Last Updated**: 2025-12-15

## 🎯 Purpose

Central registry for policy definitions and gates used across SynergyMesh. This
dimension keeps policy artifacts versioned, auditable, and ready for enforcement
by OPA/Conftest in CI/CD and runtime workflows.

## 📋 Scope

- Maintain reusable base and domain policies (architecture, security,
  compliance, data)
- Provide policy gates for CI, deployment, and runtime pipelines
- Supply shared Rego/Conftest assets and helper manifests
- Align policy content with governance-map metadata and dimension.yaml

## 📁 Structure

```
23-policies/
├── dimension.yaml            # Dimension metadata
├── base-policies.yaml        # Core policy bundle
├── ci-policy-gate.yaml       # CI gate configuration
├── *.rego                    # OPA policy rules (root)
├── conftest/                 # Conftest policies
├── security/                 # Security-focused policies
└── workflow/                 # Pipeline integration samples
```

## 🚀 Quick Use

- Run policy validation via CI gate: `ci-policy-gate.yaml`
- Integrate OPA rules from root `*.rego` files or Conftest bundles under
  `conftest/`
- Update `dimension.yaml` when adding new policy sets or enforcement targets
