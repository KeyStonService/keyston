# =============================================================================
# SynergyMesh Governance - Performance Governance Policy Tests
# Dimension: 09-performance
# =============================================================================

package governance.performance_test

import data.governance.performance

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    performance.allow with input as {
        "id": "09-performance-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not performance.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not performance.allow with input as {
        "id": "09-performance-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    performance.compliant with input as {
        "id": "09-performance-test-001",
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
    violations := performance.violations with input as {
        "id": "09-performance-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := performance.violations with input as {
        "id": "09-performance-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    performance.metadata.dimension_id == "09-performance"
}

test_metadata_version {
    performance.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := performance.audit_entry with input as {
        "id": "09-performance-test-001",
        "status": "active"
    }
    entry.dimension == "09-performance"
}
