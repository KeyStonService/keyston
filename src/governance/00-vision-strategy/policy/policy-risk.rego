# OPA Policy for RiskRegister Validation
# Auto-generated from: risk-register.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.risk

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "risk-register-policy",
  "version": "v1.0.0",
  "description": "Validates RiskRegister resources against governance rules",
  "strategic_doc": "risk-register.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "RiskRegister"
  not input.spec
  msg := "RiskRegister must define spec"
}

deny[msg] {
  input.kind == "RiskRegister"
  not input.spec.version
  msg := "RiskRegister must define spec.version"
}

deny[msg] {
  input.kind == "RiskRegister"
  not input.spec.status
  msg := "RiskRegister must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "RiskRegister"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "RiskRegister must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "RiskRegister"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "RiskRegister must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "RiskRegister"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "RiskRegister"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "RiskRegister"
  not input.spec.source
  msg := "Warning: RiskRegister should reference source strategic document"
}
