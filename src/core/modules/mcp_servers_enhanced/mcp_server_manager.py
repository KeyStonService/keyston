"""
MCP Server Manager - Central management for all MCP servers

This module provides centralized management for MCP (Model Context Protocol) servers,
handling server lifecycle, health monitoring, and load balancing across multiple servers.
"""

import asyncio
import contextlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class ServerStatus(Enum):
    """MCP Server status enumeration"""
    INITIALIZING = 'initializing'
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    UNHEALTHY = 'unhealthy'
    STOPPED = 'stopped'


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    version: str = '1.0.0'
    host: str = 'localhost'
    port: int = 3000
    transport: str = 'stdio'  # stdio, http, websocket
    timeout: int = 30000  # milliseconds
    max_retries: int = 3
    retry_delay: int = 1000  # milliseconds
    health_check_interval: int = 30  # seconds
    capabilities: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServer:
    """Represents an MCP server instance"""
    id: str
    config: MCPServerConfig
    status: ServerStatus = ServerStatus.INITIALIZING
    tools: list[dict[str, Any]] = field(default_factory=list)
    resources: list[dict[str, Any]] = field(default_factory=list)
    prompts: list[dict[str, Any]] = field(default_factory=list)
    last_health_check: datetime | None = None
    error_count: int = 0
    request_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert server to dictionary representation"""
        return {
            'id': self.id,
            'name': self.config.name,
            'version': self.config.version,
            'status': self.status.value,
            'transport': self.config.transport,
            'tools_count': len(self.tools),
            'resources_count': len(self.resources),
            'prompts_count': len(self.prompts),
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'error_count': self.error_count,
            'request_count': self.request_count,
            'created_at': self.created_at.isoformat()
        }


class MCPServerManager:
    """
    Central manager for MCP servers
    
    Handles server registration, health monitoring, load balancing,
    and tool execution routing across multiple MCP servers.
    """

    def __init__(self):
        self._servers: dict[str, MCPServer] = {}
        self._tool_index: dict[str, str] = {}  # tool_name -> server_id
        self._health_check_task: asyncio.Task | None = None
        self._event_handlers: dict[str, list[Callable]] = {}
        self._is_running: bool = False

    async def start(self) -> None:
        """Start the server manager and health check loop"""
        if self._is_running:
            return

        self._is_running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info('MCPServerManager started')

    async def stop(self) -> None:
        """Stop the server manager and cleanup"""
        self._is_running = False

        if self._health_check_task:
            self._health_check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._health_check_task

        # Stop all servers
        for server_id in list(self._servers.keys()):
            await self.unregister_server(server_id)

        logger.info('MCPServerManager stopped')

    async def register_server(self, config: MCPServerConfig) -> MCPServer:
        """
        Register a new MCP server
        
        Args:
            config: Server configuration
            
        Returns:
            Registered MCPServer instance
        """
        server_id = str(uuid4())
        server = MCPServer(
            id=server_id,
            config=config
        )

        # Initialize server and load tools
        await self._initialize_server(server)

        self._servers[server_id] = server

        # Index all tools from this server
        for tool in server.tools:
            tool_name = tool.get('name', '')
            if tool_name:
                self._tool_index[tool_name] = server_id

        await self._emit_event('server_registered', server)
        logger.info(f'Registered MCP server: {config.name} (id: {server_id})')

        return server

    async def unregister_server(self, server_id: str) -> bool:
        """
        Unregister an MCP server
        
        Args:
            server_id: ID of server to unregister
            
        Returns:
            True if server was unregistered, False if not found
        """
        server = self._servers.pop(server_id, None)
        if not server:
            return False

        # Remove tool index entries
        tools_to_remove = [
            tool_name for tool_name, sid in self._tool_index.items()
            if sid == server_id
        ]
        for tool_name in tools_to_remove:
            del self._tool_index[tool_name]

        server.status = ServerStatus.STOPPED
        await self._emit_event('server_unregistered', server)
        logger.info(f'Unregistered MCP server: {server.config.name}')

        return True

    def get_server(self, server_id: str) -> MCPServer | None:
        """Get server by ID"""
        return self._servers.get(server_id)

    def get_server_by_name(self, name: str) -> MCPServer | None:
        """Get server by name"""
        for server in self._servers.values():
            if server.config.name == name:
                return server
        return None

    def list_servers(self, status: ServerStatus | None = None) -> list[MCPServer]:
        """
        List all registered servers
        
        Args:
            status: Optional filter by status
            
        Returns:
            List of servers
        """
        servers = list(self._servers.values())
        if status:
            servers = [s for s in servers if s.status == status]
        return servers

    def get_tool_server(self, tool_name: str) -> MCPServer | None:
        """Get the server that provides a specific tool"""
        server_id = self._tool_index.get(tool_name)
        if server_id:
            return self._servers.get(server_id)
        return None

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a tool on the appropriate server
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        server = self.get_tool_server(tool_name)
        if not server:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name}',
                'error_code': 'TOOL_NOT_FOUND'
            }

        if server.status not in (ServerStatus.HEALTHY, ServerStatus.DEGRADED):
            return {
                'success': False,
                'error': f'Server {server.config.name} is not available',
                'error_code': 'SERVER_UNAVAILABLE'
            }

        try:
            result = await self._execute_tool_on_server(server, tool_name, arguments)
            server.request_count += 1
            return result
        except Exception as e:
            server.error_count += 1
            logger.error(f'Tool execution failed: {tool_name} - {e}')
            return {
                'success': False,
                'error': str(e),
                'error_code': 'EXECUTION_ERROR'
            }

    def list_all_tools(self) -> list[dict[str, Any]]:
        """Get all available tools across all servers"""
        tools = []
        for server in self._servers.values():
            if server.status == ServerStatus.HEALTHY:
                for tool in server.tools:
                    tools.append({
                        **tool,
                        'server_id': server.id,
                        'server_name': server.config.name
                    })
        return tools

    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    async def _initialize_server(self, server: MCPServer) -> None:
        """Initialize a server and load its capabilities"""
        try:
            # Simulate loading tools based on server type
            server.tools = self._get_default_tools(server.config.name)
            server.resources = []
            server.prompts = []
            server.status = ServerStatus.HEALTHY
            server.last_health_check = datetime.now()
        except Exception as e:
            server.status = ServerStatus.UNHEALTHY
            logger.error(f'Failed to initialize server {server.config.name}: {e}')
            raise

    async def _health_check_loop(self) -> None:
        """Background task for health checking servers"""
        while self._is_running:
            try:
                await asyncio.sleep(30)  # Default check interval

                for server in self._servers.values():
                    await self._check_server_health(server)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Health check loop error: {e}')

    async def _check_server_health(self, server: MCPServer) -> None:
        """Check health of a specific server"""
        try:
            # Simulate health check - in real implementation, this would
            # actually ping the server
            server.last_health_check = datetime.now()

            # Update status based on error rate
            error_rate = server.error_count / max(server.request_count, 1)
            if error_rate > 0.5:
                server.status = ServerStatus.UNHEALTHY
            elif error_rate > 0.1:
                server.status = ServerStatus.DEGRADED
            else:
                server.status = ServerStatus.HEALTHY

        except Exception as e:
            server.status = ServerStatus.UNHEALTHY
            logger.error(f'Health check failed for {server.config.name}: {e}')

    async def _execute_tool_on_server(
        self,
        server: MCPServer,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a tool on a specific server"""
        # Find the tool definition
        tool_def = None
        for tool in server.tools:
            if tool.get('name') == tool_name:
                tool_def = tool
                break

        if not tool_def:
            return {
                'success': False,
                'error': f'Tool {tool_name} not found on server {server.config.name}',
                'error_code': 'TOOL_NOT_FOUND'
            }

        # Simulate tool execution
        result = {
            'success': True,
            'tool': tool_name,
            'server': server.config.name,
            'arguments': arguments,
            'result': {
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
        }

        return result

    async def _emit_event(self, event: str, data: Any) -> None:
        """Emit an event to all handlers"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f'Event handler error for {event}: {e}')

    def _get_default_tools(self, server_name: str) -> list[dict[str, Any]]:
        """Get default tools based on server name"""
        tool_sets = {
            'code-analyzer': [
                {
                    'name': 'analyze-code',
                    'description': 'Analyze code for patterns, complexity, and quality',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string', 'description': 'Source code to analyze'},
                            'language': {'type': 'string', 'description': 'Programming language'},
                            'metrics': {'type': 'array', 'items': {'type': 'string'}}
                        },
                        'required': ['code']
                    }
                },
                {
                    'name': 'detect-patterns',
                    'description': 'Detect design patterns and anti-patterns',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string'},
                            'pattern_types': {'type': 'array', 'items': {'type': 'string'}}
                        },
                        'required': ['code']
                    }
                }
            ],
            'security-scanner': [
                {
                    'name': 'scan-vulnerabilities',
                    'description': 'Scan code for security vulnerabilities',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string'},
                            'severity_threshold': {'type': 'string', 'enum': ['low', 'medium', 'high', 'critical']}
                        },
                        'required': ['code']
                    }
                },
                {
                    'name': 'check-dependencies',
                    'description': 'Check dependencies for known vulnerabilities',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'manifest': {'type': 'string', 'description': 'Package manifest file content'},
                            'ecosystem': {'type': 'string', 'enum': ['npm', 'pip', 'maven', 'go']}
                        },
                        'required': ['manifest']
                    }
                }
            ],
            'slsa-validator': [
                {
                    'name': 'validate-provenance',
                    'description': 'Validate SLSA provenance data',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'provenance': {'type': 'object'},
                            'level': {'type': 'string', 'enum': ['1', '2', '3', '4']}
                        },
                        'required': ['provenance']
                    }
                },
                {
                    'name': 'check-slsa-compliance',
                    'description': 'Check SLSA compliance for target level',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'provenance': {'type': 'object'},
                            'targetLevel': {'type': 'string', 'enum': ['1', '2', '3', '4']}
                        },
                        'required': ['provenance']
                    }
                }
            ],
            'test-generator': [
                {
                    'name': 'generate-tests',
                    'description': 'Generate unit tests for code',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string'},
                            'framework': {'type': 'string', 'enum': ['jest', 'pytest', 'mocha', 'junit']},
                            'coverage_target': {'type': 'number', 'minimum': 0, 'maximum': 100}
                        },
                        'required': ['code']
                    }
                }
            ],
            'doc-generator': [
                {
                    'name': 'generate-docs',
                    'description': 'Generate documentation for code',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string'},
                            'format': {'type': 'string', 'enum': ['markdown', 'jsdoc', 'sphinx', 'openapi']},
                            'language': {'type': 'string'}
                        },
                        'required': ['code']
                    }
                }
            ],
            'performance-analyzer': [
                {
                    'name': 'analyze-performance',
                    'description': 'Analyze code performance characteristics',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'string'},
                            'analysis_type': {'type': 'string', 'enum': ['complexity', 'memory', 'runtime']}
                        },
                        'required': ['code']
                    }
                }
            ]
        }

        return tool_sets.get(server_name, [])


# Factory function for creating pre-configured manager
def create_server_manager() -> MCPServerManager:
    """Create a new MCPServerManager instance"""
    return MCPServerManager()
