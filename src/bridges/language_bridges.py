"""
Language Bridge System - 語言橋接系統
Phase 3: Multi-language Code Integration

This module provides intelligent bridges for integrating code across
different programming languages in the SynergyMesh ecosystem.

Supported Languages:
- Python
- JavaScript/TypeScript
- Go
- Rust
- Java
- C#

設計原則: 多語言代碼自動整合，跨系統邊界自動管理
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CSHARP = "csharp"


class BridgeType(Enum):
    """Types of language bridges"""
    FFI = "ffi"              # Foreign Function Interface
    RPC = "rpc"              # Remote Procedure Call
    MESSAGE_QUEUE = "mq"     # Message Queue
    REST_API = "rest"        # REST API
    GRPC = "grpc"            # gRPC
    WEBSOCKET = "websocket"  # WebSocket


class BridgeStatus(Enum):
    """Bridge connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class BridgeEndpoint:
    """Endpoint for a language bridge"""
    endpoint_id: str
    language: Language
    host: str = "localhost"
    port: int = 0
    protocol: str = "http"
    path: str = "/"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BridgeConnection:
    """Active bridge connection"""
    connection_id: str
    source: BridgeEndpoint
    target: BridgeEndpoint
    bridge_type: BridgeType
    status: BridgeStatus = BridgeStatus.DISCONNECTED
    established_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeFragment:
    """Code fragment for cross-language execution"""
    fragment_id: str
    language: Language
    code: str
    entry_point: str = "main"
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of cross-language execution"""
    result_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    source_language: Language = Language.PYTHON
    target_language: Language = Language.PYTHON


class LanguageBridgeManager:
    """
    語言橋接管理器 - 多語言代碼整合
    
    Language Bridge Manager for seamless multi-language code integration.
    Enables code from different languages to work together transparently.
    
    Features:
    - 自動語言偵測: Automatic language detection
    - 跨語言調用: Cross-language function calls
    - 類型轉換: Automatic type conversion
    - 錯誤處理: Unified error handling
    
    設計目標:
    - 語言無關: Language-agnostic interface
    - 自動整合: Automatic code integration
    - 高性能: Low-latency bridging
    """
    
    # Default ports for language bridges
    DEFAULT_PORTS = {
        Language.PYTHON: 5000,
        Language.JAVASCRIPT: 3000,
        Language.GO: 8080,
        Language.RUST: 8081,
        Language.JAVA: 8082,
        Language.CSHARP: 8083
    }
    
    # Type mappings between languages
    TYPE_MAPPINGS = {
        (Language.PYTHON, Language.JAVASCRIPT): {
            "str": "string",
            "int": "number",
            "float": "number",
            "bool": "boolean",
            "list": "Array",
            "dict": "Object"
        },
        (Language.PYTHON, Language.GO): {
            "str": "string",
            "int": "int64",
            "float": "float64",
            "bool": "bool",
            "list": "[]interface{}",
            "dict": "map[string]interface{}"
        }
    }
    
    def __init__(self):
        """Initialize the Language Bridge Manager"""
        self.endpoints: Dict[str, BridgeEndpoint] = {}
        self.connections: Dict[str, BridgeConnection] = {}
        self.execution_handlers: Dict[Language, Callable] = {}
        
        # Statistics
        self.stats = {
            "bridges_created": 0,
            "executions_total": 0,
            "executions_successful": 0,
            "bytes_transferred": 0
        }
        
        logger.info("LanguageBridgeManager initialized - 語言橋接管理器已初始化")
    
    def register_endpoint(
        self,
        language: Language,
        host: str = "localhost",
        port: Optional[int] = None,
        protocol: str = "http",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a language endpoint
        
        註冊語言端點
        
        Args:
            language: Programming language
            host: Endpoint host
            port: Endpoint port (auto-assigned if None)
            protocol: Communication protocol
            metadata: Additional metadata
            
        Returns:
            Endpoint ID
        """
        endpoint_id = f"ep-{language.value}-{uuid.uuid4().hex[:6]}"
        
        if port is None:
            port = self.DEFAULT_PORTS.get(language, 9000)
        
        endpoint = BridgeEndpoint(
            endpoint_id=endpoint_id,
            language=language,
            host=host,
            port=port,
            protocol=protocol,
            metadata=metadata or {}
        )
        
        self.endpoints[endpoint_id] = endpoint
        logger.info(f"Endpoint registered: {endpoint_id} ({language.value})")
        
        return endpoint_id
    
    def create_bridge(
        self,
        source_endpoint_id: str,
        target_endpoint_id: str,
        bridge_type: BridgeType = BridgeType.REST_API
    ) -> str:
        """
        Create a bridge between two language endpoints
        
        在兩個語言端點之間創建橋接
        
        Args:
            source_endpoint_id: Source endpoint ID
            target_endpoint_id: Target endpoint ID
            bridge_type: Type of bridge to create
            
        Returns:
            Connection ID
        """
        source = self.endpoints.get(source_endpoint_id)
        target = self.endpoints.get(target_endpoint_id)
        
        if not source or not target:
            raise ValueError("Invalid endpoint IDs")
        
        connection_id = f"bridge-{uuid.uuid4().hex[:8]}"
        
        connection = BridgeConnection(
            connection_id=connection_id,
            source=source,
            target=target,
            bridge_type=bridge_type,
            status=BridgeStatus.CONNECTING,
            established_at=datetime.now()
        )
        
        self.connections[connection_id] = connection
        self.stats["bridges_created"] += 1
        
        # Simulate connection establishment
        connection.status = BridgeStatus.CONNECTED
        connection.last_activity = datetime.now()
        
        logger.info(
            f"Bridge created: {connection_id} "
            f"({source.language.value} → {target.language.value})"
        )
        
        return connection_id
    
    async def execute_cross_language(
        self,
        connection_id: str,
        code_fragment: CodeFragment,
        timeout_seconds: float = 30.0
    ) -> ExecutionResult:
        """
        Execute code across language boundary
        
        跨語言執行代碼
        
        Args:
            connection_id: Bridge connection ID
            code_fragment: Code to execute
            timeout_seconds: Execution timeout
            
        Returns:
            Execution result
        """
        result_id = f"exec-{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        connection = self.connections.get(connection_id)
        if not connection:
            return ExecutionResult(
                result_id=result_id,
                success=False,
                error="Bridge connection not found"
            )
        
        if connection.status != BridgeStatus.CONNECTED:
            return ExecutionResult(
                result_id=result_id,
                success=False,
                error=f"Bridge not connected: {connection.status.value}"
            )
        
        self.stats["executions_total"] += 1
        
        try:
            # Convert types if needed
            converted_params = self._convert_types(
                code_fragment.parameters,
                code_fragment.language,
                connection.target.language
            )
            
            # Simulate execution (in real implementation, would call actual bridge)
            output = await self._simulate_execution(
                code_fragment,
                connection.target.language
            )
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            connection.last_activity = datetime.now()
            connection.metrics["last_execution_ms"] = execution_time
            
            self.stats["executions_successful"] += 1
            
            return ExecutionResult(
                result_id=result_id,
                success=True,
                output=output,
                execution_time_ms=execution_time,
                source_language=code_fragment.language,
                target_language=connection.target.language
            )
            
        except Exception as e:
            logger.error(f"Cross-language execution failed: {e}")
            return ExecutionResult(
                result_id=result_id,
                success=False,
                error=str(e),
                source_language=code_fragment.language,
                target_language=connection.target.language
            )
    
    def _convert_types(
        self,
        params: Dict[str, Any],
        source_lang: Language,
        target_lang: Language
    ) -> Dict[str, Any]:
        """Convert types between languages"""
        mapping = self.TYPE_MAPPINGS.get((source_lang, target_lang), {})
        
        # Type conversion is handled by the bridge in real implementation
        # This is a simplified version
        return params
    
    async def _simulate_execution(
        self,
        code_fragment: CodeFragment,
        target_language: Language
    ) -> Any:
        """Simulate cross-language execution"""
        # Simulate processing time
        await asyncio.sleep(0.01)
        
        # Return simulated result
        return {
            "status": "executed",
            "language": target_language.value,
            "entry_point": code_fragment.entry_point,
            "message": f"Code executed successfully in {target_language.value}"
        }
    
    def get_bridge_status(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get bridge connection status"""
        connection = self.connections.get(connection_id)
        if not connection:
            return None
        
        return {
            "connection_id": connection_id,
            "source": {
                "language": connection.source.language.value,
                "host": connection.source.host,
                "port": connection.source.port
            },
            "target": {
                "language": connection.target.language.value,
                "host": connection.target.host,
                "port": connection.target.port
            },
            "bridge_type": connection.bridge_type.value,
            "status": connection.status.value,
            "established_at": connection.established_at.isoformat() if connection.established_at else None,
            "metrics": connection.metrics
        }
    
    def list_bridges(self) -> List[Dict[str, Any]]:
        """List all bridge connections"""
        return [
            self.get_bridge_status(conn_id)
            for conn_id in self.connections.keys()
        ]
    
    def disconnect_bridge(self, connection_id: str) -> bool:
        """Disconnect a bridge"""
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        connection.status = BridgeStatus.DISCONNECTED
        logger.info(f"Bridge disconnected: {connection_id}")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bridge manager statistics"""
        active_bridges = len([
            c for c in self.connections.values()
            if c.status == BridgeStatus.CONNECTED
        ])
        
        return {
            "endpoints_registered": len(self.endpoints),
            "bridges_created": self.stats["bridges_created"],
            "active_bridges": active_bridges,
            "executions_total": self.stats["executions_total"],
            "executions_successful": self.stats["executions_successful"],
            "success_rate": round(
                self.stats["executions_successful"] / max(self.stats["executions_total"], 1) * 100, 2
            ),
            "supported_languages": [lang.value for lang in Language]
        }


# Export classes
__all__ = [
    "LanguageBridgeManager",
    "Language",
    "BridgeType",
    "BridgeStatus",
    "BridgeEndpoint",
    "BridgeConnection",
    "CodeFragment",
    "ExecutionResult"
]
