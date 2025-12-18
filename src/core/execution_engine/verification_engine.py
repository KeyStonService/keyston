"""
═══════════════════════════════════════════════════════════
        Verification Engine - 驗證引擎
        確保執行結果符合預期
═══════════════════════════════════════════════════════════

核心功能：
1. 驗證執行結果
2. 多策略驗證支持
3. 自定義驗證規則
4. 驗證報告生成
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import uuid


class VerificationStrategy(Enum):
    """驗證策略"""
    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    SCHEMA_VALIDATION = "schema_validation"
    CUSTOM = "custom"
    SEMANTIC = "semantic"
    STATISTICAL = "statistical"


class VerificationSeverity(Enum):
    """驗證嚴重性"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class VerificationCheck:
    """驗證檢查"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # 檢查類型
    strategy: VerificationStrategy = VerificationStrategy.EXACT_MATCH
    
    # 期望值
    expected: Any = None
    
    # 實際值
    actual: Any = None
    
    # 結果
    passed: bool = False
    severity: VerificationSeverity = VerificationSeverity.ERROR
    message: str = ""
    
    # 自定義檢查
    checker: Optional[Callable] = None


@dataclass
class VerificationResult:
    """驗證結果"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 整體結果
    passed: bool = False
    
    # 時間
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    
    # 檢查列表
    checks: List[VerificationCheck] = field(default_factory=list)
    
    # 統計
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    
    # 錯誤和警告
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)


