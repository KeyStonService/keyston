# =============================================================================
# SynergyMesh Governance - Agents Governance Policy Tests
# Dimension: 30-agents
# =============================================================================

package governance.agents_test

import data.governance.agents

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    agents.allow with input as {
        "id": "30-agents-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not agents.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not agents.allow with input as {
        "id": "30-agents-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    agents.compliant with input as {
        "id": "30-agents-test-001",
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
    violations := agents.violations with input as {
        "id": "30-agents-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := agents.violations with input as {
        "id": "30-agents-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    agents.metadata.dimension_id == "30-agents"
}

test_metadata_version {
    agents.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := agents.audit_entry with input as {
        "id": "30-agents-test-001",
        "status": "active"
    }
    entry.dimension == "30-agents"
}
