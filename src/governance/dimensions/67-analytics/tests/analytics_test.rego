# =============================================================================
# SynergyMesh Governance - Analytics Governance Policy Tests
# Dimension: 67-analytics
# =============================================================================

package governance.analytics_test

import data.governance.analytics

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    analytics.allow with input as {
        "id": "67-analytics-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not analytics.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not analytics.allow with input as {
        "id": "67-analytics-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    analytics.compliant with input as {
        "id": "67-analytics-test-001",
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
    violations := analytics.violations with input as {
        "id": "67-analytics-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := analytics.violations with input as {
        "id": "67-analytics-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    analytics.metadata.dimension_id == "67-analytics"
}

test_metadata_version {
    analytics.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := analytics.audit_entry with input as {
        "id": "67-analytics-test-001",
        "status": "active"
    }
    entry.dimension == "67-analytics"
}
