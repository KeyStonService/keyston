# -*- coding: utf-8 -*-
"""
核心-衛星模式架構
Core-Satellite Architecture for Prompt Combination Strategy
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class PromptCategory(Enum):
    ENTERPRISE = "enterprise"
    PROFESSIONAL = "professional"
    HIGH_VALUE = "high_value"
    MARKET_RETURN = "market_return"
    BUSINESS_ORIENTED = "business_oriented"
    ADVANCED = "advanced"
    INTELLIGENT = "intelligent"
    NEXT_GEN = "next_gen"


class AllocationRole(Enum):
    CORE = "core"
    SATELLITE = "satellite"
    EXPLORATION = "exploration"


@dataclass
class PromptAllocation:
    category: PromptCategory
    role: AllocationRole
    allocation_percentage: float
    description: str = ""
    priority: int = 1


@dataclass
class CoreSatelliteConfiguration:
    name: str
    description: str
    core_allocation: PromptAllocation
    satellite_allocations: List[PromptAllocation]
    exploration_allocation: Optional[PromptAllocation] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_total_allocation(self) -> float:
        total = self.core_allocation.allocation_percentage
        for sat in self.satellite_allocations:
            total += sat.allocation_percentage
        if self.exploration_allocation:
            total += self.exploration_allocation.allocation_percentage
        return total
    
    def is_valid(self) -> bool:
        return 99.0 <= self.get_total_allocation() <= 101.0


class CoreSatelliteArchitecture:
    """核心-衛星架構管理器"""
    
    def __init__(self):
        self._configurations: Dict[str, CoreSatelliteConfiguration] = {}
        self._presets = self._load_presets()
    
    def _load_presets(self) -> Dict[str, CoreSatelliteConfiguration]:
        presets = {}
        
        # 穩健成長型
        presets['steady_growth'] = CoreSatelliteConfiguration(
            name="穩健成長型",
            description="適合追求穩定發展的企業",
            core_allocation=PromptAllocation(PromptCategory.ENTERPRISE, AllocationRole.CORE, 70.0, "企業級應用開發"),
            satellite_allocations=[
                PromptAllocation(PromptCategory.PROFESSIONAL, AllocationRole.SATELLITE, 15.0, "專業級開發"),
                PromptAllocation(PromptCategory.HIGH_VALUE, AllocationRole.SATELLITE, 10.0, "高價值應用"),
            ],
            exploration_allocation=PromptAllocation(PromptCategory.INTELLIGENT, AllocationRole.EXPLORATION, 5.0, "智能化探索")
        )
        
        # 快速變現型
        presets['rapid_monetization'] = CoreSatelliteConfiguration(
            name="快速變現型",
            description="適合需要快速獲得市場回報的企業",
            core_allocation=PromptAllocation(PromptCategory.MARKET_RETURN, AllocationRole.CORE, 70.0, "高市場回報"),
            satellite_allocations=[
                PromptAllocation(PromptCategory.BUSINESS_ORIENTED, AllocationRole.SATELLITE, 20.0, "商業導向"),
                PromptAllocation(PromptCategory.ENTERPRISE, AllocationRole.SATELLITE, 5.0, "企業基礎"),
            ],
            exploration_allocation=PromptAllocation(PromptCategory.NEXT_GEN, AllocationRole.EXPLORATION, 5.0, "下世代探索")
        )
        
        # 技術領先型
        presets['tech_leadership'] = CoreSatelliteConfiguration(
            name="技術領先型",
            description="適合追求技術競爭優勢的企業",
            core_allocation=PromptAllocation(PromptCategory.ADVANCED, AllocationRole.CORE, 70.0, "高階開發"),
            satellite_allocations=[
                PromptAllocation(PromptCategory.INTELLIGENT, AllocationRole.SATELLITE, 15.0, "智能化"),
                PromptAllocation(PromptCategory.NEXT_GEN, AllocationRole.SATELLITE, 10.0, "下世代"),
            ],
            exploration_allocation=PromptAllocation(PromptCategory.HIGH_VALUE, AllocationRole.EXPLORATION, 5.0, "新興研究")
        )
        
        return presets
    
    def get_preset(self, name: str) -> Optional[CoreSatelliteConfiguration]:
        return self._presets.get(name)
    
    def list_presets(self) -> List[str]:
        return list(self._presets.keys())
    
    def recommend_configuration(self, company_stage: str, market_urgency: str, tech_focus: str) -> CoreSatelliteConfiguration:
        if company_stage == 'startup' and market_urgency == 'high':
            return self._presets['rapid_monetization']
        elif tech_focus == 'high':
            return self._presets['tech_leadership']
        return self._presets['steady_growth']
    
    def analyze_configuration(self, config: CoreSatelliteConfiguration) -> Dict:
        return {
            'name': config.name,
            'total_allocation': config.get_total_allocation(),
            'is_valid': config.is_valid(),
            'core_percentage': config.core_allocation.allocation_percentage,
            'satellite_count': len(config.satellite_allocations),
            'has_exploration': config.exploration_allocation is not None,
        }
