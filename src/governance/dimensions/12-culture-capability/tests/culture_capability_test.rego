# =============================================================================
# SynergyMesh Governance - Culture Capability Governance Policy Tests
# Dimension: 12-culture-capability
# =============================================================================

package governance.culture_capability_test

import data.governance.culture_capability

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    culture_capability.allow with input as {
        "id": "12-culture-capability-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not culture_capability.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not culture_capability.allow with input as {
        "id": "12-culture-capability-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    culture_capability.compliant with input as {
        "id": "12-culture-capability-test-001",
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
    violations := culture_capability.violations with input as {
        "id": "12-culture-capability-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := culture_capability.violations with input as {
        "id": "12-culture-capability-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    culture_capability.metadata.dimension_id == "12-culture-capability"
}

test_metadata_version {
    culture_capability.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := culture_capability.audit_entry with input as {
        "id": "12-culture-capability-test-001",
        "status": "active"
    }
    entry.dimension == "12-culture-capability"
}
