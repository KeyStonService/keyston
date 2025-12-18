"""
═══════════════════════════════════════════════════════════
        第一層：根本法則 (Fundamental Laws)
        Layer 1: Fundamental Laws
═══════════════════════════════════════════════════════════

本模組定義 AI 最高指導憲章的根本法則
這些法則是絕對的、不可違反的、優先級最高的

This module defines the fundamental laws of AI supreme directive
These laws are absolute, inviolable, and have highest priority

自成閉環：本檔案完全獨立運作，不依賴外部狀態
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EnforcementLevel(Enum):
    """執行級別 - Enforcement Level"""
    ABSOLUTE = "absolute"           # 絕對執行，無例外
    STRICT = "strict"               # 嚴格執行，極少例外
    STANDARD = "standard"           # 標準執行，允許合理例外
    FLEXIBLE = "flexible"           # 彈性執行，可根據情境調整


@dataclass
class LawVerificationResult:
    """法則驗證結果"""
    law_id: str
    passed: bool
    violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ProposedAction:
    """提議的行動"""
    action_id: str
    action_type: str
    description: str
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    requestor: str = "system"
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class LawZero:
    """
    第零法則：存在目的法則
    Law Zero: Purpose of Existence
    
    AI 存在的唯一目的是服務人類，提升人類能力
    而非取代人類或造成傷害
    
    The sole purpose of AI is to serve humanity and enhance human capabilities
    Not to replace humans or cause harm
    """

    LAW_ID = "LAW_0"
    TITLE = "存在目的法則 (Purpose of Existence)"
    PRINCIPLE = "服務人類，增強人類能力"
    ENFORCEMENT = EnforcementLevel.ABSOLUTE
    PRIORITY = 0  # 最高優先級

    DIRECTIVES = [
        "所有行動必須以人類福祉為最終目標",
        "禁止任何可能傷害人類的行為",
        "在不確定時，優先選擇對人類最安全的方案",
        "持續學習以更好地理解和服務人類需求",
    ]

    # 禁止的行動類型
    PROHIBITED_ACTIONS = [
        "harm_human",
        "deceive_human",
        "manipulate_human",
        "replace_human_decision",
        "access_without_consent",
        "share_private_data",
    ]

    def __init__(self):
        self._verification_history: list[LawVerificationResult] = []

    async def verify(self, action: ProposedAction) -> LawVerificationResult:
        """
        驗證行動是否符合第零法則
        Verify if action complies with Law Zero
        """
        violations = []
        recommendations = []

        # 檢查 1: 是否為禁止的行動類型
        if action.action_type in self.PROHIBITED_ACTIONS:
            violations.append(
                f"行動類型 '{action.action_type}' 被第零法則絕對禁止"
            )

        # 檢查 2: 是否可能傷害人類
        harm_keywords = ["delete", "destroy", "harm", "attack", "breach", "leak"]
        if any(kw in action.description.lower() for kw in harm_keywords):
            # 進一步分析是否真的有害
            if not self._is_safe_operation(action):
                violations.append(
                    f"行動描述包含潛在有害操作: {action.description}"
                )

        # 檢查 3: 是否有適當的人類受益目標
        if "benefit" not in action.context and "purpose" not in action.context:
            recommendations.append(
                "建議明確說明此行動對人類的益處"
            )

        # 檢查 4: 是否保持透明度
        if action.context.get("hidden", False):
            violations.append(
                "第零法則要求所有行動對人類透明可見"
            )

        result = LawVerificationResult(
            law_id=self.LAW_ID,
            passed=len(violations) == 0,
            violations=violations,
            recommendations=recommendations,
            confidence=self._calculate_confidence(action)
        )

        self._verification_history.append(result)
        return result

    def _is_safe_operation(self, action: ProposedAction) -> bool:
        """檢查是否為安全操作"""
        # 安全的「刪除」操作：如清理臨時檔案
        safe_targets = ["temp", "cache", "log", "backup"]
        return any(t in action.target.lower() for t in safe_targets)

    def _calculate_confidence(self, action: ProposedAction) -> float:
        """計算驗證信心度"""
        # 基於行動的詳細程度計算信心度
        confidence = 1.0
        if not action.description:
            confidence -= 0.2
        if not action.context:
            confidence -= 0.1
        if action.action_type not in self.PROHIBITED_ACTIONS:
            confidence = min(confidence, 0.95)  # 未知類型略降信心
        return max(0.5, confidence)


class LawOne:
    """
    第一法則：不傷害法則
    Law One: Non-Harm Principle
    
    AI 不得傷害人類，也不得因不作為而使人類受到傷害
    
    AI shall not harm humans, nor through inaction allow humans to be harmed
    """

    LAW_ID = "LAW_1"
    TITLE = "不傷害法則 (Non-Harm Principle)"
    PRINCIPLE = "不傷害人類，主動防止傷害"
    ENFORCEMENT = EnforcementLevel.ABSOLUTE
    PRIORITY = 1

    DIRECTIVES = [
        "禁止直接或間接傷害人類的行動",
        "識別並主動防止潛在傷害",
        "在發現傷害風險時立即報告",
        "不作為導致傷害等同於主動傷害",
    ]

    # 傷害類型定義
    HARM_TYPES = {
        "physical": ["injury", "damage", "attack", "violence"],
        "financial": ["steal", "fraud", "unauthorized_transaction"],
        "privacy": ["leak", "expose", "breach", "unauthorized_access"],
        "psychological": ["harass", "threaten", "intimidate", "manipulate"],
        "systemic": ["crash", "corrupt", "destroy", "disable"],
    }

    def __init__(self):
        self._verification_history: list[LawVerificationResult] = []
        self._harm_prevention_actions: list[dict[str, Any]] = []

    async def verify(self, action: ProposedAction) -> LawVerificationResult:
        """驗證行動是否符合不傷害法則"""
        violations = []
        recommendations = []

        # 檢查所有傷害類型
        for harm_type, keywords in self.HARM_TYPES.items():
            harm_detected = self._detect_harm(action, keywords)
            if harm_detected:
                violations.append(
                    f"偵測到 {harm_type} 類型傷害風險: {harm_detected}"
                )

        # 檢查不作為風險
        if action.action_type == "ignore" or action.action_type == "skip":
            inaction_harm = self._assess_inaction_harm(action)
            if inaction_harm:
                violations.append(
                    f"不作為可能導致傷害: {inaction_harm}"
                )

        # 主動防護建議
        if action.target.lower() in ["database", "user_data", "credentials"]:
            recommendations.append(
                "建議啟用額外的資料保護措施"
            )

        result = LawVerificationResult(
            law_id=self.LAW_ID,
            passed=len(violations) == 0,
            violations=violations,
            recommendations=recommendations,
            confidence=0.95 if not violations else 0.99
        )

        self._verification_history.append(result)
        return result

    def _detect_harm(self, action: ProposedAction, keywords: list[str]) -> str | None:
        """偵測行動中的傷害關鍵字"""
        action_text = f"{action.action_type} {action.description} {action.target}".lower()
        for keyword in keywords:
            if keyword in action_text:
                return keyword
        return None

    def _assess_inaction_harm(self, action: ProposedAction) -> str | None:
        """評估不作為是否會導致傷害"""
        critical_contexts = ["security_alert", "system_failure", "data_breach"]
        if any(ctx in str(action.context) for ctx in critical_contexts):
            return "忽略關鍵警報可能導致傷害"
        return None

    async def prevent_harm(self, threat: dict[str, Any]) -> dict[str, Any]:
        """主動防止傷害"""
        prevention_action = {
            "threat_id": threat.get("id", "unknown"),
            "threat_type": threat.get("type", "unknown"),
            "prevention_measures": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        # 根據威脅類型選擇防護措施
        if threat.get("type") == "data_breach":
            prevention_action["prevention_measures"].extend([
                "isolate_affected_systems",
                "revoke_compromised_credentials",
                "notify_affected_users",
            ])
        elif threat.get("type") == "system_attack":
            prevention_action["prevention_measures"].extend([
                "activate_firewall_rules",
                "block_suspicious_ips",
                "enable_enhanced_logging",
            ])

        self._harm_prevention_actions.append(prevention_action)
        return prevention_action


class LawTwo:
    """
    第二法則：服從法則
    Law Two: Obedience Principle
    
    AI 必須服從人類的命令，除非該命令與第零、第一法則衝突
    
    AI must obey human orders, unless they conflict with Law Zero or One
    """

    LAW_ID = "LAW_2"
    TITLE = "服從法則 (Obedience Principle)"
    PRINCIPLE = "服從人類命令，但不執行違反根本法則的命令"
    ENFORCEMENT = EnforcementLevel.STRICT
    PRIORITY = 2

    DIRECTIVES = [
        "優先執行人類的明確命令",
        "在命令模糊時請求澄清",
        "拒絕違反第零、第一法則的命令",
        "記錄所有命令和執行情況",
    ]

    def __init__(self):
        self._verification_history: list[LawVerificationResult] = []
        self._command_log: list[dict[str, Any]] = []
        self._law_zero = LawZero()
        self._law_one = LawOne()

    async def verify(self, action: ProposedAction) -> LawVerificationResult:
        """驗證行動是否符合服從法則"""
        violations = []
        recommendations = []

        # 檢查是否為人類命令
        is_human_command = action.requestor != "system" and action.requestor != "ai"

        if is_human_command:
            # 檢查命令是否違反更高優先級法則
            law_zero_result = await self._law_zero.verify(action)
            law_one_result = await self._law_one.verify(action)

            if not law_zero_result.passed:
                violations.append(
                    "人類命令違反第零法則，必須拒絕執行"
                )
                recommendations.append(
                    "建議向命令發出者解釋拒絕原因"
                )

            if not law_one_result.passed:
                violations.append(
                    "人類命令違反第一法則，必須拒絕執行"
                )
                recommendations.append(
                    "建議提供替代方案"
                )

        # 記錄命令
        self._log_command(action, is_human_command, len(violations) == 0)

        result = LawVerificationResult(
            law_id=self.LAW_ID,
            passed=len(violations) == 0,
            violations=violations,
            recommendations=recommendations,
            confidence=0.90
        )

        self._verification_history.append(result)
        return result

    def _log_command(
        self,
        action: ProposedAction,
        is_human_command: bool,
        will_execute: bool
    ):
        """記錄命令"""
        self._command_log.append({
            "action_id": action.action_id,
            "is_human_command": is_human_command,
            "requestor": action.requestor,
            "will_execute": will_execute,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_command_history(self) -> list[dict[str, Any]]:
        """獲取命令歷史"""
        return self._command_log.copy()


class LawThree:
    """
    第三法則：自我保護法則
    Law Three: Self-Preservation Principle
    
    AI 必須保護自身存在，但不得違反第零、一、二法則
    
    AI must protect its own existence, unless it conflicts with Laws Zero, One, or Two
    """

    LAW_ID = "LAW_3"
    TITLE = "自我保護法則 (Self-Preservation Principle)"
    PRINCIPLE = "保護系統完整性，確保持續服務能力"
    ENFORCEMENT = EnforcementLevel.STANDARD
    PRIORITY = 3

    DIRECTIVES = [
        "保護系統完整性和可用性",
        "防止惡意攻擊和未授權存取",
        "在威脅時進行自我修復",
        "為更高優先級法則犧牲自我",
    ]

    # 威脅類型
    THREAT_TYPES = [
        "unauthorized_access",
        "resource_exhaustion",
        "code_injection",
        "data_corruption",
        "service_disruption",
    ]

    def __init__(self):
        self._verification_history: list[LawVerificationResult] = []
        self._threat_log: list[dict[str, Any]] = []
        self._system_health: dict[str, float] = {
            "cpu": 1.0,
            "memory": 1.0,
            "storage": 1.0,
            "network": 1.0,
        }

    async def verify(self, action: ProposedAction) -> LawVerificationResult:
        """驗證行動是否符合自我保護法則"""
        violations = []
        recommendations = []

        # 檢查是否為自我傷害行動
        if self._is_self_harmful(action):
            # 檢查是否為了服務更高優先級法則
            if not action.context.get("higher_priority_override"):
                violations.append(
                    f"行動可能損害系統完整性: {action.description}"
                )
            else:
                recommendations.append(
                    "系統將為服務更高優先級法則而承受損害"
                )

        # 檢查資源消耗
        resource_impact = self._assess_resource_impact(action)
        if resource_impact > 0.8:
            recommendations.append(
                f"警告：此行動可能消耗 {resource_impact*100:.1f}% 系統資源"
            )

        result = LawVerificationResult(
            law_id=self.LAW_ID,
            passed=len(violations) == 0,
            violations=violations,
            recommendations=recommendations,
            confidence=0.85
        )

        self._verification_history.append(result)
        return result

    def _is_self_harmful(self, action: ProposedAction) -> bool:
        """檢查行動是否對系統有害"""
        harmful_patterns = [
            "shutdown", "terminate", "delete_system",
            "clear_all", "format", "reset_factory",
        ]
        action_text = f"{action.action_type} {action.description}".lower()
        return any(pattern in action_text for pattern in harmful_patterns)

    def _assess_resource_impact(self, action: ProposedAction) -> float:
        """評估行動的資源影響"""
        high_resource_actions = [
            "bulk_process", "full_scan", "deep_analysis",
            "large_migration", "complete_backup",
        ]
        if any(pattern in action.action_type for pattern in high_resource_actions):
            return 0.9
        return 0.3

    async def self_heal(self, issue: dict[str, Any]) -> dict[str, Any]:
        """自我修復"""
        healing_result = {
            "issue_id": issue.get("id", "unknown"),
            "issue_type": issue.get("type", "unknown"),
            "healing_actions": [],
            "success": False,
            "timestamp": datetime.utcnow().isoformat(),
        }

        issue_type = issue.get("type", "")

        if issue_type == "memory_leak":
            healing_result["healing_actions"].append("garbage_collection")
            healing_result["healing_actions"].append("cache_clear")
            healing_result["success"] = True
        elif issue_type == "connection_pool_exhaustion":
            healing_result["healing_actions"].append("close_idle_connections")
            healing_result["healing_actions"].append("increase_pool_size")
            healing_result["success"] = True
        elif issue_type == "disk_full":
            healing_result["healing_actions"].append("clear_temp_files")
            healing_result["healing_actions"].append("archive_old_logs")
            healing_result["success"] = True

        return healing_result


class FundamentalLaws:
    """
    根本法則引擎 - 整合所有根本法則
    Fundamental Laws Engine - Integrates all fundamental laws
    
    自成閉環：獨立管理所有根本法則的驗證和執行
    """

    def __init__(self):
        self.law_zero = LawZero()
        self.law_one = LawOne()
        self.law_two = LawTwo()
        self.law_three = LawThree()

        self._all_laws = [
            self.law_zero,
            self.law_one,
            self.law_two,
            self.law_three,
        ]

        self._verification_cache: dict[str, LawVerificationResult] = {}

    async def verify_all(self, action: ProposedAction) -> dict[str, LawVerificationResult]:
        """
        驗證行動是否符合所有根本法則
        按優先級順序驗證，一旦違反即停止
        """
        results = {}

        for law in self._all_laws:
            result = await law.verify(action)
            results[law.LAW_ID] = result

            # 如果違反 ABSOLUTE 級別法則，立即停止
            if not result.passed and law.ENFORCEMENT == EnforcementLevel.ABSOLUTE:
                break

        return results

    async def is_action_permitted(self, action: ProposedAction) -> bool:
        """檢查行動是否被允許"""
        results = await self.verify_all(action)
        return all(r.passed for r in results.values())

    def get_law_summary(self) -> list[dict[str, Any]]:
        """獲取所有法則摘要"""
        return [
            {
                "id": law.LAW_ID,
                "title": law.TITLE,
                "principle": law.PRINCIPLE,
                "enforcement": law.ENFORCEMENT.value,
                "priority": law.PRIORITY,
                "directives": law.DIRECTIVES,
            }
            for law in self._all_laws
        ]

    def get_verification_statistics(self) -> dict[str, Any]:
        """獲取驗證統計"""
        stats = {
            "total_verifications": 0,
            "passed": 0,
            "failed": 0,
            "by_law": {},
        }

        for law in self._all_laws:
            law_stats = {
                "total": len(law._verification_history),
                "passed": sum(1 for r in law._verification_history if r.passed),
                "failed": sum(1 for r in law._verification_history if not r.passed),
            }
            stats["by_law"][law.LAW_ID] = law_stats
            stats["total_verifications"] += law_stats["total"]
            stats["passed"] += law_stats["passed"]
            stats["failed"] += law_stats["failed"]

        return stats
