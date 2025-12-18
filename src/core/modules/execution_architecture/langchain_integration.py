"""
LangChain Tool Integration (LangChain 工具整合)
Adapts tools to LangChain format and builds ReAct agents

Reference: LangChain tool calling mechanism and ReAct agent patterns
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LangChainToolFormat:
    """LangChain compatible tool format"""
    name: str
    description: str
    func: Callable | None = None
    coroutine: Callable | None = None
    args_schema: dict | None = None
    return_direct: bool = False


class LangChainToolAdapter:
    """
    LangChain 工具適配器
    Converts internal Tool format to LangChain compatible format
    
    Reference: LangChain uses pre-built tools for ReAct agents [1]
    """

    def __init__(self):
        self._adapted_tools: dict[str, LangChainToolFormat] = {}

    def adapt(self, tool: Any) -> LangChainToolFormat:
        """Convert a tool to LangChain format"""
        adapted = LangChainToolFormat(
            name=tool.name,
            description=tool.description,
            args_schema=tool.input_schema,
            return_direct=False
        )

        # Handle async vs sync execution
        if tool.execute_fn:
            if asyncio.iscoroutinefunction(tool.execute_fn):
                adapted.coroutine = tool.execute_fn
            else:
                adapted.func = tool.execute_fn

        self._adapted_tools[tool.name] = adapted
        return adapted

    def adapt_many(self, tools: list[Any]) -> list[LangChainToolFormat]:
        """Convert multiple tools to LangChain format"""
        return [self.adapt(tool) for tool in tools]

    def get_adapted(self, tool_name: str) -> LangChainToolFormat | None:
        """Get an adapted tool by name"""
        return self._adapted_tools.get(tool_name)

    def to_langchain_tools(self) -> list[dict[str, Any]]:
        """Export all adapted tools in LangChain format"""
        tools = []
        for tool in self._adapted_tools.values():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "args_schema": tool.args_schema or {},
                "return_direct": tool.return_direct
            })
        return tools


@dataclass
class AgentConfig:
    """Configuration for ReAct agent"""
    name: str
    description: str
    model: str = "gpt-4"
    temperature: float = 0.0
    max_iterations: int = 10
    verbose: bool = True
    memory_enabled: bool = True
    handle_parsing_errors: bool = True


@dataclass
class AgentExecutionResult:
    """Result of agent execution"""
    agent_name: str
    input_text: str
    output: Any
    intermediate_steps: list[dict[str, Any]] = field(default_factory=list)
    success: bool = True
    error: str | None = None
    execution_time_ms: float = 0.0


class ReActAgentBuilder:
    """
    ReAct 代理構建器
    Builds ReAct agents with tool calling capabilities
    
    Reference: LangChain ReAct agent pattern for tool calling [1] [3]
    """

    def __init__(self, tool_adapter: LangChainToolAdapter | None = None):
        self.tool_adapter = tool_adapter or LangChainToolAdapter()
        self._agents: dict[str, dict[str, Any]] = {}

    def build_agent(
        self,
        config: AgentConfig,
        tools: list[Any]
    ) -> dict[str, Any]:
        """
        Build a ReAct agent with given tools
        
        The agent follows the ReAct pattern:
        1. Thought: Reason about what to do
        2. Action: Select and call a tool
        3. Observation: Process tool output
        4. Repeat until task is complete
        """
        # Adapt tools to LangChain format
        adapted_tools = self.tool_adapter.adapt_many(tools)

        # Build agent configuration
        agent = {
            "config": config,
            "tools": adapted_tools,
            "tool_names": [t.name for t in adapted_tools],
            "agent_type": "react",
            "created_at": datetime.now().isoformat(),
            "status": "ready"
        }

        self._agents[config.name] = agent
        return agent

    async def run_agent(
        self,
        agent_name: str,
        input_text: str,
        context: dict[str, Any] | None = None
    ) -> AgentExecutionResult:
        """Run a ReAct agent"""
        if agent_name not in self._agents:
            return AgentExecutionResult(
                agent_name=agent_name,
                input_text=input_text,
                output=None,
                success=False,
                error=f"Agent not found: {agent_name}"
            )

        agent = self._agents[agent_name]
        start_time = datetime.now()
        intermediate_steps = []

        try:
            # Simulate ReAct loop
            current_input = input_text
            max_iterations = agent["config"].max_iterations

            for iteration in range(max_iterations):
                # Step 1: Thought - Reason about what to do
                thought = f"Iteration {iteration + 1}: Analyzing task..."
                intermediate_steps.append({
                    "type": "thought",
                    "content": thought,
                    "iteration": iteration + 1
                })

                # Step 2: Action - Select tool (simplified)
                if agent["tools"]:
                    selected_tool = agent["tools"][0]
                    action = {
                        "tool": selected_tool.name,
                        "tool_input": {"query": current_input}
                    }
                    intermediate_steps.append({
                        "type": "action",
                        "content": action,
                        "iteration": iteration + 1
                    })

                    # Step 3: Observation - Execute tool
                    if selected_tool.coroutine:
                        observation = await selected_tool.coroutine(action["tool_input"])
                    elif selected_tool.func:
                        observation = selected_tool.func(action["tool_input"])
                    else:
                        observation = f"Tool {selected_tool.name} executed (simulated)"

                    intermediate_steps.append({
                        "type": "observation",
                        "content": observation,
                        "iteration": iteration + 1
                    })

                    # Check if task is complete
                    if iteration >= 1:  # Simplified completion check
                        break
                else:
                    # No tools, just respond
                    break

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return AgentExecutionResult(
                agent_name=agent_name,
                input_text=input_text,
                output=f"Task completed after {len(intermediate_steps)} steps",
                intermediate_steps=intermediate_steps,
                success=True,
                execution_time_ms=execution_time
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return AgentExecutionResult(
                agent_name=agent_name,
                input_text=input_text,
                output=None,
                intermediate_steps=intermediate_steps,
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )

    def get_agent(self, agent_name: str) -> dict[str, Any] | None:
        """Get an agent by name"""
        return self._agents.get(agent_name)

    def list_agents(self) -> list[str]:
        """List all agent names"""
        return list(self._agents.keys())


@dataclass
class ChainStep:
    """A step in a tool chain"""
    tool_name: str
    input_mapping: dict[str, str] = field(default_factory=dict)
    output_key: str = "output"
    continue_on_error: bool = False


class ChainBuilder:
    """
    鏈構建器
    Builds chains of tool calls for complex workflows
    
    Reference: LangChain chain composition for sequential tool calls
    """

    def __init__(self, tool_executor: Any = None):
        self.tool_executor = tool_executor
        self._chains: dict[str, list[ChainStep]] = {}

    def create_chain(self, chain_name: str) -> "ChainBuilder":
        """Create a new chain"""
        self._chains[chain_name] = []
        return self

    def add_step(
        self,
        chain_name: str,
        tool_name: str,
        input_mapping: dict[str, str] | None = None,
        output_key: str = "output",
        continue_on_error: bool = False
    ) -> "ChainBuilder":
        """Add a step to the chain"""
        if chain_name not in self._chains:
            self.create_chain(chain_name)

        step = ChainStep(
            tool_name=tool_name,
            input_mapping=input_mapping or {},
            output_key=output_key,
            continue_on_error=continue_on_error
        )
        self._chains[chain_name].append(step)
        return self

    async def run_chain(
        self,
        chain_name: str,
        initial_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Run a chain of tools"""
        if chain_name not in self._chains:
            return {"error": f"Chain not found: {chain_name}"}

        chain = self._chains[chain_name]
        context = initial_input.copy()
        results = []

        for step in chain:
            # Build input from mapping
            step_input = {}
            for target_key, source_key in step.input_mapping.items():
                if source_key in context:
                    step_input[target_key] = context[source_key]

            # Merge with context if no mapping specified
            if not step_input:
                step_input = context.copy()

            # Execute step
            try:
                if self.tool_executor:
                    result = await self.tool_executor.execute(step.tool_name, step_input)
                    step_output = result.output if hasattr(result, 'output') else result
                else:
                    step_output = f"Executed {step.tool_name} (simulated)"

                context[step.output_key] = step_output
                results.append({
                    "tool": step.tool_name,
                    "output": step_output,
                    "success": True
                })
            except Exception as e:
                if not step.continue_on_error:
                    return {
                        "error": str(e),
                        "failed_at": step.tool_name,
                        "results": results
                    }
                results.append({
                    "tool": step.tool_name,
                    "error": str(e),
                    "success": False
                })

        return {
            "success": True,
            "results": results,
            "final_context": context
        }

    def get_chain(self, chain_name: str) -> list[ChainStep]:
        """Get chain steps"""
        return self._chains.get(chain_name, [])

    def list_chains(self) -> list[str]:
        """List all chain names"""
        return list(self._chains.keys())
