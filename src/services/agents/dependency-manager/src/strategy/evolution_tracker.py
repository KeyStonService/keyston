"""
演進追蹤器 - 專案成熟度評估與階段轉換

此模組提供：
- 專案成熟度評估
- 發展階段識別
- 階段轉換建議
- 演進路線圖生成

Copyright (c) 2024 SynergyMesh
MIT License
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class MaturityLevel(Enum):
    """成熟度等級"""
    INITIAL = "初始"
    DEVELOPING = "發展中"
    DEFINED = "已定義"
    MANAGED = "已管理"
    OPTIMIZING = "持續優化"


class DevelopmentPhase(Enum):
    """發展階段"""
    IDEATION = "構想期"
    VALIDATION = "驗證期"
    EFFICIENCY = "效率期"
    SCALE = "規模化"
    EXPANSION = "擴張期"
    MATURITY = "成熟期"


@dataclass
class MaturityDimension:
    """成熟度維度"""
    name: str
    level: MaturityLevel
    score: float  # 0-100
    evidence: list[str]
    improvement_areas: list[str]

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'name': self.name,
            'level': self.level.value,
            'score': self.score,
            'evidence': self.evidence,
            'improvement_areas': self.improvement_areas
        }


@dataclass
class ProjectMaturity:
    """專案成熟度評估"""
    assessed_at: datetime
    overall_level: MaturityLevel
    overall_score: float
    dimensions: dict[str, MaturityDimension]
    current_phase: DevelopmentPhase
    phase_progress: float  # 當前階段完成度 0-100
    blockers: list[str]
    accelerators: list[str]

    def get_weakest_dimension(self) -> str:
        """獲取最弱維度"""
        if not self.dimensions:
            return ""
        return min(self.dimensions.items(), key=lambda x: x[1].score)[0]

    def get_strongest_dimension(self) -> str:
        """獲取最強維度"""
        if not self.dimensions:
            return ""
        return max(self.dimensions.items(), key=lambda x: x[1].score)[0]

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'assessed_at': self.assessed_at.isoformat(),
            'overall_level': self.overall_level.value,
            'overall_score': self.overall_score,
            'dimensions': {k: v.to_dict() for k, v in self.dimensions.items()},
            'current_phase': self.current_phase.value,
            'phase_progress': self.phase_progress,
            'blockers': self.blockers,
            'accelerators': self.accelerators,
            'weakest_dimension': self.get_weakest_dimension(),
            'strongest_dimension': self.get_strongest_dimension()
        }


@dataclass
class PhaseTransition:
    """階段轉換"""
    from_phase: DevelopmentPhase
    to_phase: DevelopmentPhase
    readiness_score: float  # 0-100
    prerequisites: list[str]
    completed_prerequisites: list[str]
    estimated_timeline_months: int
    risks: list[str]
    recommendations: list[str]

    def get_prerequisite_completion_rate(self) -> float:
        """獲取先決條件完成率"""
        if not self.prerequisites:
            return 100.0
        return len(self.completed_prerequisites) / len(self.prerequisites) * 100

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'from_phase': self.from_phase.value,
            'to_phase': self.to_phase.value,
            'readiness_score': self.readiness_score,
            'prerequisites': self.prerequisites,
            'completed_prerequisites': self.completed_prerequisites,
            'prerequisite_completion_rate': self.get_prerequisite_completion_rate(),
            'estimated_timeline_months': self.estimated_timeline_months,
            'risks': self.risks,
            'recommendations': self.recommendations
        }


@dataclass
class EvolutionRoadmap:
    """演進路線圖"""
    created_at: datetime
    current_phase: DevelopmentPhase
    target_phase: DevelopmentPhase
    milestones: list[dict[str, Any]]
    critical_path: list[str]
    total_timeline_months: int
    investment_required: float
    success_probability: float  # 0-100

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            'created_at': self.created_at.isoformat(),
            'current_phase': self.current_phase.value,
            'target_phase': self.target_phase.value,
            'milestones': self.milestones,
            'critical_path': self.critical_path,
            'total_timeline_months': self.total_timeline_months,
            'investment_required': self.investment_required,
            'success_probability': self.success_probability
        }


class EvolutionTracker:
    """
    演進追蹤器
    
    提供：
    - 專案成熟度評估
    - 階段識別與轉換
    - 演進路線圖
    - 進度追蹤
    """

    # 成熟度評估維度
    MATURITY_DIMENSIONS = [
        'technology',      # 技術成熟度
        'process',         # 流程成熟度
        'team',            # 團隊成熟度
        'product',         # 產品成熟度
        'market',          # 市場成熟度
        'governance',      # 治理成熟度
        'finance',         # 財務成熟度
        'culture'          # 文化成熟度
    ]

    # 階段轉換先決條件
    PHASE_PREREQUISITES = {
        (DevelopmentPhase.IDEATION, DevelopmentPhase.VALIDATION): [
            "完成市場調研",
            "定義核心價值主張",
            "建立最小團隊",
            "確認初始資金"
        ],
        (DevelopmentPhase.VALIDATION, DevelopmentPhase.EFFICIENCY): [
            "驗證產品市場契合度",
            "取得首批付費客戶",
            "建立可重複的獲客流程",
            "確立單位經濟學"
        ],
        (DevelopmentPhase.EFFICIENCY, DevelopmentPhase.SCALE): [
            "優化營運效率",
            "建立標準化流程",
            "達成正向現金流",
            "組建完整團隊"
        ],
        (DevelopmentPhase.SCALE, DevelopmentPhase.EXPANSION): [
            "證明可規模化模式",
            "建立銷售通路",
            "實現穩定增長",
            "確保資金到位"
        ],
        (DevelopmentPhase.EXPANSION, DevelopmentPhase.MATURITY): [
            "建立市場領導地位",
            "多元化收入來源",
            "建立長期競爭優勢",
            "實現持續獲利"
        ]
    }

    def __init__(self):
        """初始化演進追蹤器"""
        self._assessment_history: list[ProjectMaturity] = []

    def assess_maturity(
        self,
        project_data: dict[str, Any]
    ) -> ProjectMaturity:
        """
        評估專案成熟度
        
        Args:
            project_data: 專案數據
            
        Returns:
            成熟度評估結果
        """
        dimensions = {}

        for dim_name in self.MATURITY_DIMENSIONS:
            dim_data = project_data.get(dim_name, {})
            dimension = self._assess_dimension(dim_name, dim_data)
            dimensions[dim_name] = dimension

        # 計算整體分數
        overall_score = sum(d.score for d in dimensions.values()) / len(dimensions)

        # 判斷整體等級
        overall_level = self._score_to_level(overall_score)

        # 判斷當前階段
        current_phase = self._determine_phase(project_data, overall_score)

        # 計算階段進度
        phase_progress = self._calculate_phase_progress(
            current_phase, project_data, dimensions
        )

        # 識別阻礙因素
        blockers = self._identify_blockers(dimensions, project_data)

        # 識別加速因素
        accelerators = self._identify_accelerators(dimensions, project_data)

        maturity = ProjectMaturity(
            assessed_at=datetime.now(),
            overall_level=overall_level,
            overall_score=overall_score,
            dimensions=dimensions,
            current_phase=current_phase,
            phase_progress=phase_progress,
            blockers=blockers,
            accelerators=accelerators
        )

        self._assessment_history.append(maturity)

        return maturity

    def _assess_dimension(
        self,
        name: str,
        data: dict[str, Any]
    ) -> MaturityDimension:
        """評估單一維度"""
        # 根據維度類型計算分數
        score = data.get('score', 50.0)
        evidence = data.get('evidence', [])

        # 如果沒有直接分數，根據指標計算
        if 'indicators' in data:
            indicators = data['indicators']
            positive = sum(1 for i in indicators if indicators[i] is True)
            total = len(indicators)
            score = (positive / total * 100) if total > 0 else 50.0

        level = self._score_to_level(score)

        # 識別改善領域
        improvement_areas = self._identify_improvements(name, score, data)

        return MaturityDimension(
            name=name,
            level=level,
            score=score,
            evidence=evidence,
            improvement_areas=improvement_areas
        )

    def _score_to_level(self, score: float) -> MaturityLevel:
        """分數轉換為等級"""
        if score >= 85:
            return MaturityLevel.OPTIMIZING
        elif score >= 70:
            return MaturityLevel.MANAGED
        elif score >= 55:
            return MaturityLevel.DEFINED
        elif score >= 40:
            return MaturityLevel.DEVELOPING
        else:
            return MaturityLevel.INITIAL

    def _determine_phase(
        self,
        data: dict[str, Any],
        overall_score: float
    ) -> DevelopmentPhase:
        """判斷當前發展階段"""
        # 根據關鍵指標判斷
        revenue = data.get('revenue', 0)
        customers = data.get('customers', 0)
        data.get('team_size', 0)
        data.get('funding_stage', 'seed')

        # 判斷邏輯
        if revenue > 10000000 and customers > 1000:
            return DevelopmentPhase.MATURITY
        elif revenue > 1000000 and customers > 100:
            return DevelopmentPhase.EXPANSION
        elif revenue > 100000 and customers > 10:
            return DevelopmentPhase.SCALE
        elif customers > 0 and revenue > 0:
            return DevelopmentPhase.EFFICIENCY
        elif data.get('has_mvp', False):
            return DevelopmentPhase.VALIDATION
        else:
            return DevelopmentPhase.IDEATION

    def _calculate_phase_progress(
        self,
        phase: DevelopmentPhase,
        data: dict[str, Any],
        dimensions: dict[str, MaturityDimension]
    ) -> float:
        """計算階段完成進度"""
        # 獲取下一階段的先決條件
        phase_order = list(DevelopmentPhase)
        current_idx = phase_order.index(phase)

        if current_idx >= len(phase_order) - 1:
            return 100.0  # 已是最後階段

        next_phase = phase_order[current_idx + 1]
        prerequisites = self.PHASE_PREREQUISITES.get(
            (phase, next_phase), []
        )

        if not prerequisites:
            # 基於成熟度分數估算
            avg_score = sum(d.score for d in dimensions.values()) / len(dimensions)
            return min(100, avg_score * 1.2)

        # 計算先決條件完成度
        completed = data.get('completed_milestones', [])
        completion_count = sum(1 for p in prerequisites if p in completed)

        return completion_count / len(prerequisites) * 100

    def _identify_blockers(
        self,
        dimensions: dict[str, MaturityDimension],
        data: dict[str, Any]
    ) -> list[str]:
        """識別阻礙因素"""
        blockers = []

        # 低分維度
        for name, dim in dimensions.items():
            if dim.score < 40:
                blockers.append(f"{name} 成熟度不足 ({dim.score:.0f}分)")

        # 資源不足
        if data.get('runway_months', 12) < 6:
            blockers.append("資金跑道不足 6 個月")

        if data.get('team_size', 0) < 3:
            blockers.append("團隊規模過小")

        # 市場因素
        if data.get('market_competition', 'medium') == 'high':
            blockers.append("市場競爭激烈")

        return blockers

    def _identify_accelerators(
        self,
        dimensions: dict[str, MaturityDimension],
        data: dict[str, Any]
    ) -> list[str]:
        """識別加速因素"""
        accelerators = []

        # 高分維度
        for name, dim in dimensions.items():
            if dim.score >= 80:
                accelerators.append(f"{name} 表現優異 ({dim.score:.0f}分)")

        # 有利條件
        if data.get('has_strategic_partnerships', False):
            accelerators.append("擁有策略夥伴關係")

        if data.get('recurring_revenue_rate', 0) > 0.7:
            accelerators.append("高經常性收入比例")

        if data.get('customer_nps', 0) > 50:
            accelerators.append("客戶滿意度高")

        return accelerators

    def _identify_improvements(
        self,
        dimension: str,
        score: float,
        data: dict[str, Any]
    ) -> list[str]:
        """識別改善領域"""
        improvements_map = {
            'technology': [
                "升級技術架構",
                "加強自動化測試",
                "改善技術債務"
            ],
            'process': [
                "標準化作業流程",
                "引入敏捷方法論",
                "建立品質管理"
            ],
            'team': [
                "加強團隊培訓",
                "改善溝通機制",
                "建立績效管理"
            ],
            'product': [
                "強化用戶研究",
                "改善產品路線圖",
                "提升使用者體驗"
            ],
            'market': [
                "擴大市場調研",
                "優化定位策略",
                "強化競爭分析"
            ],
            'governance': [
                "建立決策機制",
                "強化風險管理",
                "完善合規制度"
            ],
            'finance': [
                "改善財務規劃",
                "優化現金流管理",
                "建立預算控制"
            ],
            'culture': [
                "強化價值觀傳遞",
                "改善員工參與",
                "建立創新文化"
            ]
        }

        if score >= 80:
            return []

        return improvements_map.get(dimension, ["持續改善"])[:2]

    def evaluate_transition(
        self,
        maturity: ProjectMaturity,
        target_phase: DevelopmentPhase | None = None
    ) -> PhaseTransition:
        """
        評估階段轉換
        
        Args:
            maturity: 當前成熟度評估
            target_phase: 目標階段（預設為下一階段）
            
        Returns:
            階段轉換評估
        """
        current_phase = maturity.current_phase

        # 確定目標階段
        if target_phase is None:
            phase_order = list(DevelopmentPhase)
            current_idx = phase_order.index(current_phase)
            if current_idx >= len(phase_order) - 1:
                target_phase = current_phase  # 已是最後階段
            else:
                target_phase = phase_order[current_idx + 1]

        # 獲取先決條件
        prerequisites = self.PHASE_PREREQUISITES.get(
            (current_phase, target_phase),
            []
        )

        # 評估完成狀態（基於成熟度維度）
        completed = []
        for prereq in prerequisites:
            # 簡化判斷：基於整體分數
            if maturity.overall_score >= 60:
                completed.append(prereq)

        # 計算就緒度分數
        readiness_score = self._calculate_readiness(
            maturity, prerequisites, completed
        )

        # 估算時間
        timeline = self._estimate_timeline(
            current_phase, target_phase, readiness_score
        )

        # 識別風險
        risks = self._identify_transition_risks(
            maturity, current_phase, target_phase
        )

        # 生成建議
        recommendations = self._generate_transition_recommendations(
            maturity, prerequisites, completed
        )

        return PhaseTransition(
            from_phase=current_phase,
            to_phase=target_phase,
            readiness_score=readiness_score,
            prerequisites=prerequisites,
            completed_prerequisites=completed,
            estimated_timeline_months=timeline,
            risks=risks,
            recommendations=recommendations
        )

    def _calculate_readiness(
        self,
        maturity: ProjectMaturity,
        prerequisites: list[str],
        completed: list[str]
    ) -> float:
        """計算轉換就緒度"""
        if not prerequisites:
            return maturity.phase_progress

        prereq_score = len(completed) / len(prerequisites) * 50
        maturity_score = maturity.overall_score * 0.5

        return prereq_score + maturity_score

    def _estimate_timeline(
        self,
        from_phase: DevelopmentPhase,
        to_phase: DevelopmentPhase,
        readiness: float
    ) -> int:
        """估算轉換時間"""
        # 基礎時間
        base_timelines = {
            DevelopmentPhase.IDEATION: 3,
            DevelopmentPhase.VALIDATION: 6,
            DevelopmentPhase.EFFICIENCY: 9,
            DevelopmentPhase.SCALE: 12,
            DevelopmentPhase.EXPANSION: 18,
            DevelopmentPhase.MATURITY: 24
        }

        base = base_timelines.get(to_phase, 12)

        # 根據就緒度調整
        if readiness >= 80:
            return max(1, base // 2)
        elif readiness >= 60:
            return base
        elif readiness >= 40:
            return int(base * 1.5)
        else:
            return base * 2

    def _identify_transition_risks(
        self,
        maturity: ProjectMaturity,
        from_phase: DevelopmentPhase,
        to_phase: DevelopmentPhase
    ) -> list[str]:
        """識別轉換風險"""
        risks = []

        # 成熟度風險
        if maturity.overall_score < 50:
            risks.append("整體成熟度不足，可能無法支撐階段轉換")

        # 維度不平衡風險
        weakest = maturity.get_weakest_dimension()
        strongest = maturity.get_strongest_dimension()
        if maturity.dimensions:
            score_diff = (
                maturity.dimensions[strongest].score -
                maturity.dimensions[weakest].score
            )
            if score_diff > 30:
                risks.append(f"維度發展不平衡：{weakest} 明顯落後")

        # 阻礙因素風險
        if maturity.blockers:
            risks.append(f"存在 {len(maturity.blockers)} 個阻礙因素")

        # 階段跳躍風險
        phase_order = list(DevelopmentPhase)
        from_idx = phase_order.index(from_phase)
        to_idx = phase_order.index(to_phase)
        if to_idx - from_idx > 1:
            risks.append("跳躍階段風險高，建議循序漸進")

        return risks

    def _generate_transition_recommendations(
        self,
        maturity: ProjectMaturity,
        prerequisites: list[str],
        completed: list[str]
    ) -> list[str]:
        """生成轉換建議"""
        recommendations = []

        # 未完成的先決條件
        pending = [p for p in prerequisites if p not in completed]
        if pending:
            recommendations.append(f"優先完成: {pending[0]}")

        # 加強弱項
        weakest = maturity.get_weakest_dimension()
        if weakest and maturity.dimensions[weakest].score < 60:
            recommendations.append(f"加強 {weakest} 維度的發展")

        # 善用優勢
        strongest = maturity.get_strongest_dimension()
        if strongest:
            recommendations.append(f"善用 {strongest} 優勢推動轉型")

        # 解決阻礙
        if maturity.blockers:
            recommendations.append(f"優先解決: {maturity.blockers[0]}")

        return recommendations

    def create_roadmap(
        self,
        maturity: ProjectMaturity,
        target_phase: DevelopmentPhase,
        timeline_months: int | None = None
    ) -> EvolutionRoadmap:
        """
        創建演進路線圖
        
        Args:
            maturity: 當前成熟度
            target_phase: 目標階段
            timeline_months: 目標時間（月）
            
        Returns:
            演進路線圖
        """
        current_phase = maturity.current_phase

        # 計算需要經過的階段
        phase_order = list(DevelopmentPhase)
        current_idx = phase_order.index(current_phase)
        target_idx = phase_order.index(target_phase)

        phases_to_traverse = phase_order[current_idx:target_idx + 1]

        # 生成里程碑
        milestones = []
        cumulative_months = 0

        for i, _phase in enumerate(phases_to_traverse[:-1]):
            next_phase = phases_to_traverse[i + 1]
            transition = self.evaluate_transition(maturity, next_phase)

            cumulative_months += transition.estimated_timeline_months

            milestones.append({
                'phase': next_phase.value,
                'target_date': cumulative_months,
                'prerequisites': transition.prerequisites,
                'key_metrics': self._get_phase_metrics(next_phase)
            })

        # 計算總時間
        total_timeline = timeline_months or cumulative_months

        # 識別關鍵路徑
        critical_path = self._identify_critical_path(
            phases_to_traverse, maturity
        )

        # 估算投資
        investment = self._estimate_investment(
            maturity, phases_to_traverse
        )

        # 計算成功機率
        success_prob = self._calculate_success_probability(
            maturity, phases_to_traverse
        )

        return EvolutionRoadmap(
            created_at=datetime.now(),
            current_phase=current_phase,
            target_phase=target_phase,
            milestones=milestones,
            critical_path=critical_path,
            total_timeline_months=total_timeline,
            investment_required=investment,
            success_probability=success_prob
        )

    def _get_phase_metrics(self, phase: DevelopmentPhase) -> dict[str, str]:
        """獲取階段關鍵指標"""
        metrics = {
            DevelopmentPhase.IDEATION: {
                'market_research': '完成',
                'team_size': '>= 2',
                'initial_funding': '已確認'
            },
            DevelopmentPhase.VALIDATION: {
                'mvp_launched': '是',
                'paying_customers': '>= 10',
                'product_market_fit': '初步驗證'
            },
            DevelopmentPhase.EFFICIENCY: {
                'unit_economics': '正向',
                'cac_ltv_ratio': '< 0.3',
                'churn_rate': '< 10%'
            },
            DevelopmentPhase.SCALE: {
                'revenue_growth': '> 50% MoM',
                'team_size': '>= 20',
                'process_automation': '> 50%'
            },
            DevelopmentPhase.EXPANSION: {
                'market_share': '> 10%',
                'revenue_diversity': '多元',
                'geographic_presence': '多區域'
            },
            DevelopmentPhase.MATURITY: {
                'profitability': '持續獲利',
                'market_position': '領導地位',
                'brand_value': '高認知度'
            }
        }

        return metrics.get(phase, {})

    def _identify_critical_path(
        self,
        phases: list[DevelopmentPhase],
        maturity: ProjectMaturity
    ) -> list[str]:
        """識別關鍵路徑"""
        critical = []

        # 基於最弱維度
        weakest = maturity.get_weakest_dimension()
        if weakest:
            critical.append(f"強化 {weakest}")

        # 基於阻礙因素
        if maturity.blockers:
            critical.append(f"解決: {maturity.blockers[0]}")

        # 基於階段轉換
        for phase in phases[1:]:
            critical.append(f"達成 {phase.value} 目標")

        return critical

    def _estimate_investment(
        self,
        maturity: ProjectMaturity,
        phases: list[DevelopmentPhase]
    ) -> float:
        """估算投資需求"""
        # 每階段基礎投資
        phase_investment = {
            DevelopmentPhase.IDEATION: 100000,
            DevelopmentPhase.VALIDATION: 500000,
            DevelopmentPhase.EFFICIENCY: 1000000,
            DevelopmentPhase.SCALE: 5000000,
            DevelopmentPhase.EXPANSION: 10000000,
            DevelopmentPhase.MATURITY: 20000000
        }

        total = sum(phase_investment.get(p, 1000000) for p in phases[1:])

        # 根據成熟度調整
        if maturity.overall_score < 50:
            total *= 1.3  # 需要更多投資
        elif maturity.overall_score > 70:
            total *= 0.8  # 效率較高

        return total

    def _calculate_success_probability(
        self,
        maturity: ProjectMaturity,
        phases: list[DevelopmentPhase]
    ) -> float:
        """計算成功機率"""
        base_prob = 50.0

        # 成熟度加成
        base_prob += (maturity.overall_score - 50) * 0.3

        # 階段數量影響
        num_phases = len(phases) - 1
        base_prob -= num_phases * 5

        # 阻礙因素影響
        base_prob -= len(maturity.blockers) * 5

        # 加速因素影響
        base_prob += len(maturity.accelerators) * 5

        return max(10, min(90, base_prob))

    def generate_report(
        self,
        maturity: ProjectMaturity,
        transition: PhaseTransition | None = None,
        roadmap: EvolutionRoadmap | None = None
    ) -> str:
        """生成演進追蹤報告"""
        report = []
        report.append("# 專案演進追蹤報告")
        report.append(f"\n評估時間: {maturity.assessed_at.strftime('%Y-%m-%d %H:%M')}")

        # 整體狀態
        report.append("\n## 一、成熟度評估")
        report.append(f"\n**整體等級**: {maturity.overall_level.value}")
        report.append(f"**整體分數**: {maturity.overall_score:.1f}/100")
        report.append(f"**當前階段**: {maturity.current_phase.value}")
        report.append(f"**階段進度**: {maturity.phase_progress:.1f}%")

        # 維度分析
        report.append("\n### 維度分析")
        report.append("\n| 維度 | 等級 | 分數 |")
        report.append("|------|------|------|")
        for name, dim in maturity.dimensions.items():
            report.append(f"| {name} | {dim.level.value} | {dim.score:.0f} |")

        report.append(f"\n**最強維度**: {maturity.get_strongest_dimension()}")
        report.append(f"**最弱維度**: {maturity.get_weakest_dimension()}")

        # 阻礙與加速因素
        if maturity.blockers:
            report.append("\n### 阻礙因素")
            for blocker in maturity.blockers:
                report.append(f"- ⚠️ {blocker}")

        if maturity.accelerators:
            report.append("\n### 加速因素")
            for acc in maturity.accelerators:
                report.append(f"- ✓ {acc}")

        # 階段轉換
        if transition:
            report.append("\n## 二、階段轉換評估")
            report.append(f"\n**從**: {transition.from_phase.value}")
            report.append(f"**至**: {transition.to_phase.value}")
            report.append(f"**就緒度**: {transition.readiness_score:.1f}%")
            report.append(f"**預估時間**: {transition.estimated_timeline_months} 個月")

            report.append("\n### 先決條件")
            for prereq in transition.prerequisites:
                status = "✓" if prereq in transition.completed_prerequisites else "○"
                report.append(f"- {status} {prereq}")

            if transition.risks:
                report.append("\n### 轉換風險")
                for risk in transition.risks:
                    report.append(f"- ⚠️ {risk}")

            if transition.recommendations:
                report.append("\n### 轉換建議")
                for rec in transition.recommendations:
                    report.append(f"- {rec}")

        # 路線圖
        if roadmap:
            report.append("\n## 三、演進路線圖")
            report.append(f"\n**目標階段**: {roadmap.target_phase.value}")
            report.append(f"**總時程**: {roadmap.total_timeline_months} 個月")
            report.append(f"**預估投資**: ${roadmap.investment_required:,.0f}")
            report.append(f"**成功機率**: {roadmap.success_probability:.1f}%")

            report.append("\n### 里程碑")
            for milestone in roadmap.milestones:
                report.append(f"\n**{milestone['phase']}** (第 {milestone['target_date']} 個月)")
                for metric, value in milestone['key_metrics'].items():
                    report.append(f"- {metric}: {value}")

            report.append("\n### 關鍵路徑")
            for i, step in enumerate(roadmap.critical_path, 1):
                report.append(f"{i}. {step}")

        return '\n'.join(report)
