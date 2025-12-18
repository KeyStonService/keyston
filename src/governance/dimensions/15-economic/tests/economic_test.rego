# =============================================================================
# SynergyMesh Governance - Economic Governance Policy Tests
# Dimension: 15-economic
# =============================================================================

package governance.economic_test

import data.governance.economic

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    economic.allow with input as {
        "id": "15-economic-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not economic.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not economic.allow with input as {
        "id": "15-economic-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    economic.compliant with input as {
        "id": "15-economic-test-001",
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
    violations := economic.violations with input as {
        "id": "15-economic-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := economic.violations with input as {
        "id": "15-economic-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    economic.metadata.dimension_id == "15-economic"
}

test_metadata_version {
    economic.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := economic.audit_entry with input as {
        "id": "15-economic-test-001",
        "status": "active"
    }
    entry.dimension == "15-economic"
}
