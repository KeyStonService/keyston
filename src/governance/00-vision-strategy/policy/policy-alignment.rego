# OPA Policy for AlignmentFramework Validation
# Auto-generated from: alignment-framework.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.alignment

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "alignment-framework-policy",
  "version": "v1.0.0",
  "description": "Validates AlignmentFramework resources against governance rules",
  "strategic_doc": "alignment-framework.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "AlignmentFramework"
  not input.spec
  msg := "AlignmentFramework must define spec"
}

deny[msg] {
  input.kind == "AlignmentFramework"
  not input.spec.version
  msg := "AlignmentFramework must define spec.version"
}

deny[msg] {
  input.kind == "AlignmentFramework"
  not input.spec.status
  msg := "AlignmentFramework must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "AlignmentFramework"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "AlignmentFramework must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "AlignmentFramework"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "AlignmentFramework must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "AlignmentFramework"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "AlignmentFramework"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "AlignmentFramework"
  not input.spec.source
  msg := "Warning: AlignmentFramework should reference source strategic document"
}
