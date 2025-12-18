"""
發展追蹤器 (Development Tracker)

功能：
- 3-2-1 策略實施：同時關注多個優先級提示詞
- 團隊能力建設：評估和提升團隊技能
- 持續優化：定期檢視和調整策略
- 風險管控：避免盲目追求趨勢

Features:
- 3-2-1 Strategy Implementation: Focus on multiple priority prompts simultaneously
- Team Capability Building: Assess and enhance team skills
- Continuous Optimization: Regular review and strategy adjustment
- Risk Management: Avoid blindly chasing trends
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class StrategyPriority(Enum):
    """策略優先級"""
    CURRENT = "current"         # 當前（3 個）
    PREPARING = "preparing"     # 準備中（2 個）
    RESEARCHING = "researching" # 研究中（1 個）


class SkillCategory(Enum):
    """技能類別"""
    TECHNICAL = "technical"             # 技術技能
    ARCHITECTURE = "architecture"       # 架構設計
    SECURITY = "security"               # 安全
    DEVOPS = "devops"                   # DevOps
    DATA = "data"                       # 數據
    AI_ML = "ai_ml"                     # AI/ML
    CLOUD = "cloud"                     # 雲端
    MOBILE = "mobile"                   # 移動開發
    FRONTEND = "frontend"               # 前端
    BACKEND = "backend"                 # 後端


class ReviewCycle(Enum):
    """檢視週期"""
    WEEKLY = "weekly"           # 每週
    MONTHLY = "monthly"         # 每月
    QUARTERLY = "quarterly"     # 每季
    ANNUAL = "annual"           # 每年


@dataclass
class StrategyItem:
    """策略項目"""
    strategy_id: str
    name: str
    description: str
    priority: StrategyPriority

    # 相關技能
    required_skills: list[SkillCategory] = field(default_factory=list)

    # 資源需求
    estimated_investment: float = 0.0    # 預估投資
    estimated_time_months: int = 0       # 預估時間
    team_size_required: int = 0          # 所需團隊規模

    # 預期收益
    expected_roi: float = 0.0            # 預期 ROI
    market_potential: str = "medium"     # 市場潛力 (low, medium, high)

    # 風險
    risk_level: str = "medium"           # 風險等級
    risk_factors: list[str] = field(default_factory=list)

    # 狀態
    progress: float = 0.0                # 進度 (0-100)
    status: str = "planned"              # 狀態 (planned, in_progress, completed, paused)
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class Strategy321:
    """
    3-2-1 策略管理
    
    同時關注：
    - 3 個當前優先提示詞
    - 2 個準備中的提示詞
    - 1 個研究中的未來提示詞
    """
    organization_id: str

    # 策略項目
    current_strategies: list[StrategyItem] = field(default_factory=list)      # 最多 3 個
    preparing_strategies: list[StrategyItem] = field(default_factory=list)    # 最多 2 個
    researching_strategies: list[StrategyItem] = field(default_factory=list)  # 最多 1 個

    # 歷史記錄
    strategy_history: list[dict[str, Any]] = field(default_factory=list)

    # 配置
    max_current: int = 3
    max_preparing: int = 2
    max_researching: int = 1

    # 審查日期
    last_review: datetime | None = None
    next_review: datetime | None = None
    review_cycle: ReviewCycle = ReviewCycle.QUARTERLY

    def add_strategy(
        self,
        strategy: StrategyItem
    ) -> tuple[bool, str]:
        """
        添加策略
        
        Args:
            strategy: 策略項目
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        if strategy.priority == StrategyPriority.CURRENT:
            if len(self.current_strategies) >= self.max_current:
                return False, f"當前策略已達上限 ({self.max_current})"
            self.current_strategies.append(strategy)

        elif strategy.priority == StrategyPriority.PREPARING:
            if len(self.preparing_strategies) >= self.max_preparing:
                return False, f"準備中策略已達上限 ({self.max_preparing})"
            self.preparing_strategies.append(strategy)

        elif strategy.priority == StrategyPriority.RESEARCHING:
            if len(self.researching_strategies) >= self.max_researching:
                return False, f"研究中策略已達上限 ({self.max_researching})"
            self.researching_strategies.append(strategy)

        return True, "策略添加成功"

    def promote_strategy(
        self,
        strategy_id: str
    ) -> tuple[bool, str]:
        """
        提升策略優先級
        
        Args:
            strategy_id: 策略 ID
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 從研究中提升到準備中
        for i, s in enumerate(self.researching_strategies):
            if s.strategy_id == strategy_id:
                if len(self.preparing_strategies) >= self.max_preparing:
                    return False, "準備中策略已滿"
                s.priority = StrategyPriority.PREPARING
                self.preparing_strategies.append(s)
                self.researching_strategies.pop(i)
                self._record_history(strategy_id, "promoted", "researching -> preparing")
                return True, "策略已提升到準備中"

        # 從準備中提升到當前
        for i, s in enumerate(self.preparing_strategies):
            if s.strategy_id == strategy_id:
                if len(self.current_strategies) >= self.max_current:
                    return False, "當前策略已滿"
                s.priority = StrategyPriority.CURRENT
                s.started_at = datetime.now()
                s.status = "in_progress"
                self.current_strategies.append(s)
                self.preparing_strategies.pop(i)
                self._record_history(strategy_id, "promoted", "preparing -> current")
                return True, "策略已提升到當前執行"

        return False, "找不到指定策略"

    def complete_strategy(
        self,
        strategy_id: str,
        actual_roi: float = 0.0
    ) -> tuple[bool, str]:
        """
        完成策略
        
        Args:
            strategy_id: 策略 ID
            actual_roi: 實際 ROI
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        for i, s in enumerate(self.current_strategies):
            if s.strategy_id == strategy_id:
                s.status = "completed"
                s.completed_at = datetime.now()
                s.progress = 100
                self.current_strategies.pop(i)
                self._record_history(
                    strategy_id,
                    "completed",
                    f"actual_roi: {actual_roi}"
                )
                return True, "策略已完成"

        return False, "找不到指定策略或策略不在當前執行中"

    def _record_history(
        self,
        strategy_id: str,
        action: str,
        details: str
    ) -> None:
        """記錄歷史"""
        self.strategy_history.append({
            'strategy_id': strategy_id,
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def get_status_report(self) -> dict[str, Any]:
        """獲取狀態報告"""
        return {
            'organization_id': self.organization_id,
            'current_strategies': [
                {
                    'id': s.strategy_id,
                    'name': s.name,
                    'progress': s.progress,
                    'status': s.status
                }
                for s in self.current_strategies
            ],
            'preparing_strategies': [
                {'id': s.strategy_id, 'name': s.name}
                for s in self.preparing_strategies
            ],
            'researching_strategies': [
                {'id': s.strategy_id, 'name': s.name}
                for s in self.researching_strategies
            ],
            'slots': {
                'current': f"{len(self.current_strategies)}/{self.max_current}",
                'preparing': f"{len(self.preparing_strategies)}/{self.max_preparing}",
                'researching': f"{len(self.researching_strategies)}/{self.max_researching}"
            },
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'report_date': datetime.now().isoformat()
        }


@dataclass
class TeamSkillAssessment:
    """團隊技能評估"""
    skill_category: SkillCategory
    current_level: float = 0.0          # 當前水平 (0-100)
    target_level: float = 0.0           # 目標水平
    team_members_with_skill: int = 0    # 擁有此技能的成員數
    training_hours_needed: int = 0      # 所需培訓時數
    priority: str = "medium"            # 優先級


@dataclass
class TeamCapability:
    """
    團隊能力管理
    
    功能：
    - 技能評估
    - 培訓計劃
    - 能力差距分析
    """
    team_id: str
    team_name: str
    team_size: int

    # 技能評估
    skill_assessments: dict[SkillCategory, TeamSkillAssessment] = field(default_factory=dict)

    # 培訓計劃
    training_plans: list[dict[str, Any]] = field(default_factory=list)

    # 評估日期
    last_assessment: datetime | None = None

    def assess_skill(
        self,
        category: SkillCategory,
        current_level: float,
        target_level: float,
        members_with_skill: int
    ) -> TeamSkillAssessment:
        """
        評估技能
        
        Args:
            category: 技能類別
            current_level: 當前水平
            target_level: 目標水平
            members_with_skill: 擁有此技能的成員數
        
        Returns:
            TeamSkillAssessment: 評估結果
        """
        gap = max(0, target_level - current_level)

        # 估算培訓時數（每 10 分差距約需 20 小時）
        training_hours = int(gap * 2 * (self.team_size - members_with_skill))

        # 確定優先級
        if gap >= 30:
            priority = "high"
        elif gap >= 15:
            priority = "medium"
        else:
            priority = "low"

        assessment = TeamSkillAssessment(
            skill_category=category,
            current_level=current_level,
            target_level=target_level,
            team_members_with_skill=members_with_skill,
            training_hours_needed=training_hours,
            priority=priority
        )

        self.skill_assessments[category] = assessment
        self.last_assessment = datetime.now()

        return assessment

    def get_capability_gaps(self) -> list[dict[str, Any]]:
        """獲取能力差距"""
        gaps = []

        for category, assessment in self.skill_assessments.items():
            gap = assessment.target_level - assessment.current_level
            if gap > 0:
                gaps.append({
                    'skill': category.value,
                    'current': assessment.current_level,
                    'target': assessment.target_level,
                    'gap': gap,
                    'priority': assessment.priority,
                    'training_hours': assessment.training_hours_needed,
                    'coverage': f"{assessment.team_members_with_skill}/{self.team_size}"
                })

        # 按差距大小排序
        return sorted(gaps, key=lambda x: x['gap'], reverse=True)

    def create_training_plan(
        self,
        skill_category: SkillCategory,
        training_name: str,
        duration_hours: int,
        cost: float = 0.0
    ) -> dict[str, Any]:
        """
        創建培訓計劃
        
        Args:
            skill_category: 技能類別
            training_name: 培訓名稱
            duration_hours: 時長
            cost: 成本
        
        Returns:
            Dict: 培訓計劃
        """
        plan = {
            'plan_id': f"tp_{len(self.training_plans) + 1}",
            'skill_category': skill_category.value,
            'training_name': training_name,
            'duration_hours': duration_hours,
            'cost': cost,
            'status': 'planned',
            'created_at': datetime.now().isoformat()
        }

        self.training_plans.append(plan)
        return plan

    def get_overall_capability_score(self) -> float:
        """計算整體能力分數"""
        if not self.skill_assessments:
            return 0.0

        total_score = sum(
            a.current_level for a in self.skill_assessments.values()
        )
        return total_score / len(self.skill_assessments)


@dataclass
class OptimizationReview:
    """優化審查記錄"""
    review_id: str
    review_date: datetime
    review_type: ReviewCycle

    # 審查內容
    strategies_reviewed: int = 0
    changes_made: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # 指標
    metrics_before: dict[str, float] = field(default_factory=dict)
    metrics_after: dict[str, float] = field(default_factory=dict)

    # 下次審查
    next_review_date: datetime | None = None


class ContinuousOptimization:
    """
    持續優化管理
    
    功能：
    - 定期策略檢視
    - 績效追蹤
    - 調整建議
    """

    def __init__(self):
        self.reviews: list[OptimizationReview] = []
        self.metrics_history: list[dict[str, Any]] = []
        self.alerts: list[dict[str, Any]] = []

    def schedule_review(
        self,
        review_cycle: ReviewCycle,
        start_date: datetime | None = None
    ) -> datetime:
        """
        排程審查
        
        Args:
            review_cycle: 審查週期
            start_date: 開始日期
        
        Returns:
            datetime: 下次審查日期
        """
        if start_date is None:
            start_date = datetime.now()

        delta_days = {
            ReviewCycle.WEEKLY: 7,
            ReviewCycle.MONTHLY: 30,
            ReviewCycle.QUARTERLY: 90,
            ReviewCycle.ANNUAL: 365
        }

        next_review = start_date + timedelta(days=delta_days[review_cycle])
        return next_review

    def conduct_review(
        self,
        strategy_321: Strategy321,
        team_capability: TeamCapability
    ) -> OptimizationReview:
        """
        執行審查
        
        Args:
            strategy_321: 3-2-1 策略
            team_capability: 團隊能力
        
        Returns:
            OptimizationReview: 審查結果
        """
        review_id = f"rev_{len(self.reviews) + 1}"

        # 收集當前指標
        current_metrics = {
            'active_strategies': len(strategy_321.current_strategies),
            'preparing_strategies': len(strategy_321.preparing_strategies),
            'team_capability_score': team_capability.get_overall_capability_score(),
            'capability_gaps': len(team_capability.get_capability_gaps())
        }

        # 生成變更和建議
        changes = []
        recommendations = []

        # 檢查策略進度
        for s in strategy_321.current_strategies:
            if s.progress < 25 and s.started_at:
                days_since_start = (datetime.now() - s.started_at).days
                if days_since_start > 30:
                    recommendations.append(
                        f"策略 '{s.name}' 進度緩慢 ({s.progress}%)，建議評估資源配置"
                    )

        # 檢查準備中策略
        if len(strategy_321.preparing_strategies) < strategy_321.max_preparing:
            recommendations.append(
                "準備中策略不足，建議從研究中提升或添加新策略"
            )

        # 檢查團隊能力差距
        gaps = team_capability.get_capability_gaps()
        high_priority_gaps = [g for g in gaps if g['priority'] == 'high']
        if high_priority_gaps:
            recommendations.append(
                f"發現 {len(high_priority_gaps)} 個高優先級能力差距，建議安排培訓"
            )

        # 創建審查記錄
        review = OptimizationReview(
            review_id=review_id,
            review_date=datetime.now(),
            review_type=strategy_321.review_cycle,
            strategies_reviewed=len(strategy_321.current_strategies) +
                               len(strategy_321.preparing_strategies),
            changes_made=changes,
            recommendations=recommendations,
            metrics_before=self.metrics_history[-1] if self.metrics_history else {},
            metrics_after=current_metrics,
            next_review_date=self.schedule_review(strategy_321.review_cycle)
        )

        self.reviews.append(review)
        self.metrics_history.append(current_metrics)

        # 更新策略的下次審查日期
        strategy_321.last_review = review.review_date
        strategy_321.next_review = review.next_review_date

        return review

    def generate_optimization_report(self) -> str:
        """生成優化報告"""
        if not self.reviews:
            return "尚無審查記錄"

        latest_review = self.reviews[-1]

        report_lines = [
            "=" * 60,
            "📊 持續優化報告",
            "=" * 60,
            f"審查日期: {latest_review.review_date.strftime('%Y-%m-%d')}",
            f"審查類型: {latest_review.review_type.value}",
            f"策略審查數: {latest_review.strategies_reviewed}",
            "",
            "📈 當前指標",
            "-" * 40,
        ]

        for metric, value in latest_review.metrics_after.items():
            report_lines.append(f"  {metric}: {value}")

        if latest_review.recommendations:
            report_lines.extend([
                "",
                "💡 建議",
                "-" * 40,
            ])
            for rec in latest_review.recommendations:
                report_lines.append(f"  • {rec}")

        if latest_review.next_review_date:
            report_lines.extend([
                "",
                f"📅 下次審查: {latest_review.next_review_date.strftime('%Y-%m-%d')}",
            ])

        return "\n".join(report_lines)

    def set_alert(
        self,
        metric_name: str,
        threshold: float,
        comparison: str = "below"  # below, above
    ) -> None:
        """
        設置警報
        
        Args:
            metric_name: 指標名稱
            threshold: 閾值
            comparison: 比較方式
        """
        self.alerts.append({
            'metric_name': metric_name,
            'threshold': threshold,
            'comparison': comparison,
            'created_at': datetime.now().isoformat()
        })

    def check_alerts(self, current_metrics: dict[str, float]) -> list[dict[str, Any]]:
        """
        檢查警報
        
        Args:
            current_metrics: 當前指標
        
        Returns:
            List[Dict]: 觸發的警報
        """
        triggered = []

        for alert in self.alerts:
            metric_name = alert['metric_name']
            if metric_name in current_metrics:
                value = current_metrics[metric_name]
                threshold = alert['threshold']

                if alert['comparison'] == 'below' and value < threshold:
                    triggered.append({
                        'alert': alert,
                        'current_value': value,
                        'message': f"{metric_name} ({value}) 低於閾值 ({threshold})"
                    })
                elif alert['comparison'] == 'above' and value > threshold:
                    triggered.append({
                        'alert': alert,
                        'current_value': value,
                        'message': f"{metric_name} ({value}) 高於閾值 ({threshold})"
                    })

        return triggered


class DevelopmentTracker:
    """
    發展追蹤器
    
    整合 3-2-1 策略、團隊能力和持續優化
    
    Usage:
        tracker = DevelopmentTracker("org_001")
        
        # 添加策略
        strategy = StrategyItem(...)
        tracker.add_strategy(strategy)
        
        # 評估團隊能力
        tracker.assess_team_skill(SkillCategory.SECURITY, 60, 80, 5)
        
        # 執行審查
        review = tracker.conduct_quarterly_review()
        
        # 獲取報告
        report = tracker.generate_full_report()
    """

    def __init__(
        self,
        organization_id: str,
        team_name: str = "Development Team",
        team_size: int = 10
    ):
        self.strategy_321 = Strategy321(organization_id=organization_id)
        self.team_capability = TeamCapability(
            team_id=f"{organization_id}_team",
            team_name=team_name,
            team_size=team_size
        )
        self.continuous_optimization = ContinuousOptimization()

    def add_strategy(
        self,
        strategy_id: str,
        name: str,
        description: str,
        priority: StrategyPriority,
        **kwargs
    ) -> tuple[bool, str]:
        """添加策略"""
        strategy = StrategyItem(
            strategy_id=strategy_id,
            name=name,
            description=description,
            priority=priority,
            **kwargs
        )
        return self.strategy_321.add_strategy(strategy)

    def assess_team_skill(
        self,
        category: SkillCategory,
        current_level: float,
        target_level: float,
        members_with_skill: int
    ) -> TeamSkillAssessment:
        """評估團隊技能"""
        return self.team_capability.assess_skill(
            category, current_level, target_level, members_with_skill
        )

    def conduct_quarterly_review(self) -> OptimizationReview:
        """執行季度審查"""
        self.strategy_321.review_cycle = ReviewCycle.QUARTERLY
        return self.continuous_optimization.conduct_review(
            self.strategy_321,
            self.team_capability
        )

    def generate_full_report(self) -> str:
        """生成完整報告"""
        report_lines = [
            "=" * 70,
            "🎯 發展追蹤器 - 完整報告",
            "=" * 70,
            "",
            "📋 3-2-1 策略狀態",
            "-" * 50,
        ]

        status = self.strategy_321.get_status_report()

        report_lines.append(f"當前執行 ({status['slots']['current']}):")
        for s in status['current_strategies']:
            report_lines.append(f"  • {s['name']} - {s['progress']}% ({s['status']})")

        report_lines.append(f"準備中 ({status['slots']['preparing']}):")
        for s in status['preparing_strategies']:
            report_lines.append(f"  • {s['name']}")

        report_lines.append(f"研究中 ({status['slots']['researching']}):")
        for s in status['researching_strategies']:
            report_lines.append(f"  • {s['name']}")

        # 團隊能力
        report_lines.extend([
            "",
            "👥 團隊能力",
            "-" * 50,
            f"整體能力分數: {self.team_capability.get_overall_capability_score():.1f}/100",
        ])

        gaps = self.team_capability.get_capability_gaps()
        if gaps:
            report_lines.append("能力差距:")
            for gap in gaps[:5]:  # 顯示前 5 個
                report_lines.append(
                    f"  • {gap['skill']}: {gap['current']:.0f} -> {gap['target']:.0f} "
                    f"(差距: {gap['gap']:.0f}, {gap['priority']})"
                )

        # 優化建議
        report_lines.extend([
            "",
            "💡 優化建議",
            "-" * 50,
        ])

        if self.continuous_optimization.reviews:
            latest = self.continuous_optimization.reviews[-1]
            for rec in latest.recommendations:
                report_lines.append(f"  • {rec}")
        else:
            report_lines.append("  尚無審查記錄，建議執行首次審查")

        report_lines.extend([
            "",
            "=" * 70,
            f"報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ])

        return "\n".join(report_lines)
