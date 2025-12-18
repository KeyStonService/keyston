# =============================================================================
# SynergyMesh Governance - SBOM Governance Policy Tests
# Dimension: 38-sbom
# =============================================================================

package governance.sbom_test

import data.governance.sbom

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    sbom.allow with input as {
        "id": "38-sbom-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not sbom.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not sbom.allow with input as {
        "id": "38-sbom-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    sbom.compliant with input as {
        "id": "38-sbom-test-001",
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
    violations := sbom.violations with input as {
        "id": "38-sbom-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := sbom.violations with input as {
        "id": "38-sbom-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    sbom.metadata.dimension_id == "38-sbom"
}

test_metadata_version {
    sbom.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := sbom.audit_entry with input as {
        "id": "38-sbom-test-001",
        "status": "active"
    }
    entry.dimension == "38-sbom"
}
