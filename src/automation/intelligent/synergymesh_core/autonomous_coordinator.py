"""
Autonomous Coordinator - 自主協調器
完全無人化 24/7 自主運行 / Fully Autonomous 24/7 Operation

This module provides fully autonomous operation capabilities for the SynergyMesh
system, enabling 24/7 self-operating without human intervention.

Core Capabilities:
- 24/7 autonomous task scheduling and execution
- Self-healing and error recovery
- Resource management and optimization
- Autonomous decision making based on historical data
- Predictive maintenance and proactive problem solving

設計原則: 完全無人化，無需任何人工干預
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import heapq

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class SystemHealth(Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    RECOVERING = "recovering"


@dataclass
class AutonomousTask:
    """Represents an autonomous task"""
    task_id: str
    name: str
    description: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    handler: Optional[Callable[..., Awaitable[Any]]] = None
    params: Dict[str, Any] = field(default_factory=dict)
    scheduled_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    result: Any = None
    error: Optional[str] = None
    
    def __lt__(self, other: 'AutonomousTask') -> bool:
        """For priority queue comparison"""
        return self.priority.value < other.priority.value


@dataclass
class HealthCheck:
    """Health check result"""
    component: str
    status: SystemHealth
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AutoRecoveryAction:
    """Auto-recovery action"""
    action_id: str
    action_type: str
    description: str
    target_component: str
    executed_at: datetime = field(default_factory=datetime.now)
    success: bool = False
    result_message: str = ""


class AutonomousCoordinator:
    """
    自主協調器 - 24/7 完全自主運行
    
    Autonomous Coordinator for fully autonomous 24/7 operation.
    Enables the system to operate without human intervention by:
    
    - Managing task scheduling and execution
    - Monitoring system health and performance
    - Implementing self-healing mechanisms
    - Making autonomous decisions based on historical data
    - Performing predictive maintenance
    
    設計目標:
    1. 零人工干預 - No human intervention required
    2. 自我修復 - Self-healing capabilities
    3. 智能決策 - Intelligent decision making
    4. 預測性維護 - Predictive maintenance
    """
    
    # Configuration constants
    STUCK_TASK_TIMEOUT_SECONDS = 300  # 5 minutes
    HEALTH_CHECK_INTERVAL_SECONDS = 30
    RECOVERY_CHECK_INTERVAL_SECONDS = 10
    HIGH_QUEUE_THRESHOLD = 50
    MAX_WORKERS = 8
    
    def __init__(self, worker_count: int = 4):
        """
        Initialize the Autonomous Coordinator
        
        Args:
            worker_count: Number of worker tasks for parallel execution
        """
        self.worker_count = worker_count
        self.task_queue: List[AutonomousTask] = []
        self.running_tasks: Dict[str, AutonomousTask] = {}
        self.completed_tasks: List[AutonomousTask] = []
        self.failed_tasks: List[AutonomousTask] = []
        
        self.health_checks: List[HealthCheck] = []
        self.recovery_actions: List[AutoRecoveryAction] = []
        
        self.system_health = SystemHealth.HEALTHY
        self.is_running = False
        self.workers: List[asyncio.Task[Any]] = []
        
        self._task_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self._health_monitors: Dict[str, Callable[[], Awaitable[HealthCheck]]] = {}
        
        # Statistics
        self.stats = {
            "tasks_processed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "auto_recoveries": 0,
            "uptime_start": datetime.now()
        }
        
        logger.info(f"AutonomousCoordinator initialized with {worker_count} workers")
    
    def register_task_handler(
        self,
        task_type: str,
        handler: Callable[..., Awaitable[Any]]
    ) -> None:
        """
        Register a task handler for autonomous execution
        
        Args:
            task_type: Type identifier for the task
            handler: Async function to handle the task
        """
        self._task_handlers[task_type] = handler
        logger.info(f"Task handler registered: {task_type}")
    
    def register_health_monitor(
        self,
        component: str,
        monitor: Callable[[], Awaitable[HealthCheck]]
    ) -> None:
        """
        Register a health monitor for a component
        
        Args:
            component: Component name to monitor
            monitor: Async function that returns HealthCheck
        """
        self._health_monitors[component] = monitor
        logger.info(f"Health monitor registered: {component}")
    
    def schedule_task(
        self,
        name: str,
        description: str,
        task_type: str,
        params: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """
        Schedule a task for autonomous execution
        
        自動排程任務以供自主執行
        
        Args:
            name: Task name
            description: Task description
            task_type: Type of task (must have registered handler)
            params: Parameters for the task
            priority: Task priority
            scheduled_time: Optional scheduled execution time
            
        Returns:
            Task ID
        """
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        handler = self._task_handlers.get(task_type)
        if not handler:
            logger.warning(f"No handler for task type: {task_type}")
        
        task = AutonomousTask(
            task_id=task_id,
            name=name,
            description=description,
            priority=priority,
            handler=handler,
            params=params,
            scheduled_time=scheduled_time,
            status=TaskStatus.SCHEDULED if scheduled_time else TaskStatus.PENDING
        )
        
        heapq.heappush(self.task_queue, task)
        logger.info(f"Task scheduled: {task_id} - {name} (priority: {priority.name})")
        
        return task_id
    
    async def start(self) -> None:
        """
        Start the autonomous coordinator
        
        啟動自主協調器，開始 24/7 運行
        """
        if self.is_running:
            logger.warning("Coordinator is already running")
            return
        
        self.is_running = True
        logger.info("Starting Autonomous Coordinator...")
        
        # Start worker tasks
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._worker_loop(i))
            self.workers.append(worker)
        
        # Start health monitoring
        health_monitor = asyncio.create_task(self._health_monitor_loop())
        self.workers.append(health_monitor)
        
        # Start recovery manager
        recovery_manager = asyncio.create_task(self._recovery_manager_loop())
        self.workers.append(recovery_manager)
        
        logger.info(f"Autonomous Coordinator started with {len(self.workers)} tasks")
    
    async def stop(self) -> None:
        """
        Stop the autonomous coordinator
        
        停止自主協調器
        """
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping Autonomous Coordinator...")
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Autonomous Coordinator stopped")
    
    async def _worker_loop(self, worker_id: int) -> None:
        """
        Worker loop for task execution
        
        Args:
            worker_id: Worker identifier
        """
        logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                task = await self._get_next_task()
                if task:
                    await self._execute_task(task, worker_id)
                else:
                    await asyncio.sleep(0.1)  # Brief pause if no tasks
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)  # Brief pause before retry
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _get_next_task(self) -> Optional[AutonomousTask]:
        """Get the next task from the queue"""
        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            
            # Check if task is scheduled for later
            if task.scheduled_time and task.scheduled_time > datetime.now():
                heapq.heappush(self.task_queue, task)
                return None
            
            # Check if task is not cancelled
            if task.status == TaskStatus.CANCELLED:
                continue
            
            return task
        
        return None
    
    async def _execute_task(self, task: AutonomousTask, worker_id: int) -> None:
        """
        Execute a task autonomously
        
        Args:
            task: Task to execute
            worker_id: Worker identifier
        """
        logger.info(f"Worker {worker_id} executing task: {task.task_id} - {task.name}")
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self.running_tasks[task.task_id] = task
        
        try:
            if task.handler:
                task.result = await task.handler(**task.params)
            else:
                # Default handler for tasks without specific handler
                task.result = await self._default_task_handler(task)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            self.completed_tasks.append(task)
            self.stats["tasks_succeeded"] += 1
            
            logger.info(f"Task completed: {task.task_id}")
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.RETRYING
                heapq.heappush(self.task_queue, task)
                logger.warning(
                    f"Task {task.task_id} failed, retrying ({task.retry_count}/{task.max_retries}): {e}"
                )
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                self.failed_tasks.append(task)
                self.stats["tasks_failed"] += 1
                logger.error(f"Task {task.task_id} failed permanently: {e}")
        
        finally:
            self.running_tasks.pop(task.task_id, None)
            self.stats["tasks_processed"] += 1
    
    async def _default_task_handler(self, task: AutonomousTask) -> Dict[str, Any]:
        """Default handler for tasks without specific handler"""
        logger.info(f"Executing default handler for task: {task.name}")
        
        # Simulate task execution
        await asyncio.sleep(0.1)
        
        return {
            "status": "completed",
            "task_name": task.name,
            "message": "Task executed with default handler"
        }
    
    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""
        logger.info("Health monitor started")
        
        while self.is_running:
            try:
                await self._check_system_health()
                await asyncio.sleep(self.HEALTH_CHECK_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(5)
        
        logger.info("Health monitor stopped")
    
    async def _check_system_health(self) -> None:
        """Check system health across all components"""
        health_checks = []
        overall_health = SystemHealth.HEALTHY
        
        # Check registered health monitors
        for component, monitor in self._health_monitors.items():
            try:
                check = await monitor()
                health_checks.append(check)
                
                if check.status == SystemHealth.CRITICAL:
                    overall_health = SystemHealth.CRITICAL
                elif check.status == SystemHealth.DEGRADED and overall_health != SystemHealth.CRITICAL:
                    overall_health = SystemHealth.DEGRADED
                    
            except Exception as e:
                health_checks.append(HealthCheck(
                    component=component,
                    status=SystemHealth.CRITICAL,
                    message=f"Health check failed: {e}"
                ))
                overall_health = SystemHealth.CRITICAL
        
        # Add internal metrics check
        internal_check = await self._check_internal_health()
        health_checks.append(internal_check)
        
        if internal_check.status == SystemHealth.CRITICAL:
            overall_health = SystemHealth.CRITICAL
        elif internal_check.status == SystemHealth.DEGRADED and overall_health != SystemHealth.CRITICAL:
            overall_health = SystemHealth.DEGRADED
        
        self.health_checks = health_checks
        self.system_health = overall_health
        
        if overall_health != SystemHealth.HEALTHY:
            logger.warning(f"System health: {overall_health.value}")
    
    async def _check_internal_health(self) -> HealthCheck:
        """Check internal coordinator health"""
        queue_size = len(self.task_queue)
        running_count = len(self.running_tasks)
        failed_ratio = (
            self.stats["tasks_failed"] / max(self.stats["tasks_processed"], 1)
        )
        
        status = SystemHealth.HEALTHY
        message = "All systems nominal"
        
        if queue_size > 100 or running_count > self.worker_count * 2:
            status = SystemHealth.DEGRADED
            message = "High task load detected"
        
        if failed_ratio > 0.2:
            status = SystemHealth.DEGRADED
            message = "High failure rate detected"
        
        if failed_ratio > 0.5:
            status = SystemHealth.CRITICAL
            message = "Critical failure rate"
        
        return HealthCheck(
            component="autonomous_coordinator",
            status=status,
            message=message,
            metrics={
                "queue_size": queue_size,
                "running_tasks": running_count,
                "failed_ratio": failed_ratio,
                "tasks_processed": self.stats["tasks_processed"]
            }
        )
    
    async def _recovery_manager_loop(self) -> None:
        """Self-healing recovery manager loop"""
        logger.info("Recovery manager started")
        
        while self.is_running:
            try:
                if self.system_health in [SystemHealth.DEGRADED, SystemHealth.CRITICAL]:
                    await self._attempt_auto_recovery()
                await asyncio.sleep(self.RECOVERY_CHECK_INTERVAL_SECONDS)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Recovery manager error: {e}")
                await asyncio.sleep(5)
        
        logger.info("Recovery manager stopped")
    
    async def _attempt_auto_recovery(self) -> None:
        """
        Attempt automatic recovery actions
        
        自動嘗試恢復操作
        """
        logger.info("Attempting auto-recovery...")
        
        # Check for stuck tasks
        stuck_tasks = [
            task for task in self.running_tasks.values()
            if task.started_at and (datetime.now() - task.started_at).seconds > self.STUCK_TASK_TIMEOUT_SECONDS
        ]
        
        for task in stuck_tasks:
            action = AutoRecoveryAction(
                action_id=f"recovery-{uuid.uuid4().hex[:8]}",
                action_type="task_reset",
                description=f"Reset stuck task: {task.task_id}",
                target_component=f"task:{task.task_id}"
            )
            
            # Reset the stuck task
            task.status = TaskStatus.RETRYING
            task.retry_count += 1
            self.running_tasks.pop(task.task_id, None)
            
            if task.retry_count < task.max_retries:
                heapq.heappush(self.task_queue, task)
                action.success = True
                action.result_message = "Task reset and requeued"
            else:
                task.status = TaskStatus.FAILED
                self.failed_tasks.append(task)
                action.success = False
                action.result_message = "Task max retries exceeded"
            
            self.recovery_actions.append(action)
            self.stats["auto_recoveries"] += 1
            logger.info(f"Auto-recovery action: {action.description} - {action.result_message}")
        
        # Check if we need to adjust worker count
        if len(self.task_queue) > self.HIGH_QUEUE_THRESHOLD and len(self.workers) < self.MAX_WORKERS:
            action = AutoRecoveryAction(
                action_id=f"recovery-{uuid.uuid4().hex[:8]}",
                action_type="scale_workers",
                description="Scale up workers due to high queue",
                target_component="worker_pool"
            )
            
            # Add more workers (up to limit)
            new_worker_id = len(self.workers)
            new_worker = asyncio.create_task(self._worker_loop(new_worker_id))
            self.workers.append(new_worker)
            
            action.success = True
            action.result_message = f"Added worker {new_worker_id}"
            self.recovery_actions.append(action)
            self.stats["auto_recoveries"] += 1
            logger.info(f"Auto-recovery action: {action.description}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific task
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status information or None if not found
        """
        # Check running tasks
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return self._task_to_dict(task)
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return self._task_to_dict(task)
        
        # Check failed tasks
        for task in self.failed_tasks:
            if task.task_id == task_id:
                return self._task_to_dict(task)
        
        # Check queued tasks
        for task in self.task_queue:
            if task.task_id == task_id:
                return self._task_to_dict(task)
        
        return None
    
    def _task_to_dict(self, task: AutonomousTask) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": task.task_id,
            "name": task.name,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.name,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "retry_count": task.retry_count,
            "error": task.error,
            "result": task.result
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get coordinator statistics
        
        獲取協調器統計信息
        """
        uptime = datetime.now() - self.stats["uptime_start"]
        
        return {
            "is_running": self.is_running,
            "system_health": self.system_health.value,
            "uptime_seconds": uptime.total_seconds(),
            "worker_count": len(self.workers),
            "queue_size": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "tasks_processed": self.stats["tasks_processed"],
            "tasks_succeeded": self.stats["tasks_succeeded"],
            "tasks_failed": self.stats["tasks_failed"],
            "auto_recoveries": self.stats["auto_recoveries"],
            "success_rate": round(
                self.stats["tasks_succeeded"] / max(self.stats["tasks_processed"], 1) * 100, 2
            )
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        Get system health report
        
        獲取系統健康報告
        """
        return {
            "overall_health": self.system_health.value,
            "checks": [
                {
                    "component": check.component,
                    "status": check.status.value,
                    "message": check.message,
                    "metrics": check.metrics,
                    "timestamp": check.timestamp.isoformat()
                }
                for check in self.health_checks
            ],
            "recent_recoveries": [
                {
                    "action_id": action.action_id,
                    "type": action.action_type,
                    "description": action.description,
                    "target": action.target_component,
                    "success": action.success,
                    "result": action.result_message,
                    "executed_at": action.executed_at.isoformat()
                }
                for action in self.recovery_actions[-10:]  # Last 10 recoveries
            ]
        }


