# -*- coding: utf-8 -*-
"""
行動指南 (Action Guide)

提供策略評估、行動建議和總結報告功能。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any


class ActionPriority(Enum):
    """行動優先級"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionStatus(Enum):
    """行動狀態"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"


class RecommendationType(Enum):
    """建議類型"""
    STRATEGY = "strategy"
    IMPLEMENTATION = "implementation"
    OPTIMIZATION = "optimization"
    RISK_MITIGATION = "risk_mitigation"
    CAPABILITY_BUILDING = "capability_building"


@dataclass
class ActionItem:
    """行動項目"""
    id: str
    title: str
    description: str
    priority: ActionPriority
    status: ActionStatus = ActionStatus.PENDING
    owner: str = ""
    due_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    resources_required: List[str] = field(default_factory=list)
    estimated_effort: str = ""  # e.g., "2 weeks", "40 hours"
    actual_effort: str = ""
    completed_date: Optional[datetime] = None
    notes: str = ""
    
    def is_overdue(self) -> bool:
        """檢查是否逾期"""
        if self.due_date and self.status != ActionStatus.COMPLETED:
            return datetime.now() > self.due_date
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'owner': self.owner,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'dependencies': self.dependencies,
            'success_criteria': self.success_criteria,
            'resources_required': self.resources_required,
            'estimated_effort': self.estimated_effort,
            'is_overdue': self.is_overdue()
        }


@dataclass
class Recommendation:
    """建議"""
    id: str
    type: RecommendationType
    title: str
    description: str
    rationale: str
    expected_impact: str
    effort_level: str  # "low", "medium", "high"
    priority: ActionPriority
    action_items: List[ActionItem] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'description': self.description,
            'rationale': self.rationale,
            'expected_impact': self.expected_impact,
            'effort_level': self.effort_level,
            'priority': self.priority.value,
            'action_items': [a.to_dict() for a in self.action_items],
            'prerequisites': self.prerequisites,
            'risks': self.risks
        }


class StrategyEvaluator:
    """策略評估器"""
    
    # 評估標準
    EVALUATION_CRITERIA = {
        'understanding': {
            'name': '深度理解',
            'description': '全面掌握各提示詞的本質與應用場景',
            'weight': 0.2
        },
        'quantitative': {
            'name': '量化評估',
            'description': '運用 SMART-V 框架進行客觀決策',
            'weight': 0.2
        },
        'combination': {
            'name': '組合策略',
            'description': '採用核心-衛星模式分散風險',
            'weight': 0.2
        },
        'agility': {
            'name': '動態調整',
            'description': '建立敏捷的策略調整機制',
            'weight': 0.2
        },
        'risk_control': {
            'name': '風險管控',
            'description': '制定完善的應急預案',
            'weight': 0.2
        }
    }
    
    def __init__(self):
        """初始化評估器"""
        self.scores: Dict[str, float] = {}
        self.evaluations: Dict[str, str] = {}
    
    def evaluate_criterion(self, criterion: str, score: float, notes: str = "") -> bool:
        """
        評估單個標準
        
        Args:
            criterion: 標準名稱
            score: 分數 (0-10)
            notes: 備註
        
        Returns:
            是否評估成功
        """
        if criterion not in self.EVALUATION_CRITERIA:
            return False
        
        self.scores[criterion] = min(10.0, max(0.0, score))
        self.evaluations[criterion] = notes
        return True
    
    def calculate_overall_score(self) -> float:
        """計算總體分數"""
        if not self.scores:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for criterion, info in self.EVALUATION_CRITERIA.items():
            if criterion in self.scores:
                weighted_sum += self.scores[criterion] * info['weight']
                total_weight += info['weight']
        
        if total_weight == 0:
            return 0.0
        
        return (weighted_sum / total_weight) * 10  # 轉換為 0-100 分
    
    def get_grade(self) -> str:
        """獲取等級"""
        score = self.calculate_overall_score()
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def get_weakest_areas(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """獲取最弱的領域"""
        if not self.scores:
            return []
        
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1])
        weakest = []
        
        for criterion, score in sorted_scores[:top_n]:
            if criterion in self.EVALUATION_CRITERIA:
                weakest.append({
                    'criterion': criterion,
                    'name': self.EVALUATION_CRITERIA[criterion]['name'],
                    'score': score,
                    'notes': self.evaluations.get(criterion, "")
                })
        
        return weakest
    
    def get_strongest_areas(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """獲取最強的領域"""
        if not self.scores:
            return []
        
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        strongest = []
        
        for criterion, score in sorted_scores[:top_n]:
            if criterion in self.EVALUATION_CRITERIA:
                strongest.append({
                    'criterion': criterion,
                    'name': self.EVALUATION_CRITERIA[criterion]['name'],
                    'score': score,
                    'notes': self.evaluations.get(criterion, "")
                })
        
        return strongest
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'overall_score': self.calculate_overall_score(),
            'grade': self.get_grade(),
            'scores': self.scores,
            'evaluations': self.evaluations,
            'weakest_areas': self.get_weakest_areas(),
            'strongest_areas': self.get_strongest_areas()
        }


class ActionGuide:
    """行動指南"""
    
    # 成功關鍵要素
    SUCCESS_KEYS = [
        {
            'id': 'understanding',
            'name': '深度理解',
            'description': '全面掌握各提示詞的本質與應用場景',
            'actions': [
                '研究每個提示詞的定義和適用範圍',
                '分析成功案例和失敗案例',
                '了解各提示詞之間的關聯和差異'
            ]
        },
        {
            'id': 'quantitative',
            'name': '量化評估',
            'description': '運用 SMART-V 框架進行客觀決策',
            'actions': [
                '建立評估指標體系',
                '收集和分析數據',
                '定期進行評估和回顧'
            ]
        },
        {
            'id': 'combination',
            'name': '組合策略',
            'description': '採用核心-衛星模式分散風險',
            'actions': [
                '確定核心提示詞（70% 資源）',
                '選擇衛星提示詞（20% 資源）',
                '保留探索資源（10% 資源）'
            ]
        },
        {
            'id': 'agility',
            'name': '動態調整',
            'description': '建立敏捷的策略調整機制',
            'actions': [
                '設定關鍵績效指標',
                '建立監控和預警系統',
                '制定調整觸發條件和流程'
            ]
        },
        {
            'id': 'risk_control',
            'name': '風險管控',
            'description': '制定完善的應急預案',
            'actions': [
                '識別潛在風險',
                '制定 Plan A/B/C 應急策略',
                '定期演練和更新預案'
            ]
        }
    ]
    
    def __init__(self):
        """初始化行動指南"""
        self.recommendations: List[Recommendation] = []
        self.action_items: List[ActionItem] = []
        self.evaluator = StrategyEvaluator()
        self._generate_default_recommendations()
    
    def _generate_default_recommendations(self) -> None:
        """生成預設建議"""
        # 建議 1: 策略選擇
        self.recommendations.append(Recommendation(
            id="rec_1",
            type=RecommendationType.STRATEGY,
            title="選擇最適合的提示詞組合",
            description="根據企業現況和目標，選擇最適合的核心-衛星提示詞組合",
            rationale="最好的提示詞策略不是最先進的，而是最適合當前情況的",
            expected_impact="提升策略執行效率 30%，降低風險 25%",
            effort_level="medium",
            priority=ActionPriority.HIGH,
            action_items=[
                ActionItem(
                    id="act_1_1",
                    title="進行現況評估",
                    description="評估團隊能力、市場環境、資源狀況",
                    priority=ActionPriority.HIGH,
                    estimated_effort="1 週"
                ),
                ActionItem(
                    id="act_1_2",
                    title="使用 SMART-V 框架評估候選提示詞",
                    description="對每個候選提示詞進行六維度評估",
                    priority=ActionPriority.HIGH,
                    estimated_effort="2 週"
                ),
                ActionItem(
                    id="act_1_3",
                    title="確定核心-衛星-探索配置",
                    description="根據評估結果分配資源比例",
                    priority=ActionPriority.MEDIUM,
                    estimated_effort="3 天"
                )
            ]
        ))
        
        # 建議 2: 實施規劃
        self.recommendations.append(Recommendation(
            id="rec_2",
            type=RecommendationType.IMPLEMENTATION,
            title="制定 12 個月實施計劃",
            description="建立詳細的階段性實施路線圖",
            rationale="有計劃的實施能確保策略落地並取得預期成果",
            expected_impact="提升項目成功率 40%",
            effort_level="high",
            priority=ActionPriority.HIGH,
            action_items=[
                ActionItem(
                    id="act_2_1",
                    title="規劃基礎建設期（1-3 月）",
                    description="完成團隊培訓、環境搭建、試點啟動",
                    priority=ActionPriority.HIGH,
                    estimated_effort="3 個月"
                ),
                ActionItem(
                    id="act_2_2",
                    title="規劃能力建構期（4-6 月）",
                    description="深化技術能力、完成首個項目、建立流程",
                    priority=ActionPriority.HIGH,
                    estimated_effort="3 個月"
                ),
                ActionItem(
                    id="act_2_3",
                    title="規劃規模化期（7-9 月）",
                    description="擴大團隊、引入衛星提示詞、建立回饋機制",
                    priority=ActionPriority.MEDIUM,
                    estimated_effort="3 個月"
                ),
                ActionItem(
                    id="act_2_4",
                    title="規劃優化成熟期（10-12 月）",
                    description="評估成效、調整方向、準備下年度計劃",
                    priority=ActionPriority.MEDIUM,
                    estimated_effort="3 個月"
                )
            ]
        ))
        
        # 建議 3: 風險管理
        self.recommendations.append(Recommendation(
            id="rec_3",
            type=RecommendationType.RISK_MITIGATION,
            title="建立完善的風險管控體系",
            description="識別、評估並制定風險應對策略",
            rationale="主動的風險管理能減少意外損失並提升應變能力",
            expected_impact="降低風險損失 50%",
            effort_level="medium",
            priority=ActionPriority.HIGH,
            action_items=[
                ActionItem(
                    id="act_3_1",
                    title="識別並評估潛在風險",
                    description="使用風險評估框架識別技術、市場、組織風險",
                    priority=ActionPriority.HIGH,
                    estimated_effort="1 週"
                ),
                ActionItem(
                    id="act_3_2",
                    title="制定 Plan A/B/C 應急預案",
                    description="為各類風險情境制定應對策略",
                    priority=ActionPriority.HIGH,
                    estimated_effort="2 週"
                ),
                ActionItem(
                    id="act_3_3",
                    title="建立監控和預警系統",
                    description="設定關鍵指標和預警閾值",
                    priority=ActionPriority.MEDIUM,
                    estimated_effort="1 週"
                )
            ]
        ))
        
        # 建議 4: 能力建設
        self.recommendations.append(Recommendation(
            id="rec_4",
            type=RecommendationType.CAPABILITY_BUILDING,
            title="投資團隊能力建設",
            description="提升團隊技術能力以支撐策略執行",
            rationale="團隊能力是策略成功的基礎",
            expected_impact="提升團隊生產力 25%",
            effort_level="high",
            priority=ActionPriority.MEDIUM,
            action_items=[
                ActionItem(
                    id="act_4_1",
                    title="進行技能差距分析",
                    description="評估現有能力與目標能力的差距",
                    priority=ActionPriority.HIGH,
                    estimated_effort="1 週"
                ),
                ActionItem(
                    id="act_4_2",
                    title="制定培訓計劃",
                    description="根據差距分析制定針對性培訓",
                    priority=ActionPriority.MEDIUM,
                    estimated_effort="2 週"
                ),
                ActionItem(
                    id="act_4_3",
                    title="建立持續學習機制",
                    description="鼓勵知識分享和持續學習",
                    priority=ActionPriority.MEDIUM,
                    estimated_effort="持續"
                )
            ]
        ))
    
    def add_recommendation(self, recommendation: Recommendation) -> None:
        """添加建議"""
        self.recommendations.append(recommendation)
    
    def add_action_item(self, action: ActionItem) -> None:
        """添加行動項目"""
        self.action_items.append(action)
    
    def get_recommendations_by_type(self, rec_type: RecommendationType) -> List[Recommendation]:
        """根據類型獲取建議"""
        return [r for r in self.recommendations if r.type == rec_type]
    
    def get_recommendations_by_priority(self, priority: ActionPriority) -> List[Recommendation]:
        """根據優先級獲取建議"""
        return [r for r in self.recommendations if r.priority == priority]
    
    def get_pending_actions(self) -> List[ActionItem]:
        """獲取待處理的行動項目"""
        pending = list(self.action_items)
        for rec in self.recommendations:
            for action in rec.action_items:
                if action.status == ActionStatus.PENDING:
                    pending.append(action)
        return pending
    
    def get_overdue_actions(self) -> List[ActionItem]:
        """獲取逾期的行動項目"""
        overdue = []
        for action in self.action_items:
            if action.is_overdue():
                overdue.append(action)
        for rec in self.recommendations:
            for action in rec.action_items:
                if action.is_overdue():
                    overdue.append(action)
        return overdue
    
    def generate_summary_report(self, format_type: str = "markdown") -> str:
        """
        生成總結報告
        
        Args:
            format_type: 報告格式 (markdown/text)
        
        Returns:
            格式化的報告字符串
        """
        if format_type == "markdown":
            return self._generate_markdown_summary()
        else:
            return self._generate_text_summary()
    
    def _generate_markdown_summary(self) -> str:
        """生成 Markdown 格式總結"""
        lines = [
            "# 總結與行動指南",
            "",
            "選擇合適的應用程式開發提示詞不是一次性決策，而是一個持續演進的策略過程。",
            "",
            "---",
            "",
            "## 成功的關鍵在於：",
            ""
        ]
        
        for i, key in enumerate(self.SUCCESS_KEYS, 1):
            lines.append(f"### {i}. {key['name']}")
            lines.append(f"{key['description']}")
            lines.append("")
            for action in key['actions']:
                lines.append(f"- {action}")
            lines.append("")
        
        lines.extend([
            "---",
            "",
            "## 核心建議",
            ""
        ])
        
        for rec in self.recommendations:
            priority_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }[rec.priority.value]
            
            lines.append(f"### {priority_icon} {rec.title}")
            lines.append(f"**類型：** {rec.type.value}")
            lines.append(f"**預期影響：** {rec.expected_impact}")
            lines.append("")
            lines.append(rec.description)
            lines.append("")
            
            if rec.action_items:
                lines.append("**行動項目：**")
                for action in rec.action_items:
                    lines.append(f"- [ ] {action.title} ({action.estimated_effort})")
                lines.append("")
        
        lines.extend([
            "---",
            "",
            "## 結語",
            "",
            "未來的應用程式開發將更加複雜多元，但透過系統化的提示詞策略思維，",
            "我們能夠在變化中保持競爭優勢，創造持續的商業價值。",
            "",
            "**記住，最好的提示詞策略不是最先進的，而是最適合你當前情況，",
            "並能夠為未來發展奠定堅實基礎的策略。**",
            "",
            "立即開始評估你的現況，選擇你的提示詞組合，開啟成功的應用程式開發之路！"
        ])
        
        return "\n".join(lines)
    
    def _generate_text_summary(self) -> str:
        """生成純文字格式總結"""
        lines = [
            "總結與行動指南",
            "=" * 50,
            "",
            "成功的關鍵在於：",
            ""
        ]
        
        for i, key in enumerate(self.SUCCESS_KEYS, 1):
            lines.append(f"{i}. {key['name']}: {key['description']}")
        
        lines.extend([
            "",
            "-" * 50,
            "",
            "核心建議：",
            ""
        ])
        
        for rec in self.recommendations:
            lines.append(f"• {rec.title}")
            lines.append(f"  預期影響: {rec.expected_impact}")
            lines.append("")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'success_keys': self.SUCCESS_KEYS,
            'recommendations': [r.to_dict() for r in self.recommendations],
            'action_items': [a.to_dict() for a in self.action_items],
            'strategy_evaluation': self.evaluator.to_dict(),
            'pending_actions_count': len(self.get_pending_actions()),
            'overdue_actions_count': len(self.get_overdue_actions())
        }
