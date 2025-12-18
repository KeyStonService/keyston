# =============================================================================
# SynergyMesh Governance - Behavior Contracts Governance Policy Tests
# Dimension: 37-behavior-contracts
# =============================================================================

package governance.behavior_contracts_test

import data.governance.behavior_contracts

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    behavior_contracts.allow with input as {
        "id": "37-behavior-contracts-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not behavior_contracts.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not behavior_contracts.allow with input as {
        "id": "37-behavior-contracts-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    behavior_contracts.compliant with input as {
        "id": "37-behavior-contracts-test-001",
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
    violations := behavior_contracts.violations with input as {
        "id": "37-behavior-contracts-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := behavior_contracts.violations with input as {
        "id": "37-behavior-contracts-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    behavior_contracts.metadata.dimension_id == "37-behavior-contracts"
}

test_metadata_version {
    behavior_contracts.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := behavior_contracts.audit_entry with input as {
        "id": "37-behavior-contracts-test-001",
        "status": "active"
    }
    entry.dimension == "37-behavior-contracts"
}
