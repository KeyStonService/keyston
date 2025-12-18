# =============================================================================
# SynergyMesh Governance - Optimization Governance Policy Tests
# Dimension: 72-optimization
# =============================================================================

package governance.optimization_test

import data.governance.optimization

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    optimization.allow with input as {
        "id": "72-optimization-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not optimization.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not optimization.allow with input as {
        "id": "72-optimization-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    optimization.compliant with input as {
        "id": "72-optimization-test-001",
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
    violations := optimization.violations with input as {
        "id": "72-optimization-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := optimization.violations with input as {
        "id": "72-optimization-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    optimization.metadata.dimension_id == "72-optimization"
}

test_metadata_version {
    optimization.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := optimization.audit_entry with input as {
        "id": "72-optimization-test-001",
        "status": "active"
    }
    entry.dimension == "72-optimization"
}
