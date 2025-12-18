"""
Automation Pipeline - 自動化管道
End-to-end automation workflow

端到端自動化工作流
"""

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class PipelineTask:
    """Task definition for pipeline"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: str = "generic"
    priority: TaskPriority = TaskPriority.MEDIUM
    parameters: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retries: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    status: TaskStatus
    started_at: datetime
    completed_at: datetime | None = None
    duration_seconds: float = 0.0
    output: Any = None
    error: str | None = None
    retry_count: int = 0
    phases_used: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    # Execution
    max_concurrent_tasks: int = 5
    default_timeout_seconds: int = 300
    enable_retries: bool = True
    max_retries: int = 3

    # Queue
    queue_size: int = 100
    priority_queue: bool = True

    # Routing
    auto_route_tasks: bool = True

    # Learning
    enable_learning: bool = True
    track_metrics: bool = True

    # Safety
    enable_safety_checks: bool = True
    dry_run: bool = False


class AutomationPipeline:
    """
    Automation Pipeline - 自動化管道
    
    End-to-end automation workflow that:
    - Routes tasks to appropriate phases
    - Manages task execution
    - Aggregates results
    - Enables continuous improvement
    """

    def __init__(self, config: PipelineConfig | None = None):
        """Initialize automation pipeline"""
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger("AutomationPipeline")

        # Task management
        self._queue: list[PipelineTask] = []
        self._running: dict[str, PipelineTask] = {}
        self._completed: dict[str, TaskResult] = {}

        # Task handlers
        self._handlers: dict[str, Callable] = {}

        # Phase routing
        self._phase_routes: dict[str, list[str]] = self._init_phase_routes()

        # Metrics
        self._metrics = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_duration_seconds": 0.0
        }

        # Learning
        self._patterns: dict[str, dict[str, Any]] = {}

    def _init_phase_routes(self) -> dict[str, list[str]]:
        """Initialize phase routing rules"""
        return {
            "natural_language": ["phase_1", "phase_2"],
            "intent_understanding": ["phase_2"],
            "decision": ["phase_3", "phase_4"],
            "code_generation": ["phase_3"],
            "deployment": ["phase_3"],
            "trust_evaluation": ["phase_4"],
            "governance": ["phase_4"],
            "quality_check": ["phase_5"],
            "hallucination_check": ["phase_5"],
            "bug_detection": ["phase_5"],
            "constitution_check": ["phase_6"],
            "guardrail_check": ["phase_6"],
            "training": ["phase_7"],
            "expert_consultation": ["phase_7"],
            "execution": ["phase_8", "phase_9"],
            "tool_execution": ["phase_9"],
            "safety_check": ["phase_10"],
            "circuit_breaker": ["phase_10"],
            "monitoring": ["phase_11"],
            "remediation": ["phase_11"],
            "ci_error": ["phase_12"],
            "auto_fix": ["phase_12"],
            "yaml_validation": ["phase_13"],
            "policy_check": ["phase_13"],
            "slsa_compliance": ["phase_13"],
        }

    def submit_task(self, task: PipelineTask) -> str:
        """
        Submit a task to the pipeline
        
        Args:
            task: Task to submit
            
        Returns:
            Task ID
        """
        if len(self._queue) >= self.config.queue_size:
            raise ValueError("Queue is full")

        # Add to queue
        if self.config.priority_queue:
            # Insert based on priority
            inserted = False
            for i, queued_task in enumerate(self._queue):
                if task.priority.value > queued_task.priority.value:
                    self._queue.insert(i, task)
                    inserted = True
                    break
            if not inserted:
                self._queue.append(task)
        else:
            self._queue.append(task)

        self._metrics["tasks_submitted"] += 1
        self.logger.info(f"Task submitted: {task.id} ({task.task_type})")

        return task.id

    def get_next_task(self) -> PipelineTask | None:
        """Get next task from queue"""
        if not self._queue:
            return None

        # Check dependencies
        for i, task in enumerate(self._queue):
            deps_satisfied = all(
                dep_id in self._completed
                for dep_id in task.dependencies
            )
            if deps_satisfied:
                return self._queue.pop(i)

        return None

    def route_task(self, task: PipelineTask) -> list[str]:
        """
        Route a task to appropriate phases
        
        Args:
            task: Task to route
            
        Returns:
            List of phase IDs
        """
        if not self.config.auto_route_tasks:
            return []

        phases = self._phase_routes.get(task.task_type, [])

        if not phases:
            # Default routing based on task type keywords
            task_type_lower = task.task_type.lower()

            if "language" in task_type_lower or "nlp" in task_type_lower:
                phases = ["phase_1", "phase_2"]
            elif "decision" in task_type_lower or "ai" in task_type_lower:
                phases = ["phase_3"]
            elif "trust" in task_type_lower or "governance" in task_type_lower:
                phases = ["phase_4"]
            elif "quality" in task_type_lower or "bug" in task_type_lower:
                phases = ["phase_5"]
            elif "constitution" in task_type_lower or "guardrail" in task_type_lower:
                phases = ["phase_6"]
            elif "training" in task_type_lower or "expert" in task_type_lower:
                phases = ["phase_7"]
            elif "execution" in task_type_lower or "tool" in task_type_lower:
                phases = ["phase_8", "phase_9"]
            elif "safety" in task_type_lower:
                phases = ["phase_10"]
            elif "monitor" in task_type_lower or "remediation" in task_type_lower:
                phases = ["phase_11"]
            elif "ci" in task_type_lower or "error" in task_type_lower:
                phases = ["phase_12"]
            elif "yaml" in task_type_lower or "validation" in task_type_lower:
                phases = ["phase_13"]

        return phases

    def execute_task(self, task: PipelineTask, handler: Callable | None = None) -> TaskResult:
        """
        Execute a task
        
        Args:
            task: Task to execute
            handler: Optional handler function
            
        Returns:
            Task result
        """
        self.logger.info(f"Executing task: {task.id}")

        started_at = datetime.now()
        result = TaskResult(
            task_id=task.id,
            status=TaskStatus.RUNNING,
            started_at=started_at
        )

        # Track running task
        self._running[task.id] = task

        try:
            # Safety checks
            if self.config.enable_safety_checks:
                safety_result = self._safety_check(task)
                if not safety_result["safe"]:
                    raise ValueError(f"Safety check failed: {safety_result['reason']}")

            # Route to phases
            phases = self.route_task(task)
            result.phases_used = phases

            # Dry run check
            if self.config.dry_run:
                result.status = TaskStatus.COMPLETED
                result.output = {"dry_run": True, "phases": phases}
            else:
                # Execute handler
                if handler:
                    output = handler(task)
                elif task.task_type in self._handlers:
                    output = self._handlers[task.task_type](task)
                else:
                    # Default execution
                    output = self._default_handler(task)

                result.output = output
                result.status = TaskStatus.COMPLETED

            self._metrics["tasks_completed"] += 1
            self.logger.info(f"Task completed: {task.id}")

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            self._metrics["tasks_failed"] += 1
            self.logger.error(f"Task failed: {task.id} - {e}")

            # Retry if enabled
            if self.config.enable_retries and result.retry_count < self.config.max_retries:
                result.retry_count += 1
                result.status = TaskStatus.RETRYING
                self.submit_task(task)

        finally:
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - started_at).total_seconds()
            self._metrics["total_duration_seconds"] += result.duration_seconds

            self._completed[task.id] = result
            if task.id in self._running:
                del self._running[task.id]

            # Learn from execution
            if self.config.enable_learning:
                self._learn_from_execution(task, result)

        return result

    def _safety_check(self, task: PipelineTask) -> dict[str, Any]:
        """Perform safety check on task"""
        # Check for dangerous operations
        dangerous_keywords = ["delete", "drop", "truncate", "rm -rf", "format"]
        task_str = str(task.parameters).lower()

        for keyword in dangerous_keywords:
            if keyword in task_str:
                return {
                    "safe": False,
                    "reason": f"Task contains dangerous keyword: {keyword}"
                }

        return {"safe": True, "reason": None}

    def _default_handler(self, task: PipelineTask) -> Any:
        """Default task handler"""
        return {
            "task_id": task.id,
            "task_type": task.task_type,
            "parameters": task.parameters,
            "processed": True,
            "phases": self.route_task(task)
        }

    def _learn_from_execution(self, task: PipelineTask, result: TaskResult) -> None:
        """Learn from task execution"""
        pattern_key = task.task_type

        if pattern_key not in self._patterns:
            self._patterns[pattern_key] = {
                "count": 0,
                "success_count": 0,
                "avg_duration": 0.0,
                "common_phases": {}
            }

        pattern = self._patterns[pattern_key]
        pattern["count"] += 1

        if result.status == TaskStatus.COMPLETED:
            pattern["success_count"] += 1

        # Update average duration
        pattern["avg_duration"] = (
            (pattern["avg_duration"] * (pattern["count"] - 1) + result.duration_seconds)
            / pattern["count"]
        )

        # Track common phases
        for phase in result.phases_used:
            if phase not in pattern["common_phases"]:
                pattern["common_phases"][phase] = 0
            pattern["common_phases"][phase] += 1

    def register_handler(self, task_type: str, handler: Callable) -> None:
        """Register a task handler"""
        self._handlers[task_type] = handler
        self.logger.debug(f"Handler registered for: {task_type}")

    def add_route(self, task_type: str, phases: list[str]) -> None:
        """Add a phase route"""
        self._phase_routes[task_type] = phases

    def get_task_result(self, task_id: str) -> TaskResult | None:
        """Get result for a task"""
        return self._completed.get(task_id)

    def get_queue_status(self) -> dict[str, Any]:
        """Get queue status"""
        return {
            "queued": len(self._queue),
            "running": len(self._running),
            "completed": len(self._completed),
            "queue_capacity": self.config.queue_size,
            "utilization": len(self._queue) / self.config.queue_size if self.config.queue_size > 0 else 0
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get pipeline metrics"""
        metrics = self._metrics.copy()

        # Calculate additional metrics
        total = metrics["tasks_submitted"]
        if total > 0:
            metrics["success_rate"] = metrics["tasks_completed"] / total
            metrics["avg_duration"] = metrics["total_duration_seconds"] / total
        else:
            metrics["success_rate"] = 0
            metrics["avg_duration"] = 0

        return metrics

    def get_patterns(self) -> dict[str, dict[str, Any]]:
        """Get learned patterns"""
        return self._patterns.copy()

    def clear_queue(self) -> int:
        """Clear the task queue"""
        count = len(self._queue)
        self._queue.clear()
        return count

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a queued task"""
        for i, task in enumerate(self._queue):
            if task.id == task_id:
                self._queue.pop(i)
                result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.CANCELLED,
                    started_at=datetime.now(),
                    completed_at=datetime.now()
                )
                self._completed[task_id] = result
                return True
        return False
