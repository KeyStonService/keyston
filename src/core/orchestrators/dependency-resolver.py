#!/usr/bin/env python3
"""
Dependency Resolver - 智能依賴解析和管理系統

功能：
1. 依賴圖構建
2. 循環依賴檢測
3. 拓撲排序
4. 優先級計算
5. 並行化分析
6. 性能優化建議
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


@dataclass
class DependencyNode:
    """依賴圖中的節點"""
    component_id: str
    component_type: str
    priority: int = 0
    weight: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    dependent_on: List[str] = field(default_factory=list)


@dataclass
class ExecutionPhase:
    """執行階段"""
    phase_number: int
    components: List[str]
    can_parallel: bool
    estimated_duration_ms: float
    dependency_count: int


class DependencyResolver:
    """
    智能依賴解析器

    提供：
    - 依賴圖分析
    - 拓撲排序
    - 並行化檢測
    - 關鍵路徑分析
    - 優化建議
    """

    def __init__(self):
        """初始化解析器"""
        self.nodes: Dict[str, DependencyNode] = {}
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.memo_cache: Dict[str, List[str]] = {}
        logger.info("🔄 DependencyResolver 初始化完成")

    def add_component(
        self,
        component_id: str,
        component_type: str,
        priority: int = 0,
        weight: float = 1.0
    ) -> bool:
        """添加組件"""
        try:
            self.nodes[component_id] = DependencyNode(
                component_id=component_id,
                component_type=component_type,
                priority=priority,
                weight=weight
            )
            return True
        except Exception as e:
            logger.error(f"❌ 添加組件失敗 {component_id}: {e}")
            return False

    def add_dependency(
        self,
        from_component: str,
        to_component: str
    ) -> bool:
        """添加依賴關係"""
        try:
            # 驗證組件存在
            if from_component not in self.nodes or to_component not in self.nodes:
                raise ValueError("組件不存在")

            # 檢查循環依賴
            if self._would_create_cycle(from_component, to_component):
                raise ValueError(f"循環依賴: {from_component} → {to_component}")

            self.graph[from_component].add(to_component)
            self.reverse_graph[to_component].add(from_component)

            # 更新節點引用
            self.nodes[from_component].dependencies.append(to_component)
            self.nodes[to_component].dependent_on.append(from_component)

            # 清除快取
            self.memo_cache.clear()

            logger.info(f"✅ 依賴已添加: {from_component} → {to_component}")
            return True

        except ValueError as e:
            logger.error(f"❌ 添加依賴失敗: {e}")
            return False

    def _would_create_cycle(
        self,
        from_component: str,
        to_component: str,
        visited: Optional[Set[str]] = None
    ) -> bool:
        """檢查是否會創建循環"""
        if visited is None:
            visited = set()

        if from_component in visited:
            return True

        if from_component == to_component:
            return True

        visited.add(from_component)

        for neighbor in self.graph.get(from_component, set()):
            if self._would_create_cycle(neighbor, to_component, visited.copy()):
                return True

        return False

    def topological_sort(
        self,
        component_ids: Optional[List[str]] = None
    ) -> List[str]:
        """拓撲排序"""
        if component_ids is None:
            component_ids = list(self.nodes.keys())

        # 快取檢查
        cache_key = ",".join(sorted(component_ids))
        if cache_key in self.memo_cache:
            return self.memo_cache[cache_key]

        # Kahn 演算法
        in_degree = {comp: 0 for comp in component_ids}
        for comp in component_ids:
            for dep in self.graph.get(comp, set()):
                if dep in in_degree:
                    in_degree[dep] += 1

        queue = deque([comp for comp in component_ids if in_degree[comp] == 0])
        result = []

        while queue:
            # 按優先級排序
            queue_list = sorted(
                queue,
                key=lambda x: (self.nodes[x].priority, x),
                reverse=True
            )
            current = queue_list.pop(0)
            queue = deque(queue_list)
            result.append(current)

            for dep in self.graph.get(current, set()):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

        self.memo_cache[cache_key] = result
        logger.info(f"✅ 拓撲排序完成: {result}")

        return result

    def get_execution_phases(
        self,
        component_ids: Optional[List[str]] = None
    ) -> List[ExecutionPhase]:
        """獲取執行階段（並行化分析）"""
        sorted_components = self.topological_sort(component_ids)

        phases = []
        processed = set()
        phase_number = 1

        while len(processed) < len(sorted_components):
            current_phase = []

            for comp in sorted_components:
                if comp in processed:
                    continue

                # 檢查依賴是否都已處理
                dependencies = self.graph.get(comp, set())
                if all(dep in processed for dep in dependencies):
                    current_phase.append(comp)

            if not current_phase:
                # 如果沒有可處理的組件，可能有問題
                logger.warning("⚠️ 無法繼續執行拓撲排序")
                break

            # 計算執行時間
            estimated_time = sum(
                self.nodes[comp].weight * 100 for comp in current_phase
            )

            phase = ExecutionPhase(
                phase_number=phase_number,
                components=current_phase,
                can_parallel=len(current_phase) > 1,
                estimated_duration_ms=estimated_time,
                dependency_count=len([
                    d for comp in current_phase
                    for d in self.graph.get(comp, set())
                ])
            )

            phases.append(phase)
            processed.update(current_phase)
            phase_number += 1

        logger.info(f"✅ 執行階段分析完成: {len(phases)} 個階段")
        return phases

    def get_critical_path(self) -> List[str]:
        """獲取關鍵路徑"""
        component_ids = list(self.nodes.keys())

        if not component_ids:
            return []

        # 簡化版本：最長路徑
        def dfs_longest_path(node: str, visited: Set[str]) -> Tuple[float, List[str]]:
            if node not in self.graph or not self.graph[node]:
                return self.nodes[node].weight, [node]

            max_weight = self.nodes[node].weight
            longest = [node]

            for dep in self.graph[node]:
                if dep not in visited:
                    visited.add(dep)
                    weight, path = dfs_longest_path(dep, visited)
                    if weight + self.nodes[node].weight > max_weight:
                        max_weight = weight + self.nodes[node].weight
                        longest = [node] + path
                    visited.remove(dep)

            return max_weight, longest

        visited = set()
        _, critical_path = dfs_longest_path(component_ids[0], visited)

        logger.info(f"✅ 關鍵路徑: {critical_path}")
        return critical_path

    def get_parallelization_analysis(
        self,
        component_ids: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """獲取並行化分析"""
        phases = self.get_execution_phases(component_ids)

        sequential_time = sum(p.estimated_duration_ms for p in phases)
        parallel_time = max(p.estimated_duration_ms for p in phases)
        parallelization_factor = sequential_time / max(parallel_time, 1)

        return {
            "total_components": len(component_ids or self.nodes),
            "execution_phases": len(phases),
            "sequential_time_ms": sequential_time,
            "parallel_time_ms": parallel_time,
            "parallelization_factor": parallelization_factor,
            "potential_speedup": f"{parallelization_factor:.2f}x"
        }

    def get_dependency_stats(self) -> Dict[str, any]:
        """獲取依賴統計"""
        total_edges = sum(len(deps) for deps in self.graph.values())
        avg_degree = total_edges / max(len(self.nodes), 1)

        return {
            "total_components": len(self.nodes),
            "total_dependencies": total_edges,
            "average_dependency_count": avg_degree,
            "max_dependency_depth": self._calculate_max_depth(),
            "circular_dependencies": 0  # 我們檢測並防止了循環
        }

    def _calculate_max_depth(self) -> int:
        """計算最大依賴深度"""
        max_depth = 0

        for component in self.nodes:
            depth = self._calculate_depth(component, set())
            max_depth = max(max_depth, depth)

        return max_depth

    def _calculate_depth(
        self,
        component: str,
        visited: Set[str]
    ) -> int:
        """遞歸計算深度"""
        if component in visited:
            return 0

        visited.add(component)

        dependencies = self.graph.get(component, set())
        if not dependencies:
            return 1

        max_dep_depth = max(
            self._calculate_depth(dep, visited.copy())
            for dep in dependencies
        )

        return 1 + max_dep_depth

    def get_optimization_recommendations(self) -> List[str]:
        """獲取優化建議"""
        recommendations = []
        stats = self.get_dependency_stats()
        analysis = self.get_parallelization_analysis()

        # 檢查依賴複雜性
        if stats["average_dependency_count"] > 5:
            recommendations.append(
                "⚠️ 依賴複雜性高，考慮重構以減少耦合"
            )

        # 檢查並行化機會
        if analysis["parallelization_factor"] < 2:
            recommendations.append(
                "💡 低並行化機會，考慮優化依賴關係"
            )

        # 檢查深度
        if stats["max_dependency_depth"] > 5:
            recommendations.append(
                "🔗 依賴深度深，考慮引入中間層"
            )

        if not recommendations:
            recommendations.append(
                "✅ 依賴結構健康，無特別建議"
            )

        return recommendations

    def export_graph(self) -> Dict[str, any]:
        """導出依賴圖"""
        return {
            "nodes": [
                {
                    "id": node.component_id,
                    "type": node.component_type,
                    "priority": node.priority,
                    "weight": node.weight
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {"from": from_comp, "to": to_comp}
                for from_comp in self.graph
                for to_comp in self.graph[from_comp]
            ],
            "statistics": self.get_dependency_stats(),
            "recommendations": self.get_optimization_recommendations()
        }


# 導出
__all__ = [
    "DependencyResolver",
    "DependencyNode",
    "ExecutionPhase"
]
