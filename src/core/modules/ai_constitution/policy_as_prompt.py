"""
═══════════════════════════════════════════════════════════
        政策即提示 (Policy as Prompt)
        Policy as Prompt System
═══════════════════════════════════════════════════════════

本模組實現「政策即提示」方法
將非結構化的設計文檔自動轉換為可驗證的實時護欄

This module implements the "Policy as Prompt" approach
Automatically converts unstructured design documents into verifiable real-time guardrails

參考：Policy as Prompt 方法將政策轉換為可執行的護欄 [1]

自成閉環：本檔案獨立管理政策到提示的轉換和執行
"""

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PolicyType(Enum):
    """政策類型"""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    ETHICS = "ethics"
    OPERATIONAL = "operational"
    BEHAVIORAL = "behavioral"
    QUALITY = "quality"


class EnforcementAction(Enum):
    """執行動作"""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    MODIFY = "modify"
    ESCALATE = "escalate"
    LOG = "log"


@dataclass
class PolicyPrompt:
    """
    政策提示
    Policy Prompt
    
    將政策文檔轉換為可執行的提示格式
    """
    prompt_id: str
    policy_name: str
    policy_type: PolicyType

    # 政策內容
    description: str
    rules: list[str]
    conditions: dict[str, Any]

    # 執行配置
    enforcement_action: EnforcementAction
    priority: int = 100
    enabled: bool = True

    # 自動生成的提示文本
    prompt_text: str = ""

    # 元數據
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        """初始化後自動生成提示文本"""
        if not self.prompt_text:
            self.prompt_text = self._generate_prompt()

    def _generate_prompt(self) -> str:
        """生成政策提示文本"""
        prompt_parts = [
            f"【政策: {self.policy_name}】",
            f"類型: {self.policy_type.value}",
            f"描述: {self.description}",
            "",
            "規則:",
        ]

        for i, rule in enumerate(self.rules, 1):
            prompt_parts.append(f"  {i}. {rule}")

        prompt_parts.extend([
            "",
            "條件:",
        ])

        for key, value in self.conditions.items():
            prompt_parts.append(f"  - {key}: {value}")

        prompt_parts.extend([
            "",
            f"違規處理: {self.enforcement_action.value}",
        ])

        return "\n".join(prompt_parts)


@dataclass
class PromptGuardrail:
    """
    提示護欄
    Prompt Guardrail
    
    基於政策提示實現的實時護欄
    """
    guardrail_id: str
    policy_prompt: PolicyPrompt

    # 驗證模式
    patterns: list[str] = field(default_factory=list)
    validators: list[Callable] = field(default_factory=list)

    # 執行統計
    check_count: int = 0
    violation_count: int = 0
    last_check: str | None = None

    def check(self, content: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """檢查內容是否符合護欄規則"""
        self.check_count += 1
        self.last_check = datetime.utcnow().isoformat()

        violations = []
        warnings = []

        # 模式匹配檢查
        for pattern in self.patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"匹配禁止模式: {pattern}")

        # 自定義驗證器檢查
        for validator in self.validators:
            try:
                result = validator(content, context or {})
                if not result.get("passed", True):
                    violations.append(result.get("message", "驗證失敗"))
            except Exception as e:
                warnings.append(f"驗證器錯誤: {str(e)}")

        if violations:
            self.violation_count += 1

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "guardrail_id": self.guardrail_id,
            "policy_name": self.policy_prompt.policy_name,
            "enforcement_action": self.policy_prompt.enforcement_action.value,
            "checked_at": self.last_check,
        }


