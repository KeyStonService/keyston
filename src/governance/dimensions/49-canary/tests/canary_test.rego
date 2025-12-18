# =============================================================================
# SynergyMesh Governance - Canary Governance Policy Tests
# Dimension: 49-canary
# =============================================================================

package governance.canary_test

import data.governance.canary

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    canary.allow with input as {
        "id": "49-canary-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not canary.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not canary.allow with input as {
        "id": "49-canary-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    canary.compliant with input as {
        "id": "49-canary-test-001",
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
    violations := canary.violations with input as {
        "id": "49-canary-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := canary.violations with input as {
        "id": "49-canary-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    canary.metadata.dimension_id == "49-canary"
}

test_metadata_version {
    canary.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := canary.audit_entry with input as {
        "id": "49-canary-test-001",
        "status": "active"
    }
    entry.dimension == "49-canary"
}
