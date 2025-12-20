"""
Multi-Agent Coordinator (多代理協調器)

Coordinates multiple AI agents working together on complex tasks.
Implements task routing, agent communication, and team management.

Reference: AI agents need specialization and clear role positioning [1]
Reference: Building reliable AI agents requires domain-specific expertise [1]
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime
import uuid
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Predefined agent roles in the system
    
    系統中預定義的代理角色
    """
    # Core roles
    ORCHESTRATOR = "orchestrator"       # 編排者：協調其他代理
    PLANNER = "planner"                 # 規劃者：制定執行計劃
    EXECUTOR = "executor"               # 執行者：執行具體任務
    VALIDATOR = "validator"             # 驗證者：驗證結果
    CRITIC = "critic"                   # 評論者：提供反饋
    
    # Specialized roles
    RESEARCHER = "researcher"           # 研究員：收集信息
    CODER = "coder"                     # 編碼者：編寫代碼
    REVIEWER = "reviewer"               # 審查者：代碼審查
    ANALYST = "analyst"                 # 分析師：數據分析
    ARCHITECT = "architect"             # 架構師：系統設計
    SECURITY_EXPERT = "security_expert" # 安全專家：安全審計
    DBA = "dba"                         # 數據庫管理員
    DEVOPS = "devops"                   # DevOps 工程師


class AgentCapability(Enum):
    """Capabilities that agents can have
    
    代理可以擁有的能力
    """
    # Code capabilities
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    CODE_REFACTORING = "code_refactoring"
    CODE_DEBUGGING = "code_debugging"
    
    # Analysis capabilities
    DATA_ANALYSIS = "data_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    
    # Execution capabilities
    TASK_EXECUTION = "task_execution"
    API_INTEGRATION = "api_integration"
    DATABASE_OPERATIONS = "database_operations"
    DEPLOYMENT = "deployment"
    
    # Communication capabilities
    NATURAL_LANGUAGE = "natural_language"
    DOCUMENTATION = "documentation"
    REPORTING = "reporting"


class MessageType(Enum):
    """Types of messages between agents"""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_RESULT = "task_result"
    QUERY = "query"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"
    ERROR = "error"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class AgentMessage:
    """Message passed between agents
    
    代理之間傳遞的消息
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = MessageType.NOTIFICATION
    sender_id: str = ""
    receiver_id: str = ""  # Empty for broadcast
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False
    response_timeout: float = 30.0  # seconds


@dataclass
class AgentDefinition:
    """Definition of an agent in the multi-agent system
    
    多代理系統中的代理定義
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    role: AgentRole = AgentRole.EXECUTOR
    capabilities: List[AgentCapability] = field(default_factory=list)
    description: str = ""
    model: str = "gpt-4"
    system_prompt: str = ""
    max_concurrent_tasks: int = 3
    priority: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities
    
    def can_handle_task(self, required_capabilities: List[AgentCapability]) -> bool:
        """Check if agent can handle a task with required capabilities"""
        return all(cap in self.capabilities for cap in required_capabilities)


