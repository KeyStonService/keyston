# =============================================================================
# SynergyMesh Governance - Documentation Governance Policy Tests
# Dimension: 29-docs
# =============================================================================

package governance.docs_test

import data.governance.docs

# =============================================================================
# TEST: ALLOW RULES
# =============================================================================

test_allow_valid_input {
    docs.allow with input as {
        "id": "29-docs-test-001",
        "status": "active",
        "config": {
            "enabled": true
        }
    }
}

test_deny_missing_id {
    not docs.allow with input as {
        "status": "active"
    }
}

test_deny_missing_status {
    not docs.allow with input as {
        "id": "29-docs-test-001"
    }
}

# =============================================================================
# TEST: COMPLIANCE RULES
# =============================================================================

test_compliant_with_metadata {
    docs.compliant with input as {
        "id": "29-docs-test-001",
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
    violations := docs.violations with input as {
        "id": "29-docs-test-001",
        "status": "active"
    }
    count(violations) == 0
}

test_violations_for_error_without_details {
    violations := docs.violations with input as {
        "id": "29-docs-test-001",
        "status": "error"
    }
    count(violations) > 0
}

# =============================================================================
# TEST: METADATA
# =============================================================================

test_metadata_dimension_id {
    docs.metadata.dimension_id == "29-docs"
}

test_metadata_version {
    docs.metadata.version == "1.0.0"
}

# =============================================================================
# TEST: AUDIT ENTRY
# =============================================================================

test_audit_entry_generated {
    entry := docs.audit_entry with input as {
        "id": "29-docs-test-001",
        "status": "active"
    }
    entry.dimension == "29-docs"
}
