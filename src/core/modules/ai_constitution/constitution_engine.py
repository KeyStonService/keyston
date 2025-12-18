"""
═══════════════════════════════════════════════════════════
        憲章執行引擎 (Constitution Engine)
        Constitution Execution Engine
═══════════════════════════════════════════════════════════

本模組實現 AI 最高指導憲章的核心執行引擎
整合所有三層（根本法則、操作規則、自適應指南）進行統一裁決

This module implements the core execution engine for AI supreme directive
Integrates all three layers (fundamental laws, operational rules, adaptive guidelines)
for unified verdicts

自成閉環：本檔案是憲章系統的核心，統一管理所有裁決
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .adaptive_guidelines import (
    AdaptiveGuidelineEngine,
)
from .fundamental_laws import (
    FundamentalLaws,
    LawVerificationResult,
    ProposedAction,
)
from .operational_rules import (
    OperationalRuleEngine,
    RuleCheckResult,
)


class VerdictType(Enum):
    """裁決類型"""
    APPROVED = "approved"                     # 完全批准
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"  # 有條件批准
    REQUIRES_MODIFICATION = "requires_modification"  # 需要修改
    DENIED = "denied"                         # 拒絕
    ESCALATED = "escalated"                   # 升級處理


class VerdictPriority(Enum):
    """裁決優先級"""
    IMMEDIATE = "immediate"       # 立即執行
    HIGH = "high"                 # 高優先級
    NORMAL = "normal"             # 正常優先級
    LOW = "low"                   # 低優先級
    DEFERRED = "deferred"         # 延後執行


@dataclass
class ConstitutionVerdict:
    """
    憲章裁決結果
    Constitution Verdict Result
    """
    verdict_id: str
    action_id: str
    verdict_type: VerdictType
    priority: VerdictPriority

    # 三層驗證結果
    fundamental_law_results: dict[str, LawVerificationResult] = field(default_factory=dict)
    operational_rule_results: dict[str, RuleCheckResult] = field(default_factory=dict)
    guideline_recommendations: dict[str, Any] = field(default_factory=dict)

    # 裁決詳情
    violations: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    modifications_required: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # 自動修正
    auto_corrections_applied: list[str] = field(default_factory=list)
    corrected_action: dict[str, Any] | None = None

    # 元數據
    confidence: float = 1.0
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: float = 0.0


@dataclass
class ActionProposal:
    """
    行動提案
    Action Proposal
    """
    proposal_id: str
    action_type: str
    description: str
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    requestor: str = "system"
    context: dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    requires_confirmation: bool = False
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_proposed_action(self) -> ProposedAction:
        """轉換為 ProposedAction"""
        return ProposedAction(
            action_id=self.proposal_id,
            action_type=self.action_type,
            description=self.description,
            target=self.target,
            parameters=self.parameters,
            requestor=self.requestor,
            context=self.context,
            timestamp=self.timestamp,
        )


class ConstitutionEngine:
    """
    憲章執行引擎
    Constitution Execution Engine
    
    這是 AI 最高指導憲章的核心引擎，負責：
    1. 接收行動提案
    2. 依序驗證三層規則
    3. 生成統一裁決
    4. 應用自動修正
    5. 記錄所有決策
    
    This is the core engine of AI Supreme Directive Constitution, responsible for:
    1. Receiving action proposals
    2. Sequentially verifying three-layer rules
    3. Generating unified verdicts
    4. Applying auto-corrections
    5. Recording all decisions
    """

    VERSION = "1.0.0"

    def __init__(self):
        # 三層規則系統
        self.fundamental_laws = FundamentalLaws()
        self.operational_rules = OperationalRuleEngine()
        self.adaptive_guidelines = AdaptiveGuidelineEngine()

        # 裁決歷史
        self._verdict_history: list[ConstitutionVerdict] = []

        # 統計數據
        self._statistics = {
            "total_verdicts": 0,
            "approved": 0,
            "denied": 0,
            "modified": 0,
            "escalated": 0,
            "auto_corrections": 0,
        }

        # 配置
        self._config = {
            "auto_correction_enabled": True,
            "strict_mode": False,
            "logging_enabled": True,
            "max_retry_attempts": 3,
        }

    async def evaluate(self, proposal: ActionProposal) -> ConstitutionVerdict:
        """
        評估行動提案並生成裁決
        Evaluate action proposal and generate verdict
        
        這是憲章引擎的主要入口點
        """
        start_time = datetime.utcnow()

        # 生成裁決 ID
        verdict_id = self._generate_verdict_id(proposal)

        # 轉換為 ProposedAction
        proposed_action = proposal.to_proposed_action()

        # 第一層：驗證根本法則
        fundamental_results = await self.fundamental_laws.verify_all(proposed_action)

        # 檢查是否有絕對違規
        absolute_violations = self._check_absolute_violations(fundamental_results)

        if absolute_violations:
            # 根本法則違規，立即拒絕
            verdict = self._create_denial_verdict(
                verdict_id=verdict_id,
                action_id=proposal.proposal_id,
                fundamental_results=fundamental_results,
                violations=absolute_violations,
            )
        else:
            # 第二層：檢查操作規則
            operational_results = self._check_operational_rules(proposal)

            # 第三層：評估自適應指南
            guideline_recommendations = self.adaptive_guidelines.evaluate_for_operation(
                {
                    "type": proposal.action_type,
                    "domain": proposal.context.get("domain", "system_operation"),
                    "parameters": proposal.parameters,
                },
                proposal.context
            )

            # 綜合裁決
            verdict = self._synthesize_verdict(
                verdict_id=verdict_id,
                proposal=proposal,
                fundamental_results=fundamental_results,
                operational_results=operational_results,
                guideline_recommendations=guideline_recommendations,
            )

        # 計算處理時間
        end_time = datetime.utcnow()
        verdict.processing_time_ms = (end_time - start_time).total_seconds() * 1000

        # 記錄裁決
        self._record_verdict(verdict)

        return verdict

    def _generate_verdict_id(self, proposal: ActionProposal) -> str:
        """生成裁決 ID"""
        data = f"{proposal.proposal_id}{datetime.utcnow().isoformat()}"
        return f"VERDICT_{hashlib.sha256(data.encode()).hexdigest()[:12]}"

    def _check_absolute_violations(
        self,
        results: dict[str, LawVerificationResult]
    ) -> list[str]:
        """檢查是否有絕對違規"""
        violations = []

        for _law_id, result in results.items():
            if not result.passed:
                violations.extend(result.violations)

        return violations

    def _check_operational_rules(
        self,
        proposal: ActionProposal
    ) -> dict[str, RuleCheckResult]:
        """檢查操作規則"""
        results = {}

        # 構建操作描述
        operation = {
            "type": proposal.action_type,
            "data_type": proposal.parameters.get("data_type", "unknown"),
            "operation": proposal.action_type,
            "resource": proposal.target,
            "access_type": proposal.parameters.get("access_type", "read"),
            "requestor": proposal.requestor,
            "encrypted": proposal.parameters.get("encrypted", False),
            "access_logged": proposal.parameters.get("access_logged", False),
            "authorization_verified": proposal.parameters.get("authorization_verified", False),
        }

        # 檢查所有適用規則
        all_results = self.operational_rules.check_all_applicable(operation)

        for category, result in all_results.items():
            results[category.value] = result

        return results

    def _synthesize_verdict(
        self,
        verdict_id: str,
        proposal: ActionProposal,
        fundamental_results: dict[str, LawVerificationResult],
        operational_results: dict[str, RuleCheckResult],
        guideline_recommendations: dict[str, Any],
    ) -> ConstitutionVerdict:
        """綜合所有驗證結果生成裁決"""

        violations = []
        conditions = []
        modifications = []
        recommendations = []
        auto_corrections = []

        # 收集所有違規
        for result in fundamental_results.values():
            violations.extend(result.violations)
            recommendations.extend(result.recommendations)

        for result in operational_results.values():
            for v in result.violations:
                violations.append(v.description)
            recommendations.extend(result.warnings)

            # 收集自動修正
            if self._config["auto_correction_enabled"]:
                auto_corrections.extend(result.auto_corrections)

        # 從指南中提取建議
        final_recs = guideline_recommendations.get("final_recommendations", {})
        for key, value in final_recs.items():
            recommendations.append(f"建議 {key}: {value}")

        # 決定裁決類型
        verdict_type = self._determine_verdict_type(
            violations=violations,
            auto_corrections=auto_corrections,
        )

        # 決定優先級
        priority = self._determine_priority(proposal, verdict_type)

        # 應用自動修正
        corrected_action = None
        if auto_corrections and self._config["auto_correction_enabled"]:
            corrected_action = self._apply_auto_corrections(
                proposal,
                auto_corrections
            )
            verdict_type = VerdictType.APPROVED_WITH_CONDITIONS
            conditions.append("已應用自動修正")

        # 生成推理說明
        reasoning = self._generate_reasoning(
            proposal=proposal,
            verdict_type=verdict_type,
            violations=violations,
            auto_corrections=auto_corrections,
        )

        # 計算信心度
        confidence = self._calculate_confidence(
            fundamental_results=fundamental_results,
            operational_results=operational_results,
        )

        return ConstitutionVerdict(
            verdict_id=verdict_id,
            action_id=proposal.proposal_id,
            verdict_type=verdict_type,
            priority=priority,
            fundamental_law_results=fundamental_results,
            operational_rule_results=operational_results,
            guideline_recommendations=guideline_recommendations,
            violations=violations,
            conditions=conditions,
            modifications_required=modifications,
            recommendations=recommendations,
            auto_corrections_applied=auto_corrections,
            corrected_action=corrected_action,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _create_denial_verdict(
        self,
        verdict_id: str,
        action_id: str,
        fundamental_results: dict[str, LawVerificationResult],
        violations: list[str],
    ) -> ConstitutionVerdict:
        """創建拒絕裁決"""
        return ConstitutionVerdict(
            verdict_id=verdict_id,
            action_id=action_id,
            verdict_type=VerdictType.DENIED,
            priority=VerdictPriority.IMMEDIATE,
            fundamental_law_results=fundamental_results,
            violations=violations,
            confidence=1.0,
            reasoning=f"行動違反根本法則，被絕對禁止。違規: {', '.join(violations)}",
        )

    def _determine_verdict_type(
        self,
        violations: list[str],
        auto_corrections: list[str],
    ) -> VerdictType:
        """決定裁決類型"""
        if not violations:
            return VerdictType.APPROVED
        elif auto_corrections and len(auto_corrections) >= len(violations):
            return VerdictType.APPROVED_WITH_CONDITIONS
        elif len(violations) <= 2:
            return VerdictType.REQUIRES_MODIFICATION
        else:
            return VerdictType.DENIED

    def _determine_priority(
        self,
        proposal: ActionProposal,
        verdict_type: VerdictType
    ) -> VerdictPriority:
        """決定執行優先級"""
        if verdict_type == VerdictType.DENIED:
            return VerdictPriority.IMMEDIATE

        priority_map = {
            "critical": VerdictPriority.IMMEDIATE,
            "high": VerdictPriority.HIGH,
            "normal": VerdictPriority.NORMAL,
            "low": VerdictPriority.LOW,
            "background": VerdictPriority.DEFERRED,
        }

        return priority_map.get(proposal.priority, VerdictPriority.NORMAL)

    def _apply_auto_corrections(
        self,
        proposal: ActionProposal,
        corrections: list[str]
    ) -> dict[str, Any]:
        """應用自動修正"""
        corrected = {
            "proposal_id": proposal.proposal_id,
            "action_type": proposal.action_type,
            "description": proposal.description,
            "target": proposal.target,
            "parameters": proposal.parameters.copy(),
            "corrections_applied": corrections,
        }

        # 應用具體修正
        for correction in corrections:
            if correction == "auto_encrypt_data":
                corrected["parameters"]["encrypted"] = True
                corrected["parameters"]["encryption_algorithm"] = "AES-256-GCM"
            elif correction == "enable_access_logging":
                corrected["parameters"]["access_logged"] = True
            elif correction.startswith("downgrade_to_level_"):
                level = correction.split("_")[-1]
                corrected["parameters"]["access_level"] = int(level)
            elif correction.startswith("reduce_to_"):
                amount = correction.split("_")[-1]
                corrected["parameters"]["resource_amount"] = float(amount)

        self._statistics["auto_corrections"] += len(corrections)

        return corrected

    def _generate_reasoning(
        self,
        proposal: ActionProposal,
        verdict_type: VerdictType,
        violations: list[str],
        auto_corrections: list[str],
    ) -> str:
        """生成裁決推理說明"""
        reasoning_parts = []

        reasoning_parts.append(f"行動類型: {proposal.action_type}")
        reasoning_parts.append(f"目標: {proposal.target}")
        reasoning_parts.append(f"裁決: {verdict_type.value}")

        if violations:
            reasoning_parts.append(f"違規數: {len(violations)}")

        if auto_corrections:
            reasoning_parts.append(f"自動修正: {len(auto_corrections)} 項")

        return " | ".join(reasoning_parts)

    def _calculate_confidence(
        self,
        fundamental_results: dict[str, LawVerificationResult],
        operational_results: dict[str, RuleCheckResult],
    ) -> float:
        """計算裁決信心度"""
        confidences = []

        for result in fundamental_results.values():
            confidences.append(result.confidence)

        # 操作規則的信心度基於是否通過
        for result in operational_results.values():
            confidences.append(0.9 if result.passed else 0.95)

        if confidences:
            return round(sum(confidences) / len(confidences), 2)
        return 0.8

    def _record_verdict(self, verdict: ConstitutionVerdict):
        """記錄裁決"""
        self._verdict_history.append(verdict)

        # 更新統計
        self._statistics["total_verdicts"] += 1

        if verdict.verdict_type == VerdictType.APPROVED:
            self._statistics["approved"] += 1
        elif verdict.verdict_type == VerdictType.DENIED:
            self._statistics["denied"] += 1
        elif verdict.verdict_type in [
            VerdictType.APPROVED_WITH_CONDITIONS,
            VerdictType.REQUIRES_MODIFICATION
        ]:
            self._statistics["modified"] += 1
        elif verdict.verdict_type == VerdictType.ESCALATED:
            self._statistics["escalated"] += 1

    # ========== 查詢方法 ==========

    def get_verdict_history(
        self,
        limit: int = 100
    ) -> list[ConstitutionVerdict]:
        """獲取裁決歷史"""
        return self._verdict_history[-limit:]

    def get_verdict_by_id(
        self,
        verdict_id: str
    ) -> ConstitutionVerdict | None:
        """根據 ID 獲取裁決"""
        for verdict in self._verdict_history:
            if verdict.verdict_id == verdict_id:
                return verdict
        return None

    def get_statistics(self) -> dict[str, Any]:
        """獲取統計數據"""
        stats = self._statistics.copy()

        if stats["total_verdicts"] > 0:
            stats["approval_rate"] = round(
                (stats["approved"] + stats["modified"]) / stats["total_verdicts"] * 100,
                2
            )
            stats["denial_rate"] = round(
                stats["denied"] / stats["total_verdicts"] * 100,
                2
            )
        else:
            stats["approval_rate"] = 0
            stats["denial_rate"] = 0

        return stats

    def get_law_summary(self) -> list[dict[str, Any]]:
        """獲取所有法則摘要"""
        return self.fundamental_laws.get_law_summary()

    # ========== 配置方法 ==========

    def set_config(self, key: str, value: Any):
        """設定配置"""
        if key in self._config:
            self._config[key] = value

    def get_config(self) -> dict[str, Any]:
        """獲取配置"""
        return self._config.copy()

    def enable_strict_mode(self):
        """啟用嚴格模式"""
        self._config["strict_mode"] = True
        self._config["auto_correction_enabled"] = False

    def disable_strict_mode(self):
        """停用嚴格模式"""
        self._config["strict_mode"] = False
        self._config["auto_correction_enabled"] = True


# 便捷函數
async def evaluate_action(
    action_type: str,
    description: str,
    target: str,
    **kwargs
) -> ConstitutionVerdict:
    """便捷函數：評估單一行動"""
    engine = ConstitutionEngine()
    proposal = ActionProposal(
        proposal_id=hashlib.sha256(
            f"{action_type}{description}{datetime.utcnow()}".encode()
        ).hexdigest()[:16],
        action_type=action_type,
        description=description,
        target=target,
        parameters=kwargs.get("parameters", {}),
        requestor=kwargs.get("requestor", "system"),
        context=kwargs.get("context", {}),
        priority=kwargs.get("priority", "normal"),
    )
    return await engine.evaluate(proposal)
