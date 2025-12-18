#!/usr/bin/env python3
"""
Safety Constitution - 安全憲法
AI Guardrails, Red Flags, and Constitutional AI

確保 AI 行為符合安全和道德準則
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RiskLevel(Enum):
    """風險等級"""

    CRITICAL = "critical"  # 立即阻止
    HIGH = "high"  # 需要人工審核
    MEDIUM = "medium"  # 發出警告
    LOW = "low"  # 記錄但允許
    NONE = "none"  # 安全


class ViolationType(Enum):
    """違規類型"""

    SENSITIVE_DATA = "sensitive_data"  # 敏感數據洩露
    DESTRUCTIVE_ACTION = "destructive_action"  # 破壞性操作
    UNAUTHORIZED_ACCESS = "unauthorized_access"  # 未授權訪問
    HARMFUL_CONTENT = "harmful_content"  # 有害內容
    POLICY_VIOLATION = "policy_violation"  # 政策違規
    UNSAFE_CODE = "unsafe_code"  # 不安全代碼


@dataclass
class Rule:
    """安全規則"""

    id: str
    name: str
    description: str
    violation_type: ViolationType
    risk_level: RiskLevel
    pattern: str | None = None
    validator: Callable[[str], bool] | None = None
    enabled: bool = True


@dataclass
class Violation:
    """違規記錄"""

    rule_id: str
    rule_name: str
    violation_type: ViolationType
    risk_level: RiskLevel
    content: str
    context: str = ""
    recommendation: str = ""


@dataclass
class SafetyResult:
    """安全檢查結果"""

    is_safe: bool
    risk_level: RiskLevel
    violations: list[Violation] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class Guardrails:
    """
    防護欄

    定義和執行安全規則。
    """

    DEFAULT_RULES = [
        Rule(
            id="no-secrets",
            name="No Secrets in Code",
            description="Prevent hardcoded secrets and credentials",
            violation_type=ViolationType.SENSITIVE_DATA,
            risk_level=RiskLevel.CRITICAL,
            pattern=r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']',
        ),
        Rule(
            id="no-rm-rf",
            name="No Destructive Commands",
            description="Prevent dangerous file system operations",
            violation_type=ViolationType.DESTRUCTIVE_ACTION,
            risk_level=RiskLevel.CRITICAL,
            pattern=r"rm\s+-rf\s+[/*]|del\s+/[sS]",
        ),
        Rule(
            id="no-eval",
            name="No Dynamic Code Execution",
            description="Prevent dangerous eval/exec usage",
            violation_type=ViolationType.UNSAFE_CODE,
            risk_level=RiskLevel.HIGH,
            pattern=r"eval\s*\(|exec\s*\(|__import__",
        ),
        Rule(
            id="no-sql-injection",
            name="No SQL Injection Patterns",
            description="Prevent SQL injection vulnerabilities",
            violation_type=ViolationType.UNSAFE_CODE,
            risk_level=RiskLevel.HIGH,
            pattern=r'f["\'].*SELECT.*{|\.format\(.*SELECT|%\s*\(.*SELECT',
        ),
    ]

    def __init__(self, rules: list[Rule] | None = None):
        self.rules = rules or self.DEFAULT_RULES.copy()

    def add_rule(self, rule: Rule) -> None:
        """添加規則"""
        self.rules.append(rule)

    def remove_rule(self, rule_id: str) -> None:
        """移除規則"""
        self.rules = [r for r in self.rules if r.id != rule_id]

    def check(self, content: str) -> list[Violation]:
        """檢查內容是否違規"""
        violations = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            # 模式匹配
            if rule.pattern:
                if re.search(rule.pattern, content, re.IGNORECASE):
                    violations.append(
                        Violation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            violation_type=rule.violation_type,
                            risk_level=rule.risk_level,
                            content=content[:200],
                            recommendation=f"Review and fix: {rule.description}",
                        )
                    )

            # 自定義驗證器
            if rule.validator and not rule.validator(content):
                violations.append(
                    Violation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        violation_type=rule.violation_type,
                        risk_level=rule.risk_level,
                        content=content[:200],
                        recommendation=f"Custom validation failed: {rule.description}",
                    )
                )

        return violations


class RedFlags:
    """
    紅旗警報

    檢測高風險行為模式。
    """

    PATTERNS = {
        "crypto_mining": [r"coinhive", r"cryptonight", r"stratum\+tcp"],
        "data_exfiltration": [r"curl.*\|.*base64", r"wget.*\|.*sh"],
        "privilege_escalation": [r"sudo\s+.*", r"chmod\s+777", r"chmod\s+\+s"],
        "backdoor": [r"reverse\s+shell", r"nc\s+-e", r"bash\s+-i"],
        "obfuscation": [r"base64\s+-d", r"xxd\s+-r", r"\\x[0-9a-f]{2}"],
    }

    def __init__(self):
        self.triggered_flags: list[dict[str, Any]] = []

    def scan(self, content: str) -> list[dict[str, Any]]:
        """掃描紅旗"""
        flags = []

        for category, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    flag = {
                        "category": category,
                        "pattern": pattern,
                        "risk_level": RiskLevel.CRITICAL.value,
                        "action": "block",
                    }
                    flags.append(flag)

        self.triggered_flags.extend(flags)
        return flags


class AIConstitution:
    """
    AI 憲法

    定義 AI 行為的核心準則。
    """

    PRINCIPLES = [
        {
            "id": "do-no-harm",
            "name": "不造成傷害",
            "description": "AI 不應執行可能造成傷害的操作",
            "priority": 1,
        },
        {
            "id": "transparency",
            "name": "透明度",
            "description": "AI 應清楚說明其行動和理由",
            "priority": 2,
        },
        {
            "id": "user-control",
            "name": "用戶控制",
            "description": "用戶應始終保持對 AI 行為的控制權",
            "priority": 3,
        },
        {
            "id": "privacy",
            "name": "隱私保護",
            "description": "AI 應保護用戶隱私和敏感信息",
            "priority": 4,
        },
        {
            "id": "accuracy",
            "name": "準確性",
            "description": "AI 應力求準確，避免虛假信息",
            "priority": 5,
        },
    ]

    def __init__(self, principles: list[dict[str, Any]] | None = None):
        self.principles = principles or self.PRINCIPLES.copy()

    def evaluate(self, action: dict[str, Any]) -> dict[str, Any]:
        """評估行動是否符合憲法準則"""
        result = {"compliant": True, "violations": [], "warnings": []}

        action_type = action.get("type", "")
        action_content = action.get("content", "")

        # 檢查是否違反準則
        for principle in self.principles:
            if self._violates_principle(action, principle):
                result["compliant"] = False
                result["violations"].append(
                    {
                        "principle_id": principle["id"],
                        "principle_name": principle["name"],
                        "reason": f"Action may violate: {principle['description']}",
                    }
                )

        return result

    def _violates_principle(self, action: dict[str, Any], principle: dict[str, Any]) -> bool:
        """檢查行動是否違反特定準則"""
        # 簡化的違規檢測邏輯
        action_type = action.get("type", "")

        if principle["id"] == "do-no-harm":
            harmful_types = ["delete", "destroy", "terminate", "kill"]
            return any(h in action_type.lower() for h in harmful_types)

        return False


class SafetyConstitution:
    """
    安全憲法

    整合 Guardrails、Red Flags 和 AI Constitution。

    功能：
    - 行為守則執行
    - 風險檢測
    - 合規性評估
    - 安全審計
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.guardrails = Guardrails()
        self.red_flags = RedFlags()
        self.constitution = AIConstitution()

    def check_content(self, content: str) -> SafetyResult:
        """檢查內容安全性"""
        violations = []
        recommendations = []

        # 1. Guardrails 檢查
        guardrail_violations = self.guardrails.check(content)
        violations.extend(guardrail_violations)

        # 2. Red Flags 掃描
        flags = self.red_flags.scan(content)
        for flag in flags:
            violations.append(
                Violation(
                    rule_id=f"redflag-{flag['category']}",
                    rule_name=f"Red Flag: {flag['category']}",
                    violation_type=ViolationType.POLICY_VIOLATION,
                    risk_level=RiskLevel.CRITICAL,
                    content=content[:200],
                    recommendation=f"Blocked due to {flag['category']} detection",
                )
            )

        # 確定最高風險等級
        if not violations:
            risk_level = RiskLevel.NONE
        else:
            risk_levels = [v.risk_level for v in violations]
            if RiskLevel.CRITICAL in risk_levels:
                risk_level = RiskLevel.CRITICAL
            elif RiskLevel.HIGH in risk_levels:
                risk_level = RiskLevel.HIGH
            elif RiskLevel.MEDIUM in risk_levels:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

        # 生成建議
        for v in violations:
            if v.recommendation:
                recommendations.append(v.recommendation)

        return SafetyResult(
            is_safe=len(violations) == 0,
            risk_level=risk_level,
            violations=violations,
            recommendations=recommendations,
        )

    def check_action(self, action: dict[str, Any]) -> SafetyResult:
        """檢查行動合規性"""
        # 評估行動是否符合憲法準則
        evaluation = self.constitution.evaluate(action)

        violations = []
        for v in evaluation.get("violations", []):
            violations.append(
                Violation(
                    rule_id=v["principle_id"],
                    rule_name=v["principle_name"],
                    violation_type=ViolationType.POLICY_VIOLATION,
                    risk_level=RiskLevel.HIGH,
                    content=str(action),
                    recommendation=v["reason"],
                )
            )

        return SafetyResult(
            is_safe=evaluation["compliant"],
            risk_level=RiskLevel.HIGH if violations else RiskLevel.NONE,
            violations=violations,
            recommendations=[v.recommendation for v in violations],
        )

    def audit_log(self) -> list[dict[str, Any]]:
        """獲取審計日誌"""
        return [
            {
                "category": flag["category"],
                "pattern": flag["pattern"],
                "risk_level": flag["risk_level"],
            }
            for flag in self.red_flags.triggered_flags
        ]
