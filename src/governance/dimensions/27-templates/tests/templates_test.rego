# =============================================================================
# SynergyMesh Governance - Templates Governance Policy Tests
# Dimension: 27-templates
# =============================================================================

package governance.templates_test

import data.governance.templates

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    templates.allow with input as {
        "id": "27-templates-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not templates.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not templates.allow with input as {
        "id": "27-templates-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    templates.compliant with input as {
        "id": "27-templates-test-001",
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
    violations := templates.violations with input as {
        "id": "27-templates-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := templates.violations with input as {
        "id": "27-templates-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    templates.metadata.dimension_id == "27-templates"
}

test_metadata_version {
    templates.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := templates.audit_entry with input as {
        "id": "27-templates-test-001",
        "status": "active"
    }
    entry.dimension == "27-templates"
}
