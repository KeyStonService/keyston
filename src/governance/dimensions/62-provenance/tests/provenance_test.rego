# =============================================================================
# SynergyMesh Governance - Provenance Governance Policy Tests
# Dimension: 62-provenance
# =============================================================================

package governance.provenance_test

import data.governance.provenance

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    provenance.allow with input as {
        "id": "62-provenance-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not provenance.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not provenance.allow with input as {
        "id": "62-provenance-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    provenance.compliant with input as {
        "id": "62-provenance-test-001",
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
    violations := provenance.violations with input as {
        "id": "62-provenance-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := provenance.violations with input as {
        "id": "62-provenance-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    provenance.metadata.dimension_id == "62-provenance"
}

test_metadata_version {
    provenance.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := provenance.audit_entry with input as {
        "id": "62-provenance-test-001",
        "status": "active"
    }
    entry.dimension == "62-provenance"
}
