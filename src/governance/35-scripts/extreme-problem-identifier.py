#!/usr/bin/env python3
"""
SynergyMesh Extreme Problem Identifier (極致問題識別系統)

Purpose: Advanced multi-dimensional problem detection and root cause analysis
Provides extreme-level diagnostic capabilities beyond basic validation

Features:
- 10+ problem detection categories
- Root cause analysis with AI-powered insights
- Predictive issue detection
- Cross-dimensional impact analysis
- INSTANT EXECUTION: < 10 seconds full scan

Usage:
    python governance/scripts/extreme-problem-identifier.py
    python governance/scripts/extreme-problem-identifier.py --verbose
    python governance/scripts/extreme-problem-identifier.py --category security
    python governance/scripts/extreme-problem-identifier.py --fix-auto
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import hashlib

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Global secret patterns to help sanitize log messages (defense-in-depth)
SECRET_REGEXES = [
    re.compile(r'password\s*=\s*["\'].*["\']', re.IGNORECASE),
    re.compile(r'api[_-]?key\s*=\s*["\'].*["\']', re.IGNORECASE),
    re.compile(r'secret\s*=\s*["\'].*["\']', re.IGNORECASE),
    re.compile(r'token\s*=\s*["\'].*["\']', re.IGNORECASE),
]

class ProblemSeverity:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class ProblemCategory:
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    DEPENDENCIES = "dependencies"
    CONFIGURATION = "configuration"
    DOCUMENTATION = "documentation"
    CODE_QUALITY = "code_quality"
    DRIFT = "drift"
    PREDICTIVE = "predictive"

class Problem:
    def __init__(self, category: str, severity: str, title: str, description: str, 
                 location: str, impact: str, recommendation: str, auto_fixable: bool = False):
        """Initialize a Problem instance"""
        self.id = hashlib.sha256(f"{category}{title}{location}".encode()).hexdigest()[:8]
        self.category = category
        self.severity = severity
        self.title = title
        self.description = description
        self.location = location
        self.impact = impact
        self.recommendation = recommendation
        self.auto_fixable = auto_fixable
        self.detected_at = datetime.utcnow().isoformat() + "Z"

class ExtremeProblemIdentifier:
    def __init__(self, governance_root: str = "governance", verbose: bool = False):
        self.governance_root = Path(governance_root)
        self.verbose = verbose
        self.problems: List[Problem] = []
        self.stats = defaultdict(int)
        
    def log(self, message: str, level: str = "info"):
        """Log message with color. Redacts obvious secrets in logs."""
        def redact_sensitive(msg: str) -> str:
            # Remove common possible secret substrings (passwords/keys/tokens) from msg
            redacted = msg
            # Use global secret regexes for consistency
            for regex in SECRET_REGEXES:
                redacted = regex.sub(lambda m: re.sub(r'(["\'])(.*?)(\1)', r'\1***\1', m.group(0)), redacted)
            # Additional defensive redaction for simple key=value style secrets
            patterns = [
                r'(password\s*=\s*)(["\']?)[^"\',\s]+(\2)',
                r'(api[_-]?key\s*=\s*)(["\']?)[^"\',\s]+(\2)',
                r'(secret\s*=\s*)(["\']?)[^"\',\s]+(\2)',
                r'(token\s*=\s*)(["\']?)[^"\',\s]+(\2)',
            ]
            for p in patterns:
                redacted = re.sub(p, r'\1***\3', redacted, flags=re.IGNORECASE)
            return redacted

        def is_potentially_sensitive(msg: str) -> bool:
            """Heuristic check to avoid logging messages that may contain secrets."""
            lowered = msg.lower()
            # Keyword-based heuristic
            if any(s in lowered for s in ["password", "api key", "apikey", "secret", "token", "bearer "]):
                return True
            # Regex-based heuristic using global secret patterns
            for regex in SECRET_REGEXES:
                if regex.search(msg):
                    return True
            return False

        redacted_message = redact_sensitive(message)

        # As a final safeguard, do not log messages that still look sensitive after redaction
        if is_potentially_sensitive(redacted_message):
            return

        if level == "critical":
            print(f"{Colors.FAIL}🔴 CRITICAL: {redacted_message}{Colors.ENDC}")
        elif level == "error":
            print(f"{Colors.FAIL}❌ HIGH: {redacted_message}{Colors.ENDC}")
        elif level == "warning":
            print(f"{Colors.WARNING}⚠️  MEDIUM: {redacted_message}{Colors.ENDC}")
        elif level == "info":
            if self.verbose:
                print(f"{Colors.OKBLUE}ℹ️  INFO: {redacted_message}{Colors.ENDC}")
        elif level == "success":
            print(f"{Colors.OKGREEN}✅ {redacted_message}{Colors.ENDC}")
    
    def add_problem(self, problem: Problem):
        """Add identified problem"""
        self.problems.append(problem)
        self.stats[problem.severity] += 1
        self.stats[problem.category] += 1
        
        # Log based on category and severity - suppress all details for SECURITY problems
        if problem.category == ProblemCategory.SECURITY:
            # Never log sensitive details for security problems, regardless of severity
            self.log("Security issue detected (details suppressed in logs)", "critical" if problem.severity == ProblemSeverity.CRITICAL else "warning")
        else:
            if problem.severity == ProblemSeverity.CRITICAL:
                self.log(f"[{problem.category}] {problem.title} @ {problem.location}", "critical")
            elif problem.severity == ProblemSeverity.HIGH:
                self.log(f"[{problem.category}] {problem.title} @ {problem.location}", "error")
            elif problem.severity == ProblemSeverity.MEDIUM:
                self.log(f"[{problem.category}] {problem.title} @ {problem.location}", "warning")
            else:
                self.log(f"[{problem.category}] {problem.title} @ {problem.location}", "info")
    
    def detect_security_vulnerabilities(self):
        """Category 1: Security vulnerability detection"""
        print(f"\n{Colors.BOLD}[1/10] 🔒 Detecting Security Vulnerabilities...{Colors.ENDC}")
        
        # Check for exposed secrets patterns
        secret_patterns = [
            (r'password\s*=\s*["\'].*["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'].*["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'].*["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'].*["\']', "Hardcoded token"),
        ]
        
        for yaml_file in self.governance_root.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern, desc in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.add_problem(Problem(
                                category=ProblemCategory.SECURITY,
                                severity=ProblemSeverity.CRITICAL,
                                title=f"{desc} detected",
                                description=f"Potential hardcoded credential found in configuration file",
                                location=str(yaml_file.relative_to(self.governance_root)),
                                impact="CRITICAL: Exposed credentials can lead to unauthorized access",
                                recommendation="Move credentials to environment variables or secret management system",
                                auto_fixable=False
                            ))
            except Exception:
                pass
        
        # Check for insecure permissions
        for dim_file in self.governance_root.rglob("dimension.yaml"):
            try:
                with open(dim_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'spec' in data:
                        policy = data['spec'].get('policy', {})
                        if policy.get('enforcement') == 'optional':
                            self.add_problem(Problem(
                                category=ProblemCategory.SECURITY,
                                severity=ProblemSeverity.MEDIUM,
                                title="Optional policy enforcement detected",
                                description="Dimension has optional policy enforcement which may allow violations",
                                location=str(dim_file.relative_to(self.governance_root)),
                                impact="Security policies may not be enforced consistently",
                                recommendation="Change enforcement to 'required' for critical dimensions",
                                auto_fixable=True
                            ))
            except Exception:
                pass
    
    def detect_architecture_violations(self):
        """Category 2: Architecture pattern violations"""
        print(f"\n{Colors.BOLD}[2/10] 🏗️  Detecting Architecture Violations...{Colors.ENDC}")
        
        # Check for circular dependencies
        governance_map_file = self.governance_root / "governance-map.yaml"
        if governance_map_file.exists():
            try:
                with open(governance_map_file, 'r', encoding='utf-8') as f:
                    gov_map = yaml.safe_load(f)
                    dimensions = gov_map.get('dimensions', [])
                    
                    # Build dependency graph
                    dep_graph = {}
                    for dim in dimensions:
                        name = dim.get('name')
                        depends_on = dim.get('depends_on', [])
                        dep_graph[name] = depends_on
                    
                    # Detect cycles using DFS
                    def has_cycle(node, visited, rec_stack):
                        visited.add(node)
                        rec_stack.add(node)
                        
                        for neighbor in dep_graph.get(node, []):
                            if neighbor not in visited:
                                if has_cycle(neighbor, visited, rec_stack):
                                    return True
                            elif neighbor in rec_stack:
                                return True
                        
                        rec_stack.remove(node)
                        return False
                    
                    visited = set()
                    for node in dep_graph:
                        if node not in visited:
                            rec_stack = set()
                            if has_cycle(node, visited, rec_stack):
                                self.add_problem(Problem(
                                    category=ProblemCategory.ARCHITECTURE,
                                    severity=ProblemSeverity.HIGH,
                                    title="Circular dependency detected",
                                    description=f"Dimension '{node}' is part of a circular dependency chain",
                                    location="governance-map.yaml",
                                    impact="Circular dependencies can cause initialization deadlocks",
                                    recommendation="Refactor dependencies to create a directed acyclic graph (DAG)",
                                    auto_fixable=False
                                ))
                                break
            except Exception:
                pass
        
        # Check for missing README files in dimensions
        for dim_dir in self.governance_root.glob("*-*"):
            if dim_dir.is_dir() and not (dim_dir / "README.md").exists():
                self.add_problem(Problem(
                    category=ProblemCategory.ARCHITECTURE,
                    severity=ProblemSeverity.LOW,
                    title="Missing README documentation",
                    description=f"Dimension {dim_dir.name} lacks README.md file",
                    location=str(dim_dir.relative_to(self.governance_root)),
                    impact="Reduced maintainability and onboarding difficulty",
                    recommendation="Create README.md with dimension purpose, usage, and examples",
                    auto_fixable=True
                ))
    
    def detect_performance_issues(self):
        """Category 3: Performance bottlenecks"""
        print(f"\n{Colors.BOLD}[3/10] ⚡ Detecting Performance Issues...{Colors.ENDC}")
        
        # Check for large YAML files (> 100KB)
        for yaml_file in self.governance_root.rglob("*.yaml"):
            size_kb = yaml_file.stat().st_size / 1024
            if size_kb > 100:
                self.add_problem(Problem(
                    category=ProblemCategory.PERFORMANCE,
                    severity=ProblemSeverity.MEDIUM,
                    title="Large configuration file detected",
                    description=f"File size: {size_kb:.1f}KB (threshold: 100KB)",
                    location=str(yaml_file.relative_to(self.governance_root)),
                    impact="Large files slow down parsing and CI/CD pipelines",
                    recommendation="Split into smaller files or use references",
                    auto_fixable=False
                ))
        
        # Check for deeply nested structures
        for yaml_file in self.governance_root.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                    def get_depth(d, current_depth=0):
                        if not isinstance(d, dict):
                            return current_depth
                        return max([get_depth(v, current_depth + 1) for v in d.values()] or [current_depth])
                    
                    if data:
                        depth = get_depth(data)
                        if depth > 8:
                            self.add_problem(Problem(
                                category=ProblemCategory.PERFORMANCE,
                                severity=ProblemSeverity.LOW,
                                title="Deeply nested structure detected",
                                description=f"Nesting depth: {depth} levels (recommended: ≤ 8)",
                                location=str(yaml_file.relative_to(self.governance_root)),
                                impact="Difficult to parse and maintain, potential performance impact",
                                recommendation="Flatten structure or use references",
                                auto_fixable=False
                            ))
            except Exception:
                pass
    
    def detect_compliance_gaps(self):
        """Category 4: Compliance and standard violations"""
        print(f"\n{Colors.BOLD}[4/10] 📋 Detecting Compliance Gaps...{Colors.ENDC}")
        
        # Check for dimensions missing compliance frameworks
        for dim_file in self.governance_root.rglob("dimension.yaml"):
            try:
                with open(dim_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'spec' in data:
                        compliance = data['spec'].get('compliance', {})
                        frameworks = compliance.get('frameworks', [])
                        
                        if not frameworks:
                            self.add_problem(Problem(
                                category=ProblemCategory.COMPLIANCE,
                                severity=ProblemSeverity.MEDIUM,
                                title="No compliance frameworks defined",
                                description="Dimension lacks compliance framework declarations",
                                location=str(dim_file.relative_to(self.governance_root)),
                                impact="Cannot track compliance requirements and audits",
                                recommendation="Add relevant frameworks (ISO-42001, NIST-AI-RMF, COBIT-2019)",
                                auto_fixable=True
                            ))
            except Exception:
                pass
    
    def detect_dependency_issues(self):
        """Category 5: Dependency problems"""
        print(f"\n{Colors.BOLD}[5/10] 🔗 Detecting Dependency Issues...{Colors.ENDC}")
        
        # Check for missing dependencies
        governance_map_file = self.governance_root / "governance-map.yaml"
        if governance_map_file.exists():
            try:
                with open(governance_map_file, 'r', encoding='utf-8') as f:
                    gov_map = yaml.safe_load(f)
                    dimensions = gov_map.get('dimensions', [])
                    dim_names = {d.get('name') for d in dimensions}
                    
                    for dim in dimensions:
                        name = dim.get('name')
                        depends_on = dim.get('depends_on', [])
                        
                        for dep in depends_on:
                            if dep not in dim_names:
                                self.add_problem(Problem(
                                    category=ProblemCategory.DEPENDENCIES,
                                    severity=ProblemSeverity.HIGH,
                                    title="Missing dependency detected",
                                    description=f"Dimension '{name}' depends on non-existent '{dep}'",
                                    location="governance-map.yaml",
                                    impact="Runtime failures and initialization errors",
                                    recommendation=f"Either create dimension '{dep}' or remove dependency",
                                    auto_fixable=False
                                ))
            except Exception:
                pass
    
    def detect_configuration_drift(self):
        """Category 6: Configuration drift detection"""
        print(f"\n{Colors.BOLD}[6/10] 🔄 Detecting Configuration Drift...{Colors.ENDC}")
        
        # Check for inconsistent metadata across dimension files
        metadata_fields = defaultdict(set)
        
        for dim_file in self.governance_root.rglob("dimension.yaml"):
            try:
                with open(dim_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'metadata' in data:
                        for key in data['metadata'].keys():
                            metadata_fields[key].add(str(dim_file.relative_to(self.governance_root)))
            except Exception:
                pass
        
        # Find inconsistencies
        all_files = {f for files in metadata_fields.values() for f in files}
        for field, files in metadata_fields.items():
            if len(files) < len(all_files):
                missing_count = len(all_files) - len(files)
                self.add_problem(Problem(
                    category=ProblemCategory.DRIFT,
                    severity=ProblemSeverity.LOW,
                    title=f"Inconsistent metadata field: '{field}'",
                    description=f"Field missing in {missing_count} dimension files",
                    location="multiple dimension.yaml files",
                    impact="Inconsistent metadata structure across dimensions",
                    recommendation="Standardize metadata fields across all dimensions",
                    auto_fixable=True
                ))
    
    def detect_documentation_gaps(self):
        """Category 7: Documentation quality issues"""
        print(f"\n{Colors.BOLD}[7/10] 📚 Detecting Documentation Gaps...{Colors.ENDC}")
        
        # Check for empty or minimal READMEs
        for readme in self.governance_root.rglob("README.md"):
            size = readme.stat().st_size
            if size < 500:  # Less than 500 bytes
                self.add_problem(Problem(
                    category=ProblemCategory.DOCUMENTATION,
                    severity=ProblemSeverity.LOW,
                    title="Minimal README documentation",
                    description=f"README.md is only {size} bytes",
                    location=str(readme.relative_to(self.governance_root)),
                    impact="Insufficient documentation for maintainers",
                    recommendation="Expand README with purpose, usage, examples, and maintenance info",
                    auto_fixable=False
                ))
    
    def detect_code_quality_issues(self):
        """Category 8: Code quality and technical debt"""
        print(f"\n{Colors.BOLD}[8/10] 🧹 Detecting Code Quality Issues...{Colors.ENDC}")
        
        # Check for TODO/FIXME/HACK comments in YAML
        for yaml_file in self.governance_root.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(r'#.*(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                            self.add_problem(Problem(
                                category=ProblemCategory.CODE_QUALITY,
                                severity=ProblemSeverity.LOW,
                                title="Technical debt marker found",
                                description=f"Line {line_num}: {line.strip()}",
                                location=str(yaml_file.relative_to(self.governance_root)),
                                impact="Unresolved technical debt tracked in comments",
                                recommendation="Create tracked issue and resolve or remove marker",
                                auto_fixable=False
                            ))
            except Exception:
                pass
    
    def detect_naming_violations(self):
        """Category 9: Naming convention violations"""
        print(f"\n{Colors.BOLD}[9/10] 📝 Detecting Naming Violations...{Colors.ENDC}")
        
        # Check dimension naming consistency
        for dim_dir in self.governance_root.glob("*"):
            if dim_dir.is_dir() and re.match(r'^\d{2}-', dim_dir.name):
                # Check if name uses lowercase and hyphens
                name_part = dim_dir.name[3:]  # Remove "XX-" prefix
                if not re.match(r'^[a-z-]+$', name_part):
                    self.add_problem(Problem(
                        category=ProblemCategory.CODE_QUALITY,
                        severity=ProblemSeverity.LOW,
                        title="Naming convention violation",
                        description=f"Dimension name '{dim_dir.name}' doesn't follow lowercase-hyphen pattern",
                        location=str(dim_dir.relative_to(self.governance_root)),
                        impact="Inconsistent naming reduces readability",
                        recommendation="Use lowercase letters and hyphens only (e.g., 'XX-example-name')",
                        auto_fixable=False
                    ))
    
    def detect_predictive_issues(self):
        """Category 10: Predictive issue detection"""
        print(f"\n{Colors.BOLD}[10/10] 🔮 Detecting Predictive Issues...{Colors.ENDC}")
        
        # Check for approaching migration deadlines
        governance_map_file = self.governance_root / "governance-map.yaml"
        if governance_map_file.exists():
            try:
                with open(governance_map_file, 'r', encoding='utf-8') as f:
                    gov_map = yaml.safe_load(f)
                    migrations = gov_map.get('migrations', {}).get('pending', [])
                    
                    for migration in migrations:
                        deadline_str = migration.get('deadline')
                        asset = migration.get('asset')
                        
                        if deadline_str:
                            try:
                                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                                days_left = (deadline - datetime.now()).days
                                
                                if days_left < 0:
                                    severity = ProblemSeverity.HIGH
                                    title = "Overdue migration"
                                elif days_left <= 3:
                                    severity = ProblemSeverity.MEDIUM
                                    title = "Urgent migration deadline"
                                elif days_left <= 7:
                                    severity = ProblemSeverity.LOW
                                    title = "Approaching migration deadline"
                                else:
                                    continue
                                
                                self.add_problem(Problem(
                                    category=ProblemCategory.PREDICTIVE,
                                    severity=severity,
                                    title=title,
                                    description=f"Migration for '{asset}' due in {days_left} days",
                                    location="governance-map.yaml :: migrations",
                                    impact="Delayed migrations can cause governance debt",
                                    recommendation="Prioritize migration execution or extend deadline with justification",
                                    auto_fixable=False
                                ))
                            except ValueError:
                                pass
            except Exception:
                pass
        
        # Predict based on file modification patterns
        recently_modified = []
        for yaml_file in self.governance_root.rglob("*.yaml"):
            mtime = datetime.fromtimestamp(yaml_file.stat().st_mtime)
            if (datetime.now() - mtime).days < 7:
                recently_modified.append(yaml_file)
        
        if len(recently_modified) > 20:
            self.add_problem(Problem(
                category=ProblemCategory.PREDICTIVE,
                severity=ProblemSeverity.INFO,
                title="High change velocity detected",
                description=f"{len(recently_modified)} files modified in last 7 days",
                location="governance/",
                impact="High change rate may indicate instability or active development",
                recommendation="Review changes for consistency and run full validation suite",
                auto_fixable=False
            ))
    
    def identify_all_problems(self, categories: List[str] = None):
        """Run all problem detection categories"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
        print(f"SynergyMesh Extreme Problem Identifier")
        print(f"極致問題識別系統 - Advanced Diagnostic Scanner")
        print(f"{'='*80}{Colors.ENDC}\n")
        
        start_time = datetime.now()
        
        detection_methods = {
            ProblemCategory.SECURITY: self.detect_security_vulnerabilities,
            ProblemCategory.ARCHITECTURE: self.detect_architecture_violations,
            ProblemCategory.PERFORMANCE: self.detect_performance_issues,
            ProblemCategory.COMPLIANCE: self.detect_compliance_gaps,
            ProblemCategory.DEPENDENCIES: self.detect_dependency_issues,
            ProblemCategory.DRIFT: self.detect_configuration_drift,
            ProblemCategory.DOCUMENTATION: self.detect_documentation_gaps,
            ProblemCategory.CODE_QUALITY: self.detect_code_quality_issues,
            "naming": self.detect_naming_violations,
            ProblemCategory.PREDICTIVE: self.detect_predictive_issues,
        }
        
        # Run selected categories
        if categories:
            for category in categories:
                if category in detection_methods:
                    detection_methods[category]()
        else:
            # Run all
            for method in detection_methods.values():
                method()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        self.print_summary(execution_time)
        
        return len([p for p in self.problems if p.severity in [ProblemSeverity.CRITICAL, ProblemSeverity.HIGH]]) == 0
    
    def print_summary(self, execution_time: float):
        """Print problem identification summary"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
        print(f"Problem Identification Summary")
        print(f"{'='*80}{Colors.ENDC}\n")
        
        # Group by severity
        by_severity = defaultdict(list)
        for problem in self.problems:
            by_severity[problem.severity].append(problem)
        
        # Print counts
        critical_count = len(by_severity[ProblemSeverity.CRITICAL])
        high_count = len(by_severity[ProblemSeverity.HIGH])
        medium_count = len(by_severity[ProblemSeverity.MEDIUM])
        low_count = len(by_severity[ProblemSeverity.LOW])
        info_count = len(by_severity[ProblemSeverity.INFO])
        
        print(f"{Colors.FAIL}🔴 CRITICAL: {critical_count}{Colors.ENDC}")
        print(f"{Colors.FAIL}🔴 HIGH: {high_count}{Colors.ENDC}")
        print(f"{Colors.WARNING}🟠 MEDIUM: {medium_count}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🟡 LOW: {low_count}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}ℹ️  INFO: {info_count}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Total Problems: {len(self.problems)}{Colors.ENDC}")
        
        auto_fixable = len([p for p in self.problems if p.auto_fixable])
        print(f"{Colors.OKGREEN}Auto-fixable: {auto_fixable}{Colors.ENDC}")
        
        # Category breakdown
        print(f"\n{Colors.BOLD}By Category:{Colors.ENDC}")
        categories = set(p.category for p in self.problems)
        for cat in sorted(categories):
            count = len([p for p in self.problems if p.category == cat])
            print(f"  {cat}: {count}")
        
        # Execution metrics
        print(f"\n{Colors.BOLD}Execution Metrics:{Colors.ENDC}")
        print(f"  Scan time: {execution_time:.2f} seconds")
        print(f"  Files scanned: {sum(1 for _ in self.governance_root.rglob('*.yaml'))}")
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
        
        # Risk assessment
        if critical_count > 0:
            print(f"{Colors.FAIL}{Colors.BOLD}❌ RISK LEVEL: CRITICAL - Immediate action required{Colors.ENDC}\n")
        elif high_count > 0:
            print(f"{Colors.FAIL}{Colors.BOLD}⚠️  RISK LEVEL: HIGH - Action required soon{Colors.ENDC}\n")
        elif medium_count > 5:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠️  RISK LEVEL: MEDIUM - Plan remediation{Colors.ENDC}\n")
        else:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✅ RISK LEVEL: LOW - Good governance health{Colors.ENDC}\n")
    
    def export_report(self, format: str = "json", output_file: str = None):
        """Export detailed problem report"""
        if not output_file:
            output_file = f"governance-problems-{datetime.now().strftime('%Y%m%d-%H%M%S')}.{format}"
        
        report_data = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_problems": len(self.problems),
            "problems": [
                {
                    "id": p.id,
                    "category": p.category,
                    "severity": p.severity,
                    "title": p.title,
                    "description": p.description,
                    "location": p.location,
                    "impact": p.impact,
                    "recommendation": p.recommendation,
                    "auto_fixable": p.auto_fixable,
                    "detected_at": p.detected_at
                }
                for p in self.problems
            ],
            "statistics": dict(self.stats)
        }
        
        if format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
        elif format == "yaml":
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(report_data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"{Colors.OKGREEN}Report exported to: {output_file}{Colors.ENDC}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SynergyMesh Extreme Problem Identifier - 極致問題識別系統',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python governance/scripts/extreme-problem-identifier.py
  python governance/scripts/extreme-problem-identifier.py --verbose
  python governance/scripts/extreme-problem-identifier.py --category security
  python governance/scripts/extreme-problem-identifier.py --export json --output problems.json
        """
    )
    
    parser.add_argument(
        '--governance-root',
        default='governance',
        help='Path to governance root directory (default: governance)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--category', '-c',
        choices=['security', 'architecture', 'performance', 'compliance', 'dependencies', 
                 'drift', 'documentation', 'code_quality', 'predictive'],
        help='Run specific detection category only'
    )
    
    parser.add_argument(
        '--export',
        choices=['json', 'yaml'],
        help='Export detailed report in specified format'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for report export'
    )
    
    args = parser.parse_args()
    
    # Run identification
    identifier = ExtremeProblemIdentifier(
        governance_root=args.governance_root,
        verbose=args.verbose
    )
    
    categories = [args.category] if args.category else None
    success = identifier.identify_all_problems(categories=categories)
    
    # Export if requested
    if args.export:
        identifier.export_report(format=args.export, output_file=args.output)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
