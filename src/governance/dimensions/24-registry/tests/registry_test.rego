# =============================================================================
# SynergyMesh Governance - Registry Governance Policy Tests
# Dimension: 24-registry
# =============================================================================

package governance.registry_test

import data.governance.registry

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    registry.allow with input as {
        "id": "24-registry-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not registry.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not registry.allow with input as {
        "id": "24-registry-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    registry.compliant with input as {
        "id": "24-registry-test-001",
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
    violations := registry.violations with input as {
        "id": "24-registry-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := registry.violations with input as {
        "id": "24-registry-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    registry.metadata.dimension_id == "24-registry"
}

test_metadata_version {
    registry.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := registry.audit_entry with input as {
        "id": "24-registry-test-001",
        "status": "active"
    }
    entry.dimension == "24-registry"
}
