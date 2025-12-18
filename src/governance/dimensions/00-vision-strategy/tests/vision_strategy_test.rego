# =============================================================================
# SynergyMesh Governance - Vision Strategy Governance Policy Tests
# Dimension: 00-vision-strategy
# =============================================================================

package governance.vision_strategy_test

import data.governance.vision_strategy

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    vision_strategy.allow with input as {
        "id": "00-vision-strategy-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not vision_strategy.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not vision_strategy.allow with input as {
        "id": "00-vision-strategy-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    vision_strategy.compliant with input as {
        "id": "00-vision-strategy-test-001",
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
    violations := vision_strategy.violations with input as {
        "id": "00-vision-strategy-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := vision_strategy.violations with input as {
        "id": "00-vision-strategy-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    vision_strategy.metadata.dimension_id == "00-vision-strategy"
}

test_metadata_version {
    vision_strategy.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := vision_strategy.audit_entry with input as {
        "id": "00-vision-strategy-test-001",
        "status": "active"
    }
    entry.dimension == "00-vision-strategy"
}
