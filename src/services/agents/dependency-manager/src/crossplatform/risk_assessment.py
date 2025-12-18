"""
風險評估框架
Risk Assessment Framework Module

提供技術風險分類、評估和緩解策略
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RiskCategory(Enum):
    """風險類別"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskType(Enum):
    """風險類型"""
    TECHNOLOGY_DEPENDENCY = "technology_dependency"
    VENDOR_LOCK_IN = "vendor_lock_in"
    TALENT_SCARCITY = "talent_scarcity"
    MARKET_ACCEPTANCE = "market_acceptance"
    REGULATORY_CHANGE = "regulatory_change"
    SECURITY_VULNERABILITY = "security_vulnerability"
    TECHNICAL_DEBT = "technical_debt"
    INTEGRATION_COMPLEXITY = "integration_complexity"


@dataclass
class MitigationStrategy:
    """緩解策略"""
    risk_type: RiskType
    strategy_name: str
    description: str
    implementation_effort: str  # low, medium, high
    effectiveness: int  # 1-10
    cost_impact: str  # low, medium, high
    timeline: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'risk_type': self.risk_type.value,
            'strategy_name': self.strategy_name,
            'description': self.description,
            'implementation_effort': self.implementation_effort,
            'effectiveness': self.effectiveness,
            'cost_impact': self.cost_impact,
            'timeline': self.timeline
        }


@dataclass
class RiskItem:
    """風險項目"""
    risk_id: str
    risk_type: RiskType
    category: RiskCategory
    title: str
    description: str
    probability: int  # 1-10
    impact: int  # 1-10

    # 評估結果
    risk_score: float = 0.0
    mitigation_strategies: list[MitigationStrategy] = field(default_factory=list)
    status: str = "identified"
    owner: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            'risk_id': self.risk_id,
            'risk_type': self.risk_type.value,
            'category': self.category.value,
            'title': self.title,
            'description': self.description,
            'probability': self.probability,
            'impact': self.impact,
            'risk_score': self.risk_score,
            'mitigation_strategies': [m.to_dict() for m in self.mitigation_strategies],
            'status': self.status,
            'owner': self.owner
        }


