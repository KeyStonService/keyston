# =============================================================================
# SynergyMesh Governance - Policy Definitions Policy Tests
# Dimension: 23-policies
# =============================================================================

package governance.policies_test

import data.governance.policies

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    policies.allow with input as {
        "id": "23-policies-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not policies.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not policies.allow with input as {
        "id": "23-policies-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    policies.compliant with input as {
        "id": "23-policies-test-001",
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
    violations := policies.violations with input as {
        "id": "23-policies-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := policies.violations with input as {
        "id": "23-policies-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    policies.metadata.dimension_id == "23-policies"
}

test_metadata_version {
    policies.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := policies.audit_entry with input as {
        "id": "23-policies-test-001",
        "status": "active"
    }
    entry.dimension == "23-policies"
}
