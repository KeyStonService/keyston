# =============================================================================
# SynergyMesh Governance - Change Governance Policy Tests
# Dimension: 03-change
# =============================================================================

package governance.change_test

import data.governance.change

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    change.allow with input as {
        "id": "03-change-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not change.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not change.allow with input as {
        "id": "03-change-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    change.compliant with input as {
        "id": "03-change-test-001",
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
    violations := change.violations with input as {
        "id": "03-change-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := change.violations with input as {
        "id": "03-change-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    change.metadata.dimension_id == "03-change"
}

test_metadata_version {
    change.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := change.audit_entry with input as {
        "id": "03-change-test-001",
        "status": "active"
    }
    entry.dimension == "03-change"
}
