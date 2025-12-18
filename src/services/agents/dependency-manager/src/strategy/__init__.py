"""
策略模組 - Phase 5 實現

此模組提供企業級策略規劃與決策支援功能：
- 案例學習引擎
- 策略顧問
- 資源優化器
- 演進追蹤器

Copyright (c) 2024 SynergyMesh
MIT License
"""

from .case_study_engine import CaseStudy, CaseStudyEngine, EvolutionPhase, LessonLearned
from .evolution_tracker import EvolutionTracker, MaturityLevel, PhaseTransition, ProjectMaturity
from .resource_optimizer import (
    BudgetAllocation,
    OptimizationResult,
    ResourceOptimizer,
    TeamAllocation,
)
from .strategy_advisor import (
    MarketTimingAnalysis,
    StrategyAdvisor,
    StrategyRecommendation,
    TechCapabilityAssessment,
)

__all__ = [
    # 案例學習
    'CaseStudyEngine',
    'CaseStudy',
    'EvolutionPhase',
    'LessonLearned',
    # 策略顧問
    'StrategyAdvisor',
    'TechCapabilityAssessment',
    'MarketTimingAnalysis',
    'StrategyRecommendation',
    # 資源優化
    'ResourceOptimizer',
    'BudgetAllocation',
    'TeamAllocation',
    'OptimizationResult',
    # 演進追蹤
    'EvolutionTracker',
    'ProjectMaturity',
    'MaturityLevel',
    'PhaseTransition',
]
