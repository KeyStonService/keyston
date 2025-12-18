"""
Partial Rollback Manager - 3-Level Granularity Rollback System

This module implements the partial rollback functionality with support for
Phase, Plan-unit, and Artifact level rollbacks.
"""

from typing import Dict, List, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


class RollbackLevel(Enum):
    """Granularity level for rollback operations"""
    PHASE = "phase"  # Rollback entire execution phase
    PLAN_UNIT = "plan_unit"  # Rollback specific plan components
    ARTIFACT = "artifact"  # Rollback individual artifacts


class RollbackStatus(Enum):
    """Status of rollback operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


@dataclass
class Checkpoint:
    """
    Represents a checkpoint in execution
    
    Attributes:
        checkpoint_id: Unique identifier
        level: Rollback granularity level
        timestamp: When checkpoint was created
        state: Execution state at checkpoint
        metadata: Additional context
    """
    checkpoint_id: str
    level: RollbackLevel
    timestamp: datetime = field(default_factory=datetime.now)
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackOperation:
    """
    Represents a rollback operation
    
    Attributes:
        operation_id: Unique identifier
        target_checkpoint: Checkpoint to roll back to
        level: Rollback level
        status: Current status
        affected_items: List of items to rollback
        completed_items: List of successfully rolled back items
        failed_items: List of failed rollback items
        error: Error if rollback failed
    """
    operation_id: str
    target_checkpoint: Checkpoint
    level: RollbackLevel
    status: RollbackStatus = RollbackStatus.PENDING
    affected_items: List[str] = field(default_factory=list)
    completed_items: List[str] = field(default_factory=list)
    failed_items: List[str] = field(default_factory=list)
    error: Optional[Exception] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class PartialRollbackManager:
    """
    Manages partial rollback operations with 3-level granularity
    
    Provides checkpoint creation and rollback execution with support
    for Phase, Plan-unit, and Artifact level operations.
    """
    
    def __init__(self):
        """Initialize rollback manager"""
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.operations: Dict[str, RollbackOperation] = {}
        self.checkpoint_order: List[str] = []  # Maintain checkpoint sequence
        
    def create_checkpoint(
        self,
        checkpoint_id: str,
        level: RollbackLevel,
        state: Dict[str, Any],
        **metadata
    ) -> Checkpoint:
        """
        Create a checkpoint for potential rollback
        
        Args:
            checkpoint_id: Unique identifier for checkpoint
            level: Granularity level
            state: Execution state to save
            **metadata: Additional context
            
        Returns:
            Created checkpoint
            
        Raises:
            ValueError: If checkpoint_id already exists
        """
        if checkpoint_id in self.checkpoints:
            raise ValueError(f"Checkpoint {checkpoint_id} already exists")
            
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            level=level,
            state=state.copy(),
            metadata=metadata,
        )
        
        self.checkpoints[checkpoint_id] = checkpoint
        self.checkpoint_order.append(checkpoint_id)
        
        return checkpoint
        
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Get a checkpoint by ID
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Checkpoint if found, None otherwise
        """
        return self.checkpoints.get(checkpoint_id)
        
    def list_checkpoints(
        self, level: Optional[RollbackLevel] = None
    ) -> List[Checkpoint]:
        """
        List all checkpoints, optionally filtered by level
        
        Args:
            level: Optional level filter
            
        Returns:
            List of checkpoints
        """
        checkpoints = [
            self.checkpoints[cid] for cid in self.checkpoint_order
            if cid in self.checkpoints
        ]
        
        if level:
            checkpoints = [cp for cp in checkpoints if cp.level == level]
            
        return checkpoints
        
    async def rollback_to_checkpoint(
        self,
        operation_id: str,
        checkpoint_id: str,
        affected_items: Optional[List[str]] = None,
    ) -> RollbackOperation:
        """
        Execute rollback to a specific checkpoint
        
        Args:
            operation_id: Unique identifier for this operation
            checkpoint_id: Target checkpoint to roll back to
            affected_items: Optional list of specific items to rollback
            
        Returns:
            RollbackOperation tracking the rollback
            
        Raises:
            ValueError: If checkpoint not found or operation_id exists
        """
        if operation_id in self.operations:
            raise ValueError(f"Operation {operation_id} already exists")
            
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
            
        # Create rollback operation
        operation = RollbackOperation(
            operation_id=operation_id,
            target_checkpoint=checkpoint,
            level=checkpoint.level,
            affected_items=affected_items or [],
        )
        
        self.operations[operation_id] = operation
        
        # Execute rollback
        try:
            operation.status = RollbackStatus.IN_PROGRESS
            operation.started_at = datetime.now()
            
            # Perform rollback based on level
            if checkpoint.level == RollbackLevel.PHASE:
                await self._rollback_phase(operation)
            elif checkpoint.level == RollbackLevel.PLAN_UNIT:
                await self._rollback_plan_unit(operation)
            elif checkpoint.level == RollbackLevel.ARTIFACT:
                await self._rollback_artifact(operation)
                
            # Check completion status
            if len(operation.failed_items) == 0:
                operation.status = RollbackStatus.COMPLETED
            elif len(operation.completed_items) > 0:
                operation.status = RollbackStatus.PARTIALLY_COMPLETED
            else:
                operation.status = RollbackStatus.FAILED
                
            operation.completed_at = datetime.now()
            
        except Exception as e:
            operation.status = RollbackStatus.FAILED
            operation.error = e
            operation.completed_at = datetime.now()
            raise
            
        return operation
        
    async def _rollback_phase(self, operation: RollbackOperation) -> None:
        """
        Rollback entire execution phase
        
        Args:
            operation: Rollback operation to execute
        """
        # Implementation placeholder for phase-level rollback
        # In production, this would restore all state for the phase
        for item in operation.affected_items:
            try:
                # Simulate rollback operation
                await asyncio.sleep(0.01)  # Async operation simulation
                operation.completed_items.append(item)
            except Exception as e:
                operation.failed_items.append(item)
                
    async def _rollback_plan_unit(self, operation: RollbackOperation) -> None:
        """
        Rollback specific plan components
        
        Args:
            operation: Rollback operation to execute
        """
        # Implementation placeholder for plan-unit-level rollback
        for item in operation.affected_items:
            try:
                await asyncio.sleep(0.01)
                operation.completed_items.append(item)
            except Exception as e:
                operation.failed_items.append(item)
                
    async def _rollback_artifact(self, operation: RollbackOperation) -> None:
        """
        Rollback individual artifacts
        
        Args:
            operation: Rollback operation to execute
        """
        # Implementation placeholder for artifact-level rollback
        for item in operation.affected_items:
            try:
                await asyncio.sleep(0.01)
                operation.completed_items.append(item)
            except Exception as e:
                operation.failed_items.append(item)
                
    def get_operation(self, operation_id: str) -> Optional[RollbackOperation]:
        """
        Get rollback operation by ID
        
        Args:
            operation_id: Operation identifier
            
        Returns:
            RollbackOperation if found, None otherwise
        """
        return self.operations.get(operation_id)
        
    def cleanup_checkpoints(self, keep_last_n: int = 10) -> int:
        """
        Clean up old checkpoints, keeping only the most recent N
        
        Args:
            keep_last_n: Number of recent checkpoints to keep
            
        Returns:
            Number of checkpoints removed
        """
        if len(self.checkpoint_order) <= keep_last_n:
            return 0
            
        # Remove oldest checkpoints
        to_remove = self.checkpoint_order[:-keep_last_n]
        for checkpoint_id in to_remove:
            if checkpoint_id in self.checkpoints:
                del self.checkpoints[checkpoint_id]
                
        self.checkpoint_order = self.checkpoint_order[-keep_last_n:]
        
        return len(to_remove)
        
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of rollback manager state
        
        Returns:
            Dict with statistics
        """
        status_counts = {}
        for op in self.operations.values():
            status_counts[op.status.value] = status_counts.get(op.status.value, 0) + 1
            
        return {
            "total_checkpoints": len(self.checkpoints),
            "checkpoints_by_level": {
                level.value: len([
                    cp for cp in self.checkpoints.values()
                    if cp.level == level
                ])
                for level in RollbackLevel
            },
            "total_operations": len(self.operations),
            "operations_by_status": status_counts,
        }
