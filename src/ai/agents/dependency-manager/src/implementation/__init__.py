# -*- coding: utf-8 -*-
"""
實施路徑模組 (Implementation Module)

提供 12 個月實施計劃、成功指標追蹤和行動指南功能。
"""

from .implementation_plan import (
    ImplementationPlan,
    Phase,
    Milestone,
    Task
)
from .success_metrics import (
    SuccessMetricsTracker,
    TechnicalMetric,
    BusinessMetric,
    OrganizationalMetric
)
from .action_guide import (
    ActionGuide,
    ActionItem,
    Recommendation,
    StrategyEvaluator
)

__all__ = [
    # Implementation Plan
    'ImplementationPlan',
    'Phase',
    'Milestone',
    'Task',
    # Success Metrics
    'SuccessMetricsTracker',
    'TechnicalMetric',
    'BusinessMetric',
    'OrganizationalMetric',
    # Action Guide
    'ActionGuide',
    'ActionItem',
    'Recommendation',
    'StrategyEvaluator',
]
