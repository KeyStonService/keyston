# =============================================================================
# SynergyMesh Governance - Tools Governance Policy Tests
# Dimension: 26-tools
# =============================================================================

package governance.tools_test

import data.governance.tools

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    tools.allow with input as {
        "id": "26-tools-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not tools.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not tools.allow with input as {
        "id": "26-tools-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    tools.compliant with input as {
        "id": "26-tools-test-001",
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
    violations := tools.violations with input as {
        "id": "26-tools-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := tools.violations with input as {
        "id": "26-tools-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    tools.metadata.dimension_id == "26-tools"
}

test_metadata_version {
    tools.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := tools.audit_entry with input as {
        "id": "26-tools-test-001",
        "status": "active"
    }
    entry.dimension == "26-tools"
}
