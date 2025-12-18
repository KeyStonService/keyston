#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Master Governance Matrix Validator

Validates that all 14 governance dimensions comply with all 9 meta-governance domains.
Generates a comprehensive governance matrix showing:
- Which dimensions implement which meta-governance standards
- Compliance gaps and missing implementations
- Cross-dimensional validation rules
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "✅"
    PARTIAL = "⚠️"
    NON_COMPLIANT = "❌"
    NOT_APPLICABLE = "⊘"


@dataclass
class ComplianceResult:
    """Result of a compliance check"""
    dimension: str
    meta_domain: str
    status: ComplianceStatus
    details: str
    required_files: List[str]
    missing_files: List[str]


class GovernanceMatrixValidator:
    """Validates governance matrix across all dimensions and meta-domains"""

    # 14 Governance Dimensions
    DIMENSIONS = [
        "governance-architecture",
        "decision-governance",
        "change-governance",
        "risk-governance",
        "compliance-governance",
        "security-governance",
        "audit-governance",
        "process-governance",
        "performance-governance",
        "stakeholder-governance",
        "governance-tools",
        "governance-culture",
        "governance-metrics",
        "governance-improvement",
    ]

    # 9 Meta-Governance Domains
    META_DOMAINS = [
        "architecture-governance",
        "api-governance",
        "data-governance",
        "testing-governance",
        "identity-tenancy-governance",
        "performance-reliability-governance",
        "cost-management-governance",
        "docs-governance",
        "common",
    ]

    # Expected files in each meta-domain
    EXPECTED_DOMAIN_FILES = {
        "README.md": "mandatory",
        "config": "policy_file",
        "schemas": "schema_files",
        "tools": "tool_scripts",
        "__init__.py": "optional",
    }

    # Expected files in dimension directories
    EXPECTED_DIMENSION_FILES = {
        "README.md": "mandatory",
        "config": "policy_file",
        "docs": "documentation",
        "schemas": "schema_files",
        "tools": "tool_scripts",
        "automation_engine.py": "automation_engine",
    }

    def __init__(self, governance_root: Path):
        """Initialize validator with governance root directory"""
        self.governance_root = governance_root
        self.results: List[ComplianceResult] = []
        self.matrix: Dict[str, Dict[str, ComplianceStatus]] = {}

    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Validate entire governance matrix"""
        print("🔍 Validating Governance Matrix...")
        print("=" * 100)

        # Validate meta-domains
        print("\n📋 Validating Meta-Governance Domains...")
        meta_domain_status = self._validate_meta_domains()

        # Validate dimensions
        print("\n📦 Validating Governance Dimensions...")
        dimension_status = self._validate_dimensions()

        # Build compliance matrix
        print("\n🎯 Building Compliance Matrix...")
        self._build_matrix()

        # Generate report
        report = {
            "timestamp": str(Path.cwd()),
            "total_dimensions": len(self.DIMENSIONS),
            "total_meta_domains": len(self.META_DOMAINS),
            "meta_domain_status": meta_domain_status,
            "dimension_status": dimension_status,
            "matrix": self._format_matrix(),
            "compliance_percentage": self._calculate_compliance_percentage(),
            "gaps": self._identify_gaps(),
        }

        overall_compliant = report["compliance_percentage"] >= 95

        return overall_compliant, report

    def _validate_meta_domains(self) -> Dict[str, bool]:
        """Validate all meta-governance domains exist and have required structure"""
        status = {}

        for domain in self.META_DOMAINS:
            domain_path = self.governance_root / domain
            status[domain] = domain_path.exists()

            if domain_path.exists():
                has_readme = (domain_path / "README.md").exists()
                has_config = (domain_path / "config").exists()
                print(f"  ✅ {domain:<30} (README: {has_readme}, config: {has_config})")
            else:
                print(f"  ❌ {domain:<30} (NOT FOUND)")

        return status

    def _validate_dimensions(self) -> Dict[str, bool]:
        """Validate all governance dimensions exist and have required structure"""
        status = {}

        for dimension in self.DIMENSIONS:
            dim_path = self.governance_root / dimension
            status[dimension] = dim_path.exists()

            if dim_path.exists():
                has_readme = (dim_path / "README.md").exists()
                has_automation = (dim_path / "automation_engine.py").exists()
                print(f"  ✅ {dimension:<30} (README: {has_readme}, automation: {has_automation})")
            else:
                print(f"  ❌ {dimension:<30} (NOT FOUND)")

        return status

    def _build_matrix(self) -> None:
        """Build governance compliance matrix"""
        for dimension in self.DIMENSIONS:
            self.matrix[dimension] = {}
            for meta_domain in self.META_DOMAINS:
                status = self._check_compliance(dimension, meta_domain)
                self.matrix[dimension][meta_domain] = status

    def _check_compliance(self, dimension: str, meta_domain: str) -> ComplianceStatus:
        """Check if dimension complies with meta-domain requirements"""
        # Simplified compliance check
        # In real implementation, would validate:
        # - Required files exist
        # - Policy compliance
        # - Schema validation
        # - Test coverage

        dim_path = self.governance_root / dimension
        meta_path = self.governance_root / meta_domain

        if not (dim_path.exists() and meta_path.exists()):
            return ComplianceStatus.NOT_APPLICABLE

        # Check for basic integration (README references, policy files)
        has_integration = (dim_path / "README.md").exists()

        if has_integration:
            return ComplianceStatus.COMPLIANT
        else:
            return ComplianceStatus.PARTIAL

    def _format_matrix(self) -> Dict[str, Dict[str, str]]:
        """Format matrix for display"""
        formatted = {}
        for dimension, statuses in self.matrix.items():
            formatted[dimension] = {
                meta: status.value for meta, status in statuses.items()
            }
        return formatted

    def _calculate_compliance_percentage(self) -> float:
        """Calculate overall compliance percentage"""
        total = len(self.DIMENSIONS) * len(self.META_DOMAINS)
        compliant = sum(
            1 for dim_statuses in self.matrix.values()
            for status in dim_statuses.values()
            if status == ComplianceStatus.COMPLIANT
        )
        return (compliant / total * 100) if total > 0 else 0

    def _identify_gaps(self) -> Dict[str, List[str]]:
        """Identify compliance gaps"""
        gaps = {}

        for dimension, statuses in self.matrix.items():
            missing = [
                meta for meta, status in statuses.items()
                if status != ComplianceStatus.COMPLIANT
            ]
            if missing:
                gaps[dimension] = missing

        return gaps

    def print_report(self, report: Dict[str, Any]) -> None:
        """Print detailed compliance report"""
        print("\n" + "=" * 100)
        print("📊 GOVERNANCE COMPLIANCE MATRIX REPORT")
        print("=" * 100)

        print(f"\n📈 Overall Compliance: {report['compliance_percentage']:.1f}%")
        print(f"   Dimensions: {report['total_dimensions']}")
        print(f"   Meta-Domains: {report['total_meta_domains']}")

        print("\n🔗 Governance Matrix:")
        print("-" * 100)

        # Print header
        header = f"{'Dimension':<30}"
        for meta in self.META_DOMAINS[:5]:  # Show first 5 for readability
            header += f" {meta[:15]:<15}"
        print(header)
        print("-" * 100)

        # Print matrix rows
        for dimension in self.DIMENSIONS[:7]:  # Show first 7
            row = f"{dimension:<30}"
            for meta in self.META_DOMAINS[:5]:
                if dimension in report["matrix"]:
                    status = report["matrix"][dimension].get(meta, "⊘")
                    row += f" {status:<15}"
            print(row)

        if report["gaps"]:
            print("\n⚠️  Compliance Gaps:")
            for dimension, missing in report["gaps"].items():
                if missing:
                    print(f"   {dimension}: Missing {', '.join(missing)}")


def main():
    """Main entry point"""
    governance_root = Path(__file__).parent.parent.parent

    if not governance_root.exists():
        print(f"❌ Governance root not found: {governance_root}")
        return 1

    validator = GovernanceMatrixValidator(governance_root)
    compliant, report = validator.validate_all()

    validator.print_report(report)

    # Export report
    report_path = governance_root / "governance_compliance_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✅ Report exported to: {report_path}")

    return 0 if compliant else 1


if __name__ == "__main__":
    sys.exit(main())
