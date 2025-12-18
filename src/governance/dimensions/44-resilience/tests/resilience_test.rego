# =============================================================================
# SynergyMesh Governance - Resilience Governance Policy Tests
# Dimension: 44-resilience
# =============================================================================

package governance.resilience_test

import data.governance.resilience

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    resilience.allow with input as {
        "id": "44-resilience-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not resilience.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not resilience.allow with input as {
        "id": "44-resilience-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    resilience.compliant with input as {
        "id": "44-resilience-test-001",
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
    violations := resilience.violations with input as {
        "id": "44-resilience-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := resilience.violations with input as {
        "id": "44-resilience-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    resilience.metadata.dimension_id == "44-resilience"
}

test_metadata_version {
    resilience.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := resilience.audit_entry with input as {
        "id": "44-resilience-test-001",
        "status": "active"
    }
    entry.dimension == "44-resilience"
}
