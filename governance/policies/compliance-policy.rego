# =============================================================================
# SynergyMesh Governance - Compliance Policy
# Regulatory compliance validation
# =============================================================================

package governance.compliance

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# =============================================================================
# METADATA
# =============================================================================
metadata := {
    "policy_id": "governance.compliance",
    "version": "1.0.0",
    "description": "Compliance policy for regulatory frameworks",
    "compliance": ["ISO-42001", "NIST-AI-RMF", "EU-AI-Act", "SOX", "GDPR"]
}

# =============================================================================
# SUPPORTED FRAMEWORKS
# =============================================================================
supported_frameworks := [
    "ISO-42001",
    "NIST-AI-RMF",
    "EU-AI-Act",
    "SOX",
    "GDPR",
    "ISO-27001",
    "COBIT-2019",
    "ITIL-4",
    "NIST-CSF"
]

# =============================================================================
# DEFAULT DECISIONS
# =============================================================================
default allow := false
default compliant := false

# =============================================================================
# COMPLIANCE RULES
# =============================================================================

allow if {
    no_compliance_violations
    required_fields_present
}

compliant if {
    allow
    all_frameworks_satisfied
    evidence_available
}

# =============================================================================
# COMPLIANCE VIOLATION CHECKS
# =============================================================================

no_compliance_violations if {
    count(compliance_violations) == 0
}

compliance_violations contains msg if {
    input.spec.compliance.frameworks
    framework := input.spec.compliance.frameworks[_]
    not framework in supported_frameworks
    msg := sprintf("Unknown compliance framework: %s", [framework])
}

compliance_violations contains msg if {
    input.spec.data_processing
    input.spec.data_processing.personal_data == true
    not input.spec.data_processing.gdpr_basis
    msg := "GDPR: Legal basis required for personal data processing"
}

compliance_violations contains msg if {
    input.spec.ai_system
    input.spec.ai_system.risk_level == "high"
    not input.spec.ai_system.conformity_assessment
    msg := "EU AI Act: High-risk AI systems require conformity assessment"
}

compliance_violations contains msg if {
    input.spec.financial_reporting
    not input.spec.audit.sox_controls
    msg := "SOX: Financial reporting requires SOX controls"
}

# =============================================================================
# REQUIRED FIELDS
# =============================================================================

required_fields_present if {
    input.metadata.owner
    input.metadata.version
    input.spec.description
}

# =============================================================================
# FRAMEWORK SATISFACTION
# =============================================================================

all_frameworks_satisfied if {
    not input.spec.compliance.frameworks
}

all_frameworks_satisfied if {
    input.spec.compliance.frameworks
    every framework in input.spec.compliance.frameworks {
        framework_requirements_met(framework)
    }
}

framework_requirements_met(framework) if {
    framework == "ISO-42001"
    input.spec.ai_management_system
}

framework_requirements_met(framework) if {
    framework == "NIST-AI-RMF"
    input.spec.risk_management
}

framework_requirements_met(framework) if {
    framework == "GDPR"
    gdpr_requirements_met
}

framework_requirements_met(framework) if {
    framework in supported_frameworks
    # Default: framework is satisfied if explicitly declared
    framework in input.spec.compliance.frameworks
}

gdpr_requirements_met if {
    not input.spec.data_processing.personal_data
}

gdpr_requirements_met if {
    input.spec.data_processing.personal_data
    input.spec.data_processing.gdpr_basis
    input.spec.data_processing.retention_policy
}

# =============================================================================
# EVIDENCE REQUIREMENTS
# =============================================================================

evidence_available if {
    not input.spec.compliance.evidence_required
}

evidence_available if {
    input.spec.compliance.evidence_required
    input.spec.compliance.evidence
    count(input.spec.compliance.evidence) > 0
}

# =============================================================================
# DENY RULES
# =============================================================================

deny[result] if {
    violation := compliance_violations[_]
    result := {
        "policy": "governance.compliance",
        "code": "COMPLIANCE_VIOLATION",
        "message": violation,
        "severity": "critical"
    }
}

# =============================================================================
# AUDIT ENTRY
# =============================================================================

audit_entry := {
    "policy": "governance.compliance",
    "timestamp": time.now_ns(),
    "frameworks_checked": input.spec.compliance.frameworks,
    "compliant": compliant,
    "violations": compliance_violations
}
