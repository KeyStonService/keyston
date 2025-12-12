#!/usr/bin/env python3
"""
Technical Debt Management System
=================================

Comprehensive system for identifying, tracking, and resolving technical debt
in the SynergyMesh project. Provides automated detection, prioritization,
and remediation strategies.

Core Functionality
------------------
1. **Debt Detection**: Automatically scan codebase for technical debt indicators
2. **Debt Classification**: Categorize debt by type, severity, and impact
3. **Debt Tracking**: Maintain debt registry with metrics and trends
4. **Remediation Planning**: Generate actionable remediation strategies
5. **Progress Monitoring**: Track debt reduction over time

Debt Categories
---------------
- Code Complexity: High cyclomatic complexity, long functions
- Documentation Debt: Missing docstrings, outdated comments
- Test Debt: Low coverage, missing tests
- Dependency Debt: Outdated dependencies, security vulnerabilities
- Architecture Debt: Violation of design principles, circular dependencies
- Performance Debt: Inefficient algorithms, memory leaks
- Security Debt: Known vulnerabilities, weak authentication
- Maintenance Debt: Deprecated APIs, compatibility issues

Author: SynergyMesh Governance Team
Version: 1.0.0
Date: 2025-12-12
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import ast


class DebtType(Enum):
    """Types of technical debt"""
    CODE_COMPLEXITY = "code_complexity"
    DOCUMENTATION = "documentation"
    TEST_COVERAGE = "test_coverage"
    DEPENDENCY = "dependency"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTENANCE = "maintenance"


class DebtSeverity(Enum):
    """Severity levels for technical debt"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DebtItem:
    """
    Represents a single technical debt item.
    
    Attributes:
        id: Unique identifier
        type: Category of debt
        severity: Impact severity
        file_path: File where debt exists
        line_number: Line number (if applicable)
        description: Description of the debt
        estimated_effort_hours: Estimated hours to resolve
        created_date: When debt was identified
        resolved: Whether debt has been resolved
        resolution_notes: Notes on how debt was resolved
    """
    id: str
    type: DebtType
    severity: DebtSeverity
    file_path: str
    line_number: Optional[int] = None
    description: str = ""
    estimated_effort_hours: float = 0.0
    created_date: float = field(default_factory=time.time)
    resolved: bool = False
    resolution_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['type'] = self.type.value
        result['severity'] = self.severity.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DebtItem':
        """Create from dictionary"""
        data['type'] = DebtType(data['type'])
        data['severity'] = DebtSeverity(data['severity'])
        return cls(**data)


