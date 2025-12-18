"""
Phase 9 Component Tests - Execution Architecture
Tests for Tool System, LangChain Integration, Agent Orchestration,
Function Calling, and MCP Integration
"""

import pytest
import asyncio
from datetime import datetime

import sys
sys.path.insert(0, '/home/runner/work/SynergyMesh/SynergyMesh')

from core.execution_architecture.tool_system import (
    Tool,
    ToolCategory,
    ToolRegistry,
    ToolExecutor,
    ToolResult,
    ToolStatus,
    create_database_tool,
    create_api_tool,
    create_code_tool,
)
from core.execution_architecture.langchain_integration import (
    LangChainToolAdapter,
    ReActAgentBuilder,
    ChainBuilder,
    AgentConfig,
    LangChainToolFormat,
)
from core.execution_architecture.agent_orchestration import (
    AgentOrchestrator,
    TaskPlanner,
    ExecutionContext,
    ExecutionStep,
    ExecutionPlan,
    StepStatus,
    OrchestratorConfig,
)
from core.execution_architecture.function_calling import (
    FunctionDefinition,
    FunctionCallHandler,
    ToolCallRouter,
    FunctionCallResult,
    FunctionCallStatus,
    RoutingRule,
    create_query_function,
    create_api_function,
    create_code_function,
)
from core.execution_architecture.mcp_integration import (
    MCPToolProvider,
    MCPToolConsumer,
    MCPBridge,
    MCPTool,
    MCPToolCall,
    MCPToolResult,
    MCPServerConfig,
    MCPMessageType,
)


# ==================== Tool System Tests ====================

class TestTool:
    """Tests for Tool class"""
    
    def test_tool_creation(self):
        """Test creating a tool"""
        tool = Tool(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.CODE,
            execute_fn=lambda params: "executed"
        )
        assert tool.name == "test_tool"
        assert tool.category == ToolCategory.CODE
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool execution"""
        tool = Tool(
            name="add",
            description="Add numbers",
            category=ToolCategory.CODE,
            execute_fn=lambda params: params.get("a", 0) + params.get("b", 0)
        )
        result = await tool.execute({"a": 2, "b": 3})
        assert result.status == ToolStatus.SUCCESS
        assert result.output == 5
    
    @pytest.mark.asyncio
    async def test_tool_async_execution(self):
        """Test async tool execution"""
        async def async_fn(params):
            await asyncio.sleep(0.01)
            return params.get("value", 0) * 2
        
        tool = Tool(
            name="double",
            description="Double a value",
            category=ToolCategory.CODE,
            execute_fn=async_fn
        )
        result = await tool.execute({"value": 5})
        assert result.status == ToolStatus.SUCCESS
        assert result.output == 10
    
    def test_tool_to_openai_function(self):
        """Test conversion to OpenAI format"""
        tool = Tool(
            name="query",
            description="Query database",
            category=ToolCategory.DATABASE,
            input_schema={
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"]
            }
        )
        openai_fn = tool.to_openai_function()
        assert openai_fn["name"] == "query"
        assert "parameters" in openai_fn


class TestToolRegistry:
    """Tests for ToolRegistry class"""
    
    def test_register_tool(self):
        """Test registering a tool"""
        registry = ToolRegistry()
        tool = Tool(
            name="test",
            description="Test",
            category=ToolCategory.CODE
        )
        registry.register(tool)
        assert registry.get("test") is not None
    
    def test_get_by_category(self):
        """Test getting tools by category"""
        registry = ToolRegistry()
        tool1 = Tool(name="db1", description="DB 1", category=ToolCategory.DATABASE)
        tool2 = Tool(name="db2", description="DB 2", category=ToolCategory.DATABASE)
        tool3 = Tool(name="api1", description="API 1", category=ToolCategory.API)
        
        registry.register(tool1)
        registry.register(tool2)
        registry.register(tool3)
        
        db_tools = registry.get_by_category(ToolCategory.DATABASE)
        assert len(db_tools) == 2
    
    def test_search_tools(self):
        """Test searching tools"""
        registry = ToolRegistry()
        tool1 = Tool(name="query_users", description="Query user data", category=ToolCategory.DATABASE)
        tool2 = Tool(name="send_email", description="Send email", category=ToolCategory.COMMUNICATION)
        
        registry.register(tool1)
        registry.register(tool2)
        
        results = registry.search("user")
        assert len(results) == 1
        assert results[0].name == "query_users"


class TestToolExecutor:
    """Tests for ToolExecutor class"""
    
    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test executing a tool"""
        registry = ToolRegistry()
        tool = Tool(
            name="greet",
            description="Greet someone",
            category=ToolCategory.CODE,
            execute_fn=lambda params: f"Hello, {params.get('name', 'World')}!"
        )
        registry.register(tool)
        
        executor = ToolExecutor(registry)
        result = await executor.execute("greet", {"name": "Alice"})
        
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "Hello, Alice!"
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self):
        """Test executing a nonexistent tool"""
        executor = ToolExecutor()
        result = await executor.execute("nonexistent", {})
        assert result.status == ToolStatus.FAILURE


