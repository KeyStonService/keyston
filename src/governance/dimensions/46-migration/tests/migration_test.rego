# =============================================================================
# SynergyMesh Governance - Migration Governance Policy Tests
# Dimension: 46-migration
# =============================================================================

package governance.migration_test

import data.governance.migration

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    migration.allow with input as {
        "id": "46-migration-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not migration.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not migration.allow with input as {
        "id": "46-migration-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    migration.compliant with input as {
        "id": "46-migration-test-001",
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
    violations := migration.violations with input as {
        "id": "46-migration-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := migration.violations with input as {
        "id": "46-migration-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    migration.metadata.dimension_id == "46-migration"
}

test_metadata_version {
    migration.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := migration.audit_entry with input as {
        "id": "46-migration-test-001",
        "status": "active"
    }
    entry.dimension == "46-migration"
}
