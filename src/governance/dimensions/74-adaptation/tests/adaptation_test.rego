# =============================================================================
# SynergyMesh Governance - Adaptation Governance Policy Tests
# Dimension: 74-adaptation
# =============================================================================

package governance.adaptation_test

import data.governance.adaptation

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    adaptation.allow with input as {
        "id": "74-adaptation-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not adaptation.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not adaptation.allow with input as {
        "id": "74-adaptation-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    adaptation.compliant with input as {
        "id": "74-adaptation-test-001",
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
    violations := adaptation.violations with input as {
        "id": "74-adaptation-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := adaptation.violations with input as {
        "id": "74-adaptation-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    adaptation.metadata.dimension_id == "74-adaptation"
}

test_metadata_version {
    adaptation.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := adaptation.audit_entry with input as {
        "id": "74-adaptation-test-001",
        "status": "active"
    }
    entry.dimension == "74-adaptation"
}
