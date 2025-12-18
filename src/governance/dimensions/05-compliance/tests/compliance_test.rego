# =============================================================================
# SynergyMesh Governance - Compliance Governance Policy Tests
# Dimension: 05-compliance
# =============================================================================

package governance.compliance_test

import data.governance.compliance

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    compliance.allow with input as {
        "id": "05-compliance-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not compliance.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not compliance.allow with input as {
        "id": "05-compliance-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    compliance.compliant with input as {
        "id": "05-compliance-test-001",
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
    violations := compliance.violations with input as {
        "id": "05-compliance-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := compliance.violations with input as {
        "id": "05-compliance-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    compliance.metadata.dimension_id == "05-compliance"
}

test_metadata_version {
    compliance.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := compliance.audit_entry with input as {
        "id": "05-compliance-test-001",
        "status": "active"
    }
    entry.dimension == "05-compliance"
}