@dataclass
class TeamTask:
    """A task to be executed by the agent team
    
    由代理團隊執行的任務
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    required_capabilities: List[AgentCapability] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_agents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCommunicationBus:
    """Communication bus for agent-to-agent messaging
    
    代理間通信總線
    
    Provides publish/subscribe messaging and direct messaging
    between agents in the multi-agent system.
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[AgentMessage] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self._running = False
    
    async def start(self) -> None:
        """Start the communication bus"""
        self._running = True
        asyncio.create_task(self._process_messages())
    
    async def stop(self) -> None:
        """Stop the communication bus"""
        self._running = False
    
    def subscribe(self, topic: str, callback: Callable) -> None:
        """Subscribe to a topic
        
        訂閱主題
        """
        self.subscribers[topic].append(callback)
    
    def unsubscribe(self, topic: str, callback: Callable) -> None:
        """Unsubscribe from a topic"""
        if callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
    
    async def publish(self, topic: str, message: AgentMessage) -> None:
        """Publish a message to a topic
        
        發布消息到主題
        """
        await self.message_queue.put((topic, message))
        self.message_history.append(message)
    
    async def send_direct(
        self,
        message: AgentMessage,
        wait_for_response: bool = False
    ) -> Optional[AgentMessage]:
        """Send a direct message to an agent
        
        直接發送消息給代理
        """
        topic = f"agent:{message.receiver_id}"
        await self.publish(topic, message)
        
        if wait_for_response and message.requires_response:
            future = asyncio.Future()
            self.pending_responses[message.id] = future
            try:
                return await asyncio.wait_for(
                    future,
                    timeout=message.response_timeout
                )
            except asyncio.TimeoutError:
                del self.pending_responses[message.id]
                return None
        
        return None
    
    async def broadcast(self, message: AgentMessage) -> None:
        """Broadcast a message to all agents
        
        廣播消息給所有代理
        """
        message.message_type = MessageType.BROADCAST
        await self.publish("broadcast", message)
    
    async def respond_to(self, original_message_id: str, response: AgentMessage) -> None:
        """Respond to a message
        
        回覆消息
        """
        if original_message_id in self.pending_responses:
            self.pending_responses[original_message_id].set_result(response)
            del self.pending_responses[original_message_id]
    
    async def _process_messages(self) -> None:
        """Process messages from the queue"""
        while self._running:
            try:
                topic, message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                for callback in self.subscribers.get(topic, []):
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logger.error(f"Error in message callback for topic {topic}: {e}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Critical error in message processing: {e}")
                break


class TaskRouter:
    """Routes tasks to appropriate agents based on capabilities
    
    任務路由器：根據能力將任務路由到合適的代理
    
    Implements intelligent task assignment based on:
    - Agent capabilities
    - Agent availability
    - Task priority
    - Load balancing
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentDefinition] = {}
        self.agent_load: Dict[str, int] = defaultdict(int)
        self.routing_rules: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: AgentDefinition) -> None:
        """Register an agent for routing
        
        註冊代理以進行路由
        """
        self.agents[agent.id] = agent
        self.agent_load[agent.id] = 0
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_load[agent_id]
    
    def add_routing_rule(
        self,
        name: str,
        condition: Callable[[TeamTask], bool],
        target_roles: List[AgentRole],
        priority: int = 0
    ) -> None:
        """Add a custom routing rule
        
        添加自定義路由規則
        """
        self.routing_rules.append({
            "name": name,
            "condition": condition,
            "target_roles": target_roles,
            "priority": priority
        })
        self.routing_rules.sort(key=lambda x: x["priority"])
    
    def find_suitable_agents(
        self,
        task: TeamTask,
        max_agents: int = 1
    ) -> List[AgentDefinition]:
        """Find agents suitable for a task
        
        找到適合任務的代理
        """
        suitable_agents = []
        
        # Check custom routing rules first
        for rule in self.routing_rules:
            if rule["condition"](task):
                for agent in self.agents.values():
                    if (agent.is_active and 
                        agent.role in rule["target_roles"] and
                        self.agent_load[agent.id] < agent.max_concurrent_tasks):
                        suitable_agents.append(agent)
                if suitable_agents:
                    break
        
        # Fallback to capability-based routing
        if not suitable_agents:
            for agent in self.agents.values():
                if (agent.is_active and
                    agent.can_handle_task(task.required_capabilities) and
                    self.agent_load[agent.id] < agent.max_concurrent_tasks):
                    suitable_agents.append(agent)
        
        # Sort by priority and load
        suitable_agents.sort(
            key=lambda a: (a.priority, self.agent_load[a.id])
        )
        
        return suitable_agents[:max_agents]
    
    def route_task(self, task: TeamTask) -> Optional[AgentDefinition]:
        """Route a task to the best available agent
        
        將任務路由到最佳可用代理
        """
        agents = self.find_suitable_agents(task, max_agents=1)
        if agents:
            agent = agents[0]
            self.agent_load[agent.id] += 1
            return agent
        return None
    
    def release_agent(self, agent_id: str) -> None:
        """Release an agent from a task"""
        if agent_id in self.agent_load and self.agent_load[agent_id] > 0:
            self.agent_load[agent_id] -= 1
    
    def get_load_status(self) -> Dict[str, Dict[str, Any]]:
        """Get load status for all agents"""
        return {
            agent_id: {
                "name": self.agents[agent_id].name,
                "current_load": self.agent_load[agent_id],
                "max_load": self.agents[agent_id].max_concurrent_tasks,
                "utilization": self.agent_load[agent_id] / self.agents[agent_id].max_concurrent_tasks
                if self.agents[agent_id].max_concurrent_tasks > 0 else 0
            }
            for agent_id in self.agents
        }


@dataclass
class AgentTeam:
    """A team of agents working together
    
    一起工作的代理團隊
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    agents: Dict[str, AgentDefinition] = field(default_factory=dict)
    leader_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_agent(self, agent: AgentDefinition) -> None:
        """Add an agent to the team"""
        self.agents[agent.id] = agent
    
    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the team"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            if self.leader_id == agent_id:
                self.leader_id = None
    
    def set_leader(self, agent_id: str) -> bool:
        """Set the team leader"""
        if agent_id in self.agents:
            self.leader_id = agent_id
            return True
        return False
    
    def get_agents_by_role(self, role: AgentRole) -> List[AgentDefinition]:
        """Get all agents with a specific role"""
        return [a for a in self.agents.values() if a.role == role]
    
    def get_agents_with_capability(self, capability: AgentCapability) -> List[AgentDefinition]:
        """Get all agents with a specific capability"""
        return [a for a in self.agents.values() if a.has_capability(capability)]


