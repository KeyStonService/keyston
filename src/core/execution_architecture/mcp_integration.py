"""
MCP Integration (MCP 整合)
Model Context Protocol integration for tool exposure and consumption

Reference: MCP protocol for AI agent tool interoperability
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime
import uuid
import json
import asyncio


class MCPMessageType(Enum):
    """Types of MCP messages"""
    TOOL_LIST = "tool_list"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


@dataclass
class MCPTool:
    """Tool definition in MCP format"""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Convert to MCP wire format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }
    
    @classmethod
    def from_mcp_format(cls, data: Dict[str, Any]) -> "MCPTool":
        """Create from MCP wire format"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            input_schema=data.get("inputSchema", {})
        )


@dataclass
class MCPToolCall:
    """A tool call in MCP format"""
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Convert to MCP wire format"""
        return {
            "type": MCPMessageType.TOOL_CALL.value,
            "id": self.call_id,
            "name": self.name,
            "arguments": self.arguments
        }


@dataclass
class MCPToolResult:
    """Result of an MCP tool call"""
    call_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Convert to MCP wire format"""
        return {
            "type": MCPMessageType.TOOL_RESULT.value,
            "id": self.call_id,
            "success": self.success,
            "result": self.result,
            "error": self.error
        }


class MCPToolProvider:
    """
    MCP 工具提供者
    Exposes internal tools via MCP protocol
    """
    
    def __init__(self, server_name: str = "synergymesh"):
        self.server_name = server_name
        self._tools: Dict[str, MCPTool] = {}
        self._handlers: Dict[str, Callable] = {}
        self._server_info = {
            "name": server_name,
            "version": "1.0.0",
            "protocol_version": "2024-11-05"
        }
    
    def register_tool(
        self,
        tool: MCPTool,
        handler: Callable
    ) -> None:
        """Register a tool to expose via MCP"""
        self._tools[tool.name] = tool
        self._handlers[tool.name] = handler
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool"""
        if tool_name in self._tools:
            del self._tools[tool_name]
        if tool_name in self._handlers:
            del self._handlers[tool_name]
    
    def expose_from_registry(self, tool_registry: Any) -> int:
        """Expose all tools from a ToolRegistry"""
        count = 0
        for tool in tool_registry.list_all():
            mcp_tool = MCPTool(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema
            )
            self.register_tool(mcp_tool, tool.execute)
            count += 1
        return count
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools in MCP format"""
        return [tool.to_mcp_format() for tool in self._tools.values()]
    
    def handle_list_tools(self) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "type": MCPMessageType.TOOL_LIST.value,
            "tools": self.get_tool_list()
        }
    
    async def handle_tool_call(self, call: MCPToolCall) -> MCPToolResult:
        """Handle a tool call request"""
        if call.name not in self._tools:
            return MCPToolResult(
                call_id=call.call_id,
                success=False,
                error=f"Tool not found: {call.name}"
            )
        
        handler = self._handlers.get(call.name)
        if not handler:
            return MCPToolResult(
                call_id=call.call_id,
                success=False,
                error=f"No handler for tool: {call.name}"
            )
        
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(call.arguments)
            else:
                result = handler(call.arguments)
            
            # Handle ToolResult objects
            if hasattr(result, 'output'):
                result = result.output
            
            return MCPToolResult(
                call_id=call.call_id,
                success=True,
                result=result
            )
            
        except Exception as e:
            return MCPToolResult(
                call_id=call.call_id,
                success=False,
                error=str(e)
            )
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming MCP message"""
        msg_type = message.get("type", "")
        
        if msg_type == MCPMessageType.TOOL_LIST.value or message.get("method") == "tools/list":
            return self.handle_list_tools()
        
        elif msg_type == MCPMessageType.TOOL_CALL.value or message.get("method") == "tools/call":
            call = MCPToolCall(
                name=message.get("name", message.get("params", {}).get("name", "")),
                arguments=message.get("arguments", message.get("params", {}).get("arguments", {})),
                call_id=message.get("id", str(uuid.uuid4()))
            )
            result = await self.handle_tool_call(call)
            return result.to_mcp_format()
        
        elif msg_type == MCPMessageType.PING.value:
            return {"type": MCPMessageType.PONG.value}
        
        else:
            return {
                "type": MCPMessageType.ERROR.value,
                "error": f"Unknown message type: {msg_type}"
            }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return self._server_info.copy()


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection"""
    name: str
    url: str
    protocol: str = "stdio"  # stdio, http, ws
    timeout: float = 30.0
    auth_token: Optional[str] = None


