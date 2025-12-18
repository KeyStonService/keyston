# =============================================================================
# SynergyMesh Governance - Audit Governance Policy Tests
# Dimension: 07-audit
# =============================================================================

package governance.audit_test

import data.governance.audit

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    audit.allow with input as {
        "id": "07-audit-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not audit.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not audit.allow with input as {
        "id": "07-audit-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    audit.compliant with input as {
        "id": "07-audit-test-001",
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
    violations := audit.violations with input as {
        "id": "07-audit-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := audit.violations with input as {
        "id": "07-audit-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    audit.metadata.dimension_id == "07-audit"
}

test_metadata_version {
    audit.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := audit.audit_entry with input as {
        "id": "07-audit-test-001",
        "status": "active"
    }
    entry.dimension == "07-audit"
}
