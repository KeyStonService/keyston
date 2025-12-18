# OPA Policy for ChangeProtocol Validation
# Auto-generated from: change-management-protocol.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.change

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "change-management-protocol-policy",
  "version": "v1.0.0",
  "description": "Validates ChangeProtocol resources against governance rules",
  "strategic_doc": "change-management-protocol.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "ChangeProtocol"
  not input.spec
  msg := "ChangeProtocol must define spec"
}

deny[msg] {
  input.kind == "ChangeProtocol"
  not input.spec.version
  msg := "ChangeProtocol must define spec.version"
}

deny[msg] {
  input.kind == "ChangeProtocol"
  not input.spec.status
  msg := "ChangeProtocol must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "ChangeProtocol"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "ChangeProtocol must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "ChangeProtocol"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "ChangeProtocol must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "ChangeProtocol"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "ChangeProtocol"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "ChangeProtocol"
  not input.spec.source
  msg := "Warning: ChangeProtocol should reference source strategic document"
}
