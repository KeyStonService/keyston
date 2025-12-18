# =============================================================================
# SynergyMesh Governance - Scaling Governance Policy Tests
# Dimension: 43-scaling
# =============================================================================

package governance.scaling_test

import data.governance.scaling

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    scaling.allow with input as {
        "id": "43-scaling-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not scaling.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not scaling.allow with input as {
        "id": "43-scaling-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    scaling.compliant with input as {
        "id": "43-scaling-test-001",
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
    violations := scaling.violations with input as {
        "id": "43-scaling-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := scaling.violations with input as {
        "id": "43-scaling-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    scaling.metadata.dimension_id == "43-scaling"
}

test_metadata_version {
    scaling.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := scaling.audit_entry with input as {
        "id": "43-scaling-test-001",
        "status": "active"
    }
    entry.dimension == "43-scaling"
}
