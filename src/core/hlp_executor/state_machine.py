"""
State Machine - 7-State Transition Flow with Recovery

This module implements the state machine orchestration for HLP Executor
with support for pause/resume and recovery operations.
"""

from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


class ExecutionState(Enum):
    """7-state transition flow for execution"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    RESUMED = "resumed"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class StateTransition:
    """
    Records a state transition
    
    Attributes:
        from_state: Previous state
        to_state: New state
        timestamp: When transition occurred
        reason: Reason for transition
        metadata: Additional context
    """
    from_state: ExecutionState
    to_state: ExecutionState
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateMachine:
    """
    State Machine Orchestrator
    
    Manages execution state transitions with proper validation
    and event handling.
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        ExecutionState.PENDING: [ExecutionState.RUNNING],
        ExecutionState.RUNNING: [
            ExecutionState.COMPLETED,
            ExecutionState.FAILED,
            ExecutionState.PAUSED,
        ],
        ExecutionState.PAUSED: [ExecutionState.RESUMED, ExecutionState.FAILED],
        ExecutionState.RESUMED: [
            ExecutionState.RUNNING,
            ExecutionState.COMPLETED,
            ExecutionState.FAILED,
        ],
        ExecutionState.FAILED: [ExecutionState.RECOVERING],
        ExecutionState.RECOVERING: [
            ExecutionState.RUNNING,
            ExecutionState.FAILED,
            ExecutionState.COMPLETED,
        ],
        ExecutionState.COMPLETED: [],  # Terminal state
    }
    
    def __init__(self, execution_id: str):
        """
        Initialize state machine
        
        Args:
            execution_id: Unique identifier for this execution
        """
        self.execution_id = execution_id
        self.current_state = ExecutionState.PENDING
        self.history: List[StateTransition] = []
        self.listeners: Dict[ExecutionState, List[Callable]] = {
            state: [] for state in ExecutionState
        }
        self.metadata: Dict[str, Any] = {}
        
    def add_listener(
        self, state: ExecutionState, callback: Callable[[StateTransition], None]
    ) -> None:
        """
        Add a listener for state transitions
        
        Args:
            state: State to listen for
            callback: Function to call when entering this state
        """
        self.listeners[state].append(callback)
        
    async def transition_to(
        self, new_state: ExecutionState, reason: str = "", **metadata
    ) -> bool:
        """
        Transition to a new state
        
        Args:
            new_state: Target state
            reason: Reason for transition
            **metadata: Additional context
            
        Returns:
            bool: True if transition successful
            
        Raises:
            ValueError: If transition is invalid
        """
        # Check if transition is valid
        if new_state not in self.VALID_TRANSITIONS.get(self.current_state, []):
            raise ValueError(
                f"Invalid transition from {self.current_state.value} "
                f"to {new_state.value}"
            )
            
        # Record transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            reason=reason,
            metadata=metadata,
        )
        self.history.append(transition)
        
        # Update state
        old_state = self.current_state
        self.current_state = new_state
        
        # Notify listeners
        for callback in self.listeners[new_state]:
            if asyncio.iscoroutinefunction(callback):
                await callback(transition)
            else:
                callback(transition)
                
        return True
        
    def can_transition_to(self, new_state: ExecutionState) -> bool:
        """
        Check if transition to new state is valid
        
        Args:
            new_state: State to check
            
        Returns:
            bool: True if transition is valid
        """
        return new_state in self.VALID_TRANSITIONS.get(self.current_state, [])
        
    def get_state(self) -> ExecutionState:
        """Get current state"""
        return self.current_state
        
    def is_terminal_state(self) -> bool:
        """Check if in terminal state (no further transitions)"""
        return len(self.VALID_TRANSITIONS.get(self.current_state, [])) == 0
        
    def get_history(self) -> List[StateTransition]:
        """Get state transition history"""
        return self.history.copy()
        
    def get_summary(self) -> Dict[str, Any]:
        """
        Get state machine summary
        
        Returns:
            Dict with current state and statistics
        """
        return {
            "execution_id": self.execution_id,
            "current_state": self.current_state.value,
            "is_terminal": self.is_terminal_state(),
            "total_transitions": len(self.history),
            "metadata": self.metadata,
        }


class ExecutionOrchestrator:
    """
    Orchestrates execution with state machine management
    
    Combines state machine with execution logic and provides
    high-level control over workflow execution.
    """
    
    def __init__(self, execution_id: str):
        """
        Initialize orchestrator
        
        Args:
            execution_id: Unique identifier for this execution
        """
        self.execution_id = execution_id
        self.state_machine = StateMachine(execution_id)
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[Exception] = None
        
    async def start(self) -> None:
        """Start execution"""
        self.start_time = datetime.now()
        await self.state_machine.transition_to(
            ExecutionState.RUNNING, reason="Execution started"
        )
        
    async def pause(self, reason: str = "") -> None:
        """Pause execution"""
        await self.state_machine.transition_to(
            ExecutionState.PAUSED, reason=reason or "Execution paused"
        )
        
    async def resume(self) -> None:
        """Resume execution"""
        await self.state_machine.transition_to(
            ExecutionState.RESUMED, reason="Execution resumed"
        )
        # Transition back to running
        await self.state_machine.transition_to(
            ExecutionState.RUNNING, reason="Resumed to running state"
        )
        
    async def complete(self) -> None:
        """Mark execution as completed"""
        self.end_time = datetime.now()
        await self.state_machine.transition_to(
            ExecutionState.COMPLETED, reason="Execution completed successfully"
        )
        
    async def fail(self, error: Exception) -> None:
        """Mark execution as failed"""
        self.error = error
        self.end_time = datetime.now()
        await self.state_machine.transition_to(
            ExecutionState.FAILED, reason=f"Execution failed: {str(error)}"
        )
        
    async def recover(self) -> None:
        """Attempt recovery from failure"""
        await self.state_machine.transition_to(
            ExecutionState.RECOVERING, reason="Attempting recovery"
        )
        
    def get_duration(self) -> Optional[float]:
        """
        Get execution duration in seconds
        
        Returns:
            Duration in seconds, or None if not started
        """
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive execution status
        
        Returns:
            Dict with execution details
        """
        return {
            "execution_id": self.execution_id,
            "state": self.state_machine.get_state().value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration(),
            "error": str(self.error) if self.error else None,
            "state_summary": self.state_machine.get_summary(),
        }
