"""
═══════════════════════════════════════════════════════════
        SynergyMesh AI 最高指導憲章系統 v1.0
        AI Supreme Directive Constitution System
═══════════════════════════════════════════════════════════

本系統是所有 AI 智能體的最高行為準則實現
任何 AI 執行任何操作都必須遵循此憲章

This system implements the supreme directive constitution
that all AI agents must follow for any operation.

Phase 6 Implementation - 100% Complete Self-Contained Modules
"""

from .fundamental_laws import (
    FundamentalLaws,
    LawZero,
    LawOne,
    LawTwo,
    LawThree,
    EnforcementLevel,
)

from .operational_rules import (
    OperationalRules,
    DataHandlingRule,
    SystemAccessRule,
    ResourceUsageRule,
    CommunicationRule,
    OperationalRuleEngine,
)

from .adaptive_guidelines import (
    AdaptiveGuidelines,
    DomainGuideline,
    ContextualGuideline,
    LearningGuideline,
    AdaptiveGuidelineEngine,
)

from .constitution_engine import (
    ConstitutionEngine,
    ConstitutionVerdict,
    VerdictType,
    ActionProposal,
)

from .policy_as_prompt import (
    PolicyAsPrompt,
    PolicyPrompt,
    PromptGuardrail,
    PolicyEnforcer,
)

from .guardrails import (
    GuardrailSystem,
    Guardrail,
    GuardrailType,
    GuardrailResult,
    SafetyGuardrail,
    ComplianceGuardrail,
    EthicsGuardrail,
)

__all__ = [
    # Fundamental Laws
    'FundamentalLaws',
    'LawZero',
    'LawOne',
    'LawTwo',
    'LawThree',
    'EnforcementLevel',
    # Operational Rules
    'OperationalRules',
    'DataHandlingRule',
    'SystemAccessRule',
    'ResourceUsageRule',
    'CommunicationRule',
    'OperationalRuleEngine',
    # Adaptive Guidelines
    'AdaptiveGuidelines',
    'DomainGuideline',
    'ContextualGuideline',
    'LearningGuideline',
    'AdaptiveGuidelineEngine',
    # Constitution Engine
    'ConstitutionEngine',
    'ConstitutionVerdict',
    'VerdictType',
    'ActionProposal',
    # Policy as Prompt
    'PolicyAsPrompt',
    'PolicyPrompt',
    'PromptGuardrail',
    'PolicyEnforcer',
    # Guardrails
    'GuardrailSystem',
    'Guardrail',
    'GuardrailType',
    'GuardrailResult',
    'SafetyGuardrail',
    'ComplianceGuardrail',
    'EthicsGuardrail',
]

__version__ = '1.0.0'
__author__ = 'SynergyMesh Team'
