# =============================================================================
# SynergyMesh Governance - Logging Governance Policy Tests
# Dimension: 51-logging
# =============================================================================

package governance.logging_test

import data.governance.logging

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    logging.allow with input as {
        "id": "51-logging-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not logging.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not logging.allow with input as {
        "id": "51-logging-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    logging.compliant with input as {
        "id": "51-logging-test-001",
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
    violations := logging.violations with input as {
        "id": "51-logging-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := logging.violations with input as {
        "id": "51-logging-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    logging.metadata.dimension_id == "51-logging"
}

test_metadata_version {
    logging.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := logging.audit_entry with input as {
        "id": "51-logging-test-001",
        "status": "active"
    }
    entry.dimension == "51-logging"
}
