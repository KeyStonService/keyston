"""
政策模擬沙箱 - Policy Simulation Sandbox
模擬不同更新策略的影響
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..models.dependency import Dependency, DependencyAnalysis
from ..models.update import Update, UpdatePolicy, UpdateType

logger = logging.getLogger(__name__)


class SimulationMode(Enum):
    """模擬模式"""
    CONSERVATIVE = "conservative"   # 保守模式：僅更新 patch
    BALANCED = "balanced"          # 平衡模式：自動 patch，PR minor
    AGGRESSIVE = "aggressive"      # 積極模式：自動 patch + minor
    SECURITY_ONLY = "security_only"  # 安全優先：僅更新有漏洞的依賴


@dataclass
class SimulationScenario:
    """
    模擬情境
    
    Attributes:
        name: 情境名稱
        mode: 模擬模式
        description: 情境描述
        update_policy: 更新策略配置
    """
    name: str
    mode: SimulationMode
    description: str = ""
    update_policy: dict[str, UpdatePolicy] = field(default_factory=dict)

    @classmethod
    def conservative(cls) -> "SimulationScenario":
        """保守模式情境"""
        return cls(
            name="保守更新",
            mode=SimulationMode.CONSERVATIVE,
            description="僅自動更新 patch 版本，其他需要人工審查",
            update_policy={
                "patch": UpdatePolicy.AUTO,
                "minor": UpdatePolicy.MANUAL,
                "major": UpdatePolicy.MANUAL
            }
        )

    @classmethod
    def balanced(cls) -> "SimulationScenario":
        """平衡模式情境"""
        return cls(
            name="平衡更新",
            mode=SimulationMode.BALANCED,
            description="自動更新 patch，minor 建立 PR，major 需人工審查",
            update_policy={
                "patch": UpdatePolicy.AUTO,
                "minor": UpdatePolicy.PR,
                "major": UpdatePolicy.MANUAL
            }
        )

    @classmethod
    def aggressive(cls) -> "SimulationScenario":
        """積極模式情境"""
        return cls(
            name="積極更新",
            mode=SimulationMode.AGGRESSIVE,
            description="自動更新 patch 和 minor，major 建立 PR",
            update_policy={
                "patch": UpdatePolicy.AUTO,
                "minor": UpdatePolicy.AUTO,
                "major": UpdatePolicy.PR
            }
        )

    @classmethod
    def security_only(cls) -> "SimulationScenario":
        """安全優先情境"""
        return cls(
            name="安全優先",
            mode=SimulationMode.SECURITY_ONLY,
            description="僅更新有安全漏洞的依賴項",
            update_policy={
                "patch": UpdatePolicy.SKIP,
                "minor": UpdatePolicy.SKIP,
                "major": UpdatePolicy.SKIP,
                "security": UpdatePolicy.AUTO
            }
        )


@dataclass
class SimulationResult:
    """
    模擬結果
    
    Attributes:
        scenario: 模擬情境
        timestamp: 模擬時間
        total_dependencies: 總依賴數
        updates_proposed: 建議的更新列表
        auto_updates: 自動更新數
        pr_updates: 需要 PR 的更新數
        manual_updates: 需要人工審查的更新數
        skipped_updates: 跳過的更新數
        risk_score: 風險評分 (0-100)
        estimated_time_hours: 預估處理時間（小時）
    """
    scenario: SimulationScenario
    timestamp: datetime = field(default_factory=datetime.utcnow)
    total_dependencies: int = 0
    updates_proposed: list[Update] = field(default_factory=list)
    auto_updates: int = 0
    pr_updates: int = 0
    manual_updates: int = 0
    skipped_updates: int = 0
    risk_score: float = 0.0
    estimated_time_hours: float = 0.0
    breaking_changes_risk: int = 0

    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "scenario": {
                "name": self.scenario.name,
                "mode": self.scenario.mode.value,
                "description": self.scenario.description
            },
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total_dependencies": self.total_dependencies,
                "total_updates": len(self.updates_proposed),
                "auto_updates": self.auto_updates,
                "pr_updates": self.pr_updates,
                "manual_updates": self.manual_updates,
                "skipped_updates": self.skipped_updates
            },
            "risk_assessment": {
                "risk_score": self.risk_score,
                "breaking_changes_risk": self.breaking_changes_risk,
                "estimated_time_hours": self.estimated_time_hours
            },
            "updates": [u.to_dict() for u in self.updates_proposed]
        }


class PolicySimulator:
    """
    政策模擬器
    
    模擬不同更新策略對專案的影響，幫助團隊做出明智的決策
    """

    # 預估處理時間（分鐘）
    TIME_ESTIMATES = {
        UpdatePolicy.AUTO: 0.5,      # 自動更新：30 秒
        UpdatePolicy.PR: 15,         # PR 審查：15 分鐘
        UpdatePolicy.MANUAL: 60,     # 人工處理：1 小時
        UpdatePolicy.SKIP: 0         # 跳過：無時間
    }

    # 風險權重
    RISK_WEIGHTS = {
        UpdateType.MAJOR: 30,    # major 更新風險最高
        UpdateType.MINOR: 10,    # minor 更新中等風險
        UpdateType.PATCH: 2,     # patch 更新低風險
        UpdateType.SECURITY: 5   # 安全更新需要快速處理
    }

    def __init__(self):
        """初始化模擬器"""
        self._scenarios: list[SimulationScenario] = [
            SimulationScenario.conservative(),
            SimulationScenario.balanced(),
            SimulationScenario.aggressive(),
            SimulationScenario.security_only()
        ]
        logger.info("政策模擬器初始化完成")

    def simulate(
        self,
        analysis: DependencyAnalysis,
        scenario: SimulationScenario
    ) -> SimulationResult:
        """
        執行單一情境模擬
        
        Args:
            analysis: 依賴分析結果
            scenario: 模擬情境
            
        Returns:
            模擬結果
        """
        logger.info(f"開始模擬: {scenario.name}")

        result = SimulationResult(
            scenario=scenario,
            total_dependencies=analysis.total_count
        )

        # 模擬每個過時依賴的更新
        for dep in analysis.dependencies:
            if not dep.is_outdated() and not dep.has_vulnerability:
                continue

            update = self._simulate_update(dep, scenario)
            if update:
                result.updates_proposed.append(update)

                # 統計各類更新
                if update.policy == UpdatePolicy.AUTO:
                    result.auto_updates += 1
                elif update.policy == UpdatePolicy.PR:
                    result.pr_updates += 1
                elif update.policy == UpdatePolicy.MANUAL:
                    result.manual_updates += 1
                else:
                    result.skipped_updates += 1

        # 計算風險評分
        result.risk_score = self._calculate_risk_score(result)

        # 計算預估時間
        result.estimated_time_hours = self._estimate_time(result)

        # 計算破壞性變更風險
        result.breaking_changes_risk = sum(
            1 for u in result.updates_proposed
            if u.update_type == UpdateType.MAJOR
        )

        logger.info(
            f"模擬完成: {len(result.updates_proposed)} 個更新, "
            f"風險評分: {result.risk_score:.1f}"
        )

        return result

    def simulate_all(
        self,
        analysis: DependencyAnalysis
    ) -> list[SimulationResult]:
        """
        執行所有預設情境模擬
        
        Args:
            analysis: 依賴分析結果
            
        Returns:
            所有情境的模擬結果
        """
        results = []
        for scenario in self._scenarios:
            result = self.simulate(analysis, scenario)
            results.append(result)

        return results

    def compare_scenarios(
        self,
        results: list[SimulationResult]
    ) -> dict[str, Any]:
        """
        比較不同情境的結果
        
        Args:
            results: 模擬結果列表
            
        Returns:
            比較分析
        """
        comparison = {
            "scenarios": [],
            "recommendation": None,
            "analysis": {}
        }

        for result in results:
            comparison["scenarios"].append({
                "name": result.scenario.name,
                "mode": result.scenario.mode.value,
                "total_updates": len(result.updates_proposed),
                "auto_updates": result.auto_updates,
                "risk_score": result.risk_score,
                "estimated_time_hours": result.estimated_time_hours,
                "breaking_changes": result.breaking_changes_risk
            })

        # 計算推薦情境
        comparison["recommendation"] = self._recommend_scenario(results)

        # 綜合分析
        comparison["analysis"] = {
            "lowest_risk": min(results, key=lambda r: r.risk_score).scenario.name,
            "fastest": min(results, key=lambda r: r.estimated_time_hours).scenario.name,
            "most_automated": max(results, key=lambda r: r.auto_updates).scenario.name
        }

        return comparison

    def _simulate_update(
        self,
        dep: Dependency,
        scenario: SimulationScenario
    ) -> Update | None:
        """
        模擬單個依賴的更新
        
        Args:
            dep: 依賴項
            scenario: 模擬情境
            
        Returns:
            模擬的更新對象
        """
        if not dep.latest_version:
            return None

        # 判斷更新類型
        update_type = self._classify_update_type(
            dep.current_version,
            dep.latest_version
        )

        # 安全優先模式特殊處理
        if scenario.mode == SimulationMode.SECURITY_ONLY:
            if not dep.has_vulnerability:
                return None
            policy = scenario.update_policy.get("security", UpdatePolicy.AUTO)
        else:
            # 根據更新類型獲取策略
            type_key = update_type.value.lower()
            policy = scenario.update_policy.get(type_key, UpdatePolicy.MANUAL)

        return Update(
            package=dep.name,
            from_version=dep.current_version,
            to_version=dep.latest_version,
            update_type=update_type,
            policy=policy,
            is_security_fix=dep.has_vulnerability,
            breaking_changes=(update_type == UpdateType.MAJOR)
        )

    def _classify_update_type(self, current: str, latest: str) -> UpdateType:
        """
        分類更新類型
        
        Args:
            current: 當前版本
            latest: 最新版本
            
        Returns:
            更新類型
        """
        def parse_version(v: str) -> tuple:
            # 移除 v 前綴
            if v.startswith('v'):
                v = v[1:]

            parts = v.split('.')
            try:
                return (
                    int(parts[0]) if len(parts) > 0 else 0,
                    int(parts[1]) if len(parts) > 1 else 0,
                    int(parts[2].split('-')[0]) if len(parts) > 2 else 0
                )
            except ValueError:
                return (0, 0, 0)

        curr = parse_version(current)
        lat = parse_version(latest)

        if lat[0] > curr[0]:
            return UpdateType.MAJOR
        elif lat[1] > curr[1]:
            return UpdateType.MINOR
        else:
            return UpdateType.PATCH

    def _calculate_risk_score(self, result: SimulationResult) -> float:
        """
        計算風險評分
        
        Args:
            result: 模擬結果
            
        Returns:
            風險評分 (0-100)
        """
        if not result.updates_proposed:
            return 0.0

        total_risk = 0.0

        for update in result.updates_proposed:
            # 基礎風險
            base_risk = self.RISK_WEIGHTS.get(update.update_type, 5)

            # 自動更新增加風險
            if update.policy == UpdatePolicy.AUTO:
                base_risk *= 1.5

            # 安全修復降低風險
            if update.is_security_fix:
                base_risk *= 0.7

            total_risk += base_risk

        # 正規化到 0-100
        max_possible = len(result.updates_proposed) * 30 * 1.5
        score = (total_risk / max_possible) * 100 if max_possible > 0 else 0

        return min(100.0, score)

    def _estimate_time(self, result: SimulationResult) -> float:
        """
        估算處理時間
        
        Args:
            result: 模擬結果
            
        Returns:
            預估時間（小時）
        """
        total_minutes = 0.0

        for update in result.updates_proposed:
            time = self.TIME_ESTIMATES.get(update.policy, 0)
            total_minutes += time

        return total_minutes / 60.0

    def _recommend_scenario(
        self,
        results: list[SimulationResult]
    ) -> dict[str, Any]:
        """
        推薦最佳情境
        
        基於風險、時間、自動化程度綜合評估
        
        Args:
            results: 所有模擬結果
            
        Returns:
            推薦結果
        """
        if not results:
            return {"scenario": None, "reason": "無模擬結果"}

        # 計算綜合分數（越低越好）
        def calculate_score(r: SimulationResult) -> float:
            # 風險佔 40%
            risk_factor = r.risk_score * 0.4
            # 時間佔 30%
            time_factor = (r.estimated_time_hours * 10) * 0.3
            # 人工介入佔 30%
            manual_factor = (r.manual_updates * 5) * 0.3
            return risk_factor + time_factor + manual_factor

        scores = [(r, calculate_score(r)) for r in results]
        best = min(scores, key=lambda x: x[1])

        return {
            "scenario": best[0].scenario.name,
            "mode": best[0].scenario.mode.value,
            "reason": f"綜合評分最優（風險 {best[0].risk_score:.1f}, "
                     f"時間 {best[0].estimated_time_hours:.1f}h）",
            "score": best[1]
        }

    def add_custom_scenario(self, scenario: SimulationScenario) -> None:
        """
        添加自定義情境
        
        Args:
            scenario: 自定義模擬情境
        """
        self._scenarios.append(scenario)
        logger.info(f"已添加自定義情境: {scenario.name}")

    def generate_report(
        self,
        results: list[SimulationResult],
        lang: str = "zh-TW"
    ) -> str:
        """
        生成模擬報告
        
        Args:
            results: 模擬結果列表
            lang: 語言（預設繁體中文）
            
        Returns:
            格式化報告
        """
        lines = [
            "=" * 60,
            "📊 政策模擬報告",
            "=" * 60,
            ""
        ]

        for result in results:
            lines.extend([
                f"📋 情境: {result.scenario.name}",
                f"   模式: {result.scenario.mode.value}",
                f"   描述: {result.scenario.description}",
                "",
                "   📈 統計：",
                f"      總更新數: {len(result.updates_proposed)}",
                f"      自動更新: {result.auto_updates}",
                f"      需要 PR: {result.pr_updates}",
                f"      人工審查: {result.manual_updates}",
                "",
                "   ⚠️ 風險評估：",
                f"      風險評分: {result.risk_score:.1f}/100",
                f"      破壞性變更: {result.breaking_changes_risk}",
                f"      預估時間: {result.estimated_time_hours:.1f} 小時",
                "",
                "-" * 40,
                ""
            ])

        # 添加推薦
        comparison = self.compare_scenarios(results)
        lines.extend([
            "🎯 推薦策略",
            f"   推薦情境: {comparison['recommendation']['scenario']}",
            f"   原因: {comparison['recommendation']['reason']}",
            "",
            "=" * 60
        ])

        return "\n".join(lines)
