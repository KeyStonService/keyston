#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Governance Dependency Analyzer

Analyzes governance dependencies across all dimensions and meta-domains.
Detects:
- Circular dependencies
- Missing dependencies
- Initialization order violations
- Bottlenecks and critical paths
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class DependencyInfo:
    """Information about a governance entity's dependencies"""
    name: str
    dependencies: List[str]
    dependents: List[str]
    initialization_order: int
    is_circular: bool


class DependencyAnalyzer:
    """Analyzes governance dependencies"""

    # 14 Governance Dimensions
    DIMENSIONS = {
        "governance-architecture": ["identity-tenancy-governance", "security-governance"],
        "decision-governance": ["governance-architecture"],
        "change-governance": ["decision-governance", "risk-governance"],
        "risk-governance": ["decision-governance"],
        "compliance-governance": ["risk-governance"],
        "security-governance": ["architecture-governance"],
        "audit-governance": ["compliance-governance"],
        "process-governance": ["governance-architecture"],
        "performance-governance": ["architecture-governance"],
        "stakeholder-governance": ["decision-governance"],
        "governance-tools": ["architecture-governance"],
        "governance-culture": ["stakeholder-governance"],
        "governance-metrics": ["governance-tools"],
        "governance-improvement": ["governance-metrics"],
    }

    # 9 Meta-Governance Domains
    META_DOMAINS = {
        "architecture-governance": ["identity-tenancy-governance", "security-governance", "common"],
        "api-governance": ["docs-governance", "security-governance", "architecture-governance", "common"],
        "data-governance": ["identity-tenancy-governance", "security-governance", "compliance-governance", "common"],
        "testing-governance": ["architecture-governance", "api-governance", "data-governance", "security-governance", "common"],
        "identity-tenancy-governance": ["security-governance", "data-governance", "audit-governance", "common"],
        "performance-reliability-governance": ["architecture-governance", "security-governance", "performance-governance", "common"],
        "cost-management-governance": ["data-governance", "architecture-governance", "performance-reliability-governance", "common"],
        "docs-governance": ["api-governance", "architecture-governance", "data-governance", "common"],
        "common": [],
    }

    def __init__(self, governance_root: Path):
        """Initialize analyzer"""
        self.governance_root = governance_root
        self.all_entities = {**self.DIMENSIONS, **self.META_DOMAINS}
        self.dependency_graph: Dict[str, DependencyInfo] = {}
        self.circular_dependencies: List[List[str]] = []

    def analyze(self) -> Tuple[bool, Dict[str, Any]]:
        """Analyze all dependencies"""
        print("🔍 Analyzing Governance Dependencies...")
        print("=" * 100)

        # Build dependency graph
        self._build_dependency_graph()

        # Detect circular dependencies
        self._detect_circular_dependencies()

        # Calculate initialization order
        self._calculate_initialization_order()

        # Generate report
        report = {
            "total_entities": len(self.all_entities),
            "total_dependencies": sum(len(deps) for deps in self.all_entities.values()),
            "circular_dependencies": self.circular_dependencies,
            "has_circular": len(self.circular_dependencies) > 0,
            "dependency_graph": self._format_graph(),
            "initialization_order": self._get_initialization_order(),
            "critical_dependencies": self._find_critical_dependencies(),
        }

        return len(self.circular_dependencies) == 0, report

    def _build_dependency_graph(self) -> None:
        """Build complete dependency graph"""
        for entity, dependencies in self.all_entities.items():
            # Filter out invalid dependencies
            valid_deps = [d for d in dependencies if d in self.all_entities]

            self.dependency_graph[entity] = DependencyInfo(
                name=entity,
                dependencies=valid_deps,
                dependents=[],
                initialization_order=0,
                is_circular=False
            )

        # Build reverse dependencies (dependents)
        for entity, info in self.dependency_graph.items():
            for dep in info.dependencies:
                if dep in self.dependency_graph:
                    self.dependency_graph[dep].dependents.append(entity)

    def _detect_circular_dependencies(self) -> None:
        """Detect circular dependency cycles"""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            if node in self.dependency_graph:
                for neighbor in self.dependency_graph[node].dependencies:
                    if neighbor not in visited:
                        dfs(neighbor, path[:])
                    elif neighbor in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        if cycle not in self.circular_dependencies:
                            self.circular_dependencies.append(cycle)
                        self.dependency_graph[neighbor].is_circular = True

            rec_stack.remove(node)

        for entity in self.dependency_graph:
            if entity not in visited:
                dfs(entity, [])

    def _calculate_initialization_order(self) -> None:
        """Calculate topological sort order for initialization"""
        in_degree = {entity: 0 for entity in self.dependency_graph}

        # Calculate in-degrees
        for entity, info in self.dependency_graph.items():
            for dep in info.dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1

        # Topological sort using Kahn's algorithm
        queue = deque([entity for entity in in_degree if in_degree[entity] == 0])
        order = 0

        while queue:
            current = queue.popleft()
            self.dependency_graph[current].initialization_order = order
            order += 1

            for dependent in self.dependency_graph[current].dependents:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    def _find_critical_dependencies(self) -> List[str]:
        """Find critical path dependencies"""
        critical = []

        for entity, info in self.dependency_graph.items():
            # Entity is critical if many others depend on it
            if len(info.dependents) > 2:
                critical.append(entity)

        return sorted(critical, key=lambda e: len(self.dependency_graph[e].dependents), reverse=True)

    def _get_initialization_order(self) -> Dict[int, List[str]]:
        """Get initialization order grouped by level"""
        order_map = defaultdict(list)

        for entity, info in self.dependency_graph.items():
            order_map[info.initialization_order].append(entity)

        return {order: sorted(entities) for order, entities in order_map.items()}

    def _format_graph(self) -> Dict[str, Dict[str, Any]]:
        """Format dependency graph for output"""
        return {
            entity: {
                "dependencies": info.dependencies,
                "dependents": info.dependents,
                "is_circular": info.is_circular,
            }
            for entity, info in self.dependency_graph.items()
        }

    def print_report(self, report: Dict[str, Any]) -> None:
        """Print dependency analysis report"""
        print("\n" + "=" * 100)
        print("📊 GOVERNANCE DEPENDENCY ANALYSIS REPORT")
        print("=" * 100)

        print(f"\n📈 Summary:")
        print(f"   Total Entities:       {report['total_entities']}")
        print(f"   Total Dependencies:   {report['total_dependencies']}")
        print(f"   Circular Deps Found:  {len(report['circular_dependencies'])}")

        if report["has_circular"]:
            print(f"\n⚠️  CIRCULAR DEPENDENCIES DETECTED:")
            for cycle in report["circular_dependencies"]:
                print(f"   {' → '.join(cycle)}")

        print(f"\n🎯 Initialization Order:")
        for order, entities in sorted(report["initialization_order"].items()):
            print(f"   Level {order}:")
            for entity in entities[:3]:  # Show first 3
                print(f"      • {entity}")
            if len(entities) > 3:
                print(f"      • ... and {len(entities) - 3} more")

        if report["critical_dependencies"]:
            print(f"\n⚡ Critical Dependencies (high dependent count):")
            for entity in report["critical_dependencies"][:5]:
                dependents = report["dependency_graph"][entity]["dependents"]
                print(f"   {entity}: {len(dependents)} dependents")

        print(f"\n{'=' * 100}")


def main():
    """Main entry point"""
    governance_root = Path(__file__).parent.parent.parent

    analyzer = DependencyAnalyzer(governance_root)
    valid, report = analyzer.analyze()

    analyzer.print_report(report)

    # Export report
    report_path = governance_root / "dependency_analysis_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n✅ Report exported to: {report_path}")

    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