class RiskAssessment:
    """風險評估器"""

    # 預設緩解策略
    DEFAULT_MITIGATIONS = {
        RiskType.TECHNOLOGY_DEPENDENCY: [
            MitigationStrategy(
                risk_type=RiskType.TECHNOLOGY_DEPENDENCY,
                strategy_name="技術替代方案",
                description="建立技術替代方案，避免單一技術依賴",
                implementation_effort="medium",
                effectiveness=8,
                cost_impact="medium",
                timeline="3-6 個月"
            ),
            MitigationStrategy(
                risk_type=RiskType.TECHNOLOGY_DEPENDENCY,
                strategy_name="抽象層設計",
                description="在核心業務邏輯與外部技術間建立抽象層",
                implementation_effort="high",
                effectiveness=9,
                cost_impact="medium",
                timeline="6-12 個月"
            )
        ],
        RiskType.VENDOR_LOCK_IN: [
            MitigationStrategy(
                risk_type=RiskType.VENDOR_LOCK_IN,
                strategy_name="多元化技術選擇",
                description="採用開放標準和多供應商策略",
                implementation_effort="medium",
                effectiveness=7,
                cost_impact="medium",
                timeline="3-6 個月"
            ),
            MitigationStrategy(
                risk_type=RiskType.VENDOR_LOCK_IN,
                strategy_name="可攜性設計",
                description="設計可遷移的架構，降低轉換成本",
                implementation_effort="high",
                effectiveness=8,
                cost_impact="high",
                timeline="6-12 個月"
            )
        ],
        RiskType.TALENT_SCARCITY: [
            MitigationStrategy(
                risk_type=RiskType.TALENT_SCARCITY,
                strategy_name="內部培訓計畫",
                description="投資內部培訓，提升團隊技能",
                implementation_effort="medium",
                effectiveness=7,
                cost_impact="medium",
                timeline="6-12 個月"
            ),
            MitigationStrategy(
                risk_type=RiskType.TALENT_SCARCITY,
                strategy_name="知識文件化",
                description="完善技術文件，降低人員依賴",
                implementation_effort="low",
                effectiveness=6,
                cost_impact="low",
                timeline="1-3 個月"
            )
        ],
        RiskType.MARKET_ACCEPTANCE: [
            MitigationStrategy(
                risk_type=RiskType.MARKET_ACCEPTANCE,
                strategy_name="小規模試點驗證",
                description="在正式推出前進行小規模市場測試",
                implementation_effort="low",
                effectiveness=8,
                cost_impact="low",
                timeline="1-3 個月"
            ),
            MitigationStrategy(
                risk_type=RiskType.MARKET_ACCEPTANCE,
                strategy_name="用戶回饋循環",
                description="建立持續的用戶回饋機制",
                implementation_effort="low",
                effectiveness=7,
                cost_impact="low",
                timeline="持續進行"
            )
        ],
        RiskType.REGULATORY_CHANGE: [
            MitigationStrategy(
                risk_type=RiskType.REGULATORY_CHANGE,
                strategy_name="合規性持續監控",
                description="建立法規變化監控機制",
                implementation_effort="low",
                effectiveness=6,
                cost_impact="low",
                timeline="持續進行"
            ),
            MitigationStrategy(
                risk_type=RiskType.REGULATORY_CHANGE,
                strategy_name="彈性架構設計",
                description="設計可快速調整的合規架構",
                implementation_effort="high",
                effectiveness=8,
                cost_impact="medium",
                timeline="3-6 個月"
            )
        ],
        RiskType.SECURITY_VULNERABILITY: [
            MitigationStrategy(
                risk_type=RiskType.SECURITY_VULNERABILITY,
                strategy_name="定期安全審計",
                description="實施定期安全掃描和滲透測試",
                implementation_effort="medium",
                effectiveness=9,
                cost_impact="medium",
                timeline="持續進行"
            ),
            MitigationStrategy(
                risk_type=RiskType.SECURITY_VULNERABILITY,
                strategy_name="安全開發流程",
                description="導入 DevSecOps 和安全編碼規範",
                implementation_effort="high",
                effectiveness=9,
                cost_impact="high",
                timeline="6-12 個月"
            )
        ],
        RiskType.TECHNICAL_DEBT: [
            MitigationStrategy(
                risk_type=RiskType.TECHNICAL_DEBT,
                strategy_name="技術債務管理",
                description="建立技術債務追蹤和還款計畫",
                implementation_effort="medium",
                effectiveness=7,
                cost_impact="medium",
                timeline="持續進行"
            ),
            MitigationStrategy(
                risk_type=RiskType.TECHNICAL_DEBT,
                strategy_name="重構優先級",
                description="優先處理高利息技術債務",
                implementation_effort="medium",
                effectiveness=8,
                cost_impact="medium",
                timeline="3-6 個月"
            )
        ],
        RiskType.INTEGRATION_COMPLEXITY: [
            MitigationStrategy(
                risk_type=RiskType.INTEGRATION_COMPLEXITY,
                strategy_name="整合測試策略",
                description="建立完善的整合測試環境和流程",
                implementation_effort="medium",
                effectiveness=8,
                cost_impact="medium",
                timeline="3-6 個月"
            ),
            MitigationStrategy(
                risk_type=RiskType.INTEGRATION_COMPLEXITY,
                strategy_name="API 契約管理",
                description="實施 API 版本控制和契約測試",
                implementation_effort="medium",
                effectiveness=7,
                cost_impact="low",
                timeline="1-3 個月"
            )
        ]
    }

    def __init__(self):
        self.risks: list[RiskItem] = []
        self._risk_counter = 0

    def _generate_risk_id(self) -> str:
        """生成風險 ID"""
        self._risk_counter += 1
        return f"RISK-{self._risk_counter:04d}"

    def add_risk(
        self,
        risk_type: RiskType,
        title: str,
        description: str,
        probability: int,
        impact: int,
        owner: str = ""
    ) -> RiskItem:
        """添加風險"""
        # 計算風險分數
        risk_score = probability * impact

        # 確定風險類別
        if risk_score >= 60:
            category = RiskCategory.HIGH
        elif risk_score >= 30:
            category = RiskCategory.MEDIUM
        else:
            category = RiskCategory.LOW

        risk = RiskItem(
            risk_id=self._generate_risk_id(),
            risk_type=risk_type,
            category=category,
            title=title,
            description=description,
            probability=probability,
            impact=impact,
            risk_score=risk_score,
            owner=owner
        )

        # 添加預設緩解策略
        risk.mitigation_strategies = self.DEFAULT_MITIGATIONS.get(risk_type, []).copy()

        self.risks.append(risk)
        return risk

    def assess_project_risks(
        self,
        technology_stack: list[str],
        team_experience: str,
        market_maturity: str,
        regulatory_requirements: list[str]
    ) -> list[RiskItem]:
        """評估項目風險"""
        assessed_risks = []

        # 技術依賴風險
        if len(technology_stack) > 5:
            risk = self.add_risk(
                RiskType.TECHNOLOGY_DEPENDENCY,
                "複雜技術棧依賴",
                f"項目使用 {len(technology_stack)} 種技術，增加維護複雜度",
                6, 7
            )
            assessed_risks.append(risk)

        # 人才風險
        experience_risk = {'low': (8, 8), 'medium': (5, 6), 'high': (3, 4)}
        prob, imp = experience_risk.get(team_experience, (5, 5))
        risk = self.add_risk(
            RiskType.TALENT_SCARCITY,
            "團隊經驗風險",
            f"團隊經驗等級: {team_experience}",
            prob, imp
        )
        assessed_risks.append(risk)

        # 市場風險
        market_risk = {'emerging': (7, 8), 'growing': (5, 6), 'mature': (3, 4)}
        prob, imp = market_risk.get(market_maturity, (5, 5))
        risk = self.add_risk(
            RiskType.MARKET_ACCEPTANCE,
            "市場接受度風險",
            f"市場成熟度: {market_maturity}",
            prob, imp
        )
        assessed_risks.append(risk)

        # 法規風險
        if regulatory_requirements:
            risk = self.add_risk(
                RiskType.REGULATORY_CHANGE,
                "法規合規風險",
                f"需符合: {', '.join(regulatory_requirements)}",
                6, 7
            )
            assessed_risks.append(risk)

        return assessed_risks

    def get_high_priority_risks(self) -> list[RiskItem]:
        """獲取高優先級風險"""
        return [r for r in self.risks if r.category == RiskCategory.HIGH]

    def get_risks_by_type(self, risk_type: RiskType) -> list[RiskItem]:
        """按類型獲取風險"""
        return [r for r in self.risks if r.risk_type == risk_type]

    def update_risk_status(self, risk_id: str, status: str) -> RiskItem | None:
        """更新風險狀態"""
        for risk in self.risks:
            if risk.risk_id == risk_id:
                risk.status = status
                return risk
        return None

    def calculate_overall_risk_score(self) -> float:
        """計算整體風險分數"""
        if not self.risks:
            return 0.0

        # 加權平均，高風險權重更高
        weights = {RiskCategory.HIGH: 3, RiskCategory.MEDIUM: 2, RiskCategory.LOW: 1}
        total_weighted_score = sum(r.risk_score * weights[r.category] for r in self.risks)
        total_weights = sum(weights[r.category] for r in self.risks)

        return total_weighted_score / total_weights if total_weights > 0 else 0.0

    def generate_risk_report(self, format: str = 'markdown') -> str:
        """生成風險報告"""
        if format == 'markdown':
            return self._generate_markdown_report()
        else:
            return self._generate_text_report()

    def _generate_markdown_report(self) -> str:
        """生成 Markdown 報告"""
        lines = [
            "# 風險評估報告",
            f"\n**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\n**整體風險分數**: {self.calculate_overall_risk_score():.1f}/100",
            f"\n**識別風險數量**: {len(self.risks)}",
            "\n## 風險摘要",
            f"- 🔴 高風險: {len([r for r in self.risks if r.category == RiskCategory.HIGH])}",
            f"- 🟡 中風險: {len([r for r in self.risks if r.category == RiskCategory.MEDIUM])}",
            f"- 🟢 低風險: {len([r for r in self.risks if r.category == RiskCategory.LOW])}",
            "\n## 詳細風險列表\n"
        ]

        for risk in sorted(self.risks, key=lambda r: r.risk_score, reverse=True):
            emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[risk.category.value]
            lines.extend([
                f"### {emoji} {risk.title}",
                f"- **ID**: {risk.risk_id}",
                f"- **類型**: {risk.risk_type.value}",
                f"- **風險分數**: {risk.risk_score}",
                f"- **機率**: {risk.probability}/10 | **影響**: {risk.impact}/10",
                f"- **描述**: {risk.description}",
                f"- **狀態**: {risk.status}",
                "\n**緩解策略**:"
            ])
            for strat in risk.mitigation_strategies:
                lines.append(f"- {strat.strategy_name}: {strat.description}")
            lines.append("")

        return "\n".join(lines)

    def _generate_text_report(self) -> str:
        """生成純文字報告"""
        lines = [
            "=" * 60,
            "風險評估報告",
            "=" * 60,
            f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"整體風險分數: {self.calculate_overall_risk_score():.1f}/100",
            f"識別風險數量: {len(self.risks)}",
            "-" * 60
        ]

        for risk in sorted(self.risks, key=lambda r: r.risk_score, reverse=True):
            lines.extend([
                f"\n[{risk.category.value.upper()}] {risk.title}",
                f"  ID: {risk.risk_id}",
                f"  風險分數: {risk.risk_score}",
                f"  描述: {risk.description}"
            ])

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'generated_at': datetime.now().isoformat(),
            'overall_risk_score': self.calculate_overall_risk_score(),
            'risks': [r.to_dict() for r in self.risks],
            'summary': {
                'total': len(self.risks),
                'high': len([r for r in self.risks if r.category == RiskCategory.HIGH]),
                'medium': len([r for r in self.risks if r.category == RiskCategory.MEDIUM]),
                'low': len([r for r in self.risks if r.category == RiskCategory.LOW])
            }
        }
