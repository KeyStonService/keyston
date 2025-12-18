# =============================================================================
# SynergyMesh Governance - Policy Governance Policy Tests
# Dimension: 10-policy
# =============================================================================

package governance.policy_test

import data.governance.policy

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    policy.allow with input as {
        "id": "10-policy-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not policy.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not policy.allow with input as {
        "id": "10-policy-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    policy.compliant with input as {
        "id": "10-policy-test-001",
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
    violations := policy.violations with input as {
        "id": "10-policy-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := policy.violations with input as {
        "id": "10-policy-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    policy.metadata.dimension_id == "10-policy"
}

test_metadata_version {
    policy.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := policy.audit_entry with input as {
        "id": "10-policy-test-001",
        "status": "active"
    }
    entry.dimension == "10-policy"
}