class MultiAgentCoordinator:
    """Coordinator for multi-agent systems
    
    多代理系統協調器
    
    This class manages multiple AI agents, coordinating their work,
    routing tasks, and managing communication between them.
    
    核心功能：
    1. 代理管理：註冊、配置、監控代理
    2. 任務路由：智能分配任務給合適的代理
    3. 通信管理：代理間的消息傳遞
    4. 團隊協作：組織代理成團隊
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentDefinition] = {}
        self.teams: Dict[str, AgentTeam] = {}
        self.tasks: Dict[str, TeamTask] = {}
        self.communication_bus = AgentCommunicationBus()
        self.task_router = TaskRouter()
        self._started = False
    
    async def start(self) -> None:
        """Start the coordinator
        
        啟動協調器
        """
        await self.communication_bus.start()
        self._started = True
    
    async def stop(self) -> None:
        """Stop the coordinator
        
        停止協調器
        """
        await self.communication_bus.stop()
        self._started = False
    
    def register_agent(self, agent: AgentDefinition) -> str:
        """Register a new agent
        
        註冊新代理
        """
        self.agents[agent.id] = agent
        self.task_router.register_agent(agent)
        
        # Subscribe agent to its own channel
        self.communication_bus.subscribe(
            f"agent:{agent.id}",
            lambda msg: self._handle_agent_message(agent.id, msg)
        )
        
        return agent.id
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent
        
        取消註冊代理
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.task_router.unregister_agent(agent_id)
            return True
        return False
    
    def create_team(
        self,
        name: str,
        agent_ids: List[str],
        leader_id: Optional[str] = None
    ) -> AgentTeam:
        """Create a team of agents
        
        創建代理團隊
        """
        team = AgentTeam(name=name, description=f"Team: {name}")
        
        for agent_id in agent_ids:
            if agent_id in self.agents:
                team.add_agent(self.agents[agent_id])
        
        if leader_id and leader_id in team.agents:
            team.set_leader(leader_id)
        
        self.teams[team.id] = team
        return team
    
    async def submit_task(self, task: TeamTask) -> str:
        """Submit a task for execution
        
        提交任務以執行
        """
        self.tasks[task.id] = task
        
        # Route task to appropriate agent
        agent = self.task_router.route_task(task)
        if agent:
            task.assigned_agents.append(agent.id)
            task.status = "assigned"
            
            # Notify agent
            await self.communication_bus.send_direct(
                AgentMessage(
                    message_type=MessageType.TASK_ASSIGNMENT,
                    sender_id="coordinator",
                    receiver_id=agent.id,
                    content=task,
                    requires_response=True
                )
            )
        else:
            task.status = "unassigned"
        
        return task.id
    
    async def execute_task(self, task_id: str) -> Optional[TeamTask]:
        """Execute a task
        
        執行任務
        """
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        task.status = "running"
        task.started_at = datetime.now()
        
        try:
            # In production: Actually execute via framework integrations
            await asyncio.sleep(0.1)  # Simulate execution
            
            task.result = f"Task {task.title} completed successfully"
            task.status = "completed"
            task.completed_at = datetime.now()
            
            # Release agents
            for agent_id in task.assigned_agents:
                self.task_router.release_agent(agent_id)
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.now()
        
        return task
    
    async def execute_workflow(
        self,
        tasks: List[TeamTask],
        parallel: bool = False
    ) -> List[TeamTask]:
        """Execute a workflow of tasks
        
        執行任務工作流
        """
        # Submit all tasks
        for task in tasks:
            await self.submit_task(task)
        
        results = []
        
        if parallel:
            # Execute tasks in parallel
            coroutines = [self.execute_task(t.id) for t in tasks]
            results = await asyncio.gather(*coroutines)
        else:
            # Execute tasks sequentially
            for task in tasks:
                result = await self.execute_task(task.id)
                results.append(result)
        
        return results
    
    def _handle_agent_message(self, agent_id: str, message: AgentMessage) -> None:
        """Handle a message received by an agent"""
        # In production: Process message and potentially trigger actions
        pass
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "id": agent.id,
            "name": agent.name,
            "role": agent.role.value,
            "is_active": agent.is_active,
            "capabilities": [c.value for c in agent.capabilities],
            "current_tasks": [
                t.id for t in self.tasks.values()
                if agent_id in t.assigned_agents and t.status == "running"
            ],
            "load": self.task_router.agent_load.get(agent_id, 0)
        }
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of the entire coordinator
        
        獲取整個協調器的狀態
        """
        return {
            "started": self._started,
            "agents_count": len(self.agents),
            "teams_count": len(self.teams),
            "tasks": {
                "total": len(self.tasks),
                "pending": len([t for t in self.tasks.values() if t.status == "pending"]),
                "running": len([t for t in self.tasks.values() if t.status == "running"]),
                "completed": len([t for t in self.tasks.values() if t.status == "completed"]),
                "failed": len([t for t in self.tasks.values() if t.status == "failed"])
            },
            "agent_load": self.task_router.get_load_status()
        }


