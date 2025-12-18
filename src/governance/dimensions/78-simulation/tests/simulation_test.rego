# =============================================================================
# SynergyMesh Governance - Simulation Governance Policy Tests
# Dimension: 78-simulation
# =============================================================================

package governance.simulation_test

import data.governance.simulation

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    simulation.allow with input as {
        "id": "78-simulation-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not simulation.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not simulation.allow with input as {
        "id": "78-simulation-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    simulation.compliant with input as {
        "id": "78-simulation-test-001",
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
    violations := simulation.violations with input as {
        "id": "78-simulation-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := simulation.violations with input as {
        "id": "78-simulation-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    simulation.metadata.dimension_id == "78-simulation"
}

test_metadata_version {
    simulation.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := simulation.audit_entry with input as {
        "id": "78-simulation-test-001",
        "status": "active"
    }
    entry.dimension == "78-simulation"
}
