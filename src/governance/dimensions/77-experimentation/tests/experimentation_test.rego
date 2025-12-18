# =============================================================================
# SynergyMesh Governance - Experimentation Governance Policy Tests
# Dimension: 77-experimentation
# =============================================================================

package governance.experimentation_test

import data.governance.experimentation

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    experimentation.allow with input as {
        "id": "77-experimentation-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not experimentation.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not experimentation.allow with input as {
        "id": "77-experimentation-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    experimentation.compliant with input as {
        "id": "77-experimentation-test-001",
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
    violations := experimentation.violations with input as {
        "id": "77-experimentation-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := experimentation.violations with input as {
        "id": "77-experimentation-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    experimentation.metadata.dimension_id == "77-experimentation"
}

test_metadata_version {
    experimentation.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := experimentation.audit_entry with input as {
        "id": "77-experimentation-test-001",
        "status": "active"
    }
    entry.dimension == "77-experimentation"
}
