"""
Rollback System (回滾系統)

Support safe rollback strategies for recovering from errors.

Reference: Strategies supporting safe rollback are particularly important,
allowing institutions to revert changes like files, databases, configurations [4]
"""

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
import copy


class SnapshotType(Enum):
    """Types of snapshots"""
    FULL = "full"              # Complete system state
    INCREMENTAL = "incremental"  # Changes since last snapshot
    SELECTIVE = "selective"    # Specific components only
    CHECKPOINT = "checkpoint"  # Lightweight checkpoint


class RollbackStrategy(Enum):
    """Strategies for rollback"""
    FULL = "full"              # Restore complete state
    INCREMENTAL = "incremental"  # Reverse changes one by one
    SELECTIVE = "selective"    # Restore specific components
    COMPENSATING = "compensating"  # Execute compensating transactions


@dataclass
class Snapshot:
    """System state snapshot"""
    id: str
    type: SnapshotType
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
            "parent_id": self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snapshot':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            type=SnapshotType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            metadata=data.get("metadata", {}),
            parent_id=data.get("parent_id")
        )


@dataclass
class RollbackResult:
    """Result of a rollback operation"""
    success: bool
    snapshot_id: str
    strategy: RollbackStrategy
    timestamp: datetime
    components_restored: List[str]
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0