class TechnicalDebtManager:
    """
    Main class for managing technical debt.
    
    Provides comprehensive debt tracking, analysis, and remediation.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize the technical debt manager.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.debt_items: List[DebtItem] = []
        self.debt_counter = 0
        
    def scan_for_debt(self, directories: Optional[List[str]] = None) -> int:
        """
        Scan project for technical debt.
        
        Args:
            directories: List of directories to scan (default: all)
        
        Returns:
            Number of debt items found
        """
        if directories is None:
            directories = ['governance']
        
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.rglob('*.py'):
                self._scan_python_file(file_path)
            
            for file_path in dir_path.rglob('*.md'):
                self._scan_markdown_file(file_path)
        
        return len(self.debt_items)
    
    def _scan_python_file(self, file_path: Path) -> None:
        """Scan Python file for debt indicators"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for debt markers (TODO, FIXME, etc.)
            self._detect_debt_markers(file_path, content)
            
            # Check for missing docstrings
            self._detect_missing_docstrings(file_path, content)
            
            # Check for code complexity
            self._detect_complexity(file_path, content)
            
        except Exception as e:
            pass  # Skip files that can't be read
    
    def _scan_markdown_file(self, file_path: Path) -> None:
        """Scan Markdown file for debt indicators"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for debt markers
            self._detect_debt_markers(file_path, content)
            
        except Exception:
            pass
    
    def _detect_debt_markers(self, file_path: Path, content: str) -> None:
        """Detect TODO, FIXME, HACK markers"""
        markers = {
            'TODO': (DebtType.MAINTENANCE, DebtSeverity.LOW),
            'FIXME': (DebtType.MAINTENANCE, DebtSeverity.MEDIUM),
            'HACK': (DebtType.CODE_COMPLEXITY, DebtSeverity.MEDIUM),
            'XXX': (DebtType.MAINTENANCE, DebtSeverity.HIGH),
            'DEPRECATED': (DebtType.MAINTENANCE, DebtSeverity.HIGH)
        }
        
        for line_num, line in enumerate(content.split('\n'), 1):
            for marker, (debt_type, severity) in markers.items():
                if marker in line.upper():
                    # Extract comment text
                    match = re.search(r'#\s*' + marker + r'[:\s]*(.*)', line, re.IGNORECASE)
                    description = match.group(1).strip() if match else f"{marker} found"
                    
                    debt_id = f"DEBT-{self.debt_counter:04d}"
                    self.debt_counter += 1
                    
                    self.debt_items.append(DebtItem(
                        id=debt_id,
                        type=debt_type,
                        severity=severity,
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=line_num,
                        description=f"{marker}: {description}",
                        estimated_effort_hours=1.0 if severity == DebtSeverity.LOW else 4.0
                    ))
    
    def _detect_missing_docstrings(self, file_path: Path, content: str) -> None:
        """Detect functions/classes missing docstrings"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if not docstring and not node.name.startswith('_'):
                        debt_id = f"DEBT-{self.debt_counter:04d}"
                        self.debt_counter += 1
                        
                        self.debt_items.append(DebtItem(
                            id=debt_id,
                            type=DebtType.DOCUMENTATION,
                            severity=DebtSeverity.LOW,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            description=f"Missing docstring for {node.__class__.__name__}: {node.name}",
                            estimated_effort_hours=0.5
                        ))
        except Exception:
            pass
    
    def _detect_complexity(self, file_path: Path, content: str) -> None:
        """Detect overly complex functions"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Simple complexity metric: count branches
                    complexity = self._calculate_complexity(node)
                    
                    if complexity > 10:  # McCabe complexity threshold
                        debt_id = f"DEBT-{self.debt_counter:04d}"
                        self.debt_counter += 1
                        
                        severity = DebtSeverity.HIGH if complexity > 20 else DebtSeverity.MEDIUM
                        
                        self.debt_items.append(DebtItem(
                            id=debt_id,
                            type=DebtType.CODE_COMPLEXITY,
                            severity=severity,
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            description=f"High complexity ({complexity}) in function: {node.name}",
                            estimated_effort_hours=complexity * 0.5
                        ))
        except Exception:
            pass
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def get_debt_by_severity(self) -> Dict[str, List[DebtItem]]:
        """Group debt items by severity"""
        result = defaultdict(list)
        for item in self.debt_items:
            if not item.resolved:
                result[item.severity.value].append(item)
        return dict(result)
    
    def get_debt_by_type(self) -> Dict[str, List[DebtItem]]:
        """Group debt items by type"""
        result = defaultdict(list)
        for item in self.debt_items:
            if not item.resolved:
                result[item.type.value].append(item)
        return dict(result)
    
    def get_top_debt_files(self, limit: int = 10) -> List[tuple]:
        """Get files with most debt"""
        file_debt_count = defaultdict(int)
        
        for item in self.debt_items:
            if not item.resolved:
                file_debt_count[item.file_path] += 1
        
        sorted_files = sorted(file_debt_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_files[:limit]
    
    def calculate_total_effort(self) -> float:
        """Calculate total effort hours to resolve all debt"""
        return sum(item.estimated_effort_hours for item in self.debt_items if not item.resolved)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive debt report"""
        total_debt = len([item for item in self.debt_items if not item.resolved])
        resolved_debt = len([item for item in self.debt_items if item.resolved])
        
        by_severity = self.get_debt_by_severity()
        by_type = self.get_debt_by_type()
        
        report = {
            'timestamp': time.time(),
            'summary': {
                'total_debt_items': total_debt,
                'resolved_items': resolved_debt,
                'resolution_rate': resolved_debt / len(self.debt_items) if self.debt_items else 0,
                'total_estimated_effort_hours': self.calculate_total_effort()
            },
            'by_severity': {
                severity: len(items) for severity, items in by_severity.items()
            },
            'by_type': {
                debt_type: len(items) for debt_type, items in by_type.items()
            },
            'top_debt_files': [
                {'file': file, 'debt_count': count}
                for file, count in self.get_top_debt_files()
            ],
            'critical_items': [
                item.to_dict() for item in self.debt_items
                if item.severity == DebtSeverity.CRITICAL and not item.resolved
            ]
        }
        
        return report
    
    def generate_remediation_plan(self) -> Dict[str, Any]:
        """Generate actionable remediation plan"""
        critical = [item for item in self.debt_items 
                   if item.severity == DebtSeverity.CRITICAL and not item.resolved]
        high = [item for item in self.debt_items 
               if item.severity == DebtSeverity.HIGH and not item.resolved]
        
        plan = {
            'sprint_1_immediate': {
                'description': 'Address critical and high-severity issues',
                'items': [item.to_dict() for item in (critical + high)[:10]],
                'estimated_hours': sum(item.estimated_effort_hours for item in (critical + high)[:10])
            },
            'sprint_2_important': {
                'description': 'Address medium-severity issues',
                'items': [item.to_dict() for item in self.debt_items 
                         if item.severity == DebtSeverity.MEDIUM and not item.resolved][:15],
                'estimated_hours': sum(item.estimated_effort_hours for item in self.debt_items 
                                     if item.severity == DebtSeverity.MEDIUM and not item.resolved)
            },
            'backlog': {
                'description': 'Address low-severity issues',
                'items_count': len([item for item in self.debt_items 
                                   if item.severity == DebtSeverity.LOW and not item.resolved]),
                'estimated_hours': sum(item.estimated_effort_hours for item in self.debt_items 
                                     if item.severity == DebtSeverity.LOW and not item.resolved)
            }
        }
        
        return plan
    
    def export_to_json(self, filepath: str) -> None:
        """Export debt registry to JSON"""
        data = {
            'debt_items': [item.to_dict() for item in self.debt_items],
            'report': self.generate_report(),
            'remediation_plan': self.generate_remediation_plan()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_from_json(self, filepath: str) -> None:
        """Import debt registry from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.debt_items = [DebtItem.from_dict(item) for item in data['debt_items']]
        self.debt_counter = len(self.debt_items)
    
    def mark_resolved(self, debt_id: str, resolution_notes: str = "") -> bool:
        """Mark a debt item as resolved"""
        for item in self.debt_items:
            if item.id == debt_id:
                item.resolved = True
                item.resolution_notes = resolution_notes
                return True
        return False


# Example usage
if __name__ == "__main__":
    import sys
    
    # Detect project root
    project_root = Path.cwd()
    while not (project_root / ".git").exists() and project_root.parent != project_root:
        project_root = project_root.parent
    
    print("=" * 70)
    print("  TECHNICAL DEBT MANAGEMENT SYSTEM")
    print("=" * 70)
    print(f"\nProject Root: {project_root}\n")
    
    # Initialize manager
    manager = TechnicalDebtManager(project_root)
    
    # Scan for debt
    print("🔍 Scanning for technical debt...")
    debt_count = manager.scan_for_debt(['governance'])
    print(f"✅ Found {debt_count} debt items\n")
    
    # Generate report
    print("📊 Generating report...")
    report = manager.generate_report()
    
    print(f"\n📈 Summary:")
    print(f"  Total Debt Items: {report['summary']['total_debt_items']}")
    print(f"  Estimated Effort: {report['summary']['total_estimated_effort_hours']:.1f} hours")
    
    print(f"\n🔥 By Severity:")
    for severity, count in report['by_severity'].items():
        print(f"  {severity}: {count} items")
    
    print(f"\n📁 By Type:")
    for debt_type, count in report['by_type'].items():
        print(f"  {debt_type}: {count} items")
    
    print(f"\n🎯 Top Debt Files:")
    for file_info in report['top_debt_files'][:5]:
        print(f"  {file_info['file']}: {file_info['debt_count']} items")
    
    # Generate remediation plan
    print(f"\n🛠️  Remediation Plan:")
    plan = manager.generate_remediation_plan()
    print(f"  Sprint 1 (Immediate): {len(plan['sprint_1_immediate']['items'])} items, "
          f"{plan['sprint_1_immediate']['estimated_hours']:.1f} hours")
    print(f"  Sprint 2 (Important): {len(plan['sprint_2_important']['items'])} items, "
          f"{plan['sprint_2_important']['estimated_hours']:.1f} hours")
    print(f"  Backlog: {plan['backlog']['items_count']} items, "
          f"{plan['backlog']['estimated_hours']:.1f} hours")
    
    # Export
    output_file = project_root / "governance" / "technical-debt-report.json"
    manager.export_to_json(str(output_file))
    print(f"\n💾 Report exported to: {output_file}")
    
    print("\n" + "=" * 70)
    print("  ✅ TECHNICAL DEBT ANALYSIS COMPLETE")
    print("=" * 70 + "\n")
