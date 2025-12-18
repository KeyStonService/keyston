# =============================================================================
# SynergyMesh Governance - Reporting Governance Policy Tests
# Dimension: 66-reporting
# =============================================================================

package governance.reporting_test

import data.governance.reporting

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    reporting.allow with input as {
        "id": "66-reporting-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not reporting.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not reporting.allow with input as {
        "id": "66-reporting-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    reporting.compliant with input as {
        "id": "66-reporting-test-001",
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
    violations := reporting.violations with input as {
        "id": "66-reporting-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := reporting.violations with input as {
        "id": "66-reporting-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    reporting.metadata.dimension_id == "66-reporting"
}

test_metadata_version {
    reporting.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := reporting.audit_entry with input as {
        "id": "66-reporting-test-001",
        "status": "active"
    }
    entry.dimension == "66-reporting"
}
