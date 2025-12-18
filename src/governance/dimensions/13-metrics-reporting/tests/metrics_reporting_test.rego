# =============================================================================
# SynergyMesh Governance - Metrics Reporting Governance Policy Tests
# Dimension: 13-metrics-reporting
# =============================================================================

package governance.metrics_reporting_test

import data.governance.metrics_reporting

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    metrics_reporting.allow with input as {
        "id": "13-metrics-reporting-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not metrics_reporting.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not metrics_reporting.allow with input as {
        "id": "13-metrics-reporting-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    metrics_reporting.compliant with input as {
        "id": "13-metrics-reporting-test-001",
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
    violations := metrics_reporting.violations with input as {
        "id": "13-metrics-reporting-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := metrics_reporting.violations with input as {
        "id": "13-metrics-reporting-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    metrics_reporting.metadata.dimension_id == "13-metrics-reporting"
}

test_metadata_version {
    metrics_reporting.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := metrics_reporting.audit_entry with input as {
        "id": "13-metrics-reporting-test-001",
        "status": "active"
    }
    entry.dimension == "13-metrics-reporting"
}
