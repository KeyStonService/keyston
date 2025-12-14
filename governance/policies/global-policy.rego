# =============================================================================
# SynergyMesh Governance - Global Policy
# Cross-dimensional governance rules and constraints
# =============================================================================
# Policy Engine: OPA (Open Policy Agent)
# Language: Rego
# Enforcement: CI/CD, Runtime, Admission Control
# =============================================================================

package governance.global

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# =============================================================================
# METADATA
# =============================================================================
metadata := {
    "policy_id": "governance.global",
    "version": "2.0.0",
    "description": "Global governance policy for all dimensions",
    "compliance": ["ISO-42001", "NIST-AI-RMF", "COBIT-2019"]
}

# =============================================================================
# DEFAULT DECISIONS
# =============================================================================
default allow := false
default compliant := false
default governance_valid := false

# =============================================================================
# GLOBAL ALLOW RULE
# =============================================================================

# Allow if all global requirements are met
allow if {
    valid_structure
    valid_metadata
    no_global_violations
    dimension_registered
}

# =============================================================================
# COMPLIANCE RULE
# =============================================================================

compliant if {
    allow
    has_audit_trail
    meets_security_requirements
    meets_documentation_requirements
}

# =============================================================================
# GOVERNANCE VALIDITY
# =============================================================================

governance_valid if {
    compliant
    all_dependencies_satisfied
    lifecycle_state_valid
}

# =============================================================================
# STRUCTURAL VALIDATION
# =============================================================================

# Valid structure checks
valid_structure if {
    input.apiVersion
    startswith(input.apiVersion, "governance.synergymesh.io/")
    input.kind
    input.metadata
    input.spec
}

# Metadata validation
valid_metadata if {
    input.metadata.name
    input.metadata.version
    valid_semver(input.metadata.version)
    input.metadata.owner
}

# Semantic version validation
valid_semver(version) if {
    regex.match(`^\d+\.\d+\.\d+$`, version)
}

# =============================================================================
# GLOBAL VIOLATION CHECKS
# =============================================================================

no_global_violations if {
    count(global_violations) == 0
}

# Collect all global violations
global_violations contains msg if {
    not input.apiVersion
    msg := "apiVersion is required"
}

global_violations contains msg if {
    not input.kind
    msg := "kind is required"
}

global_violations contains msg if {
    not input.metadata
    msg := "metadata section is required"
}

global_violations contains msg if {
    not input.metadata.name
    msg := "metadata.name is required"
}

global_violations contains msg if {
    not input.metadata.version
    msg := "metadata.version is required"
}

global_violations contains msg if {
    input.metadata.version
    not valid_semver(input.metadata.version)
    msg := "metadata.version must follow semantic versioning (MAJOR.MINOR.PATCH)"
}

global_violations contains msg if {
    not input.metadata.owner
    msg := "metadata.owner is required for accountability"
}

global_violations contains msg if {
    input.status == "active"
    not input.spec
    msg := "Active resources must have spec defined"
}

# =============================================================================
# DIMENSION REGISTRY CHECK
# =============================================================================

dimension_registered if {
    # Check if dimension ID follows standard format
    regex.match(`^\d{2}-[a-z-]+$`, input.metadata.id)
}

dimension_registered if {
    # Alternative: check against known dimensions
    input.metadata.category in ["strategic", "operational", "execution", "observability", "feedback"]
}

# =============================================================================
# AUDIT TRAIL REQUIREMENTS
# =============================================================================

has_audit_trail if {
    input.metadata.created_at
    input.metadata.updated_at
}

has_audit_trail if {
    # New resources may not have timestamps yet
    input.status == "pending"
}

# =============================================================================
# SECURITY REQUIREMENTS
# =============================================================================

meets_security_requirements if {
    # No secrets in plain text
    no_exposed_secrets
    # Has required security fields if applicable
    valid_security_config
}

no_exposed_secrets if {
    not contains_secret_patterns(input)
}

# Check for common secret patterns
contains_secret_patterns(obj) if {
    walk(obj, [path, value])
    is_string(value)
    contains_secret_keyword(path[count(path)-1])
    not is_masked(value)
}

contains_secret_keyword(key) if {
    lower(key) in ["password", "secret", "api_key", "apikey", "token", "credential", "private_key"]
}

is_masked(value) if {
    # Value is masked or encrypted
    startswith(value, "***")
}

is_masked(value) if {
    startswith(value, "encrypted:")
}

is_masked(value) if {
    startswith(value, "vault:")
}

valid_security_config if {
    # Default: security config is valid if not specified
    not input.spec.security
}

valid_security_config if {
    input.spec.security
    input.spec.security.encryption != false
}

# =============================================================================
# DOCUMENTATION REQUIREMENTS
# =============================================================================

meets_documentation_requirements if {
    input.spec.description
    count(input.spec.description) > 10
}

meets_documentation_requirements if {
    # Allow resources without description in draft status
    input.status in ["pending", "draft"]
}

# =============================================================================
# DEPENDENCY VALIDATION
# =============================================================================

all_dependencies_satisfied if {
    # No dependencies required
    not input.spec.dependencies
}

all_dependencies_satisfied if {
    input.spec.dependencies
    # Check each required dependency
    every dep in input.spec.dependencies.required {
        dependency_available(dep)
    }
}

dependency_available(dep) if {
    # Placeholder: check dependency availability
    # In production, this would check against registry
    dep != ""
}

# =============================================================================
# LIFECYCLE STATE VALIDATION
# =============================================================================

valid_lifecycle_states := [
    "pending",
    "initializing",
    "active",
    "degraded",
    "maintenance",
    "retiring",
    "retired",
    "draft"
]

lifecycle_state_valid if {
    not input.status
}

lifecycle_state_valid if {
    input.status in valid_lifecycle_states
}

# =============================================================================
# ENFORCEMENT ACTIONS
# =============================================================================

# Deny with reasons
deny[result] if {
    violation := global_violations[_]
    result := {
        "policy": "governance.global",
        "code": "GLOBAL_VIOLATION",
        "message": violation,
        "severity": "error"
    }
}

# Warnings (non-blocking)
warn[result] if {
    not input.metadata.tags
    result := {
        "policy": "governance.global",
        "code": "MISSING_TAGS",
        "message": "Resource should have tags for categorization",
        "severity": "warning"
    }
}

warn[result] if {
    not input.spec.compliance
    result := {
        "policy": "governance.global",
        "code": "MISSING_COMPLIANCE",
        "message": "Resource should specify compliance frameworks",
        "severity": "warning"
    }
}

# =============================================================================
# AUDIT ENTRY GENERATION
# =============================================================================

audit_entry := {
    "policy": "governance.global",
    "timestamp": time.now_ns(),
    "resource": {
        "kind": input.kind,
        "name": input.metadata.name,
        "version": input.metadata.version
    },
    "decision": {
        "allow": allow,
        "compliant": compliant,
        "governance_valid": governance_valid
    },
    "violations": global_violations,
    "warnings": [w.message | w := warn[_]]
}

# =============================================================================
# METRICS
# =============================================================================

metrics := {
    "policy_evaluations": 1,
    "violations_count": count(global_violations),
    "warnings_count": count(warn),
    "compliant": compliant,
    "governance_valid": governance_valid
}
