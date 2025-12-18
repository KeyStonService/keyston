# -*- coding: utf-8 -*-
"""
動態調整機制
Dynamic Adjustment Mechanism
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class AdjustmentTrigger(Enum):
    KPI_DEVIATION = "kpi_deviation"
    MARKET_CHANGE = "market_change"
    TECH_BREAKTHROUGH = "tech_breakthrough"
    RESOURCE_CONSTRAINT = "resource_constraint"


class AdjustmentDirection(Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"
    PIVOT = "pivot"


@dataclass
class KPIMetric:
    name: str
    target: float
    actual: float
    unit: str = ""
    
    @property
    def deviation(self) -> float:
        return (self.actual - self.target) / self.target * 100 if self.target else 0
    
    @property
    def is_on_track(self) -> bool:
        return abs(self.deviation) <= 20


@dataclass
class AdjustmentRecommendation:
    trigger: AdjustmentTrigger
    prompt_category: str
    direction: AdjustmentDirection
    adjustment_percentage: float
    reason: str
    priority: int
    confidence: float


class DynamicAdjuster:
    """動態調整器"""
    
    def __init__(self):
        self._kpis: Dict[str, KPIMetric] = {}
        self._current_allocation: Dict[str, float] = {}
        self._thresholds = {'kpi_deviation': 20.0, 'market_change': 30.0}
    
    def set_allocation(self, allocation: Dict[str, float]):
        self._current_allocation = allocation.copy()
    
    def register_kpi(self, name: str, target: float, actual: float, unit: str = ""):
        self._kpis[name] = KPIMetric(name, target, actual, unit)
    
    def analyze_kpis(self) -> Dict:
        if not self._kpis:
            return {'status': 'no_kpis'}
        
        metrics = [{'name': k.name, 'deviation': k.deviation, 'on_track': k.is_on_track} for k in self._kpis.values()]
        avg_dev = sum(abs(m['deviation']) for m in metrics) / len(metrics)
        
        return {
            'metrics': metrics,
            'overall_deviation': avg_dev,
            'trigger_adjustment': avg_dev > self._thresholds['kpi_deviation'],
            'on_track_ratio': sum(1 for m in metrics if m['on_track']) / len(metrics),
        }
    
    def evaluate_market(self, satisfaction: float, competitor_moves: List[str], trends: List[str]) -> Dict:
        severity = (60 - satisfaction) / 2 if satisfaction < 60 else 0
        severity += len(competitor_moves) * 5 + len(trends) * 8
        
        return {
            'satisfaction': satisfaction,
            'severity_score': min(severity, 100),
            'trigger_adjustment': severity >= self._thresholds['market_change'],
        }
    
    def generate_recommendations(self, kpi: Dict, market: Dict, financial: Dict) -> List[AdjustmentRecommendation]:
        recs = []
        if kpi.get('trigger_adjustment'):
            recs.append(AdjustmentRecommendation(
                AdjustmentTrigger.KPI_DEVIATION, 'core',
                AdjustmentDirection.INCREASE if kpi['overall_deviation'] < 0 else AdjustmentDirection.DECREASE,
                10.0, f"KPI偏差 {kpi['overall_deviation']:.1f}%", 1, 0.85
            ))
        if market.get('trigger_adjustment'):
            recs.append(AdjustmentRecommendation(
                AdjustmentTrigger.MARKET_CHANGE, 'satellite',
                AdjustmentDirection.PIVOT if market['severity_score'] > 50 else AdjustmentDirection.INCREASE,
                10.0, f"市場變化 {market['severity_score']:.1f}", 2, 0.75
            ))
        return sorted(recs, key=lambda x: x.priority)
