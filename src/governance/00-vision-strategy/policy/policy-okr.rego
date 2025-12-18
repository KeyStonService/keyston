# OPA Policy for StrategicObjective Validation
# Auto-generated from: strategic-objectives.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.okr

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "strategic-objectives-policy",
  "version": "v1.0.0",
  "description": "Validates StrategicObjective resources against governance rules",
  "strategic_doc": "strategic-objectives.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "StrategicObjective"
  not input.spec
  msg := "StrategicObjective must define spec"
}

deny[msg] {
  input.kind == "StrategicObjective"
  not input.spec.version
  msg := "StrategicObjective must define spec.version"
}

deny[msg] {
  input.kind == "StrategicObjective"
  not input.spec.status
  msg := "StrategicObjective must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "StrategicObjective"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "StrategicObjective must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "StrategicObjective"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "StrategicObjective must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "StrategicObjective"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "StrategicObjective"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "StrategicObjective"
  not input.spec.source
  msg := "Warning: StrategicObjective should reference source strategic document"
}
