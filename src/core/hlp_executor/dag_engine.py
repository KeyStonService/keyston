"""
DAG Engine - Directed Acyclic Graph Orchestration Engine

This module implements the core DAG orchestration logic with topological sorting,
dependency resolution, and parallel execution capabilities.
"""

from typing import Dict, List, Set, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import asyncio
from collections import defaultdict, deque


class NodeStatus(Enum):
    """Status of a DAG node"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """
    Represents a node in the DAG
    
    Attributes:
        node_id: Unique identifier for the node
        task: Callable task to execute
        dependencies: List of node_ids this node depends on
        status: Current execution status
        result: Execution result
        error: Error if execution failed
        metadata: Additional metadata
    """
    node_id: str
    task: Callable
    dependencies: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DAGEngine:
    """
    Async DAG Orchestration Engine
    
    Provides topological sorting, dependency resolution, and parallel execution
    of directed acyclic graph workflows.
    """
    
    def __init__(self):
        """Initialize the DAG engine"""
        self.nodes: Dict[str, DAGNode] = {}
        self.execution_order: List[List[str]] = []
        
    def add_node(self, node: DAGNode) -> None:
        """
        Add a node to the DAG
        
        Args:
            node: DAGNode to add
            
        Raises:
            ValueError: If node_id already exists
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists")
        self.nodes[node.node_id] = node
        
    def _detect_cycle(self) -> bool:
        """
        Detect if there are cycles in the DAG
        
        Returns:
            bool: True if cycle detected, False otherwise
        """
        visited = set()
        rec_stack = set()
        
        def visit(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = self.nodes.get(node_id)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        if visit(dep):
                            return True
                    elif dep in rec_stack:
                        return True
                        
            rec_stack.remove(node_id)
            return False
            
        for node_id in self.nodes:
            if node_id not in visited:
                if visit(node_id):
                    return True
        return False
        
    def topological_sort(self) -> List[List[str]]:
        """
        Perform topological sort with level-based grouping for parallel execution
        
        Returns:
            List of levels, where each level contains node_ids that can run in parallel
            
        Raises:
            ValueError: If cycle is detected
        """
        if self._detect_cycle():
            raise ValueError("Cycle detected in DAG")
            
        # Calculate in-degree for each node
        in_degree = {node_id: 0 for node_id in self.nodes}
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
                    
        # Find all nodes with in-degree 0
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        levels = []
        
        while queue:
            # Current level - all nodes that can run in parallel
            current_level = list(queue)
            levels.append(current_level)
            
            # Process current level
            next_queue = []
            for node_id in current_level:
                queue.popleft()
                node = self.nodes[node_id]
                
                # Decrease in-degree for dependent nodes
                for dependent_id in self.nodes:
                    dependent = self.nodes[dependent_id]
                    if node_id in dependent.dependencies:
                        in_degree[dependent_id] -= 1
                        if in_degree[dependent_id] == 0:
                            next_queue.append(dependent_id)
                            
            queue.extend(next_queue)
            
        self.execution_order = levels
        return levels
        
    async def _execute_node(self, node: DAGNode) -> Any:
        """
        Execute a single node
        
        Args:
            node: Node to execute
            
        Returns:
            Execution result
        """
        try:
            node.status = NodeStatus.RUNNING
            
            # Execute the task
            if asyncio.iscoroutinefunction(node.task):
                result = await node.task()
            else:
                result = node.task()
                
            node.status = NodeStatus.COMPLETED
            node.result = result
            return result
            
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = e
            raise
            
    async def execute(self) -> Dict[str, Any]:
        """
        Execute the DAG with parallel execution where possible
        
        Returns:
            Dict mapping node_id to execution result
            
        Raises:
            ValueError: If DAG has cycles or dependencies are invalid
        """
        # Perform topological sort
        levels = self.topological_sort()
        
        results = {}
        
        # Execute level by level
        for level in levels:
            # Execute all nodes in this level in parallel
            tasks = []
            for node_id in level:
                node = self.nodes[node_id]
                
                # Check if all dependencies completed successfully
                dependencies_ok = True
                for dep_id in node.dependencies:
                    dep_node = self.nodes.get(dep_id)
                    if not dep_node or dep_node.status != NodeStatus.COMPLETED:
                        dependencies_ok = False
                        break
                        
                if dependencies_ok:
                    tasks.append(self._execute_node(node))
                else:
                    node.status = NodeStatus.SKIPPED
                    
            # Wait for all tasks in this level to complete
            if tasks:
                level_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Store results
                for i, node_id in enumerate([nid for nid in level if self.nodes[nid].status == NodeStatus.RUNNING or self.nodes[nid].status == NodeStatus.COMPLETED]):
                    results[node_id] = level_results[i] if i < len(level_results) else None
                    
        return results
        
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of DAG execution
        
        Returns:
            Dict with execution statistics
        """
        status_counts = defaultdict(int)
        for node in self.nodes.values():
            status_counts[node.status.value] += 1
            
        return {
            "total_nodes": len(self.nodes),
            "status_counts": dict(status_counts),
            "execution_levels": len(self.execution_order),
            "nodes_by_level": [len(level) for level in self.execution_order],
        }
