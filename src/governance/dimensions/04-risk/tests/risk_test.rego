# =============================================================================
# SynergyMesh Governance - Risk Governance Policy Tests
# Dimension: 04-risk
# =============================================================================

package governance.risk_test

import data.governance.risk

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    risk.allow with input as {
        "id": "04-risk-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not risk.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not risk.allow with input as {
        "id": "04-risk-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    risk.compliant with input as {
        "id": "04-risk-test-001",
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
    violations := risk.violations with input as {
        "id": "04-risk-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := risk.violations with input as {
        "id": "04-risk-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    risk.metadata.dimension_id == "04-risk"
}

test_metadata_version {
    risk.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := risk.audit_entry with input as {
        "id": "04-risk-test-001",
        "status": "active"
    }
    entry.dimension == "04-risk"
}