# ==================== LangChain Integration Tests ====================

class TestLangChainToolAdapter:
    """Tests for LangChainToolAdapter"""
    
    def test_adapt_tool(self):
        """Test adapting a tool to LangChain format"""
        adapter = LangChainToolAdapter()
        tool = Tool(
            name="test",
            description="Test tool",
            category=ToolCategory.CODE,
            execute_fn=lambda x: x
        )
        adapted = adapter.adapt(tool)
        assert isinstance(adapted, LangChainToolFormat)
        assert adapted.name == "test"
    
    def test_adapt_many(self):
        """Test adapting multiple tools"""
        adapter = LangChainToolAdapter()
        tools = [
            Tool(name=f"tool_{i}", description=f"Tool {i}", category=ToolCategory.CODE)
            for i in range(3)
        ]
        adapted = adapter.adapt_many(tools)
        assert len(adapted) == 3


class TestReActAgentBuilder:
    """Tests for ReActAgentBuilder"""
    
    def test_build_agent(self):
        """Test building a ReAct agent"""
        builder = ReActAgentBuilder()
        config = AgentConfig(name="test_agent", description="Test agent")
        tools = [
            Tool(name="search", description="Search", category=ToolCategory.API)
        ]
        agent = builder.build_agent(config, tools)
        assert agent["config"].name == "test_agent"
        assert len(agent["tools"]) == 1
    
    @pytest.mark.asyncio
    async def test_run_agent(self):
        """Test running an agent"""
        builder = ReActAgentBuilder()
        config = AgentConfig(name="test", description="Test", max_iterations=2)
        tools = [
            Tool(name="echo", description="Echo", category=ToolCategory.CODE, execute_fn=lambda x: str(x))
        ]
        builder.build_agent(config, tools)
        
        result = await builder.run_agent("test", "Hello")
        assert result.success
        assert len(result.intermediate_steps) > 0


class TestChainBuilder:
    """Tests for ChainBuilder"""
    
    def test_create_chain(self):
        """Test creating a chain"""
        builder = ChainBuilder()
        builder.create_chain("test_chain")
        builder.add_step("test_chain", "tool1")
        builder.add_step("test_chain", "tool2")
        
        chain = builder.get_chain("test_chain")
        assert len(chain) == 2
    
    @pytest.mark.asyncio
    async def test_run_chain(self):
        """Test running a chain"""
        builder = ChainBuilder()
        builder.create_chain("simple")
        builder.add_step("simple", "step1", output_key="result1")
        
        result = await builder.run_chain("simple", {"input": "test"})
        assert result.get("success") or "error" not in result


# ==================== Agent Orchestration Tests ====================

class TestExecutionContext:
    """Tests for ExecutionContext"""
    
    def test_set_and_get(self):
        """Test setting and getting variables"""
        context = ExecutionContext()
        context.set("key", "value")
        assert context.get("key") == "value"
    
    def test_default_value(self):
        """Test default value for missing key"""
        context = ExecutionContext()
        assert context.get("missing", "default") == "default"
    
    def test_child_context(self):
        """Test child context inheritance"""
        parent = ExecutionContext()
        parent.set("parent_key", "parent_value")
        
        child = parent.create_child()
        assert child.get("parent_key") == "parent_value"
        
        child.set("child_key", "child_value")
        assert parent.get("child_key") is None


