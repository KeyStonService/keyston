"""
CI Error Analyzer

Parse and analyze CI/CD error logs to identify error types, severity,
and provide structured error information for issue creation and auto-fix.

Reference: AI-driven GitHub Action auto-suggest fixes [3]
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ErrorCategory(Enum):
    """Categories of CI/CD errors"""
    BUILD_ERROR = "build_error"
    TEST_FAILURE = "test_failure"
    LINT_ERROR = "lint_error"
    TYPE_ERROR = "type_error"
    DEPENDENCY_ERROR = "dependency_error"
    SECURITY_SCAN = "security_scan"
    DEPLOYMENT_ERROR = "deployment_error"
    TIMEOUT = "timeout"
    RESOURCE_LIMIT = "resource_limit"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for CI errors"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorPattern:
    """Pattern for matching specific error types"""
    pattern_id: str
    category: ErrorCategory
    regex: str
    severity: ErrorSeverity
    description: str
    auto_fixable: bool = False
    fix_hint: str | None = None

    def matches(self, log_content: str) -> bool:
        """Check if this pattern matches the log content"""
        return bool(re.search(self.regex, log_content, re.MULTILINE | re.IGNORECASE))

    def extract_details(self, log_content: str) -> dict[str, Any]:
        """Extract error details from log content"""
        match = re.search(self.regex, log_content, re.MULTILINE | re.IGNORECASE)
        if match:
            return {
                'matched_text': match.group(0),
                'groups': match.groups(),
                'start': match.start(),
                'end': match.end(),
            }
        return {}


@dataclass
class CIError:
    """Represents a parsed CI/CD error"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    message: str
    file_path: str | None = None
    line_number: int | None = None
    column_number: int | None = None
    code_snippet: str | None = None
    stack_trace: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    auto_fixable: bool = False
    fix_suggestion: str | None = None
    raw_log: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'error_id': self.error_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'column_number': self.column_number,
            'code_snippet': self.code_snippet,
            'stack_trace': self.stack_trace,
            'timestamp': self.timestamp.isoformat(),
            'auto_fixable': self.auto_fixable,
            'fix_suggestion': self.fix_suggestion,
            'metadata': self.metadata,
        }


