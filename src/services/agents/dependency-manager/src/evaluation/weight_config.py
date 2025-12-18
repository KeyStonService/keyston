"""
權重配置管理器

根據公司階段提供不同的評估權重配置。
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CompanyStage(Enum):
    """公司發展階段"""
    STARTUP = "startup"           # 初創期
    GROWTH = "growth"             # 成長期
    ENTERPRISE = "enterprise"     # 成熟企業
    INNOVATION = "innovation"     # 創新轉型
    RESTRUCTURING = "restructuring"  # 重組期


@dataclass
class WeightProfile:
    """權重配置檔"""
    name: str
    stage: CompanyStage
    weights: dict[str, float]
    description: str
    use_cases: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "stage": self.stage.value,
            "weights": self.weights,
            "description": self.description,
            "use_cases": self.use_cases,
            "created_at": self.created_at
        }


class WeightConfigManager:
    """權重配置管理器"""

    # 預設權重配置
    PRESET_CONFIGS = {
        CompanyStage.STARTUP: {
            "scalability": 0.10,
            "market_fit": 0.25,
            "achievability": 0.20,
            "roi": 0.25,
            "technology_maturity": 0.05,
            "value_creation": 0.15,
        },
        CompanyStage.GROWTH: {
            "scalability": 0.20,
            "market_fit": 0.20,
            "achievability": 0.15,
            "roi": 0.20,
            "technology_maturity": 0.10,
            "value_creation": 0.15,
        },
        CompanyStage.ENTERPRISE: {
            "scalability": 0.25,
            "market_fit": 0.15,
            "achievability": 0.05,
            "roi": 0.15,
            "technology_maturity": 0.20,
            "value_creation": 0.20,
        },
        CompanyStage.INNOVATION: {
            "scalability": 0.15,
            "market_fit": 0.20,
            "achievability": 0.10,
            "roi": 0.15,
            "technology_maturity": 0.15,
            "value_creation": 0.25,
        },
        CompanyStage.RESTRUCTURING: {
            "scalability": 0.10,
            "market_fit": 0.15,
            "achievability": 0.25,
            "roi": 0.30,
            "technology_maturity": 0.10,
            "value_creation": 0.10,
        },
    }

    # 權重描述
    WEIGHT_DESCRIPTIONS = {
        "scalability": "可擴展性 - 評估技術架構、用戶增長潛力、負載能力",
        "market_fit": "市場適配度 - 評估用戶需求匹配、市場時機、競爭環境",
        "achievability": "可實現性 - 評估團隊能力、預算時程、技術風險",
        "roi": "投資報酬率 - 評估財務回報、成本效益、資源效率",
        "technology_maturity": "技術成熟度 - 評估技術穩定性、生態系統、學習曲線",
        "value_creation": "價值創造 - 評估競爭優勢、品牌價值、創新影響",
    }

    def __init__(self):
        self.custom_profiles: dict[str, WeightProfile] = {}

    def get_preset_weights(self, stage: CompanyStage) -> dict[str, float]:
        """獲取預設權重"""
        return self.PRESET_CONFIGS.get(stage, self.PRESET_CONFIGS[CompanyStage.GROWTH])

    def create_custom_profile(
        self,
        name: str,
        stage: CompanyStage,
        weights: dict[str, float],
        description: str = "",
        use_cases: list[str] | None = None
    ) -> WeightProfile:
        """創建自定義權重配置"""
        # 驗證權重
        self._validate_weights(weights)

        profile = WeightProfile(
            name=name,
            stage=stage,
            weights=self._normalize_weights(weights),
            description=description,
            use_cases=use_cases or []
        )

        self.custom_profiles[name] = profile
        return profile

    def get_profile(self, name: str) -> WeightProfile | None:
        """獲取權重配置"""
        return self.custom_profiles.get(name)

    def list_profiles(self) -> list[str]:
        """列出所有自定義配置"""
        return list(self.custom_profiles.keys())

    def _validate_weights(self, weights: dict[str, float]) -> None:
        """驗證權重配置"""
        required_keys = set(self.WEIGHT_DESCRIPTIONS.keys())
        provided_keys = set(weights.keys())

        missing = required_keys - provided_keys
        if missing:
            raise ValueError(f"缺少必要的權重維度: {missing}")

        for key, value in weights.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"權重值必須為數字: {key}")
            if value < 0:
                raise ValueError(f"權重值不能為負數: {key}")

    def _normalize_weights(self, weights: dict[str, float]) -> dict[str, float]:
        """正規化權重（總和為 1）"""
        total = sum(weights.values())
        if total == 0:
            # 如果總和為 0，返回均勻分配
            n = len(weights)
            return dict.fromkeys(weights, 1.0 / n)
        return {k: v / total for k, v in weights.items()}

    def suggest_weights(
        self,
        priorities: dict[str, int]  # 1-5 的優先級
    ) -> dict[str, float]:
        """根據優先級建議權重"""
        # 將優先級轉換為權重
        weights = {}
        for dimension, priority in priorities.items():
            if dimension in self.WEIGHT_DESCRIPTIONS:
                # 優先級 1-5 對應權重 0.1-0.5
                weights[dimension] = 0.1 + (priority - 1) * 0.1

        # 補充未提供的維度
        for dim in self.WEIGHT_DESCRIPTIONS:
            if dim not in weights:
                weights[dim] = 0.15  # 預設中等權重

        return self._normalize_weights(weights)

    def compare_profiles(
        self,
        profile_names: list[str]
    ) -> dict[str, dict[str, float]]:
        """比較多個權重配置"""
        comparison = {}
        for name in profile_names:
            profile = self.custom_profiles.get(name)
            if profile:
                comparison[name] = profile.weights
        return comparison

    def export_profile(self, name: str) -> str | None:
        """導出權重配置為 JSON"""
        profile = self.custom_profiles.get(name)
        if profile:
            return json.dumps(profile.to_dict(), ensure_ascii=False, indent=2)
        return None

    def import_profile(self, json_str: str) -> WeightProfile:
        """從 JSON 導入權重配置"""
        data = json.loads(json_str)
        return self.create_custom_profile(
            name=data["name"],
            stage=CompanyStage(data["stage"]),
            weights=data["weights"],
            description=data.get("description", ""),
            use_cases=data.get("use_cases", [])
        )

    def get_stage_description(self, stage: CompanyStage) -> str:
        """獲取階段描述"""
        descriptions = {
            CompanyStage.STARTUP: "初創期：專注於產品市場適配和快速驗證商業模式",
            CompanyStage.GROWTH: "成長期：平衡擴展需求和資源效率，追求穩定增長",
            CompanyStage.ENTERPRISE: "成熟企業：重視可擴展性、技術穩定性和長期價值",
            CompanyStage.INNOVATION: "創新轉型：強調價值創造和市場適配，追求突破性創新",
            CompanyStage.RESTRUCTURING: "重組期：優先考慮可實現性和投資回報，降低風險",
        }
        return descriptions.get(stage, "")

    def get_all_weight_descriptions(self) -> dict[str, str]:
        """獲取所有權重維度的描述"""
        return self.WEIGHT_DESCRIPTIONS.copy()
