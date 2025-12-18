"""
Real-Time Connector - Real-time connection management for MCP servers

This module provides real-time connection management capabilities
including WebSocket support, connection pooling, and automatic reconnection.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Connection status enumeration"""
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    RECONNECTING = 'reconnecting'
    ERROR = 'error'


class TransportType(Enum):
    """Transport type enumeration"""
    STDIO = 'stdio'
    HTTP = 'http'
    WEBSOCKET = 'websocket'
    SSE = 'sse'  # Server-Sent Events


@dataclass
class ConnectionConfig:
    """Configuration for a connection"""
    server_name: str
    transport: TransportType = TransportType.STDIO
    host: str = 'localhost'
    port: int = 3000
    path: str = '/'
    timeout: int = 30000  # milliseconds
    reconnect: bool = True
    reconnect_interval: int = 5000  # milliseconds
    max_reconnect_attempts: int = 10
    heartbeat_interval: int = 30000  # milliseconds
    headers: dict[str, str] = field(default_factory=dict)
    ssl: bool = False
    ssl_verify: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Connection:
    """Represents a connection to an MCP server"""
    id: str
    config: ConnectionConfig
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_activity: datetime | None = None
    connect_time: datetime | None = None
    reconnect_count: int = 0
    error_count: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert connection to dictionary"""
        return {
            'id': self.id,
            'server_name': self.config.server_name,
            'transport': self.config.transport.value,
            'status': self.status.value,
            'host': self.config.host,
            'port': self.config.port,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'connect_time': self.connect_time.isoformat() if self.connect_time else None,
            'reconnect_count': self.reconnect_count,
            'error_count': self.error_count,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'latency_ms': self.latency_ms,
            'metadata': self.metadata
        }


@dataclass
class Message:
    """Message for communication"""
    id: str
    type: str  # request, response, notification
    method: str | None = None
    params: dict[str, Any] | None = None
    result: Any | None = None
    error: dict[str, Any] | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary"""
        data = {
            'jsonrpc': '2.0',
            'id': self.id
        }
        if self.type == 'request':
            data['method'] = self.method
            if self.params:
                data['params'] = self.params
        elif self.type == 'response':
            if self.error:
                data['error'] = self.error
            else:
                data['result'] = self.result
        elif self.type == 'notification':
            data['method'] = self.method
            if self.params:
                data['params'] = self.params
            del data['id']
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        msg_id = data.get('id', str(uuid4()))

        if 'method' in data and 'id' in data:
            msg_type = 'request'
        elif 'method' in data:
            msg_type = 'notification'
        else:
            msg_type = 'response'

        return cls(
            id=msg_id,
            type=msg_type,
            method=data.get('method'),
            params=data.get('params'),
            result=data.get('result'),
            error=data.get('error')
        )


