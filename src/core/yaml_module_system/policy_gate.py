"""
DevSecOps Policy Gate (安全策略閘門)

實施安全策略驗證，確保 YAML 模組符合組織的安全要求。

Reference: DevSecOps best practices [3] [5]
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import re


class PolicySeverity(Enum):
    """策略嚴重性等級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyCategory(Enum):
    """策略類別"""
    SECURITY = "security"           # 安全相關
    COMPLIANCE = "compliance"       # 合規相關
    QUALITY = "quality"             # 質量相關
    PERFORMANCE = "performance"     # 性能相關
    GOVERNANCE = "governance"       # 治理相關
    OPERATIONAL = "operational"     # 操作相關


class PolicyAction(Enum):
    """策略違規後的動作"""
    BLOCK = "block"         # 阻止部署
    WARN = "warn"           # 發出警告
    AUDIT = "audit"         # 記錄審計
    NOTIFY = "notify"       # 發送通知


@dataclass
class PolicyViolation:
    """策略違規記錄"""
    rule_id: str
    rule_name: str
    severity: PolicySeverity
    category: PolicyCategory
    message: str
    path: Optional[str] = None
    actual_value: Any = None
    expected_value: Any = None
    remediation: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'path': self.path,
            'actual_value': self.actual_value,
            'expected_value': self.expected_value,
            'remediation': self.remediation,
            'detected_at': self.detected_at.isoformat(),
        }


