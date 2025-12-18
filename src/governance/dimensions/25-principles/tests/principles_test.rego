# =============================================================================
# SynergyMesh Governance - Principles Governance Policy Tests
# Dimension: 25-principles
# =============================================================================

package governance.principles_test

import data.governance.principles

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    principles.allow with input as {
        "id": "25-principles-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not principles.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not principles.allow with input as {
        "id": "25-principles-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    principles.compliant with input as {
        "id": "25-principles-test-001",
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
    violations := principles.violations with input as {
        "id": "25-principles-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := principles.violations with input as {
        "id": "25-principles-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    principles.metadata.dimension_id == "25-principles"
}

test_metadata_version {
    principles.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := principles.audit_entry with input as {
        "id": "25-principles-test-001",
        "status": "active"
    }
    entry.dimension == "25-principles"
}
