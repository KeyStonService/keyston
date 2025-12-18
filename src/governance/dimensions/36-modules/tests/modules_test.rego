# =============================================================================
# SynergyMesh Governance - Modules Governance Policy Tests
# Dimension: 36-modules
# =============================================================================

package governance.modules_test

import data.governance.modules

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    modules.allow with input as {
        "id": "36-modules-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not modules.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not modules.allow with input as {
        "id": "36-modules-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    modules.compliant with input as {
        "id": "36-modules-test-001",
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
    violations := modules.violations with input as {
        "id": "36-modules-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := modules.violations with input as {
        "id": "36-modules-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    modules.metadata.dimension_id == "36-modules"
}

test_metadata_version {
    modules.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := modules.audit_entry with input as {
        "id": "36-modules-test-001",
        "status": "active"
    }
    entry.dimension == "36-modules"
}
