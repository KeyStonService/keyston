# OPA Policy for ImplementationRoadmap Validation
# Auto-generated from: implementation-roadmap.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.roadmap

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "implementation-roadmap-policy",
  "version": "v1.0.0",
  "description": "Validates ImplementationRoadmap resources against governance rules",
  "strategic_doc": "implementation-roadmap.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "ImplementationRoadmap"
  not input.spec
  msg := "ImplementationRoadmap must define spec"
}

deny[msg] {
  input.kind == "ImplementationRoadmap"
  not input.spec.version
  msg := "ImplementationRoadmap must define spec.version"
}

deny[msg] {
  input.kind == "ImplementationRoadmap"
  not input.spec.status
  msg := "ImplementationRoadmap must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "ImplementationRoadmap"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "ImplementationRoadmap must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "ImplementationRoadmap"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "ImplementationRoadmap must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "ImplementationRoadmap"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "ImplementationRoadmap"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "ImplementationRoadmap"
  not input.spec.source
  msg := "Warning: ImplementationRoadmap should reference source strategic document"
}
