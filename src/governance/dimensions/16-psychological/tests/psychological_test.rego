# =============================================================================
# SynergyMesh Governance - Psychological Governance Policy Tests
# Dimension: 16-psychological
# =============================================================================

package governance.psychological_test

import data.governance.psychological

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    psychological.allow with input as {
        "id": "16-psychological-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not psychological.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not psychological.allow with input as {
        "id": "16-psychological-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    psychological.compliant with input as {
        "id": "16-psychological-test-001",
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
    violations := psychological.violations with input as {
        "id": "16-psychological-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := psychological.violations with input as {
        "id": "16-psychological-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    psychological.metadata.dimension_id == "16-psychological"
}

test_metadata_version {
    psychological.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := psychological.audit_entry with input as {
        "id": "16-psychological-test-001",
        "status": "active"
    }
    entry.dimension == "16-psychological"
}