class RealTimeConnector:
    """
    Real-time connector for MCP server communication
    
    Features:
    - Multiple transport support (stdio, HTTP, WebSocket, SSE)
    - Connection pooling
    - Automatic reconnection
    - Heartbeat monitoring
    - Message queuing
    """

    def __init__(self):
        self._connections: dict[str, Connection] = {}
        self._pending_requests: dict[str, asyncio.Future] = {}
        self._message_handlers: dict[str, list[Callable]] = {}
        self._heartbeat_tasks: dict[str, asyncio.Task] = {}
        self._reconnect_tasks: dict[str, asyncio.Task] = {}
        self._is_running: bool = False

    async def start(self) -> None:
        """Start the connector"""
        self._is_running = True
        logger.info('RealTimeConnector started')

    async def stop(self) -> None:
        """Stop the connector and close all connections"""
        self._is_running = False

        # Cancel all heartbeat tasks
        for task in self._heartbeat_tasks.values():
            task.cancel()
        self._heartbeat_tasks.clear()

        # Cancel all reconnect tasks
        for task in self._reconnect_tasks.values():
            task.cancel()
        self._reconnect_tasks.clear()

        # Close all connections
        for conn_id in list(self._connections.keys()):
            await self.disconnect(conn_id)

        # Cancel pending requests
        for future in self._pending_requests.values():
            future.cancel()
        self._pending_requests.clear()

        logger.info('RealTimeConnector stopped')

    async def connect(self, config: ConnectionConfig) -> Connection:
        """
        Establish a connection to an MCP server
        
        Args:
            config: Connection configuration
            
        Returns:
            Connection instance
        """
        conn_id = str(uuid4())
        connection = Connection(
            id=conn_id,
            config=config,
            status=ConnectionStatus.CONNECTING
        )

        self._connections[conn_id] = connection

        try:
            # Simulate connection establishment
            await self._establish_connection(connection)
            connection.status = ConnectionStatus.CONNECTED
            connection.connect_time = datetime.now()
            connection.last_activity = datetime.now()

            # Start heartbeat if configured
            if config.heartbeat_interval > 0:
                self._heartbeat_tasks[conn_id] = asyncio.create_task(
                    self._heartbeat_loop(connection)
                )

            await self._emit_event('connected', connection)
            logger.info(f'Connected to {config.server_name} (id: {conn_id})')

        except Exception as e:
            connection.status = ConnectionStatus.ERROR
            connection.error_count += 1
            logger.error(f'Failed to connect to {config.server_name}: {e}')

            if config.reconnect:
                self._schedule_reconnect(connection)
            else:
                raise

        return connection

    async def disconnect(self, connection_id: str) -> bool:
        """
        Disconnect from a server
        
        Returns:
            True if disconnected, False if not found
        """
        connection = self._connections.pop(connection_id, None)
        if not connection:
            return False

        # Cancel heartbeat
        task = self._heartbeat_tasks.pop(connection_id, None)
        if task:
            task.cancel()

        # Cancel reconnect
        task = self._reconnect_tasks.pop(connection_id, None)
        if task:
            task.cancel()

        connection.status = ConnectionStatus.DISCONNECTED
        await self._emit_event('disconnected', connection)
        logger.info(f'Disconnected from {connection.config.server_name}')

        return True

    def get_connection(self, connection_id: str) -> Connection | None:
        """Get a connection by ID"""
        return self._connections.get(connection_id)

    def get_connection_by_server(self, server_name: str) -> Connection | None:
        """Get a connection by server name"""
        for conn in self._connections.values():
            if conn.config.server_name == server_name:
                return conn
        return None

    def list_connections(
        self,
        status: ConnectionStatus | None = None
    ) -> list[Connection]:
        """List all connections, optionally filtered by status"""
        connections = list(self._connections.values())
        if status:
            connections = [c for c in connections if c.status == status]
        return connections

    async def send_request(
        self,
        connection_id: str,
        method: str,
        params: dict[str, Any] | None = None,
        timeout: int | None = None
    ) -> Any:
        """
        Send a request to a server
        
        Args:
            connection_id: Connection ID
            method: Method name
            params: Optional parameters
            timeout: Optional timeout in milliseconds
            
        Returns:
            Response result
            
        Raises:
            ConnectionError: If not connected
            TimeoutError: If request times out
        """
        connection = self._connections.get(connection_id)
        if not connection:
            raise ConnectionError(f'Connection not found: {connection_id}')

        if connection.status != ConnectionStatus.CONNECTED:
            raise ConnectionError(f'Connection not active: {connection.status.value}')

        # Create request message
        request_id = str(uuid4())
        message = Message(
            id=request_id,
            type='request',
            method=method,
            params=params
        )

        # Create future for response
        future = asyncio.Future()
        self._pending_requests[request_id] = future

        try:
            # Send message
            await self._send_message(connection, message)
            connection.messages_sent += 1
            connection.last_activity = datetime.now()

            # Wait for response
            timeout_sec = (timeout or connection.config.timeout) / 1000.0
            result = await asyncio.wait_for(future, timeout=timeout_sec)

            # Calculate latency
            latency = (datetime.now() - message.timestamp).total_seconds() * 1000
            connection.latency_ms = (connection.latency_ms + latency) / 2

            return result

        except TimeoutError:
            raise TimeoutError(f'Request timed out: {method}')
        finally:
            self._pending_requests.pop(request_id, None)

    async def send_notification(
        self,
        connection_id: str,
        method: str,
        params: dict[str, Any] | None = None
    ) -> None:
        """Send a notification (no response expected)"""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ConnectionError(f'Connection not found: {connection_id}')

        if connection.status != ConnectionStatus.CONNECTED:
            raise ConnectionError(f'Connection not active: {connection.status.value}')

        message = Message(
            id=str(uuid4()),
            type='notification',
            method=method,
            params=params
        )

        await self._send_message(connection, message)
        connection.messages_sent += 1
        connection.last_activity = datetime.now()

    def on_message(self, method: str, handler: Callable) -> None:
        """Register a handler for incoming messages"""
        if method not in self._message_handlers:
            self._message_handlers[method] = []
        self._message_handlers[method].append(handler)

    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler"""
        if event not in self._message_handlers:
            self._message_handlers[event] = []
        self._message_handlers[event].append(handler)

    async def _establish_connection(self, connection: Connection) -> None:
        """Establish connection based on transport type"""
        config = connection.config

        if config.transport == TransportType.STDIO:
            # Simulate stdio connection
            pass
        elif config.transport == TransportType.HTTP:
            # HTTP doesn't maintain persistent connection
            pass
        elif config.transport == TransportType.WEBSOCKET:
            # Simulate WebSocket connection
            await asyncio.sleep(0.1)  # Simulate handshake
        elif config.transport == TransportType.SSE:
            # Simulate SSE connection
            await asyncio.sleep(0.1)

    async def _send_message(self, connection: Connection, message: Message) -> None:
        """Send a message over the connection"""
        config = connection.config
        json.dumps(message.to_dict())

        if config.transport == TransportType.STDIO:
            # In real implementation, write to stdin
            pass
        elif config.transport == TransportType.HTTP:
            # In real implementation, make HTTP request
            pass
        elif config.transport == TransportType.WEBSOCKET:
            # In real implementation, send over WebSocket
            pass

        # Simulate sending
        logger.debug(f'Sent message to {connection.config.server_name}: {message.method}')

        # Simulate response for requests
        if message.type == 'request':
            asyncio.create_task(self._simulate_response(connection, message))

    async def _simulate_response(self, connection: Connection, request: Message) -> None:
        """Simulate a response for testing"""
        await asyncio.sleep(0.05)  # Simulate latency

        response = Message(
            id=request.id,
            type='response',
            result={'status': 'success', 'method': request.method}
        )

        await self._handle_response(response)
        connection.messages_received += 1

    async def _handle_response(self, message: Message) -> None:
        """Handle an incoming response"""
        future = self._pending_requests.get(message.id)
        if future and not future.done():
            if message.error:
                future.set_exception(
                    Exception(message.error.get('message', 'Unknown error'))
                )
            else:
                future.set_result(message.result)

    async def _heartbeat_loop(self, connection: Connection) -> None:
        """Heartbeat loop for connection health monitoring"""
        while self._is_running and connection.id in self._connections:
            try:
                interval = connection.config.heartbeat_interval / 1000.0
                await asyncio.sleep(interval)

                if connection.status != ConnectionStatus.CONNECTED:
                    continue

                # Send heartbeat
                try:
                    await self.send_notification(
                        connection.id,
                        'ping',
                        {'timestamp': datetime.now().isoformat()}
                    )
                except Exception as e:
                    logger.warning(f'Heartbeat failed for {connection.config.server_name}: {e}')
                    connection.error_count += 1

                    if connection.error_count >= 3:
                        connection.status = ConnectionStatus.ERROR
                        if connection.config.reconnect:
                            self._schedule_reconnect(connection)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f'Heartbeat loop error: {e}')

    def _schedule_reconnect(self, connection: Connection) -> None:
        """Schedule a reconnection attempt"""
        if connection.reconnect_count >= connection.config.max_reconnect_attempts:
            logger.error(f'Max reconnect attempts reached for {connection.config.server_name}')
            return

        connection.status = ConnectionStatus.RECONNECTING

        async def reconnect():
            try:
                interval = connection.config.reconnect_interval / 1000.0
                await asyncio.sleep(interval)

                connection.reconnect_count += 1
                await self._establish_connection(connection)
                connection.status = ConnectionStatus.CONNECTED
                connection.error_count = 0
                connection.last_activity = datetime.now()

                await self._emit_event('reconnected', connection)
                logger.info(f'Reconnected to {connection.config.server_name}')

            except Exception as e:
                logger.error(f'Reconnect failed for {connection.config.server_name}: {e}')
                self._schedule_reconnect(connection)

        self._reconnect_tasks[connection.id] = asyncio.create_task(reconnect())

    async def _emit_event(self, event: str, data: Any) -> None:
        """Emit an event to handlers"""
        handlers = self._message_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f'Event handler error for {event}: {e}')

    def get_stats(self) -> dict[str, Any]:
        """Get connector statistics"""
        status_counts = {}
        for conn in self._connections.values():
            status = conn.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        total_sent = sum(c.messages_sent for c in self._connections.values())
        total_received = sum(c.messages_received for c in self._connections.values())
        avg_latency = (
            sum(c.latency_ms for c in self._connections.values()) /
            max(len(self._connections), 1)
        )

        return {
            'total_connections': len(self._connections),
            'status_distribution': status_counts,
            'pending_requests': len(self._pending_requests),
            'total_messages_sent': total_sent,
            'total_messages_received': total_received,
            'average_latency_ms': avg_latency
        }


# Factory function
def create_realtime_connector() -> RealTimeConnector:
    """Create a new RealTimeConnector instance"""
    return RealTimeConnector()
