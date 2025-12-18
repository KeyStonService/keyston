"""
Ecosystem Orchestrator - 生態協同編排器
智能生態協同 / Intelligent Ecosystem Coordination

This module provides ecosystem-level orchestration for SynergyMesh,
enabling independent subsystems to work together in harmony while
maintaining their autonomy.

Core Capabilities:
- Subsystem registration and lifecycle management
- Inter-subsystem communication and coordination
- Resource allocation and load balancing
- Conflict resolution and priority management
- System-wide state management and synchronization

設計原則: 每個子系統既獨立運作又相互協同
Each subsystem operates independently yet coordinates with others.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class SubsystemType(Enum):
    """Types of subsystems in the ecosystem"""
    LANGUAGE_PROCESSOR = "language_processor"
    AUTONOMOUS_COORDINATOR = "autonomous_coordinator"
    EVOLUTION_ENGINE = "evolution_engine"
    CODE_ANALYZER = "code_analyzer"
    SECURITY_MONITOR = "security_monitor"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    DATA_MIGRATOR = "data_migrator"
    WORKFLOW_AUTOMATOR = "workflow_automator"
    CUSTOM = "custom"


class SubsystemStatus(Enum):
    """Status of a subsystem"""
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    BUSY = "busy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class MessageType(Enum):
    """Types of inter-subsystem messages"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COMMAND = "command"
    STATUS = "status"
    SYNC = "sync"


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Subsystem:
    """Represents a subsystem in the ecosystem"""
    subsystem_id: str
    name: str
    subsystem_type: SubsystemType
    status: SubsystemStatus = SubsystemStatus.INITIALIZING
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    handler: Optional[Callable[..., Awaitable[Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    message_count: int = 0


@dataclass
class EcosystemMessage:
    """Message for inter-subsystem communication"""
    message_id: str
    message_type: MessageType
    priority: MessagePriority
    source_id: str
    target_id: str  # Can be specific subsystem or "broadcast"
    payload: Dict[str, Any] = field(default_factory=dict)
    response_to: Optional[str] = None  # For response messages
    created_at: datetime = field(default_factory=datetime.now)
    delivered: bool = False
    processed: bool = False


@dataclass
class CoordinationTask:
    """Task that requires coordination between subsystems"""
    task_id: str
    name: str
    description: str
    required_subsystems: List[str]
    current_step: int = 0
    total_steps: int = 0
    status: str = "pending"
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceAllocation:
    """Resource allocation for a subsystem"""
    allocation_id: str
    subsystem_id: str
    resource_type: str  # cpu, memory, connections, etc.
    allocated_amount: float
    used_amount: float = 0.0
    allocated_at: datetime = field(default_factory=datetime.now)


class EcosystemOrchestrator:
    """
    生態協同編排器 - 智能子系統協調
    
    Ecosystem Orchestrator for intelligent subsystem coordination.
    Enables multiple independent subsystems to work together while
    maintaining their autonomy.
    
    Features:
    - 子系統註冊與生命週期管理 (Subsystem registration and lifecycle)
    - 跨子系統通信與協調 (Inter-subsystem communication)
    - 資源分配與負載平衡 (Resource allocation and load balancing)
    - 衝突解決與優先級管理 (Conflict resolution and priority)
    - 全系統狀態同步 (System-wide state synchronization)
    
    設計目標:
    - 獨立性: 每個子系統可獨立運作
    - 協同性: 子系統間無縫協作
    - 彈性: 動態添加/移除子系統
    - 容錯: 子系統故障不影響整體
    """
    
    # Configuration constants
    HEARTBEAT_TIMEOUT_SECONDS = 60
    HEALTH_CHECK_INTERVAL_SECONDS = 30
    
    def __init__(self):
        """Initialize the Ecosystem Orchestrator"""
        self.subsystems: Dict[str, Subsystem] = {}
        self.message_queue: List[EcosystemMessage] = []
        self.coordination_tasks: Dict[str, CoordinationTask] = {}
        self.resource_allocations: Dict[str, List[ResourceAllocation]] = {}
        
        self.is_running = False
        self.background_tasks: List[asyncio.Task[Any]] = []
        
        # Capability registry for routing
        self._capability_index: Dict[str, Set[str]] = {}
        
        # Message handlers
        self._message_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "coordinations_completed": 0,
            "subsystem_registrations": 0,
            "conflicts_resolved": 0
        }
        
        logger.info("EcosystemOrchestrator initialized - 生態協同編排器已初始化")
    
    def register_subsystem(
        self,
        name: str,
        subsystem_type: SubsystemType,
        capabilities: List[str],
        dependencies: Optional[List[str]] = None,
        handler: Optional[Callable[..., Awaitable[Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a subsystem in the ecosystem
        
        在生態系統中註冊子系統
        
        Args:
            name: Subsystem name
            subsystem_type: Type of subsystem
            capabilities: List of capabilities provided
            dependencies: List of subsystem IDs this depends on
            handler: Async handler for processing messages
            metadata: Additional metadata
            
        Returns:
            Subsystem ID
        """
        subsystem_id = f"sub-{uuid.uuid4().hex[:8]}"
        
        subsystem = Subsystem(
            subsystem_id=subsystem_id,
            name=name,
            subsystem_type=subsystem_type,
            capabilities=capabilities,
            dependencies=dependencies or [],
            handler=handler,
            metadata=metadata or {},
            status=SubsystemStatus.INITIALIZING
        )
        
        self.subsystems[subsystem_id] = subsystem
        
        # Index capabilities for fast lookup
        for capability in capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = set()
            self._capability_index[capability].add(subsystem_id)
        
        self.stats["subsystem_registrations"] += 1
        
        # Check dependencies and set status
        if self._check_dependencies(subsystem):
            subsystem.status = SubsystemStatus.READY
        
        logger.info(
            f"Subsystem registered: {name} ({subsystem_id}) "
            f"with {len(capabilities)} capabilities"
        )
        
        return subsystem_id
    
    def unregister_subsystem(self, subsystem_id: str) -> bool:
        """
        Unregister a subsystem from the ecosystem
        
        Args:
            subsystem_id: ID of subsystem to unregister
            
        Returns:
            True if successful
        """
        if subsystem_id not in self.subsystems:
            return False
        
        subsystem = self.subsystems[subsystem_id]
        
        # Remove from capability index
        for capability in subsystem.capabilities:
            if capability in self._capability_index:
                self._capability_index[capability].discard(subsystem_id)
        
        # Mark as offline before removal
        subsystem.status = SubsystemStatus.OFFLINE
        
        # Remove from registry
        del self.subsystems[subsystem_id]
        
        # Remove resource allocations
        if subsystem_id in self.resource_allocations:
            del self.resource_allocations[subsystem_id]
        
        logger.info(f"Subsystem unregistered: {subsystem.name} ({subsystem_id})")
        return True
    
    def _check_dependencies(self, subsystem: Subsystem) -> bool:
        """Check if all dependencies of a subsystem are met"""
        for dep_id in subsystem.dependencies:
            if dep_id not in self.subsystems:
                return False
            if self.subsystems[dep_id].status not in [
                SubsystemStatus.READY,
                SubsystemStatus.ACTIVE
            ]:
                return False
        return True
    
    async def send_message(
        self,
        source_id: str,
        target_id: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        response_to: Optional[str] = None
    ) -> str:
        """
        Send a message between subsystems
        
        在子系統間發送消息
        
        Args:
            source_id: Source subsystem ID
            target_id: Target subsystem ID or "broadcast"
            message_type: Type of message
            payload: Message payload
            priority: Message priority
            response_to: Optional message ID this is responding to
            
        Returns:
            Message ID
        """
        message_id = f"msg-{uuid.uuid4().hex[:8]}"
        
        message = EcosystemMessage(
            message_id=message_id,
            message_type=message_type,
            priority=priority,
            source_id=source_id,
            target_id=target_id,
            payload=payload,
            response_to=response_to
        )
        
        self.message_queue.append(message)
        self.stats["messages_sent"] += 1
        
        # Update source subsystem message count
        if source_id in self.subsystems:
            self.subsystems[source_id].message_count += 1
        
        # Process message immediately if orchestrator is running
        if self.is_running:
            await self._deliver_message(message)
        
        return message_id
    
    async def _deliver_message(self, message: EcosystemMessage) -> None:
        """Deliver a message to its target"""
        if message.target_id == "broadcast":
            # Deliver to all subsystems
            for subsystem_id, subsystem in self.subsystems.items():
                if subsystem_id != message.source_id:
                    await self._process_message_for_subsystem(message, subsystem)
        else:
            # Deliver to specific subsystem
            if message.target_id in self.subsystems:
                subsystem = self.subsystems[message.target_id]
                await self._process_message_for_subsystem(message, subsystem)
        
        message.delivered = True
        self.stats["messages_delivered"] += 1
    
    async def _process_message_for_subsystem(
        self,
        message: EcosystemMessage,
        subsystem: Subsystem
    ) -> None:
        """Process a message for a specific subsystem"""
        if subsystem.handler:
            try:
                await subsystem.handler(message)
                message.processed = True
            except Exception as e:
                logger.error(
                    f"Error processing message for {subsystem.name}: {e}"
                )
        
        # Check for registered message handlers
        handler_key = f"{subsystem.subsystem_id}:{message.message_type.value}"
        if handler_key in self._message_handlers:
            try:
                await self._message_handlers[handler_key](message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    def register_message_handler(
        self,
        subsystem_id: str,
        message_type: MessageType,
        handler: Callable[..., Awaitable[Any]]
    ) -> None:
        """
        Register a message handler for a subsystem
        
        Args:
            subsystem_id: Subsystem ID
            message_type: Type of messages to handle
            handler: Async handler function
        """
        handler_key = f"{subsystem_id}:{message_type.value}"
        self._message_handlers[handler_key] = handler
        logger.debug(f"Message handler registered: {handler_key}")
    
    def find_subsystems_by_capability(self, capability: str) -> List[str]:
        """
        Find subsystems that provide a specific capability
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of subsystem IDs
        """
        if capability in self._capability_index:
            return list(self._capability_index[capability])
        return []
    
    async def create_coordination_task(
        self,
        name: str,
        description: str,
        required_capabilities: List[str],
        steps: List[Dict[str, Any]]
    ) -> str:
        """
        Create a task that requires coordination between subsystems
        
        創建需要子系統協調的任務
        
        Args:
            name: Task name
            description: Task description
            required_capabilities: Capabilities needed for this task
            steps: List of steps to execute
            
        Returns:
            Task ID
        """
        task_id = f"coord-{uuid.uuid4().hex[:8]}"
        
        # Find subsystems for required capabilities
        required_subsystems = []
        for capability in required_capabilities:
            subsystem_ids = self.find_subsystems_by_capability(capability)
            if not subsystem_ids:
                logger.warning(f"No subsystem found for capability: {capability}")
            else:
                # Select best available subsystem
                selected = self._select_best_subsystem(subsystem_ids)
                if selected:
                    required_subsystems.append(selected)
        
        task = CoordinationTask(
            task_id=task_id,
            name=name,
            description=description,
            required_subsystems=required_subsystems,
            total_steps=len(steps),
            status="pending"
        )
        
        self.coordination_tasks[task_id] = task
        
        # Start coordination
        asyncio.create_task(self._execute_coordination(task, steps))
        
        logger.info(
            f"Coordination task created: {name} ({task_id}) "
            f"with {len(required_subsystems)} subsystems"
        )
        
        return task_id
    
    def _select_best_subsystem(self, subsystem_ids: List[str]) -> Optional[str]:
        """Select the best available subsystem from a list"""
        available = [
            sid for sid in subsystem_ids
            if sid in self.subsystems
            and self.subsystems[sid].status in [
                SubsystemStatus.READY,
                SubsystemStatus.ACTIVE
            ]
        ]
        
        if not available:
            return None
        
        # Select based on load (message count as proxy)
        return min(available, key=lambda x: self.subsystems[x].message_count)
    
    async def _execute_coordination(
        self,
        task: CoordinationTask,
        steps: List[Dict[str, Any]]
    ) -> None:
        """Execute a coordination task"""
        task.status = "running"
        
        try:
            for i, step in enumerate(steps):
                task.current_step = i + 1
                
                # Notify relevant subsystems
                for subsystem_id in task.required_subsystems:
                    await self.send_message(
                        source_id="orchestrator",
                        target_id=subsystem_id,
                        message_type=MessageType.COMMAND,
                        payload={
                            "task_id": task.task_id,
                            "step": i + 1,
                            "action": step.get("action", "execute"),
                            "params": step.get("params", {})
                        },
                        priority=MessagePriority.HIGH
                    )
                
                # Wait for step completion (simplified)
                await asyncio.sleep(0.1)
            
            task.status = "completed"
            self.stats["coordinations_completed"] += 1
            
        except Exception as e:
            logger.error(f"Coordination task failed: {e}")
            task.status = "failed"
    
    def allocate_resource(
        self,
        subsystem_id: str,
        resource_type: str,
        amount: float
    ) -> str:
        """
        Allocate resources to a subsystem
        
        Args:
            subsystem_id: Subsystem to allocate to
            resource_type: Type of resource
            amount: Amount to allocate
            
        Returns:
            Allocation ID
        """
        allocation_id = f"alloc-{uuid.uuid4().hex[:8]}"
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            subsystem_id=subsystem_id,
            resource_type=resource_type,
            allocated_amount=amount
        )
        
        if subsystem_id not in self.resource_allocations:
            self.resource_allocations[subsystem_id] = []
        
        self.resource_allocations[subsystem_id].append(allocation)
        
        logger.debug(
            f"Resource allocated: {amount} {resource_type} to {subsystem_id}"
        )
        
        return allocation_id
    
    def update_subsystem_status(
        self,
        subsystem_id: str,
        status: SubsystemStatus
    ) -> bool:
        """
        Update the status of a subsystem
        
        Args:
            subsystem_id: Subsystem ID
            status: New status
            
        Returns:
            True if successful
        """
        if subsystem_id not in self.subsystems:
            return False
        
        old_status = self.subsystems[subsystem_id].status
        self.subsystems[subsystem_id].status = status
        self.subsystems[subsystem_id].last_heartbeat = datetime.now()
        
        # Notify other subsystems of status change
        if self.is_running:
            asyncio.create_task(
                self.send_message(
                    source_id=subsystem_id,
                    target_id="broadcast",
                    message_type=MessageType.STATUS,
                    payload={
                        "subsystem_id": subsystem_id,
                        "old_status": old_status.value,
                        "new_status": status.value
                    }
                )
            )
        
        logger.info(
            f"Subsystem {subsystem_id} status: {old_status.value} -> {status.value}"
        )
        return True
    
    async def start(self) -> None:
        """
        Start the ecosystem orchestrator
        
        啟動生態協同編排器
        """
        if self.is_running:
            logger.warning("Orchestrator is already running")
            return
        
        self.is_running = True
        
        # Start background tasks
        message_processor = asyncio.create_task(self._message_processor_loop())
        self.background_tasks.append(message_processor)
        
        health_checker = asyncio.create_task(self._health_check_loop())
        self.background_tasks.append(health_checker)
        
        # Activate all ready subsystems
        for subsystem_id, subsystem in self.subsystems.items():
            if subsystem.status == SubsystemStatus.READY:
                subsystem.status = SubsystemStatus.ACTIVE
        
        logger.info("Ecosystem Orchestrator started")
    
    async def stop(self) -> None:
        """
        Stop the ecosystem orchestrator
        
        停止生態協同編排器
        """
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        # Set all subsystems to offline
        for subsystem in self.subsystems.values():
            subsystem.status = SubsystemStatus.OFFLINE
        
        logger.info("Ecosystem Orchestrator stopped")
    
    async def _message_processor_loop(self) -> None:
        """Background loop for processing messages"""
        while self.is_running:
            try:
                # Process pending messages
                pending = [m for m in self.message_queue if not m.delivered]
                
                # Sort by priority
                pending.sort(key=lambda x: x.priority.value)
                
                for message in pending:
                    await self._deliver_message(message)
                
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Message processor error: {e}")
                await asyncio.sleep(1)
    
    async def _health_check_loop(self) -> None:
        """Background loop for health checking subsystems"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                for subsystem_id, subsystem in self.subsystems.items():
                    # Check for stale heartbeat
                    time_diff = (current_time - subsystem.last_heartbeat).seconds
                    
                    if time_diff > self.HEARTBEAT_TIMEOUT_SECONDS and subsystem.status == SubsystemStatus.ACTIVE:
                        logger.warning(
                            f"Subsystem {subsystem.name} heartbeat stale, "
                            f"marking as degraded"
                        )
                        self.update_subsystem_status(
                            subsystem_id,
                            SubsystemStatus.DEGRADED
                        )
                    
                    # Check dependencies
                    if not self._check_dependencies(subsystem):
                        if subsystem.status == SubsystemStatus.ACTIVE:
                            logger.warning(
                                f"Subsystem {subsystem.name} dependencies not met"
                            )
                            self.update_subsystem_status(
                                subsystem_id,
                                SubsystemStatus.DEGRADED
                            )
                
                await asyncio.sleep(self.HEALTH_CHECK_INTERVAL_SECONDS)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(5)
    
    def get_ecosystem_status(self) -> Dict[str, Any]:
        """
        Get overall ecosystem status
        
        獲取整體生態系統狀態
        """
        subsystem_counts = {status.value: 0 for status in SubsystemStatus}
        
        for subsystem in self.subsystems.values():
            subsystem_counts[subsystem.status.value] += 1
        
        pending_tasks = len([
            t for t in self.coordination_tasks.values()
            if t.status in ["pending", "running"]
        ])
        
        return {
            "is_running": self.is_running,
            "total_subsystems": len(self.subsystems),
            "subsystem_status_counts": subsystem_counts,
            "pending_messages": len([m for m in self.message_queue if not m.delivered]),
            "pending_coordination_tasks": pending_tasks,
            "capabilities_available": list(self._capability_index.keys()),
            "statistics": self.stats
        }
    
    def get_subsystem_info(self, subsystem_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a subsystem
        
        Args:
            subsystem_id: Subsystem ID
            
        Returns:
            Subsystem information or None if not found
        """
        if subsystem_id not in self.subsystems:
            return None
        
        subsystem = self.subsystems[subsystem_id]
        
        return {
            "subsystem_id": subsystem.subsystem_id,
            "name": subsystem.name,
            "type": subsystem.subsystem_type.value,
            "status": subsystem.status.value,
            "capabilities": subsystem.capabilities,
            "dependencies": subsystem.dependencies,
            "message_count": subsystem.message_count,
            "registered_at": subsystem.registered_at.isoformat(),
            "last_heartbeat": subsystem.last_heartbeat.isoformat(),
            "metadata": subsystem.metadata,
            "resource_allocations": [
                {
                    "allocation_id": a.allocation_id,
                    "resource_type": a.resource_type,
                    "allocated": a.allocated_amount,
                    "used": a.used_amount
                }
                for a in self.resource_allocations.get(subsystem_id, [])
            ]
        }
    
    def list_subsystems(self) -> List[Dict[str, Any]]:
        """
        List all registered subsystems
        
        列出所有已註冊子系統
        """
        return [
            {
                "subsystem_id": s.subsystem_id,
                "name": s.name,
                "type": s.subsystem_type.value,
                "status": s.status.value,
                "capabilities_count": len(s.capabilities),
                "message_count": s.message_count
            }
            for s in self.subsystems.values()
        ]


# Example usage
if __name__ == "__main__":
    import json
    
    async def example_handler(message: EcosystemMessage) -> None:
        """Example message handler"""
        logger.info(
            f"Received message: {message.message_type.value} from {message.source_id}"
        )
    
    async def main():
        orchestrator = EcosystemOrchestrator()
        
        print("=== Ecosystem Orchestrator Test ===\n")
        
        # Register subsystems
        nlp_id = orchestrator.register_subsystem(
            name="Natural Language Processor",
            subsystem_type=SubsystemType.LANGUAGE_PROCESSOR,
            capabilities=["natural_language", "intent_detection", "translation"],
            handler=example_handler
        )
        
        coordinator_id = orchestrator.register_subsystem(
            name="Autonomous Coordinator",
            subsystem_type=SubsystemType.AUTONOMOUS_COORDINATOR,
            capabilities=["task_scheduling", "self_healing", "monitoring"],
            dependencies=[nlp_id],
            handler=example_handler
        )
        
        evolution_id = orchestrator.register_subsystem(
            name="Evolution Engine",
            subsystem_type=SubsystemType.EVOLUTION_ENGINE,
            capabilities=["learning", "optimization", "auto_upgrade"],
            dependencies=[coordinator_id],
            handler=example_handler
        )
        
        analyzer_id = orchestrator.register_subsystem(
            name="Code Analyzer",
            subsystem_type=SubsystemType.CODE_ANALYZER,
            capabilities=["code_analysis", "security_scan", "performance_check"],
            handler=example_handler
        )
        
        print(f"Registered {len(orchestrator.subsystems)} subsystems")
        
        # Start orchestrator
        await orchestrator.start()
        
        # Send messages
        print("\nSending messages...")
        
        await orchestrator.send_message(
            source_id=nlp_id,
            target_id=coordinator_id,
            message_type=MessageType.REQUEST,
            payload={"action": "schedule_task", "task_name": "Test Task"}
        )
        
        await orchestrator.send_message(
            source_id=coordinator_id,
            target_id="broadcast",
            message_type=MessageType.NOTIFICATION,
            payload={"event": "system_ready"}
        )
        
        # Create coordination task
        print("\nCreating coordination task...")
        task_id = await orchestrator.create_coordination_task(
            name="Complete Analysis Pipeline",
            description="Analyze code and optimize performance",
            required_capabilities=["code_analysis", "optimization"],
            steps=[
                {"action": "analyze", "params": {"target": "codebase"}},
                {"action": "optimize", "params": {"level": "aggressive"}}
            ]
        )
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Get ecosystem status
        print("\n=== Ecosystem Status ===")
        status = orchestrator.get_ecosystem_status()
        print(json.dumps(status, indent=2))
        
        # List subsystems
        print("\n=== Subsystems ===")
        subsystems = orchestrator.list_subsystems()
        print(json.dumps(subsystems, indent=2))
        
        # Get specific subsystem info
        print(f"\n=== Subsystem Info ({nlp_id}) ===")
        info = orchestrator.get_subsystem_info(nlp_id)
        print(json.dumps(info, indent=2))
        
        # Stop orchestrator
        await orchestrator.stop()
        print("\nOrchestrator stopped")
    
    asyncio.run(main())
