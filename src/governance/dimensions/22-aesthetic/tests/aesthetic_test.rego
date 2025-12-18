# =============================================================================
# SynergyMesh Governance - Aesthetic Governance Policy Tests
# Dimension: 22-aesthetic
# =============================================================================

package governance.aesthetic_test

import data.governance.aesthetic

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    aesthetic.allow with input as {
        "id": "22-aesthetic-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not aesthetic.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not aesthetic.allow with input as {
        "id": "22-aesthetic-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    aesthetic.compliant with input as {
        "id": "22-aesthetic-test-001",
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
    violations := aesthetic.violations with input as {
        "id": "22-aesthetic-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := aesthetic.violations with input as {
        "id": "22-aesthetic-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    aesthetic.metadata.dimension_id == "22-aesthetic"
}

test_metadata_version {
    aesthetic.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := aesthetic.audit_entry with input as {
        "id": "22-aesthetic-test-001",
        "status": "active"
    }
    entry.dimension == "22-aesthetic"
}
