# =============================================================================
# SynergyMesh Governance - Decision Governance Policy Tests
# Dimension: 02-decision
# =============================================================================

package governance.decision_test

import data.governance.decision

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    decision.allow with input as {
        "id": "02-decision-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not decision.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not decision.allow with input as {
        "id": "02-decision-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    decision.compliant with input as {
        "id": "02-decision-test-001",
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
    violations := decision.violations with input as {
        "id": "02-decision-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := decision.violations with input as {
        "id": "02-decision-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    decision.metadata.dimension_id == "02-decision"
}

test_metadata_version {
    decision.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := decision.audit_entry with input as {
        "id": "02-decision-test-001",
        "status": "active"
    }
    entry.dimension == "02-decision"
}
