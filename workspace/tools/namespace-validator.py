#!/usr/bin/env python3
"""
MachineNativeOps Namespace Validator

Validates that all resources comply with MachineNativeOps namespace standards.
Checks against rules defined in mno-namespace.yaml and root.specs.naming.yaml.

Usage:
    python namespace-validator.py [--verbose] [--strict] <path>
    python namespace-validator.py --fix <path>

Examples:
    python namespace-validator.py .
    python namespace-validator.py --verbose --strict src/
    python namespace-validator.py --fix config/

Version: 1.0.0
Author: MachineNativeOps Platform Team
"""

import re
import sys
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Severity(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    file_path: str
    line_number: Optional[int]
    rule_id: str
    severity: Severity
    message: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Represents validation results for a file."""
    file_path: str
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: bool = True
    
    def add_issue(self, issue: ValidationIssue):
        """Add an issue to the result."""
        self.issues.append(issue)
        if issue.severity == Severity.ERROR:
            self.passed = False


class NamespaceValidator:
    """
    Comprehensive namespace validator for MachineNativeOps standards.
    """
    
    def __init__(self, strict=False, verbose=False, auto_fix=False):
        self.strict = strict
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.results: List[ValidationResult] = []
        
        # Validation rules aligned with mno-namespace.yaml
        self.validation_rules = {
            'NS-001': {
                'description': 'All resources must use machinenativeops namespace',
                'severity': Severity.ERROR,
                'pattern': r'namespace:\s*machinenativeops',
                'forbidden_pattern': r'namespace:\s*axiom\b',
                'suggestion': 'Use "namespace: machinenativeops"'
            },
            'NS-002': {
                'description': 'API versions must follow domain/version format',
                'severity': Severity.ERROR,
                'pattern': r'apiVersion:\s*machinenativeops\.io/v\d+',
                'forbidden_pattern': r'apiVersion:\s*axiom\.io',
                'suggestion': 'Use "apiVersion: machinenativeops.io/v1"'
            },
            'NS-003': {
                'description': 'Resource names must use kebab-case',
                'severity': Severity.ERROR,
                'pattern': r'name:\s*[a-z][a-z0-9-]*[a-z0-9]',
                'check_function': '_validate_kebab_case'
            },
            'NS-004': {
                'description': 'No legacy axiom namespace references allowed',
                'severity': Severity.ERROR,
                'forbidden_pattern': r'\baxiom\.io/|\bAxiom[A-Z]|urn:machinenativeops:',
                'suggestion': 'Replace axiom references with machinenativeops'
            },
            'NS-005': {
                'description': 'Registry must use machinenativeops.io domain',
                'severity': Severity.ERROR,
                'pattern': r'registry\.machinenativeops\.io',
                'forbidden_pattern': r'registry\.axiom\.io',
                'suggestion': 'Use "registry.machinenativeops.io"'
            },
            'NS-006': {
                'description': 'Paths must use /etc/machinenativeops prefix',
                'severity': Severity.ERROR,
                'pattern': r'/etc/machinenativeops',
                'forbidden_pattern': r'/etc/axiom',
                'suggestion': 'Use "/etc/machinenativeops" for configuration paths'
            },
            'NS-007': {
                'description': 'ETCD cluster must be super-agent-etcd-cluster',
                'severity': Severity.ERROR,
                'pattern': r'super-agent-etcd-cluster',
                'forbidden_pattern': r'machinenativeops-etcd-cluster',
                'suggestion': 'Use "super-agent-etcd-cluster"'
            },
            'NS-008': {
                'description': 'Labels must use machinenativeops.io/ prefix',
                'severity': Severity.WARNING,
                'pattern': r'machinenativeops\.io/[a-z][a-z0-9-]*',
                'forbidden_pattern': r'axiom\.io/',
                'suggestion': 'Use "machinenativeops.io/" for label keys'
            },
            'NS-009': {
                'description': 'Kind names must use MachineNativeOps prefix',
                'severity': Severity.WARNING,
                'pattern': r'kind:\s*MachineNativeOps[A-Z]\w*',
                'forbidden_pattern': r'kind:\s*Axiom[A-Z]',
                'suggestion': 'Use "MachineNativeOps" prefix for Kind names'
            },
            'NS-010': {
                'description': 'YAML keys must use snake_case',
                'severity': Severity.WARNING if not strict else Severity.ERROR,
                'check_function': '_validate_yaml_keys'
            }
        }
        
        # File extensions to validate
        self.processable_extensions = {
            '.yaml', '.yml', '.json', '.py', '.js', '.ts', '.md'
        }
        
        # Excluded directories
        self.excluded_dirs = {
            '.git', 'node_modules', '__pycache__', '.venv',
            'venv', 'dist', 'build', 'target', 'archive'
        }
    
    def load_namespace_config(self, config_path: str = 'mno-namespace.yaml') -> Optional[Dict]:
        """Load namespace configuration."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            if self.verbose:
                print(f"Info: {config_path} not found, using default rules")
            return None
        except Exception as e:
            print(f"Warning: Error loading namespace config: {e}")
            return None
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single file against namespace standards."""
        result = ValidationResult(file_path=str(file_path))
Namespace Validator Tool
命名空間驗證工具

Validates that all files conform to MachineNativeOps namespace standards.
驗證所有檔案符合 MachineNativeOps 命名空間標準。

Usage:
    python namespace-validator.py --file <file>
    python namespace-validator.py --scan <directory>
    python namespace-validator.py --report

Returns exit code 0 if all validations pass, non-zero otherwise.
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of a validation check"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.passed = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def add_error(self, message: str):
        """Add an error (causes validation to fail)"""
        self.errors.append(message)
        self.passed = False
    
    def add_warning(self, message: str):
        """Add a warning (doesn't cause validation to fail)"""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add informational message"""
        self.info.append(message)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "file": self.file_path,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info
        }


class NamespaceValidator:
    """Validates namespace compliance"""
    
    def __init__(self, config_path: str = "mno-namespace.yaml"):
        """Initialize validator with namespace configuration"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.results: List[ValidationResult] = []
        self.stats = {
            "files_checked": 0,
            "files_passed": 0,
            "files_failed": 0,
            "errors": 0,
            "warnings": 0
        }
    
    def _load_config(self) -> dict:
        """Load namespace configuration from YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded namespace config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate a single file
        
        Args:
            file_path: Path to file to validate
        
        Returns:
            ValidationResult object
        """
        result = ValidationResult(str(file_path))
        self.stats["files_checked"] += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check each validation rule
            for rule_id, rule in self.validation_rules.items():
                # Check forbidden patterns
                if 'forbidden_pattern' in rule:
                    self._check_forbidden_pattern(
                        content, lines, file_path, rule_id, rule, result
                    )
                
                # Check required patterns (only for YAML/JSON files)
                if 'pattern' in rule and file_path.suffix in {'.yaml', '.yml', '.json'}:
                    self._check_required_pattern(
                        content, file_path, rule_id, rule, result
                    )
                
                # Check with custom function
                if 'check_function' in rule:
                    check_func = getattr(self, rule['check_function'], None)
                    if check_func:
                        check_func(content, lines, file_path, rule_id, rule, result)
        
        except Exception as e:
            result.add_issue(ValidationIssue(
                file_path=str(file_path),
                line_number=None,
                rule_id='SYSTEM',
                severity=Severity.ERROR,
                message=f"Error validating file: {e}"
            ))
        
        return result
    
    def _check_forbidden_pattern(self, content: str, lines: List[str], 
                                 file_path: Path, rule_id: str, 
                                 rule: Dict, result: ValidationResult):
        """Check for forbidden patterns."""
        pattern = rule['forbidden_pattern']
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        if matches:
            for match in matches:
                # Find line number
                line_number = content[:match.start()].count('\n') + 1
                
                result.add_issue(ValidationIssue(
                    file_path=str(file_path),
                    line_number=line_number,
                    rule_id=rule_id,
                    severity=rule['severity'],
                    message=f"{rule['description']}: Found '{match.group()}'",
                    suggestion=rule.get('suggestion')
                ))
    
    def _check_required_pattern(self, content: str, file_path: Path,
                               rule_id: str, rule: Dict, result: ValidationResult):
        """Check for required patterns in YAML/JSON files."""
        pattern = rule['pattern']
        
        # Only check if the file seems to define the relevant resource
        # (e.g., only check namespace if 'namespace:' exists)
        if rule_id == 'NS-001' and 'namespace:' in content:
            if not re.search(pattern, content, re.MULTILINE):
                result.add_issue(ValidationIssue(
                    file_path=str(file_path),
                    line_number=None,
                    rule_id=rule_id,
                    severity=rule['severity'],
                    message=rule['description'],
                    suggestion=rule.get('suggestion')
                ))
    
    def _validate_kebab_case(self, content: str, lines: List[str],
                            file_path: Path, rule_id: str,
                            rule: Dict, result: ValidationResult):
        """Validate that resource names use kebab-case."""
        # Check for 'name:' fields in YAML
        if file_path.suffix in {'.yaml', '.yml'}:
            name_pattern = r'^\s*name:\s*(["\']?)([^"\'\s]+)\1\s*$'
            for i, line in enumerate(lines):
                match = re.match(name_pattern, line)
                if match:
                    name = match.group(2)
                    # Skip if it's a variable or environment reference
                    if '{{' in name or '${' in name:
                        continue
                    
                    # Check kebab-case
                    if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$', name):
                        result.add_issue(ValidationIssue(
                            file_path=str(file_path),
                            line_number=i + 1,
                            rule_id=rule_id,
                            severity=rule['severity'],
                            message=f"Resource name '{name}' does not use kebab-case",
                            suggestion="Use lowercase letters, numbers, and hyphens only"
                        ))
    
    def _validate_yaml_keys(self, content: str, lines: List[str],
                           file_path: Path, rule_id: str,
                           rule: Dict, result: ValidationResult):
        """Validate that YAML keys use snake_case."""
        if file_path.suffix not in {'.yaml', '.yml'}:
            return
        
        # Pattern to match YAML keys
        key_pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:'
        
        for i, line in enumerate(lines):
            match = re.match(key_pattern, line)
            if match:
                key = match.group(1)
                
                # Skip special cases (environment variables, metadata fields)
                if key.isupper() or key in {'apiVersion', 'kind', 'metadata'}:
                    continue
                
                # Check snake_case
                if not re.match(r'^[a-z][a-z0-9_]*$', key):
                    result.add_issue(ValidationIssue(
                        file_path=str(file_path),
                        line_number=i + 1,
                        rule_id=rule_id,
                        severity=rule['severity'],
                        message=f"YAML key '{key}' does not use snake_case",
                        suggestion="Use lowercase letters, numbers, and underscores only"
                    ))
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be validated."""
        # Check file extension
        if file_path.suffix not in self.processable_extensions:
            return False
        
        # Check if in excluded directory
        for parent in file_path.parents:
            if parent.name in self.excluded_dirs:
                return False
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return False
        
        return True
    
    def validate_directory(self, directory_path: Path) -> List[ValidationResult]:
        """Recursively validate all files in a directory."""
        results = []
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                result = self.validate_file(file_path)
                if not result.passed or result.issues:
                    results.append(result)
        
        return results
    
    def validate_path(self, path: Path) -> List[ValidationResult]:
        """Validate a file or directory."""
        if path.is_file():
            return [self.validate_file(path)]
        elif path.is_dir():
            return self.validate_directory(path)
        else:
            print(f"Error: {path} is not a valid file or directory")
            return []
    
    def generate_report(self) -> str:
        """Generate a detailed validation report."""
        total_files = len(self.results)
        total_issues = sum(len(r.issues) for r in self.results)
        total_errors = sum(
            len([i for i in r.issues if i.severity == Severity.ERROR])
            for r in self.results
        )
        total_warnings = sum(
            len([i for i in r.issues if i.severity == Severity.WARNING])
            for r in self.results
        )
        files_passed = sum(1 for r in self.results if r.passed)
        
        report = []
        report.append("=" * 80)
        report.append("MachineNativeOps Namespace Validation Report")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Mode: {'Strict' if self.strict else 'Standard'}")
        report.append("")
        report.append("Summary")
        report.append("-" * 80)
        report.append(f"Files validated:     {total_files}")
        report.append(f"Files passed:        {files_passed}")
        report.append(f"Files failed:        {total_files - files_passed}")
        report.append(f"Total issues:        {total_issues}")
        report.append(f"  Errors:            {total_errors}")
        report.append(f"  Warnings:          {total_warnings}")
        report.append("")
        
        if self.results:
            # Group issues by rule
            issues_by_rule: Dict[str, List[ValidationIssue]] = {}
            for result in self.results:
                for issue in result.issues:
                    if issue.rule_id not in issues_by_rule:
                        issues_by_rule[issue.rule_id] = []
                    issues_by_rule[issue.rule_id].append(issue)
            
            report.append("Issues by Rule")
            report.append("-" * 80)
            for rule_id in sorted(issues_by_rule.keys()):
                issues = issues_by_rule[rule_id]
                report.append(f"\n{rule_id}: {len(issues)} occurrences")
                rule = self.validation_rules.get(rule_id, {})
                if rule:
                    report.append(f"  Description: {rule.get('description', 'N/A')}")
                
                # Show first few examples
                for issue in issues[:3]:
                    report.append(f"  - {issue.file_path}:{issue.line_number or '?'}")
                    report.append(f"    {issue.message}")
                    if issue.suggestion:
                        report.append(f"    💡 {issue.suggestion}")
                
                if len(issues) > 3:
                    report.append(f"  ... and {len(issues) - 3} more")
        
        report.append("")
        report.append("=" * 80)
        
        if total_errors == 0 and total_warnings == 0:
            report.append("✓ All files comply with MachineNativeOps namespace standards")
        elif total_errors == 0:
            report.append(f"⚠ Validation completed with {total_warnings} warnings")
        else:
            report.append(f"✗ Validation failed with {total_errors} errors")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, report: str, output_path: str = "namespace-validation-report.txt"):
        """Save report to file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\nReport saved to: {output_path}")
        except Exception as e:
            print(f"Error saving report: {e}")


def main():
    """Main entry point for the namespace validator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='MachineNativeOps Namespace Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate current directory
  python namespace-validator.py .
  
  # Strict validation with verbose output
  python namespace-validator.py --strict --verbose src/
  
  # Generate detailed report
  python namespace-validator.py --report .
        """
    )
    
    parser.add_argument('path', type=str, help='File or directory path to validate')
    parser.add_argument('--strict', action='store_true', help='Enable strict validation mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--report', action='store_true', help='Generate detailed report file')
    parser.add_argument('--report-path', type=str, default='namespace-validation-report.txt',
                       help='Path for report file (default: namespace-validation-report.txt)')
    
    args = parser.parse_args()
    
    # Validate path exists
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path {path} does not exist")
        sys.exit(1)
    
    # Create validator
    validator = NamespaceValidator(
        strict=args.strict,
        verbose=args.verbose
    )
    
    # Load namespace config if available
    validator.load_namespace_config()
    
    # Perform validation
    print(f"Validating namespace compliance in: {path}")
    if args.strict:
        print("(STRICT MODE - warnings treated as errors)")
    print()
    
    validator.results = validator.validate_path(path)
    
    # Generate and display report
    report = validator.generate_report()
    print("\n" + report)
    
    # Save report if requested
    if args.report:
        validator.save_report(report, args.report_path)
    
    # Exit with appropriate code
    total_errors = sum(
        len([i for i in r.issues if i.severity == Severity.ERROR])
        for r in validator.results
    )
    sys.exit(1 if total_errors > 0 else 0)
            
            # Run validation checks
            self._check_legacy_namespaces(content, result)
            self._check_namespace_consistency(content, result)
            self._check_naming_patterns(content, result)
            self._check_registry_urls(content, result)
            self._check_certificate_paths(content, result)
            self._check_cluster_tokens(content, result)
            
            # Update stats
            if result.passed:
                self.stats["files_passed"] += 1
            else:
                self.stats["files_failed"] += 1
            
            self.stats["errors"] += len(result.errors)
            self.stats["warnings"] += len(result.warnings)
            
        except Exception as e:
            result.add_error(f"Validation error: {e}")
            self.stats["files_failed"] += 1
            self.stats["errors"] += 1
        
        self.results.append(result)
        return result
    
    def _check_legacy_namespaces(self, content: str, result: ValidationResult):
        """Check for legacy namespace usage"""
        migration = self.config.get("migration", {})
        legacy_namespaces = migration.get("legacy_namespaces", [])
        
        for legacy_ns in legacy_namespaces:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(legacy_ns) + r'\b'
            if re.search(pattern, content):
                result.add_error(
                    f"Legacy namespace '{legacy_ns}' found - should be migrated to 'machinenativeops'"
                )
    
    def _check_namespace_consistency(self, content: str, result: ValidationResult):
        """Check that namespace usage is consistent"""
        namespace_config = self.config.get("namespace", {})
        primary_ns = namespace_config.get("primary", "")
        variants = namespace_config.get("variants", {})
        
        # Count occurrences of each variant
        variant_counts = {}
        for variant_type, variant_name in variants.items():
            count = len(re.findall(re.escape(variant_name), content))
            if count > 0:
                variant_counts[variant_type] = count
        
        # If multiple variants are used, that might indicate inconsistency
        if len(variant_counts) > 2:  # Allow some flexibility
            result.add_warning(
                f"Multiple namespace variants used: {', '.join(variant_counts.keys())} - "
                "consider using consistent casing"
            )
    
    def _check_naming_patterns(self, content: str, result: ValidationResult):
        """Validate naming pattern compliance"""
        validation_config = self.config.get("validation", {})
        
        # Check namespace pattern
        namespace_pattern = validation_config.get("namespace_pattern", "")
        if namespace_pattern:
            # Find all potential namespace references
            matches = re.findall(r'\bmachinenativeops(?:-[a-z0-9]+)*\b', content, re.IGNORECASE)
            for match in matches:
                if not re.match(namespace_pattern, match.lower()):
                    result.add_error(
                        f"Invalid namespace format '{match}' - must match pattern {namespace_pattern}"
                    )
        
        # Check version pattern if versions are present
        version_pattern = validation_config.get("version_pattern", "")
        if version_pattern:
            version_matches = re.findall(r'\b[vV]?\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?\b', content)
            for version in version_matches:
                if not re.match(version_pattern, version):
                    result.add_warning(
                        f"Version '{version}' may not match standard pattern {version_pattern}"
                    )
    
    def _check_registry_urls(self, content: str, result: ValidationResult):
        """Check registry URL usage"""
        registries = self.config.get("registries", {})
        primary_registry = registries.get("primary", {}).get("url", "")
        
        if not primary_registry:
            return
        
        # Check for correct registry usage
        if primary_registry in content:
            result.add_info(f"Uses primary registry: {primary_registry}")
        
        # Check for incorrect registry patterns
        incorrect_patterns = [
            r'docker\.io/machine-native-ops',
            r'ghcr\.io/machine-native-ops-machine-native-ops',
            r'docker\.io/machine-native-ops-machine-native-ops',
            r'docker\.io/machine-native-ops-apps',
            r'ghcr\.io/machine-native-ops-apps',
        ]
        
        for pattern in incorrect_patterns:
            if re.search(pattern, content):
                result.add_error(
                    f"Found legacy registry pattern - should use {primary_registry}"
                )
    
    def _check_certificate_paths(self, content: str, result: ValidationResult):
        """Check certificate path compliance"""
        certs = self.config.get("certificates", {})
        correct_base_path = certs.get("base_path", "")
        correct_pkl_path = certs.get("pkl_path", "")
        
        # Check for correct paths
        if correct_pkl_path and correct_pkl_path in content:
            result.add_info(f"Uses correct PKL path: {correct_pkl_path}")
        
        # Check for incorrect certificate paths
        incorrect_paths = [
            r'/etc/machine-native-ops',
            r'/etc/machine-native-ops',
            r'/etc/apps',
        ]
        
        for pattern in incorrect_paths:
            if re.search(pattern, content):
                result.add_error(
                    f"Found legacy certificate path - should use {correct_base_path}"
                )
    
    def _check_cluster_tokens(self, content: str, result: ValidationResult):
        """Check cluster token usage"""
        clusters = self.config.get("clusters", {})
        etcd_config = clusters.get("etcd", {})
        correct_token = etcd_config.get("token", "")
        
        if correct_token and correct_token in content:
            result.add_info(f"Uses correct etcd cluster token")
        
        # Check for legacy cluster tokens
        legacy_tokens = [
            'machine-native-ops-etcd-cluster',
            'machine-native-ops-etcd',
        ]
        
        for token in legacy_tokens:
            if token in content:
                result.add_error(
                    f"Found legacy cluster token '{token}' - should use {correct_token}"
                )
    
    def scan_directory(self, directory: Path, patterns: List[str] = None) -> None:
        """
        Scan and validate all files in a directory
        
        Args:
            directory: Directory to scan
            patterns: File patterns to match
        """
        if patterns is None:
            patterns = ['*.yaml', '*.yml', '*.md', '*.json', '*.sh', '*.py', '*.ts', '*.js']
        
        directory = Path(directory)
        if not directory.is_dir():
            logger.error(f"Not a directory: {directory}")
            return
        
        logger.info(f"Scanning directory: {directory}")
        
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                # Skip hidden files and directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                
                # Skip certain directories
                skip_dirs = {'node_modules', 'dist', 'build', '.git', '__pycache__', 'vendor'}
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                
                self.validate_file(file_path)
    
    def print_report(self, verbose: bool = False):
        """Print validation report"""
        print("\n" + "="*80)
        print("Namespace Validation Report")
        print("="*80)
        
        # Summary statistics
        print(f"\n📊 Summary:")
        print(f"  Files checked:  {self.stats['files_checked']}")
        print(f"  ✅ Passed:      {self.stats['files_passed']}")
        print(f"  ❌ Failed:      {self.stats['files_failed']}")
        print(f"  Errors:         {self.stats['errors']}")
        print(f"  Warnings:       {self.stats['warnings']}")
        
        # Failed files
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            print(f"\n❌ Failed Files ({len(failed_results)}):")
            for result in failed_results:
                print(f"\n  {result.file_path}")
                for error in result.errors:
                    print(f"    ❌ {error}")
                if verbose and result.warnings:
                    for warning in result.warnings:
                        print(f"    ⚠️  {warning}")
        
        # Warnings (if verbose)
        if verbose:
            warning_results = [r for r in self.results if r.warnings and r.passed]
            if warning_results:
                print(f"\n⚠️  Files with Warnings ({len(warning_results)}):")
                for result in warning_results:
                    print(f"\n  {result.file_path}")
                    for warning in result.warnings:
                        print(f"    ⚠️  {warning}")
        
        # Overall result
        print("\n" + "="*80)
        if self.stats['files_failed'] == 0:
            print("✅ All validations passed!")
        else:
            print(f"❌ Validation failed: {self.stats['files_failed']} files need attention")
        print("="*80 + "\n")
    
    def generate_json_report(self) -> str:
        """Generate JSON report"""
        report = {
            "summary": self.stats,
            "results": [r.to_dict() for r in self.results]
        }
        return json.dumps(report, indent=2)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate namespace compliance with MachineNativeOps standards"
    )
    parser.add_argument(
        "--config",
        default="mno-namespace.yaml",
        help="Path to namespace configuration file"
    )
    parser.add_argument(
        "--file",
        help="Validate a single file"
    )
    parser.add_argument(
        "--scan",
        help="Scan and validate all files in directory"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )
    parser.add_argument(
        "--json",
        help="Output JSON report to file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Initialize validator
    validator = NamespaceValidator(config_path=args.config)
    
    # Execute requested operation
    if args.file:
        result = validator.validate_file(Path(args.file))
        
        print(f"\nValidation result for {result.file_path}:")
        print(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")
        
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  ❌ {error}")
        
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")
        
        if args.verbose and result.info:
            print("\nInfo:")
            for info in result.info:
                print(f"  ℹ️  {info}")
        
        sys.exit(0 if result.passed else 1)
    
    elif args.scan:
        validator.scan_directory(Path(args.scan))
        validator.print_report(verbose=args.verbose)
        
        if args.json:
            with open(args.json, 'w') as f:
                f.write(validator.generate_json_report())
            print(f"JSON report written to {args.json}")
        
        sys.exit(0 if validator.stats['files_failed'] == 0 else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
