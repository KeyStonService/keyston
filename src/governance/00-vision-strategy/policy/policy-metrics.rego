# OPA Policy for MetricsDashboard Validation
# Auto-generated from: success-metrics-dashboard.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.metrics

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "success-metrics-dashboard-policy",
  "version": "v1.0.0",
  "description": "Validates MetricsDashboard resources against governance rules",
  "strategic_doc": "success-metrics-dashboard.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "MetricsDashboard"
  not input.spec
  msg := "MetricsDashboard must define spec"
}

deny[msg] {
  input.kind == "MetricsDashboard"
  not input.spec.version
  msg := "MetricsDashboard must define spec.version"
}

deny[msg] {
  input.kind == "MetricsDashboard"
  not input.spec.status
  msg := "MetricsDashboard must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "MetricsDashboard"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "MetricsDashboard must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "MetricsDashboard"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "MetricsDashboard must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "MetricsDashboard"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "MetricsDashboard"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "MetricsDashboard"
  not input.spec.source
  msg := "Warning: MetricsDashboard should reference source strategic document"
}
