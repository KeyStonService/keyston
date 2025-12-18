# =============================================================================
# SynergyMesh Governance - Self-Healing Governance Policy Tests
# Dimension: 40-self-healing
# =============================================================================

package governance.self_healing_test

import data.governance.self_healing

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    self_healing.allow with input as {
        "id": "40-self-healing-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not self_healing.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not self_healing.allow with input as {
        "id": "40-self-healing-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    self_healing.compliant with input as {
        "id": "40-self-healing-test-001",
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
    violations := self_healing.violations with input as {
        "id": "40-self-healing-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := self_healing.violations with input as {
        "id": "40-self-healing-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    self_healing.metadata.dimension_id == "40-self-healing"
}

test_metadata_version {
    self_healing.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := self_healing.audit_entry with input as {
        "id": "40-self-healing-test-001",
        "status": "active"
    }
    entry.dimension == "40-self-healing"
}
