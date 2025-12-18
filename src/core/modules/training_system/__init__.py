"""
SynergyMesh AI Training System (AI 訓練系統)

Phase 7: Knowledge & Skills Base for AI Agent Training

This module provides comprehensive training capabilities for AI agents,
including domain knowledge, skill development, and example-driven learning.

核心理念：不只是告訴 AI「不能做什麼」，更要教導 AI「應該怎麼做」
"""

from .example_library import (
    CodeExample,
    DecisionExample,
    ExampleCategory,
    ExampleLibrary,
    ScenarioExample,
)
from .knowledge_base import (
    AntiPattern,
    BestPractice,
    ConceptDefinition,
    DomainKnowledge,
    KnowledgeBase,
    KnowledgeCategory,
)
from .skills_training import (
    LearningPath,
    Skill,
    SkillAssessment,
    SkillLevel,
    SkillsTrainingSystem,
    TrainingModule,
    TrainingSession,
)

__all__ = [
    # Knowledge Base
    'KnowledgeBase',
    'DomainKnowledge',
    'ConceptDefinition',
    'BestPractice',
    'AntiPattern',
    'KnowledgeCategory',
    # Skills Training
    'SkillsTrainingSystem',
    'Skill',
    'SkillLevel',
    'TrainingModule',
    'TrainingSession',
    'SkillAssessment',
    'LearningPath',
    # Example Library
    'ExampleLibrary',
    'CodeExample',
    'ScenarioExample',
    'DecisionExample',
    'ExampleCategory',
]

__version__ = '1.0.0'
