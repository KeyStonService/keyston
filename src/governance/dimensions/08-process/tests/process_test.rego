# =============================================================================
# SynergyMesh Governance - Process Governance Policy Tests
# Dimension: 08-process
# =============================================================================

package governance.process_test

import data.governance.process

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    process.allow with input as {
        "id": "08-process-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not process.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not process.allow with input as {
        "id": "08-process-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    process.compliant with input as {
        "id": "08-process-test-001",
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
    violations := process.violations with input as {
        "id": "08-process-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := process.violations with input as {
        "id": "08-process-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    process.metadata.dimension_id == "08-process"
}

test_metadata_version {
    process.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := process.audit_entry with input as {
        "id": "08-process-test-001",
        "status": "active"
    }
    entry.dimension == "08-process"
}
