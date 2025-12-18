# =============================================================================
# SynergyMesh Governance - Common Governance Policy Tests
# Dimension: 33-common
# =============================================================================

package governance.common_test

import data.governance.common

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    common.allow with input as {
        "id": "33-common-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not common.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not common.allow with input as {
        "id": "33-common-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    common.compliant with input as {
        "id": "33-common-test-001",
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
    violations := common.violations with input as {
        "id": "33-common-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := common.violations with input as {
        "id": "33-common-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    common.metadata.dimension_id == "33-common"
}

test_metadata_version {
    common.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := common.audit_entry with input as {
        "id": "33-common-test-001",
        "status": "active"
    }
    entry.dimension == "33-common"
}
