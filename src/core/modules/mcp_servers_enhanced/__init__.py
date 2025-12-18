"""
Phase 19: MCP Servers Enhanced Integration Module

This module provides enhanced MCP (Model Context Protocol) server integrations
with real tool definitions, workflow orchestration, and advanced capabilities.

Key Components:
- MCPServerManager: Central manager for all MCP servers
- ToolRegistry: Registry for available tools across all servers
- WorkflowOrchestrator: Orchestrates complex multi-tool workflows
- RealTimeConnector: Real-time connection management for MCP servers
"""

from .mcp_server_manager import MCPServer, MCPServerConfig, MCPServerManager
from .realtime_connector import ConnectionConfig, ConnectionStatus, RealTimeConnector, TransportType
from .tool_registry import ToolCategory, ToolDefinition, ToolExecutionResult, ToolRegistry
from .workflow_orchestrator import Workflow, WorkflowOrchestrator, WorkflowResult, WorkflowStep

__all__ = [
    'MCPServerManager',
    'MCPServer',
    'MCPServerConfig',
    'ToolRegistry',
    'ToolDefinition',
    'ToolExecutionResult',
    'ToolCategory',
    'WorkflowOrchestrator',
    'WorkflowStep',
    'WorkflowResult',
    'Workflow',
    'RealTimeConnector',
    'ConnectionStatus',
    'ConnectionConfig',
    'TransportType',
]

__version__ = '1.0.0'
__author__ = 'SynergyMesh Team'
