# -*- coding: utf-8 -*-
"""
成功指標追蹤器 (Success Metrics Tracker)

提供技術、商業和組織指標的追蹤與分析功能。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Callable
import statistics


class MetricCategory(Enum):
    """指標類別"""
    TECHNICAL = "technical"
    BUSINESS = "business"
    ORGANIZATIONAL = "organizational"


class MetricTrend(Enum):
    """指標趨勢"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class MetricStatus(Enum):
    """指標狀態"""
    ON_TARGET = "on_target"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricDataPoint:
    """指標數據點"""
    value: float
    timestamp: datetime
    notes: str = ""


@dataclass
class TechnicalMetric:
    """技術指標"""
    id: str
    name: str
    description: str
    unit: str
    target_value: float
    warning_threshold: float  # 低於此值為警告
    critical_threshold: float  # 低於此值為危險
    higher_is_better: bool = True
    data_points: List[MetricDataPoint] = field(default_factory=list)
    
    def add_data_point(self, value: float, notes: str = "") -> None:
        """添加數據點"""
        self.data_points.append(MetricDataPoint(
            value=value,
            timestamp=datetime.now(),
            notes=notes
        ))
    
    def current_value(self) -> Optional[float]:
        """獲取當前值"""
        if not self.data_points:
            return None
        return self.data_points[-1].value
    
    def get_status(self) -> MetricStatus:
        """獲取指標狀態"""
        value = self.current_value()
        if value is None:
            return MetricStatus.WARNING
        
        if self.higher_is_better:
            if value >= self.target_value:
                return MetricStatus.ON_TARGET
            elif value >= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
        else:
            if value <= self.target_value:
                return MetricStatus.ON_TARGET
            elif value <= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
    
    def get_trend(self, periods: int = 5) -> MetricTrend:
        """獲取趨勢"""
        if len(self.data_points) < 2:
            return MetricTrend.STABLE
        
        recent = [dp.value for dp in self.data_points[-periods:]]
        if len(recent) < 2:
            return MetricTrend.STABLE
        
        avg_first = statistics.mean(recent[:len(recent)//2])
        avg_second = statistics.mean(recent[len(recent)//2:])
        
        threshold = 0.05  # 5% 變化閾值
        if avg_second > avg_first * (1 + threshold):
            return MetricTrend.UP
        elif avg_second < avg_first * (1 - threshold):
            return MetricTrend.DOWN
        else:
            return MetricTrend.STABLE
    
    def achievement_rate(self) -> float:
        """計算達成率"""
        value = self.current_value()
        if value is None or self.target_value == 0:
            return 0.0
        
        if self.higher_is_better:
            return min(100.0, (value / self.target_value) * 100)
        else:
            if value == 0:
                return 100.0
            return min(100.0, (self.target_value / value) * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'unit': self.unit,
            'target_value': self.target_value,
            'current_value': self.current_value(),
            'status': self.get_status().value,
            'trend': self.get_trend().value,
            'achievement_rate': self.achievement_rate(),
            'data_points_count': len(self.data_points)
        }


@dataclass
class BusinessMetric:
    """商業指標"""
    id: str
    name: str
    description: str
    unit: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    higher_is_better: bool = True
    data_points: List[MetricDataPoint] = field(default_factory=list)
    
    def add_data_point(self, value: float, notes: str = "") -> None:
        """添加數據點"""
        self.data_points.append(MetricDataPoint(
            value=value,
            timestamp=datetime.now(),
            notes=notes
        ))
    
    def current_value(self) -> Optional[float]:
        """獲取當前值"""
        if not self.data_points:
            return None
        return self.data_points[-1].value
    
    def get_status(self) -> MetricStatus:
        """獲取指標狀態"""
        value = self.current_value()
        if value is None:
            return MetricStatus.WARNING
        
        if self.higher_is_better:
            if value >= self.target_value:
                return MetricStatus.ON_TARGET
            elif value >= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
        else:
            if value <= self.target_value:
                return MetricStatus.ON_TARGET
            elif value <= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
    
    def get_trend(self, periods: int = 5) -> MetricTrend:
        """獲取趨勢"""
        if len(self.data_points) < 2:
            return MetricTrend.STABLE
        
        recent = [dp.value for dp in self.data_points[-periods:]]
        if len(recent) < 2:
            return MetricTrend.STABLE
        
        avg_first = statistics.mean(recent[:len(recent)//2])
        avg_second = statistics.mean(recent[len(recent)//2:])
        
        threshold = 0.05
        if avg_second > avg_first * (1 + threshold):
            return MetricTrend.UP
        elif avg_second < avg_first * (1 - threshold):
            return MetricTrend.DOWN
        else:
            return MetricTrend.STABLE
    
    def growth_rate(self) -> Optional[float]:
        """計算增長率"""
        if len(self.data_points) < 2:
            return None
        first_value = self.data_points[0].value
        last_value = self.data_points[-1].value
        if first_value == 0:
            return None
        return ((last_value - first_value) / first_value) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'unit': self.unit,
            'target_value': self.target_value,
            'current_value': self.current_value(),
            'status': self.get_status().value,
            'trend': self.get_trend().value,
            'growth_rate': self.growth_rate(),
            'data_points_count': len(self.data_points)
        }


@dataclass
class OrganizationalMetric:
    """組織指標"""
    id: str
    name: str
    description: str
    unit: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    higher_is_better: bool = True
    data_points: List[MetricDataPoint] = field(default_factory=list)
    
    def add_data_point(self, value: float, notes: str = "") -> None:
        """添加數據點"""
        self.data_points.append(MetricDataPoint(
            value=value,
            timestamp=datetime.now(),
            notes=notes
        ))
    
    def current_value(self) -> Optional[float]:
        """獲取當前值"""
        if not self.data_points:
            return None
        return self.data_points[-1].value
    
    def get_status(self) -> MetricStatus:
        """獲取指標狀態"""
        value = self.current_value()
        if value is None:
            return MetricStatus.WARNING
        
        if self.higher_is_better:
            if value >= self.target_value:
                return MetricStatus.ON_TARGET
            elif value >= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
        else:
            if value <= self.target_value:
                return MetricStatus.ON_TARGET
            elif value <= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'unit': self.unit,
            'target_value': self.target_value,
            'current_value': self.current_value(),
            'status': self.get_status().value,
            'data_points_count': len(self.data_points)
        }


class SuccessMetricsTracker:
    """成功指標追蹤器"""
    
    def __init__(self):
        """初始化追蹤器"""
        self.technical_metrics: Dict[str, TechnicalMetric] = {}
        self.business_metrics: Dict[str, BusinessMetric] = {}
        self.organizational_metrics: Dict[str, OrganizationalMetric] = {}
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self) -> None:
        """初始化預設指標"""
        # 技術指標
        self.add_technical_metric(TechnicalMetric(
            id="code_quality",
            name="代碼品質分數",
            description="基於靜態分析的代碼品質評分",
            unit="分",
            target_value=85,
            warning_threshold=70,
            critical_threshold=60,
            higher_is_better=True
        ))
        
        self.add_technical_metric(TechnicalMetric(
            id="performance",
            name="系統性能指標",
            description="平均響應時間（毫秒）",
            unit="ms",
            target_value=200,
            warning_threshold=500,
            critical_threshold=1000,
            higher_is_better=False
        ))
        
        self.add_technical_metric(TechnicalMetric(
            id="tech_debt_ratio",
            name="技術債務比率",
            description="技術債務佔總代碼量的比例",
            unit="%",
            target_value=5,
            warning_threshold=10,
            critical_threshold=20,
            higher_is_better=False
        ))
        
        self.add_technical_metric(TechnicalMetric(
            id="test_coverage",
            name="測試覆蓋率",
            description="自動化測試覆蓋的代碼比例",
            unit="%",
            target_value=80,
            warning_threshold=60,
            critical_threshold=40,
            higher_is_better=True
        ))
        
        # 商業指標
        self.add_business_metric(BusinessMetric(
            id="cac",
            name="用戶獲取成本 (CAC)",
            description="獲取單個新用戶的平均成本",
            unit="USD",
            target_value=50,
            warning_threshold=75,
            critical_threshold=100,
            higher_is_better=False
        ))
        
        self.add_business_metric(BusinessMetric(
            id="ltv",
            name="客戶生命週期價值 (LTV)",
            description="單個客戶預期帶來的總收入",
            unit="USD",
            target_value=500,
            warning_threshold=300,
            critical_threshold=200,
            higher_is_better=True
        ))
        
        self.add_business_metric(BusinessMetric(
            id="mrr_growth",
            name="月度經常性收入成長率",
            description="MRR 月度增長百分比",
            unit="%",
            target_value=10,
            warning_threshold=5,
            critical_threshold=0,
            higher_is_better=True
        ))
        
        self.add_business_metric(BusinessMetric(
            id="ltv_cac_ratio",
            name="LTV/CAC 比率",
            description="客戶生命週期價值與獲取成本的比率",
            unit="x",
            target_value=3.0,
            warning_threshold=2.0,
            critical_threshold=1.0,
            higher_is_better=True
        ))
        
        # 組織指標
        self.add_organizational_metric(OrganizationalMetric(
            id="productivity",
            name="團隊生產力指數",
            description="每個開發者每週完成的故事點",
            unit="點/人/週",
            target_value=15,
            warning_threshold=10,
            critical_threshold=5,
            higher_is_better=True
        ))
        
        self.add_organizational_metric(OrganizationalMetric(
            id="skill_growth",
            name="員工技能成長曲線",
            description="技能評估分數的月度增長",
            unit="%",
            target_value=5,
            warning_threshold=2,
            critical_threshold=0,
            higher_is_better=True
        ))
        
        self.add_organizational_metric(OrganizationalMetric(
            id="innovation_success",
            name="創新項目成功率",
            description="成功交付的創新項目佔比",
            unit="%",
            target_value=70,
            warning_threshold=50,
            critical_threshold=30,
            higher_is_better=True
        ))
        
        self.add_organizational_metric(OrganizationalMetric(
            id="employee_satisfaction",
            name="員工滿意度",
            description="員工滿意度調查分數",
            unit="分",
            target_value=4.0,
            warning_threshold=3.5,
            critical_threshold=3.0,
            higher_is_better=True
        ))
    
    def add_technical_metric(self, metric: TechnicalMetric) -> None:
        """添加技術指標"""
        self.technical_metrics[metric.id] = metric
    
    def add_business_metric(self, metric: BusinessMetric) -> None:
        """添加商業指標"""
        self.business_metrics[metric.id] = metric
    
    def add_organizational_metric(self, metric: OrganizationalMetric) -> None:
        """添加組織指標"""
        self.organizational_metrics[metric.id] = metric
    
    def record_value(self, category: MetricCategory, metric_id: str, value: float, notes: str = "") -> bool:
        """記錄指標值"""
        if category == MetricCategory.TECHNICAL:
            if metric_id in self.technical_metrics:
                self.technical_metrics[metric_id].add_data_point(value, notes)
                return True
        elif category == MetricCategory.BUSINESS:
            if metric_id in self.business_metrics:
                self.business_metrics[metric_id].add_data_point(value, notes)
                return True
        elif category == MetricCategory.ORGANIZATIONAL:
            if metric_id in self.organizational_metrics:
                self.organizational_metrics[metric_id].add_data_point(value, notes)
                return True
        return False
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """獲取儀表板摘要"""
        def count_by_status(metrics: Dict) -> Dict[str, int]:
            status_counts = {s.value: 0 for s in MetricStatus}
            for m in metrics.values():
                status = m.get_status()
                status_counts[status.value] += 1
            return status_counts
        
        return {
            'technical': {
                'total': len(self.technical_metrics),
                'by_status': count_by_status(self.technical_metrics),
                'metrics': [m.to_dict() for m in self.technical_metrics.values()]
            },
            'business': {
                'total': len(self.business_metrics),
                'by_status': count_by_status(self.business_metrics),
                'metrics': [m.to_dict() for m in self.business_metrics.values()]
            },
            'organizational': {
                'total': len(self.organizational_metrics),
                'by_status': count_by_status(self.organizational_metrics),
                'metrics': [m.to_dict() for m in self.organizational_metrics.values()]
            }
        }
    
    def get_critical_metrics(self) -> List[Dict[str, Any]]:
        """獲取危險狀態的指標"""
        critical = []
        
        for m in self.technical_metrics.values():
            if m.get_status() == MetricStatus.CRITICAL:
                critical.append({
                    'category': 'technical',
                    **m.to_dict()
                })
        
        for m in self.business_metrics.values():
            if m.get_status() == MetricStatus.CRITICAL:
                critical.append({
                    'category': 'business',
                    **m.to_dict()
                })
        
        for m in self.organizational_metrics.values():
            if m.get_status() == MetricStatus.CRITICAL:
                critical.append({
                    'category': 'organizational',
                    **m.to_dict()
                })
        
        return critical
    
    def generate_report(self, format_type: str = "markdown") -> str:
        """生成指標報告"""
        if format_type == "markdown":
            return self._generate_markdown_report()
        else:
            return self._generate_text_report()
    
    def _generate_markdown_report(self) -> str:
        """生成 Markdown 格式報告"""
        lines = [
            "# 成功指標追蹤報告",
            "",
            f"**生成時間：** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## 技術指標",
            "",
            "| 指標 | 目標 | 當前值 | 狀態 | 趨勢 |",
            "|------|------|--------|------|------|"
        ]
        
        for m in self.technical_metrics.values():
            status_icon = {"on_target": "✅", "warning": "⚠️", "critical": "❌"}[m.get_status().value]
            trend_icon = {"up": "📈", "down": "📉", "stable": "➡️"}[m.get_trend().value]
            current = m.current_value()
            current_str = f"{current:.1f}" if current is not None else "N/A"
            lines.append(f"| {m.name} | {m.target_value} {m.unit} | {current_str} {m.unit} | {status_icon} | {trend_icon} |")
        
        lines.extend([
            "",
            "## 商業指標",
            "",
            "| 指標 | 目標 | 當前值 | 狀態 | 增長率 |",
            "|------|------|--------|------|--------|"
        ])
        
        for m in self.business_metrics.values():
            status_icon = {"on_target": "✅", "warning": "⚠️", "critical": "❌"}[m.get_status().value]
            current = m.current_value()
            current_str = f"{current:.1f}" if current is not None else "N/A"
            growth = m.growth_rate()
            growth_str = f"{growth:+.1f}%" if growth is not None else "N/A"
            lines.append(f"| {m.name} | {m.target_value} {m.unit} | {current_str} {m.unit} | {status_icon} | {growth_str} |")
        
        lines.extend([
            "",
            "## 組織指標",
            "",
            "| 指標 | 目標 | 當前值 | 狀態 |",
            "|------|------|--------|------|"
        ])
        
        for m in self.organizational_metrics.values():
            status_icon = {"on_target": "✅", "warning": "⚠️", "critical": "❌"}[m.get_status().value]
            current = m.current_value()
            current_str = f"{current:.1f}" if current is not None else "N/A"
            lines.append(f"| {m.name} | {m.target_value} {m.unit} | {current_str} {m.unit} | {status_icon} |")
        
        return "\n".join(lines)
    
    def _generate_text_report(self) -> str:
        """生成純文字格式報告"""
        lines = [
            "成功指標追蹤報告",
            "=" * 50,
            f"生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "技術指標：",
            "-" * 30
        ]
        
        for m in self.technical_metrics.values():
            current = m.current_value()
            current_str = f"{current:.1f}" if current is not None else "N/A"
            lines.append(f"  {m.name}: {current_str}/{m.target_value} {m.unit} [{m.get_status().value}]")
        
        lines.extend([
            "",
            "商業指標：",
            "-" * 30
        ])
        
        for m in self.business_metrics.values():
            current = m.current_value()
            current_str = f"{current:.1f}" if current is not None else "N/A"
            lines.append(f"  {m.name}: {current_str}/{m.target_value} {m.unit} [{m.get_status().value}]")
        
        lines.extend([
            "",
            "組織指標：",
            "-" * 30
        ])
        
        for m in self.organizational_metrics.values():
            current = m.current_value()
            current_str = f"{current:.1f}" if current is not None else "N/A"
            lines.append(f"  {m.name}: {current_str}/{m.target_value} {m.unit} [{m.get_status().value}]")
        
        return "\n".join(lines)
