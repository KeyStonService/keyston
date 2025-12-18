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

from .adaptive_guidelines import (
    AdaptiveGuidelineEngine,
    AdaptiveGuidelines,
    ContextualGuideline,
    DomainGuideline,
    LearningGuideline,
)
from .constitution_engine import (
    ActionProposal,
    ConstitutionEngine,
    ConstitutionVerdict,
    VerdictType,
)
from .fundamental_laws import (
    EnforcementLevel,
    FundamentalLaws,
    LawOne,
    LawThree,
    LawTwo,
    LawZero,
)
from .guardrails import (
    ComplianceGuardrail,
    EthicsGuardrail,
    Guardrail,
    GuardrailResult,
    GuardrailSystem,
    GuardrailType,
    SafetyGuardrail,
)
from .operational_rules import (
    CommunicationRule,
    DataHandlingRule,
    OperationalRuleEngine,
    OperationalRules,
    ResourceUsageRule,
    SystemAccessRule,
)
from .policy_as_prompt import (
    PolicyAsPrompt,
    PolicyEnforcer,
    PolicyPrompt,
    PromptGuardrail,
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
