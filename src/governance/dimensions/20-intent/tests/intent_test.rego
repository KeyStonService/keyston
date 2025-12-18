# =============================================================================
# SynergyMesh Governance - Intent Governance Policy Tests
# Dimension: 20-intent
# =============================================================================

package governance.intent_test

import data.governance.intent

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    intent.allow with input as {
        "id": "20-intent-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not intent.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not intent.allow with input as {
        "id": "20-intent-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    intent.compliant with input as {
        "id": "20-intent-test-001",
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
    violations := intent.violations with input as {
        "id": "20-intent-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := intent.violations with input as {
        "id": "20-intent-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    intent.metadata.dimension_id == "20-intent"
}

test_metadata_version {
    intent.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := intent.audit_entry with input as {
        "id": "20-intent-test-001",
        "status": "active"
    }
    entry.dimension == "20-intent"
}
