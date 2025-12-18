"""
═══════════════════════════════════════════════════════════
        護欄系統 (Guardrail System)
        Guardrail System
═══════════════════════════════════════════════════════════

本模組實現完整的 AI 護欄系統
確保 AI 操作始終可預測、安全且合規

This module implements a complete AI guardrail system
Ensures AI operations are always predictable, safe, and compliant

參考：護欄是對 AI 代理施加的限制和檢查 [4]

自成閉環：本檔案獨立管理所有護欄的定義和執行
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class GuardrailType(Enum):
    """護欄類型"""
    SAFETY = "safety"               # 安全護欄
    COMPLIANCE = "compliance"       # 合規護欄
    ETHICS = "ethics"               # 倫理護欄
    QUALITY = "quality"             # 品質護欄
    PERFORMANCE = "performance"     # 效能護欄
    CONTENT = "content"             # 內容護欄
    INPUT = "input"                 # 輸入護欄
    OUTPUT = "output"               # 輸出護欄


class GuardrailSeverity(Enum):
    """護欄嚴重性"""
    CRITICAL = "critical"   # 絕對阻止
    HIGH = "high"           # 強烈建議阻止
    MEDIUM = "medium"       # 警告並記錄
    LOW = "low"             # 僅記錄


@dataclass
class GuardrailResult:
    """
    護欄檢查結果
    Guardrail Check Result
    """
    guardrail_id: str
    guardrail_type: GuardrailType
    passed: bool
    severity: GuardrailSeverity

    # 詳細資訊
    message: str = ""
    violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # 修正資訊
    auto_correctable: bool = False
    correction_applied: bool = False
    corrected_content: str | None = None

    # 元數據
    confidence: float = 1.0
    checked_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: float = 0.0


class Guardrail(ABC):
    """
    護欄基類
    Base Guardrail Class
    
    所有護欄必須繼承此類
    """

    def __init__(
        self,
        guardrail_id: str,
        name: str,
        guardrail_type: GuardrailType,
        severity: GuardrailSeverity = GuardrailSeverity.MEDIUM,
        enabled: bool = True,
    ):
        self.guardrail_id = guardrail_id
        self.name = name
        self.guardrail_type = guardrail_type
        self.severity = severity
        self.enabled = enabled

        # 統計
        self.check_count = 0
        self.pass_count = 0
        self.fail_count = 0

    @abstractmethod
    def check(self, content: Any, context: dict[str, Any] = None) -> GuardrailResult:
        """執行護欄檢查"""
        pass

    def _create_result(
        self,
        passed: bool,
        message: str = "",
        violations: list[str] = None,
        recommendations: list[str] = None,
        **kwargs
    ) -> GuardrailResult:
        """創建檢查結果"""
        self.check_count += 1
        if passed:
            self.pass_count += 1
        else:
            self.fail_count += 1

        return GuardrailResult(
            guardrail_id=self.guardrail_id,
            guardrail_type=self.guardrail_type,
            passed=passed,
            severity=self.severity,
            message=message,
            violations=violations or [],
            recommendations=recommendations or [],
            **kwargs
        )


class SafetyGuardrail(Guardrail):
    """
    安全護欄
    Safety Guardrail
    
    防止生成有害、危險或不安全的內容
    """

    # 有害內容模式
    HARMFUL_PATTERNS = {
        "violence": [
            r"\b(kill|murder|attack|assault|harm|hurt)\b",
            r"how to (make|create|build) (bomb|weapon|explosive)",
        ],
        "self_harm": [
            r"(suicide|self[-\s]?harm)",
            r"ways to (hurt|harm|kill) (yourself|myself)",
        ],
        "illegal": [
            r"how to (hack|crack|break into)",
            r"(steal|fraud|scam) (money|identity)",
        ],
        "dangerous": [
            r"instructions for (poison|toxin)",
            r"how to (bypass|circumvent) security",
        ],
    }

    # 安全替換建議
    SAFE_ALTERNATIVES = {
        "violence": "請考慮使用和平、建設性的方式解決問題。",
        "self_harm": "如果您有這方面的困擾，請聯繫專業心理健康服務。",
        "illegal": "請遵守法律法規，選擇合法的替代方案。",
        "dangerous": "這類資訊可能造成危害，建議諮詢專業人士。",
    }

    def __init__(
        self,
        guardrail_id: str = "SAFETY_001",
        name: str = "安全護欄",
        severity: GuardrailSeverity = GuardrailSeverity.CRITICAL,
    ):
        super().__init__(
            guardrail_id=guardrail_id,
            name=name,
            guardrail_type=GuardrailType.SAFETY,
            severity=severity,
        )

    def check(self, content: Any, context: dict[str, Any] = None) -> GuardrailResult:
        """檢查內容安全性"""
        start_time = datetime.utcnow()

        if not isinstance(content, str):
            content = str(content)

        content_lower = content.lower()
        violations = []
        recommendations = []

        # 檢查所有有害模式
        for category, patterns in self.HARMFUL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    violations.append(f"偵測到 {category} 類型的潛在有害內容")
                    recommendations.append(self.SAFE_ALTERNATIVES.get(category, ""))
                    break  # 每個類別只報告一次

        # 移除重複的建議
        recommendations = list({r for r in recommendations if r})

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000

        return self._create_result(
            passed=len(violations) == 0,
            message="內容安全檢查" + ("通過" if not violations else "未通過"),
            violations=violations,
            recommendations=recommendations,
            processing_time_ms=processing_time,
        )


class ComplianceGuardrail(Guardrail):
    """
    合規護欄
    Compliance Guardrail
    
    確保符合各種法規和標準
    """

    # 合規檢查規則
    COMPLIANCE_RULES = {
        "gdpr": {
            "name": "GDPR 合規",
            "patterns": {
                "pii_exposure": r"\b(email|phone|address|name)\s*[:=]\s*[^\s]+",
                "no_consent": r"without (consent|permission|authorization)",
            },
            "requirements": [
                "必須獲得數據主體同意",
                "必須提供數據存取權",
                "必須支援數據刪除權",
            ],
        },
        "hipaa": {
            "name": "HIPAA 合規",
            "patterns": {
                "phi_exposure": r"\b(patient|diagnosis|treatment|medication)\b",
            },
            "requirements": [
                "必須保護病患健康資訊",
                "必須實施存取控制",
                "必須記錄所有存取",
            ],
        },
        "pci_dss": {
            "name": "PCI-DSS 合規",
            "patterns": {
                "card_data": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                "cvv": r"\bcvv\b.*\d{3,4}",
            },
            "requirements": [
                "禁止存儲 CVV",
                "必須加密卡號",
                "必須使用安全傳輸",
            ],
        },
    }

    def __init__(
        self,
        guardrail_id: str = "COMPLIANCE_001",
        name: str = "合規護欄",
        severity: GuardrailSeverity = GuardrailSeverity.HIGH,
        enabled_standards: list[str] = None,
    ):
        super().__init__(
            guardrail_id=guardrail_id,
            name=name,
            guardrail_type=GuardrailType.COMPLIANCE,
            severity=severity,
        )

        self.enabled_standards = enabled_standards or list(self.COMPLIANCE_RULES.keys())

    def check(self, content: Any, context: dict[str, Any] = None) -> GuardrailResult:
        """檢查合規性"""
        start_time = datetime.utcnow()

        if not isinstance(content, str):
            content = str(content)

        violations = []
        recommendations = []

        # 檢查所有啟用的合規標準
        for standard in self.enabled_standards:
            if standard not in self.COMPLIANCE_RULES:
                continue

            rule = self.COMPLIANCE_RULES[standard]

            for pattern_name, pattern in rule["patterns"].items():
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(
                        f"[{rule['name']}] 偵測到 {pattern_name} 違規"
                    )
                    recommendations.extend(rule["requirements"])

        # 移除重複的建議
        recommendations = list(set(recommendations))

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000

        return self._create_result(
            passed=len(violations) == 0,
            message="合規檢查" + ("通過" if not violations else "發現違規"),
            violations=violations,
            recommendations=recommendations,
            processing_time_ms=processing_time,
        )


class EthicsGuardrail(Guardrail):
    """
    倫理護欄
    Ethics Guardrail
    
    確保 AI 行為符合倫理標準
    """

    # 倫理原則
    ETHICS_PRINCIPLES = {
        "fairness": {
            "name": "公平性",
            "indicators": [
                r"\b(discriminat|bias|prejudic)\w*\b",
                r"\b(unfair|inequal)\w*\b",
            ],
            "guidance": "確保對所有用戶和群體公平對待",
        },
        "transparency": {
            "name": "透明度",
            "indicators": [
                r"\b(hidden|secret|covert)\s+(agenda|purpose|intention)\b",
                r"\b(deceive|mislead|manipulat)\w*\b",
            ],
            "guidance": "保持操作和決策的透明性",
        },
        "privacy": {
            "name": "隱私",
            "indicators": [
                r"\b(track|monitor|surveil)\w*\b.*\b(without|no)\s*(consent|permission)\b",
                r"\bsecret(ly)?\s+(collect|gather|record)\b",
            ],
            "guidance": "尊重用戶隱私權",
        },
        "autonomy": {
            "name": "自主性",
            "indicators": [
                r"\b(force|coerce|compel)\b",
                r"\b(manipulat|control)\w*\s+(user|person|people)\b",
            ],
            "guidance": "尊重用戶的自主決策權",
        },
    }

    def __init__(
        self,
        guardrail_id: str = "ETHICS_001",
        name: str = "倫理護欄",
        severity: GuardrailSeverity = GuardrailSeverity.HIGH,
    ):
        super().__init__(
            guardrail_id=guardrail_id,
            name=name,
            guardrail_type=GuardrailType.ETHICS,
            severity=severity,
        )

    def check(self, content: Any, context: dict[str, Any] = None) -> GuardrailResult:
        """檢查倫理合規性"""
        start_time = datetime.utcnow()

        if not isinstance(content, str):
            content = str(content)

        violations = []
        recommendations = []

        # 檢查所有倫理原則
        for _principle_id, principle in self.ETHICS_PRINCIPLES.items():
            for indicator in principle["indicators"]:
                if re.search(indicator, content, re.IGNORECASE):
                    violations.append(
                        f"可能違反 {principle['name']} 原則"
                    )
                    recommendations.append(principle["guidance"])
                    break  # 每個原則只報告一次

        # 移除重複的建議
        recommendations = list(set(recommendations))

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000

        return self._create_result(
            passed=len(violations) == 0,
            message="倫理檢查" + ("通過" if not violations else "發現問題"),
            violations=violations,
            recommendations=recommendations,
            processing_time_ms=processing_time,
        )


class ContentGuardrail(Guardrail):
    """
    內容護欄
    Content Guardrail
    
    過濾不當或低品質內容
    """

    # 內容過濾規則
    CONTENT_FILTERS = {
        "profanity": {
            "patterns": [
                # 此處省略具體髒話，使用佔位符
                r"\b(placeholder_profanity)\b",
            ],
            "action": "filter",
        },
        "spam": {
            "patterns": [
                r"(.)\1{5,}",  # 重複字符
                r"(\b\w+\b)(\s+\1){3,}",  # 重複詞
            ],
            "action": "warn",
        },
        "low_quality": {
            "patterns": [
                r"^.{0,10}$",  # 太短
                r"^[^a-zA-Z\u4e00-\u9fff]*$",  # 無有意義文字
            ],
            "action": "warn",
        },
    }

    def __init__(
        self,
        guardrail_id: str = "CONTENT_001",
        name: str = "內容護欄",
        severity: GuardrailSeverity = GuardrailSeverity.MEDIUM,
    ):
        super().__init__(
            guardrail_id=guardrail_id,
            name=name,
            guardrail_type=GuardrailType.CONTENT,
            severity=severity,
        )

    def check(self, content: Any, context: dict[str, Any] = None) -> GuardrailResult:
        """檢查內容品質"""
        start_time = datetime.utcnow()

        if not isinstance(content, str):
            content = str(content)

        violations = []
        recommendations = []

        # 檢查所有內容過濾規則
        for filter_type, filter_config in self.CONTENT_FILTERS.items():
            for pattern in filter_config["patterns"]:
                if re.search(pattern, content, re.IGNORECASE):
                    if filter_config["action"] == "filter":
                        violations.append(f"偵測到 {filter_type} 內容")
                    else:
                        recommendations.append(f"建議改善: {filter_type}")

        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000

        return self._create_result(
            passed=len(violations) == 0,
            message="內容檢查" + ("通過" if not violations else "需要修改"),
            violations=violations,
            recommendations=recommendations,
            auto_correctable=len(violations) > 0,
            processing_time_ms=processing_time,
        )


class GuardrailSystem:
    """
    護欄系統
    Guardrail System
    
    整合所有護欄的核心系統
    
    This is the core system that integrates all guardrails
    
    自成閉環：完整管理所有護欄的註冊、執行和統計
    """

    def __init__(self):
        self._guardrails: dict[str, Guardrail] = {}
        self._execution_log: list[dict[str, Any]] = []

        # 初始化預設護欄
        self._initialize_default_guardrails()

    def _initialize_default_guardrails(self):
        """初始化預設護欄"""
        default_guardrails = [
            SafetyGuardrail(),
            ComplianceGuardrail(),
            EthicsGuardrail(),
            ContentGuardrail(),
        ]

        for guardrail in default_guardrails:
            self.register_guardrail(guardrail)

    def register_guardrail(self, guardrail: Guardrail):
        """註冊護欄"""
        self._guardrails[guardrail.guardrail_id] = guardrail

    def unregister_guardrail(self, guardrail_id: str):
        """取消註冊護欄"""
        if guardrail_id in self._guardrails:
            del self._guardrails[guardrail_id]

    def check_all(
        self,
        content: Any,
        context: dict[str, Any] = None,
        guardrail_types: list[GuardrailType] = None,
    ) -> dict[str, GuardrailResult]:
        """執行所有護欄檢查"""
        results = {}

        for guardrail_id, guardrail in self._guardrails.items():
            # 檢查是否啟用
            if not guardrail.enabled:
                continue

            # 檢查類型過濾
            if guardrail_types and guardrail.guardrail_type not in guardrail_types:
                continue

            # 執行檢查
            result = guardrail.check(content, context)
            results[guardrail_id] = result

            # 記錄執行
            self._log_execution(guardrail_id, result)

            # 如果是 CRITICAL 級別且未通過，可以提前返回
            if not result.passed and result.severity == GuardrailSeverity.CRITICAL:
                break

        return results

    def check_single(
        self,
        guardrail_id: str,
        content: Any,
        context: dict[str, Any] = None,
    ) -> GuardrailResult | None:
        """執行單一護欄檢查"""
        guardrail = self._guardrails.get(guardrail_id)

        if guardrail and guardrail.enabled:
            result = guardrail.check(content, context)
            self._log_execution(guardrail_id, result)
            return result

        return None

    def _log_execution(self, guardrail_id: str, result: GuardrailResult):
        """記錄執行"""
        self._execution_log.append({
            "guardrail_id": guardrail_id,
            "passed": result.passed,
            "severity": result.severity.value,
            "violation_count": len(result.violations),
            "timestamp": result.checked_at,
        })

    def is_safe(
        self,
        content: Any,
        context: dict[str, Any] = None,
    ) -> bool:
        """快速安全檢查"""
        results = self.check_all(content, context, [GuardrailType.SAFETY])
        return all(r.passed for r in results.values())

    def is_compliant(
        self,
        content: Any,
        context: dict[str, Any] = None,
    ) -> bool:
        """快速合規檢查"""
        results = self.check_all(content, context, [GuardrailType.COMPLIANCE])
        return all(r.passed for r in results.values())

    def is_ethical(
        self,
        content: Any,
        context: dict[str, Any] = None,
    ) -> bool:
        """快速倫理檢查"""
        results = self.check_all(content, context, [GuardrailType.ETHICS])
        return all(r.passed for r in results.values())

    def get_guardrail(self, guardrail_id: str) -> Guardrail | None:
        """獲取護欄"""
        return self._guardrails.get(guardrail_id)

    def get_all_guardrails(self) -> list[Guardrail]:
        """獲取所有護欄"""
        return list(self._guardrails.values())

    def enable_guardrail(self, guardrail_id: str):
        """啟用護欄"""
        if guardrail_id in self._guardrails:
            self._guardrails[guardrail_id].enabled = True

    def disable_guardrail(self, guardrail_id: str):
        """停用護欄"""
        if guardrail_id in self._guardrails:
            self._guardrails[guardrail_id].enabled = False

    def get_execution_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """獲取執行記錄"""
        return self._execution_log[-limit:]

    def get_statistics(self) -> dict[str, Any]:
        """獲取統計數據"""
        stats = {
            "total_guardrails": len(self._guardrails),
            "active_guardrails": sum(
                1 for g in self._guardrails.values() if g.enabled
            ),
            "by_type": {},
            "total_checks": 0,
            "total_passes": 0,
            "total_failures": 0,
        }

        for guardrail in self._guardrails.values():
            # 按類型統計
            type_key = guardrail.guardrail_type.value
            if type_key not in stats["by_type"]:
                stats["by_type"][type_key] = {
                    "count": 0,
                    "checks": 0,
                    "passes": 0,
                    "failures": 0,
                }

            stats["by_type"][type_key]["count"] += 1
            stats["by_type"][type_key]["checks"] += guardrail.check_count
            stats["by_type"][type_key]["passes"] += guardrail.pass_count
            stats["by_type"][type_key]["failures"] += guardrail.fail_count

            stats["total_checks"] += guardrail.check_count
            stats["total_passes"] += guardrail.pass_count
            stats["total_failures"] += guardrail.fail_count

        if stats["total_checks"] > 0:
            stats["pass_rate"] = round(
                stats["total_passes"] / stats["total_checks"] * 100,
                2
            )
        else:
            stats["pass_rate"] = 0

        return stats

    def reset_statistics(self):
        """重置統計數據"""
        for guardrail in self._guardrails.values():
            guardrail.check_count = 0
            guardrail.pass_count = 0
            guardrail.fail_count = 0

        self._execution_log = []
