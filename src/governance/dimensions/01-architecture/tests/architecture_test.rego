# =============================================================================
# SynergyMesh Governance - Architecture Governance Policy Tests
# Dimension: 01-architecture
# =============================================================================

package governance.architecture_test

import data.governance.architecture

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    architecture.allow with input as {
        "id": "01-architecture-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not architecture.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not architecture.allow with input as {
        "id": "01-architecture-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    architecture.compliant with input as {
        "id": "01-architecture-test-001",
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
    violations := architecture.violations with input as {
        "id": "01-architecture-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := architecture.violations with input as {
        "id": "01-architecture-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    architecture.metadata.dimension_id == "01-architecture"
}

test_metadata_version {
    architecture.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := architecture.audit_entry with input as {
        "id": "01-architecture-test-001",
        "status": "active"
    }
    entry.dimension == "01-architecture"
}
