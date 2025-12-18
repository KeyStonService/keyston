# =============================================================================
# SynergyMesh Governance - Tools Systems Governance Policy Tests
# Dimension: 11-tools-systems
# =============================================================================

package governance.tools_systems_test

import data.governance.tools_systems

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    tools_systems.allow with input as {
        "id": "11-tools-systems-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not tools_systems.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not tools_systems.allow with input as {
        "id": "11-tools-systems-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    tools_systems.compliant with input as {
        "id": "11-tools-systems-test-001",
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
    violations := tools_systems.violations with input as {
        "id": "11-tools-systems-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := tools_systems.violations with input as {
        "id": "11-tools-systems-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    tools_systems.metadata.dimension_id == "11-tools-systems"
}

test_metadata_version {
    tools_systems.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := tools_systems.audit_entry with input as {
        "id": "11-tools-systems-test-001",
        "status": "active"
    }
    entry.dimension == "11-tools-systems"
}
