# OPA Policy for VisionStatement Validation
# Auto-generated from: vision-statement.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.vision

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "vision-statement-policy",
  "version": "v1.0.0",
  "description": "Validates VisionStatement resources against governance rules",
  "strategic_doc": "vision-statement.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "VisionStatement"
  not input.spec.vision
  msg := "VisionStatement must define spec.vision"
}

deny[msg] {
  input.kind == "VisionStatement"
  not input.spec.mission
  msg := "VisionStatement must define spec.mission"
}

deny[msg] {
  input.kind == "VisionStatement"
  not input.spec.vision.title
  msg := "Vision must include a title"
}

deny[msg] {
  input.kind == "VisionStatement"
  not input.spec.vision.statement
  msg := "Vision must include a statement"
}

# ============================================================================
# Mission Validation
# ============================================================================
deny[msg] {
  input.kind == "VisionStatement"
  not input.spec.mission.statement
  msg := "Mission must include a statement"
}

# ============================================================================
# Core Values Validation
# ============================================================================
deny[msg] {
  input.kind == "VisionStatement"
  count(input.spec.core_values) < 3
  msg := sprintf("Insufficient core values: found %d, require at least 3", [count(input.spec.core_values)])
}

deny[msg] {
  input.kind == "VisionStatement"
  some i
  value := input.spec.core_values[i]
  not value.value
  msg := sprintf("Core value at index %d missing 'value' field", [i])
}

# ============================================================================
# Key Outcomes Validation
# ============================================================================
deny[msg] {
  input.kind == "VisionStatement"
  count(input.spec.vision.key_outcomes) < 3
  msg := sprintf("Insufficient key outcomes: found %d, require at least 3", [count(input.spec.vision.key_outcomes)])
}

deny[msg] {
  input.kind == "VisionStatement"
  some i
  outcome := input.spec.vision.key_outcomes[i]
  not outcome.metrics
  msg := sprintf("Key outcome '%s' must define metrics", [outcome.outcome])
}

deny[msg] {
  input.kind == "VisionStatement"
  some i
  outcome := input.spec.vision.key_outcomes[i]
  count(outcome.metrics) == 0
  msg := sprintf("Key outcome '%s' must have at least one metric", [outcome.outcome])
}

# ============================================================================
# Strategic Themes Validation
# ============================================================================
deny[msg] {
  input.kind == "VisionStatement"
  count(input.spec.strategic_themes) < 2
  msg := sprintf("Insufficient strategic themes: found %d, require at least 2", [count(input.spec.strategic_themes)])
}

deny[msg] {
  input.kind == "VisionStatement"
  some i
  theme := input.spec.strategic_themes[i]
  not theme.theme
  msg := sprintf("Strategic theme at index %d missing 'theme' field", [i])
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "VisionStatement"
  not input.spec.status
  msg := "VisionStatement must define spec.status"
}

deny[msg] {
  input.kind == "VisionStatement"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "VisionStatement"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "VisionStatement must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "VisionStatement"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "VisionStatement must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "VisionStatement"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "VisionStatement"
  not input.spec.vision.horizon
  msg := "Warning: Vision should define a time horizon"
}

warn[msg] {
  input.kind == "VisionStatement"
  not input.spec.vision.title_en
  msg := "Warning: Consider adding English translation for vision title"
}

warn[msg] {
  input.kind == "VisionStatement"
  not input.spec.mission.statement_en
  msg := "Warning: Consider adding English translation for mission statement"
}
