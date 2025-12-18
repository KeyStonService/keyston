# =============================================================================
# SynergyMesh Governance - Security Policy
# Security-focused governance rules
# =============================================================================

package governance.security

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# =============================================================================
# METADATA
# =============================================================================
metadata := {
    "policy_id": "governance.security",
    "version": "1.0.0",
    "description": "Security policy for governance framework",
    "compliance": ["ISO-27001", "NIST-CSF", "Zero-Trust"]
}

# =============================================================================
# DEFAULT DECISIONS
# =============================================================================
default allow := false
default secure := false

# =============================================================================
# SECURITY RULES
# =============================================================================

allow if {
    no_security_violations
    authentication_valid
    authorization_valid
}

secure if {
    allow
    encryption_enabled
    audit_logging_enabled
}

# =============================================================================
# SECURITY VIOLATION CHECKS
# =============================================================================

no_security_violations if {
    count(security_violations) == 0
}

# Collect security violations
security_violations contains msg if {
    input.spec.security.encryption == false
    msg := "Encryption must be enabled"
}

security_violations contains msg if {
    input.spec.permissions
    permission := input.spec.permissions[_]
    permission.scope == "*"
    permission.action == "*"
    msg := "Wildcard permissions are not allowed"
}

security_violations contains msg if {
    input.spec.network
    input.spec.network.allow_public == true
    not input.spec.network.rate_limiting
    msg := "Public access requires rate limiting"
}

security_violations contains msg if {
    input.spec.credentials
    credential := input.spec.credentials[_]
    not credential.encrypted
    msg := "Credentials must be encrypted"
}

# =============================================================================
# AUTHENTICATION VALIDATION
# =============================================================================

authentication_valid if {
    # No auth config required
    not input.spec.authentication
}

authentication_valid if {
    input.spec.authentication
    input.spec.authentication.required == true
    valid_auth_method(input.spec.authentication.method)
}

valid_auth_method(method) if {
    method in ["oauth2", "oidc", "mtls", "api_key", "jwt"]
}

# =============================================================================
# AUTHORIZATION VALIDATION
# =============================================================================

authorization_valid if {
    # No authz config required
    not input.spec.authorization
}

authorization_valid if {
    input.spec.authorization
    input.spec.authorization.model in ["rbac", "abac", "pbac"]
}

# =============================================================================
# ENCRYPTION REQUIREMENTS
# =============================================================================

encryption_enabled if {
    not input.spec.security
}

encryption_enabled if {
    input.spec.security.encryption != false
}

# =============================================================================
# AUDIT LOGGING REQUIREMENTS
# =============================================================================

audit_logging_enabled if {
    not input.spec.audit
}

audit_logging_enabled if {
    input.spec.audit.enabled != false
}

# =============================================================================
# DENY RULES
# =============================================================================

deny[result] if {
    violation := security_violations[_]
    result := {
        "policy": "governance.security",
        "code": "SECURITY_VIOLATION",
        "message": violation,
        "severity": "critical"
    }
}
