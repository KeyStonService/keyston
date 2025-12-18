# =============================================================================
# SynergyMesh Governance - Alerting Governance Policy Tests
# Dimension: 53-alerting
# =============================================================================

package governance.alerting_test

import data.governance.alerting

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    alerting.allow with input as {
        "id": "53-alerting-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not alerting.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not alerting.allow with input as {
        "id": "53-alerting-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    alerting.compliant with input as {
        "id": "53-alerting-test-001",
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
    violations := alerting.violations with input as {
        "id": "53-alerting-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := alerting.violations with input as {
        "id": "53-alerting-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    alerting.metadata.dimension_id == "53-alerting"
}

test_metadata_version {
    alerting.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := alerting.audit_entry with input as {
        "id": "53-alerting-test-001",
        "status": "active"
    }
    entry.dimension == "53-alerting"
}
