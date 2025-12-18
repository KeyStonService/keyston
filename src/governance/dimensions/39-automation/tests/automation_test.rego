# =============================================================================
# SynergyMesh Governance - Automation Governance Policy Tests
# Dimension: 39-automation
# =============================================================================

package governance.automation_test

import data.governance.automation

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    automation.allow with input as {
        "id": "39-automation-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not automation.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not automation.allow with input as {
        "id": "39-automation-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    automation.compliant with input as {
        "id": "39-automation-test-001",
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
    violations := automation.violations with input as {
        "id": "39-automation-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := automation.violations with input as {
        "id": "39-automation-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    automation.metadata.dimension_id == "39-automation"
}

test_metadata_version {
    automation.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := automation.audit_entry with input as {
        "id": "39-automation-test-001",
        "status": "active"
    }
    entry.dimension == "39-automation"
}
