# =============================================================================
# SynergyMesh Governance - Visualization Governance Policy Tests
# Dimension: 68-visualization
# =============================================================================

package governance.visualization_test

import data.governance.visualization

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    visualization.allow with input as {
        "id": "68-visualization-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not visualization.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not visualization.allow with input as {
        "id": "68-visualization-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    visualization.compliant with input as {
        "id": "68-visualization-test-001",
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
    violations := visualization.violations with input as {
        "id": "68-visualization-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := visualization.violations with input as {
        "id": "68-visualization-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    visualization.metadata.dimension_id == "68-visualization"
}

test_metadata_version {
    visualization.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := visualization.audit_entry with input as {
        "id": "68-visualization-test-001",
        "status": "active"
    }
    entry.dimension == "68-visualization"
}
