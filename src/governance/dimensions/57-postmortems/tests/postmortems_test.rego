# =============================================================================
# SynergyMesh Governance - Postmortems Governance Policy Tests
# Dimension: 57-postmortems
# =============================================================================

package governance.postmortems_test

import data.governance.postmortems

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    postmortems.allow with input as {
        "id": "57-postmortems-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not postmortems.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not postmortems.allow with input as {
        "id": "57-postmortems-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    postmortems.compliant with input as {
        "id": "57-postmortems-test-001",
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
    violations := postmortems.violations with input as {
        "id": "57-postmortems-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := postmortems.violations with input as {
        "id": "57-postmortems-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    postmortems.metadata.dimension_id == "57-postmortems"
}

test_metadata_version {
    postmortems.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := postmortems.audit_entry with input as {
        "id": "57-postmortems-test-001",
        "status": "active"
    }
    entry.dimension == "57-postmortems"
}
