# =============================================================================
# SynergyMesh Governance - Tools Systems Governance Policy
# Dimension: 11-tools-systems
# =============================================================================
# Policy Engine: OPA (Open Policy Agent)
# Language: Rego
# =============================================================================

package governance.tools_systems

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# =============================================================================
# DEFAULT DENY
# =============================================================================
default allow := false
default compliant := false

# =============================================================================
# METADATA
# =============================================================================
metadata := {
    "dimension_id": "11-tools-systems",
    "dimension_name": "Tools Systems Governance",
    "version": "1.0.0",
    "tags": ["tools", "systems", "platform", "integration"]
}

# =============================================================================
# ALLOW RULES
# =============================================================================

# Allow if all validation rules pass
allow if {
    valid_input
    valid_config
    no_policy_violations
}

# =============================================================================
# COMPLIANCE RULES
# =============================================================================

# Resource is compliant if all compliance checks pass
compliant if {
    allow
    audit_trail_exists
    dependencies_satisfied
}

# =============================================================================
# VALIDATION RULES
# =============================================================================

# Input validation
valid_input if {
    input.id
    input.status
}

# Configuration validation
valid_config if {
    input.config.enabled != null
}

# Default for missing config
valid_config if {
    not input.config
}

# =============================================================================
# POLICY VIOLATION CHECKS
# =============================================================================

# No violations if violations set is empty
no_policy_violations if {
    count(violations) == 0
}

# Collect all violations
violations contains msg if {
    not input.id
    msg := "Resource ID is required"
}

violations contains msg if {
    not input.status
    msg := "Resource status is required"
}

violations contains msg if {
    input.status == "error"
    not input.error_details
    msg := "Error status requires error_details"
}

# =============================================================================
# AUDIT RULES
# =============================================================================

# Audit trail exists (always true for new resources)
audit_trail_exists if {
    input.metadata.created_at
}

# Default audit trail for resources without metadata
audit_trail_exists if {
    not input.metadata
}

# =============================================================================
# DEPENDENCY RULES
# =============================================================================

# Dependencies are satisfied if all required deps are available
dependencies_satisfied if {
    # Placeholder: check dependencies in context
    true
}

# =============================================================================
# ENFORCEMENT ACTIONS
# =============================================================================

# Deny response with reasons
deny[reason] if {
    violation := violations[_]
    reason := {
        "code": "E11001",
        "dimension": "11-tools-systems",
        "message": violation
    }
}

# =============================================================================
# AUDIT LOG GENERATION
# =============================================================================

audit_entry := {
    "dimension": "11-tools-systems",
    "timestamp": time.now_ns(),
    "input_id": input.id,
    "decision": {
        "allow": allow,
        "compliant": compliant,
        "violations": violations
    }
}

# =============================================================================
# METRICS
# =============================================================================

metrics := {
    "policy_evaluations": 1,
    "violations_count": count(violations),
    "compliant": compliant
}
