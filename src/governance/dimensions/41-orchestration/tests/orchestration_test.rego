# =============================================================================
# SynergyMesh Governance - Orchestration Governance Policy Tests
# Dimension: 41-orchestration
# =============================================================================

package governance.orchestration_test

import data.governance.orchestration

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    orchestration.allow with input as {
        "id": "41-orchestration-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not orchestration.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not orchestration.allow with input as {
        "id": "41-orchestration-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    orchestration.compliant with input as {
        "id": "41-orchestration-test-001",
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
    violations := orchestration.violations with input as {
        "id": "41-orchestration-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := orchestration.violations with input as {
        "id": "41-orchestration-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    orchestration.metadata.dimension_id == "41-orchestration"
}

test_metadata_version {
    orchestration.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := orchestration.audit_entry with input as {
        "id": "41-orchestration-test-001",
        "status": "active"
    }
    entry.dimension == "41-orchestration"
}
