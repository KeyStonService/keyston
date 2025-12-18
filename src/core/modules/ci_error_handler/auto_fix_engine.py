"""
Auto Fix Engine

Generate and apply AI-driven fixes for CI/CD errors.
Supports safe auto-fix for known patterns and AI-powered suggestions.

Reference: Using Codex to auto-fix CI failures [10]
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .ci_error_analyzer import CIError, ErrorCategory


class FixStrategy(Enum):
    """Strategy for fixing CI errors"""
    AUTO_FIX = "auto_fix"           # Automatically apply fix
    SUGGEST_FIX = "suggest_fix"     # Suggest fix via PR comment
    CREATE_PR = "create_pr"         # Create PR with fix
    MANUAL = "manual"               # Requires manual intervention
    AI_ASSISTED = "ai_assisted"     # AI generates fix suggestion


@dataclass
class FixAttempt:
    """Record of a fix attempt"""
    attempt_id: str
    error_id: str
    strategy: FixStrategy
    fix_description: str
    fix_code: str | None = None
    files_modified: list[str] = field(default_factory=list)
    pr_number: int | None = None
    pr_url: str | None = None
    success: bool = False
    error_message: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'attempt_id': self.attempt_id,
            'error_id': self.error_id,
            'strategy': self.strategy.value,
            'fix_description': self.fix_description,
            'fix_code': self.fix_code,
            'files_modified': self.files_modified,
            'pr_number': self.pr_number,
            'pr_url': self.pr_url,
            'success': self.success,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class FixResult:
    """Result of a fix operation"""
    success: bool
    message: str
    strategy_used: FixStrategy
    attempt: FixAttempt | None = None
    suggested_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'strategy_used': self.strategy_used.value,
            'attempt': self.attempt.to_dict() if self.attempt else None,
            'suggested_actions': self.suggested_actions,
        }


@dataclass
class FixRule:
    """Rule for automatic fixing"""
    rule_id: str
    category: ErrorCategory
    pattern: str  # Regex pattern to match
    fix_command: str  # Command to run for fix
    fix_description: str
    safe_to_auto_apply: bool = False
    prerequisites: list[str] = field(default_factory=list)

    def matches(self, error: CIError) -> bool:
        """Check if this rule matches the error"""
        if error.category != self.category:
            return False
        return bool(re.search(self.pattern, error.message, re.IGNORECASE))


class AutoFixEngine:
    """
    Auto Fix Engine
    
    Generate and apply fixes for CI/CD errors.
    
    Features:
    - Rule-based auto-fix for known patterns
    - AI-powered fix suggestions
    - Safe execution with rollback
    - PR creation for suggested fixes
    """

    # Default fix rules
    DEFAULT_FIX_RULES = [
        # Lint Fixes
        FixRule(
            rule_id="eslint_auto_fix",
            category=ErrorCategory.LINT_ERROR,
            pattern=r"eslint|ESLint",
            fix_command="npm run lint -- --fix",
            fix_description="Auto-fix ESLint errors",
            safe_to_auto_apply=True,
            prerequisites=["node", "npm"],
        ),
        FixRule(
            rule_id="prettier_fix",
            category=ErrorCategory.LINT_ERROR,
            pattern=r"prettier|Prettier",
            fix_command="npx prettier --write .",
            fix_description="Auto-fix Prettier formatting",
            safe_to_auto_apply=True,
            prerequisites=["node", "npm"],
        ),
        FixRule(
            rule_id="black_fix",
            category=ErrorCategory.LINT_ERROR,
            pattern=r"black|Black",
            fix_command="black .",
            fix_description="Auto-fix with Black formatter",
            safe_to_auto_apply=True,
            prerequisites=["python", "black"],
        ),
        FixRule(
            rule_id="flake8_autopep8",
            category=ErrorCategory.LINT_ERROR,
            pattern=r"flake8|E\d{3}|W\d{3}",
            fix_command="autopep8 --in-place --recursive .",
            fix_description="Auto-fix with autopep8",
            safe_to_auto_apply=True,
            prerequisites=["python", "autopep8"],
        ),

        # Dependency Fixes
        FixRule(
            rule_id="npm_audit_fix",
            category=ErrorCategory.SECURITY_SCAN,
            pattern=r"npm audit|vulnerability|vulnerabilities",
            fix_command="npm audit fix",
            fix_description="Fix npm security vulnerabilities",
            safe_to_auto_apply=True,
            prerequisites=["node", "npm"],
        ),
        FixRule(
            rule_id="npm_legacy_peer_deps",
            category=ErrorCategory.DEPENDENCY_ERROR,
            pattern=r"ERESOLVE|peer dep|peer dependency",
            fix_command="npm install --legacy-peer-deps",
            fix_description="Install with legacy peer deps",
            safe_to_auto_apply=False,  # May have side effects
            prerequisites=["node", "npm"],
        ),
        FixRule(
            rule_id="pip_upgrade",
            category=ErrorCategory.DEPENDENCY_ERROR,
            pattern=r"pip.*upgrade|outdated",
            fix_command="pip install --upgrade -r requirements.txt",
            fix_description="Upgrade Python dependencies",
            safe_to_auto_apply=False,
            prerequisites=["python", "pip"],
        ),
    ]

    # AI fix prompt templates
    AI_FIX_PROMPTS = {
        ErrorCategory.BUILD_ERROR: """
