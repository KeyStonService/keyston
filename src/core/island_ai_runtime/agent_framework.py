#!/usr/bin/env python3
"""
Agent Framework - 代理框架
Multi-Agent System for Automated Development

支援多種角色的 AI 代理：Architect, Developer, QA, Security, DevOps
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(Enum):
    """代理角色枚舉"""

    ARCHITECT = "architect"
    DEVELOPER = "developer"
    QA = "qa"
    SECURITY = "security"
    DEVOPS = "devops"


class AgentStatus(Enum):
    """代理狀態枚舉"""

    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentConfig:
    """代理配置"""

    name: str
    role: AgentRole
    model: str = "gpt-4o"
    temperature: float = 0.7
    system_prompt: str = ""
    capabilities: list[str] = field(default_factory=list)


@dataclass
class Task:
    """任務定義"""

    id: str
    name: str
    description: str
    assigned_agent: str | None = None
    status: str = "pending"
    result: Any = None
    dependencies: list[str] = field(default_factory=list)


@dataclass
class AgentMessage:
    """代理間訊息"""

    sender: str
    receiver: str
    content: str
    message_type: str = "request"  # request, response, notification


class Agent(ABC):
    """
    代理基類

    所有具體代理都應繼承此類別。
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = AgentStatus.IDLE
        self._message_queue: list[AgentMessage] = []

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def role(self) -> AgentRole:
        return self.config.role

    @abstractmethod
    async def execute_task(self, task: Task) -> Any:
        """執行任務"""
        pass

    @abstractmethod
    async def process_message(self, message: AgentMessage) -> AgentMessage | None:
        """處理訊息"""
        pass

    def send_message(self, receiver: str, content: str, msg_type: str = "request") -> None:
        """發送訊息"""
        message = AgentMessage(
            sender=self.name, receiver=receiver, content=content, message_type=msg_type
        )
        self._message_queue.append(message)

    def receive_message(self, message: AgentMessage) -> None:
        """接收訊息"""
        self._message_queue.append(message)


class ArchitectAgent(Agent):
    """架構師代理"""

    async def execute_task(self, task: Task) -> Any:
        """執行架構設計任務"""
        self.status = AgentStatus.WORKING
        # 實際實現會調用 LLM
        result = {"design": "Architecture design for " + task.name, "recommendations": []}
        self.status = AgentStatus.COMPLETED
        return result

    async def process_message(self, message: AgentMessage) -> AgentMessage | None:
        """處理架構相關訊息"""
        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=f"Acknowledged: {message.content}",
            message_type="response",
        )


class DeveloperAgent(Agent):
    """開發者代理"""

    async def execute_task(self, task: Task) -> Any:
        """執行開發任務"""
        self.status = AgentStatus.WORKING
        result = {"code": "// Generated code for " + task.name, "files_modified": []}
        self.status = AgentStatus.COMPLETED
        return result

    async def process_message(self, message: AgentMessage) -> AgentMessage | None:
        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=f"Acknowledged: {message.content}",
            message_type="response",
        )


class QAAgent(Agent):
    """QA 代理"""

    async def execute_task(self, task: Task) -> Any:
        """執行測試任務"""
        self.status = AgentStatus.WORKING
        result = {"tests": [], "coverage": 0.0, "passed": True}
        self.status = AgentStatus.COMPLETED
        return result

    async def process_message(self, message: AgentMessage) -> AgentMessage | None:
        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=f"Acknowledged: {message.content}",
            message_type="response",
        )


class SecurityAgent(Agent):
    """安全代理"""

    async def execute_task(self, task: Task) -> Any:
        """執行安全審計任務"""
        self.status = AgentStatus.WORKING
        result = {"vulnerabilities": [], "risk_level": "low", "recommendations": []}
        self.status = AgentStatus.COMPLETED
        return result

    async def process_message(self, message: AgentMessage) -> AgentMessage | None:
        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=f"Acknowledged: {message.content}",
            message_type="response",
        )


class DevOpsAgent(Agent):
    """DevOps 代理"""

    async def execute_task(self, task: Task) -> Any:
        """執行 DevOps 任務"""
        self.status = AgentStatus.WORKING
        result = {"deployment_status": "success", "artifacts": []}
        self.status = AgentStatus.COMPLETED
        return result

    async def process_message(self, message: AgentMessage) -> AgentMessage | None:
        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=f"Acknowledged: {message.content}",
            message_type="response",
        )


class AgentFramework:
    """
    代理框架

    負責管理和協調多個 AI 代理的運作。

    功能：
    - 代理編排
    - 任務分配
    - 協作通信
    - 狀態管理
    """

    AGENT_CLASSES: dict[AgentRole, type[Agent]] = {
        AgentRole.ARCHITECT: ArchitectAgent,
        AgentRole.DEVELOPER: DeveloperAgent,
        AgentRole.QA: QAAgent,
        AgentRole.SECURITY: SecurityAgent,
        AgentRole.DEVOPS: DevOpsAgent,
    }

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.agents: dict[str, Agent] = {}
        self.tasks: dict[str, Task] = {}
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """初始化代理"""
        agents_config = self.config.get("agents", {})

        for agent_id, agent_data in agents_config.items():
            role = AgentRole(agent_id)
            agent_config = AgentConfig(
                name=agent_data.get("name", agent_id),
                role=role,
                model=agent_data.get("model", "gpt-4o"),
                temperature=agent_data.get("temperature", 0.7),
                system_prompt=agent_data.get("system_prompt", ""),
                capabilities=agent_data.get("capabilities", []),
            )

            agent_class = self.AGENT_CLASSES.get(role)
            if agent_class:
                self.agents[agent_id] = agent_class(agent_config)

    def get_agent(self, agent_id: str) -> Agent | None:
        """獲取代理"""
        return self.agents.get(agent_id)

    def list_agents(self) -> list[str]:
        """列出所有代理"""
        return list(self.agents.keys())

    async def assign_task(self, task: Task, agent_id: str) -> None:
        """分配任務給代理"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        task.assigned_agent = agent_id
        task.status = "assigned"
        self.tasks[task.id] = task

    async def execute_task(self, task_id: str) -> Any:
        """執行任務"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        agent = self.agents.get(task.assigned_agent or "")
        if not agent:
            raise ValueError(f"No agent assigned to task: {task_id}")

        task.status = "running"
        result = await agent.execute_task(task)
        task.result = result
        task.status = "completed"

        return result

    async def orchestrate(self, tasks: list[Task]) -> dict[str, Any]:
        """編排多個任務"""
        results = {}

        for task in tasks:
            # 自動分配任務到適當的代理
            agent_id = self._select_agent_for_task(task)
            await self.assign_task(task, agent_id)
            results[task.id] = await self.execute_task(task.id)

        return results

    def _select_agent_for_task(self, task: Task) -> str:
        """根據任務選擇適當的代理"""
        # 簡單的任務分配邏輯
        task_lower = task.name.lower()

        if "design" in task_lower or "architecture" in task_lower:
            return "architect"
        elif "test" in task_lower or "qa" in task_lower:
            return "qa"
        elif "security" in task_lower or "audit" in task_lower:
            return "security"
        elif "deploy" in task_lower or "ci" in task_lower:
            return "devops"
        else:
            return "developer"
