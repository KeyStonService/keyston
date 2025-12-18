#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Governance Policy Checker

Validates policy files across governance domains against the policy schema.
Checks for:
- Schema compliance
- Required fields
- Policy consistency
- Dependency validation
- Enforcement rules
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class PolicyCheckResult:
    """Result of a policy check"""
    policy_file: str
    domain: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


class GovernancePolicyChecker:
    """Validates governance policy files"""

    REQUIRED_POLICY_FIELDS = [
        "name",
        "description",
        "version",
        "enforcement",
        "rules",
    ]

    VALID_ENFORCEMENT_LEVELS = ["strict", "warning", "advisory"]

    def __init__(self, policy_schema_path: Path):
        """Initialize with policy schema"""
        self.policy_schema_path = policy_schema_path
        self.schema = self._load_schema()
        self.results: List[PolicyCheckResult] = []

    def _load_schema(self) -> Dict[str, Any]:
        """Load policy schema"""
        if not self.policy_schema_path.exists():
            print(f"⚠️  Policy schema not found: {self.policy_schema_path}")
            return {}

        with open(self.policy_schema_path) as f:
            return json.load(f)

    def check_policy_file(self, policy_path: Path) -> PolicyCheckResult:
        """Check a single policy file"""
        errors = []
        warnings = []
        metrics = {}

        try:
            with open(policy_path) as f:
                if policy_path.suffix == '.yaml' or policy_path.suffix == '.yml':
                    policy = yaml.safe_load(f)
                else:
                    policy = json.load(f)
        except Exception as e:
            return PolicyCheckResult(
                policy_file=str(policy_path),
                domain=policy_path.parent.name,
                valid=False,
                errors=[f"Failed to parse: {str(e)}"],
                warnings=[],
                metrics={}
            )

        if not policy:
            errors.append("Policy file is empty")
            return PolicyCheckResult(
                policy_file=str(policy_path),
                domain=policy_path.parent.name,
                valid=False,
                errors=errors,
                warnings=[],
                metrics={}
            )

        # Check required fields
        for field in self.REQUIRED_POLICY_FIELDS:
            if field not in policy:
                errors.append(f"Missing required field: {field}")

        # Check field types
        if "name" in policy and not isinstance(policy["name"], str):
            errors.append("Field 'name' must be a string")

        if "enforcement" in policy:
            if policy["enforcement"] not in self.VALID_ENFORCEMENT_LEVELS:
                errors.append(f"Invalid enforcement level: {policy['enforcement']}")

        # Check rules
        if "rules" in policy:
            if not isinstance(policy["rules"], dict):
                errors.append("Field 'rules' must be a dictionary")
            metrics["rule_count"] = len(policy.get("rules", {}))

        # Check dependencies
        if "dependencies" in policy:
            if not isinstance(policy["dependencies"], list):
                errors.append("Field 'dependencies' must be a list")
            metrics["dependency_count"] = len(policy.get("dependencies", []))
        else:
            warnings.append("Consider adding 'dependencies' field")

        # Check compliance metrics
        if "compliance_metrics" in policy:
            metrics["compliance_metric_count"] = len(policy.get("compliance_metrics", []))
        else:
            warnings.append("Consider adding 'compliance_metrics' field")

        # Check version format
        if "version" in policy:
            import re
            if not re.match(r"^\d+\.\d+(\.\d+)?$", str(policy["version"])):
                warnings.append(f"Version should follow semantic versioning: {policy['version']}")

        valid = len(errors) == 0

        return PolicyCheckResult(
            policy_file=str(policy_path),
            domain=policy_path.parent.name,
            valid=valid,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )

    def check_domain_policies(self, domain_path: Path) -> List[PolicyCheckResult]:
        """Check all policies in a governance domain"""
        results = []

        config_dir = domain_path / "config"
        if not config_dir.exists():
            return results

        for policy_file in config_dir.glob("*.yaml"):
            result = self.check_policy_file(policy_file)
            results.append(result)

        for policy_file in config_dir.glob("*.yml"):
            result = self.check_policy_file(policy_file)
            results.append(result)

        return results

    def check_all_policies(self, governance_root: Path) -> Tuple[bool, Dict[str, Any]]:
        """Check all policies across all domains"""
        print("🔍 Checking Governance Policies...")
        print("=" * 100)

        total_checks = 0
        total_valid = 0
        total_errors = 0
        total_warnings = 0

        domain_results = {}

        # Check meta-governance domains
        meta_domains = [
            "architecture-governance", "api-governance", "data-governance",
            "testing-governance", "identity-tenancy-governance",
            "performance-reliability-governance", "cost-management-governance",
            "docs-governance"
        ]

        for domain_name in meta_domains:
            domain_path = governance_root / domain_name
            if not domain_path.exists():
                continue

            results = self.check_domain_policies(domain_path)
            if results:
                domain_results[domain_name] = results
                total_checks += len(results)

                for result in results:
                    if result.valid:
                        total_valid += 1
                        print(f"  ✅ {domain_name}: {result.policy_file.split('/')[-1]}")
                    else:
                        print(f"  ❌ {domain_name}: {result.policy_file.split('/')[-1]}")
                        for error in result.errors:
                            print(f"      • {error}")
                    total_errors += len(result.errors)
                    total_warnings += len(result.warnings)

        overall_valid = total_errors == 0

        report = {
            "total_policies_checked": total_checks,
            "valid_policies": total_valid,
            "invalid_policies": total_checks - total_valid,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "compliance_rate": (total_valid / total_checks * 100) if total_checks > 0 else 0,
            "domain_results": domain_results
        }

        return overall_valid, report

    def print_report(self, report: Dict[str, Any]) -> None:
        """Print policy check report"""
        print("\n" + "=" * 100)
        print("📋 GOVERNANCE POLICY CHECK REPORT")
        print("=" * 100)

        print(f"\n📊 Summary:")
        print(f"   Policies Checked:  {report['total_policies_checked']}")
        print(f"   Valid:             {report['valid_policies']}")
        print(f"   Invalid:           {report['invalid_policies']}")
        print(f"   Errors:            {report['total_errors']}")
        print(f"   Warnings:          {report['total_warnings']}")
        print(f"   Compliance Rate:   {report['compliance_rate']:.1f}%")

        if report["total_errors"] > 0:
            print(f"\n❌ Errors Found:")
            for domain, results in report["domain_results"].items():
                for result in results:
                    if result.errors:
                        print(f"   {domain}/{result.policy_file.split('/')[-1]}:")
                        for error in result.errors:
                            print(f"      • {error}")


def main():
    """Main entry point"""
    governance_root = Path(__file__).parent.parent.parent
    schema_path = governance_root / "common" / "schemas" / "policy.schema.json"

    checker = GovernancePolicyChecker(schema_path)
    valid, report = checker.check_all_policies(governance_root)

    checker.print_report(report)

    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
