# =============================================================================
# SynergyMesh Governance - Correlation Governance Policy Tests
# Dimension: 69-correlation
# =============================================================================

package governance.correlation_test

import data.governance.correlation

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    correlation.allow with input as {
        "id": "69-correlation-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not correlation.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not correlation.allow with input as {
        "id": "69-correlation-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    correlation.compliant with input as {
        "id": "69-correlation-test-001",
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
    violations := correlation.violations with input as {
        "id": "69-correlation-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := correlation.violations with input as {
        "id": "69-correlation-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    correlation.metadata.dimension_id == "69-correlation"
}

test_metadata_version {
    correlation.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := correlation.audit_entry with input as {
        "id": "69-correlation-test-001",
        "status": "active"
    }
    entry.dimension == "69-correlation"
}