class VerificationEngine:
    """
    驗證引擎 - 確保執行結果符合預期
    
    核心職責：
    1. 驗證執行輸出是否正確
    2. 支持多種驗證策略
    3. 生成詳細的驗證報告
    4. 支持自定義驗證規則
    """
    
    def __init__(self):
        """初始化驗證引擎"""
        
        # 自定義驗證器
        self._validators: Dict[str, Callable] = {}
        
        # 驗證歷史
        self._verification_history: List[VerificationResult] = []
        
        # 統計
        self._stats = {
            "total_verifications": 0,
            "passed_verifications": 0,
            "failed_verifications": 0,
        }
        
        # 註冊默認驗證器
        self._register_default_validators()
    
    def _register_default_validators(self):
        """註冊默認驗證器"""
        
        self._validators["not_null"] = self._validate_not_null
        self._validators["type_check"] = self._validate_type
        self._validators["range_check"] = self._validate_range
        self._validators["pattern_match"] = self._validate_pattern
        self._validators["contains"] = self._validate_contains
        self._validators["length"] = self._validate_length
    
    def verify(
        self,
        actual: Any,
        expected: Any,
        strategy: VerificationStrategy = VerificationStrategy.EXACT_MATCH,
        checks: Optional[List[Dict[str, Any]]] = None
    ) -> VerificationResult:
        """
        執行驗證
        
        Args:
            actual: 實際值
            expected: 期望值
            strategy: 驗證策略
            checks: 額外檢查列表
            
        Returns:
            驗證結果
        """
        
        start_time = datetime.now()
        
        result = VerificationResult()
        
        # 執行主要驗證
        main_check = self._execute_check(
            VerificationCheck(
                name="main_verification",
                description="Main verification check",
                strategy=strategy,
                expected=expected,
                actual=actual,
            )
        )
        result.checks.append(main_check)
        
        # 執行額外檢查
        if checks:
            for check_def in checks:
                check = VerificationCheck(
                    name=check_def.get("name", "custom_check"),
                    description=check_def.get("description", ""),
                    strategy=VerificationStrategy(
                        check_def.get("strategy", "exact_match")
                    ),
                    expected=check_def.get("expected"),
                    actual=check_def.get("actual", actual),
                    severity=VerificationSeverity(
                        check_def.get("severity", "error")
                    ),
                )
                
                executed_check = self._execute_check(check)
                result.checks.append(executed_check)
        
        # 計算統計
        result.total_checks = len(result.checks)
        result.passed_checks = len([c for c in result.checks if c.passed])
        result.failed_checks = len([
            c for c in result.checks 
            if not c.passed and c.severity == VerificationSeverity.ERROR
        ])
        result.warning_checks = len([
            c for c in result.checks 
            if not c.passed and c.severity == VerificationSeverity.WARNING
        ])
        
        # 收集錯誤和警告
        for check in result.checks:
            if not check.passed:
                if check.severity == VerificationSeverity.ERROR:
                    result.errors.append(check.message)
                elif check.severity == VerificationSeverity.WARNING:
                    result.warnings.append(check.message)
        
        # 判斷整體結果
        result.passed = result.failed_checks == 0
        
        # 計算持續時間
        end_time = datetime.now()
        result.duration_ms = int(
            (end_time - start_time).total_seconds() * 1000
        )
        
        # 更新統計
        self._stats["total_verifications"] += 1
        if result.passed:
            self._stats["passed_verifications"] += 1
        else:
            self._stats["failed_verifications"] += 1
        
        # 保存歷史
        self._verification_history.append(result)
        
        return result
    
    def _execute_check(self, check: VerificationCheck) -> VerificationCheck:
        """執行單個驗證檢查"""
        
        try:
            if check.strategy == VerificationStrategy.EXACT_MATCH:
                check.passed = self._exact_match(check.actual, check.expected)
                
            elif check.strategy == VerificationStrategy.PARTIAL_MATCH:
                check.passed = self._partial_match(check.actual, check.expected)
                
            elif check.strategy == VerificationStrategy.SCHEMA_VALIDATION:
                check.passed = self._schema_validate(check.actual, check.expected)
                
            elif check.strategy == VerificationStrategy.SEMANTIC:
                check.passed = self._semantic_match(check.actual, check.expected)
                
            elif check.strategy == VerificationStrategy.STATISTICAL:
                check.passed = self._statistical_match(check.actual, check.expected)
                
            elif check.strategy == VerificationStrategy.CUSTOM:
                if check.checker:
                    check.passed = check.checker(check.actual, check.expected)
                else:
                    check.passed = False
            
            if check.passed:
                check.message = f"Check '{check.name}' passed"
            else:
                check.message = (
                    f"Check '{check.name}' failed: "
                    f"expected {check.expected}, got {check.actual}"
                )
                
        except Exception as e:
            check.passed = False
            check.message = f"Check '{check.name}' error: {str(e)}"
        
        return check
    
    def _exact_match(self, actual: Any, expected: Any) -> bool:
        """精確匹配"""
        return actual == expected
    
    def _partial_match(self, actual: Any, expected: Any) -> bool:
        """部分匹配"""
        
        if isinstance(expected, dict) and isinstance(actual, dict):
            # 檢查 expected 中的所有鍵是否在 actual 中且值匹配
            for key, value in expected.items():
                if key not in actual:
                    return False
                if not self._partial_match(actual[key], value):
                    return False
            return True
        
        elif isinstance(expected, list) and isinstance(actual, list):
            # 檢查 expected 中的所有項是否在 actual 中
            for item in expected:
                if item not in actual:
                    return False
            return True
        
        elif isinstance(expected, str) and isinstance(actual, str):
            # 字符串包含檢查
            return expected in actual
        
        else:
            return actual == expected
    
    def _schema_validate(self, actual: Any, schema: Any) -> bool:
        """Schema 驗證"""
        
        if not isinstance(schema, dict):
            return False
        
        schema_type = schema.get("type")
        
        if schema_type == "object":
            if not isinstance(actual, dict):
                return False
            
            # 檢查必需字段
            required = schema.get("required", [])
            for field in required:
                if field not in actual:
                    return False
            
            # 檢查屬性
            properties = schema.get("properties", {})
            for prop, prop_schema in properties.items():
                if prop in actual:
                    if not self._schema_validate(actual[prop], prop_schema):
                        return False
            
            return True
        
        elif schema_type == "array":
            if not isinstance(actual, list):
                return False
            
            items_schema = schema.get("items")
            if items_schema:
                for item in actual:
                    if not self._schema_validate(item, items_schema):
                        return False
            
            return True
        
        elif schema_type == "string":
            return isinstance(actual, str)
        
        elif schema_type == "number":
            return isinstance(actual, (int, float))
        
        elif schema_type == "boolean":
            return isinstance(actual, bool)
        
        elif schema_type == "null":
            return actual is None
        
        return True
    
    def _semantic_match(self, actual: Any, expected: Any) -> bool:
        """語義匹配（簡化實現）"""
        
        # 轉換為字符串進行比較
        actual_str = str(actual).lower()
        expected_str = str(expected).lower()
        
        # 檢查語義相似性
        # 這是簡化實現，實際應使用 NLP
        return (
            actual_str == expected_str or
            expected_str in actual_str or
            actual_str in expected_str
        )
    
    def _statistical_match(self, actual: Any, expected: Any) -> bool:
        """統計匹配"""
        
        if not isinstance(expected, dict):
            return False
        
        # 獲取期望的統計參數
        min_val = expected.get("min")
        max_val = expected.get("max")
        mean = expected.get("mean")
        tolerance = expected.get("tolerance", 0.1)
        
        if isinstance(actual, (int, float)):
            if min_val is not None and actual < min_val:
                return False
            if max_val is not None and actual > max_val:
                return False
            if mean is not None:
                if abs(actual - mean) > mean * tolerance:
                    return False
            return True
        
        elif isinstance(actual, list):
            if not actual:
                return False
            
            actual_mean = sum(actual) / len(actual)
            if mean is not None:
                if abs(actual_mean - mean) > mean * tolerance:
                    return False
            
            if min_val is not None and min(actual) < min_val:
                return False
            if max_val is not None and max(actual) > max_val:
                return False
            
            return True
        
        return False
    
    def verify_output(
        self,
        output: Any,
        rules: List[Dict[str, Any]]
    ) -> VerificationResult:
        """
        使用規則列表驗證輸出
        
        Args:
            output: 輸出值
            rules: 驗證規則列表
            
        Returns:
            驗證結果
        """
        
        checks = []
        
        for rule in rules:
            rule_type = rule.get("type", "not_null")
            validator = self._validators.get(rule_type)
            
            if validator:
                passed, message = validator(output, rule)
                checks.append({
                    "name": rule.get("name", rule_type),
                    "strategy": "custom",
                    "expected": rule.get("expected"),
                    "passed": passed,
                    "message": message,
                })
        
        return self.verify(output, None, checks=checks)
    
    def register_validator(self, name: str, validator: Callable):
        """註冊自定義驗證器"""
        self._validators[name] = validator
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return self._stats.copy()
    
    def get_history(self, limit: int = 100) -> List[VerificationResult]:
        """獲取驗證歷史"""
        return self._verification_history[-limit:]
    
    # ============ 默認驗證器實現 ============
    
    def _validate_not_null(
        self,
        value: Any,
        rule: Dict[str, Any]
    ) -> tuple:
        """非空驗證"""
        passed = value is not None
        message = "Value is not null" if passed else "Value is null"
        return passed, message
    
    def _validate_type(
        self,
        value: Any,
        rule: Dict[str, Any]
    ) -> tuple:
        """類型驗證"""
        expected_type = rule.get("expected_type")
        
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "list": list,
            "dict": dict,
            "object": dict,
        }
        
        expected = type_map.get(expected_type, str)
        passed = isinstance(value, expected)
        message = (
            f"Type check {'passed' if passed else 'failed'}: "
            f"expected {expected_type}, got {type(value).__name__}"
        )
        return passed, message
    
    def _validate_range(
        self,
        value: Any,
        rule: Dict[str, Any]
    ) -> tuple:
        """範圍驗證"""
        min_val = rule.get("min")
        max_val = rule.get("max")
        
        if not isinstance(value, (int, float)):
            return False, "Value is not a number"
        
        passed = True
        if min_val is not None and value < min_val:
            passed = False
        if max_val is not None and value > max_val:
            passed = False
        
        message = (
            f"Range check {'passed' if passed else 'failed'}: "
            f"value={value}, range=[{min_val}, {max_val}]"
        )
        return passed, message
    
    def _validate_pattern(
        self,
        value: Any,
        rule: Dict[str, Any]
    ) -> tuple:
        """模式匹配驗證"""
        import re
        
        pattern = rule.get("pattern", ".*")
        
        if not isinstance(value, str):
            value = str(value)
        
        passed = bool(re.match(pattern, value))
        message = (
            f"Pattern check {'passed' if passed else 'failed'}: "
            f"pattern={pattern}"
        )
        return passed, message
    
    def _validate_contains(
        self,
        value: Any,
        rule: Dict[str, Any]
    ) -> tuple:
        """包含驗證"""
        expected = rule.get("expected")
        
        if isinstance(value, (list, tuple, set)):
            passed = expected in value
        elif isinstance(value, dict):
            passed = expected in value
        elif isinstance(value, str):
            passed = str(expected) in value
        else:
            passed = False
        
        message = (
            f"Contains check {'passed' if passed else 'failed'}: "
            f"expected '{expected}' in value"
        )
        return passed, message
    
    def _validate_length(
        self,
        value: Any,
        rule: Dict[str, Any]
    ) -> tuple:
        """長度驗證"""
        min_len = rule.get("min_length", 0)
        max_len = rule.get("max_length")
        
        try:
            length = len(value)
        except TypeError:
            return False, "Value has no length"
        
        passed = length >= min_len
        if max_len is not None:
            passed = passed and length <= max_len
        
        message = (
            f"Length check {'passed' if passed else 'failed'}: "
            f"length={length}, expected=[{min_len}, {max_len}]"
        )
        return passed, message
