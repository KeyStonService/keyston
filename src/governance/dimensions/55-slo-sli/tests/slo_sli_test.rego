# =============================================================================
# SynergyMesh Governance - SLO SLI Governance Policy Tests
# Dimension: 55-slo-sli
# =============================================================================

package governance.slo_sli_test

import data.governance.slo_sli

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    slo_sli.allow with input as {
        "id": "55-slo-sli-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not slo_sli.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not slo_sli.allow with input as {
        "id": "55-slo-sli-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    slo_sli.compliant with input as {
        "id": "55-slo-sli-test-001",
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
    violations := slo_sli.violations with input as {
        "id": "55-slo-sli-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := slo_sli.violations with input as {
        "id": "55-slo-sli-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    slo_sli.metadata.dimension_id == "55-slo-sli"
}

test_metadata_version {
    slo_sli.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := slo_sli.audit_entry with input as {
        "id": "55-slo-sli-test-001",
        "status": "active"
    }
    entry.dimension == "55-slo-sli"
}