class CIErrorAnalyzer:
    """
    CI Error Analyzer
    
    Parse and analyze CI/CD error logs to identify error types, severity,
    and provide structured error information.
    
    Features:
    - Multi-format log parsing (GitHub Actions, Jenkins, etc.)
    - Pattern-based error detection
    - AI-powered error analysis
    - Auto-fix capability detection
    """

    # Default error patterns
    DEFAULT_PATTERNS = [
        # Build Errors
        ErrorPattern(
            pattern_id="npm_build_error",
            category=ErrorCategory.BUILD_ERROR,
            regex=r"npm ERR!.*(?:build|compile).*failed",
            severity=ErrorSeverity.HIGH,
            description="NPM build failed",
            auto_fixable=False,
        ),
        ErrorPattern(
            pattern_id="typescript_compile_error",
            category=ErrorCategory.TYPE_ERROR,
            regex=r"error TS\d+:.*",
            severity=ErrorSeverity.HIGH,
            description="TypeScript compilation error",
            auto_fixable=False,
            fix_hint="Check type definitions and imports",
        ),
        ErrorPattern(
            pattern_id="python_syntax_error",
            category=ErrorCategory.BUILD_ERROR,
            regex=r"SyntaxError:.*",
            severity=ErrorSeverity.HIGH,
            description="Python syntax error",
            auto_fixable=False,
        ),

        # Test Failures
        ErrorPattern(
            pattern_id="jest_test_failure",
            category=ErrorCategory.TEST_FAILURE,
            regex=r"FAIL.*\.test\.(js|ts|jsx|tsx)",
            severity=ErrorSeverity.MEDIUM,
            description="Jest test failure",
            auto_fixable=False,
        ),
        ErrorPattern(
            pattern_id="pytest_failure",
            category=ErrorCategory.TEST_FAILURE,
            regex=r"FAILED.*test_.*\.py",
            severity=ErrorSeverity.MEDIUM,
            description="Pytest failure",
            auto_fixable=False,
        ),

        # Lint Errors
        ErrorPattern(
            pattern_id="eslint_error",
            category=ErrorCategory.LINT_ERROR,
            regex=r"\d+:\d+\s+error\s+.*eslint",
            severity=ErrorSeverity.LOW,
            description="ESLint error",
            auto_fixable=True,
            fix_hint="Run 'npm run lint -- --fix'",
        ),
        ErrorPattern(
            pattern_id="prettier_error",
            category=ErrorCategory.LINT_ERROR,
            regex=r"Prettier.*(?:error|failed)",
            severity=ErrorSeverity.LOW,
            description="Prettier formatting error",
            auto_fixable=True,
            fix_hint="Run 'npm run format'",
        ),
        ErrorPattern(
            pattern_id="flake8_error",
            category=ErrorCategory.LINT_ERROR,
            regex=r".*\.py:\d+:\d+:.*[EWFC]\d+",
            severity=ErrorSeverity.LOW,
            description="Flake8 lint error",
            auto_fixable=True,
            fix_hint="Run 'black' or 'autopep8'",
        ),

        # Dependency Errors
        ErrorPattern(
            pattern_id="npm_dependency_error",
            category=ErrorCategory.DEPENDENCY_ERROR,
            regex=r"npm ERR!.*(?:peer dep|dependency|ERESOLVE)",
            severity=ErrorSeverity.MEDIUM,
            description="NPM dependency resolution error",
            auto_fixable=True,
            fix_hint="Run 'npm install --legacy-peer-deps'",
        ),
        ErrorPattern(
            pattern_id="pip_dependency_error",
            category=ErrorCategory.DEPENDENCY_ERROR,
            regex=r"(?:pip|ERROR).*(?:Could not find|No matching distribution)",
            severity=ErrorSeverity.MEDIUM,
            description="Python dependency error",
            auto_fixable=False,
        ),

        # Security Scan Errors
        ErrorPattern(
            pattern_id="npm_audit_vulnerability",
            category=ErrorCategory.SECURITY_SCAN,
            regex=r"npm audit.*(?:high|critical)",
            severity=ErrorSeverity.HIGH,
            description="NPM security vulnerability",
            auto_fixable=True,
            fix_hint="Run 'npm audit fix'",
        ),
        ErrorPattern(
            pattern_id="codeql_alert",
            category=ErrorCategory.SECURITY_SCAN,
            regex=r"CodeQL.*(?:alert|vulnerability|warning)",
            severity=ErrorSeverity.HIGH,
            description="CodeQL security alert",
            auto_fixable=False,
        ),

        # Deployment Errors
        ErrorPattern(
            pattern_id="docker_build_error",
            category=ErrorCategory.DEPLOYMENT_ERROR,
            regex=r"docker.*(?:build|push).*(?:error|failed)",
            severity=ErrorSeverity.HIGH,
            description="Docker build/push error",
            auto_fixable=False,
        ),
        ErrorPattern(
            pattern_id="k8s_deployment_error",
            category=ErrorCategory.DEPLOYMENT_ERROR,
            regex=r"kubectl.*(?:error|failed|Error from server)",
            severity=ErrorSeverity.CRITICAL,
            description="Kubernetes deployment error",
            auto_fixable=False,
        ),

        # Timeout Errors
        ErrorPattern(
            pattern_id="job_timeout",
            category=ErrorCategory.TIMEOUT,
            regex=r"(?:job|step|action).*(?:timed out|timeout|exceeded)",
            severity=ErrorSeverity.MEDIUM,
            description="Job timeout",
            auto_fixable=False,
        ),

        # Permission Errors
        ErrorPattern(
            pattern_id="permission_denied",
            category=ErrorCategory.PERMISSION_ERROR,
            regex=r"(?:permission denied|EACCES|403 Forbidden)",
            severity=ErrorSeverity.HIGH,
            description="Permission denied error",
            auto_fixable=False,
        ),
    ]

    def __init__(self, custom_patterns: list[ErrorPattern] | None = None):
        """
        Initialize the CI Error Analyzer
        
        Args:
            custom_patterns: Additional custom error patterns
        """
        self.patterns = self.DEFAULT_PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        self._error_counter = 0

    def _generate_error_id(self) -> str:
        """Generate a unique error ID"""
        self._error_counter += 1
        return f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._error_counter:04d}"

    def analyze_log(self, log_content: str, source: str = "unknown") -> list[CIError]:
        """
        Analyze CI/CD log content and extract errors
        
        Args:
            log_content: Raw log content
            source: Source of the log (e.g., "github_actions", "jenkins")
            
        Returns:
            List of parsed CI errors
        """
        errors = []

        for pattern in self.patterns:
            if pattern.matches(log_content):
                details = pattern.extract_details(log_content)

                # Extract file path and line number if available
                file_info = self._extract_file_info(log_content, pattern.category)

                error = CIError(
                    error_id=self._generate_error_id(),
                    category=pattern.category,
                    severity=pattern.severity,
                    title=pattern.description,
                    message=details.get('matched_text', 'Error detected'),
                    file_path=file_info.get('file_path'),
                    line_number=file_info.get('line_number'),
                    column_number=file_info.get('column_number'),
                    code_snippet=self._extract_code_snippet(log_content, file_info),
                    stack_trace=self._extract_stack_trace(log_content),
                    auto_fixable=pattern.auto_fixable,
                    fix_suggestion=pattern.fix_hint,
                    raw_log=log_content[:5000],  # Limit raw log size
                    metadata={
                        'source': source,
                        'pattern_id': pattern.pattern_id,
                    }
                )
                errors.append(error)

        # If no patterns matched, create an unknown error
        if not errors and self._looks_like_error(log_content):
            errors.append(CIError(
                error_id=self._generate_error_id(),
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                title="Unknown CI Error",
                message=self._extract_error_summary(log_content),
                raw_log=log_content[:5000],
                metadata={'source': source}
            ))

        return errors

    def _extract_file_info(self, log_content: str, category: ErrorCategory) -> dict[str, Any]:
        """Extract file path and line number from log content"""
        # Common patterns for file:line:column format
        patterns = [
            r'([^\s:]+\.(?:js|ts|jsx|tsx|py|java|go|rs|rb)):(\d+):(\d+)',
            r'([^\s:]+\.(?:js|ts|jsx|tsx|py|java|go|rs|rb)):(\d+)',
            r'File "([^"]+)", line (\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, log_content)
            if match:
                groups = match.groups()
                result = {'file_path': groups[0]}
                if len(groups) > 1:
                    result['line_number'] = int(groups[1])
                if len(groups) > 2:
                    result['column_number'] = int(groups[2])
                return result

        return {}

    def _extract_code_snippet(self, log_content: str, file_info: dict[str, Any]) -> str | None:
        """Extract code snippet from log content if available"""
        # Look for code snippet markers
        snippet_patterns = [
            r'>\s*\d+\s*\|.*\n.*\n.*',  # Typical error format with line markers
            r'```[\s\S]*?```',  # Markdown code blocks
        ]

        for pattern in snippet_patterns:
            match = re.search(pattern, log_content)
            if match:
                return match.group(0)[:500]  # Limit snippet size

        return None

    def _extract_stack_trace(self, log_content: str) -> str | None:
        """Extract stack trace from log content"""
        # Look for stack trace patterns
        stack_patterns = [
            r'(at\s+.*\(.*:\d+:\d+\)[\s\S]*){3,}',  # JavaScript stack
            r'(File ".*", line \d+[\s\S]*){3,}',  # Python traceback
            r'(^\s+at\s+.*$[\s\S]*){3,}',  # Java/Go stack
        ]

        for pattern in stack_patterns:
            match = re.search(pattern, log_content, re.MULTILINE)
            if match:
                return match.group(0)[:2000]  # Limit stack trace size

        return None

    def _looks_like_error(self, log_content: str) -> bool:
        """Check if log content looks like it contains errors"""
        error_indicators = [
            r'\berror\b',
            r'\bfail(?:ed|ure)?\b',
            r'\bexception\b',
            r'\bcrash(?:ed)?\b',
            r'exit code [1-9]',
            r'Process completed with exit code [1-9]',
        ]

        for indicator in error_indicators:
            if re.search(indicator, log_content, re.IGNORECASE):
                return True

        return False

    def _extract_error_summary(self, log_content: str) -> str:
        """Extract a summary of the error from log content"""
        # Look for common error message patterns
        error_line_patterns = [
            r'^.*error.*$',
            r'^.*failed.*$',
            r'^.*exception.*$',
        ]

        for pattern in error_line_patterns:
            match = re.search(pattern, log_content, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(0)[:500]

        # Return first non-empty line as fallback
        lines = [line.strip() for line in log_content.split('\n') if line.strip()]
        return lines[0][:500] if lines else "Unknown error"

    def add_pattern(self, pattern: ErrorPattern) -> None:
        """Add a custom error pattern"""
        self.patterns.append(pattern)

    def get_patterns_for_category(self, category: ErrorCategory) -> list[ErrorPattern]:
        """Get all patterns for a specific category"""
        return [p for p in self.patterns if p.category == category]

    def get_auto_fixable_errors(self, errors: list[CIError]) -> list[CIError]:
        """Filter errors that can be automatically fixed"""
        return [e for e in errors if e.auto_fixable]

    def summarize_errors(self, errors: list[CIError]) -> dict[str, Any]:
        """Generate a summary of analyzed errors"""
        if not errors:
            return {'total': 0, 'by_category': {}, 'by_severity': {}}

        summary = {
            'total': len(errors),
            'by_category': {},
            'by_severity': {},
            'auto_fixable_count': len(self.get_auto_fixable_errors(errors)),
            'files_affected': list({e.file_path for e in errors if e.file_path}),
        }

        for error in errors:
            cat = error.category.value
            sev = error.severity.value
            summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1
            summary['by_severity'][sev] = summary['by_severity'].get(sev, 0) + 1

        return summary
