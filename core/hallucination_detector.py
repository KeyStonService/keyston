"""
AI Hallucination Detector (AI 幻覺檢測器)

Phase 5 Component: Detects and prevents AI-generated hallucinations in code and outputs.

核心功能：
1. 代碼幻覺檢測 - 識別 AI 生成的看似正確但實際有問題的代碼
2. 置信度評估 - 評估 AI 輸出的可靠性
3. 事實驗證 - 驗證 AI 生成內容的準確性
4. 安全漏洞檢測 - 識別 AI 可能忽略的安全問題

Design Philosophy: "讓程式服務於人類，而非人類服務於程式"
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import re
import hashlib


class HallucinationType(Enum):
    """Types of AI hallucinations (AI 幻覺類型)"""
    CODE_SYNTAX = "code_syntax"           # 語法幻覺
    SECURITY_FLAW = "security_flaw"       # 安全漏洞幻覺
    LOGIC_ERROR = "logic_error"           # 邏輯錯誤幻覺
    API_MISUSE = "api_misuse"             # API 誤用幻覺
    CONTEXT_MISMATCH = "context_mismatch" # 上下文不匹配
    OVERCONFIDENCE = "overconfidence"     # 過度自信幻覺
    INCOMPLETE = "incomplete"             # 不完整實現
    FALSE_CLAIM = "false_claim"           # 虛假聲明


class SeverityLevel(Enum):
    """Severity levels for detected issues (問題嚴重程度)"""
    CRITICAL = "critical"   # 致命 - 必須立即處理
    HIGH = "high"           # 高 - 應盡快處理
    MEDIUM = "medium"       # 中 - 需要關注
    LOW = "low"             # 低 - 建議改進
    INFO = "info"           # 資訊 - 僅供參考


@dataclass
class HallucinationDetection:
    """Detected hallucination record (檢測到的幻覺記錄)"""
    detection_id: str
    hallucination_type: HallucinationType
    severity: SeverityLevel
    description: str
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: float = 0.0  # 檢測置信度 0-1
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Code validation result (代碼驗證結果)"""
    is_valid: bool
    overall_confidence: float  # 整體置信度 0-1
    hallucinations: list[HallucinationDetection] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=datetime.now)


class SecurityPattern:
    """Security vulnerability patterns (安全漏洞模式)"""
    
    # 明文密碼存儲模式
    PLAINTEXT_PASSWORD = [
        r'password\s*[:=]\s*["\'][^"\']+["\']',
        r'password\s*[:=]\s*data\.password',
        r'password\s*[:=]\s*\w+\.password(?!\s*\.\s*hash)',
    ]
    
    # SQL 注入風險模式
    SQL_INJECTION = [
        r'execute\s*\(\s*["\'].*\$\{',
        r'query\s*\(\s*["\'].*\+\s*\w+',
        r'raw\s*\(\s*["\'].*\+',
    ]
    
    # 缺少輸入驗證
    MISSING_VALIDATION = [
        r'async\s+\w+\s*\([^)]*data[^)]*\)\s*\{[^}]*(?!validate|check|verify)',
    ]
    
    # 缺少錯誤處理
    MISSING_ERROR_HANDLING = [
        r'await\s+\w+\.[^;]+(?!\s*\.catch|\s*try)',
    ]
    
    # 敏感數據暴露
    SENSITIVE_DATA_EXPOSURE = [
        r'console\.log\s*\([^)]*password',
        r'console\.log\s*\([^)]*secret',
        r'console\.log\s*\([^)]*token',
    ]


