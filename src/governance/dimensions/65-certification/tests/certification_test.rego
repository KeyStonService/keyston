# =============================================================================
# SynergyMesh Governance - Certification Governance Policy Tests
# Dimension: 65-certification
# =============================================================================

package governance.certification_test

import data.governance.certification

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    certification.allow with input as {
        "id": "65-certification-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not certification.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not certification.allow with input as {
        "id": "65-certification-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    certification.compliant with input as {
        "id": "65-certification-test-001",
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
    violations := certification.violations with input as {
        "id": "65-certification-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := certification.violations with input as {
        "id": "65-certification-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    certification.metadata.dimension_id == "65-certification"
}

test_metadata_version {
    certification.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := certification.audit_entry with input as {
        "id": "65-certification-test-001",
        "status": "active"
    }
    entry.dimension == "65-certification"
}
