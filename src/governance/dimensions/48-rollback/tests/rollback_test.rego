# =============================================================================
# SynergyMesh Governance - Rollback Governance Policy Tests
# Dimension: 48-rollback
# =============================================================================

package governance.rollback_test

import data.governance.rollback

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    rollback.allow with input as {
        "id": "48-rollback-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not rollback.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not rollback.allow with input as {
        "id": "48-rollback-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    rollback.compliant with input as {
        "id": "48-rollback-test-001",
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
    violations := rollback.violations with input as {
        "id": "48-rollback-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := rollback.violations with input as {
        "id": "48-rollback-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    rollback.metadata.dimension_id == "48-rollback"
}

test_metadata_version {
    rollback.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := rollback.audit_entry with input as {
        "id": "48-rollback-test-001",
        "status": "active"
    }
    entry.dimension == "48-rollback"
}