class TestTaskPlanner:
    """Tests for TaskPlanner"""
    
    def test_create_plan(self):
        """Test creating a plan"""
        planner = TaskPlanner()
        plan = planner.create_plan(
            name="Test Plan",
            steps=[
                {"name": "Step 1", "tool_name": "tool1"},
                {"name": "Step 2", "tool_name": "tool2"}
            ]
        )
        assert len(plan.steps) == 2
    
    def test_decompose_task(self):
        """Test task decomposition"""
        planner = TaskPlanner()
        plan = planner.decompose_task(
            "Query the database and deploy the result",
            ["database", "deployment"]
        )
        assert len(plan.steps) >= 1


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator"""
    
    def test_create_agent(self):
        """Test creating an agent"""
        orchestrator = AgentOrchestrator()
        agent = orchestrator.create_agent(
            agent_id="agent1",
            agent_type="worker",
            capabilities=["database", "api"]
        )
        assert agent["agent_id"] == "agent1"
    
    def test_find_capable_agent(self):
        """Test finding an agent by capability"""
        orchestrator = AgentOrchestrator()
        orchestrator.create_agent("db_agent", "worker", ["database"])
        orchestrator.create_agent("api_agent", "worker", ["api"])
        
        found = orchestrator.find_capable_agent("database")
        assert found is not None
        assert found["agent_id"] == "db_agent"
    
    @pytest.mark.asyncio
    async def test_execute_plan(self):
        """Test executing a plan"""
        orchestrator = AgentOrchestrator()
        planner = orchestrator.get_planner()
        
        plan = planner.create_plan(
            name="Simple Plan",
            steps=[{"name": "Step 1"}]
        )
        
        result = await orchestrator.execute_plan(plan)
        assert result["status"] == "completed"


# ==================== Function Calling Tests ====================

class TestFunctionDefinition:
    """Tests for FunctionDefinition"""
    
    def test_to_openai_format(self):
        """Test conversion to OpenAI format"""
        func = FunctionDefinition(
            name="get_weather",
            description="Get weather",
            parameters={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        )
        openai_format = func.to_openai_format()
        assert openai_format["type"] == "function"
        assert openai_format["function"]["name"] == "get_weather"
    
    def test_validate_arguments(self):
        """Test argument validation"""
        func = FunctionDefinition(
            name="test",
            description="Test",
            parameters={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        )
        errors = func.validate_arguments({})
        assert len(errors) > 0
        
        errors = func.validate_arguments({"name": "Alice"})
        assert len(errors) == 0


class TestFunctionCallHandler:
    """Tests for FunctionCallHandler"""
    
    def test_register_function(self):
        """Test registering a function"""
        handler = FunctionCallHandler()
        func = FunctionDefinition(name="test", description="Test")
        handler.register(func, lambda: "result")
        
        assert handler.get_function("test") is not None
    
    @pytest.mark.asyncio
    async def test_handle_call(self):
        """Test handling a function call"""
        handler = FunctionCallHandler()
        func = FunctionDefinition(
            name="add",
            description="Add numbers",
            parameters={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                }
            }
        )
        handler.register(func, lambda a, b: a + b)
        
        result = await handler.handle_call("add", {"a": 2, "b": 3})
        assert result.status == FunctionCallStatus.SUCCESS
        assert result.result == 5


class TestToolCallRouter:
    """Tests for ToolCallRouter"""
    
    def test_register_executor(self):
        """Test registering an executor"""
        router = ToolCallRouter()
        router.register_executor("exec1", lambda t, p: "result")
        assert "exec1" in router.list_executors()
    
    def test_routing_rules(self):
        """Test routing with rules"""
        router = ToolCallRouter()
        router.register_executor("db_exec", lambda t, p: "db_result")
        router.register_executor("default", lambda t, p: "default_result")
        
        router.add_rule(RoutingRule(
            name="db_rule",
            condition=lambda tool, params: "database" in tool,
            executor_id="db_exec",
            priority=1
        ))
        router.set_default_executor("default")
        
        executor = router.route("database_query", {})
        assert executor is not None


# ==================== MCP Integration Tests ====================

class TestMCPTool:
    """Tests for MCPTool"""
    
    def test_to_mcp_format(self):
        """Test conversion to MCP format"""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"}
        )
        mcp_format = tool.to_mcp_format()
        assert mcp_format["name"] == "test_tool"
        assert "inputSchema" in mcp_format
    
    def test_from_mcp_format(self):
        """Test creation from MCP format"""
        data = {
            "name": "imported_tool",
            "description": "Imported",
            "inputSchema": {"type": "object"}
        }
        tool = MCPTool.from_mcp_format(data)
        assert tool.name == "imported_tool"


class TestMCPToolProvider:
    """Tests for MCPToolProvider"""
    
    def test_register_tool(self):
        """Test registering a tool"""
        provider = MCPToolProvider()
        tool = MCPTool(name="test", description="Test")
        provider.register_tool(tool, lambda x: "result")
        
        tools = provider.get_tool_list()
        assert len(tools) == 1
    
    @pytest.mark.asyncio
    async def test_handle_tool_call(self):
        """Test handling a tool call"""
        provider = MCPToolProvider()
        tool = MCPTool(name="echo", description="Echo")
        provider.register_tool(tool, lambda args: args.get("msg", ""))
        
        call = MCPToolCall(name="echo", arguments={"msg": "hello"})
        result = await provider.handle_tool_call(call)
        
        assert result.success
        assert result.result == "hello"
    
    @pytest.mark.asyncio
    async def test_handle_list_tools_message(self):
        """Test handling tools/list message"""
        provider = MCPToolProvider()
        tool = MCPTool(name="tool1", description="Tool 1")
        provider.register_tool(tool, lambda x: x)
        
        response = await provider.handle_message({"method": "tools/list"})
        assert response["type"] == MCPMessageType.TOOL_LIST.value


class TestMCPToolConsumer:
    """Tests for MCPToolConsumer"""
    
    def test_add_server(self):
        """Test adding a server"""
        consumer = MCPToolConsumer()
        config = MCPServerConfig(name="test_server", url="http://localhost:8080")
        consumer.add_server(config)
        
        assert "test_server" in consumer.list_servers()
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """Test connecting and disconnecting"""
        consumer = MCPToolConsumer()
        config = MCPServerConfig(name="server1", url="http://localhost")
        consumer.add_server(config)
        
        connected = await consumer.connect("server1")
        assert connected
        assert consumer.is_connected("server1")
        
        await consumer.disconnect("server1")
        assert not consumer.is_connected("server1")


class TestMCPBridge:
    """Tests for MCPBridge"""
    
    def test_expose_tool(self):
        """Test exposing a tool"""
        bridge = MCPBridge()
        tool = Tool(
            name="internal_tool",
            description="Internal",
            category=ToolCategory.CODE,
            input_schema={"type": "object"},
            execute_fn=lambda x: "result"
        )
        bridge.expose_tool(tool)
        
        tools = bridge.get_all_tools()
        assert len(tools["local"]) == 1
    
    @pytest.mark.asyncio
    async def test_call_local_tool(self):
        """Test calling a local tool"""
        bridge = MCPBridge()
        tool = Tool(
            name="add",
            description="Add",
            category=ToolCategory.CODE,
            input_schema={"type": "object"},
            execute_fn=lambda params: params.get("a", 0) + params.get("b", 0)
        )
        bridge.expose_tool(tool)
        
        result = await bridge.call_tool("add", {"a": 1, "b": 2})
        assert result.success
        assert result.result == 3


# ==================== Factory Function Tests ====================

class TestToolFactories:
    """Tests for tool factory functions"""
    
    def test_create_database_tool(self):
        """Test database tool factory"""
        tool = create_database_tool(
            name="query",
            description="Query DB",
            execute_fn=lambda x: "query result"
        )
        assert tool.category == ToolCategory.DATABASE
        assert "database" in tool.tags
    
    def test_create_api_tool(self):
        """Test API tool factory"""
        tool = create_api_tool(
            name="fetch",
            description="Fetch data",
            execute_fn=lambda x: "api result"
        )
        assert tool.category == ToolCategory.API
        assert "api" in tool.tags
    
    def test_create_code_tool(self):
        """Test code tool factory"""
        tool = create_code_tool(
            name="execute",
            description="Execute code",
            execute_fn=lambda x: "code result"
        )
        assert tool.category == ToolCategory.CODE
        assert "code" in tool.tags


class TestFunctionFactories:
    """Tests for function definition factories"""
    
    def test_create_query_function(self):
        """Test query function factory"""
        func = create_query_function()
        assert func.name == "query_database"
        assert "query" in func.parameters.get("required", [])
    
    def test_create_api_function(self):
        """Test API function factory"""
        func = create_api_function()
        assert func.name == "call_api"
        assert "url" in func.parameters.get("required", [])
    
    def test_create_code_function(self):
        """Test code function factory"""
        func = create_code_function()
        assert func.name == "execute_code"
        assert "code" in func.parameters.get("required", [])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
