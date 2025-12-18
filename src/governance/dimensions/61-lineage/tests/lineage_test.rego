# =============================================================================
# SynergyMesh Governance - Lineage Governance Policy Tests
# Dimension: 61-lineage
# =============================================================================

package governance.lineage_test

import data.governance.lineage

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    lineage.allow with input as {
        "id": "61-lineage-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not lineage.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not lineage.allow with input as {
        "id": "61-lineage-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    lineage.compliant with input as {
        "id": "61-lineage-test-001",
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
    violations := lineage.violations with input as {
        "id": "61-lineage-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := lineage.violations with input as {
        "id": "61-lineage-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    lineage.metadata.dimension_id == "61-lineage"
}

test_metadata_version {
    lineage.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := lineage.audit_entry with input as {
        "id": "61-lineage-test-001",
        "status": "active"
    }
    entry.dimension == "61-lineage"
}
