"""
商業分析模組 (Commercial Analytics Module)

提供商業導向的分析與追蹤功能：
- ROI 計算與追蹤
- 依賴項成本分析
- 技術債務量化
- 市場價值評估
- 資源配置優化建議

第二優先級：市場驗證階段 - 高市場回報應用開發
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import math


class CostCategory(Enum):
    """成本類別"""
    LICENSE = "license"              # 授權費用
    MAINTENANCE = "maintenance"      # 維護成本
    SECURITY = "security"            # 安全修復
    UPGRADE = "upgrade"              # 升級成本
    TRAINING = "training"            # 培訓成本
    DOWNTIME = "downtime"            # 停機損失
    COMPLIANCE = "compliance"        # 合規成本


class ValueCategory(Enum):
    """價值類別"""
    PRODUCTIVITY = "productivity"        # 生產力提升
    SECURITY_REDUCTION = "security"      # 安全風險降低
    COMPLIANCE_ASSURANCE = "compliance"  # 合規保障
    TIME_SAVING = "time_saving"          # 時間節省
    QUALITY_IMPROVEMENT = "quality"      # 品質提升


class TechDebtType(Enum):
    """技術債務類型"""
    OUTDATED_DEPENDENCY = "outdated"     # 過時依賴
    SECURITY_VULNERABILITY = "security"  # 安全漏洞
    LICENSE_RISK = "license"             # 授權風險
    DEPRECATED_API = "deprecated"        # 已棄用 API
    MISSING_TESTS = "tests"              # 缺少測試


@dataclass
class CostItem:
    """成本項目"""
    category: CostCategory
    amount: float
    currency: str = "USD"
    period: str = "monthly"  # monthly, yearly, one-time
    description: str = ""
    confidence: float = 0.8  # 估算信心度 0-1


@dataclass
class ValueItem:
    """價值項目"""
    category: ValueCategory
    amount: float
    currency: str = "USD"
    period: str = "monthly"
    description: str = ""
    confidence: float = 0.8


@dataclass
class TechDebtItem:
    """技術債務項目"""
    debt_type: TechDebtType
    dependency_name: str
    severity: str  # critical, high, medium, low
    estimated_fix_hours: float
    hourly_rate: float = 100.0
    interest_rate_monthly: float = 0.05  # 每月利息率
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def principal_cost(self) -> float:
        """本金成本"""
        return self.estimated_fix_hours * self.hourly_rate
    
    @property
    def accumulated_interest(self) -> float:
        """累計利息"""
        months = (datetime.now() - self.created_at).days / 30
        return self.principal_cost * (pow(1 + self.interest_rate_monthly, months) - 1)
    
    @property
    def total_debt(self) -> float:
        """總債務"""
        return self.principal_cost + self.accumulated_interest


@dataclass
class ROIAnalysis:
    """ROI 分析結果"""
    total_investment: float
    total_return: float
    roi_percentage: float
    payback_period_months: float
    net_present_value: float
    internal_rate_of_return: float
    break_even_point: Optional[datetime] = None
    confidence_level: float = 0.8
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class DependencyEconomics:
    """依賴項經濟分析"""
    dependency_name: str
    version: str
    total_cost: float
    total_value: float
    net_value: float
    cost_breakdown: List[CostItem] = field(default_factory=list)
    value_breakdown: List[ValueItem] = field(default_factory=list)
    tech_debt: List[TechDebtItem] = field(default_factory=list)
    recommendation: str = ""


class CommercialAnalytics:
    """
    商業分析引擎
    
    提供依賴管理的商業價值分析，包括：
    - ROI 計算
    - 成本效益分析
    - 技術債務量化
    - 投資優化建議
    """
    
    # 預設成本參數
    DEFAULT_COSTS = {
        CostCategory.MAINTENANCE: 50.0,      # 每月每依賴維護成本
        CostCategory.SECURITY: 500.0,        # 每個安全漏洞修復成本
        CostCategory.UPGRADE: 100.0,         # 每次升級成本
        CostCategory.DOWNTIME: 1000.0,       # 每小時停機成本
        CostCategory.COMPLIANCE: 200.0,      # 合規審查成本
    }
    
    # 預設價值參數
    DEFAULT_VALUES = {
        ValueCategory.PRODUCTIVITY: 200.0,       # 生產力提升價值/月
        ValueCategory.SECURITY_REDUCTION: 500.0, # 安全風險降低價值
        ValueCategory.TIME_SAVING: 150.0,        # 時間節省價值/月
    }
    
    def __init__(self, 
                 hourly_rate: float = 100.0,
                 discount_rate: float = 0.10):
        """
        初始化分析引擎
        
        Args:
            hourly_rate: 開發人員時薪
            discount_rate: 年折現率
        """
        self.hourly_rate = hourly_rate
        self.discount_rate = discount_rate
        self._cost_history: List[CostItem] = []
        self._value_history: List[ValueItem] = []
        self._tech_debt_registry: Dict[str, List[TechDebtItem]] = {}
    
    # ==================== ROI 分析 ====================
    
    def calculate_roi(self,
                     investment: float,
                     returns: List[float],
                     periods: int = 12) -> ROIAnalysis:
        """
        計算投資回報率
        
        Args:
            investment: 初始投資
            returns: 各期回報
            periods: 分析期數
            
        Returns:
            ROI 分析結果
        """
        total_return = sum(returns[:periods])
        roi = ((total_return - investment) / investment) * 100 if investment > 0 else 0
        
        # 回本期計算
        cumulative = 0
        payback_months = periods
        for i, ret in enumerate(returns):
            cumulative += ret
            if cumulative >= investment:
                payback_months = i + 1
                break
        
        # NPV 計算
        npv = -investment
        monthly_rate = self.discount_rate / 12
        for i, ret in enumerate(returns[:periods]):
            npv += ret / pow(1 + monthly_rate, i + 1)
        
        # IRR 近似計算
        irr = self._calculate_irr(investment, returns[:periods])
        
        # 損益平衡點
        if payback_months < periods:
            break_even = datetime.now() + timedelta(days=30 * payback_months)
        else:
            break_even = None
        
        return ROIAnalysis(
            total_investment=investment,
            total_return=total_return,
            roi_percentage=roi,
            payback_period_months=payback_months,
            net_present_value=npv,
            internal_rate_of_return=irr,
            break_even_point=break_even
        )
    
    def _calculate_irr(self, 
                       investment: float, 
                       cash_flows: List[float],
                       precision: float = 0.0001) -> float:
        """計算內部收益率"""
        flows = [-investment] + cash_flows
        
        low, high = -0.99, 10.0
        while high - low > precision:
            mid = (low + high) / 2
            npv = sum(cf / pow(1 + mid, i) for i, cf in enumerate(flows))
            if npv > 0:
                low = mid
            else:
                high = mid
        
        return (low + high) / 2 * 12  # 年化
    
    # ==================== 成本分析 ====================
    
    def analyze_dependency_cost(self,
                               dependency_name: str,
                               version: str,
                               is_outdated: bool = False,
                               has_vulnerabilities: int = 0,
                               has_license_risk: bool = False,
                               monthly_maintenance_hours: float = 1.0) -> List[CostItem]:
        """
        分析依賴項成本
        
        Args:
            dependency_name: 依賴名稱
            version: 版本
            is_outdated: 是否過時
            has_vulnerabilities: 漏洞數量
            has_license_risk: 是否有授權風險
            monthly_maintenance_hours: 每月維護時數
            
        Returns:
            成本項目列表
        """
        costs = []
        
        # 基本維護成本
        costs.append(CostItem(
            category=CostCategory.MAINTENANCE,
            amount=monthly_maintenance_hours * self.hourly_rate,
            description=f"{dependency_name} 每月維護成本",
            confidence=0.9
        ))
        
        # 過時升級成本
        if is_outdated:
            costs.append(CostItem(
                category=CostCategory.UPGRADE,
                amount=self.DEFAULT_COSTS[CostCategory.UPGRADE],
                period="one-time",
                description=f"{dependency_name} 升級成本",
                confidence=0.7
            ))
        
        # 安全修復成本
        if has_vulnerabilities > 0:
            costs.append(CostItem(
                category=CostCategory.SECURITY,
                amount=has_vulnerabilities * self.DEFAULT_COSTS[CostCategory.SECURITY],
                period="one-time",
                description=f"{dependency_name} 安全修復成本 ({has_vulnerabilities} 個漏洞)",
                confidence=0.8
            ))
        
        # 合規風險成本
        if has_license_risk:
            costs.append(CostItem(
                category=CostCategory.COMPLIANCE,
                amount=self.DEFAULT_COSTS[CostCategory.COMPLIANCE],
                period="one-time",
                description=f"{dependency_name} 授權合規審查成本",
                confidence=0.6
            ))
        
        return costs
    
    # ==================== 技術債務 ====================
    
    def register_tech_debt(self, item: TechDebtItem) -> None:
        """
        註冊技術債務
        
        Args:
            item: 技術債務項目
        """
        if item.dependency_name not in self._tech_debt_registry:
            self._tech_debt_registry[item.dependency_name] = []
        self._tech_debt_registry[item.dependency_name].append(item)
    
    def get_tech_debt_summary(self) -> Dict[str, Any]:
        """
        取得技術債務摘要
        
        Returns:
            債務摘要
        """
        total_principal = 0
        total_interest = 0
        total_debt = 0
        by_type: Dict[str, float] = {}
        by_severity: Dict[str, float] = {}
        
        for dep_items in self._tech_debt_registry.values():
            for item in dep_items:
                total_principal += item.principal_cost
                total_interest += item.accumulated_interest
                total_debt += item.total_debt
                
                type_key = item.debt_type.value
                by_type[type_key] = by_type.get(type_key, 0) + item.total_debt
                
                by_severity[item.severity] = by_severity.get(item.severity, 0) + item.total_debt
        
        return {
            "total_principal": total_principal,
            "total_interest": total_interest,
            "total_debt": total_debt,
            "debt_by_type": by_type,
            "debt_by_severity": by_severity,
            "affected_dependencies": len(self._tech_debt_registry)
        }
    
    def calculate_debt_payoff_plan(self,
                                  monthly_budget: float,
                                  strategy: str = "highest_interest") -> List[Dict[str, Any]]:
        """
        計算債務還清計畫
        
        Args:
            monthly_budget: 每月預算
            strategy: 還款策略 (highest_interest, highest_debt, critical_first)
            
        Returns:
            還款計畫
        """
        # 展平所有債務
        all_debts = []
        for dep_items in self._tech_debt_registry.values():
            all_debts.extend(dep_items)
        
        if not all_debts:
            return []
        
        # 排序策略
        if strategy == "highest_interest":
            all_debts.sort(key=lambda x: x.interest_rate_monthly, reverse=True)
        elif strategy == "highest_debt":
            all_debts.sort(key=lambda x: x.total_debt, reverse=True)
        elif strategy == "critical_first":
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            all_debts.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        # 生成還款計畫
        plan = []
        remaining_budget = monthly_budget
        current_month = 1
        
        for debt in all_debts:
            months_to_pay = math.ceil(debt.total_debt / monthly_budget)
            plan.append({
                "dependency": debt.dependency_name,
                "debt_type": debt.debt_type.value,
                "severity": debt.severity,
                "amount": debt.total_debt,
                "start_month": current_month,
                "end_month": current_month + months_to_pay - 1,
                "monthly_payment": min(monthly_budget, debt.total_debt)
            })
            current_month += months_to_pay
        
        return plan
    
    # ==================== 價值分析 ====================
    
    def analyze_automation_value(self,
                                dependencies_count: int,
                                monthly_manual_hours: float,
                                error_rate_reduction: float = 0.5,
                                security_improvement: float = 0.3) -> List[ValueItem]:
        """
        分析自動化價值
        
        Args:
            dependencies_count: 依賴項數量
            monthly_manual_hours: 手動管理時數/月
            error_rate_reduction: 錯誤率降低比例
            security_improvement: 安全改善比例
            
        Returns:
            價值項目列表
        """
        values = []
        
        # 時間節省
        time_saved_hours = monthly_manual_hours * 0.8  # 假設自動化節省 80%
        values.append(ValueItem(
            category=ValueCategory.TIME_SAVING,
            amount=time_saved_hours * self.hourly_rate,
            description=f"每月節省 {time_saved_hours:.1f} 小時人工作業",
            confidence=0.85
        ))
        
        # 生產力提升
        productivity_gain = dependencies_count * self.DEFAULT_VALUES[ValueCategory.PRODUCTIVITY] / 10
        values.append(ValueItem(
            category=ValueCategory.PRODUCTIVITY,
            amount=productivity_gain,
            description="依賴管理自動化帶來的生產力提升",
            confidence=0.7
        ))
        
        # 安全風險降低
        security_value = dependencies_count * self.DEFAULT_VALUES[ValueCategory.SECURITY_REDUCTION] * security_improvement
        values.append(ValueItem(
            category=ValueCategory.SECURITY_REDUCTION,
            amount=security_value,
            period="yearly",
            description=f"安全風險降低 {security_improvement*100:.0f}%",
            confidence=0.6
        ))
        
        return values
    
    # ==================== 綜合分析 ====================
    
    def comprehensive_analysis(self,
                              dependencies: List[Dict[str, Any]],
                              automation_hours_saved: float = 20.0) -> Dict[str, Any]:
        """
        綜合商業分析
        
        Args:
            dependencies: 依賴項列表
            automation_hours_saved: 自動化節省時數/月
            
        Returns:
            綜合分析結果
        """
        total_costs: List[CostItem] = []
        total_values: List[ValueItem] = []
        dependency_analyses: List[DependencyEconomics] = []
        
        for dep in dependencies:
            # 分析每個依賴的成本
            costs = self.analyze_dependency_cost(
                dependency_name=dep.get("name", "unknown"),
                version=dep.get("version", "0.0.0"),
                is_outdated=dep.get("outdated", False),
                has_vulnerabilities=dep.get("vulnerabilities", 0),
                has_license_risk=dep.get("license_risk", False)
            )
            total_costs.extend(costs)
            
            # 建立技術債務
            if dep.get("outdated") or dep.get("vulnerabilities", 0) > 0:
                debt_items = []
                if dep.get("outdated"):
                    debt = TechDebtItem(
                        debt_type=TechDebtType.OUTDATED_DEPENDENCY,
                        dependency_name=dep.get("name", "unknown"),
                        severity="medium",
                        estimated_fix_hours=2.0,
                        hourly_rate=self.hourly_rate
                    )
                    self.register_tech_debt(debt)
                    debt_items.append(debt)
                
                if dep.get("vulnerabilities", 0) > 0:
                    severity = "critical" if dep.get("vulnerabilities", 0) >= 3 else "high"
                    debt = TechDebtItem(
                        debt_type=TechDebtType.SECURITY_VULNERABILITY,
                        dependency_name=dep.get("name", "unknown"),
                        severity=severity,
                        estimated_fix_hours=dep.get("vulnerabilities", 0) * 4.0,
                        hourly_rate=self.hourly_rate
                    )
                    self.register_tech_debt(debt)
                    debt_items.append(debt)
            
            # 個別依賴經濟分析
            dep_cost = sum(c.amount for c in costs)
            dep_value = 50.0  # 基本價值
            
            dependency_analyses.append(DependencyEconomics(
                dependency_name=dep.get("name", "unknown"),
                version=dep.get("version", "0.0.0"),
                total_cost=dep_cost,
                total_value=dep_value,
                net_value=dep_value - dep_cost,
                cost_breakdown=costs
            ))
        
        # 分析自動化價值
        automation_values = self.analyze_automation_value(
            dependencies_count=len(dependencies),
            monthly_manual_hours=automation_hours_saved
        )
        total_values.extend(automation_values)
        
        # 計算 ROI
        monthly_cost = sum(c.amount for c in total_costs if c.period == "monthly")
        one_time_cost = sum(c.amount for c in total_costs if c.period == "one-time")
        monthly_value = sum(v.amount for v in total_values if v.period == "monthly")
        
        investment = one_time_cost + monthly_cost * 3  # 3個月成本作為投資
        returns = [monthly_value] * 12
        roi_analysis = self.calculate_roi(investment, returns)
        
        # 技術債務摘要
        debt_summary = self.get_tech_debt_summary()
        
        return {
            "summary": {
                "total_dependencies": len(dependencies),
                "total_monthly_cost": monthly_cost,
                "total_one_time_cost": one_time_cost,
                "total_monthly_value": monthly_value,
                "net_monthly_benefit": monthly_value - monthly_cost
            },
            "roi_analysis": {
                "investment": roi_analysis.total_investment,
                "total_return": roi_analysis.total_return,
                "roi_percentage": roi_analysis.roi_percentage,
                "payback_months": roi_analysis.payback_period_months,
                "npv": roi_analysis.net_present_value,
                "irr": roi_analysis.internal_rate_of_return
            },
            "tech_debt": debt_summary,
            "dependency_economics": [
                {
                    "name": d.dependency_name,
                    "version": d.version,
                    "cost": d.total_cost,
                    "value": d.total_value,
                    "net": d.net_value
                }
                for d in dependency_analyses
            ],
            "recommendations": self._generate_recommendations(
                roi_analysis, debt_summary, dependency_analyses
            )
        }
    
    def _generate_recommendations(self,
                                 roi: ROIAnalysis,
                                 debt: Dict[str, Any],
                                 deps: List[DependencyEconomics]) -> List[str]:
        """生成建議"""
        recommendations = []
        
        if roi.roi_percentage < 0:
            recommendations.append("⚠️ 目前投資回報為負，建議重新評估依賴管理策略")
        elif roi.roi_percentage > 100:
            recommendations.append("✅ 投資回報優良，建議持續投入自動化")
        
        if debt.get("total_debt", 0) > 10000:
            recommendations.append("🔴 技術債務過高，建議優先處理高風險項目")
        
        negative_deps = [d for d in deps if d.net_value < 0]
        if negative_deps:
            names = ", ".join(d.dependency_name for d in negative_deps[:3])
            recommendations.append(f"💡 建議評估以下負價值依賴：{names}")
        
        if debt.get("debt_by_severity", {}).get("critical", 0) > 0:
            recommendations.append("🚨 存在關鍵級技術債務，需立即處理")
        
        return recommendations
    
    # ==================== 報告生成 ====================
    
    def format_report_zh_tw(self, analysis: Dict[str, Any]) -> str:
        """
        生成繁體中文報告
        
        Args:
            analysis: 分析結果
            
        Returns:
            格式化報告
        """
        lines = [
            "=" * 60,
            "📊 商業分析報告 - 依賴管理 ROI 分析",
            "=" * 60,
            "",
            "📈 摘要",
            "-" * 40,
            f"  依賴項總數：{analysis['summary']['total_dependencies']}",
            f"  每月成本：${analysis['summary']['total_monthly_cost']:,.2f}",
            f"  一次性成本：${analysis['summary']['total_one_time_cost']:,.2f}",
            f"  每月價值：${analysis['summary']['total_monthly_value']:,.2f}",
            f"  淨月收益：${analysis['summary']['net_monthly_benefit']:,.2f}",
            "",
            "💰 ROI 分析",
            "-" * 40,
            f"  總投資：${analysis['roi_analysis']['investment']:,.2f}",
            f"  總回報：${analysis['roi_analysis']['total_return']:,.2f}",
            f"  ROI：{analysis['roi_analysis']['roi_percentage']:.1f}%",
            f"  回本期：{analysis['roi_analysis']['payback_months']:.1f} 個月",
            f"  淨現值 (NPV)：${analysis['roi_analysis']['npv']:,.2f}",
            f"  內部收益率 (IRR)：{analysis['roi_analysis']['irr']*100:.1f}%",
            "",
            "🔧 技術債務",
            "-" * 40,
            f"  總債務：${analysis['tech_debt']['total_debt']:,.2f}",
            f"  本金：${analysis['tech_debt']['total_principal']:,.2f}",
            f"  累計利息：${analysis['tech_debt']['total_interest']:,.2f}",
            f"  受影響依賴：{analysis['tech_debt']['affected_dependencies']} 個",
            "",
            "💡 建議",
            "-" * 40,
        ]
        
        for rec in analysis.get("recommendations", []):
            lines.append(f"  {rec}")
        
        lines.extend(["", "=" * 60])
        
        return "\n".join(lines)
