# =============================================================================
# SynergyMesh Governance - AI Agent Policy
# AI Agent lifecycle and permission governance
# =============================================================================

package governance.agent

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# =============================================================================
# METADATA
# =============================================================================
metadata := {
    "policy_id": "governance.agent",
    "version": "1.0.0",
    "description": "AI Agent governance policy",
    "compliance": ["ISO-42001", "NIST-AI-RMF", "EU-AI-Act"]
}

# =============================================================================
# AGENT LIFECYCLE STATES
# =============================================================================
valid_states := [
    "registered",
    "developing",
    "testing",
    "validating",
    "approved",
    "deploying",
    "active",
    "monitoring",
    "degraded",
    "retraining",
    "updating",
    "retiring",
    "retired"
]

# =============================================================================
# VALID STATE TRANSITIONS
# =============================================================================
valid_transitions := {
    "registered": ["developing"],
    "developing": ["testing"],
    "testing": ["validating", "developing"],
    "validating": ["approved", "developing"],
    "approved": ["deploying"],
    "deploying": ["active", "approved"],
    "active": ["monitoring", "degraded", "updating", "retiring"],
    "monitoring": ["active", "degraded"],
    "degraded": ["active", "retraining", "retiring"],
    "retraining": ["testing"],
    "updating": ["testing"],
    "retiring": ["retired"],
    "retired": []
}

# =============================================================================
# RISK LEVELS
# =============================================================================
risk_levels := ["minimal", "limited", "high", "unacceptable"]

# =============================================================================
# DEFAULT DECISIONS
# =============================================================================
default allow := false
default lifecycle_valid := false
default permissions_valid := false
default compliant := false

# =============================================================================
# AGENT GOVERNANCE RULES
# =============================================================================

allow if {
    no_agent_violations
    lifecycle_valid
    permissions_valid
}

compliant if {
    allow
    risk_assessment_complete
    human_oversight_configured
    audit_trail_exists
}

# =============================================================================
# LIFECYCLE VALIDATION
# =============================================================================

lifecycle_valid if {
    input.spec.lifecycle.state in valid_states
    valid_state_transition
}

valid_state_transition if {
    # No previous state (new agent)
    not input.spec.lifecycle.previous_state
}

valid_state_transition if {
    input.spec.lifecycle.previous_state
    input.spec.lifecycle.state in valid_transitions[input.spec.lifecycle.previous_state]
}

# =============================================================================
# PERMISSIONS VALIDATION
# =============================================================================

permissions_valid if {
    # No permissions defined (read-only agent)
    not input.spec.permissions
}

permissions_valid if {
    input.spec.permissions
    no_excessive_permissions
    all_permissions_justified
}

no_excessive_permissions if {
    not input.spec.permissions.admin
}

no_excessive_permissions if {
    input.spec.permissions.admin
    input.spec.permissions.admin_justification
}

all_permissions_justified if {
    every permission in input.spec.permissions.granted {
        permission_justified(permission)
    }
}

permission_justified(permission) if {
    permission.justification
    count(permission.justification) > 10
}

permission_justified(permission) if {
    # Default permissions don't need justification
    permission.type in ["read", "execute"]
}

# =============================================================================
# AGENT VIOLATION CHECKS
# =============================================================================

no_agent_violations if {
    count(agent_violations) == 0
}

agent_violations contains msg if {
    not input.spec.lifecycle.state
    msg := "Agent must have a lifecycle state"
}

agent_violations contains msg if {
    input.spec.lifecycle.state
    not input.spec.lifecycle.state in valid_states
    msg := sprintf("Invalid lifecycle state: %s", [input.spec.lifecycle.state])
}

agent_violations contains msg if {
    input.spec.lifecycle.previous_state
    not input.spec.lifecycle.state in valid_transitions[input.spec.lifecycle.previous_state]
    msg := sprintf("Invalid state transition: %s -> %s", [input.spec.lifecycle.previous_state, input.spec.lifecycle.state])
}

agent_violations contains msg if {
    input.spec.risk_level == "unacceptable"
    msg := "Unacceptable risk level: Agent cannot be deployed"
}

agent_violations contains msg if {
    input.spec.risk_level == "high"
    not input.spec.human_oversight.required
    msg := "High-risk agents require human oversight"
}

agent_violations contains msg if {
    input.spec.capabilities
    "unrestricted_internet" in input.spec.capabilities
    not input.spec.network_policy
    msg := "Unrestricted internet access requires network policy"
}

agent_violations contains msg if {
    input.spec.capabilities
    "execute_code" in input.spec.capabilities
    not input.spec.sandbox.enabled
    msg := "Code execution capability requires sandboxing"
}

# =============================================================================
# RISK ASSESSMENT
# =============================================================================

risk_assessment_complete if {
    input.spec.risk_level
    input.spec.risk_level in risk_levels
    input.spec.risk_assessment
    input.spec.risk_assessment.completed_at
}

# =============================================================================
# HUMAN OVERSIGHT
# =============================================================================

human_oversight_configured if {
    input.spec.risk_level in ["minimal", "limited"]
}

human_oversight_configured if {
    input.spec.risk_level in ["high"]
    input.spec.human_oversight.required == true
    input.spec.human_oversight.approval_chain
    count(input.spec.human_oversight.approval_chain) > 0
}

# =============================================================================
# AUDIT TRAIL
# =============================================================================

audit_trail_exists if {
    input.metadata.created_at
    input.spec.lifecycle.state_history
}

# =============================================================================
# RESPONSIBILITY BOUNDARY
# =============================================================================

responsibility := {
    "ai_autonomous": {
        "operations": ["monitoring", "scaling", "optimization", "recovery"],
        "autonomy": "100%"
    },
    "human_control": {
        "operations": ["strategic_decisions", "policy_approval", "budget", "ethics"],
        "control": "100%"
    }
}

operation_allowed(operation) if {
    operation in responsibility.ai_autonomous.operations
}

operation_requires_approval(operation) if {
    operation in responsibility.human_control.operations
}

# =============================================================================
# DENY RULES
# =============================================================================

deny[result] if {
    violation := agent_violations[_]
    result := {
        "policy": "governance.agent",
        "code": "AGENT_VIOLATION",
        "message": violation,
        "severity": "critical"
    }
}

# =============================================================================
# AUDIT ENTRY
# =============================================================================

audit_entry := {
    "policy": "governance.agent",
    "timestamp": time.now_ns(),
    "agent_id": input.metadata.id,
    "state": input.spec.lifecycle.state,
    "risk_level": input.spec.risk_level,
    "compliant": compliant,
    "violations": agent_violations
}
