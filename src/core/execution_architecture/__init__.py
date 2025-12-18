"""
SynergyMesh Execution Architecture (執行架構)
Phase 9: Complete tool system for converting AI knowledge into action

Core Components:
- Tool Definition System (工具定義系統)
- LangChain Tool Integration (LangChain 工具整合)
- Dynamic Agent Orchestration (動態代理編排)
- Function Calling System (函數調用系統)
- MCP Integration (MCP 整合)
"""

from .tool_system import (
    Tool,
    ToolCategory,
    ToolRegistry,
    ToolExecutor,
    ToolResult,
    ToolStatus,
)
from .langchain_integration import (
    LangChainToolAdapter,
    ReActAgentBuilder,
    ChainBuilder,
)
from .agent_orchestration import (
    AgentOrchestrator,
    TaskPlanner,
    ExecutionContext,
    ExecutionStep,
    StepStatus,
)
from .function_calling import (
    FunctionDefinition,
    FunctionCallHandler,
    ToolCallRouter,
    FunctionCallResult,
)
from .mcp_integration import (
    MCPToolProvider,
    MCPToolConsumer,
    MCPBridge,
)

__all__ = [
    # Tool System
    'Tool',
    'ToolCategory',
    'ToolRegistry',
    'ToolExecutor',
    'ToolResult',
    'ToolStatus',
    # LangChain Integration
    'LangChainToolAdapter',
    'ReActAgentBuilder',
    'ChainBuilder',
    # Agent Orchestration
    'AgentOrchestrator',
    'TaskPlanner',
    'ExecutionContext',
    'ExecutionStep',
    'StepStatus',
    # Function Calling
    'FunctionDefinition',
    'FunctionCallHandler',
    'ToolCallRouter',
    'FunctionCallResult',
    # MCP Integration
    'MCPToolProvider',
    'MCPToolConsumer',
    'MCPBridge',
]
