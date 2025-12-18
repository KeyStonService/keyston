"""
System Orchestrator - High-level system management

This module provides high-level orchestration for the entire SynergyMesh
system, managing workflows, scheduling, and system-wide operations.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = 'pending'
    RUNNING = 'running'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class TaskType(Enum):
    """System task types"""
    INITIALIZATION = 'initialization'
    HEALTH_CHECK = 'health_check'
    MAINTENANCE = 'maintenance'
    OPTIMIZATION = 'optimization'
    BACKUP = 'backup'
    CLEANUP = 'cleanup'
    CUSTOM = 'custom'


@dataclass
class OrchestratorConfig:
    """Configuration for the system orchestrator"""
    name: str = 'synergymesh-orchestrator'
    max_concurrent_workflows: int = 10
    max_concurrent_tasks: int = 50
    default_task_timeout_seconds: int = 300
    health_check_interval_seconds: int = 60
    enable_auto_recovery: bool = True
    enable_performance_optimization: bool = True
    log_level: str = 'INFO'


@dataclass
class ScheduledTask:
    """A scheduled system task"""
    id: str
    name: str
    task_type: TaskType
    handler: Callable
    interval_seconds: int
    next_run: datetime
    last_run: Optional[datetime] = None
    enabled: bool = True
    run_count: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """A system workflow"""
    id: str
    name: str
    steps: List[Dict[str, Any]]
    state: WorkflowState = WorkflowState.PENDING
    current_step: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state.value,
            'current_step': self.current_step,
            'total_steps': len(self.steps),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'results': self.results,
            'error': self.error,
            'metadata': self.metadata
        }


class SystemOrchestrator:
    """
    System Orchestrator - 系統編排器
    
    High-level orchestration providing:
    - Workflow management and execution
    - Task scheduling
    - System-wide health monitoring
    - Performance optimization
    - Auto-recovery mechanisms
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """Initialize the system orchestrator"""
        self.config = config or OrchestratorConfig()
        
        # Workflows
        self._workflows: Dict[str, Workflow] = {}
        self._running_workflows: Dict[str, asyncio.Task] = {}
        
        # Scheduled tasks
        self._scheduled_tasks: Dict[str, ScheduledTask] = {}
        self._scheduler_task: Optional[asyncio.Task] = None
        
        # Task semaphore for concurrency control
        self._workflow_semaphore: Optional[asyncio.Semaphore] = None
        self._task_semaphore: Optional[asyncio.Semaphore] = None
        
        # State
        self._is_running = False
        self._startup_time: Optional[datetime] = None
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
    async def start(self) -> None:
        """Start the orchestrator"""
        if self._is_running:
            return
            
        self._is_running = True
        self._startup_time = datetime.now(timezone.utc)
        self._workflow_semaphore = asyncio.Semaphore(self.config.max_concurrent_workflows)
        self._task_semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        
        # Start scheduler
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        await self._emit_event('orchestrator_started', {'timestamp': self._startup_time})
        logger.info("SystemOrchestrator started")
        
    async def stop(self) -> None:
        """Stop the orchestrator"""
        self._is_running = False
        
        # Stop scheduler
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
                
        # Cancel running workflows
        for workflow_id, task in list(self._running_workflows.items()):
            task.cancel()
            workflow = self._workflows.get(workflow_id)
            if workflow:
                workflow.state = WorkflowState.CANCELLED
                
        self._running_workflows.clear()
        
        await self._emit_event('orchestrator_stopped', {'timestamp': datetime.now(timezone.utc)})
        logger.info("SystemOrchestrator stopped")
        
    async def execute_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """
        Execute a workflow
        
        Args:
            name: Workflow name
            steps: List of workflow steps
            metadata: Optional workflow metadata
            
        Returns:
            Workflow object
        """
        workflow = Workflow(
            id=str(uuid4()),
            name=name,
            steps=steps,
            metadata=metadata or {}
        )
        
        self._workflows[workflow.id] = workflow
        
        async with self._workflow_semaphore:
            await self._run_workflow(workflow)
            
        return workflow
        
    async def execute_workflow_async(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a workflow asynchronously
        
        Returns:
            Workflow ID
        """
        workflow = Workflow(
            id=str(uuid4()),
            name=name,
            steps=steps,
            metadata=metadata or {}
        )
        
        self._workflows[workflow.id] = workflow
        
        task = asyncio.create_task(self._run_workflow_with_semaphore(workflow))
        self._running_workflows[workflow.id] = task
        
        return workflow.id
        
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        task = self._running_workflows.get(workflow_id)
        if task and not task.done():
            task.cancel()
            
            workflow = self._workflows.get(workflow_id)
            if workflow:
                workflow.state = WorkflowState.CANCELLED
                workflow.completed_at = datetime.now(timezone.utc)
                
            return True
        return False
        
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self._workflows.get(workflow_id)
        
    def list_workflows(
        self,
        state: Optional[WorkflowState] = None
    ) -> List[Workflow]:
        """List workflows with optional state filter"""
        workflows = list(self._workflows.values())
        if state:
            workflows = [w for w in workflows if w.state == state]
        return workflows
        
    def schedule_task(
        self,
        name: str,
        task_type: TaskType,
        handler: Callable,
        interval_seconds: int,
        enabled: bool = True
    ) -> str:
        """
        Schedule a recurring task
        
        Args:
            name: Task name
            task_type: Type of task
            handler: Task handler function
            interval_seconds: Interval between runs
            enabled: Whether task is enabled
            
        Returns:
            Task ID
        """
        task_id = str(uuid4())
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type=task_type,
            handler=handler,
            interval_seconds=interval_seconds,
            next_run=datetime.now(timezone.utc),
            enabled=enabled
        )
        
        self._scheduled_tasks[task_id] = task
        logger.info(f"Scheduled task: {name} (every {interval_seconds}s)")
        return task_id
        
    def unschedule_task(self, task_id: str) -> bool:
        """Unschedule a task"""
        return self._scheduled_tasks.pop(task_id, None) is not None
        
    def enable_task(self, task_id: str) -> bool:
        """Enable a scheduled task"""
        task = self._scheduled_tasks.get(task_id)
        if task:
            task.enabled = True
            return True
        return False
        
    def disable_task(self, task_id: str) -> bool:
        """Disable a scheduled task"""
        task = self._scheduled_tasks.get(task_id)
        if task:
            task.enabled = False
            return True
        return False
        
    def get_scheduled_tasks(self) -> List[ScheduledTask]:
        """Get all scheduled tasks"""
        return list(self._scheduled_tasks.values())
        
    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        workflow_states = {}
        for workflow in self._workflows.values():
            state = workflow.state.value
            workflow_states[state] = workflow_states.get(state, 0) + 1
            
        uptime = 0.0
        if self._startup_time:
            uptime = (datetime.now(timezone.utc) - self._startup_time).total_seconds()
            
        return {
            'is_running': self._is_running,
            'uptime_seconds': uptime,
            'total_workflows': len(self._workflows),
            'running_workflows': len(self._running_workflows),
            'workflow_states': workflow_states,
            'scheduled_tasks': len(self._scheduled_tasks),
            'enabled_tasks': sum(1 for t in self._scheduled_tasks.values() if t.enabled)
        }
        
    async def _run_workflow_with_semaphore(self, workflow: Workflow) -> None:
        """Run workflow with semaphore"""
        async with self._workflow_semaphore:
            await self._run_workflow(workflow)
            
    async def _run_workflow(self, workflow: Workflow) -> None:
        """Execute a workflow"""
        workflow.state = WorkflowState.RUNNING
        workflow.started_at = datetime.now(timezone.utc)
        
        await self._emit_event('workflow_started', {'workflow_id': workflow.id})
        
        try:
            for i, step in enumerate(workflow.steps):
                workflow.current_step = i
                
                step_name = step.get('name', f'step_{i}')
                step_handler = step.get('handler')
                step_args = step.get('args', {})
                
                try:
                    if step_handler:
                        if asyncio.iscoroutinefunction(step_handler):
                            result = await step_handler(**step_args)
                        else:
                            result = step_handler(**step_args)
                    else:
                        # Simulated step execution
                        await asyncio.sleep(0.01)
                        result = {'status': 'completed'}
                        
                    workflow.results[step_name] = result
                    
                except Exception as e:
                    workflow.results[step_name] = {'error': str(e)}
                    
                    # Check if step is critical
                    if step.get('critical', False):
                        raise
                        
            workflow.state = WorkflowState.COMPLETED
            workflow.completed_at = datetime.now(timezone.utc)
            
            await self._emit_event('workflow_completed', {
                'workflow_id': workflow.id,
                'results': workflow.results
            })
            
        except asyncio.CancelledError:
            workflow.state = WorkflowState.CANCELLED
            workflow.completed_at = datetime.now(timezone.utc)
            raise
            
        except Exception as e:
            workflow.state = WorkflowState.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.now(timezone.utc)
            
            await self._emit_event('workflow_failed', {
                'workflow_id': workflow.id,
                'error': str(e)
            })
            
            logger.error(f"Workflow {workflow.id} failed: {e}")
            
        finally:
            self._running_workflows.pop(workflow.id, None)
            
    async def _scheduler_loop(self) -> None:
        """Scheduler loop for running scheduled tasks"""
        while self._is_running:
            try:
                now = datetime.now(timezone.utc)
                
                for task in self._scheduled_tasks.values():
                    if not task.enabled:
                        continue
                        
                    if now >= task.next_run:
                        await self._execute_scheduled_task(task)
                        # Use timedelta for proper date arithmetic
                        from datetime import timedelta
                        task.next_run = now + timedelta(seconds=task.interval_seconds)
                        
                await asyncio.sleep(1)  # Check every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(5)
                
    async def _execute_scheduled_task(self, task: ScheduledTask) -> None:
        """Execute a scheduled task"""
        async with self._task_semaphore:
            try:
                task.last_run = datetime.now(timezone.utc)
                task.run_count += 1
                
                if asyncio.iscoroutinefunction(task.handler):
                    await task.handler()
                else:
                    task.handler()
                    
            except Exception as e:
                task.error_count += 1
                logger.error(f"Scheduled task {task.name} failed: {e}")
                
    async def _emit_event(self, event: str, data: Any) -> None:
        """Emit an event to handlers"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Event handler error for {event}: {e}")


# Factory function
def create_system_orchestrator(
    config: Optional[OrchestratorConfig] = None
) -> SystemOrchestrator:
    """Create a new SystemOrchestrator instance"""
    return SystemOrchestrator(config)
