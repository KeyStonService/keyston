# =============================================================================
# SynergyMesh Governance - Schemas Governance Policy Tests
# Dimension: 31-schemas
# =============================================================================

package governance.schemas_test

import data.governance.schemas

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    schemas.allow with input as {
        "id": "31-schemas-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not schemas.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not schemas.allow with input as {
        "id": "31-schemas-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    schemas.compliant with input as {
        "id": "31-schemas-test-001",
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
    violations := schemas.violations with input as {
        "id": "31-schemas-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := schemas.violations with input as {
        "id": "31-schemas-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    schemas.metadata.dimension_id == "31-schemas"
}

test_metadata_version {
    schemas.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := schemas.audit_entry with input as {
        "id": "31-schemas-test-001",
        "status": "active"
    }
    entry.dimension == "31-schemas"
}
