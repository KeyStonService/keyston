# OPA Policy for GovernanceCharter Validation
# Auto-generated from: governance-charter.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.governance

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "governance-charter-policy",
  "version": "v1.0.0",
  "description": "Validates GovernanceCharter resources against governance rules",
  "strategic_doc": "governance-charter.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "GovernanceCharter"
  not input.spec
  msg := "GovernanceCharter must define spec"
}

deny[msg] {
  input.kind == "GovernanceCharter"
  not input.spec.version
  msg := "GovernanceCharter must define spec.version"
}

deny[msg] {
  input.kind == "GovernanceCharter"
  not input.spec.status
  msg := "GovernanceCharter must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "GovernanceCharter"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "GovernanceCharter must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "GovernanceCharter"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "GovernanceCharter must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "GovernanceCharter"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "GovernanceCharter"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "GovernanceCharter"
  not input.spec.source
  msg := "Warning: GovernanceCharter should reference source strategic document"
}
