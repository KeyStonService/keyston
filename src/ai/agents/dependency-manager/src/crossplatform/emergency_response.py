"""
應急預案系統
Emergency Response System Module

提供 Plan A/B/C 應急預案設計和觸發條件評估
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime


class PlanType(Enum):
    """預案類型"""
    PLAN_A = "plan_a"  # 主要策略
    PLAN_B = "plan_b"  # 調整策略
    PLAN_C = "plan_c"  # 緊急策略


class TriggerCategory(Enum):
    """觸發類別"""
    MARKET_CHANGE = "market_change"
    TECHNOLOGY_SHIFT = "technology_shift"
    COMPETITOR_ACTION = "competitor_action"
    RESOURCE_CONSTRAINT = "resource_constraint"
    REGULATORY_CHANGE = "regulatory_change"
    PERFORMANCE_DECLINE = "performance_decline"


@dataclass
class TriggerCondition:
    """觸發條件"""
    trigger_id: str
    category: TriggerCategory
    name: str
    description: str
    threshold: float
    current_value: float = 0.0
    is_triggered: bool = False
    target_plan: PlanType = PlanType.PLAN_B
    
    def evaluate(self, value: float) -> bool:
        """評估觸發條件"""
        self.current_value = value
        self.is_triggered = value >= self.threshold
        return self.is_triggered
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trigger_id': self.trigger_id,
            'category': self.category.value,
            'name': self.name,
            'description': self.description,
            'threshold': self.threshold,
            'current_value': self.current_value,
            'is_triggered': self.is_triggered,
            'target_plan': self.target_plan.value
        }


@dataclass
class ActionItem:
    """行動項目"""
    action_id: str
    title: str
    description: str
    priority: int  # 1-5
    responsible: str
    deadline: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_id': self.action_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'responsible': self.responsible,
            'deadline': self.deadline,
            'dependencies': self.dependencies,
            'status': self.status
        }


@dataclass
class EmergencyPlan:
    """應急預案"""
    plan_type: PlanType
    name: str
    description: str
    objective: str
    trigger_conditions: List[str]  # 觸發條件 ID 列表
    actions: List[ActionItem] = field(default_factory=list)
    resource_allocation: Dict[str, float] = field(default_factory=dict)
    success_metrics: Dict[str, float] = field(default_factory=dict)
    rollback_plan: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plan_type': self.plan_type.value,
            'name': self.name,
            'description': self.description,
            'objective': self.objective,
            'trigger_conditions': self.trigger_conditions,
            'actions': [a.to_dict() for a in self.actions],
            'resource_allocation': self.resource_allocation,
            'success_metrics': self.success_metrics,
            'rollback_plan': self.rollback_plan
        }


class EmergencyResponse:
    """應急響應系統"""
    
    def __init__(self):
        self.plans: Dict[PlanType, EmergencyPlan] = {}
        self.triggers: Dict[str, TriggerCondition] = {}
        self.active_plan: PlanType = PlanType.PLAN_A
        self._trigger_counter = 0
        self._action_counter = 0
        
        # 初始化預設預案
        self._initialize_default_plans()
        self._initialize_default_triggers()
    
    def _initialize_default_plans(self):
        """初始化預設預案"""
        # Plan A: 主要策略
        self.plans[PlanType.PLAN_A] = EmergencyPlan(
            plan_type=PlanType.PLAN_A,
            name="主要策略 - 正常執行",
            description="按照既定提示詞策略執行，維持正常運營",
            objective="達成既定目標，穩定成長",
            trigger_conditions=[],
            resource_allocation={
                'development': 0.50,
                'operations': 0.20,
                'marketing': 0.15,
                'reserve': 0.15
            },
            success_metrics={
                'revenue_growth': 0.15,
                'user_retention': 0.85,
                'nps_score': 50
            },
            rollback_plan="無需回滾，持續監控關鍵指標"
        )
        
        # Plan B: 調整策略
        self.plans[PlanType.PLAN_B] = EmergencyPlan(
            plan_type=PlanType.PLAN_B,
            name="調整策略 - 適應變化",
            description="市場或技術變化時的策略調整",
            objective="快速適應環境變化，維持競爭力",
            trigger_conditions=['TRIG-0001', 'TRIG-0002', 'TRIG-0003'],
            resource_allocation={
                'development': 0.40,
                'operations': 0.25,
                'marketing': 0.20,
                'reserve': 0.15
            },
            success_metrics={
                'revenue_growth': 0.08,
                'user_retention': 0.80,
                'adaptation_speed': 0.9
            },
            rollback_plan="若調整無效，評估是否需要啟動 Plan C"
        )
        
        # Plan C: 緊急策略
        self.plans[PlanType.PLAN_C] = EmergencyPlan(
            plan_type=PlanType.PLAN_C,
            name="緊急策略 - 危機應對",
            description="重大技術變革或市場崩潰時的防守策略",
            objective="保護核心資產，確保生存",
            trigger_conditions=['TRIG-0004', 'TRIG-0005', 'TRIG-0006'],
            resource_allocation={
                'development': 0.30,
                'operations': 0.35,
                'marketing': 0.10,
                'reserve': 0.25
            },
            success_metrics={
                'cost_reduction': 0.30,
                'core_user_retention': 0.70,
                'cash_runway_months': 12
            },
            rollback_plan="穩定後逐步恢復正常策略"
        )
        
        # 為每個預案添加默認行動
        self._add_default_actions()
    
    def _add_default_actions(self):
        """添加預設行動項目"""
        # Plan A 行動
        plan_a_actions = [
            ActionItem(
                action_id="ACT-A001",
                title="定期監控關鍵指標",
                description="每週審查 KPI 達成狀況",
                priority=2,
                responsible="產品經理",
                deadline="持續進行"
            ),
            ActionItem(
                action_id="ACT-A002",
                title="維持正常資源配置",
                description="按計畫執行資源分配",
                priority=2,
                responsible="項目經理",
                deadline="持續進行"
            )
        ]
        self.plans[PlanType.PLAN_A].actions = plan_a_actions
        
        # Plan B 行動
        plan_b_actions = [
            ActionItem(
                action_id="ACT-B001",
                title="市場變化評估",
                description="分析市場變化對業務的影響",
                priority=1,
                responsible="市場分析師",
                deadline="觸發後 3 天內"
            ),
            ActionItem(
                action_id="ACT-B002",
                title="技術方向調整",
                description="評估並調整技術發展方向",
                priority=1,
                responsible="技術主管",
                deadline="觸發後 1 週內"
            ),
            ActionItem(
                action_id="ACT-B003",
                title="競爭反制措施",
                description="制定競爭對手動作的反制策略",
                priority=2,
                responsible="策略經理",
                deadline="觸發後 2 週內"
            )
        ]
        self.plans[PlanType.PLAN_B].actions = plan_b_actions
        
        # Plan C 行動
        plan_c_actions = [
            ActionItem(
                action_id="ACT-C001",
                title="停止所有新投資",
                description="暫停非核心項目投資",
                priority=1,
                responsible="財務長",
                deadline="立即"
            ),
            ActionItem(
                action_id="ACT-C002",
                title="核心業務保護",
                description="集中資源保護核心業務",
                priority=1,
                responsible="CEO",
                deadline="觸發後 24 小時內"
            ),
            ActionItem(
                action_id="ACT-C003",
                title="成本削減計畫",
                description="執行緊急成本削減措施",
                priority=1,
                responsible="營運長",
                deadline="觸發後 1 週內"
            ),
            ActionItem(
                action_id="ACT-C004",
                title="危機溝通",
                description="與利害關係人進行危機溝通",
                priority=2,
                responsible="公關主管",
                deadline="觸發後 48 小時內"
            )
        ]
        self.plans[PlanType.PLAN_C].actions = plan_c_actions
    
    def _initialize_default_triggers(self):
        """初始化預設觸發條件"""
        default_triggers = [
            # Plan B 觸發條件
            TriggerCondition(
                trigger_id="TRIG-0001",
                category=TriggerCategory.MARKET_CHANGE,
                name="市場需求下降",
                description="核心市場需求下降超過閾值",
                threshold=20,  # 下降 20%
                target_plan=PlanType.PLAN_B
            ),
            TriggerCondition(
                trigger_id="TRIG-0002",
                category=TriggerCategory.COMPETITOR_ACTION,
                name="競爭對手重大行動",
                description="競爭對手推出破壞性產品或大幅降價",
                threshold=1,  # 發生
                target_plan=PlanType.PLAN_B
            ),
            TriggerCondition(
                trigger_id="TRIG-0003",
                category=TriggerCategory.TECHNOLOGY_SHIFT,
                name="技術發展超出預期",
                description="新技術出現可能改變遊戲規則",
                threshold=1,
                target_plan=PlanType.PLAN_B
            ),
            # Plan C 觸發條件
            TriggerCondition(
                trigger_id="TRIG-0004",
                category=TriggerCategory.MARKET_CHANGE,
                name="市場崩潰",
                description="核心市場嚴重萎縮",
                threshold=50,  # 下降 50%
                target_plan=PlanType.PLAN_C
            ),
            TriggerCondition(
                trigger_id="TRIG-0005",
                category=TriggerCategory.RESOURCE_CONSTRAINT,
                name="資源嚴重緊縮",
                description="可用資源低於維持運營所需",
                threshold=30,  # 資源減少 30%
                target_plan=PlanType.PLAN_C
            ),
            TriggerCondition(
                trigger_id="TRIG-0006",
                category=TriggerCategory.TECHNOLOGY_SHIFT,
                name="重大技術顛覆",
                description="核心技術被徹底顛覆",
                threshold=1,
                target_plan=PlanType.PLAN_C
            )
        ]
        
        for trigger in default_triggers:
            self.triggers[trigger.trigger_id] = trigger
    
    def add_trigger(
        self,
        category: TriggerCategory,
        name: str,
        description: str,
        threshold: float,
        target_plan: PlanType = PlanType.PLAN_B
    ) -> TriggerCondition:
        """添加觸發條件"""
        self._trigger_counter += 1
        trigger = TriggerCondition(
            trigger_id=f"TRIG-{self._trigger_counter:04d}",
            category=category,
            name=name,
            description=description,
            threshold=threshold,
            target_plan=target_plan
        )
        self.triggers[trigger.trigger_id] = trigger
        return trigger
    
    def evaluate_triggers(self, metrics: Dict[str, float]) -> List[TriggerCondition]:
        """評估所有觸發條件"""
        triggered = []
        
        for trigger_id, trigger in self.triggers.items():
            # 根據類別映射到指標
            metric_key = self._get_metric_key(trigger.category)
            if metric_key in metrics:
                if trigger.evaluate(metrics[metric_key]):
                    triggered.append(trigger)
        
        return triggered
    
    def _get_metric_key(self, category: TriggerCategory) -> str:
        """獲取類別對應的指標鍵"""
        mapping = {
            TriggerCategory.MARKET_CHANGE: 'market_decline',
            TriggerCategory.TECHNOLOGY_SHIFT: 'tech_disruption',
            TriggerCategory.COMPETITOR_ACTION: 'competitor_threat',
            TriggerCategory.RESOURCE_CONSTRAINT: 'resource_reduction',
            TriggerCategory.REGULATORY_CHANGE: 'regulatory_risk',
            TriggerCategory.PERFORMANCE_DECLINE: 'performance_drop'
        }
        return mapping.get(category, '')
    
    def activate_plan(self, plan_type: PlanType) -> EmergencyPlan:
        """激活預案"""
        if plan_type in self.plans:
            self.active_plan = plan_type
            return self.plans[plan_type]
        raise ValueError(f"預案 {plan_type.value} 不存在")
    
    def get_active_plan(self) -> EmergencyPlan:
        """獲取當前活動預案"""
        return self.plans.get(self.active_plan)
    
    def recommend_plan(self, metrics: Dict[str, float]) -> PlanType:
        """基於指標推薦預案"""
        triggered = self.evaluate_triggers(metrics)
        
        if not triggered:
            return PlanType.PLAN_A
        
        # 檢查是否有 Plan C 觸發
        plan_c_triggers = [t for t in triggered if t.target_plan == PlanType.PLAN_C]
        if plan_c_triggers:
            return PlanType.PLAN_C
        
        return PlanType.PLAN_B
    
    def generate_response_report(self, format: str = 'markdown') -> str:
        """生成應急響應報告"""
        if format == 'markdown':
            return self._generate_markdown_report()
        else:
            return self._generate_text_report()
    
    def _generate_markdown_report(self) -> str:
        """生成 Markdown 報告"""
        lines = [
            "# 應急預案系統報告",
            f"\n**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\n**當前活動預案**: {self.active_plan.value}",
            "\n## 預案概覽\n"
        ]
        
        for plan_type, plan in self.plans.items():
            emoji = {'plan_a': '🟢', 'plan_b': '🟡', 'plan_c': '🔴'}[plan_type.value]
            active = " **(當前)**" if plan_type == self.active_plan else ""
            lines.extend([
                f"### {emoji} {plan.name}{active}",
                f"**目標**: {plan.objective}",
                f"**描述**: {plan.description}",
                "\n**資源分配**:"
            ])
            for resource, allocation in plan.resource_allocation.items():
                lines.append(f"- {resource}: {allocation*100:.0f}%")
            
            lines.append("\n**關鍵行動**:")
            for action in plan.actions[:3]:  # 顯示前 3 個行動
                lines.append(f"- [{action.priority}] {action.title}")
            lines.append("")
        
        lines.extend([
            "\n## 觸發條件狀態\n",
            "| ID | 名稱 | 類別 | 閾值 | 當前值 | 狀態 |",
            "|---|---|---|---|---|---|"
        ])
        
        for trigger in self.triggers.values():
            status = "🔴 已觸發" if trigger.is_triggered else "🟢 正常"
            lines.append(
                f"| {trigger.trigger_id} | {trigger.name} | "
                f"{trigger.category.value} | {trigger.threshold} | "
                f"{trigger.current_value} | {status} |"
            )
        
        return "\n".join(lines)
    
    def _generate_text_report(self) -> str:
        """生成純文字報告"""
        lines = [
            "=" * 60,
            "應急預案系統報告",
            "=" * 60,
            f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"當前活動預案: {self.active_plan.value}",
            "-" * 60
        ]
        
        for plan_type, plan in self.plans.items():
            lines.extend([
                f"\n[{plan_type.value.upper()}] {plan.name}",
                f"  目標: {plan.objective}",
                f"  描述: {plan.description}"
            ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'generated_at': datetime.now().isoformat(),
            'active_plan': self.active_plan.value,
            'plans': {k.value: v.to_dict() for k, v in self.plans.items()},
            'triggers': {k: v.to_dict() for k, v in self.triggers.items()},
            'triggered_count': len([t for t in self.triggers.values() if t.is_triggered])
        }