class RollbackSystem:
    """
    Rollback System
    
    Manages snapshots and provides safe rollback capabilities
    for recovering from errors.
    
    Features:
    - Multiple snapshot types (full, incremental, selective)
    - Multiple rollback strategies
    - Component-level restoration
    - Compensating transactions
    
    Example:
        rollback = RollbackSystem()
        snapshot_id = await rollback.create_snapshot(
            {"database": db_state, "config": config_state}
        )
        # ... operations ...
        if error:
            await rollback.rollback(snapshot_id)
    """
    
    def __init__(self, max_snapshots: int = 100):
        self._snapshots: Dict[str, Snapshot] = {}
        self._snapshot_order: List[str] = []
        self._max_snapshots = max_snapshots
        self._component_handlers: Dict[str, ComponentHandler] = {}
        self._listeners: List[Callable[[RollbackResult], None]] = []
        self._current_state: Dict[str, Any] = {}
    
    def register_component(
        self, 
        name: str, 
        save_handler: Callable[[], Any],
        restore_handler: Callable[[Any], None],
        compensate_handler: Optional[Callable[[Any, Any], None]] = None
    ) -> None:
        """
        Register a component for snapshot/rollback
        
        Args:
            name: Component name
            save_handler: Function to save component state
            restore_handler: Function to restore component state
            compensate_handler: Optional function for compensating transactions
        """
        self._component_handlers[name] = ComponentHandler(
            name=name,
            save=save_handler,
            restore=restore_handler,
            compensate=compensate_handler
        )
    
    def add_listener(self, listener: Callable[[RollbackResult], None]) -> None:
        """Add listener for rollback events"""
        self._listeners.append(listener)
    
    async def create_snapshot(
        self,
        data: Optional[Dict[str, Any]] = None,
        snapshot_type: SnapshotType = SnapshotType.FULL,
        components: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a system snapshot
        
        Args:
            data: Optional data to snapshot (if None, uses registered handlers)
            snapshot_type: Type of snapshot
            components: Optional list of components (for selective snapshot)
            metadata: Optional metadata
            
        Returns:
            Snapshot ID
        """
        import uuid
        
        snapshot_id = str(uuid.uuid4())
        
        # Collect data
        if data is None:
            data = {}
            handlers_to_use = (
                {k: v for k, v in self._component_handlers.items() if k in components}
                if components
                else self._component_handlers
            )
            
            for name, handler in handlers_to_use.items():
                try:
                    state = handler.save()
                    if asyncio.iscoroutine(state):
                        state = await state
                    data[name] = copy.deepcopy(state)
                except Exception as e:
                    data[name] = {"error": str(e)}
        
        # Get parent for incremental
        parent_id = None
        if snapshot_type == SnapshotType.INCREMENTAL and self._snapshot_order:
            parent_id = self._snapshot_order[-1]
        
        # Create snapshot
        snapshot = Snapshot(
            id=snapshot_id,
            type=snapshot_type,
            timestamp=datetime.now(),
            data=data,
            metadata=metadata or {},
            parent_id=parent_id
        )
        
        # Store snapshot
        self._snapshots[snapshot_id] = snapshot
        self._snapshot_order.append(snapshot_id)
        
        # Update current state
        self._current_state = copy.deepcopy(data)
        
        # Cleanup old snapshots
        await self._cleanup_old_snapshots()
        
        return snapshot_id
    
    async def rollback(
        self,
        snapshot_id: str,
        strategy: RollbackStrategy = RollbackStrategy.FULL,
        components: Optional[List[str]] = None
    ) -> RollbackResult:
        """
        Rollback to a snapshot
        
        Args:
            snapshot_id: ID of snapshot to restore
            strategy: Rollback strategy to use
            components: Optional list of components to restore
            
        Returns:
            RollbackResult
        """
        import time
        start_time = time.time()
        
        if snapshot_id not in self._snapshots:
            return RollbackResult(
                success=False,
                snapshot_id=snapshot_id,
                strategy=strategy,
                timestamp=datetime.now(),
                components_restored=[],
                errors=[f"Snapshot {snapshot_id} not found"]
            )
        
        snapshot = self._snapshots[snapshot_id]
        errors: List[str] = []
        restored: List[str] = []
        
        # Determine components to restore
        data_keys = set(snapshot.data.keys())
        if components:
            data_keys = data_keys.intersection(set(components))
        
        # Execute rollback based on strategy
        if strategy == RollbackStrategy.FULL:
            restored, errors = await self._rollback_full(snapshot, data_keys)
        elif strategy == RollbackStrategy.INCREMENTAL:
            restored, errors = await self._rollback_incremental(snapshot_id, data_keys)
        elif strategy == RollbackStrategy.SELECTIVE:
            restored, errors = await self._rollback_selective(snapshot, data_keys)
        elif strategy == RollbackStrategy.COMPENSATING:
            restored, errors = await self._rollback_compensating(snapshot, data_keys)
        
        duration_ms = (time.time() - start_time) * 1000
        
        result = RollbackResult(
            success=len(errors) == 0,
            snapshot_id=snapshot_id,
            strategy=strategy,
            timestamp=datetime.now(),
            components_restored=restored,
            errors=errors,
            duration_ms=duration_ms
        )
        
        # Notify listeners
        for listener in self._listeners:
            try:
                listener(result)
            except Exception:
                pass
        
        return result
    
    async def _rollback_full(
        self, 
        snapshot: Snapshot, 
        components: set
    ) -> tuple:
        """Full rollback - restore complete state"""
        restored = []
        errors = []
        
        for name in components:
            if name not in snapshot.data:
                continue
            
            if name in self._component_handlers:
                handler = self._component_handlers[name]
                try:
                    result = handler.restore(snapshot.data[name])
                    if asyncio.iscoroutine(result):
                        await result
                    restored.append(name)
                except Exception as e:
                    errors.append(f"{name}: {str(e)}")
            else:
                restored.append(name)
        
        self._current_state = copy.deepcopy(snapshot.data)
        return restored, errors
    
    async def _rollback_incremental(
        self, 
        target_snapshot_id: str, 
        components: set
    ) -> tuple:
        """Incremental rollback - reverse changes one by one"""
        restored = []
        errors = []
        
        # Find path from current to target
        current_idx = len(self._snapshot_order) - 1
        target_idx = self._snapshot_order.index(target_snapshot_id)
        
        # Roll back through each intermediate snapshot
        for idx in range(current_idx, target_idx, -1):
            snap_id = self._snapshot_order[idx]
            snapshot = self._snapshots[snap_id]
            
            # Apply reverse changes
            for name in components.intersection(snapshot.data.keys()):
                if name in self._component_handlers:
                    handler = self._component_handlers[name]
                    try:
                        # Get previous state
                        if snapshot.parent_id and snapshot.parent_id in self._snapshots:
                            prev_state = self._snapshots[snapshot.parent_id].data.get(name)
                        else:
                            prev_state = snapshot.data.get(name)
                        
                        result = handler.restore(prev_state)
                        if asyncio.iscoroutine(result):
                            await result
                        
                        if name not in restored:
                            restored.append(name)
                    except Exception as e:
                        errors.append(f"{name}: {str(e)}")
        
        return restored, errors
    
    async def _rollback_selective(
        self, 
        snapshot: Snapshot, 
        components: set
    ) -> tuple:
        """Selective rollback - restore specific components"""
        return await self._rollback_full(snapshot, components)
    
    async def _rollback_compensating(
        self, 
        snapshot: Snapshot, 
        components: set
    ) -> tuple:
        """Compensating rollback - execute compensating transactions"""
        restored = []
        errors = []
        
        for name in components:
            if name not in snapshot.data:
                continue
            
            if name in self._component_handlers:
                handler = self._component_handlers[name]
                if handler.compensate:
                    try:
                        current = self._current_state.get(name, {})
                        target = snapshot.data[name]
                        result = handler.compensate(current, target)
                        if asyncio.iscoroutine(result):
                            await result
                        restored.append(name)
                    except Exception as e:
                        errors.append(f"{name}: {str(e)}")
                else:
                    # Fall back to regular restore
                    try:
                        result = handler.restore(snapshot.data[name])
                        if asyncio.iscoroutine(result):
                            await result
                        restored.append(name)
                    except Exception as e:
                        errors.append(f"{name}: {str(e)}")
        
        return restored, errors
    
    async def _cleanup_old_snapshots(self) -> None:
        """Remove old snapshots beyond max limit"""
        while len(self._snapshot_order) > self._max_snapshots:
            old_id = self._snapshot_order.pop(0)
            del self._snapshots[old_id]
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get a snapshot by ID"""
        return self._snapshots.get(snapshot_id)
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all snapshots"""
        return [
            {
                "id": s.id,
                "type": s.type.value,
                "timestamp": s.timestamp.isoformat(),
                "components": list(s.data.keys())
            }
            for s in [self._snapshots[sid] for sid in self._snapshot_order]
        ]
    
    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """Get the most recent snapshot"""
        if not self._snapshot_order:
            return None
        return self._snapshots[self._snapshot_order[-1]]
    
    def clear_history(self) -> None:
        """Clear all snapshots"""
        self._snapshots.clear()
        self._snapshot_order.clear()


@dataclass
class ComponentHandler:
    """Handler for a component's save/restore operations"""
    name: str
    save: Callable[[], Any]
    restore: Callable[[Any], None]
    compensate: Optional[Callable[[Any, Any], None]] = None
