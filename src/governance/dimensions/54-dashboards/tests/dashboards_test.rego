# =============================================================================
# SynergyMesh Governance - Dashboards Governance Policy Tests
# Dimension: 54-dashboards
# =============================================================================

package governance.dashboards_test

import data.governance.dashboards

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    dashboards.allow with input as {
        "id": "54-dashboards-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not dashboards.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not dashboards.allow with input as {
        "id": "54-dashboards-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    dashboards.compliant with input as {
        "id": "54-dashboards-test-001",
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
    violations := dashboards.violations with input as {
        "id": "54-dashboards-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := dashboards.violations with input as {
        "id": "54-dashboards-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    dashboards.metadata.dimension_id == "54-dashboards"
}

test_metadata_version {
    dashboards.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := dashboards.audit_entry with input as {
        "id": "54-dashboards-test-001",
        "status": "active"
    }
    entry.dimension == "54-dashboards"
}
