"""
評估框架模組 - SMART-V 量化評估系統

提供全面的提示詞選擇和專案評估框架。
"""

from .evaluation_report import EvaluationReportGenerator
from .smartv_framework import (
    AchievabilityEvaluator,
    EvaluationDimension,
    MarketFitEvaluator,
    ROIEvaluator,
    ScalabilityEvaluator,
    SMARTVFramework,
    SMARTVResult,
    TechnologyMaturityEvaluator,
    ValueCreationEvaluator,
)
from .weight_config import CompanyStage, WeightConfigManager

__all__ = [
    'SMARTVFramework',
    'ScalabilityEvaluator',
    'MarketFitEvaluator',
    'AchievabilityEvaluator',
    'ROIEvaluator',
    'TechnologyMaturityEvaluator',
    'ValueCreationEvaluator',
    'EvaluationDimension',
    'SMARTVResult',
    'WeightConfigManager',
    'CompanyStage',
    'EvaluationReportGenerator',
]
