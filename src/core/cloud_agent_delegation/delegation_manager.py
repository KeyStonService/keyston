"""
Delegation Manager - Central management for cloud agent delegation

This module provides centralized management for delegating tasks
to cloud-based agents across multiple cloud providers.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class DelegationStatus(Enum):
    """Status of a delegation"""
    PENDING = 'pending'
    QUEUED = 'queued'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    RETRYING = 'retrying'


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


@dataclass
class DelegationConfig:
    """Configuration for delegation"""
    name: str
    enabled: bool = True
    environment: str = 'production'
    max_concurrent_tasks: int = 100
    default_timeout: int = 300  # seconds
    retry_enabled: bool = True
    max_retries: int = 3
    retry_delay: int = 1  # seconds
    backoff_multiplier: float = 2.0
    queue_config: Dict[str, Any] = field(default_factory=dict)
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'environment': self.environment,
            'maxConcurrentTasks': self.max_concurrent_tasks,
            'defaultTimeout': self.default_timeout,
            'retryEnabled': self.retry_enabled,
            'maxRetries': self.max_retries,
            'retryDelay': self.retry_delay,
            'backoffMultiplier': self.backoff_multiplier,
            'queueConfig': self.queue_config,
            'monitoringConfig': self.monitoring_config
        }


@dataclass
class Task:
    """Represents a task to be delegated"""
    id: str
    name: str
    type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'payload': self.payload,
            'priority': self.priority.value,
            'timeout': self.timeout,
            'metadata': self.metadata,
            'createdAt': self.created_at.isoformat()
        }


@dataclass
class DelegationResult:
    """Result of a delegation"""
    task_id: str
    status: DelegationStatus
    provider: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    attempts: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'taskId': self.task_id,
            'status': self.status.value,
            'provider': self.provider,
            'result': self.result,
            'error': self.error,
            'startedAt': self.started_at.isoformat() if self.started_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'durationMs': self.duration_ms,
            'attempts': self.attempts,
            'metadata': self.metadata
        }
        
    @property
    def is_success(self) -> bool:
        """Check if delegation was successful"""
        return self.status == DelegationStatus.COMPLETED


class DelegationManager:
    """
    Central manager for cloud agent delegation
    
    Provides functionality to:
    - Delegate tasks to cloud-based agents
    - Manage task queues and priorities
    - Handle retries and failover
    - Monitor delegation status
    """
    
    def __init__(
        self,
        config: DelegationConfig,
        router: Optional[Any] = None,
        load_balancer: Optional[Any] = None
    ):
        """
        Initialize the delegation manager
        
        Args:
            config: Delegation configuration
            router: Optional task router
            load_balancer: Optional load balancer
        """
        self.config = config
        self._router = router
        self._load_balancer = load_balancer
        self._tasks: Dict[str, Task] = {}
        self._results: Dict[str, DelegationResult] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._providers: Dict[str, Any] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._is_running: bool = False
        self._task_semaphore: Optional[asyncio.Semaphore] = None
        
    async def start(self) -> None:
        """Start the delegation manager"""
        if self._is_running:
            return
            
        self._is_running = True
        self._task_semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        
        logger.info(f'DelegationManager started: {self.config.name}')
        await self._emit_event('manager_started', {'config': self.config.to_dict()})
        
    async def stop(self) -> None:
        """Stop the delegation manager"""
        self._is_running = False
        
        # Cancel running tasks
        for task_id, task in list(self._running_tasks.items()):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        self._running_tasks.clear()
        
        logger.info('DelegationManager stopped')
        await self._emit_event('manager_stopped', {})
        
    def register_provider(self, name: str, provider: Any) -> None:
        """Register a cloud provider"""
        self._providers[name] = provider
        logger.info(f'Registered provider: {name}')
        
    def unregister_provider(self, name: str) -> bool:
        """Unregister a cloud provider"""
        provider = self._providers.pop(name, None)
        if provider:
            logger.info(f'Unregistered provider: {name}')
            return True
        return False
        
    async def delegate(
        self,
        task_name: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        timeout: Optional[int] = None,
        target_provider: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DelegationResult:
        """
        Delegate a task to a cloud agent
        
        Args:
            task_name: Name of the task
            task_type: Type of task (e.g., 'analyze', 'fix', 'security')
            payload: Task payload data
            priority: Task priority
            timeout: Optional timeout override
            target_provider: Optional specific provider to use
            metadata: Optional metadata
            
        Returns:
            DelegationResult with execution status
        """
        if not self._is_running:
            raise RuntimeError('DelegationManager is not running')
            
        # Create task
        task = Task(
            id=str(uuid4()),
            name=task_name,
            type=task_type,
            payload=payload,
            priority=priority,
            timeout=timeout or self.config.default_timeout,
            metadata=metadata or {}
        )
        
        self._tasks[task.id] = task
        
        # Create initial result
        result = DelegationResult(
            task_id=task.id,
            status=DelegationStatus.PENDING
        )
        self._results[task.id] = result
        
        # Select provider
        provider_name = target_provider or await self._select_provider(task)
        if not provider_name:
            result.status = DelegationStatus.FAILED
            result.error = 'No available provider'
            return result
            
        result.provider = provider_name
        
        # Execute task
        await self._execute_task(task, result)
        
        return result
        
    async def delegate_batch(
        self,
        tasks: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[DelegationResult]:
        """
        Delegate multiple tasks
        
        Args:
            tasks: List of task specifications
            parallel: Execute in parallel if True
            
        Returns:
            List of delegation results
        """
        if parallel:
            coroutines = [
                self.delegate(
                    task_name=t['name'],
                    task_type=t['type'],
                    payload=t.get('payload', {}),
                    priority=TaskPriority(t.get('priority', 'medium')),
                    timeout=t.get('timeout'),
                    target_provider=t.get('provider'),
                    metadata=t.get('metadata')
                )
                for t in tasks
            ]
            return await asyncio.gather(*coroutines)
        else:
            results = []
            for t in tasks:
                result = await self.delegate(
                    task_name=t['name'],
                    task_type=t['type'],
                    payload=t.get('payload', {}),
                    priority=TaskPriority(t.get('priority', 'medium')),
                    timeout=t.get('timeout'),
                    target_provider=t.get('provider'),
                    metadata=t.get('metadata')
                )
                results.append(result)
            return results
            
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task
        
        Returns:
            True if cancelled, False if not found
        """
        running_task = self._running_tasks.get(task_id)
        if running_task and not running_task.done():
            running_task.cancel()
            
            result = self._results.get(task_id)
            if result:
                result.status = DelegationStatus.CANCELLED
                result.completed_at = datetime.now(timezone.utc)
                
            logger.info(f'Cancelled task: {task_id}')
            return True
            
        return False
        
    def get_task_status(self, task_id: str) -> Optional[DelegationResult]:
        """Get status of a task"""
        return self._results.get(task_id)
        
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self._tasks.get(task_id)
        
    def list_tasks(
        self,
        status: Optional[DelegationStatus] = None,
        task_type: Optional[str] = None
    ) -> List[Task]:
        """List tasks with optional filters"""
        tasks = list(self._tasks.values())
        
        if status:
            task_ids = [
                tid for tid, result in self._results.items()
                if result.status == status
            ]
            tasks = [t for t in tasks if t.id in task_ids]
            
        if task_type:
            tasks = [t for t in tasks if t.type == task_type]
            
        return tasks
        
    def get_stats(self) -> Dict[str, Any]:
        """Get delegation statistics"""
        status_counts = {}
        for result in self._results.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
        provider_counts = {}
        for result in self._results.values():
            if result.provider:
                provider_counts[result.provider] = provider_counts.get(result.provider, 0) + 1
                
        total_duration = sum(r.duration_ms for r in self._results.values())
        avg_duration = total_duration / max(len(self._results), 1)
        
        success_count = sum(1 for r in self._results.values() if r.is_success)
        success_rate = success_count / max(len(self._results), 1)
        
        return {
            'total_tasks': len(self._tasks),
            'running_tasks': len(self._running_tasks),
            'status_distribution': status_counts,
            'provider_distribution': provider_counts,
            'average_duration_ms': avg_duration,
            'success_rate': success_rate,
            'providers_count': len(self._providers)
        }
        
    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        
    async def _execute_task(self, task: Task, result: DelegationResult) -> None:
        """Execute a task with retry logic"""
        async with self._task_semaphore:
            result.status = DelegationStatus.RUNNING
            result.started_at = datetime.now(timezone.utc)
            
            await self._emit_event('task_started', {'task': task.to_dict()})
            
            attempts = 0
            last_error = None
            
            while attempts < (self.config.max_retries if self.config.retry_enabled else 1):
                attempts += 1
                result.attempts = attempts
                
                if attempts > 1:
                    result.status = DelegationStatus.RETRYING
                    delay = self.config.retry_delay * (self.config.backoff_multiplier ** (attempts - 1))
                    await asyncio.sleep(delay)
                    
                try:
                    # Create execution task
                    exec_task = asyncio.create_task(
                        self._execute_on_provider(task, result.provider)
                    )
                    self._running_tasks[task.id] = exec_task
                    
                    # Wait with timeout
                    execution_result = await asyncio.wait_for(
                        exec_task,
                        timeout=task.timeout
                    )
                    
                    result.result = execution_result
                    result.status = DelegationStatus.COMPLETED
                    result.completed_at = datetime.now(timezone.utc)
                    result.duration_ms = (
                        result.completed_at - result.started_at
                    ).total_seconds() * 1000
                    
                    await self._emit_event('task_completed', {'result': result.to_dict()})
                    break
                    
                except asyncio.TimeoutError:
                    last_error = f'Task timed out after {task.timeout}s'
                    logger.warning(f'Task {task.id} timed out (attempt {attempts})')
                    
                except asyncio.CancelledError:
                    result.status = DelegationStatus.CANCELLED
                    result.completed_at = datetime.now(timezone.utc)
                    raise
                    
                except Exception as e:
                    last_error = str(e)
                    logger.error(f'Task {task.id} failed (attempt {attempts}): {e}')
                    
                finally:
                    self._running_tasks.pop(task.id, None)
                    
            if result.status != DelegationStatus.COMPLETED:
                result.status = DelegationStatus.FAILED
                result.error = last_error
                result.completed_at = datetime.now(timezone.utc)
                result.duration_ms = (
                    result.completed_at - result.started_at
                ).total_seconds() * 1000
                
                await self._emit_event('task_failed', {'result': result.to_dict()})
                
    async def _execute_on_provider(
        self,
        task: Task,
        provider_name: str
    ) -> Any:
        """
        Execute task on a specific provider
        
        NOTE: This is a simulation for framework demonstration.
        Production implementation should integrate with actual cloud
        provider SDKs (boto3 for AWS, google-cloud for GCP, azure for Azure).
        
        Args:
            task: Task to execute
            provider_name: Name of the provider
            
        Returns:
            Execution result
        """
        provider = self._providers.get(provider_name)
        
        if not provider:
            # Simulate execution for testing/demonstration
            await asyncio.sleep(0.1)
            return {
                'status': 'success',
                'provider': provider_name,
                'task_type': task.type,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            
        # In real implementation, call provider's execute method
        if hasattr(provider, 'execute'):
            return await provider.execute(task)
        else:
            return await provider(task)
            
    async def _select_provider(self, task: Task) -> Optional[str]:
        """Select appropriate provider for task"""
        if not self._providers:
            # Return default provider name for testing
            return 'default'
            
        # Use router if available
        if self._router:
            routing_result = await self._router.route(task)
            if routing_result and routing_result.provider:
                return routing_result.provider
                
        # Use load balancer if available
        if self._load_balancer:
            provider = await self._load_balancer.select_provider()
            if provider:
                return provider
                
        # Return first available provider
        return next(iter(self._providers.keys()), None)
        
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
                logger.error(f'Event handler error for {event}: {e}')


# Factory functions
def create_delegation_manager(
    name: str,
    **kwargs
) -> DelegationManager:
    """Create a new DelegationManager instance"""
    config = DelegationConfig(name=name, **kwargs)
    return DelegationManager(config)


def create_task(
    name: str,
    task_type: str,
    payload: Dict[str, Any],
    **kwargs
) -> Task:
    """Create a new Task"""
    return Task(
        id=str(uuid4()),
        name=name,
        type=task_type,
        payload=payload,
        **kwargs
    )
