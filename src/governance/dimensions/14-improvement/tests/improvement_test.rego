# =============================================================================
# SynergyMesh Governance - Improvement Governance Policy Tests
# Dimension: 14-improvement
# =============================================================================

package governance.improvement_test

import data.governance.improvement

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    improvement.allow with input as {
        "id": "14-improvement-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not improvement.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not improvement.allow with input as {
        "id": "14-improvement-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    improvement.compliant with input as {
        "id": "14-improvement-test-001",
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
    violations := improvement.violations with input as {
        "id": "14-improvement-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := improvement.violations with input as {
        "id": "14-improvement-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    improvement.metadata.dimension_id == "14-improvement"
}

test_metadata_version {
    improvement.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := improvement.audit_entry with input as {
        "id": "14-improvement-test-001",
        "status": "active"
    }
    entry.dimension == "14-improvement"
}
