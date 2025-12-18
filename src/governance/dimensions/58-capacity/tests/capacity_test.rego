# =============================================================================
# SynergyMesh Governance - Capacity Governance Policy Tests
# Dimension: 58-capacity
# =============================================================================

package governance.capacity_test

import data.governance.capacity

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    capacity.allow with input as {
        "id": "58-capacity-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not capacity.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not capacity.allow with input as {
        "id": "58-capacity-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    capacity.compliant with input as {
        "id": "58-capacity-test-001",
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
    violations := capacity.violations with input as {
        "id": "58-capacity-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := capacity.violations with input as {
        "id": "58-capacity-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    capacity.metadata.dimension_id == "58-capacity"
}

test_metadata_version {
    capacity.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := capacity.audit_entry with input as {
        "id": "58-capacity-test-001",
        "status": "active"
    }
    entry.dimension == "58-capacity"
}
