# =============================================================================
# SynergyMesh Governance - Security Governance Policy Tests
# Dimension: 06-security
# =============================================================================

package governance.security_test

import data.governance.security

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    security.allow with input as {
        "id": "06-security-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not security.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not security.allow with input as {
        "id": "06-security-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    security.compliant with input as {
        "id": "06-security-test-001",
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
    violations := security.violations with input as {
        "id": "06-security-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := security.violations with input as {
        "id": "06-security-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    security.metadata.dimension_id == "06-security"
}

test_metadata_version {
    security.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := security.audit_entry with input as {
        "id": "06-security-test-001",
        "status": "active"
    }
    entry.dimension == "06-security"
}
