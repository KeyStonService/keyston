"""
資源優化器 - 預算與團隊配置優化

此模組提供：
- 預算分配優化
- 團隊配置建議
- 投資組合分析
- ROI 預測

Copyright (c) 2024 SynergyMesh
MIT License
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ResourceType(Enum):
    """資源類型"""
    BUDGET = "預算"
    HEADCOUNT = "人力"
    TIME = "時間"
    TECHNOLOGY = "技術"


class AllocationStrategy(Enum):
    """分配策略"""
    BALANCED = "平衡分配"
    GROWTH_FOCUSED = "增長導向"
    EFFICIENCY_FOCUSED = "效率導向"
    INNOVATION_FOCUSED = "創新導向"
    RISK_AVERSE = "風險規避"


@dataclass
class BudgetCategory:
    """預算類別"""
    name: str
    amount: float
    priority: int  # 1-5, 1 最高
    flexibility: float  # 0-1, 可調整程度
    roi_multiplier: float  # 預期投資回報倍數

    def get_effective_value(self) -> float:
        """計算有效價值"""
        return self.amount * self.roi_multiplier * (6 - self.priority) / 5


@dataclass
class BudgetAllocation:
    """預算分配方案"""
    total_budget: float
    allocations: dict[str, BudgetCategory]
    strategy: AllocationStrategy
    optimization_score: float  # 優化分數 0-100
    notes: list[str]

    def get_summary(self) -> dict[str, float]:
        """獲取分配摘要"""
        return {
            name: cat.amount
            for name, cat in self.allocations.items()
        }

    def get_by_priority(self, priority: int) -> list[str]:
        """根據優先級獲取類別"""
        return [
            name for name, cat in self.allocations.items()
            if cat.priority == priority
        ]

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'total_budget': self.total_budget,
            'allocations': {
                name: {
                    'amount': cat.amount,
                    'percentage': cat.amount / self.total_budget * 100,
                    'priority': cat.priority,
                    'flexibility': cat.flexibility,
                    'roi_multiplier': cat.roi_multiplier
                }
                for name, cat in self.allocations.items()
            },
            'strategy': self.strategy.value,
            'optimization_score': self.optimization_score,
            'notes': self.notes
        }


@dataclass
class TeamRole:
    """團隊角色"""
    role_name: str
    headcount: int
    cost_per_person: float
    skill_requirements: list[str]
    criticality: str  # critical, important, nice_to_have

    def get_total_cost(self) -> float:
        """計算總成本"""
        return self.headcount * self.cost_per_person


@dataclass
class TeamAllocation:
    """團隊配置方案"""
    total_headcount: int
    total_cost: float
    roles: dict[str, TeamRole]
    structure: str  # flat, hierarchical, matrix
    optimization_score: float
    hiring_plan: list[dict[str, Any]]

    def get_by_criticality(self, criticality: str) -> list[str]:
        """根據關鍵度獲取角色"""
        return [
            name for name, role in self.roles.items()
            if role.criticality == criticality
        ]

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'total_headcount': self.total_headcount,
            'total_cost': self.total_cost,
            'roles': {
                name: {
                    'headcount': role.headcount,
                    'cost_per_person': role.cost_per_person,
                    'total_cost': role.get_total_cost(),
                    'skill_requirements': role.skill_requirements,
                    'criticality': role.criticality
                }
                for name, role in self.roles.items()
            },
            'structure': self.structure,
            'optimization_score': self.optimization_score,
            'hiring_plan': self.hiring_plan
        }


@dataclass
class OptimizationResult:
    """優化結果"""
    budget_allocation: BudgetAllocation
    team_allocation: TeamAllocation
    projected_roi: float
    payback_months: int
    risk_score: float  # 0-100
    confidence: float  # 0-100
    sensitivity_analysis: dict[str, Any]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'budget_allocation': self.budget_allocation.to_dict(),
            'team_allocation': self.team_allocation.to_dict(),
            'projected_roi': self.projected_roi,
            'payback_months': self.payback_months,
            'risk_score': self.risk_score,
            'confidence': self.confidence,
            'sensitivity_analysis': self.sensitivity_analysis,
            'recommendations': self.recommendations
        }


class ResourceOptimizer:
    """
    資源優化器
    
    提供：
    - 預算分配優化
    - 團隊配置優化
    - 投資組合分析
    - ROI 預測
    """

    # 預設預算分配模板
    BUDGET_TEMPLATES = {
        AllocationStrategy.BALANCED: {
            'engineering': {'ratio': 0.35, 'priority': 1, 'roi': 2.5},
            'marketing': {'ratio': 0.20, 'priority': 2, 'roi': 3.0},
            'sales': {'ratio': 0.20, 'priority': 2, 'roi': 4.0},
            'operations': {'ratio': 0.15, 'priority': 3, 'roi': 1.5},
            'r_and_d': {'ratio': 0.10, 'priority': 3, 'roi': 5.0}
        },
        AllocationStrategy.GROWTH_FOCUSED: {
            'engineering': {'ratio': 0.25, 'priority': 2, 'roi': 2.5},
            'marketing': {'ratio': 0.30, 'priority': 1, 'roi': 3.5},
            'sales': {'ratio': 0.25, 'priority': 1, 'roi': 4.5},
            'operations': {'ratio': 0.10, 'priority': 3, 'roi': 1.5},
            'r_and_d': {'ratio': 0.10, 'priority': 4, 'roi': 5.0}
        },
        AllocationStrategy.EFFICIENCY_FOCUSED: {
            'engineering': {'ratio': 0.30, 'priority': 1, 'roi': 3.0},
            'marketing': {'ratio': 0.15, 'priority': 3, 'roi': 2.5},
            'sales': {'ratio': 0.20, 'priority': 2, 'roi': 3.5},
            'operations': {'ratio': 0.25, 'priority': 1, 'roi': 2.0},
            'r_and_d': {'ratio': 0.10, 'priority': 4, 'roi': 4.0}
        },
        AllocationStrategy.INNOVATION_FOCUSED: {
            'engineering': {'ratio': 0.35, 'priority': 1, 'roi': 2.5},
            'marketing': {'ratio': 0.10, 'priority': 4, 'roi': 2.0},
            'sales': {'ratio': 0.10, 'priority': 4, 'roi': 3.0},
            'operations': {'ratio': 0.15, 'priority': 3, 'roi': 1.5},
            'r_and_d': {'ratio': 0.30, 'priority': 1, 'roi': 6.0}
        },
        AllocationStrategy.RISK_AVERSE: {
            'engineering': {'ratio': 0.30, 'priority': 2, 'roi': 2.0},
            'marketing': {'ratio': 0.15, 'priority': 3, 'roi': 2.0},
            'sales': {'ratio': 0.15, 'priority': 3, 'roi': 2.5},
            'operations': {'ratio': 0.30, 'priority': 1, 'roi': 1.5},
            'r_and_d': {'ratio': 0.10, 'priority': 4, 'roi': 3.0}
        }
    }

    # 預設團隊配置模板
    TEAM_TEMPLATES = {
        'startup': {
            'engineering': {'ratio': 0.50, 'criticality': 'critical', 'cost': 120000},
            'product': {'ratio': 0.10, 'criticality': 'critical', 'cost': 130000},
            'marketing': {'ratio': 0.15, 'criticality': 'important', 'cost': 90000},
            'sales': {'ratio': 0.15, 'criticality': 'important', 'cost': 100000},
            'operations': {'ratio': 0.10, 'criticality': 'nice_to_have', 'cost': 80000}
        },
        'growth': {
            'engineering': {'ratio': 0.40, 'criticality': 'critical', 'cost': 130000},
            'product': {'ratio': 0.10, 'criticality': 'critical', 'cost': 140000},
            'marketing': {'ratio': 0.15, 'criticality': 'critical', 'cost': 100000},
            'sales': {'ratio': 0.20, 'criticality': 'critical', 'cost': 110000},
            'operations': {'ratio': 0.10, 'criticality': 'important', 'cost': 85000},
            'customer_success': {'ratio': 0.05, 'criticality': 'important', 'cost': 75000}
        },
        'enterprise': {
            'engineering': {'ratio': 0.30, 'criticality': 'critical', 'cost': 150000},
            'product': {'ratio': 0.10, 'criticality': 'critical', 'cost': 160000},
            'marketing': {'ratio': 0.10, 'criticality': 'important', 'cost': 110000},
            'sales': {'ratio': 0.20, 'criticality': 'critical', 'cost': 130000},
            'operations': {'ratio': 0.15, 'criticality': 'important', 'cost': 90000},
            'customer_success': {'ratio': 0.10, 'criticality': 'critical', 'cost': 85000},
            'finance': {'ratio': 0.05, 'criticality': 'important', 'cost': 120000}
        }
    }

    def __init__(self):
        """初始化資源優化器"""
        pass

    def optimize_budget(
        self,
        total_budget: float,
        strategy: AllocationStrategy = AllocationStrategy.BALANCED,
        constraints: dict[str, tuple[float, float]] | None = None,
        custom_priorities: dict[str, int] | None = None
    ) -> BudgetAllocation:
        """
        優化預算分配
        
        Args:
            total_budget: 總預算
            strategy: 分配策略
            constraints: 各類別的最小/最大金額限制 {category: (min, max)}
            custom_priorities: 自定義優先級 {category: priority}
            
        Returns:
            優化後的預算分配
        """
        template = self.BUDGET_TEMPLATES.get(
            strategy,
            self.BUDGET_TEMPLATES[AllocationStrategy.BALANCED]
        )

        allocations = {}
        notes = []

        for category, config in template.items():
            amount = total_budget * config['ratio']
            priority = config['priority']
            roi = config['roi']

            # 應用自定義優先級
            if custom_priorities and category in custom_priorities:
                priority = custom_priorities[category]
                notes.append(f"{category} 優先級已調整為 {priority}")

            # 應用約束
            if constraints and category in constraints:
                min_amt, max_amt = constraints[category]
                if amount < min_amt:
                    amount = min_amt
                    notes.append(f"{category} 已調整至最小金額 ${min_amt:,.0f}")
                elif amount > max_amt:
                    amount = max_amt
                    notes.append(f"{category} 已調整至最大金額 ${max_amt:,.0f}")

            allocations[category] = BudgetCategory(
                name=category,
                amount=amount,
                priority=priority,
                flexibility=0.2 if priority <= 2 else 0.4,
                roi_multiplier=roi
            )

        # 重新平衡以確保總和等於總預算
        current_total = sum(cat.amount for cat in allocations.values())
        if current_total != total_budget:
            adjustment_ratio = total_budget / current_total
            for cat in allocations.values():
                cat.amount *= adjustment_ratio

        # 計算優化分數
        optimization_score = self._calculate_budget_optimization_score(
            allocations, strategy
        )

        return BudgetAllocation(
            total_budget=total_budget,
            allocations=allocations,
            strategy=strategy,
            optimization_score=optimization_score,
            notes=notes
        )

    def _calculate_budget_optimization_score(
        self,
        allocations: dict[str, BudgetCategory],
        strategy: AllocationStrategy
    ) -> float:
        """計算預算優化分數"""
        # 基於有效價值計算分數
        total_effective_value = sum(
            cat.get_effective_value() for cat in allocations.values()
        )
        total_amount = sum(cat.amount for cat in allocations.values())

        if total_amount == 0:
            return 0.0

        # 正規化分數
        score = (total_effective_value / total_amount) * 25

        # 策略契合度加分
        strategy_bonus = {
            AllocationStrategy.BALANCED: 10,
            AllocationStrategy.GROWTH_FOCUSED: 15 if 'marketing' in allocations else 5,
            AllocationStrategy.EFFICIENCY_FOCUSED: 15 if 'operations' in allocations else 5,
            AllocationStrategy.INNOVATION_FOCUSED: 15 if 'r_and_d' in allocations else 5,
            AllocationStrategy.RISK_AVERSE: 10
        }
        score += strategy_bonus.get(strategy, 0)

        return min(100, max(0, score))

    def optimize_team(
        self,
        target_headcount: int,
        budget_constraint: float,
        stage: str = 'startup',
        skill_requirements: dict[str, list[str]] | None = None
    ) -> TeamAllocation:
        """
        優化團隊配置
        
        Args:
            target_headcount: 目標人數
            budget_constraint: 預算限制 (年度)
            stage: 公司階段 (startup, growth, enterprise)
            skill_requirements: 各角色所需技能
            
        Returns:
            優化後的團隊配置
        """
        template = self.TEAM_TEMPLATES.get(
            stage,
            self.TEAM_TEMPLATES['startup']
        )

        roles = {}
        hiring_plan = []
        total_cost = 0

        for role_name, config in template.items():
            headcount = max(1, round(target_headcount * config['ratio']))
            cost = config['cost']
            role_cost = headcount * cost

            # 檢查是否超出預算
            if total_cost + role_cost > budget_constraint:
                # 調整人數以符合預算
                max_affordable = int((budget_constraint - total_cost) / cost)
                if max_affordable < 1 and config['criticality'] == 'critical':
                    max_affordable = 1  # 關鍵角色至少 1 人
                headcount = max_affordable
                role_cost = headcount * cost

            if headcount > 0:
                skills = (skill_requirements or {}).get(role_name, [])
                roles[role_name] = TeamRole(
                    role_name=role_name,
                    headcount=headcount,
                    cost_per_person=cost,
                    skill_requirements=skills,
                    criticality=config['criticality']
                )
                total_cost += role_cost

                # 生成招聘計畫
                if headcount > 0:
                    hiring_plan.append({
                        'role': role_name,
                        'headcount': headcount,
                        'priority': 1 if config['criticality'] == 'critical' else
                                   2 if config['criticality'] == 'important' else 3,
                        'timeline_months': 1 if config['criticality'] == 'critical' else 3
                    })

        actual_headcount = sum(role.headcount for role in roles.values())

        # 計算優化分數
        optimization_score = self._calculate_team_optimization_score(
            roles, target_headcount, budget_constraint, total_cost
        )

        # 排序招聘計畫
        hiring_plan.sort(key=lambda x: x['priority'])

        return TeamAllocation(
            total_headcount=actual_headcount,
            total_cost=total_cost,
            roles=roles,
            structure='flat' if actual_headcount < 10 else
                      'hierarchical' if actual_headcount < 50 else 'matrix',
            optimization_score=optimization_score,
            hiring_plan=hiring_plan
        )

    def _calculate_team_optimization_score(
        self,
        roles: dict[str, TeamRole],
        target: int,
        budget: float,
        actual_cost: float
    ) -> float:
        """計算團隊優化分數"""
        score = 50.0  # 基礎分

        # 人數達成度
        actual = sum(r.headcount for r in roles.values())
        headcount_ratio = actual / target if target > 0 else 0
        score += headcount_ratio * 20

        # 預算利用率
        budget_utilization = actual_cost / budget if budget > 0 else 0
        if 0.8 <= budget_utilization <= 1.0:
            score += 20
        elif 0.6 <= budget_utilization < 0.8:
            score += 10
        elif budget_utilization > 1.0:
            score -= 10

        # 關鍵角色覆蓋
        critical_roles = [r for r in roles.values() if r.criticality == 'critical']
        if critical_roles:
            score += 10

        return min(100, max(0, score))

    def generate_optimization(
        self,
        total_budget: float,
        target_headcount: int,
        strategy: AllocationStrategy = AllocationStrategy.BALANCED,
        stage: str = 'startup',
        business_goals: list[str] | None = None
    ) -> OptimizationResult:
        """
        生成完整的資源優化方案
        
        Args:
            total_budget: 總預算
            target_headcount: 目標人數
            strategy: 分配策略
            stage: 公司階段
            business_goals: 業務目標
            
        Returns:
            完整優化結果
        """
        # 計算預算分配
        # 假設 70% 用於人力成本，30% 用於營運
        personnel_budget = total_budget * 0.7
        operational_budget = total_budget * 0.3

        budget_allocation = self.optimize_budget(
            operational_budget,
            strategy
        )

        team_allocation = self.optimize_team(
            target_headcount,
            personnel_budget,
            stage
        )

        # 計算 ROI 預測
        projected_roi = self._calculate_projected_roi(
            budget_allocation, team_allocation, business_goals
        )

        # 計算回收期
        payback_months = self._calculate_payback_period(
            total_budget, projected_roi
        )

        # 風險評估
        risk_score = self._calculate_risk_score(
            budget_allocation, team_allocation, strategy
        )

        # 敏感度分析
        sensitivity = self._perform_sensitivity_analysis(
            total_budget, target_headcount, projected_roi
        )

        # 生成建議
        recommendations = self._generate_recommendations(
            budget_allocation, team_allocation, business_goals
        )

        return OptimizationResult(
            budget_allocation=budget_allocation,
            team_allocation=team_allocation,
            projected_roi=projected_roi,
            payback_months=payback_months,
            risk_score=risk_score,
            confidence=max(0, 100 - risk_score),
            sensitivity_analysis=sensitivity,
            recommendations=recommendations
        )

    def _calculate_projected_roi(
        self,
        budget: BudgetAllocation,
        team: TeamAllocation,
        goals: list[str] | None
    ) -> float:
        """計算預測 ROI"""
        # 基於預算分配的預期回報
        total_expected_return = sum(
            cat.amount * cat.roi_multiplier
            for cat in budget.allocations.values()
        )

        # 加上人力投資的預期回報 (假設 3x)
        personnel_return = team.total_cost * 3.0

        total_investment = budget.total_budget + team.total_cost
        total_return = total_expected_return + personnel_return

        roi = (total_return - total_investment) / total_investment * 100

        # 根據目標調整
        if goals:
            if 'growth' in [g.lower() for g in goals]:
                roi *= 1.2
            if 'efficiency' in [g.lower() for g in goals]:
                roi *= 0.9

        return round(roi, 2)

    def _calculate_payback_period(
        self,
        investment: float,
        roi_percent: float
    ) -> int:
        """計算回收期（月）"""
        if roi_percent <= 0:
            return 120  # 10 年

        annual_return_rate = roi_percent / 100
        # 簡化計算：投資金額 / 年回報
        months = 12 / annual_return_rate if annual_return_rate > 0 else 120

        return min(120, max(1, round(months)))

    def _calculate_risk_score(
        self,
        budget: BudgetAllocation,
        team: TeamAllocation,
        strategy: AllocationStrategy
    ) -> float:
        """計算風險分數 (0-100, 越高越危險)"""
        score = 20.0  # 基礎風險

        # 策略風險
        strategy_risk = {
            AllocationStrategy.BALANCED: 0,
            AllocationStrategy.GROWTH_FOCUSED: 20,
            AllocationStrategy.EFFICIENCY_FOCUSED: 10,
            AllocationStrategy.INNOVATION_FOCUSED: 30,
            AllocationStrategy.RISK_AVERSE: -10
        }
        score += strategy_risk.get(strategy, 0)

        # 預算集中度風險
        max_ratio = max(
            cat.amount / budget.total_budget
            for cat in budget.allocations.values()
        )
        if max_ratio > 0.4:
            score += 15

        # 團隊規模風險
        if team.total_headcount < 5:
            score += 10
        elif team.total_headcount > 50:
            score += 5

        # 關鍵角色缺失風險
        critical = team.get_by_criticality('critical')
        if len(critical) < 2:
            score += 20

        return min(100, max(0, score))

    def _perform_sensitivity_analysis(
        self,
        budget: float,
        headcount: int,
        base_roi: float
    ) -> dict[str, Any]:
        """執行敏感度分析"""
        return {
            'budget_sensitivity': {
                '-20%': round(base_roi * 0.7, 2),
                '-10%': round(base_roi * 0.85, 2),
                'base': base_roi,
                '+10%': round(base_roi * 1.1, 2),
                '+20%': round(base_roi * 1.15, 2)
            },
            'headcount_sensitivity': {
                '-20%': round(base_roi * 0.75, 2),
                '-10%': round(base_roi * 0.9, 2),
                'base': base_roi,
                '+10%': round(base_roi * 1.05, 2),
                '+20%': round(base_roi * 1.08, 2)
            },
            'market_scenarios': {
                'pessimistic': round(base_roi * 0.5, 2),
                'conservative': round(base_roi * 0.75, 2),
                'base': base_roi,
                'optimistic': round(base_roi * 1.25, 2),
                'best_case': round(base_roi * 1.5, 2)
            }
        }

    def _generate_recommendations(
        self,
        budget: BudgetAllocation,
        team: TeamAllocation,
        goals: list[str] | None
    ) -> list[str]:
        """生成建議"""
        recommendations = []

        # 預算建議
        if budget.optimization_score < 60:
            recommendations.append("建議重新檢視預算分配，當前配置可能不夠優化")

        # 團隊建議
        critical = team.get_by_criticality('critical')
        if not critical:
            recommendations.append("建議優先招聘關鍵角色，確保核心能力")

        # 結構建議
        if team.total_headcount > 10 and team.structure == 'flat':
            recommendations.append("團隊規模擴大，建議考慮層級化管理結構")

        # 目標對齊建議
        if goals:
            if 'growth' in [g.lower() for g in goals]:
                if 'marketing' not in budget.allocations or \
                   budget.allocations['marketing'].amount < budget.total_budget * 0.15:
                    recommendations.append("增長目標需要更多行銷投資")

            if 'innovation' in [g.lower() for g in goals]:
                if 'r_and_d' not in budget.allocations or \
                   budget.allocations['r_and_d'].amount < budget.total_budget * 0.15:
                    recommendations.append("創新目標需要更多研發投資")

        if not recommendations:
            recommendations.append("當前配置已優化，建議持續監控執行情況")

        return recommendations

    def generate_report(self, result: OptimizationResult) -> str:
        """生成資源優化報告"""
        report = []
        report.append("# 資源優化報告")
        report.append(f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # 預算分配
        report.append("\n## 一、預算分配")
        report.append(f"\n**總預算**: ${result.budget_allocation.total_budget:,.0f}")
        report.append(f"**分配策略**: {result.budget_allocation.strategy.value}")
        report.append(f"**優化分數**: {result.budget_allocation.optimization_score:.1f}/100")

        report.append("\n| 類別 | 金額 | 佔比 | 優先級 | 預期 ROI |")
        report.append("|------|------|------|--------|----------|")
        for name, cat in result.budget_allocation.allocations.items():
            pct = cat.amount / result.budget_allocation.total_budget * 100
            report.append(
                f"| {name} | ${cat.amount:,.0f} | {pct:.1f}% | "
                f"P{cat.priority} | {cat.roi_multiplier}x |"
            )

        # 團隊配置
        report.append("\n## 二、團隊配置")
        report.append(f"\n**總人數**: {result.team_allocation.total_headcount}")
        report.append(f"**年度成本**: ${result.team_allocation.total_cost:,.0f}")
        report.append(f"**組織結構**: {result.team_allocation.structure}")
        report.append(f"**優化分數**: {result.team_allocation.optimization_score:.1f}/100")

        report.append("\n| 角色 | 人數 | 年薪 | 總成本 | 關鍵度 |")
        report.append("|------|------|------|--------|--------|")
        for name, role in result.team_allocation.roles.items():
            report.append(
                f"| {name} | {role.headcount} | ${role.cost_per_person:,.0f} | "
                f"${role.get_total_cost():,.0f} | {role.criticality} |"
            )

        # 投資回報
        report.append("\n## 三、投資回報預測")
        report.append(f"\n**預測 ROI**: {result.projected_roi:.1f}%")
        report.append(f"**預估回收期**: {result.payback_months} 個月")
        report.append(f"**風險分數**: {result.risk_score:.1f}/100")
        report.append(f"**信心指數**: {result.confidence:.1f}%")

        # 敏感度分析
        report.append("\n## 四、敏感度分析")
        report.append("\n**市場情境**:")
        for scenario, roi in result.sensitivity_analysis['market_scenarios'].items():
            report.append(f"- {scenario}: ROI {roi:.1f}%")

        # 建議
        report.append("\n## 五、優化建議")
        for i, rec in enumerate(result.recommendations, 1):
            report.append(f"{i}. {rec}")

        return '\n'.join(report)
