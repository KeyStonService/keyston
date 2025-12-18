"""
Phase Orchestrator - 階段協調器
Coordinate phase execution and dependencies

協調階段執行和依賴關係
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import logging


class ExecutionMode(Enum):
    """Phase execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ON_DEMAND = "on_demand"


class PhaseState(Enum):
    """Phase states"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class PhaseDefinition:
    """Phase definition"""
    id: str
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    timeout_seconds: int = 300
    retries: int = 0
    enabled: bool = True
    condition: Optional[Callable[[], bool]] = None
    on_enter: Optional[Callable] = None
    on_exit: Optional[Callable] = None
    on_error: Optional[Callable] = None


@dataclass
class PhaseTransition:
    """Phase transition record"""
    from_phase: str
    to_phase: str
    timestamp: datetime
    trigger: str
    success: bool
    duration_seconds: float
    error: Optional[str] = None


@dataclass
class PhaseExecutionResult:
    """Phase execution result"""
    phase_id: str
    state: PhaseState
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    output: Any = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


class PhaseOrchestrator:
    """
    Phase Orchestrator - 階段協調器
    
    Coordinates execution of all system phases:
    - Manages phase dependencies
    - Handles phase transitions
    - Monitors phase health
    - Provides automatic recovery
    """
    
    def __init__(self):
        """Initialize phase orchestrator"""
        self.logger = logging.getLogger("PhaseOrchestrator")
        
        # Phase registry
        self._phases: Dict[str, PhaseDefinition] = {}
        
        # Phase states
        self._states: Dict[str, PhaseState] = {}
        
        # Execution results
        self._results: Dict[str, PhaseExecutionResult] = {}
        
        # Transitions history
        self._transitions: List[PhaseTransition] = []
        
        # Event handlers
        self._handlers: Dict[str, List[Callable]] = {}
        
        # Current execution
        self._current_phase: Optional[str] = None
        self._execution_queue: List[str] = []
        
        # Initialize default phases
        self._init_default_phases()
    
    def _init_default_phases(self) -> None:
        """Initialize default phase definitions"""
        default_phases = [
            PhaseDefinition(
                id="phase_1",
                name="Core Autonomous Coordination",
                description="自主協調核心",
                dependencies=[]
            ),
            PhaseDefinition(
                id="phase_2",
                name="Advanced Interaction & Orchestration",
                description="進階互動與編排",
                dependencies=["phase_1"]
            ),
            PhaseDefinition(
                id="phase_3",
                name="AI Core, Bridges & Automation",
                description="AI核心、橋接與自動化",
                dependencies=["phase_1", "phase_2"]
            ),
            PhaseDefinition(
                id="phase_4",
                name="Autonomous Trust & Governance",
                description="自主信任與治理",
                dependencies=["phase_3"]
            ),
            PhaseDefinition(
                id="phase_5",
                name="AI Quality & Bug Prevention",
                description="AI品質與漏洞預防",
                dependencies=["phase_3"]
            ),
            PhaseDefinition(
                id="phase_6",
                name="AI Supreme Directive Constitution",
                description="AI最高指令憲法",
                dependencies=["phase_4", "phase_5"]
            ),
            PhaseDefinition(
                id="phase_7",
                name="Knowledge & Skills Training",
                description="知識與技能訓練",
                dependencies=["phase_6"]
            ),
            PhaseDefinition(
                id="phase_8",
                name="Execution Engine & Tech Stack",
                description="執行引擎與技術棧",
                dependencies=["phase_7"]
            ),
            PhaseDefinition(
                id="phase_9",
                name="Complete Execution Architecture",
                description="完整執行架構",
                dependencies=["phase_8"]
            ),
            PhaseDefinition(
                id="phase_10",
                name="Safety Mechanisms",
                description="安全機制",
                dependencies=["phase_9"]
            ),
            PhaseDefinition(
                id="phase_11",
                name="Intelligent Monitoring & Remediation",
                description="智能監控與修復",
                dependencies=["phase_10"]
            ),
            PhaseDefinition(
                id="phase_12",
                name="CI Error Auto-Handler",
                description="CI錯誤自動處理",
                dependencies=["phase_11"]
            ),
            PhaseDefinition(
                id="phase_13",
                name="Deep Verifiable YAML System",
                description="深度可驗證YAML系統",
                dependencies=["phase_12"]
            ),
        ]
        
        for phase in default_phases:
            self.register_phase(phase)
    
    def register_phase(self, definition: PhaseDefinition) -> None:
        """Register a phase"""
        self._phases[definition.id] = definition
        self._states[definition.id] = PhaseState.PENDING
        self.logger.debug(f"Registered phase: {definition.id}")
    
    def get_phase(self, phase_id: str) -> Optional[PhaseDefinition]:
        """Get a phase definition"""
        return self._phases.get(phase_id)
    
    def get_state(self, phase_id: str) -> Optional[PhaseState]:
        """Get current state of a phase"""
        return self._states.get(phase_id)
    
    def get_all_phases(self) -> Dict[str, PhaseDefinition]:
        """Get all phases"""
        return self._phases.copy()
    
    def get_execution_order(self) -> List[str]:
        """
        Get execution order based on dependencies
        
        Returns:
            List of phase IDs in execution order
        """
        visited: Set[str] = set()
        order: List[str] = []
        
        def visit(phase_id: str):
            if phase_id in visited:
                return
            visited.add(phase_id)
            
            phase = self._phases.get(phase_id)
            if phase:
                for dep in phase.dependencies:
                    visit(dep)
                order.append(phase_id)
        
        for phase_id in self._phases:
            visit(phase_id)
        
        return order
    
    def can_execute(self, phase_id: str) -> bool:
        """
        Check if a phase can be executed
        
        Args:
            phase_id: Phase ID to check
            
        Returns:
            True if phase can be executed
        """
        phase = self._phases.get(phase_id)
        if not phase:
            return False
        
        if not phase.enabled:
            return False
        
        # Check dependencies
        for dep in phase.dependencies:
            dep_state = self._states.get(dep)
            if dep_state != PhaseState.COMPLETED:
                return False
        
        # Check condition
        if phase.condition and not phase.condition():
            return False
        
        return True
    
    def execute_phase(self, phase_id: str, executor: Optional[Callable] = None) -> PhaseExecutionResult:
        """
        Execute a single phase
        
        Args:
            phase_id: Phase ID to execute
            executor: Optional executor function
            
        Returns:
            Execution result
        """
        phase = self._phases.get(phase_id)
        if not phase:
            return PhaseExecutionResult(
                phase_id=phase_id,
                state=PhaseState.FAILED,
                started_at=datetime.now(),
                error="Phase not found"
            )
        
        if not self.can_execute(phase_id):
            return PhaseExecutionResult(
                phase_id=phase_id,
                state=PhaseState.SKIPPED,
                started_at=datetime.now(),
                error="Dependencies not satisfied or condition not met"
            )
        
        self.logger.info(f"Executing phase: {phase_id}")
        self._current_phase = phase_id
        self._states[phase_id] = PhaseState.RUNNING
        
        started_at = datetime.now()
        result = PhaseExecutionResult(
            phase_id=phase_id,
            state=PhaseState.RUNNING,
            started_at=started_at
        )
        
        try:
            # Call on_enter hook
            if phase.on_enter:
                phase.on_enter()
            
            # Execute phase
            if executor:
                output = executor()
                result.output = output
            
            # Call on_exit hook
            if phase.on_exit:
                phase.on_exit()
            
            result.state = PhaseState.COMPLETED
            self._states[phase_id] = PhaseState.COMPLETED
            self.logger.info(f"Phase completed: {phase_id}")
            
        except Exception as e:
            result.state = PhaseState.FAILED
            result.error = str(e)
            self._states[phase_id] = PhaseState.FAILED
            self.logger.error(f"Phase failed: {phase_id} - {e}")
            
            # Call on_error hook
            if phase.on_error:
                phase.on_error(e)
        
        finally:
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - started_at).total_seconds()
            self._results[phase_id] = result
            self._current_phase = None
        
        return result
    
    def execute_all(self, executors: Optional[Dict[str, Callable]] = None) -> Dict[str, PhaseExecutionResult]:
        """
        Execute all phases in order
        
        Args:
            executors: Optional dict of phase ID to executor function
            
        Returns:
            Dict of phase ID to execution result
        """
        executors = executors or {}
        results: Dict[str, PhaseExecutionResult] = {}
        
        order = self.get_execution_order()
        self.logger.info(f"Executing phases in order: {order}")
        
        for phase_id in order:
            executor = executors.get(phase_id)
            result = self.execute_phase(phase_id, executor)
            results[phase_id] = result
            
            # Stop on failure if phase is required
            if result.state == PhaseState.FAILED:
                phase = self._phases.get(phase_id)
                if phase and phase.enabled:
                    self.logger.error(f"Stopping execution due to phase failure: {phase_id}")
                    break
        
        return results
    
    def transition(self, from_phase: str, to_phase: str, trigger: str) -> PhaseTransition:
        """
        Record a phase transition
        
        Args:
            from_phase: Source phase ID
            to_phase: Target phase ID
            trigger: Transition trigger
            
        Returns:
            Transition record
        """
        started = datetime.now()
        success = True
        error = None
        
        try:
            # Check if transition is valid
            to_phase_def = self._phases.get(to_phase)
            if to_phase_def and from_phase not in to_phase_def.dependencies:
                if to_phase_def.dependencies:  # Only check if there are dependencies
                    pass  # Allow transitions even if not a direct dependency
        except Exception as e:
            success = False
            error = str(e)
        
        transition = PhaseTransition(
            from_phase=from_phase,
            to_phase=to_phase,
            timestamp=started,
            trigger=trigger,
            success=success,
            duration_seconds=0.0,
            error=error
        )
        
        self._transitions.append(transition)
        self.logger.debug(f"Transition: {from_phase} -> {to_phase} ({trigger})")
        
        return transition
    
    def get_transitions(self) -> List[PhaseTransition]:
        """Get all transitions"""
        return self._transitions.copy()
    
    def reset_phase(self, phase_id: str) -> bool:
        """
        Reset a phase to pending state
        
        Args:
            phase_id: Phase ID to reset
            
        Returns:
            True if reset successful
        """
        if phase_id in self._states:
            self._states[phase_id] = PhaseState.PENDING
            if phase_id in self._results:
                del self._results[phase_id]
            self.logger.info(f"Phase reset: {phase_id}")
            return True
        return False
    
    def reset_all(self) -> None:
        """Reset all phases"""
        for phase_id in self._phases:
            self.reset_phase(phase_id)
        self._transitions.clear()
        self.logger.info("All phases reset")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get execution summary
        
        Returns:
            Summary dict
        """
        total = len(self._phases)
        pending = sum(1 for s in self._states.values() if s == PhaseState.PENDING)
        completed = sum(1 for s in self._states.values() if s == PhaseState.COMPLETED)
        failed = sum(1 for s in self._states.values() if s == PhaseState.FAILED)
        skipped = sum(1 for s in self._states.values() if s == PhaseState.SKIPPED)
        
        return {
            "total_phases": total,
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "completion_rate": completed / total if total > 0 else 0,
            "transitions": len(self._transitions),
            "current_phase": self._current_phase
        }
    
    @property
    def current_phase(self) -> Optional[str]:
        """Get current executing phase"""
        return self._current_phase