class HallucinationDetector:
    """
    AI Hallucination Detector (AI 幻覺檢測器)
    
    核心原則：
    1. 不信任 AI 的任何輸出，全部需要驗證
    2. 多層檢測，從語法到語義到安全
    3. 提供修復建議，而非僅指出問題
    
    研究顯示：約 50% 的 AI 生成代碼審查包含幻覺
    """
    
    def __init__(self) -> None:
        """Initialize the detector with in-memory state.

        The constructor prepares all bookkeeping structures used across the
        detection lifecycle so that downstream methods can focus purely on
        analysis. State tracked includes:

        - detection history for auditability and post-hoc analysis
        - a lookup index for detection identifiers to enable feedback mapping
        - custom validators registered by callers for domain-specific checks
        - a false-positive cache to suppress repeated noise from known code
        - monotonically increasing detection identifiers for traceability
        - statistics that summarize validations and severities for reporting
        - feedback summaries to understand false-positive clusters and trend lines
        """

        self._detection_history: list[HallucinationDetection] = []
        self._detection_index: dict[str, HallucinationDetection] = {}
        self._custom_validators: list[Callable[[str], list[HallucinationDetection]]] = []
        self._false_positive_hashes: set[str] = set()
        self._detection_count = 0

        # 統計數據
        self._stats = {
            "total_validations": 0,
            "total_hallucinations": 0,
            "by_type": {},
            "by_severity": {},
            "by_pattern": {},
            "false_positive_marks": 0,
        }

        # 人類回饋記錄，用於自動演化與誤報抑制
        self._feedback_log: list[dict[str, Any]] = []
        self._feedback_stats: dict[str, Any] = {
            "total": 0,
            "by_verdict": {},
            "by_pattern": {},
            "by_type": {},
        }
    
    def validate_code(self, code: str, language: str = "python") -> ValidationResult:
        """Validate AI-generated code for hallucinations.

        The validator runs layered checks ranging from regular-expression
        heuristics to caller-supplied validators, filters known false
        positives, and produces both a structured list of detections and
        actionable suggestions. This is the primary API entry point for the
        detector.

        Args:
            code: Source code produced by an AI system or other generator.
            language: Programming language hint used by some heuristics
                (currently tuned for Python defaults).

        Returns:
            ValidationResult capturing validity, detections, warnings,
            suggestions, and the computed overall confidence score.
        """
        hallucinations: list[HallucinationDetection] = []
        warnings: list[str] = []
        suggestions: list[str] = []
        
        # 1. 安全漏洞檢測
        security_issues = self._detect_security_flaws(code)
        hallucinations.extend(security_issues)
        
        # 2. 邏輯錯誤檢測
        logic_issues = self._detect_logic_errors(code, language)
        hallucinations.extend(logic_issues)
        
        # 3. 不完整實現檢測
        incomplete_issues = self._detect_incomplete_implementation(code)
        hallucinations.extend(incomplete_issues)
        
        # 4. 過度自信檢測
        overconfidence_issues = self._detect_overconfidence(code)
        hallucinations.extend(overconfidence_issues)
        
        # 5. 運行自定義驗證器
        for validator in self._custom_validators:
            try:
                custom_issues = validator(code)
                hallucinations.extend(custom_issues)
            except Exception:
                warnings.append("Custom validator failed")
        
        # 過濾已標記為誤報的檢測
        hallucinations = self._filter_false_positives(hallucinations, code)
        
        # 計算整體置信度
        overall_confidence = self._calculate_confidence(hallucinations)
        
        # 生成建議
        suggestions = self._generate_suggestions(hallucinations)
        
        # 更新統計
        self._update_stats(hallucinations)

        # 記錄歷史
        self._record_detections(hallucinations)
        
        return ValidationResult(
            is_valid=len([h for h in hallucinations if h.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]) == 0,
            overall_confidence=overall_confidence,
            hallucinations=hallucinations,
            warnings=warnings,
            suggestions=suggestions,
        )
    
    def _detect_security_flaws(self, code: str) -> list[HallucinationDetection]:
        """Detect security vulnerabilities (檢測安全漏洞).

        This helper scans for common vulnerability signatures, including
        plaintext credential handling, SQL injection patterns, and logging of
        secrets. Matches are converted into strongly typed detection objects so
        that callers can trace the precise pattern and suggested remediation.

        Args:
            code: Raw code text to be inspected.

        Returns:
            A list of security-focused :class:`HallucinationDetection` entries.
        """
        detections: list[HallucinationDetection] = []
        
        # 檢測明文密碼
        for pattern in SecurityPattern.PLAINTEXT_PASSWORD:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self._detection_count += 1
                detections.append(HallucinationDetection(
                    detection_id=f"SEC-{self._detection_count:06d}",
                    hallucination_type=HallucinationType.SECURITY_FLAW,
                    severity=SeverityLevel.CRITICAL,
                    description="Potential plaintext password storage detected (可能的明文密碼存儲)",
                    location=f"Line containing: {match.group()[:50]}...",
                    suggested_fix="Use bcrypt or argon2 for password hashing",
                    confidence=0.85,
                    metadata={"pattern": "PLAINTEXT_PASSWORD"},
                ))
        
        # 檢測 SQL 注入
        for pattern in SecurityPattern.SQL_INJECTION:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self._detection_count += 1
                detections.append(HallucinationDetection(
                    detection_id=f"SEC-{self._detection_count:06d}",
                    hallucination_type=HallucinationType.SECURITY_FLAW,
                    severity=SeverityLevel.CRITICAL,
                    description="Potential SQL injection vulnerability (可能的 SQL 注入漏洞)",
                    location=f"Line containing: {match.group()[:50]}...",
                    suggested_fix="Use parameterized queries or ORM",
                    confidence=0.80,
                    metadata={"pattern": "SQL_INJECTION"},
                ))
        
        # 檢測敏感數據暴露
        for pattern in SecurityPattern.SENSITIVE_DATA_EXPOSURE:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self._detection_count += 1
                detections.append(HallucinationDetection(
                    detection_id=f"SEC-{self._detection_count:06d}",
                    hallucination_type=HallucinationType.SECURITY_FLAW,
                    severity=SeverityLevel.HIGH,
                    description="Sensitive data may be exposed in logs (敏感數據可能在日誌中暴露)",
                    location=f"Line containing: {match.group()[:50]}...",
                    suggested_fix="Remove sensitive data from logs or use redaction",
                    confidence=0.75,
                    metadata={"pattern": "SENSITIVE_DATA_EXPOSURE"},
                ))
        
        return detections
    
    def _detect_logic_errors(self, code: str, language: str) -> list[HallucinationDetection]:
        """Detect logic errors (檢測邏輯錯誤).

        Looks for implementation smells that often slip past superficial
        reviews, such as empty catch blocks, potential infinite loops, and
        unused variable assignments. Python-specific heuristics are applied
        only when the ``language`` hint is set accordingly.

        Args:
            code: The candidate code to assess.
            language: Programming language context that gates some heuristics.

        Returns:
            A collection of logic-oriented detections with severity and fixes.
        """
        detections: list[HallucinationDetection] = []
        
        # 檢測空 catch 塊
        empty_catch_pattern = r'catch\s*\([^)]*\)\s*\{\s*\}'
        matches = re.finditer(empty_catch_pattern, code)
        for match in matches:
            self._detection_count += 1
            detections.append(HallucinationDetection(
                detection_id=f"LOG-{self._detection_count:06d}",
                hallucination_type=HallucinationType.LOGIC_ERROR,
                severity=SeverityLevel.MEDIUM,
                description="Empty catch block swallows errors (空的 catch 塊吞噬錯誤)",
                location=f"Line containing: {match.group()[:50]}...",
                suggested_fix="Log the error or handle it appropriately",
                confidence=0.90,
            ))
        
        # 檢測無限循環風險
        infinite_loop_patterns = [
            r'while\s*\(\s*true\s*\)\s*\{(?![^}]*break)',
            r'for\s*\(\s*;\s*;\s*\)\s*\{(?![^}]*break)',
        ]
        for pattern in infinite_loop_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                self._detection_count += 1
                detections.append(HallucinationDetection(
                    detection_id=f"LOG-{self._detection_count:06d}",
                    hallucination_type=HallucinationType.LOGIC_ERROR,
                    severity=SeverityLevel.HIGH,
                    description="Potential infinite loop without break condition (可能的無限循環)",
                    location=f"Line containing: {match.group()[:50]}...",
                    suggested_fix="Add a break condition or timeout",
                    confidence=0.70,
                ))
        
        # 檢測未使用的變量（簡化版）
        if language == "python":
            # 查找賦值但未使用的變量
            assignments = re.findall(r'^(\s*)(\w+)\s*=\s*.+$', code, re.MULTILINE)
            for _, var_name in assignments:
                # 排除常見的特殊變量
                if var_name.startswith('_') or var_name in ['self', 'cls']:
                    continue
                # 檢查變量是否在後續代碼中使用
                usage_pattern = rf'\b{re.escape(var_name)}\b'
                usages = re.findall(usage_pattern, code)
                if len(usages) == 1:  # 只有一次出現（賦值本身）
                    self._detection_count += 1
                    detections.append(HallucinationDetection(
                        detection_id=f"LOG-{self._detection_count:06d}",
                        hallucination_type=HallucinationType.LOGIC_ERROR,
                        severity=SeverityLevel.LOW,
                        description=f"Variable '{var_name}' may be unused (變量可能未使用)",
                        suggested_fix="Remove or use the variable",
                        confidence=0.60,
                    ))
        
        return detections
    
    def _detect_incomplete_implementation(self, code: str) -> list[HallucinationDetection]:
        """Detect incomplete implementations (檢測不完整實現).

        Flags placeholders that indicate unfinished work, including TODO/FIXME
        markers and deliberate ``NotImplementedError`` stubs. The resulting
        detections enable downstream tooling to block promotion of code that
        still contains scaffolding.

        Args:
            code: Source text that may include unfinished fragments.

        Returns:
            Detected incompleteness signals annotated with guidance.
        """
        detections: list[HallucinationDetection] = []
        
        # 檢測 TODO/FIXME 註釋
        todo_pattern = r'#\s*(TODO|FIXME|XXX|HACK)\s*:?\s*(.+)'
        matches = re.finditer(todo_pattern, code, re.IGNORECASE)
        for match in matches:
            self._detection_count += 1
            detections.append(HallucinationDetection(
                detection_id=f"INC-{self._detection_count:06d}",
                hallucination_type=HallucinationType.INCOMPLETE,
                severity=SeverityLevel.MEDIUM,
                description=f"Incomplete implementation: {match.group(2)[:50]}",
                location=f"Line containing: {match.group()[:50]}...",
                suggested_fix="Complete the implementation before deployment",
                confidence=0.95,
            ))
        
        # 檢測 pass 語句（可能是佔位符）
        pass_pattern = r'def\s+\w+\s*\([^)]*\)\s*:\s*\n\s*pass'
        matches = re.finditer(pass_pattern, code)
        for match in matches:
            self._detection_count += 1
            detections.append(HallucinationDetection(
                detection_id=f"INC-{self._detection_count:06d}",
                hallucination_type=HallucinationType.INCOMPLETE,
                severity=SeverityLevel.HIGH,
                description="Function with only 'pass' statement (僅有 pass 的函數)",
                location=f"Line containing: {match.group()[:50]}...",
                suggested_fix="Implement the function body",
                confidence=0.85,
            ))
        
        # 檢測 NotImplementedError
        not_impl_pattern = r'raise\s+NotImplementedError'
        matches = re.finditer(not_impl_pattern, code)
        for match in matches:
            self._detection_count += 1
            detections.append(HallucinationDetection(
                detection_id=f"INC-{self._detection_count:06d}",
                hallucination_type=HallucinationType.INCOMPLETE,
                severity=SeverityLevel.HIGH,
                description="NotImplementedError indicates incomplete code",
                location=f"Line containing: {match.group()[:50]}...",
                suggested_fix="Implement the required functionality",
                confidence=0.90,
            ))
        
        return detections
    
    def _detect_overconfidence(self, code: str) -> list[HallucinationDetection]:
        """Detect overconfident claims in comments (檢測過度自信的聲明).

        Searches for unverified assertions about security, completeness, or
        testing rigor. These markers often mask missing evidence and should be
        challenged before acceptance.

        Args:
            code: Code and associated comments to analyze.

        Returns:
            Detections indicating overconfident statements and suggested next
            steps to validate them.
        """
        detections: list[HallucinationDetection] = []
        
        # 過度自信的註釋模式
        overconfident_patterns = [
            (r'#\s*(This is|This code is)\s*(secure|safe|perfect|complete|optimal)', "Security/quality claim"),
            (r'#\s*(Fully|Completely)\s*(tested|validated|verified)', "Testing claim"),
            (r'#\s*(No\s+)?(bugs?|errors?|issues?)\s*(here|in this)', "Bug-free claim"),
            (r'✅.*完成.*安全', "Completion and security claim"),
        ]
        
        for pattern, claim_type in overconfident_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                self._detection_count += 1
                detections.append(HallucinationDetection(
                    detection_id=f"OVR-{self._detection_count:06d}",
                    hallucination_type=HallucinationType.OVERCONFIDENCE,
                    severity=SeverityLevel.MEDIUM,
                    description=f"Overconfident {claim_type} without verification (未經驗證的過度自信聲明)",
                    location=f"Line containing: {match.group()[:50]}...",
                    suggested_fix="Remove or verify the claim with tests",
                    confidence=0.80,
                ))
        
        return detections
    
    def _filter_false_positives(
        self,
        detections: list[HallucinationDetection],
        code: str
    ) -> list[HallucinationDetection]:
        """Filter out known false positives (過濾已知的誤報).

        Uses a content hash combined with the detection identifier to
        de-duplicate issues that the user has explicitly suppressed for the
        given code snapshot.

        Args:
            detections: Candidate detections to evaluate.
            code: The exact code string associated with the detections.

        Returns:
            A filtered list excluding detections previously marked as noise.
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return [
            d for d in detections 
            if f"{code_hash}:{d.detection_id}" not in self._false_positive_hashes
        ]
    
    def mark_false_positive(self, code: str, detection_id: str) -> None:
        """Mark a detection as false positive (標記為誤報).

        Persists a hash-based fingerprint so subsequent validation passes ignore
        the same detection on identical code, preventing repetitive alerts.

        Args:
            code: The code sample that produced the detection.
            detection_id: Identifier of the detection to silence.
        """
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        self._false_positive_hashes.add(f"{code_hash}:{detection_id}")
    
    def _calculate_confidence(self, detections: list[HallucinationDetection]) -> float:
        """Calculate overall confidence score (計算整體置信度).

        Applies weighted penalties based on severity to derive an aggregate
        confidence value between 0 and 1, where 1 represents no detected
        hallucinations.

        Args:
            detections: Detections generated for a single validation run.

        Returns:
            Normalized confidence score reflecting remaining risk.
        """
        if not detections:
            return 1.0
        
        # 根據檢測結果計算置信度
        severity_weights = {
            SeverityLevel.CRITICAL: 0.4,
            SeverityLevel.HIGH: 0.25,
            SeverityLevel.MEDIUM: 0.15,
            SeverityLevel.LOW: 0.08,
            SeverityLevel.INFO: 0.02,
        }
        
        total_penalty = sum(
            severity_weights.get(d.severity, 0.1) * d.confidence
            for d in detections
        )

        return max(0.0, 1.0 - min(total_penalty, 1.0))

    def _record_detections(self, detections: list[HallucinationDetection]) -> None:
        """Persist detections to history and lookup index (保存檢測紀錄與索引)."""

        self._detection_history.extend(detections)
        for detection in detections:
            self._detection_index[detection.detection_id] = detection
    
    def _generate_suggestions(self, detections: list[HallucinationDetection]) -> list[str]:
        """Generate improvement suggestions (生成改進建議).

        Aggregates detections by severity and type to create concise,
        prioritized remediation hints that can be shown to engineers or fed
        into automated workflows.

        Args:
            detections: Detections to summarize.

        Returns:
            Ordered list of human-readable suggestions.
        """
        suggestions = []
        
        # 按嚴重程度分組
        critical = [d for d in detections if d.severity == SeverityLevel.CRITICAL]
        high = [d for d in detections if d.severity == SeverityLevel.HIGH]
        
        if critical:
            suggestions.append(f"⚠️ {len(critical)} critical issues require immediate attention")
        if high:
            suggestions.append(f"🔴 {len(high)} high-priority issues should be addressed soon")
        
        # 按類型提供建議
        security_issues = [d for d in detections if d.hallucination_type == HallucinationType.SECURITY_FLAW]
        if security_issues:
            suggestions.append("🔒 Security review recommended before deployment")
        
        incomplete_issues = [d for d in detections if d.hallucination_type == HallucinationType.INCOMPLETE]
        if incomplete_issues:
            suggestions.append("📝 Complete all TODO items and placeholder implementations")
        
        return suggestions
    
    def _update_stats(self, detections: list[HallucinationDetection]) -> None:
        """Update detection statistics (更新檢測統計).

        Maintains aggregate counts across validations to support reporting and
        trend analysis without exposing mutable internal state to callers.

        Args:
            detections: New detections from the current validation pass.
        """
        self._stats["total_validations"] += 1
        self._stats["total_hallucinations"] += len(detections)

        for d in detections:
            type_key = d.hallucination_type.value
            self._stats["by_type"][type_key] = self._stats["by_type"].get(type_key, 0) + 1

            severity_key = d.severity.value
            self._stats["by_severity"][severity_key] = self._stats["by_severity"].get(severity_key, 0) + 1

            pattern_key = d.metadata.get("pattern") if isinstance(d.metadata, dict) else None
            if pattern_key:
                self._stats["by_pattern"][pattern_key] = self._stats["by_pattern"].get(pattern_key, 0) + 1
    
    def register_custom_validator(
        self, 
        validator: Callable[[str], list[HallucinationDetection]]
    ) -> None:
        """Register a custom validation function (註冊自定義驗證器).

        Custom validators allow domain teams to enforce additional rules (for
        example, framework conventions) while reusing the detector's lifecycle
        management and reporting pipeline.

        Args:
            validator: Callable returning detections for the provided code.
        """
        self._custom_validators.append(validator)
    
    def get_statistics(self) -> dict[str, Any]:
        """Get detection statistics (獲取檢測統計).

        Returns a shallow copy to prevent external mutation of the collector's
        internal counters.
        """
        return self._stats.copy()
    
    def get_detection_history(self) -> list[HallucinationDetection]:
        """Get detection history (獲取檢測歷史).

        Provides an immutable snapshot of all detections seen so far to support
        audit logging or user-visible history views.
        """
        return self._detection_history.copy()

    def ingest_feedback(
        self,
        code: str,
        detection_id: str,
        verdict: str,
        notes: Optional[str] = None,
    ) -> None:
        """Capture human feedback to evolve detector behavior (接收人類回饋並自動演化).

        This method enables a lightweight reinforcement loop:

        - ``false_positive`` verdicts silence the referenced detection for the
          provided code hash and increment a suppression counter.
        - ``true_positive`` verdicts are logged to help prioritize heuristics
          that commonly surface real issues.
        - ``improvement_applied`` verdicts note that remediation actions were
          taken, allowing downstream dashboards to track closure rates.

        Args:
            code: Exact code sample that produced the detection.
            detection_id: Identifier of the detection being reviewed.
            verdict: One of ``"false_positive"``, ``"true_positive"``, or
                ``"improvement_applied"``.
            notes: Optional analyst notes or remediation details.
        """
        timestamp = datetime.now().isoformat()
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        if verdict == "false_positive":
            self._false_positive_hashes.add(f"{code_hash}:{detection_id}")
            self._stats["false_positive_marks"] += 1

        detection = self._find_detection(detection_id)
        pattern_key = detection.metadata.get("pattern") if detection and isinstance(detection.metadata, dict) else None
        type_key = detection.hallucination_type.value if detection else None

        self._feedback_stats["total"] += 1
        self._feedback_stats["by_verdict"][verdict] = self._feedback_stats["by_verdict"].get(verdict, 0) + 1

        if pattern_key:
            bucket = self._feedback_stats["by_pattern"].setdefault(pattern_key, {"false_positive": 0, "true_positive": 0, "improvement_applied": 0})
            if verdict in bucket:
                bucket[verdict] += 1

        if type_key:
            bucket = self._feedback_stats["by_type"].setdefault(type_key, {"false_positive": 0, "true_positive": 0, "improvement_applied": 0})
            if verdict in bucket:
                bucket[verdict] += 1

        self._feedback_log.append(
            {
                "code_hash": code_hash,
                "detection_id": detection_id,
                "verdict": verdict,
                "notes": notes,
                "timestamp": timestamp,
            }
        )

    def get_feedback_log(self) -> list[dict[str, Any]]:
        """Return accumulated feedback entries (回傳累積回饋記錄)."""
        return self._feedback_log.copy()

    def get_feedback_summary(self) -> dict[str, Any]:
        """Aggregate feedback signals for dashboards (彙總回饋訊號供看板使用)."""

        return {
            "total": self._feedback_stats.get("total", 0),
            "by_verdict": self._feedback_stats.get("by_verdict", {}).copy(),
            "by_pattern": {k: v.copy() for k, v in self._feedback_stats.get("by_pattern", {}).items()},
            "by_type": {k: v.copy() for k, v in self._feedback_stats.get("by_type", {}).items()},
        }

    def get_adaptive_recommendations(self, min_occurrences: int = 3) -> list[str]:
        """Suggest evolutions to detection rules (建議自動演化方向).

        Reviews aggregated statistics and human feedback to highlight areas
        where heuristics should be strengthened or relaxed.

        Args:
            min_occurrences: Minimum pattern count to be considered "trending".

        Returns:
            A list of human-readable recommendations suitable for backlog items
            or rule updates.
        """
        recommendations: list[str] = []

        for pattern, count in self._stats.get("by_pattern", {}).items():
            if count >= min_occurrences:
                recommendations.append(
                    f"Pattern '{pattern}' triggered {count} times; consider a dedicated rule or test."
                )

        for pattern, feedback in self._feedback_stats.get("by_pattern", {}).items():
            false_pos = feedback.get("false_positive", 0)
            true_pos = feedback.get("true_positive", 0)
            improvements = feedback.get("improvement_applied", 0)

            if false_pos >= min_occurrences and false_pos > true_pos:
                recommendations.append(
                    f"Pattern '{pattern}' draws frequent false positives ({false_pos}); relax regex or downgrade severity."
                )
            if true_pos >= min_occurrences and true_pos > false_pos:
                recommendations.append(
                    f"Pattern '{pattern}' confirmed {true_pos} times; strengthen detection with tests or linters."
                )
            if improvements > 0:
                recommendations.append(
                    f"Pattern '{pattern}' prompted {improvements} remediations; add regression checks to prevent recurrence."
                )

        for type_key, feedback in self._feedback_stats.get("by_type", {}).items():
            if feedback.get("false_positive", 0) >= min_occurrences and feedback.get("false_positive", 0) > feedback.get("true_positive", 0):
                recommendations.append(
                    f"Hallucination type '{type_key}' has elevated false positives; recalibrate detection thresholds."
                )
            if feedback.get("true_positive", 0) >= min_occurrences and feedback.get("true_positive", 0) > feedback.get("false_positive", 0):
                recommendations.append(
                    f"Hallucination type '{type_key}' consistently surfaces real issues; prioritize rule hardening."
                )

        if self._stats.get("false_positive_marks", 0) >= min_occurrences:
            recommendations.append(
                "High false-positive volume detected; review regexes or lower severities for noisy rules."
            )

        if not recommendations:
            recommendations.append("No adaptive actions required; keep monitoring usage signals.")

        return recommendations

    def _find_detection(self, detection_id: str) -> Optional[HallucinationDetection]:
        """Retrieve a detection by id from history (從歷史中查找檢測記錄)."""

        return self._detection_index.get(detection_id)