class MCPToolConsumer:
    """
    MCP 工具消費者
    Consumes tools from external MCP servers
    """
    
    def __init__(self):
        self._servers: Dict[str, MCPServerConfig] = {}
        self._remote_tools: Dict[str, Dict[str, MCPTool]] = {}
        self._connected: Set[str] = set()
    
    def add_server(self, config: MCPServerConfig) -> None:
        """Add an MCP server configuration"""
        self._servers[config.name] = config
        self._remote_tools[config.name] = {}
    
    def remove_server(self, server_name: str) -> None:
        """Remove an MCP server"""
        if server_name in self._servers:
            del self._servers[server_name]
        if server_name in self._remote_tools:
            del self._remote_tools[server_name]
        self._connected.discard(server_name)
    
    async def connect(self, server_name: str) -> bool:
        """Connect to an MCP server and fetch tools"""
        if server_name not in self._servers:
            return False
        
        # Simulated connection - in real implementation would use actual protocol
        self._connected.add(server_name)
        return True
    
    async def disconnect(self, server_name: str) -> None:
        """Disconnect from an MCP server"""
        self._connected.discard(server_name)
        if server_name in self._remote_tools:
            self._remote_tools[server_name].clear()
    
    def is_connected(self, server_name: str) -> bool:
        """Check if connected to a server"""
        return server_name in self._connected
    
    async def refresh_tools(self, server_name: str) -> int:
        """Refresh tool list from a server"""
        if server_name not in self._connected:
            return 0
        
        # Simulated tool fetch - in real implementation would call server
        # For now, return empty to indicate need for actual implementation
        return len(self._remote_tools.get(server_name, {}))
    
    def get_tools(self, server_name: str) -> List[MCPTool]:
        """Get tools from a specific server"""
        return list(self._remote_tools.get(server_name, {}).values())
    
    def get_all_tools(self) -> Dict[str, List[MCPTool]]:
        """Get all tools from all servers"""
        return {
            server: list(tools.values())
            for server, tools in self._remote_tools.items()
        }
    
    def find_tool(self, tool_name: str) -> Optional[tuple[str, MCPTool]]:
        """Find a tool across all servers"""
        for server_name, tools in self._remote_tools.items():
            if tool_name in tools:
                return (server_name, tools[tool_name])
        return None
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> MCPToolResult:
        """Call a tool on a remote server"""
        if server_name not in self._connected:
            return MCPToolResult(
                call_id=str(uuid.uuid4()),
                success=False,
                error=f"Not connected to server: {server_name}"
            )
        
        tools = self._remote_tools.get(server_name, {})
        if tool_name not in tools:
            return MCPToolResult(
                call_id=str(uuid.uuid4()),
                success=False,
                error=f"Tool not found on server {server_name}: {tool_name}"
            )
        
        # Simulated call - in real implementation would use actual protocol
        return MCPToolResult(
            call_id=str(uuid.uuid4()),
            success=True,
            result=f"Called {tool_name} on {server_name} (simulated)"
        )
    
    def list_servers(self) -> List[str]:
        """List all configured servers"""
        return list(self._servers.keys())
    
    def list_connected(self) -> List[str]:
        """List connected servers"""
        return list(self._connected)


class MCPBridge:
    """
    MCP 橋接器
    Bridges between internal tool system and MCP protocol
    """
    
    def __init__(
        self,
        provider: Optional[MCPToolProvider] = None,
        consumer: Optional[MCPToolConsumer] = None
    ):
        self.provider = provider or MCPToolProvider()
        self.consumer = consumer or MCPToolConsumer()
        self._tool_mappings: Dict[str, str] = {}  # MCP name -> internal name
    
    def expose_tool(
        self,
        internal_tool: Any,
        mcp_name: Optional[str] = None
    ) -> None:
        """Expose an internal tool via MCP"""
        name = mcp_name or internal_tool.name
        mcp_tool = MCPTool(
            name=name,
            description=internal_tool.description,
            input_schema=internal_tool.input_schema
        )
        self.provider.register_tool(mcp_tool, internal_tool.execute)
        self._tool_mappings[name] = internal_tool.name
    
    def expose_registry(self, registry: Any) -> int:
        """Expose all tools from a registry"""
        return self.provider.expose_from_registry(registry)
    
    async def import_server_tools(
        self,
        server_config: MCPServerConfig
    ) -> int:
        """Import tools from an external MCP server"""
        self.consumer.add_server(server_config)
        if await self.consumer.connect(server_config.name):
            return await self.consumer.refresh_tools(server_config.name)
        return 0
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool (local or remote)"""
        # Check local tools first
        if tool_name in self._tool_mappings or tool_name in self.provider._tools:
            call = MCPToolCall(name=tool_name, arguments=arguments)
            return await self.provider.handle_tool_call(call)
        
        # Check remote tools
        remote = self.consumer.find_tool(tool_name)
        if remote:
            server_name, _ = remote
            return await self.consumer.call_tool(server_name, tool_name, arguments)
        
        return MCPToolResult(
            call_id=str(uuid.uuid4()),
            success=False,
            error=f"Tool not found: {tool_name}"
        )
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all available tools (local and remote)"""
        return {
            "local": self.provider.get_tool_list(),
            "remote": self.consumer.get_all_tools()
        }
    
    def get_provider(self) -> MCPToolProvider:
        """Get the tool provider"""
        return self.provider
    
    def get_consumer(self) -> MCPToolConsumer:
        """Get the tool consumer"""
        return self.consumer
