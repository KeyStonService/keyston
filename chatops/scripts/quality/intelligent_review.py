#!/usr/bin/env python3
# scripts/quality/intelligent_review.py
# Phase-3: Intelligent Code Review System
# for Multi-Agent AI Production Environment
"""
Intelligent Code Reviewer for chatops multi-agent AI infrastructure.
Scans: services/engine-python/, services/gateway-ts/,
       scripts/, tests/
Excludes: artifacts/, var/, deployments/, policies/,
          .git/, node_modules/, __pycache__/, .venv/
"""
import ast
import re
import json
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class CodeIssue:
    """Represents a code quality issue found during review."""
    file: str
    line: int
    column: int
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'security', 'performance',
    # 'maintainability', 'style', 'system'
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ReviewReport:
    """Complete review report with summary and issues."""
    summary: Dict
    issues: List[Dict]
    recommendations: List[str]
    metadata: Dict = field(default_factory=dict)


class IntelligentCodeReviewer:
    """
    Multi-Agent AI Code Review System.

    Responsibilities:
    - Security scanning (Security Agent data source)
    - Code quality assessment (CI Agent data source)
    - Maintainability analysis
    - Style checking
    """

    def __init__(self):
        self.rules = self._load_review_rules()
        self.complexity_threshold = 10
        self.line_length_limit = 120

    def _load_review_rules(self) -> Dict:
        """Load code review rules by category."""
        return {
            'security': [
                {
                    'pattern': r'eval\(',
                    'message': 'Avoid using eval(), may lead to code injection',
                    'severity': 'error'
                },
                {
                    'pattern': r'exec\(',
                    'message': 'Avoid using exec(), may lead to code injection',
                    'severity': 'error'
                },
                {
                    'pattern': r'subprocess\.call\([^)]*shell=True',
                    'message': 'Avoid shell=True in subprocess, may lead to command injection',
                    'severity': 'error'
                },
                {
                    'pattern': r'os\.system\(',
                    'message': 'Avoid os.system(), prefer subprocess with shell=False',
                    'severity': 'warning'
                },
                {
                    'pattern': r'pickle\.loads?\(',
                    'message': 'Unsafe deserialization with pickle, consider using json',
                    'severity': 'warning'
                },
                {
                    'pattern': r'password\s*=\s*["\'][^"\']+["\']',
                    'message': 'Hardcoded password detected',
                    'severity': 'error'
                },
                {
                    'pattern': r'api_key\s*=\s*["\'][^"\']+["\']',
                    'message': 'Hardcoded API key detected',
                    'severity': 'error'
                },
            ],
            'performance': [
                {
                    'pattern': r'for.*in.*range\(len\(',
                    'message': 'Use enumerate() instead of range(len())',
                    'severity': 'info'
                },
                {
                    'pattern': r'list\(filter\(lambda',
                    'message': 'Use list comprehension instead of filter + lambda',
                    'severity': 'info'
                },
                {
                    'pattern': r'\+ *=.*in.*for',
                    'message': 'Consider using list comprehension or join() for string concatenation in loop',
                    'severity': 'info'
                },
            ],
            'maintainability': [
                {
                    'pattern': r'TODO|FIXME|HACK|XXX',
                    'message': 'Technical debt marker found',
                    'severity': 'info'
                },
                {
                    'pattern': r'print\(',
                    'message': 'Use logging module instead of print()',
                    'severity': 'info'
                },
                {
                    'pattern': r'except\s*:',
                    'message': 'Avoid bare except, catch specific exceptions',
                    'severity': 'warning'
                },
                {
                    'pattern': r'except Exception\s*:',
                    'message': 'Consider catching more specific exceptions',
                    'severity': 'info'
                },
            ],
            'style': [
                {
                    'pattern': r'\t',
                    'message': 'Use spaces instead of tabs for indentation',
                    'severity': 'info'
                },
                {
                    'pattern': r'\s+$',
                    'message': 'Trailing whitespace detected',
                    'severity': 'info',
                    'auto_fixable': True
                },
            ],
        }

    def review_file(self, file_path: str) -> List[CodeIssue]:
        """
        Review a single file for code quality issues.

        Args:
            file_path: Path to the file to review

        Returns:
            List of CodeIssue objects found in the file
        """
        issues: List[CodeIssue] = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            if file_path.endswith('.py'):
                issues.extend(self._analyze_python_file(file_path, content, lines))
            elif file_path.endswith(('.js', '.ts', '.tsx')):
                issues.extend(self._analyze_js_file(file_path, content, lines))

            issues.extend(self._check_common_issues(file_path, lines))

        except Exception as e:
            issues.append(CodeIssue(
                file=file_path,
                line=0,
                column=0,
                severity='error',
                category='system',
                message=f'File analysis failed: {str(e)}'
            ))

        return issues

    def _analyze_python_file(self, file_path: str, content: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze Python file for issues."""
        issues: List[CodeIssue] = []

        # Rule-based scanning (regex)
        for category, rules in self.rules.items():
            for rule in rules:
                for idx, line in enumerate(lines, start=1):
                    if re.search(rule['pattern'], line):
                        issues.append(CodeIssue(
                            file=file_path,
                            line=idx,
                            column=1,
                            severity=rule.get('severity', 'warning'),
                            category=category,
                            message=rule['message'],
                            auto_fixable=rule.get('auto_fixable', False)
                        ))

        # AST-based analysis
        try:
            tree = ast.parse(content)
            issues.extend(self._analyze_ast(file_path, tree))
        except SyntaxError as e:
            issues.append(CodeIssue(
                file=file_path,
                line=e.lineno or 0,
                column=e.offset or 0,
                severity='error',
                category='style',
                message=f'Python syntax error: {e.msg}'
            ))

        return issues

    def _analyze_ast(self, file_path: str, tree: ast.AST) -> List[CodeIssue]:
        """Analyze Python AST for complex issues."""
        issues: List[CodeIssue] = []

        for node in ast.walk(tree):
            # Check function complexity
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > self.complexity_threshold:
                    issues.append(CodeIssue(
                        file=file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        severity='warning',
                        category='maintainability',
                        message=f'Function "{node.name}" has high complexity ({complexity})',
                        suggestion=f'Consider refactoring to reduce complexity below {self.complexity_threshold}'
                    ))

            # Check for too many arguments
            if isinstance(node, ast.FunctionDef) and len(node.args.args) > 5:
                issues.append(CodeIssue(
                    file=file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    severity='info',
                    category='maintainability',
                    message=f'Function "{node.name}" has too many parameters ({len(node.args.args)})',
                    suggestion='Consider using a configuration object or kwargs'
                ))

        return issues

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity

    def _analyze_js_file(self, file_path: str, content: str, lines: List[str]) -> List[CodeIssue]:
        """Analyze JavaScript/TypeScript file for issues."""
        issues: List[CodeIssue] = []

        # Apply maintainability rules
        for rule in self.rules.get('maintainability', []):
            for idx, line in enumerate(lines, start=1):
                if re.search(rule['pattern'], line):
                    issues.append(CodeIssue(
                        file=file_path,
                        line=idx,
                        column=1,
                        severity='info',
                        category='maintainability',
                        message=rule['message']
                    ))

        # JS/TS specific checks
        js_patterns = [
            {
                'pattern': r'console\.log\(',
                'message': 'Remove console.log() in production code',
                'severity': 'info'
            },
            {
                'pattern': r'debugger',
                'message': 'Remove debugger statement',
                'severity': 'warning'
            },
            {
                'pattern': r'==\s',
                'message': 'Use === instead of == for strict equality',
                'severity': 'info'
            },
            {
                'pattern': r'var\s+\w+',
                'message': 'Use let or const instead of var',
                'severity': 'info'
            },
        ]

        for rule in js_patterns:
            for idx, line in enumerate(lines, start=1):
                if re.search(rule['pattern'], line):
                    issues.append(CodeIssue(
                        file=file_path,
                        line=idx,
                        column=1,
                        severity=rule['severity'],
                        category='style',
                        message=rule['message']
                    ))

        return issues

    def _check_common_issues(self, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """Check for common issues across all file types."""
        issues: List[CodeIssue] = []

        for idx, line in enumerate(lines, start=1):
            # Check line length
            if len(line) > self.line_length_limit:
                issues.append(CodeIssue(
                    file=file_path,
                    line=idx,
                    column=self.line_length_limit,
                    severity='info',
                    category='style',
                    message=f'Line exceeds {self.line_length_limit} characters ({len(line)})'
                ))

        return issues

    def generate_report(self, issues: List[CodeIssue]) -> ReviewReport:
        """Generate comprehensive review report."""
        summary = {
            'total_issues': len(issues),
            'by_severity': {},
            'by_category': {},
            'auto_fixable': len([i for i in issues if i.auto_fixable]),
            'quality_score': self._calculate_quality_score(issues)
        }

        for issue in issues:
            summary['by_severity'][issue.severity] = summary['by_severity'].get(issue.severity, 0) + 1
            summary['by_category'][issue.category] = summary['by_category'].get(issue.category, 0) + 1

        recommendations = self._generate_recommendations(issues)

        return ReviewReport(
            summary=summary,
            issues=[asdict(issue) for issue in issues],
            recommendations=recommendations,
            metadata={
                'reviewer_version': '1.0.0',
                'rules_applied': list(self.rules.keys())
            }
        )

    def _calculate_quality_score(self, issues: List[CodeIssue]) -> int:
        """Calculate quality score (0-100) based on issues."""
        base_score = 100

        # Deduct points based on severity
        severity_weights = {
            'error': 10,
            'warning': 3,
            'info': 1
        }

        for issue in issues:
            weight = severity_weights.get(issue.severity, 1)
            # Extra weight for security issues
            if issue.category == 'security':
                weight *= 2
            # Cap deductions so the score never drops below 0 during calculation
            base_score = max(0, base_score - weight)

        return max(0, base_score)

    def _generate_recommendations(self, issues: List[CodeIssue]) -> List[str]:
        """Generate recommendations based on found issues."""
        recommendations: List[str] = []

        security_errors = [i for i in issues if i.category == 'security' and i.severity == 'error']
        if security_errors:
            recommendations.append(
                f'CRITICAL: {len(security_errors)} high-risk security issue(s) found. '
                'Must be fixed before prod gate approval.'
            )

        maintainability_issues = [i for i in issues if i.category == 'maintainability']
        if maintainability_issues:
            recommendations.append(
                f'{len(maintainability_issues)} maintainability issue(s) found. '
                'Consider adding to technical debt backlog.'
            )

        auto_fixable = [i for i in issues if i.auto_fixable]
        if auto_fixable:
            recommendations.append(
                f'{len(auto_fixable)} issue(s) can be auto-fixed. '
                'Run formatter to resolve.'
            )

        return recommendations


def _scan_targets() -> List[str]:
    """Get list of files to scan based on chatops namespace."""
    roots = [
        Path('services/engine-python'),
        Path('services/gateway-ts'),
        Path('scripts'),
        Path('tests'),
    ]

    exclude_prefix = (
        'artifacts', 'var', 'deployments', 'policies',
        '.git', 'node_modules', '__pycache__', '.venv',
        'dist', 'build', 'coverage'
    )

    files: List[str] = []

    for root in roots:
        if not root.exists():
            continue

        for path in root.rglob('*'):
            if not path.is_file():
                continue

            # Skip excluded directories
            if any(part in exclude_prefix for part in path.parts):
                continue

            # Only scan source files
            if path.suffix in ('.py', '.ts', '.js', '.tsx', '.jsx'):
                files.append(str(path))

    return sorted(files)


def main():
    """CLI entry point for intelligent code reviewer."""
    print("Intelligent Code Review System starting...")

    reviewer = IntelligentCodeReviewer()
    targets = _scan_targets()

    if not targets:
        print("No files found to scan.")
        print("Expected directories: services/engine-python/, services/gateway-ts/, scripts/, tests/")

        # Create minimal report
        report = ReviewReport(
            summary={'total_issues': 0, 'by_severity': {}, 'by_category': {}, 'auto_fixable': 0, 'quality_score': 100},
            issues=[],
            recommendations=['No source files found to review.']
        )
    else:
        print(f"Scanning {len(targets)} file(s)...")

        all_issues: List[CodeIssue] = []
        for filepath in targets:
            issues = reviewer.review_file(filepath)
            all_issues.extend(issues)
            if issues:
                print(f"  {filepath}: {len(issues)} issue(s)")

        report = reviewer.generate_report(all_issues)

    # Output report
    artifacts_dir = Path('artifacts')
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    output_path = artifacts_dir / 'intelligent-review.report.json'
    output_path.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print("")
    print("=" * 50)
    print("Intelligent Code Review System Complete")
    print("=" * 50)
    print(f"Total issues: {report.summary['total_issues']}")
    print(f"Quality score: {report.summary['quality_score']}/100")
    print(f"Report: {output_path}")

    if report.recommendations:
        print("")
        print("Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    # Exit with error if there are security errors
    if report.summary.get('by_severity', {}).get('error', 0) > 0:
        security_errors = report.summary.get('by_category', {}).get('security', 0)
        if security_errors > 0:
            print("")
            print(f"GATE BLOCKED: {security_errors} security error(s) found")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
