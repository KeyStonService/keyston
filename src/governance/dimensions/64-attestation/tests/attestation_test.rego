# =============================================================================
# SynergyMesh Governance - Attestation Governance Policy Tests
# Dimension: 64-attestation
# =============================================================================

package governance.attestation_test

import data.governance.attestation

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    attestation.allow with input as {
        "id": "64-attestation-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not attestation.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not attestation.allow with input as {
        "id": "64-attestation-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    attestation.compliant with input as {
        "id": "64-attestation-test-001",
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
    violations := attestation.violations with input as {
        "id": "64-attestation-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := attestation.violations with input as {
        "id": "64-attestation-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    attestation.metadata.dimension_id == "64-attestation"
}

test_metadata_version {
    attestation.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := attestation.audit_entry with input as {
        "id": "64-attestation-test-001",
        "status": "active"
    }
    entry.dimension == "64-attestation"
}