Analyze this build error and suggest a fix:

Error: {message}
File: {file_path}
Line: {line_number}

Code snippet:
```
{code_snippet}
```

Provide:
1. Root cause analysis
2. Suggested fix (code if applicable)
3. Prevention tips
""",
        ErrorCategory.TEST_FAILURE: """
Analyze this test failure and suggest a fix:

Error: {message}
Test file: {file_path}

Stack trace:
```
{stack_trace}
```

Provide:
1. What the test is checking
2. Why it's failing
3. How to fix it
""",
        ErrorCategory.TYPE_ERROR: """
Analyze this type error and suggest a fix:

Error: {message}
File: {file_path}:{line_number}

Code:
```
{code_snippet}
```

Provide:
1. Type mismatch explanation
2. Corrected code
3. Related type definitions to update
""",
    }

    def __init__(self, custom_rules: list[FixRule] | None = None):
        """
        Initialize the Auto Fix Engine
        
        Args:
            custom_rules: Additional custom fix rules
        """
        self.rules = self.DEFAULT_FIX_RULES.copy()
        if custom_rules:
            self.rules.extend(custom_rules)
        self._attempt_counter = 0
        self._attempts: dict[str, FixAttempt] = {}

    def _generate_attempt_id(self) -> str:
        """Generate unique attempt ID"""
        self._attempt_counter += 1
        return f"FIX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._attempt_counter:04d}"

    def analyze_fix_options(self, error: CIError) -> dict[str, Any]:
        """
        Analyze available fix options for an error
        
        Args:
            error: The CI error to fix
            
        Returns:
            Dictionary with fix options and recommendations
        """
        options = {
            'error_id': error.error_id,
            'category': error.category.value,
            'auto_fixable': error.auto_fixable,
            'matching_rules': [],
            'recommended_strategy': FixStrategy.MANUAL,
            'ai_assist_available': error.category in self.AI_FIX_PROMPTS,
        }

        # Find matching rules
        for rule in self.rules:
            if rule.matches(error):
                options['matching_rules'].append({
                    'rule_id': rule.rule_id,
                    'fix_command': rule.fix_command,
                    'description': rule.fix_description,
                    'safe_to_auto_apply': rule.safe_to_auto_apply,
                })

        # Determine recommended strategy
        if options['matching_rules']:
            safe_rules = [r for r in options['matching_rules'] if r['safe_to_auto_apply']]
            if safe_rules:
                options['recommended_strategy'] = FixStrategy.AUTO_FIX
            else:
                options['recommended_strategy'] = FixStrategy.CREATE_PR
        elif options['ai_assist_available']:
            options['recommended_strategy'] = FixStrategy.AI_ASSISTED
        else:
            options['recommended_strategy'] = FixStrategy.MANUAL

        return options

    def generate_fix_suggestion(self, error: CIError) -> FixResult:
        """
        Generate a fix suggestion for an error
        
        Args:
            error: The CI error to fix
            
        Returns:
            FixResult with suggestion
        """
        options = self.analyze_fix_options(error)

        if options['matching_rules']:
            # Use rule-based fix
            rule = options['matching_rules'][0]
            return FixResult(
                success=True,
                message=f"Fix available: {rule['description']}",
                strategy_used=FixStrategy.SUGGEST_FIX,
                suggested_actions=[
                    f"Run: `{rule['fix_command']}`",
                    "Commit the changes",
                    "Re-run CI pipeline",
                ],
            )

        if options['ai_assist_available']:
            # Generate AI fix prompt
            self._generate_ai_prompt(error)
            return FixResult(
                success=True,
                message="AI assistance available for this error",
                strategy_used=FixStrategy.AI_ASSISTED,
                suggested_actions=[
                    "Review the AI analysis below",
                    "Apply suggested changes",
                    "Test locally before committing",
                ],
            )

        return FixResult(
            success=False,
            message="No automatic fix available",
            strategy_used=FixStrategy.MANUAL,
            suggested_actions=[
                "Review the error message carefully",
                "Check related documentation",
                "Consult team if needed",
            ],
        )

    def _generate_ai_prompt(self, error: CIError) -> str:
        """Generate AI prompt for error analysis"""
        template = self.AI_FIX_PROMPTS.get(
            error.category,
            "Analyze this error and suggest a fix:\n\n{message}"
        )

        return template.format(
            message=error.message,
            file_path=error.file_path or "Unknown",
            line_number=error.line_number or "Unknown",
            code_snippet=error.code_snippet or "Not available",
            stack_trace=error.stack_trace or "Not available",
        )

    def create_fix_attempt(
        self,
        error: CIError,
        strategy: FixStrategy,
        fix_description: str,
        fix_code: str | None = None,
        files_modified: list[str] | None = None
    ) -> FixAttempt:
        """
        Create and record a fix attempt
        
        Args:
            error: The CI error being fixed
            strategy: Strategy being used
            fix_description: Description of the fix
            fix_code: Code for the fix (if applicable)
            files_modified: List of files modified
            
        Returns:
            The created FixAttempt
        """
        attempt = FixAttempt(
            attempt_id=self._generate_attempt_id(),
            error_id=error.error_id,
            strategy=strategy,
            fix_description=fix_description,
            fix_code=fix_code,
            files_modified=files_modified or [],
        )

        self._attempts[attempt.attempt_id] = attempt
        return attempt

    def record_attempt_result(
        self,
        attempt_id: str,
        success: bool,
        pr_number: int | None = None,
        pr_url: str | None = None,
        error_message: str | None = None
    ) -> FixAttempt | None:
        """
        Record the result of a fix attempt
        
        Args:
            attempt_id: ID of the attempt
            success: Whether the fix was successful
            pr_number: PR number if one was created
            pr_url: PR URL if one was created
            error_message: Error message if fix failed
            
        Returns:
            Updated FixAttempt or None if not found
        """
        if attempt_id not in self._attempts:
            return None

        attempt = self._attempts[attempt_id]
        attempt.success = success
        attempt.pr_number = pr_number
        attempt.pr_url = pr_url
        attempt.error_message = error_message

        return attempt

    def get_attempt(self, attempt_id: str) -> FixAttempt | None:
        """Get a fix attempt by ID"""
        return self._attempts.get(attempt_id)

    def get_attempts_for_error(self, error_id: str) -> list[FixAttempt]:
        """Get all fix attempts for an error"""
        return [a for a in self._attempts.values() if a.error_id == error_id]

    def generate_fix_pr_content(
        self,
        error: CIError,
        fix_description: str,
        fix_code: str
    ) -> dict[str, Any]:
        """
        Generate content for a fix PR
        
        Args:
            error: The CI error being fixed
            fix_description: Description of the fix
            fix_code: The fix code
            
        Returns:
            Dictionary with PR title, body, and branch name
        """
        branch_name = f"fix/ci-{error.error_id.lower()}"

        title = f"fix: {error.title}"
        if error.file_path:
            title += f" in {error.file_path}"

        body = f"""## 🔧 Automated CI Fix

This PR was automatically generated to fix a CI error.

### Error Information

| Field | Value |
|-------|-------|
| **Error ID** | `{error.error_id}` |
| **Category** | {error.category.value} |
| **Severity** | {error.severity.value} |
| **File** | `{error.file_path or 'N/A'}` |

### Error Message

```
{error.message[:500]}
```

### Fix Description

{fix_description}

### Changes Made

```diff
{fix_code}
```

---

**⚠️ Please review this change carefully before merging.**

*Generated by SynergyMesh Auto Fix Engine*
"""

        return {
            'branch_name': branch_name,
            'title': title[:256],
            'body': body,
            'labels': ['automated-fix', 'ci-error'],
        }

    def add_rule(self, rule: FixRule) -> None:
        """Add a custom fix rule"""
        self.rules.append(rule)

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about fix attempts"""
        total = len(self._attempts)
        if total == 0:
            return {'total': 0}

        successful = sum(1 for a in self._attempts.values() if a.success)
        by_strategy = {}

        for attempt in self._attempts.values():
            strategy = attempt.strategy.value
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1

        return {
            'total': total,
            'successful': successful,
            'success_rate': successful / total if total > 0 else 0,
            'by_strategy': by_strategy,
        }
