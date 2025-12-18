# =============================================================================
# SynergyMesh Governance - Synthesis Governance Policy Tests
# Dimension: 80-synthesis
# =============================================================================

package governance.synthesis_test

import data.governance.synthesis

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    synthesis.allow with input as {
        "id": "80-synthesis-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not synthesis.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not synthesis.allow with input as {
        "id": "80-synthesis-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    synthesis.compliant with input as {
        "id": "80-synthesis-test-001",
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
    violations := synthesis.violations with input as {
        "id": "80-synthesis-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := synthesis.violations with input as {
        "id": "80-synthesis-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    synthesis.metadata.dimension_id == "80-synthesis"
}

test_metadata_version {
    synthesis.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := synthesis.audit_entry with input as {
        "id": "80-synthesis-test-001",
        "status": "active"
    }
    entry.dimension == "80-synthesis"
}
