# =============================================================================
# SynergyMesh Governance - Feedback Loops Governance Policy Tests
# Dimension: 71-feedback-loops
# =============================================================================

package governance.feedback_loops_test

import data.governance.feedback_loops

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    feedback_loops.allow with input as {
        "id": "71-feedback-loops-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not feedback_loops.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not feedback_loops.allow with input as {
        "id": "71-feedback-loops-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    feedback_loops.compliant with input as {
        "id": "71-feedback-loops-test-001",
        "status": "active",
        "config": {
            "enabled": true
        },
        "metadata": {
            "created_at": "2025-12-11T00:00:00Z"
        }
    }
}

# =============================================================================
# TEST: VIOLATION RULES
# =============================================================================

test_violations_empty_for_valid {
    violations := feedback_loops.violations with input as {
        "id": "71-feedback-loops-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := feedback_loops.violations with input as {
        "id": "71-feedback-loops-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    feedback_loops.metadata.dimension_id == "71-feedback-loops"
}

test_metadata_version {
    feedback_loops.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := feedback_loops.audit_entry with input as {
        "id": "71-feedback-loops-test-001",
        "status": "active"
    }
    entry.dimension == "71-feedback-loops"
}
