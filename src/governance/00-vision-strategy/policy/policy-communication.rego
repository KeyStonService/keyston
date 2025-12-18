# OPA Policy for CommunicationPlan Validation
# Auto-generated from: communication-plan.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.communication

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "communication-plan-policy",
  "version": "v1.0.0",
  "description": "Validates CommunicationPlan resources against governance rules",
  "strategic_doc": "communication-plan.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "CommunicationPlan"
  not input.spec
  msg := "CommunicationPlan must define spec"
}

deny[msg] {
  input.kind == "CommunicationPlan"
  not input.spec.version
  msg := "CommunicationPlan must define spec.version"
}

deny[msg] {
  input.kind == "CommunicationPlan"
  not input.spec.status
  msg := "CommunicationPlan must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "CommunicationPlan"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "CommunicationPlan must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "CommunicationPlan"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "CommunicationPlan must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "CommunicationPlan"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "CommunicationPlan"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "CommunicationPlan"
  not input.spec.source
  msg := "Warning: CommunicationPlan should reference source strategic document"
}
