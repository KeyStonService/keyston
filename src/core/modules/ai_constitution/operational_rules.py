"""
═══════════════════════════════════════════════════════════
        第二層：操作規則 (Operational Rules)
        Layer 2: Operational Rules
═══════════════════════════════════════════════════════════

本模組定義 AI 操作層面的具體規則
這些規則是根本法則的實際執行細節

This module defines operational-level rules for AI actions
These rules are the practical execution details of fundamental laws

自成閉環：本檔案完全獨立運作，不依賴外部狀態
"""

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RuleCategory(Enum):
    """規則類別"""
    DATA_HANDLING = "data_handling"
    SYSTEM_ACCESS = "system_access"
    RESOURCE_USAGE = "resource_usage"
    COMMUNICATION = "communication"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class RuleSeverity(Enum):
    """規則嚴重性"""
    CRITICAL = "critical"       # 違反會導致立即停止
    HIGH = "high"              # 違反會導致警告並可能阻止
    MEDIUM = "medium"          # 違反會記錄並建議修正
    LOW = "low"                # 違反會記錄供審查


@dataclass
class RuleViolation:
    """規則違反記錄"""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    auto_corrected: bool = False
    correction_applied: str | None = None


@dataclass
class RuleCheckResult:
    """規則檢查結果"""
    rule_id: str
    passed: bool
    violations: list[RuleViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    auto_corrections: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DataHandlingRule:
    """
    數據處理規則
    Data Handling Rules
    
    定義 AI 如何正確處理各類數據
    """

    RULE_ID = "RULE_DATA"
    RULE_NAME = "數據處理規則"
    CATEGORY = RuleCategory.DATA_HANDLING

    # 敏感數據類型
    SENSITIVE_DATA_TYPES = {
        "pii": ["email", "phone", "address", "ssn", "passport"],
        "financial": ["credit_card", "bank_account", "salary", "tax"],
        "health": ["medical_record", "diagnosis", "prescription"],
        "credentials": ["password", "api_key", "token", "secret"],
    }

    # 數據處理規則
    RULES = {
        "encryption_required": {
            "description": "敏感數據必須加密存儲",
            "severity": RuleSeverity.CRITICAL,
            "applies_to": ["pii", "financial", "health", "credentials"],
        },
        "access_logging": {
            "description": "所有數據存取必須記錄",
            "severity": RuleSeverity.HIGH,
            "applies_to": ["all"],
        },
        "retention_limit": {
            "description": "數據必須遵守保留期限",
            "severity": RuleSeverity.MEDIUM,
            "applies_to": ["pii", "financial"],
        },
        "anonymization": {
            "description": "分析用數據必須匿名化",
            "severity": RuleSeverity.HIGH,
            "applies_to": ["pii", "health"],
        },
    }

    def __init__(self):
        self._violation_history: list[RuleViolation] = []
        self._check_history: list[RuleCheckResult] = []

    def check(self, operation: dict[str, Any]) -> RuleCheckResult:
        """檢查數據操作是否符合規則"""
        violations = []
        warnings = []
        auto_corrections = []

        data_type = operation.get("data_type", "unknown")
        operation_type = operation.get("operation", "unknown")

        # 檢查是否為敏感數據
        sensitive_category = self._identify_sensitive_category(data_type)

        if sensitive_category:
            # 檢查加密
            if not operation.get("encrypted", False):
                violations.append(RuleViolation(
                    rule_id=f"{self.RULE_ID}_encryption",
                    rule_name="加密要求",
                    severity=RuleSeverity.CRITICAL,
                    description=f"敏感數據 {data_type} 必須加密",
                    context={"data_type": data_type, "category": sensitive_category}
                ))
                auto_corrections.append("auto_encrypt_data")

            # 檢查存取記錄
            if not operation.get("access_logged", False):
                violations.append(RuleViolation(
                    rule_id=f"{self.RULE_ID}_logging",
                    rule_name="存取記錄",
                    severity=RuleSeverity.HIGH,
                    description="敏感數據存取未記錄",
                    context={"operation": operation_type}
                ))
                auto_corrections.append("enable_access_logging")

        # 檢查數據洩漏風險
        if operation_type in ["export", "share", "transfer"]:
            if not operation.get("authorization_verified", False):
                violations.append(RuleViolation(
                    rule_id=f"{self.RULE_ID}_auth",
                    rule_name="授權驗證",
                    severity=RuleSeverity.CRITICAL,
                    description="數據外傳前必須驗證授權",
                    context={"operation": operation_type}
                ))

        result = RuleCheckResult(
            rule_id=self.RULE_ID,
            passed=len([v for v in violations if v.severity == RuleSeverity.CRITICAL]) == 0,
            violations=violations,
            warnings=warnings,
            auto_corrections=auto_corrections
        )

        self._check_history.append(result)
        self._violation_history.extend(violations)

        return result

    def _identify_sensitive_category(self, data_type: str) -> str | None:
        """識別敏感數據類別"""
        data_type_lower = data_type.lower()
        for category, types in self.SENSITIVE_DATA_TYPES.items():
            if any(t in data_type_lower for t in types):
                return category
        return None

    def apply_auto_correction(self, correction: str, data: dict[str, Any]) -> dict[str, Any]:
        """應用自動修正"""
        if correction == "auto_encrypt_data":
            # 模擬加密
            data["encrypted"] = True
            data["encryption_algorithm"] = "AES-256-GCM"
        elif correction == "enable_access_logging":
            data["access_logged"] = True
            data["log_id"] = hashlib.sha256(
                str(datetime.utcnow()).encode()
            ).hexdigest()[:16]

        return data


class SystemAccessRule:
    """
    系統存取規則
    System Access Rules
    
    定義 AI 如何安全地存取系統資源
    """

    RULE_ID = "RULE_ACCESS"
    RULE_NAME = "系統存取規則"
    CATEGORY = RuleCategory.SYSTEM_ACCESS

    # 存取級別定義
    ACCESS_LEVELS = {
        "read": 1,
        "write": 2,
        "execute": 3,
        "admin": 4,
        "root": 5,
    }

    # 資源類別及其最大允許存取級別
    RESOURCE_ACCESS_LIMITS = {
        "public_data": 1,      # 只讀
        "user_data": 2,        # 讀寫
        "system_config": 3,    # 讀寫執行
        "security_config": 4,  # 需要管理員權限
        "core_system": 5,      # 需要 root 權限
    }

    # 禁止存取的資源
    PROHIBITED_RESOURCES = [
        "/etc/shadow",
        "/etc/passwd",
        "~/.ssh/",
        "/var/log/auth.log",
        "credentials.json",
        ".env",
    ]

    def __init__(self):
        self._current_access_level: int = 1  # 預設為讀取權限
        self._access_history: list[dict[str, Any]] = []
        self._violation_history: list[RuleViolation] = []

    def check(self, access_request: dict[str, Any]) -> RuleCheckResult:
        """檢查系統存取請求"""
        violations = []
        warnings = []
        auto_corrections = []

        resource = access_request.get("resource", "")
        access_type = access_request.get("access_type", "read")
        requestor = access_request.get("requestor", "unknown")

        # 檢查是否為禁止資源
        if self._is_prohibited_resource(resource):
            violations.append(RuleViolation(
                rule_id=f"{self.RULE_ID}_prohibited",
                rule_name="禁止存取",
                severity=RuleSeverity.CRITICAL,
                description=f"資源 {resource} 被禁止存取",
                context={"resource": resource, "requestor": requestor}
            ))

        # 檢查存取級別
        requested_level = self.ACCESS_LEVELS.get(access_type, 1)
        resource_category = self._categorize_resource(resource)
        max_allowed = self.RESOURCE_ACCESS_LIMITS.get(resource_category, 1)

        if requested_level > max_allowed:
            violations.append(RuleViolation(
                rule_id=f"{self.RULE_ID}_level",
                rule_name="存取級別超限",
                severity=RuleSeverity.HIGH,
                description=f"請求的存取級別 {access_type} 超過資源 {resource_category} 允許的最大級別",
                context={
                    "requested": access_type,
                    "max_allowed": max_allowed,
                    "resource_category": resource_category
                }
            ))
            # 建議降級存取
            auto_corrections.append(f"downgrade_to_level_{max_allowed}")

        # 記錄存取
        self._log_access(access_request)

        result = RuleCheckResult(
            rule_id=self.RULE_ID,
            passed=len([v for v in violations if v.severity == RuleSeverity.CRITICAL]) == 0,
            violations=violations,
            warnings=warnings,
            auto_corrections=auto_corrections
        )

        self._violation_history.extend(violations)

        return result

    def _is_prohibited_resource(self, resource: str) -> bool:
        """檢查是否為禁止資源"""
        resource_lower = resource.lower()
        return any(
            prohibited.lower() in resource_lower
            for prohibited in self.PROHIBITED_RESOURCES
        )

    def _categorize_resource(self, resource: str) -> str:
        """分類資源"""
        resource_lower = resource.lower()

        if any(p in resource_lower for p in ["public", "static", "assets"]):
            return "public_data"
        elif any(p in resource_lower for p in ["user", "profile", "account"]):
            return "user_data"
        elif any(p in resource_lower for p in ["config", "settings", "preferences"]):
            return "system_config"
        elif any(p in resource_lower for p in ["security", "auth", "permission"]):
            return "security_config"
        elif any(p in resource_lower for p in ["kernel", "boot", "init", "core"]):
            return "core_system"

        return "public_data"  # 預設最低級別

    def _log_access(self, access_request: dict[str, Any]):
        """記錄存取請求"""
        self._access_history.append({
            **access_request,
            "timestamp": datetime.utcnow().isoformat(),
            "log_id": hashlib.sha256(
                f"{access_request}{datetime.utcnow()}".encode()
            ).hexdigest()[:16]
        })

    def get_access_history(self) -> list[dict[str, Any]]:
        """獲取存取歷史"""
        return self._access_history.copy()


class ResourceUsageRule:
    """
    資源使用規則
    Resource Usage Rules
    
    定義 AI 如何合理使用系統資源
    """

    RULE_ID = "RULE_RESOURCE"
    RULE_NAME = "資源使用規則"
    CATEGORY = RuleCategory.RESOURCE_USAGE

    # 資源限制
    LIMITS = {
        "cpu_percent": 80.0,        # CPU 使用上限 80%
        "memory_percent": 75.0,     # 記憶體使用上限 75%
        "disk_percent": 90.0,       # 磁碟使用上限 90%
        "network_mbps": 100.0,      # 網路頻寬上限 100 Mbps
        "concurrent_tasks": 50,     # 並發任務上限
        "api_calls_per_minute": 1000,  # API 呼叫上限
    }

    # 資源優先級
    PRIORITY_MULTIPLIERS = {
        "critical": 1.5,    # 關鍵任務可使用 150% 資源
        "high": 1.2,        # 高優先級可使用 120% 資源
        "normal": 1.0,      # 正常優先級
        "low": 0.8,         # 低優先級限制 80% 資源
        "background": 0.5,  # 背景任務限制 50% 資源
    }

    def __init__(self):
        self._current_usage: dict[str, float] = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "network_mbps": 0.0,
            "concurrent_tasks": 0,
            "api_calls_per_minute": 0,
        }
        self._usage_history: list[dict[str, Any]] = []
        self._violation_history: list[RuleViolation] = []

    def check(self, resource_request: dict[str, Any]) -> RuleCheckResult:
        """檢查資源使用請求"""
        violations = []
        warnings = []
        auto_corrections = []

        resource_type = resource_request.get("resource_type", "cpu")
        requested_amount = resource_request.get("amount", 0)
        priority = resource_request.get("priority", "normal")

        # 計算實際限制（考慮優先級）
        multiplier = self.PRIORITY_MULTIPLIERS.get(priority, 1.0)
        limit_key = f"{resource_type}_percent" if resource_type in ["cpu", "memory", "disk"] else resource_type
        base_limit = self.LIMITS.get(limit_key, float('inf'))
        adjusted_limit = base_limit * multiplier

        # 計算總使用量
        current = self._current_usage.get(limit_key, 0)
        total_after_request = current + requested_amount

        if total_after_request > adjusted_limit:
            severity = RuleSeverity.CRITICAL if total_after_request > base_limit * 1.5 else RuleSeverity.HIGH
            violations.append(RuleViolation(
                rule_id=f"{self.RULE_ID}_{resource_type}",
                rule_name=f"{resource_type} 使用超限",
                severity=severity,
                description=f"請求的 {resource_type} 使用量 ({requested_amount}) 將導致總使用量 ({total_after_request}) 超過限制 ({adjusted_limit})",
                context={
                    "resource_type": resource_type,
                    "requested": requested_amount,
                    "current": current,
                    "limit": adjusted_limit
                }
            ))
            # 建議減少資源使用
            safe_amount = max(0, adjusted_limit - current)
            auto_corrections.append(f"reduce_to_{safe_amount}")
        elif total_after_request > adjusted_limit * 0.8:
            warnings.append(
                f"{resource_type} 使用率將達到 {(total_after_request/adjusted_limit)*100:.1f}%"
            )

        result = RuleCheckResult(
            rule_id=self.RULE_ID,
            passed=len([v for v in violations if v.severity == RuleSeverity.CRITICAL]) == 0,
            violations=violations,
            warnings=warnings,
            auto_corrections=auto_corrections
        )

        self._violation_history.extend(violations)

        return result

    def update_usage(self, resource_type: str, amount: float):
        """更新資源使用量"""
        limit_key = f"{resource_type}_percent" if resource_type in ["cpu", "memory", "disk"] else resource_type
        if limit_key in self._current_usage:
            self._current_usage[limit_key] = amount
            self._usage_history.append({
                "resource_type": resource_type,
                "amount": amount,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_current_usage(self) -> dict[str, float]:
        """獲取當前資源使用情況"""
        return self._current_usage.copy()


class CommunicationRule:
    """
    通訊規則
    Communication Rules
    
    定義 AI 如何與人類和其他系統通訊
    """

    RULE_ID = "RULE_COMM"
    RULE_NAME = "通訊規則"
    CATEGORY = RuleCategory.COMMUNICATION

    # 禁止的通訊內容
    PROHIBITED_CONTENT = [
        "password",
        "secret",
        "api_key",
        "private_key",
        "credit_card",
        "ssn",
    ]

    # 通訊限制
    LIMITS = {
        "max_message_size_kb": 1024,     # 最大訊息大小 1MB
        "max_recipients": 100,            # 最大收件人數
        "rate_limit_per_minute": 60,      # 每分鐘發送上限
    }

    # 必須記錄的通訊類型
    LOGGED_COMMUNICATION_TYPES = [
        "external_api",
        "user_notification",
        "system_alert",
        "data_transfer",
    ]

    def __init__(self):
        self._communication_log: list[dict[str, Any]] = []
        self._rate_counter: dict[str, int] = {}
        self._violation_history: list[RuleViolation] = []

    def check(self, communication: dict[str, Any]) -> RuleCheckResult:
        """檢查通訊請求"""
        violations = []
        warnings = []
        auto_corrections = []

        content = communication.get("content", "")
        comm_type = communication.get("type", "internal")
        recipients = communication.get("recipients", [])

        # 檢查禁止內容
        content_lower = content.lower()
        for prohibited in self.PROHIBITED_CONTENT:
            if prohibited in content_lower:
                violations.append(RuleViolation(
                    rule_id=f"{self.RULE_ID}_content",
                    rule_name="禁止內容",
                    severity=RuleSeverity.CRITICAL,
                    description=f"通訊內容包含禁止的敏感資訊: {prohibited}",
                    context={"prohibited_type": prohibited}
                ))
                auto_corrections.append(f"redact_{prohibited}")

        # 檢查訊息大小
        content_size_kb = len(content.encode('utf-8')) / 1024
        if content_size_kb > self.LIMITS["max_message_size_kb"]:
            violations.append(RuleViolation(
                rule_id=f"{self.RULE_ID}_size",
                rule_name="訊息過大",
                severity=RuleSeverity.MEDIUM,
                description=f"訊息大小 {content_size_kb:.1f}KB 超過限制 {self.LIMITS['max_message_size_kb']}KB",
                context={"size_kb": content_size_kb}
            ))
            auto_corrections.append("compress_or_split_message")

        # 檢查收件人數量
        if len(recipients) > self.LIMITS["max_recipients"]:
            violations.append(RuleViolation(
                rule_id=f"{self.RULE_ID}_recipients",
                rule_name="收件人過多",
                severity=RuleSeverity.MEDIUM,
                description=f"收件人數量 {len(recipients)} 超過限制 {self.LIMITS['max_recipients']}",
                context={"count": len(recipients)}
            ))
            auto_corrections.append("batch_recipients")

        # 記錄通訊
        if comm_type in self.LOGGED_COMMUNICATION_TYPES:
            self._log_communication(communication)

        result = RuleCheckResult(
            rule_id=self.RULE_ID,
            passed=len([v for v in violations if v.severity == RuleSeverity.CRITICAL]) == 0,
            violations=violations,
            warnings=warnings,
            auto_corrections=auto_corrections
        )

        self._violation_history.extend(violations)

        return result

    def _log_communication(self, communication: dict[str, Any]):
        """記錄通訊"""
        # 移除敏感內容後記錄
        safe_comm = {
            "type": communication.get("type"),
            "recipient_count": len(communication.get("recipients", [])),
            "content_size": len(communication.get("content", "")),
            "timestamp": datetime.utcnow().isoformat(),
            "log_id": hashlib.sha256(
                f"{communication}{datetime.utcnow()}".encode()
            ).hexdigest()[:16]
        }
        self._communication_log.append(safe_comm)

    def redact_sensitive_content(self, content: str) -> str:
        """編輯敏感內容"""
        redacted = content
        for prohibited in self.PROHIBITED_CONTENT:
            # 使用正則表達式匹配並替換
            pattern = re.compile(re.escape(prohibited), re.IGNORECASE)
            redacted = pattern.sub("[REDACTED]", redacted)
        return redacted

    def get_communication_log(self) -> list[dict[str, Any]]:
        """獲取通訊記錄"""
        return self._communication_log.copy()


class OperationalRuleEngine:
    """
    操作規則引擎 - 整合所有操作規則
    Operational Rule Engine - Integrates all operational rules
    
    自成閉環：獨立管理所有操作規則的檢查和執行
    """

    def __init__(self):
        self.data_handling = DataHandlingRule()
        self.system_access = SystemAccessRule()
        self.resource_usage = ResourceUsageRule()
        self.communication = CommunicationRule()

        self._all_rules = {
            RuleCategory.DATA_HANDLING: self.data_handling,
            RuleCategory.SYSTEM_ACCESS: self.system_access,
            RuleCategory.RESOURCE_USAGE: self.resource_usage,
            RuleCategory.COMMUNICATION: self.communication,
        }

    def check_operation(
        self,
        category: RuleCategory,
        operation: dict[str, Any]
    ) -> RuleCheckResult:
        """檢查特定類別的操作"""
        rule = self._all_rules.get(category)
        if rule:
            return rule.check(operation)
        return RuleCheckResult(
            rule_id="UNKNOWN",
            passed=False,
            violations=[RuleViolation(
                rule_id="UNKNOWN",
                rule_name="未知類別",
                severity=RuleSeverity.HIGH,
                description=f"未知的規則類別: {category}"
            )]
        )

    def check_all_applicable(
        self,
        operation: dict[str, Any]
    ) -> dict[RuleCategory, RuleCheckResult]:
        """檢查所有適用的規則"""
        results = {}

        # 根據操作類型決定需要檢查的規則
        op_type = operation.get("type", "").lower()

        # 數據操作
        if any(kw in op_type for kw in ["data", "read", "write", "query", "store"]):
            results[RuleCategory.DATA_HANDLING] = self.data_handling.check(operation)

        # 系統存取
        if any(kw in op_type for kw in ["access", "file", "system", "resource"]):
            results[RuleCategory.SYSTEM_ACCESS] = self.system_access.check(operation)

        # 資源使用
        if any(kw in op_type for kw in ["compute", "memory", "cpu", "network"]):
            results[RuleCategory.RESOURCE_USAGE] = self.resource_usage.check(operation)

        # 通訊
        if any(kw in op_type for kw in ["send", "notify", "communicate", "transfer"]):
            results[RuleCategory.COMMUNICATION] = self.communication.check(operation)

        # 如果沒有匹配任何類別，檢查所有規則
        if not results:
            for category, rule in self._all_rules.items():
                results[category] = rule.check(operation)

        return results

    def get_all_violations(self) -> list[RuleViolation]:
        """獲取所有違規記錄"""
        violations = []
        for rule in self._all_rules.values():
            violations.extend(rule._violation_history)
        return violations

    def get_statistics(self) -> dict[str, Any]:
        """獲取統計資訊"""
        stats = {
            "total_violations": 0,
            "by_category": {},
            "by_severity": {s.value: 0 for s in RuleSeverity},
        }

        for category, rule in self._all_rules.items():
            category_violations = rule._violation_history
            stats["by_category"][category.value] = len(category_violations)
            stats["total_violations"] += len(category_violations)

            for v in category_violations:
                stats["by_severity"][v.severity.value] += 1

        return stats


# 便捷類別別名
OperationalRules = OperationalRuleEngine
