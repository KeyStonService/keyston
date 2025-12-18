"""
Dynamic Agent Orchestration (動態代理編排)
Manages agent creation, task planning, and execution context

Reference: AI agent orchestration patterns and task planning
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StepStatus(Enum):
    """Status of an execution step"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class ExecutionStep:
    """A single step in the execution plan"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tool_name: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def duration_ms(self) -> float | None:
        """Get execution duration in milliseconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return None


@dataclass
class ExecutionPlan:
    """A complete execution plan"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    steps: list[ExecutionStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "created"

    def get_step(self, step_id: str) -> ExecutionStep | None:
        """Get a step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_ready_steps(self) -> list[ExecutionStep]:
        """Get steps that are ready to execute (all dependencies completed)"""
        completed_ids = {s.step_id for s in self.steps if s.status == StepStatus.COMPLETED}
        ready = []
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                if all(dep in completed_ids for dep in step.dependencies):
                    ready.append(step)
        return ready


class ExecutionContext:
    """
    執行上下文
    Manages state and variables across agent execution
    """

    def __init__(self, context_id: str | None = None):
        self.context_id = context_id or str(uuid.uuid4())
        self._variables: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []
        self._metadata: dict[str, Any] = {}
        self.created_at = datetime.now()
        self._parent_context: ExecutionContext | None = None

    def set(self, key: str, value: Any) -> None:
        """Set a context variable"""
        self._variables[key] = value
        self._history.append({
            "action": "set",
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context variable"""
        if key in self._variables:
            return self._variables[key]
        if self._parent_context:
            return self._parent_context.get(key, default)
        return default

    def delete(self, key: str) -> None:
        """Delete a context variable"""
        if key in self._variables:
            del self._variables[key]
            self._history.append({
                "action": "delete",
                "key": key,
                "timestamp": datetime.now().isoformat()
            })

    def has(self, key: str) -> bool:
        """Check if a variable exists"""
        if key in self._variables:
            return True
        if self._parent_context:
            return self._parent_context.has(key)
        return False

    def get_all(self) -> dict[str, Any]:
        """Get all variables"""
        all_vars = {}
        if self._parent_context:
            all_vars.update(self._parent_context.get_all())
        all_vars.update(self._variables)
        return all_vars

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata"""
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata"""
        return self._metadata.get(key, default)

    def create_child(self) -> "ExecutionContext":
        """Create a child context"""
        child = ExecutionContext()
        child._parent_context = self
        return child

    def get_history(self) -> list[dict[str, Any]]:
        """Get context history"""
        return self._history.copy()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "context_id": self.context_id,
            "variables": self._variables,
            "metadata": self._metadata,
            "created_at": self.created_at.isoformat()
        }


class TaskPlanner:
    """
    任務規劃器
    Breaks complex tasks into executable steps
    
    Reference: Task planning and decomposition for AI agents
    """

    def __init__(self):
        self._templates: dict[str, list[dict[str, Any]]] = {}
        self._plans: dict[str, ExecutionPlan] = {}

    def register_template(
        self,
        template_name: str,
        steps: list[dict[str, Any]]
    ) -> None:
        """Register a plan template"""
        self._templates[template_name] = steps

    def create_plan(
        self,
        name: str,
        description: str = "",
        steps: list[dict[str, Any]] | None = None,
        from_template: str | None = None
    ) -> ExecutionPlan:
        """Create an execution plan"""
        plan_steps = []

        if from_template and from_template in self._templates:
            template_steps = self._templates[from_template]
        else:
            template_steps = steps or []

        for i, step_def in enumerate(template_steps):
            step = ExecutionStep(
                name=step_def.get("name", f"Step {i + 1}"),
                description=step_def.get("description", ""),
                tool_name=step_def.get("tool_name"),
                params=step_def.get("params", {}),
                dependencies=step_def.get("dependencies", [])
            )
            plan_steps.append(step)

        plan = ExecutionPlan(
            name=name,
            description=description,
            steps=plan_steps
        )

        self._plans[plan.plan_id] = plan
        return plan

    def decompose_task(
        self,
        task_description: str,
        available_tools: list[str]
    ) -> ExecutionPlan:
        """
        Decompose a task description into executable steps
        Uses heuristics to break down complex tasks
        """
        # Simple task decomposition based on keywords
        steps = []

        task_lower = task_description.lower()

        # Analyze task and create steps
        if "database" in task_lower or "query" in task_lower or "sql" in task_lower:
            if "database" in available_tools:
                steps.append({
                    "name": "Database Operation",
                    "description": "Execute database operation",
                    "tool_name": "database",
                    "params": {"task": task_description}
                })

        if "api" in task_lower or "http" in task_lower or "request" in task_lower:
            if "api" in available_tools:
                steps.append({
                    "name": "API Call",
                    "description": "Make API request",
                    "tool_name": "api",
                    "params": {"task": task_description}
                })

        if "deploy" in task_lower or "release" in task_lower:
            if "deployment" in available_tools:
                steps.append({
                    "name": "Deployment",
                    "description": "Deploy application",
                    "tool_name": "deployment",
                    "params": {"task": task_description}
                })

        if "code" in task_lower or "script" in task_lower or "execute" in task_lower:
            if "code" in available_tools:
                steps.append({
                    "name": "Code Execution",
                    "description": "Execute code",
                    "tool_name": "code",
                    "params": {"task": task_description}
                })

        # Default step if no specific tools matched
        if not steps:
            steps.append({
                "name": "General Task",
                "description": task_description,
                "tool_name": available_tools[0] if available_tools else None,
                "params": {"task": task_description}
            })

        return self.create_plan(
            name=f"Plan for: {task_description[:50]}...",
            description=task_description,
            steps=steps
        )

    def get_plan(self, plan_id: str) -> ExecutionPlan | None:
        """Get a plan by ID"""
        return self._plans.get(plan_id)

    def list_plans(self) -> list[str]:
        """List all plan IDs"""
        return list(self._plans.keys())


@dataclass
class OrchestratorConfig:
    """Configuration for agent orchestrator"""
    max_concurrent_agents: int = 5
    default_timeout: float = 300.0
    auto_retry: bool = True
    max_retries: int = 3


class AgentOrchestrator:
    """
    代理編排器
    Manages dynamic agent creation and coordination
    
    Reference: Dynamic agent orchestration patterns
    """

    def __init__(self, config: OrchestratorConfig | None = None):
        self.config = config or OrchestratorConfig()
        self._agents: dict[str, dict[str, Any]] = {}
        self._active_executions: dict[str, asyncio.Task] = {}
        self._planner = TaskPlanner()
        self._contexts: dict[str, ExecutionContext] = {}

    def create_agent(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: list[str],
        config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a new agent dynamically"""
        agent = {
            "agent_id": agent_id,
            "type": agent_type,
            "capabilities": capabilities,
            "config": config or {},
            "status": "ready",
            "created_at": datetime.now().isoformat()
        }
        self._agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        """Get an agent by ID"""
        return self._agents.get(agent_id)

    def list_agents(self) -> list[dict[str, Any]]:
        """List all agents"""
        return list(self._agents.values())

    def find_capable_agent(self, required_capability: str) -> dict[str, Any] | None:
        """Find an agent with a specific capability"""
        for agent in self._agents.values():
            if required_capability in agent["capabilities"]:
                return agent
        return None

    def create_context(self, context_id: str | None = None) -> ExecutionContext:
        """Create a new execution context"""
        context = ExecutionContext(context_id)
        self._contexts[context.context_id] = context
        return context

    def get_context(self, context_id: str) -> ExecutionContext | None:
        """Get a context by ID"""
        return self._contexts.get(context_id)

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        context: ExecutionContext | None = None,
        tool_executor: Any = None
    ) -> dict[str, Any]:
        """Execute a complete plan"""
        if context is None:
            context = self.create_context()

        plan.status = "running"
        results = []

        while True:
            ready_steps = plan.get_ready_steps()
            if not ready_steps:
                # Check if all steps are done or if we're stuck
                pending = [s for s in plan.steps if s.status == StepStatus.PENDING]
                if not pending:
                    break
                # Check for circular dependencies or missing dependencies
                failed = [s for s in plan.steps if s.status == StepStatus.FAILED]
                if failed:
                    break
                await asyncio.sleep(0.1)
                continue

            # Execute ready steps (could be parallel)
            for step in ready_steps:
                step.status = StepStatus.RUNNING
                step.started_at = datetime.now()

                try:
                    if step.tool_name and tool_executor:
                        result = await tool_executor.execute(step.tool_name, step.params)
                        step.result = result.output if hasattr(result, 'output') else result
                    else:
                        step.result = f"Executed {step.name} (simulated)"

                    step.status = StepStatus.COMPLETED
                    context.set(f"step_{step.step_id}_result", step.result)

                except Exception as e:
                    step.status = StepStatus.FAILED
                    step.error = str(e)

                step.completed_at = datetime.now()
                results.append({
                    "step_id": step.step_id,
                    "name": step.name,
                    "status": step.status.value,
                    "result": step.result,
                    "error": step.error,
                    "duration_ms": step.duration_ms
                })

        plan.status = "completed"

        return {
            "plan_id": plan.plan_id,
            "status": plan.status,
            "results": results,
            "context": context.to_dict()
        }

    async def orchestrate_task(
        self,
        task_description: str,
        available_tools: list[str],
        tool_executor: Any = None
    ) -> dict[str, Any]:
        """
        High-level task orchestration
        1. Decompose task into plan
        2. Create execution context
        3. Execute plan
        """
        # Create plan from task
        plan = self._planner.decompose_task(task_description, available_tools)

        # Create context
        context = self.create_context()
        context.set("task_description", task_description)
        context.set("available_tools", available_tools)

        # Execute plan
        result = await self.execute_plan(plan, context, tool_executor)

        return result

    def get_planner(self) -> TaskPlanner:
        """Get the task planner"""
        return self._planner