@dataclass
class PolicyRule:
    """
    策略規則定義
    
    定義單個安全/合規策略規則。
    """
    id: str
    name: str
    description: str
    severity: PolicySeverity
    category: PolicyCategory
    action: PolicyAction
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    
    # 驗證邏輯
    validator: Optional[Callable[[Any], bool]] = None
    condition: Optional[str] = None  # 簡單條件表達式
    
    # 元數據
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    
    # 補救建議
    remediation: Optional[str] = None
    documentation_url: Optional[str] = None
    
    def evaluate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Optional[PolicyViolation]:
        """
        評估數據是否符合策略
        
        Args:
            data: 待評估的數據
            context: 額外的上下文信息
        
        Returns:
            PolicyViolation if rule is violated, None otherwise
        """
        if not self.enabled:
            return None
        
        violated = False
        
        if self.validator:
            try:
                violated = not self.validator(data)
            except Exception:
                violated = True
        elif self.condition:
            violated = not self._evaluate_condition(data, context)
        
        if violated:
            return PolicyViolation(
                rule_id=self.id,
                rule_name=self.name,
                severity=self.severity,
                category=self.category,
                message=self.description,
                remediation=self.remediation,
            )
        
        return None
    
    def _evaluate_condition(self, data: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """評估條件表達式"""
        # 簡單的條件評估
        # 支持: exists, equals, contains, matches, etc.
        if not self.condition:
            return True
        
        parts = self.condition.split()
        if len(parts) < 2:
            return True
        
        operator = parts[0]
        path = parts[1]
        value = parts[2] if len(parts) > 2 else None
        
        actual = self._get_value_by_path(data, path)
        
        if operator == 'exists':
            return actual is not None
        elif operator == 'not_exists':
            return actual is None
        elif operator == 'equals' and value:
            return str(actual) == value
        elif operator == 'not_equals' and value:
            return str(actual) != value
        elif operator == 'contains' and value:
            return value in str(actual)
        elif operator == 'matches' and value:
            return bool(re.match(value, str(actual)))
        elif operator == 'greater_than' and value:
            return float(actual) > float(value) if actual else False
        elif operator == 'less_than' and value:
            return float(actual) < float(value) if actual else False
        
        return True
    
    def _get_value_by_path(self, data: Any, path: str) -> Any:
        """根據路徑獲取值"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                current = current[index] if index < len(current) else None
            else:
                return None
        
        return current
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'severity': self.severity.value,
            'category': self.category.value,
            'action': self.action.value,
            'enabled': self.enabled,
            'tags': self.tags,
            'remediation': self.remediation,
            'documentation_url': self.documentation_url,
        }


@dataclass
class PolicyEvaluationResult:
    """策略評估結果"""
    passed: bool
    violations: List[PolicyViolation] = field(default_factory=list)
    warnings: List[PolicyViolation] = field(default_factory=list)
    evaluated_rules: int = 0
    passed_rules: int = 0
    evaluated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def critical_count(self) -> int:
        """嚴重違規數量"""
        return len([v for v in self.violations if v.severity == PolicySeverity.CRITICAL])
    
    @property
    def high_count(self) -> int:
        """高危違規數量"""
        return len([v for v in self.violations if v.severity == PolicySeverity.HIGH])
    
    @property
    def should_block(self) -> bool:
        """是否應該阻止部署"""
        return self.critical_count > 0 or self.high_count > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'passed': self.passed,
            'violations': [v.to_dict() for v in self.violations],
            'warnings': [w.to_dict() for w in self.warnings],
            'evaluated_rules': self.evaluated_rules,
            'passed_rules': self.passed_rules,
            'critical_count': self.critical_count,
            'high_count': self.high_count,
            'should_block': self.should_block,
            'evaluated_at': self.evaluated_at.isoformat(),
        }


class PolicyGate:
    """
    策略閘門
    
    管理和執行所有安全策略規則。
    
    參考：DevSecOps 最佳實踐 [3] [5]
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self._rules: Dict[str, PolicyRule] = {}
        self._exceptions: Dict[str, List[str]] = {}  # rule_id -> [module_ids]
    
    def add_rule(self, rule: PolicyRule) -> None:
        """添加策略規則"""
        self._rules[rule.id] = rule
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除策略規則"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """啟用策略規則"""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = True
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """禁用策略規則"""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = False
            return True
        return False
    
    def add_exception(self, rule_id: str, module_id: str, reason: str, approved_by: str) -> bool:
        """添加例外"""
        if rule_id not in self._rules:
            return False
        
        if rule_id not in self._exceptions:
            self._exceptions[rule_id] = []
        
        self._exceptions[rule_id].append(module_id)
        return True
    
    def is_excepted(self, rule_id: str, module_id: str) -> bool:
        """檢查是否有例外"""
        return module_id in self._exceptions.get(rule_id, [])
    
    def evaluate(self, data: Any, module_id: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None) -> PolicyEvaluationResult:
        """
        評估數據是否符合所有策略
        
        Args:
            data: 待評估的數據
            module_id: 模組 ID（用於檢查例外）
            context: 額外的上下文信息
        
        Returns:
            PolicyEvaluationResult: 評估結果
        """
        result = PolicyEvaluationResult(passed=True)
        
        for rule_id, rule in self._rules.items():
            if not rule.enabled:
                continue
            
            # 檢查例外
            if module_id and self.is_excepted(rule_id, module_id):
                continue
            
            result.evaluated_rules += 1
            
            violation = rule.evaluate(data, context)
            
            if violation:
                if rule.action == PolicyAction.BLOCK:
                    result.violations.append(violation)
                    result.passed = False
                elif rule.action == PolicyAction.WARN:
                    result.warnings.append(violation)
                elif rule.action == PolicyAction.AUDIT:
                    result.warnings.append(violation)
                elif rule.action == PolicyAction.NOTIFY:
                    result.warnings.append(violation)
            else:
                result.passed_rules += 1
        
        return result
    
    def evaluate_by_category(self, data: Any, category: PolicyCategory, 
                            module_id: Optional[str] = None) -> PolicyEvaluationResult:
        """按類別評估策略"""
        result = PolicyEvaluationResult(passed=True)
        
        for rule in self._rules.values():
            if not rule.enabled or rule.category != category:
                continue
            
            if module_id and self.is_excepted(rule.id, module_id):
                continue
            
            result.evaluated_rules += 1
            violation = rule.evaluate(data, None)
            
            if violation:
                if rule.action == PolicyAction.BLOCK:
                    result.violations.append(violation)
                    result.passed = False
                else:
                    result.warnings.append(violation)
            else:
                result.passed_rules += 1
        
        return result
    
    def get_rules(self, category: Optional[PolicyCategory] = None, 
                 severity: Optional[PolicySeverity] = None) -> List[PolicyRule]:
        """獲取策略規則列表"""
        rules = list(self._rules.values())
        
        if category:
            rules = [r for r in rules if r.category == category]
        
        if severity:
            rules = [r for r in rules if r.severity == severity]
        
        return rules
    
    def get_rule(self, rule_id: str) -> Optional[PolicyRule]:
        """獲取單個策略規則"""
        return self._rules.get(rule_id)
    
    # 預定義策略規則
    @classmethod
    def create_default_security_rules(cls) -> List[PolicyRule]:
        """創建默認安全規則"""
        return [
            PolicyRule(
                id="sec-001",
                name="No Plaintext Secrets",
                description="Secrets must not be stored in plaintext",
                severity=PolicySeverity.CRITICAL,
                category=PolicyCategory.SECURITY,
                action=PolicyAction.BLOCK,
                condition="not_exists secrets.plaintext",
                remediation="Use encrypted secrets or secret management service",
            ),
            PolicyRule(
                id="sec-002",
                name="HTTPS Only",
                description="All endpoints must use HTTPS",
                severity=PolicySeverity.HIGH,
                category=PolicyCategory.SECURITY,
                action=PolicyAction.BLOCK,
                validator=lambda data: all(
                    url.startswith('https://') 
                    for url in data.get('endpoints', []) if isinstance(url, str)
                ) if isinstance(data, dict) else True,
                remediation="Change all HTTP URLs to HTTPS",
            ),
            PolicyRule(
                id="sec-003",
                name="No Debug Mode in Production",
                description="Debug mode must be disabled in production",
                severity=PolicySeverity.HIGH,
                category=PolicyCategory.SECURITY,
                action=PolicyAction.BLOCK,
                condition="not_equals debug true",
                remediation="Set debug=false for production deployments",
            ),
            PolicyRule(
                id="sec-004",
                name="Authentication Required",
                description="All services must have authentication enabled",
                severity=PolicySeverity.CRITICAL,
                category=PolicyCategory.SECURITY,
                action=PolicyAction.BLOCK,
                condition="exists authentication.enabled",
                remediation="Enable authentication for all services",
            ),
        ]
    
    @classmethod
    def create_default_compliance_rules(cls) -> List[PolicyRule]:
        """創建默認合規規則"""
        return [
            PolicyRule(
                id="comp-001",
                name="Owner Required",
                description="All modules must have an owner defined",
                severity=PolicySeverity.HIGH,
                category=PolicyCategory.COMPLIANCE,
                action=PolicyAction.BLOCK,
                condition="exists owner.team",
                remediation="Add owner.team to module definition",
            ),
            PolicyRule(
                id="comp-002",
                name="Version Required",
                description="All modules must have a semantic version",
                severity=PolicySeverity.MEDIUM,
                category=PolicyCategory.COMPLIANCE,
                action=PolicyAction.WARN,
                condition="matches version ^\\d+\\.\\d+\\.\\d+",
                remediation="Use semantic versioning (e.g., 1.0.0)",
            ),
            PolicyRule(
                id="comp-003",
                name="Description Required",
                description="All modules must have a description",
                severity=PolicySeverity.LOW,
                category=PolicyCategory.COMPLIANCE,
                action=PolicyAction.WARN,
                condition="exists description",
                remediation="Add a description to the module",
            ),
        ]
