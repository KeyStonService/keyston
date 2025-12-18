# =============================================================================
# SynergyMesh Governance - Evolutionary Governance Policy Tests
# Dimension: 19-evolutionary
# =============================================================================

package governance.evolutionary_test

import data.governance.evolutionary

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    evolutionary.allow with input as {
        "id": "19-evolutionary-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not evolutionary.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not evolutionary.allow with input as {
        "id": "19-evolutionary-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    evolutionary.compliant with input as {
        "id": "19-evolutionary-test-001",
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
    violations := evolutionary.violations with input as {
        "id": "19-evolutionary-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := evolutionary.violations with input as {
        "id": "19-evolutionary-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    evolutionary.metadata.dimension_id == "19-evolutionary"
}

test_metadata_version {
    evolutionary.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := evolutionary.audit_entry with input as {
        "id": "19-evolutionary-test-001",
        "status": "active"
    }
    entry.dimension == "19-evolutionary"
}
