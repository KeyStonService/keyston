# =============================================================================
# SynergyMesh Governance - Incidents Governance Policy Tests
# Dimension: 56-incidents
# =============================================================================

package governance.incidents_test

import data.governance.incidents

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    incidents.allow with input as {
        "id": "56-incidents-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not incidents.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not incidents.allow with input as {
        "id": "56-incidents-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    incidents.compliant with input as {
        "id": "56-incidents-test-001",
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
    violations := incidents.violations with input as {
        "id": "56-incidents-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := incidents.violations with input as {
        "id": "56-incidents-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    incidents.metadata.dimension_id == "56-incidents"
}

test_metadata_version {
    incidents.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := incidents.audit_entry with input as {
        "id": "56-incidents-test-001",
        "status": "active"
    }
    entry.dimension == "56-incidents"
}