# Example usage
if __name__ == "__main__":
    import json
    
    async def example_task_handler(task_name: str, duration: float = 0.5) -> Dict[str, Any]:
        """Example task handler"""
        await asyncio.sleep(duration)
        return {
            "processed": task_name,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
    
    async def main():
        coordinator = AutonomousCoordinator(worker_count=2)
        
        # Register task handler
        coordinator.register_task_handler("example", example_task_handler)
        
        print("=== Autonomous Coordinator Test ===\n")
        
        # Start coordinator
        await coordinator.start()
        
        # Schedule some tasks
        task_ids = []
        for i in range(5):
            task_id = coordinator.schedule_task(
                name=f"Example Task {i+1}",
                description=f"Test task number {i+1}",
                task_type="example",
                params={"task_name": f"task_{i+1}", "duration": 0.2},
                priority=TaskPriority.MEDIUM
            )
            task_ids.append(task_id)
            print(f"Scheduled: {task_id}")
        
        # Wait for tasks to complete
        print("\nWaiting for tasks to complete...")
        await asyncio.sleep(3)
        
        # Check task statuses
        print("\n=== Task Statuses ===")
        for task_id in task_ids:
            status = coordinator.get_task_status(task_id)
            print(f"{task_id}: {status['status'] if status else 'not found'}")
        
        # Get statistics
        print("\n=== Statistics ===")
        stats = coordinator.get_statistics()
        print(json.dumps(stats, indent=2))
        
        # Get health report
        print("\n=== Health Report ===")
        health = coordinator.get_health_report()
        print(json.dumps(health, indent=2, default=str))
        
        # Stop coordinator
        await coordinator.stop()
        print("\nCoordinator stopped")
    
    asyncio.run(main())