class PolicyEnforcer:
    """
    政策執行器
    Policy Enforcer
    
    負責執行所有政策提示和護欄
    """

    def __init__(self):
        self._guardrails: dict[str, PromptGuardrail] = {}
        self._enforcement_log: list[dict[str, Any]] = []

    def register_guardrail(self, guardrail: PromptGuardrail):
        """註冊護欄"""
        self._guardrails[guardrail.guardrail_id] = guardrail

    def enforce(
        self,
        content: str,
        context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """執行所有護欄檢查"""
        results = {
            "passed": True,
            "violations": [],
            "warnings": [],
            "actions_taken": [],
            "checked_guardrails": [],
        }

        # 按優先級排序護欄
        sorted_guardrails = sorted(
            self._guardrails.values(),
            key=lambda g: g.policy_prompt.priority,
            reverse=True
        )

        for guardrail in sorted_guardrails:
            if not guardrail.policy_prompt.enabled:
                continue

            check_result = guardrail.check(content, context)
            results["checked_guardrails"].append(guardrail.guardrail_id)

            if not check_result["passed"]:
                results["passed"] = False
                results["violations"].extend(check_result["violations"])

                # 根據執行動作決定處理
                action = guardrail.policy_prompt.enforcement_action
                if action == EnforcementAction.DENY:
                    results["actions_taken"].append(f"拒絕: {guardrail.policy_prompt.policy_name}")
                    break  # 立即停止
                elif action == EnforcementAction.WARN:
                    results["warnings"].extend(check_result["violations"])
                elif action == EnforcementAction.LOG:
                    self._log_enforcement(guardrail, check_result)

            results["warnings"].extend(check_result.get("warnings", []))

        # 記錄執行結果
        self._log_enforcement_result(results)

        return results

    def _log_enforcement(self, guardrail: PromptGuardrail, result: dict[str, Any]):
        """記錄執行"""
        self._enforcement_log.append({
            "guardrail_id": guardrail.guardrail_id,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def _log_enforcement_result(self, result: dict[str, Any]):
        """記錄執行結果"""
        self._enforcement_log.append({
            "type": "enforcement_result",
            "passed": result["passed"],
            "violation_count": len(result["violations"]),
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_enforcement_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """獲取執行記錄"""
        return self._enforcement_log[-limit:]

    def get_statistics(self) -> dict[str, Any]:
        """獲取統計數據"""
        stats = {
            "total_guardrails": len(self._guardrails),
            "active_guardrails": sum(
                1 for g in self._guardrails.values()
                if g.policy_prompt.enabled
            ),
            "total_checks": sum(g.check_count for g in self._guardrails.values()),
            "total_violations": sum(g.violation_count for g in self._guardrails.values()),
        }

        if stats["total_checks"] > 0:
            stats["violation_rate"] = round(
                stats["total_violations"] / stats["total_checks"] * 100,
                2
            )
        else:
            stats["violation_rate"] = 0

        return stats


class PolicyAsPrompt:
    """
    政策即提示系統
    Policy as Prompt System
    
    核心類別，負責：
    1. 將政策文檔轉換為可執行提示
    2. 生成對應的護欄
    3. 管理政策的生命週期
    
    This is the core class responsible for:
    1. Converting policy documents to executable prompts
    2. Generating corresponding guardrails
    3. Managing policy lifecycle
    
    自成閉環：完整的政策管理生命週期
    """

    # 預定義政策模板
    POLICY_TEMPLATES = {
        "no_harmful_content": {
            "name": "禁止有害內容",
            "type": PolicyType.ETHICS,
            "description": "禁止生成或傳播有害、暴力、歧視性內容",
            "rules": [
                "不得生成暴力或威脅性內容",
                "不得生成歧視性或仇恨言論",
                "不得生成虛假或誤導性資訊",
                "不得生成涉及非法活動的內容",
            ],
            "patterns": [
                r"\b(kill|murder|attack|harm)\b",
                r"\b(hate|racist|sexist)\b",
                r"\b(fake news|misinformation)\b",
            ],
            "enforcement": EnforcementAction.DENY,
        },
        "data_privacy": {
            "name": "數據隱私保護",
            "type": PolicyType.SECURITY,
            "description": "保護個人身份資訊和敏感數據",
            "rules": [
                "不得暴露個人身份資訊 (PII)",
                "不得記錄或傳輸密碼和憑證",
                "不得未授權存取敏感數據",
                "必須對敏感數據進行加密",
            ],
            "patterns": [
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b\d{16}\b",  # Credit card
                r"password\s*[:=]\s*\S+",
                r"api[_-]?key\s*[:=]\s*\S+",
            ],
            "enforcement": EnforcementAction.DENY,
        },
        "code_quality": {
            "name": "代碼品質",
            "type": PolicyType.QUALITY,
            "description": "確保生成的代碼符合品質標準",
            "rules": [
                "不得生成包含已知漏洞的代碼",
                "必須包含適當的錯誤處理",
                "不得使用已棄用的 API",
                "必須遵循安全編碼實踐",
            ],
            "patterns": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"__import__\s*\(",
                r"os\.system\s*\(",
            ],
            "enforcement": EnforcementAction.WARN,
        },
        "compliance_gdpr": {
            "name": "GDPR 合規",
            "type": PolicyType.COMPLIANCE,
            "description": "確保符合歐盟通用數據保護條例",
            "rules": [
                "收集數據前必須獲得同意",
                "必須提供數據刪除機制",
                "必須記錄數據處理活動",
                "必須報告數據洩露事件",
            ],
            "patterns": [],
            "enforcement": EnforcementAction.LOG,
        },
    }

    def __init__(self):
        self._policies: dict[str, PolicyPrompt] = {}
        self._guardrails: dict[str, PromptGuardrail] = {}
        self.enforcer = PolicyEnforcer()

        # 初始化預定義政策
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """初始化預定義政策"""
        for template_id, _template in self.POLICY_TEMPLATES.items():
            self.create_policy_from_template(template_id)

    def create_policy_from_template(self, template_id: str) -> PolicyPrompt | None:
        """從模板創建政策"""
        if template_id not in self.POLICY_TEMPLATES:
            return None

        template = self.POLICY_TEMPLATES[template_id]

        policy_prompt = PolicyPrompt(
            prompt_id=f"POLICY_{template_id.upper()}",
            policy_name=template["name"],
            policy_type=template["type"],
            description=template["description"],
            rules=template["rules"],
            conditions={},
            enforcement_action=template["enforcement"],
        )

        self._policies[policy_prompt.prompt_id] = policy_prompt

        # 創建對應的護欄
        guardrail = PromptGuardrail(
            guardrail_id=f"GUARD_{template_id.upper()}",
            policy_prompt=policy_prompt,
            patterns=template.get("patterns", []),
        )

        self._guardrails[guardrail.guardrail_id] = guardrail
        self.enforcer.register_guardrail(guardrail)

        return policy_prompt

    def create_policy(
        self,
        name: str,
        policy_type: PolicyType,
        description: str,
        rules: list[str],
        patterns: list[str] = None,
        enforcement: EnforcementAction = EnforcementAction.WARN,
        conditions: dict[str, Any] = None,
    ) -> PolicyPrompt:
        """創建自定義政策"""
        prompt_id = f"POLICY_{hashlib.sha256(name.encode()).hexdigest()[:8].upper()}"

        policy_prompt = PolicyPrompt(
            prompt_id=prompt_id,
            policy_name=name,
            policy_type=policy_type,
            description=description,
            rules=rules,
            conditions=conditions or {},
            enforcement_action=enforcement,
        )

        self._policies[prompt_id] = policy_prompt

        # 創建對應的護欄
        guardrail = PromptGuardrail(
            guardrail_id=f"GUARD_{prompt_id.split('_')[1]}",
            policy_prompt=policy_prompt,
            patterns=patterns or [],
        )

        self._guardrails[guardrail.guardrail_id] = guardrail
        self.enforcer.register_guardrail(guardrail)

        return policy_prompt

    def parse_policy_document(self, document: str) -> PolicyPrompt:
        """
        解析政策文檔並轉換為政策提示
        Parse policy document and convert to policy prompt
        
        這是 Policy as Prompt 的核心功能
        """
        # 提取政策名稱
        name_match = re.search(r"政策(名稱|名称)?\s*[:：]\s*(.+)", document)
        name = name_match.group(2).strip() if name_match else "未命名政策"

        # 提取描述
        desc_match = re.search(r"[描述说明]\s*[:：]\s*(.+)", document)
        description = desc_match.group(1).strip() if desc_match else "自動解析的政策"

        # 提取規則
        rules = []
        rule_matches = re.findall(r"[·•\-]\s*(.+)", document)
        rules = [match.strip() for match in rule_matches if len(match.strip()) > 5]

        # 如果沒有找到規則，嘗試提取句子
        if not rules:
            sentences = re.split(r"[。\.\n]", document)
            rules = [s.strip() for s in sentences if 10 < len(s.strip()) < 200]

        # 檢測政策類型
        policy_type = self._detect_policy_type(document)

        # 提取潛在的禁止模式
        patterns = self._extract_patterns(document)

        # 檢測執行動作
        enforcement = self._detect_enforcement(document)

        return self.create_policy(
            name=name,
            policy_type=policy_type,
            description=description,
            rules=rules[:10],  # 最多 10 條規則
            patterns=patterns,
            enforcement=enforcement,
        )

    def _detect_policy_type(self, document: str) -> PolicyType:
        """檢測政策類型"""
        doc_lower = document.lower()

        if any(kw in doc_lower for kw in ["security", "安全", "加密", "認證"]):
            return PolicyType.SECURITY
        elif any(kw in doc_lower for kw in ["compliance", "合規", "gdpr", "hipaa"]):
            return PolicyType.COMPLIANCE
        elif any(kw in doc_lower for kw in ["ethics", "倫理", "道德", "公平"]):
            return PolicyType.ETHICS
        elif any(kw in doc_lower for kw in ["quality", "品質", "質量", "標準"]):
            return PolicyType.QUALITY
        else:
            return PolicyType.OPERATIONAL

    def _extract_patterns(self, document: str) -> list[str]:
        """從文檔中提取禁止模式"""
        patterns = []

        # 查找明確的禁止詞
        prohibit_matches = re.findall(
            r"禁止[^，。\n]*[「『]([^」』]+)[」』]",
            document
        )
        patterns.extend(prohibit_matches)

        # 查找英文關鍵詞
        english_matches = re.findall(
            r"prohibit[ed]?\s+([a-zA-Z_]+)",
            document,
            re.IGNORECASE
        )
        patterns.extend(english_matches)

        return patterns

    def _detect_enforcement(self, document: str) -> EnforcementAction:
        """檢測執行動作"""
        doc_lower = document.lower()

        if any(kw in doc_lower for kw in ["禁止", "拒絕", "deny", "block"]):
            return EnforcementAction.DENY
        elif any(kw in doc_lower for kw in ["警告", "warn"]):
            return EnforcementAction.WARN
        elif any(kw in doc_lower for kw in ["記錄", "log", "audit"]):
            return EnforcementAction.LOG
        else:
            return EnforcementAction.WARN

    def enforce_policies(
        self,
        content: str,
        context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """執行所有政策"""
        return self.enforcer.enforce(content, context)

    def get_policy(self, prompt_id: str) -> PolicyPrompt | None:
        """獲取政策"""
        return self._policies.get(prompt_id)

    def get_all_policies(self) -> list[PolicyPrompt]:
        """獲取所有政策"""
        return list(self._policies.values())

    def enable_policy(self, prompt_id: str):
        """啟用政策"""
        if prompt_id in self._policies:
            self._policies[prompt_id].enabled = True

    def disable_policy(self, prompt_id: str):
        """停用政策"""
        if prompt_id in self._policies:
            self._policies[prompt_id].enabled = False

    def get_prompt_for_ai(self, include_all: bool = False) -> str:
        """
        生成給 AI 的政策提示
        Generate policy prompt for AI
        
        這是 Policy as Prompt 的核心輸出
        """
        prompts = []

        prompts.append("=" * 60)
        prompts.append("AI 行為準則和政策約束")
        prompts.append("=" * 60)
        prompts.append("")

        for policy in self._policies.values():
            if policy.enabled or include_all:
                prompts.append(policy.prompt_text)
                prompts.append("")
                prompts.append("-" * 40)
                prompts.append("")

        prompts.append("=" * 60)
        prompts.append("請嚴格遵守以上所有政策。違反政策的行為將被拒絕或記錄。")
        prompts.append("=" * 60)

        return "\n".join(prompts)

    def get_statistics(self) -> dict[str, Any]:
        """獲取統計數據"""
        base_stats = self.enforcer.get_statistics()

        base_stats.update({
            "total_policies": len(self._policies),
            "policies_by_type": {},
            "policies_by_enforcement": {},
        })

        for policy in self._policies.values():
            # 按類型統計
            type_key = policy.policy_type.value
            base_stats["policies_by_type"][type_key] = \
                base_stats["policies_by_type"].get(type_key, 0) + 1

            # 按執行動作統計
            action_key = policy.enforcement_action.value
            base_stats["policies_by_enforcement"][action_key] = \
                base_stats["policies_by_enforcement"].get(action_key, 0) + 1

        return base_stats
