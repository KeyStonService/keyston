# =============================================================================
# SynergyMesh Governance - Audit Trail Governance Policy Tests
# Dimension: 70-audit-trail
# =============================================================================

package governance.audit_trail_test

import data.governance.audit_trail

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    audit_trail.allow with input as {
        "id": "70-audit-trail-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not audit_trail.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not audit_trail.allow with input as {
        "id": "70-audit-trail-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    audit_trail.compliant with input as {
        "id": "70-audit-trail-test-001",
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
    violations := audit_trail.violations with input as {
        "id": "70-audit-trail-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := audit_trail.violations with input as {
        "id": "70-audit-trail-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    audit_trail.metadata.dimension_id == "70-audit-trail"
}

test_metadata_version {
    audit_trail.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := audit_trail.audit_entry with input as {
        "id": "70-audit-trail-test-001",
        "status": "active"
    }
    entry.dimension == "70-audit-trail"
}
