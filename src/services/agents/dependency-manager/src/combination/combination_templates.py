"""
組合範本管理器
Combination Template Manager
"""

from dataclasses import dataclass
from enum import Enum


class TemplateCategory(Enum):
    STEADY_GROWTH = "steady_growth"
    RAPID_MONETIZATION = "rapid_monetization"
    TECH_LEADERSHIP = "tech_leadership"
    BALANCED = "balanced"
    INNOVATION_FOCUSED = "innovation_focused"


class CompanyStage(Enum):
    STARTUP = "startup"
    GROWTH = "growth"
    MATURE = "mature"


@dataclass
class CombinationTemplate:
    id: str
    name: str
    description: str
    category: TemplateCategory
    suitable_stages: list[CompanyStage]
    core_prompt: str
    core_allocation: float
    satellite_prompts: dict[str, float]
    exploration_prompt: str | None
    exploration_allocation: float
    expected_outcomes: list[str]
    risks: list[str]

    def get_total_allocation(self) -> float:
        return self.core_allocation + sum(self.satellite_prompts.values()) + self.exploration_allocation


class CombinationTemplateManager:
    """組合範本管理器"""

    def __init__(self):
        self._templates: dict[str, CombinationTemplate] = {}
        self._load_defaults()

    def _load_defaults(self):
        self._templates['steady_a'] = CombinationTemplate(
            id='steady_a', name='穩健成長型 A', description='長期穩定發展',
            category=TemplateCategory.STEADY_GROWTH,
            suitable_stages=[CompanyStage.GROWTH, CompanyStage.MATURE],
            core_prompt='企業級應用開發', core_allocation=70.0,
            satellite_prompts={'專業級開發': 15.0, '高價值應用': 10.0},
            exploration_prompt='智能化', exploration_allocation=5.0,
            expected_outcomes=['穩固基礎', '客戶信任'], risks=['錯失機會']
        )

        self._templates['rapid_b'] = CombinationTemplate(
            id='rapid_b', name='快速變現型 B', description='快速市場驗證',
            category=TemplateCategory.RAPID_MONETIZATION,
            suitable_stages=[CompanyStage.STARTUP],
            core_prompt='高市場回報', core_allocation=70.0,
            satellite_prompts={'商業導向': 20.0, '企業級': 5.0},
            exploration_prompt='下世代', exploration_allocation=5.0,
            expected_outcomes=['快速驗證', '早期營收'], risks=['技術債務']
        )

    def get_template(self, template_id: str) -> CombinationTemplate | None:
        return self._templates.get(template_id)

    def list_templates(self) -> list[dict]:
        return [{'id': t.id, 'name': t.name, 'category': t.category.value} for t in self._templates.values()]

    def recommend_template(self, stage: CompanyStage, priority: str) -> CombinationTemplate:
        for t in self._templates.values():
            if stage in t.suitable_stages:
                return t
        return list(self._templates.values())[0]
