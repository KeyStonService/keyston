# =============================================================================
# SynergyMesh Governance - Scripts Governance Policy Tests
# Dimension: 35-scripts
# =============================================================================

package governance.scripts_test

import data.governance.scripts

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    scripts.allow with input as {
        "id": "35-scripts-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not scripts.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not scripts.allow with input as {
        "id": "35-scripts-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    scripts.compliant with input as {
        "id": "35-scripts-test-001",
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
    violations := scripts.violations with input as {
        "id": "35-scripts-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := scripts.violations with input as {
        "id": "35-scripts-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    scripts.metadata.dimension_id == "35-scripts"
}

test_metadata_version {
    scripts.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := scripts.audit_entry with input as {
        "id": "35-scripts-test-001",
        "status": "active"
    }
    entry.dimension == "35-scripts"
}
