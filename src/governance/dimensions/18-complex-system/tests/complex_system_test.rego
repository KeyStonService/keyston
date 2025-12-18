# =============================================================================
# SynergyMesh Governance - Complex System Governance Policy Tests
# Dimension: 18-complex-system
# =============================================================================

package governance.complex_system_test

import data.governance.complex_system

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    complex_system.allow with input as {
        "id": "18-complex-system-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not complex_system.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not complex_system.allow with input as {
        "id": "18-complex-system-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    complex_system.compliant with input as {
        "id": "18-complex-system-test-001",
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
    violations := complex_system.violations with input as {
        "id": "18-complex-system-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := complex_system.violations with input as {
        "id": "18-complex-system-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    complex_system.metadata.dimension_id == "18-complex-system"
}

test_metadata_version {
    complex_system.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := complex_system.audit_entry with input as {
        "id": "18-complex-system-test-001",
        "status": "active"
    }
    entry.dimension == "18-complex-system"
}
