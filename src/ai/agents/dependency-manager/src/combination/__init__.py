# -*- coding: utf-8 -*-
"""
進階提示詞組合策略模組
Advanced Prompt Combination Strategy Module

Phase 8: Core-Satellite Architecture, Dynamic Adjustment Mechanisms
"""

from .core_satellite import CoreSatelliteArchitecture
from .combination_templates import CombinationTemplateManager
from .dynamic_adjuster import DynamicAdjuster
from .quarterly_review import QuarterlyReviewEngine

__all__ = [
    'CoreSatelliteArchitecture',
    'CombinationTemplateManager',
    'DynamicAdjuster',
    'QuarterlyReviewEngine',
]
