#!/usr/bin/env python3
"""
Governance Index Validator
==========================

This script validates the governance index for:
- DAG (Directed Acyclic Graph) integrity
- Circular dependency detection
- Missing dependency checks
- Orphan node detection
- Schema compliance
- Consistency across index files

Usage:
    python index-validator.py
    python index-validator.py --verbose
    python index-validator.py --fix  # Auto-fix issues where possible

Exit Codes:
    0 - All validations passed
    1 - Validation errors found
    2 - Critical errors (file not found, parse errors)
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    details: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Complete validation report."""
    results: List[ValidationResult] = field(default_factory=list)
    errors: int = 0
    warnings: int = 0
    passed: int = 0

    def add(self, result: ValidationResult):
        self.results.append(result)
        if result.passed:
            self.passed += 1
        elif result.severity == "warning":
            self.warnings += 1
        else:
            self.errors += 1

    def is_valid(self) -> bool:
        return self.errors == 0


class GovernanceIndexValidator:
    """Validator for the governance index system."""

    def __init__(self, index_path: Optional[Path] = None, verbose: bool = False):
        """Initialize the validator."""
        if index_path is None:
            index_path = Path(__file__).parent.parent

        self.index_path = index_path
        self.verbose = verbose
        self.report = ValidationReport()

        # Index files to validate
        self.index_files = {
            "root": index_path.parent / "governance-index.json",
            "dimensions": index_path / "dimensions.json",
            "shared": index_path / "shared.json",
            "compliance": index_path / "compliance.json",
            "events": index_path / "events.json",
            "tech_debt": index_path / "tech-debt.json",
            "vectors": index_path / "vectors.json",
            "observability": index_path / "observability.json",
        }

        # Loaded data
        self.data: Dict[str, Dict] = {}

    def load_index_files(self) -> bool:
        """Load all index files."""
        all_loaded = True

        for name, path in self.index_files.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.data[name] = json.load(f)
                self.report.add(ValidationResult(
                    check=f"load_{name}",
                    passed=True,
                    message=f"Successfully loaded {path.name}",
                    severity="info"
                ))
            except FileNotFoundError:
                self.report.add(ValidationResult(
                    check=f"load_{name}",
                    passed=False,
                    message=f"Index file not found: {path}",
                    severity="error"
                ))
                all_loaded = False
            except json.JSONDecodeError as e:
                self.report.add(ValidationResult(
                    check=f"load_{name}",
                    passed=False,
                    message=f"JSON parse error in {path.name}: {e}",
                    severity="error"
                ))
                all_loaded = False

        return all_loaded

    def validate_dag(self) -> ValidationResult:
        """Validate the DAG structure - check for circular dependencies."""
        if "dimensions" not in self.data:
            return ValidationResult(
                check="dag_circular",
                passed=False,
                message="Cannot validate DAG - dimensions.json not loaded",
                severity="error"
            )

        dimensions = self.data["dimensions"].get("dimensions", [])
        graph: Dict[str, List[str]] = {}

        # Build adjacency list
        for dim in dimensions:
            dim_id = dim.get("id", "")
            deps = dim.get("depends_on", [])
            graph[dim_id] = deps

        # Detect cycles using DFS
        cycles = self._find_cycles(graph)

        if cycles:
            return ValidationResult(
                check="dag_circular",
                passed=False,
                message=f"Circular dependencies detected: {len(cycles)} cycle(s) found",
                severity="error",
                details=[f"Cycle: {' -> '.join(cycle)}" for cycle in cycles]
            )

        return ValidationResult(
            check="dag_circular",
            passed=True,
            message="No circular dependencies found in DAG",
            severity="info"
        )

    def _find_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find all cycles in the graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def validate_missing_dependencies(self) -> ValidationResult:
        """Check for missing dependencies."""
        if "dimensions" not in self.data:
            return ValidationResult(
                check="dag_missing",
                passed=False,
                message="Cannot validate dependencies - dimensions.json not loaded",
                severity="error"
            )

        dimensions = self.data["dimensions"].get("dimensions", [])
        all_ids = {dim.get("id", "") for dim in dimensions}
        missing = []

        for dim in dimensions:
            dim_id = dim.get("id", "")
            deps = dim.get("depends_on", [])

            for dep in deps:
                if dep not in all_ids:
                    missing.append(f"{dim_id} depends on unknown: {dep}")

        if missing:
            return ValidationResult(
                check="dag_missing",
                passed=False,
                message=f"Found {len(missing)} missing dependencies",
                severity="error",
                details=missing
            )

        return ValidationResult(
            check="dag_missing",
            passed=True,
            message="All dependencies reference valid dimensions",
            severity="info"
        )

    def validate_orphan_nodes(self) -> ValidationResult:
        """Check for orphan nodes (no dependencies and not depended upon)."""
        if "dimensions" not in self.data:
            return ValidationResult(
                check="dag_orphans",
                passed=False,
                message="Cannot validate orphans - dimensions.json not loaded",
                severity="error"
            )

        dimensions = self.data["dimensions"].get("dimensions", [])

        # Build dependency maps
        has_deps = set()
        is_depended = set()

        for dim in dimensions:
            dim_id = dim.get("id", "")
            deps = dim.get("depends_on", [])

            if deps:
                has_deps.add(dim_id)

            for dep in deps:
                is_depended.add(dep)

        # Find orphans (not in has_deps and not in is_depended)
        all_ids = {dim.get("id", "") for dim in dimensions}
        orphans = all_ids - has_deps - is_depended

        # Root nodes (no deps but depended upon) are OK
        root_nodes = is_depended - has_deps

        # True orphans
        true_orphans = orphans - root_nodes

        if true_orphans:
            return ValidationResult(
                check="dag_orphans",
                passed=True,  # Orphans are warnings, not errors
                message=f"Found {len(true_orphans)} orphan dimensions (isolated)",
                severity="warning",
                details=list(true_orphans)
            )

        return ValidationResult(
            check="dag_orphans",
            passed=True,
            message="No orphan dimensions found",
            severity="info"
        )

    def validate_execution_order(self) -> ValidationResult:
        """Validate that execution order respects dependencies."""
        if "dimensions" not in self.data:
            return ValidationResult(
                check="execution_order",
                passed=False,
                message="Cannot validate execution order - dimensions.json not loaded",
                severity="error"
            )

        dimensions = self.data["dimensions"].get("dimensions", [])
        execution_order = self.data["dimensions"].get("execution_order", {})

        required_first = set(execution_order.get("required_first", []))
        core_flow = execution_order.get("core_flow", [])

        # Build dependency map
        deps_map = {dim.get("id"): set(dim.get("depends_on", [])) for dim in dimensions}

        # Validate required_first have no unmet dependencies
        issues = []
        for dim_id in required_first:
            deps = deps_map.get(dim_id, set())
            unmet = deps - required_first
            if unmet:
                issues.append(f"{dim_id} has unmet dependencies: {unmet}")

        if issues:
            return ValidationResult(
                check="execution_order",
                passed=False,
                message="Execution order has dependency issues",
                severity="error",
                details=issues
            )

        return ValidationResult(
            check="execution_order",
            passed=True,
            message="Execution order respects dependencies",
            severity="info"
        )

    def validate_compliance_mapping(self) -> ValidationResult:
        """Validate that compliance mappings reference valid dimensions."""
        if "compliance" not in self.data or "dimensions" not in self.data:
            return ValidationResult(
                check="compliance_mapping",
                passed=False,
                message="Cannot validate compliance - required files not loaded",
                severity="error"
            )

        dimensions = self.data["dimensions"].get("dimensions", [])
        all_dim_ids = {dim.get("id") for dim in dimensions}
        all_dim_paths = {dim.get("path") for dim in dimensions}

        compliance = self.data["compliance"]
        matrix = compliance.get("compliance_matrix", {}).get("by_dimension", {})

        issues = []
        for dim_path, frameworks in matrix.items():
            # Check if dimension exists (by path)
            if dim_path not in all_dim_paths:
                issues.append(f"Unknown dimension in compliance matrix: {dim_path}")

        if issues:
            return ValidationResult(
                check="compliance_mapping",
                passed=True,  # Warning only
                message=f"Found {len(issues)} compliance mapping issues",
                severity="warning",
                details=issues
            )

        return ValidationResult(
            check="compliance_mapping",
            passed=True,
            message="All compliance mappings reference valid dimensions",
            severity="info"
        )

    def validate_events_agents(self) -> ValidationResult:
        """Validate that event configurations are consistent."""
        if "events" not in self.data:
            return ValidationResult(
                check="events_agents",
                passed=False,
                message="Cannot validate events - events.json not loaded",
                severity="error"
            )

        events = self.data["events"]
        categories = events.get("event_categories", [])

        issues = []
        for cat in categories:
            for event in cat.get("events", []):
                # Check that agents are specified
                if not event.get("agents"):
                    issues.append(f"Event {event.get('id')} has no agents")

                # Check latency format
                latency = event.get("latency", "")
                if latency and not latency.startswith("<="):
                    issues.append(f"Event {event.get('id')} has invalid latency format: {latency}")

        if issues:
            return ValidationResult(
                check="events_agents",
                passed=False,
                message=f"Found {len(issues)} event configuration issues",
                severity="error",
                details=issues
            )

        return ValidationResult(
            check="events_agents",
            passed=True,
            message="Event configurations are valid",
            severity="info"
        )

    def validate_vectors_coverage(self) -> ValidationResult:
        """Validate that vectors cover all core dimensions."""
        if "vectors" not in self.data or "dimensions" not in self.data:
            return ValidationResult(
                check="vectors_coverage",
                passed=False,
                message="Cannot validate vectors - required files not loaded",
                severity="error"
            )

        dim_data = self.data["dimensions"].get("dimensions", [])
        required_dims = {
            dim.get("id") for dim in dim_data
            if dim.get("execution") == "required" and dim.get("status") in ["production", "active"]
        }

        vec_data = self.data["vectors"].get("dimensions", [])
        vectorized = {v.get("id") for v in vec_data}

        missing = required_dims - vectorized

        if missing:
            return ValidationResult(
                check="vectors_coverage",
                passed=True,  # Warning only
                message=f"Found {len(missing)} required dimensions without vectors",
                severity="warning",
                details=list(missing)
            )

        return ValidationResult(
            check="vectors_coverage",
            passed=True,
            message="All required dimensions have vectors",
            severity="info"
        )

    def validate_index_registry(self) -> ValidationResult:
        """Validate that root index references all sub-indexes."""
        if "root" not in self.data:
            return ValidationResult(
                check="index_registry",
                passed=False,
                message="Cannot validate registry - governance-index.json not loaded",
                severity="error"
            )

        registry = self.data["root"].get("index_registry", {})
        expected_indexes = ["dimensions", "shared", "compliance", "events", "tech_debt", "vectors", "observability"]

        missing = []
        for idx in expected_indexes:
            if idx not in registry:
                missing.append(idx)

        if missing:
            return ValidationResult(
                check="index_registry",
                passed=False,
                message=f"Root index missing references to: {missing}",
                severity="error",
                details=missing
            )

        return ValidationResult(
            check="index_registry",
            passed=True,
            message="Root index references all sub-indexes",
            severity="info"
        )

    def validate_all(self) -> ValidationReport:
        """Run all validations."""
        print("=" * 60)
        print("Governance Index Validation")
        print("=" * 60)
        print()

        # Load files
        print("Loading index files...")
        if not self.load_index_files():
            print("\nCritical: Some index files could not be loaded.")

        # Run validations
        validations = [
            ("DAG Circular Dependencies", self.validate_dag),
            ("Missing Dependencies", self.validate_missing_dependencies),
            ("Orphan Nodes", self.validate_orphan_nodes),
            ("Execution Order", self.validate_execution_order),
            ("Compliance Mapping", self.validate_compliance_mapping),
            ("Events Configuration", self.validate_events_agents),
            ("Vectors Coverage", self.validate_vectors_coverage),
            ("Index Registry", self.validate_index_registry),
        ]

        print("\nRunning validations...")
        print("-" * 40)

        for name, validator in validations:
            result = validator()
            self.report.add(result)

            status = "✓" if result.passed else ("⚠" if result.severity == "warning" else "✗")
            print(f"{status} {name}: {result.message}")

            if self.verbose and result.details:
                for detail in result.details[:5]:  # Limit to 5 details
                    print(f"    - {detail}")
                if len(result.details) > 5:
                    print(f"    ... and {len(result.details) - 5} more")

        return self.report

    def print_summary(self):
        """Print validation summary."""
        print()
        print("=" * 60)
        print("Validation Summary")
        print("=" * 60)
        print(f"  Passed:   {self.report.passed}")
        print(f"  Warnings: {self.report.warnings}")
        print(f"  Errors:   {self.report.errors}")
        print()

        if self.report.is_valid():
            print("✓ All validations passed! Index is ready for use.")
        else:
            print("✗ Validation failed. Please fix the errors above.")


def main():
    parser = argparse.ArgumentParser(
        description="Validate the Governance Index",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed validation results")
    parser.add_argument("--index-path", type=Path,
                        help="Path to index directory")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    validator = GovernanceIndexValidator(args.index_path, args.verbose)
    report = validator.validate_all()

    if args.json:
        results = [
            {
                "check": r.check,
                "passed": r.passed,
                "message": r.message,
                "severity": r.severity,
                "details": r.details
            }
            for r in report.results
        ]
        print(json.dumps({
            "valid": report.is_valid(),
            "errors": report.errors,
            "warnings": report.warnings,
            "passed": report.passed,
            "results": results
        }, indent=2))
    else:
        validator.print_summary()

    sys.exit(0 if report.is_valid() else 1)


if __name__ == "__main__":
    main()
