# =============================================================================
# SynergyMesh Governance - Prediction Governance Policy Tests
# Dimension: 79-prediction
# =============================================================================

package governance.prediction_test

import data.governance.prediction

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    prediction.allow with input as {
        "id": "79-prediction-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not prediction.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not prediction.allow with input as {
        "id": "79-prediction-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    prediction.compliant with input as {
        "id": "79-prediction-test-001",
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
    violations := prediction.violations with input as {
        "id": "79-prediction-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := prediction.violations with input as {
        "id": "79-prediction-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    prediction.metadata.dimension_id == "79-prediction"
}

test_metadata_version {
    prediction.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := prediction.audit_entry with input as {
        "id": "79-prediction-test-001",
        "status": "active"
    }
    entry.dimension == "79-prediction"
}
