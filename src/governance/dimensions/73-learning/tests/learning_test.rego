# =============================================================================
# SynergyMesh Governance - Learning Governance Policy Tests
# Dimension: 73-learning
# =============================================================================

package governance.learning_test

import data.governance.learning

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    learning.allow with input as {
        "id": "73-learning-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not learning.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not learning.allow with input as {
        "id": "73-learning-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    learning.compliant with input as {
        "id": "73-learning-test-001",
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
    violations := learning.violations with input as {
        "id": "73-learning-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := learning.violations with input as {
        "id": "73-learning-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    learning.metadata.dimension_id == "73-learning"
}

test_metadata_version {
    learning.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := learning.audit_entry with input as {
        "id": "73-learning-test-001",
        "status": "active"
    }
    entry.dimension == "73-learning"
}
