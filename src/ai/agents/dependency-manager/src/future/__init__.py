# -*- coding: utf-8 -*-
"""
未來發展模組 (Future Development Module)

第六階段實現：
- 永續發展分析器：綠色開發、碳足跡計算
- 低代碼整合：公民開發者支援
- 隱私優先框架：隱私設計、數據主權
- 發展追蹤器：3-2-1 策略、持續優化

Phase 6 Implementation:
- Sustainable Development Analyzer: Green development, carbon footprint calculation
- Low-Code Integration: Citizen developer support
- Privacy-First Framework: Privacy by design, data sovereignty
- Development Tracker: 3-2-1 strategy, continuous optimization
"""

from .sustainable_analyzer import (
    SustainableAnalyzer,
    CarbonFootprint,
    EnergyEfficiency,
    GreenScore,
)
from .lowcode_integration import (
    LowCodeIntegration,
    CitizenDeveloper,
    VisualWorkflow,
    AutoGenerator,
)
from .privacy_framework import (
    PrivacyFramework,
    PrivacyByDesign,
    DataSovereignty,
    ConsentManager,
)
from .development_tracker import (
    DevelopmentTracker,
    Strategy321,
    TeamCapability,
    ContinuousOptimization,
)

__all__ = [
    # 永續發展
    'SustainableAnalyzer',
    'CarbonFootprint',
    'EnergyEfficiency',
    'GreenScore',
    # 低代碼
    'LowCodeIntegration',
    'CitizenDeveloper',
    'VisualWorkflow',
    'AutoGenerator',
    # 隱私優先
    'PrivacyFramework',
    'PrivacyByDesign',
    'DataSovereignty',
    'ConsentManager',
    # 發展追蹤
    'DevelopmentTracker',
    'Strategy321',
    'TeamCapability',
    'ContinuousOptimization',
]
