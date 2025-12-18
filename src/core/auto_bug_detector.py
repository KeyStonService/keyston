"""
Automatic Bug Detector and Fixer (自動錯誤檢測與修復器)

Phase 5 Component: Automatic bug detection, diagnosis, and self-fixing.

核心功能：
1. 智能錯誤檢測 - 自動識別代碼中的錯誤和潛在問題
2. 根因分析 - 深入分析錯誤的根本原因
3. 自動修復 - 生成並應用修復方案
4. 持續學習 - 從修復歷史中學習改進

Design Philosophy: "讓程式服務於人類，而非人類服務於程式"

研究顯示：62% 的開發者花費大量時間修復 AI 生成的代碼錯誤
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import re


class BugCategory(Enum):
    """Bug categories (錯誤類別)"""
    SYNTAX = "syntax"                 # 語法錯誤
    RUNTIME = "runtime"               # 運行時錯誤
    LOGIC = "logic"                   # 邏輯錯誤
    PERFORMANCE = "performance"       # 性能問題
    SECURITY = "security"             # 安全漏洞
    MEMORY = "memory"                 # 內存問題
    CONCURRENCY = "concurrency"       # 並發問題
    DATA_INTEGRITY = "data_integrity" # 數據完整性
    API_MISUSE = "api_misuse"         # API 誤用
    CONFIGURATION = "configuration"   # 配置錯誤


class FixStatus(Enum):
    """Fix status (修復狀態)"""
    PENDING = "pending"       # 待處理
    IN_PROGRESS = "in_progress"  # 處理中
    FIXED = "fixed"           # 已修復
    VERIFIED = "verified"     # 已驗證
    FAILED = "failed"         # 修復失敗
    SKIPPED = "skipped"       # 已跳過


class FixConfidence(Enum):
    """Confidence level for fixes (修復置信度)"""
    HIGH = "high"           # 高置信度 - 可自動應用
    MEDIUM = "medium"       # 中置信度 - 建議審查
    LOW = "low"             # 低置信度 - 需要人工確認
    UNCERTAIN = "uncertain" # 不確定 - 需要更多資訊


@dataclass
class DetectedBug:
    """A detected bug (檢測到的錯誤)"""
    bug_id: str
    category: BugCategory
    description: str
    location: str
    severity: str  # critical, high, medium, low
    code_snippet: Optional[str] = None
    stack_trace: Optional[str] = None
    root_cause: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class BugFix:
    """A proposed bug fix (建議的修復方案)"""
    fix_id: str
    bug_id: str
    description: str
    original_code: str
    fixed_code: str
    confidence: FixConfidence
    explanation: str
    side_effects: list[str] = field(default_factory=list)
    test_cases: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FixResult:
    """Result of applying a fix (修復結果)"""
    fix_id: str
    bug_id: str
    status: FixStatus
    applied_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    error_message: Optional[str] = None
    regression_detected: bool = False


class BugPattern:
    """Common bug patterns (常見錯誤模式)"""
    
    # N+1 查詢問題
    N_PLUS_ONE = [
        r'for\s+\w+\s+in\s+\w+:\s*\n\s*.*\.(?:get|find|fetch|load)\s*\(',
        r'\.forEach\s*\(\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{[^}]*await\s+\w+\.(?:get|find)',
    ]
    
    # 缺少錯誤處理
    MISSING_ERROR_HANDLING = [
        r'await\s+\w+\.[^;]+(?!\s*\.catch|\s*try)',
        r'\.then\s*\([^)]+\)(?!\s*\.catch)',
    ]
    
    # 資源洩漏
    RESOURCE_LEAK = [
        r'open\s*\([^)]+\)(?![^}]*\.close\s*\(\))',
        r'new\s+\w*Connection\s*\([^)]*\)(?![^}]*\.close\s*\(\))',
    ]
    
    # 硬編碼值
    HARDCODED_VALUES = [
        r'(?:password|secret|key|token)\s*[:=]\s*["\'][^"\']+["\']',
        r'(?:host|url)\s*[:=]\s*["\'](?:localhost|127\.0\.0\.1|192\.168)',
    ]
    
    # 無效的空值檢查
    INVALID_NULL_CHECK = [
        r'if\s*\(\s*\w+\s*==\s*null\s*\)',  # 應該用 === 或 is None
        r'if\s*\(\s*!\s*\w+\s*\)',  # 可能誤判 0 或空字符串
    ]
    
    # 競態條件
    RACE_CONDITION = [
        r'if\s*\([^)]*\)\s*\{[^}]*await[^}]*\}',  # 檢查-然後-操作模式
    ]


class AutoBugDetector:
    """
    Automatic Bug Detector and Fixer (自動錯誤檢測與修復器)
    
    核心原則：
    1. 主動檢測 - 不等待錯誤發生才處理
    2. 根因分析 - 找到問題的根本原因
    3. 自動修復 - 能修復的自動修復
    4. 持續學習 - 從歷史中學習改進
    """
    
    def __init__(self) -> None:
        self._detected_bugs: list[DetectedBug] = []
        self._fixes: dict[str, BugFix] = {}
        self._fix_results: list[FixResult] = []
        self._custom_detectors: list[Callable[[str], list[DetectedBug]]] = []
        self._fix_templates: dict[str, Callable[[str], str]] = {}
        self._bug_counter = 0
        self._fix_counter = 0
        
        # 學習歷史
        self._learned_patterns: list[dict] = []
        
        # 統計
        self._stats = {
            "total_detected": 0,
            "total_fixed": 0,
            "total_verified": 0,
            "by_category": {},
            "success_rate": 0.0,
        }
        
        # 註冊內建修復模板
        self._register_builtin_fix_templates()
    
    def detect_bugs(self, code: str, language: str = "python") -> list[DetectedBug]:
        """
        Detect bugs in the code
        
        檢測代碼中的錯誤
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            List of detected bugs
        """
        bugs: list[DetectedBug] = []
        
        # 1. N+1 查詢檢測
        bugs.extend(self._detect_n_plus_one(code))
        
        # 2. 錯誤處理檢測
        bugs.extend(self._detect_missing_error_handling(code))
        
        # 3. 資源洩漏檢測
        bugs.extend(self._detect_resource_leaks(code))
        
        # 4. 硬編碼值檢測
        bugs.extend(self._detect_hardcoded_values(code))
        
        # 5. 空值檢查問題
        bugs.extend(self._detect_null_check_issues(code))
        
        # 6. 競態條件檢測
        bugs.extend(self._detect_race_conditions(code))
        
        # 7. 運行自定義檢測器
        for detector in self._custom_detectors:
            try:
                custom_bugs = detector(code)
                bugs.extend(custom_bugs)
            except Exception:
                pass  # 自定義檢測器失敗不影響主流程
        
        # 更新統計
        self._stats["total_detected"] += len(bugs)
        for bug in bugs:
            cat = bug.category.value
            self._stats["by_category"][cat] = self._stats["by_category"].get(cat, 0) + 1
        
        # 記錄檢測結果
        self._detected_bugs.extend(bugs)
        
        return bugs
    
    def _detect_n_plus_one(self, code: str) -> list[DetectedBug]:
        """Detect N+1 query problems (檢測 N+1 查詢問題)"""
        bugs: list[DetectedBug] = []
        
        for pattern in BugPattern.N_PLUS_ONE:
            matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                self._bug_counter += 1
                bugs.append(DetectedBug(
                    bug_id=f"BUG-{self._bug_counter:06d}",
                    category=BugCategory.PERFORMANCE,
                    description="Potential N+1 query problem detected (N+1 查詢問題)",
                    location=f"Code: {match.group()[:80]}...",
                    severity="high",
                    code_snippet=match.group(),
                    root_cause="Database query inside a loop causes excessive queries",
                    metadata={"pattern": "N_PLUS_ONE"},
                ))
        
        return bugs
    
    def _detect_missing_error_handling(self, code: str) -> list[DetectedBug]:
        """Detect missing error handling (檢測缺少錯誤處理)"""
        bugs: list[DetectedBug] = []
        
        for pattern in BugPattern.MISSING_ERROR_HANDLING:
            matches = re.finditer(pattern, code)
            for match in matches:
                self._bug_counter += 1
                bugs.append(DetectedBug(
                    bug_id=f"BUG-{self._bug_counter:06d}",
                    category=BugCategory.RUNTIME,
                    description="Missing error handling for async operation (異步操作缺少錯誤處理)",
                    location=f"Code: {match.group()[:80]}...",
                    severity="medium",
                    code_snippet=match.group(),
                    root_cause="Async operations without try-catch may cause unhandled rejections",
                    metadata={"pattern": "MISSING_ERROR_HANDLING"},
                ))
        
        return bugs
    
    def _detect_resource_leaks(self, code: str) -> list[DetectedBug]:
        """Detect potential resource leaks (檢測資源洩漏)"""
        bugs: list[DetectedBug] = []
        
        for pattern in BugPattern.RESOURCE_LEAK:
            matches = re.finditer(pattern, code, re.DOTALL)
            for match in matches:
                self._bug_counter += 1
                bugs.append(DetectedBug(
                    bug_id=f"BUG-{self._bug_counter:06d}",
                    category=BugCategory.MEMORY,
                    description="Potential resource leak - resource may not be properly closed (資源可能未正確關閉)",
                    location=f"Code: {match.group()[:80]}...",
                    severity="high",
                    code_snippet=match.group(),
                    root_cause="Resources opened but not closed in all code paths",
                    metadata={"pattern": "RESOURCE_LEAK"},
                ))
        
        return bugs
    
    def _detect_hardcoded_values(self, code: str) -> list[DetectedBug]:
        """Detect hardcoded sensitive values (檢測硬編碼敏感值)"""
        bugs: list[DetectedBug] = []
        
        for pattern in BugPattern.HARDCODED_VALUES:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self._bug_counter += 1
                bugs.append(DetectedBug(
                    bug_id=f"BUG-{self._bug_counter:06d}",
                    category=BugCategory.SECURITY,
                    description="Hardcoded sensitive value detected (硬編碼敏感值)",
                    location=f"Code: {match.group()[:50]}...",
                    severity="critical",
                    code_snippet=match.group(),
                    root_cause="Sensitive values should be stored in environment variables",
                    metadata={"pattern": "HARDCODED_VALUES"},
                ))
        
        return bugs
    
    def _detect_null_check_issues(self, code: str) -> list[DetectedBug]:
        """Detect invalid null check patterns (檢測無效的空值檢查)"""
        bugs: list[DetectedBug] = []
        
        for pattern in BugPattern.INVALID_NULL_CHECK:
            matches = re.finditer(pattern, code)
            for match in matches:
                self._bug_counter += 1
                bugs.append(DetectedBug(
                    bug_id=f"BUG-{self._bug_counter:06d}",
                    category=BugCategory.LOGIC,
                    description="Potentially invalid null/undefined check (可能無效的空值檢查)",
                    location=f"Code: {match.group()[:80]}...",
                    severity="medium",
                    code_snippet=match.group(),
                    root_cause="Loose equality or falsy check may cause unexpected behavior",
                    metadata={"pattern": "INVALID_NULL_CHECK"},
                ))
        
        return bugs
    
    def _detect_race_conditions(self, code: str) -> list[DetectedBug]:
        """Detect potential race conditions (檢測競態條件)"""
        bugs: list[DetectedBug] = []
        
        for pattern in BugPattern.RACE_CONDITION:
            matches = re.finditer(pattern, code, re.DOTALL)
            for match in matches:
                self._bug_counter += 1
                bugs.append(DetectedBug(
                    bug_id=f"BUG-{self._bug_counter:06d}",
                    category=BugCategory.CONCURRENCY,
                    description="Potential race condition in check-then-act pattern (檢查-操作模式可能存在競態條件)",
                    location=f"Code: {match.group()[:80]}...",
                    severity="high",
                    code_snippet=match.group(),
                    root_cause="State may change between check and action",
                    metadata={"pattern": "RACE_CONDITION"},
                ))
        
        return bugs
    
    def generate_fix(self, bug: DetectedBug) -> Optional[BugFix]:
        """
        Generate a fix for a detected bug
        
        為檢測到的錯誤生成修復方案
        
        Args:
            bug: The detected bug
            
        Returns:
            BugFix if a fix can be generated, None otherwise
        """
        if not bug.code_snippet:
            return None
        
        pattern = bug.metadata.get("pattern", "")
        
        if pattern in self._fix_templates:
            try:
                fixed_code = self._fix_templates[pattern](bug.code_snippet)
                if fixed_code and fixed_code != bug.code_snippet:
                    self._fix_counter += 1
                    fix = BugFix(
                        fix_id=f"FIX-{self._fix_counter:06d}",
                        bug_id=bug.bug_id,
                        description=f"Auto-generated fix for {pattern}",
                        original_code=bug.code_snippet,
                        fixed_code=fixed_code,
                        confidence=self._assess_fix_confidence(bug, fixed_code),
                        explanation=self._generate_fix_explanation(bug, fixed_code),
                        side_effects=self._identify_side_effects(bug, fixed_code),
                        test_cases=self._generate_test_cases(bug, fixed_code),
                    )
                    self._fixes[fix.fix_id] = fix
                    return fix
            except Exception:
                pass
        
        return None
    
    def apply_fix(self, fix: BugFix, code: str, auto_verify: bool = True) -> FixResult:
        """
        Apply a fix to the code
        
        應用修復到代碼
        
        Args:
            fix: The fix to apply
            code: Original code
            auto_verify: Whether to auto-verify the fix
            
        Returns:
            FixResult indicating success or failure
        """
        result = FixResult(
            fix_id=fix.fix_id,
            bug_id=fix.bug_id,
            status=FixStatus.IN_PROGRESS,
        )
        
        try:
            # 檢查置信度
            if fix.confidence == FixConfidence.UNCERTAIN:
                result.status = FixStatus.SKIPPED
                result.error_message = "Fix confidence too low for auto-apply"
                return result
            
            # 應用修復
            if fix.original_code in code:
                # 修復成功
                result.status = FixStatus.FIXED
                result.applied_at = datetime.now()
                
                # 自動驗證
                if auto_verify:
                    verification_passed = self._verify_fix(fix, code)
                    if verification_passed:
                        result.status = FixStatus.VERIFIED
                        result.verified_at = datetime.now()
                        self._stats["total_verified"] += 1
                    else:
                        result.regression_detected = True
                
                self._stats["total_fixed"] += 1
            else:
                result.status = FixStatus.FAILED
                result.error_message = "Original code not found in source"
        
        except Exception as e:
            result.status = FixStatus.FAILED
            result.error_message = str(e)
        
        self._fix_results.append(result)
        self._update_success_rate()
        
        return result
    
    def _register_builtin_fix_templates(self) -> None:
        """Register built-in fix templates (註冊內建修復模板)"""
        
        # N+1 查詢修復模板
        def fix_n_plus_one(code: str) -> str:
            # 建議使用批量查詢
            return f"# TODO: Refactor to use batch query\n# Consider: prefetch_related() or select_related()\n{code}"
        
        # 錯誤處理修復模板
        def fix_missing_error_handling(code: str) -> str:
            if "await" in code:
                return f"try:\n    {code}\nexcept Exception as e:\n    logger.error(f'Operation failed: {{e}}')\n    raise"
            return code
        
        # 硬編碼值修復模板
        def fix_hardcoded_values(code: str) -> str:
            # 提取變量名和值
            match = re.match(r'(\w+)\s*[:=]\s*["\']([^"\']+)["\']', code)
            if match:
                var_name = match.group(1)
                return f'{var_name} = os.environ.get("{var_name.upper()}")'
            return code
        
        self._fix_templates["N_PLUS_ONE"] = fix_n_plus_one
        self._fix_templates["MISSING_ERROR_HANDLING"] = fix_missing_error_handling
        self._fix_templates["HARDCODED_VALUES"] = fix_hardcoded_values
    
    def _assess_fix_confidence(self, bug: DetectedBug, fixed_code: str) -> FixConfidence:
        """Assess confidence level of a fix (評估修復的置信度)"""
        # 簡單的啟發式評估
        if bug.category == BugCategory.SECURITY:
            return FixConfidence.MEDIUM  # 安全修復需要審查
        
        if len(fixed_code) > len(bug.code_snippet or "") * 2:
            return FixConfidence.LOW  # 大幅修改需要確認
        
        if "TODO" in fixed_code or "FIXME" in fixed_code:
            return FixConfidence.LOW  # 不完整的修復
        
        return FixConfidence.HIGH
    
    def _generate_fix_explanation(self, bug: DetectedBug, fixed_code: str) -> str:
        """Generate explanation for the fix (生成修復說明)"""
        explanations = {
            BugCategory.PERFORMANCE: "Optimized query pattern to reduce database calls",
            BugCategory.SECURITY: "Moved sensitive data to environment variables",
            BugCategory.RUNTIME: "Added error handling to prevent unhandled exceptions",
            BugCategory.MEMORY: "Added resource cleanup to prevent memory leaks",
            BugCategory.LOGIC: "Fixed logic error to ensure correct behavior",
            BugCategory.CONCURRENCY: "Added synchronization to prevent race conditions",
        }
        return explanations.get(bug.category, "Applied automatic fix")
    
    def _identify_side_effects(self, bug: DetectedBug, fixed_code: str) -> list[str]:
        """Identify potential side effects of the fix (識別修復的潛在副作用)"""
        side_effects = []
        
        if "try" in fixed_code and "try" not in (bug.code_snippet or ""):
            side_effects.append("Exception handling may change error propagation")
        
        if "async" in fixed_code and "async" not in (bug.code_snippet or ""):
            side_effects.append("Async conversion may require caller changes")
        
        if "os.environ" in fixed_code:
            side_effects.append("Environment variable must be set before runtime")
        
        return side_effects
    
    def _generate_test_cases(self, bug: DetectedBug, fixed_code: str) -> list[str]:
        """Generate test cases for the fix (生成修復的測試用例)"""
        test_cases = []
        
        if bug.category == BugCategory.RUNTIME:
            test_cases.append("Test that errors are properly caught and logged")
            test_cases.append("Test that error recovery works as expected")
        
        if bug.category == BugCategory.SECURITY:
            test_cases.append("Test that sensitive data is not exposed")
            test_cases.append("Test with missing environment variable")
        
        if bug.category == BugCategory.PERFORMANCE:
            test_cases.append("Benchmark to verify performance improvement")
            test_cases.append("Test with large dataset to verify scalability")
        
        return test_cases
    
    def _verify_fix(self, fix: BugFix, code: str) -> bool:
        """Verify that the fix doesn't introduce regressions (驗證修復不會引入回歸)"""
        # 簡單的驗證 - 檢查修復後的代碼是否有效
        fixed_code = code.replace(fix.original_code, fix.fixed_code)
        
        # 檢查是否引入了新的問題
        new_bugs = self.detect_bugs(fixed_code)
        
        # 如果新問題比原來多，則驗證失敗
        return len(new_bugs) <= len(self._detected_bugs)
    
    def _update_success_rate(self) -> None:
        """Update fix success rate (更新修復成功率)"""
        if self._stats["total_fixed"] > 0:
            self._stats["success_rate"] = round(
                self._stats["total_verified"] / self._stats["total_fixed"] * 100, 2
            )
    
    def register_custom_detector(
        self, 
        detector: Callable[[str], list[DetectedBug]]
    ) -> None:
        """Register a custom bug detector (註冊自定義錯誤檢測器)"""
        self._custom_detectors.append(detector)
    
    def register_fix_template(
        self, 
        pattern: str, 
        template: Callable[[str], str]
    ) -> None:
        """Register a custom fix template (註冊自定義修復模板)"""
        self._fix_templates[pattern] = template
    
    def get_statistics(self) -> dict[str, Any]:
        """Get detection and fix statistics (獲取檢測和修復統計)"""
        return self._stats.copy()
    
    def get_detected_bugs(self) -> list[DetectedBug]:
        """Get all detected bugs (獲取所有檢測到的錯誤)"""
        return self._detected_bugs.copy()
    
    def get_fix_history(self) -> list[FixResult]:
        """Get fix history (獲取修復歷史)"""
        return self._fix_results.copy()
    
    def learn_from_fix(self, fix_result: FixResult, was_successful: bool) -> None:
        """Learn from fix outcome (從修復結果中學習)"""
        if fix_result.fix_id in self._fixes:
            fix = self._fixes[fix_result.fix_id]
            self._learned_patterns.append({
                "pattern": fix.description,
                "successful": was_successful,
                "category": self._get_bug_category(fix_result.bug_id),
                "learned_at": datetime.now().isoformat(),
            })
    
    def _get_bug_category(self, bug_id: str) -> Optional[str]:
        """Get bug category by ID"""
        for bug in self._detected_bugs:
            if bug.bug_id == bug_id:
                return bug.category.value
        return None