# Factory functions for creating common agent configurations
def create_code_review_agent(name: str = "CodeReviewer") -> AgentDefinition:
    """Create a code review agent
    
    創建代碼審查代理
    """
    return AgentDefinition(
        name=name,
        role=AgentRole.REVIEWER,
        capabilities=[
            AgentCapability.CODE_REVIEW,
            AgentCapability.SECURITY_ANALYSIS,
            AgentCapability.DOCUMENTATION
        ],
        system_prompt="You are an expert code reviewer focused on quality, security, and best practices."
    )


def create_architect_agent(name: str = "Architect") -> AgentDefinition:
    """Create an architect agent
    
    創建架構師代理
    """
    return AgentDefinition(
        name=name,
        role=AgentRole.ARCHITECT,
        capabilities=[
            AgentCapability.ARCHITECTURE_ANALYSIS,
            AgentCapability.CODE_GENERATION,
            AgentCapability.DOCUMENTATION
        ],
        system_prompt="You are a system architect expert in designing scalable and maintainable systems."
    )


def create_security_agent(name: str = "SecurityExpert") -> AgentDefinition:
    """Create a security expert agent
    
    創建安全專家代理
    """
    return AgentDefinition(
        name=name,
        role=AgentRole.SECURITY_EXPERT,
        capabilities=[
            AgentCapability.SECURITY_ANALYSIS,
            AgentCapability.CODE_REVIEW,
            AgentCapability.REPORTING
        ],
        system_prompt="You are a security expert focused on identifying and mitigating security vulnerabilities."
    )


def create_devops_agent(name: str = "DevOpsEngineer") -> AgentDefinition:
    """Create a DevOps agent
    
    創建 DevOps 代理
    """
    return AgentDefinition(
        name=name,
        role=AgentRole.DEVOPS,
        capabilities=[
            AgentCapability.DEPLOYMENT,
            AgentCapability.API_INTEGRATION,
            AgentCapability.PERFORMANCE_ANALYSIS
        ],
        system_prompt="You are a DevOps engineer expert in CI/CD, deployment, and infrastructure."
    )
