# =============================================================================
# SynergyMesh Governance - Deployment Governance Policy Tests
# Dimension: 42-deployment
# =============================================================================

package governance.deployment_test

import data.governance.deployment

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    deployment.allow with input as {
        "id": "42-deployment-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not deployment.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not deployment.allow with input as {
        "id": "42-deployment-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    deployment.compliant with input as {
        "id": "42-deployment-test-001",
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
    violations := deployment.violations with input as {
        "id": "42-deployment-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := deployment.violations with input as {
        "id": "42-deployment-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    deployment.metadata.dimension_id == "42-deployment"
}

test_metadata_version {
    deployment.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := deployment.audit_entry with input as {
        "id": "42-deployment-test-001",
        "status": "active"
    }
    entry.dimension == "42-deployment"
}
