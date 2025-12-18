# =============================================================================
# SynergyMesh Governance - Monitoring Governance Policy Tests
# Dimension: 50-monitoring
# =============================================================================

package governance.monitoring_test

import data.governance.monitoring

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    monitoring.allow with input as {
        "id": "50-monitoring-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not monitoring.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not monitoring.allow with input as {
        "id": "50-monitoring-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    monitoring.compliant with input as {
        "id": "50-monitoring-test-001",
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
    violations := monitoring.violations with input as {
        "id": "50-monitoring-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := monitoring.violations with input as {
        "id": "50-monitoring-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    monitoring.metadata.dimension_id == "50-monitoring"
}

test_metadata_version {
    monitoring.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := monitoring.audit_entry with input as {
        "id": "50-monitoring-test-001",
        "status": "active"
    }
    entry.dimension == "50-monitoring"
}
