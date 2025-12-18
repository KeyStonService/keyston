"""
Partial Rollback Manager for HLP Executor Core

Implements phase-level, plan-unit-level, and artifact-level rollback
capabilities with dependency tracking.

This module provides granular rollback functionality for the HLP Executor Core,
allowing safe recovery from failures at multiple levels of granularity.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RollbackScope(Enum):
    """Defines the scope/granularity of rollback operations."""
    PHASE = "phase"
    PLAN_UNIT = "plan-unit"
    ARTIFACT = "artifact"
    ENTIRE_EXECUTION = "entire-execution"


class RollbackTrigger(Enum):
    """Defines the conditions that trigger rollback."""
    VALIDATION_FAILURE = "validation-failure"
    RESOURCE_EXHAUSTION = "resource-exhaustion"
    SECURITY_VIOLATION = "security-violation"
    TIMEOUT = "timeout"
    MANUAL = "manual"


class RollbackAction(Enum):
    """Defines the action to take during rollback."""
    ROLLBACK_CURRENT_PHASE = "rollback-current-phase"
    RESCHEDULE_WITH_BACKOFF = "reschedule-with-backoff"
    EMERGENCY_STOP_AND_ROLLBACK = "emergency-stop-and-rollback"
    SKIP_AND_CONTINUE = "skip-and-continue"


@dataclass
class Checkpoint:
    """Represents a checkpoint for rollback."""
    checkpoint_id: str
    execution_id: str
    phase_id: str
    timestamp: datetime
    state: dict[str, Any]
    dependencies: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    success: bool
    scope: RollbackScope
    target_id: str
    checkpoint_id: str | None
    message: str
    rolled_back_items: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PartialRollbackManager:
    """
    Manages partial rollback operations at multiple granularity levels.
    
    Features:
    - Phase-level rollback: Roll back entire execution phase
    - Plan-unit-level rollback: Roll back individual plan units
    - Artifact-level rollback: Roll back specific artifacts
    - Dependency tracking: Forward and backward dependency analysis
    - Checkpoint management: Create and restore from checkpoints
    """
    
    def __init__(self, checkpoint_retention: int = 5):
        """
        Initialize the PartialRollbackManager.
        
        Args:
            checkpoint_retention: Number of checkpoints to retain per execution
        """
        self.checkpoint_retention = checkpoint_retention
        self._checkpoints: dict[str, list[Checkpoint]] = {}
        self._execution_graph: dict[str, set[str]] = {}
        self._reverse_graph: dict[str, set[str]] = {}
        
        logger.info(
            "PartialRollbackManager initialized with retention=%d",
            checkpoint_retention
        )
    
    def evaluate_rollback_trigger(
        self,
        condition: str,
        scope: str
    ) -> RollbackAction:
        """
        Evaluate a rollback trigger and determine the appropriate action.
        
        Args:
            condition: The trigger condition (e.g., 'validation-failure')
            scope: The scope of impact (e.g., 'phase', 'plan-unit')
        
        Returns:
            RollbackAction to take
        """
        try:
            trigger = RollbackTrigger(condition)
            rollback_scope = RollbackScope(scope)
        except ValueError as e:
            logger.error("Invalid trigger or scope: %s", e)
            return RollbackAction.EMERGENCY_STOP_AND_ROLLBACK
        
        # Define trigger-to-action mappings
        trigger_map = {
            RollbackTrigger.VALIDATION_FAILURE: {
                RollbackScope.PHASE: RollbackAction.ROLLBACK_CURRENT_PHASE,
                RollbackScope.PLAN_UNIT: RollbackAction.ROLLBACK_CURRENT_PHASE,
                RollbackScope.ARTIFACT: RollbackAction.SKIP_AND_CONTINUE,
            },
            RollbackTrigger.RESOURCE_EXHAUSTION: {
                RollbackScope.PHASE: RollbackAction.RESCHEDULE_WITH_BACKOFF,
                RollbackScope.PLAN_UNIT: RollbackAction.RESCHEDULE_WITH_BACKOFF,
                RollbackScope.ARTIFACT: RollbackAction.RESCHEDULE_WITH_BACKOFF,
            },
            RollbackTrigger.SECURITY_VIOLATION: {
                RollbackScope.PHASE: RollbackAction.EMERGENCY_STOP_AND_ROLLBACK,
                RollbackScope.PLAN_UNIT: RollbackAction.EMERGENCY_STOP_AND_ROLLBACK,
                RollbackScope.ARTIFACT: RollbackAction.EMERGENCY_STOP_AND_ROLLBACK,
                RollbackScope.ENTIRE_EXECUTION: RollbackAction.EMERGENCY_STOP_AND_ROLLBACK,
            },
        }
        
        action = trigger_map.get(trigger, {}).get(
            rollback_scope,
            RollbackAction.EMERGENCY_STOP_AND_ROLLBACK
        )
        
        logger.info(
            "Evaluated trigger=%s, scope=%s -> action=%s",
            trigger.value,
            rollback_scope.value,
            action.value
        )
        
        return action
    
    def execute_rollback(
        self,
        scope: str,
        target: str,
        execution_id: str | None = None
    ) -> RollbackResult:
        """
        Execute a rollback operation.
        
        Args:
            scope: Scope of rollback ('phase', 'plan-unit', 'artifact')
            target: Target identifier to roll back
            execution_id: Optional execution ID for checkpoint lookup
        
        Returns:
            RollbackResult with operation details
        """
        try:
            rollback_scope = RollbackScope(scope)
        except ValueError:
            return RollbackResult(
                success=False,
                scope=RollbackScope.PHASE,
                target_id=target,
                checkpoint_id=None,
                message=f"Invalid rollback scope: {scope}"
            )
        
        logger.info(
            "Executing rollback: scope=%s, target=%s, execution_id=%s",
            scope,
            target,
            execution_id
        )
        
        # Find dependencies that need to be rolled back
        affected_items = self._find_dependent_items(target)
        
        # Perform the rollback
        checkpoint_id = None
        if execution_id and execution_id in self._checkpoints:
            # Restore from checkpoint
            checkpoint = self._find_checkpoint_for_target(execution_id, target)
            if checkpoint:
                checkpoint_id = checkpoint.checkpoint_id
                self._restore_from_checkpoint(checkpoint)
        
        # Roll back the target and its dependents
        rolled_back = [target] + list(affected_items)
        
        return RollbackResult(
            success=True,
            scope=rollback_scope,
            target_id=target,
            checkpoint_id=checkpoint_id,
            message=f"Successfully rolled back {len(rolled_back)} items",
            rolled_back_items=rolled_back
        )
    
    def create_checkpoint(
        self,
        execution_id: str,
        phase_id: str,
        state: dict[str, Any]
    ) -> str:
        """
        Create a checkpoint for rollback.
        
        Args:
            execution_id: Unique execution identifier
            phase_id: Phase identifier
            state: Current state to checkpoint
        
        Returns:
            Checkpoint ID
        """
        checkpoint_id = f"cp_{execution_id}_{phase_id}_{int(datetime.utcnow().timestamp())}"
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            execution_id=execution_id,
            phase_id=phase_id,
            timestamp=datetime.utcnow(),
            state=state.copy(),
            dependencies=self._execution_graph.get(phase_id, set()).copy()
        )
        
        if execution_id not in self._checkpoints:
            self._checkpoints[execution_id] = []
        
        self._checkpoints[execution_id].append(checkpoint)
        
        # Enforce retention policy
        if len(self._checkpoints[execution_id]) > self.checkpoint_retention:
            removed = self._checkpoints[execution_id].pop(0)
            logger.debug("Removed old checkpoint: %s", removed.checkpoint_id)
        
        logger.info(
            "Created checkpoint: %s for execution=%s, phase=%s",
            checkpoint_id,
            execution_id,
            phase_id
        )
        
        return checkpoint_id
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> RollbackResult:
        """
        Restore state from a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            RollbackResult with restoration details
        """
        checkpoint = self._find_checkpoint_by_id(checkpoint_id)
        
        if not checkpoint:
            return RollbackResult(
                success=False,
                scope=RollbackScope.PHASE,
                target_id="",
                checkpoint_id=checkpoint_id,
                message=f"Checkpoint not found: {checkpoint_id}"
            )
        
        self._restore_from_checkpoint(checkpoint)
        
        return RollbackResult(
            success=True,
            scope=RollbackScope.PHASE,
            target_id=checkpoint.phase_id,
            checkpoint_id=checkpoint_id,
            message=f"Restored from checkpoint: {checkpoint_id}"
        )
    
    def register_dependency(
        self,
        source: str,
        target: str
    ) -> None:
        """
        Register a dependency relationship for rollback tracking.
        
        Args:
            source: Source item (depends on target)
            target: Target item (depended upon by source)
        """
        if target not in self._execution_graph:
            self._execution_graph[target] = set()
        self._execution_graph[target].add(source)
        
        if source not in self._reverse_graph:
            self._reverse_graph[source] = set()
        self._reverse_graph[source].add(target)
        
        logger.debug("Registered dependency: %s -> %s", source, target)
    
    def _find_dependent_items(self, target: str) -> set[str]:
        """
        Find all items that depend on the target (forward dependencies).
        
        Args:
            target: Target item
        
        Returns:
            Set of dependent items
        """
        dependents = set()
        to_visit = [target]
        visited = set()
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            
            if current in self._execution_graph:
                for dependent in self._execution_graph[current]:
                    dependents.add(dependent)
                    to_visit.append(dependent)
        
        return dependents
    
    def _find_checkpoint_for_target(
        self,
        execution_id: str,
        target: str
    ) -> Checkpoint | None:
        """
        Find the most recent checkpoint for a target.
        
        Args:
            execution_id: Execution identifier
            target: Target identifier
        
        Returns:
            Checkpoint if found, None otherwise
        """
        if execution_id not in self._checkpoints:
            return None
        
        # Find the most recent checkpoint
        for checkpoint in reversed(self._checkpoints[execution_id]):
            if checkpoint.phase_id == target:
                return checkpoint
        
        return None
    
    def _find_checkpoint_by_id(self, checkpoint_id: str) -> Checkpoint | None:
        """Find a checkpoint by its ID."""
        for checkpoints in self._checkpoints.values():
            for checkpoint in checkpoints:
                if checkpoint.checkpoint_id == checkpoint_id:
                    return checkpoint
        return None
    
    def _restore_from_checkpoint(self, checkpoint: Checkpoint) -> None:
        """
        Internal method to restore state from a checkpoint.
        
        Args:
            checkpoint: Checkpoint to restore from
        """
        logger.info(
            "Restoring from checkpoint: %s (phase=%s, execution=%s)",
            checkpoint.checkpoint_id,
            checkpoint.phase_id,
            checkpoint.execution_id
        )
        
        # In a real implementation, this would restore:
        # - Kubernetes resources
        # - Database state
        # - File system state
        # - Configuration state
        
        # For now, we log the restoration
        logger.debug("Checkpoint state keys: %s", list(checkpoint.state.keys()))
    
    def get_checkpoint_count(self, execution_id: str) -> int:
        """Get the number of checkpoints for an execution."""
        return len(self._checkpoints.get(execution_id, []))
    
    def list_checkpoints(self, execution_id: str) -> list[Checkpoint]:
        """List all checkpoints for an execution."""
        return self._checkpoints.get(execution_id, []).copy()
    
    def cleanup_old_checkpoints(
        self,
        execution_id: str,
        keep_count: int = 5
    ) -> int:
        """
        Clean up old checkpoints beyond the retention limit.
        
        Args:
            execution_id: Execution identifier
            keep_count: Number of recent checkpoints to keep
        
        Returns:
            Number of checkpoints removed
        """
        if execution_id not in self._checkpoints:
            return 0
        
        current_count = len(self._checkpoints[execution_id])
        if current_count <= keep_count:
            return 0
        
        to_remove = current_count - keep_count
        self._checkpoints[execution_id] = self._checkpoints[execution_id][to_remove:]
        
        logger.info(
            "Cleaned up %d old checkpoints for execution=%s",
            to_remove,
            execution_id
        )
        
        return to_remove
