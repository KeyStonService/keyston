"""
═══════════════════════════════════════════════════════════
        Connector Manager - 連接器管理器
        管理與外部系統的實際連接
═══════════════════════════════════════════════════════════

核心功能：
1. 管理連接器生命週期
2. 提供連接池管理
3. 處理連接重試和故障轉移
4. 監控連接健康狀態
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
import uuid


class ConnectorType(Enum):
    """連接器類型"""
    DATABASE = "database"
    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    CLOUD = "cloud"
    CUSTOM = "custom"


class ConnectionStatus(Enum):
    """連接狀態"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class ConnectionConfig:
    """連接配置"""
    
    host: str = "localhost"
    port: int = 0
    
    # 認證
    username: str = ""
    password: str = ""
    api_key: str = ""
    token: str = ""
    
    # SSL/TLS
    use_ssl: bool = False
    ssl_cert: str = ""
    ssl_key: str = ""
    ssl_ca: str = ""
    
    # 連接池
    pool_size: int = 10
    max_overflow: int = 5
    pool_timeout_seconds: int = 30
    
    # 重試
    retry_count: int = 3
    retry_delay_seconds: float = 1.0
    retry_backoff_multiplier: float = 2.0
    
    # 超時
    connect_timeout_seconds: int = 10
    read_timeout_seconds: int = 30
    write_timeout_seconds: int = 30
    
    # 其他
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Connector:
    """連接器"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    connector_type: ConnectorType = ConnectorType.CUSTOM
    
    # 狀態
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    
    # 配置
    config: ConnectionConfig = field(default_factory=ConnectionConfig)
    
    # 連接實例（實際的連接對象）
    connection: Any = None
    
    # 時間戳
    created_at: datetime = field(default_factory=datetime.now)
    connected_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    
    # 錯誤信息
    last_error: str = ""
    error_count: int = 0
    
    # 統計
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    
    # 健康檢查
    health_check: Optional[Callable] = None
    last_health_check: Optional[datetime] = None
    is_healthy: bool = False


class ConnectorManager:
    """
    連接器管理器 - 管理與外部系統的實際連接
    
    這是執行層的關鍵組件：
    - 沒有連接器，代碼只是理論
    - 連接器提供與真實世界的橋樑
    """
    
    def __init__(self):
        """初始化連接器管理器"""
        
        # 連接器存儲
        self._connectors: Dict[str, Connector] = {}
        
        # 類型索引
        self._type_index: Dict[ConnectorType, List[str]] = {}
        
        # 連接工廠
        self._factories: Dict[ConnectorType, Callable] = {}
        
        # 健康檢查任務
        self._health_check_task: Optional[asyncio.Task] = None
        self._health_check_interval: int = 30
        
        # 事件監聽器
        self._listeners: List[Callable] = []
        
        # 註冊默認工廠
        self._register_default_factories()
    
    def _register_default_factories(self):
        """註冊默認連接工廠"""
        
        self._factories[ConnectorType.DATABASE] = self._create_database_connector
        self._factories[ConnectorType.HTTP] = self._create_http_connector
        self._factories[ConnectorType.KUBERNETES] = self._create_kubernetes_connector
        self._factories[ConnectorType.DOCKER] = self._create_docker_connector
        self._factories[ConnectorType.FILE_SYSTEM] = self._create_filesystem_connector
        self._factories[ConnectorType.MESSAGE_QUEUE] = self._create_mq_connector
    
    async def create(
        self,
        name: str,
        connector_type: ConnectorType,
        config: Optional[ConnectionConfig] = None
    ) -> Connector:
        """
        創建連接器
        
        Args:
            name: 連接器名稱
            connector_type: 連接器類型
            config: 連接配置
            
        Returns:
            創建的連接器
        """
        
        if config is None:
            config = ConnectionConfig()
        
        connector = Connector(
            name=name,
            connector_type=connector_type,
            config=config,
        )
        
        # 使用工廠創建實際連接
        if connector_type in self._factories:
            factory = self._factories[connector_type]
            connector.connection = await factory(config)
        
        # 存儲連接器
        self._connectors[name] = connector
        
        # 更新類型索引
        if connector_type not in self._type_index:
            self._type_index[connector_type] = []
        self._type_index[connector_type].append(name)
        
        # 通知監聽器
        self._notify_listeners("created", connector)
        
        return connector
    
    async def connect(self, name: str) -> bool:
        """
        建立連接
        
        Args:
            name: 連接器名稱
            
        Returns:
            是否成功
        """
        
        connector = self.get(name)
        if connector is None:
            return False
        
        connector.status = ConnectionStatus.CONNECTING
        
        try:
            # 模擬連接過程
            await asyncio.sleep(0.1)
            
            connector.status = ConnectionStatus.CONNECTED
            connector.connected_at = datetime.now()
            connector.is_healthy = True
            
            self._notify_listeners("connected", connector)
            
            return True
            
        except Exception as e:
            connector.status = ConnectionStatus.ERROR
            connector.last_error = str(e)
            connector.last_error_at = datetime.now()
            connector.error_count += 1
            
            self._notify_listeners("connection_error", connector, {"error": str(e)})
            
            return False
    
    async def disconnect(self, name: str) -> bool:
        """
        斷開連接
        
        Args:
            name: 連接器名稱
            
        Returns:
            是否成功
        """
        
        connector = self.get(name)
        if connector is None:
            return False
        
        try:
            # 模擬斷開連接
            await asyncio.sleep(0.05)
            
            connector.status = ConnectionStatus.DISCONNECTED
            connector.connection = None
            connector.is_healthy = False
            
            self._notify_listeners("disconnected", connector)
            
            return True
            
        except Exception as e:
            connector.last_error = str(e)
            connector.last_error_at = datetime.now()
            return False
    
    async def reconnect(self, name: str) -> bool:
        """
        重新連接
        
        Args:
            name: 連接器名稱
            
        Returns:
            是否成功
        """
        
        connector = self.get(name)
        if connector is None:
            return False
        
        connector.status = ConnectionStatus.RECONNECTING
        
        # 斷開現有連接
        if connector.connection is not None:
            await self.disconnect(name)
        
        # 重試連接
        config = connector.config
        for attempt in range(config.retry_count):
            success = await self.connect(name)
            if success:
                return True
            
            # 等待重試
            delay = config.retry_delay_seconds * (
                config.retry_backoff_multiplier ** attempt
            )
            await asyncio.sleep(delay)
        
        return False
    
    def get(self, name: str) -> Optional[Connector]:
        """獲取連接器"""
        return self._connectors.get(name)
    
    def has(self, name: str) -> bool:
        """檢查是否存在連接器"""
        return name in self._connectors
    
    def is_connected(self, name: str) -> bool:
        """檢查是否已連接"""
        connector = self.get(name)
        if connector is None:
            return False
        return connector.status == ConnectionStatus.CONNECTED
    
    def get_by_type(self, connector_type: ConnectorType) -> List[Connector]:
        """按類型獲取連接器"""
        names = self._type_index.get(connector_type, [])
        return [self._connectors[name] for name in names if name in self._connectors]
    
    def get_all(self) -> List[Connector]:
        """獲取所有連接器"""
        return list(self._connectors.values())
    
    def get_connected(self) -> List[Connector]:
        """獲取所有已連接的連接器"""
        return [
            c for c in self._connectors.values()
            if c.status == ConnectionStatus.CONNECTED
        ]
    
    async def remove(self, name: str) -> bool:
        """
        移除連接器
        
        Args:
            name: 連接器名稱
            
        Returns:
            是否成功
        """
        
        connector = self.get(name)
        if connector is None:
            return False
        
        # 先斷開連接
        if connector.status == ConnectionStatus.CONNECTED:
            await self.disconnect(name)
        
        # 從存儲中移除
        del self._connectors[name]
        
        # 更新類型索引
        if connector.connector_type in self._type_index:
            if name in self._type_index[connector.connector_type]:
                self._type_index[connector.connector_type].remove(name)
        
        self._notify_listeners("removed", connector)
        
        return True
    
    async def execute(
        self,
        name: str,
        operation: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        通過連接器執行操作
        
        Args:
            name: 連接器名稱
            operation: 操作名稱
            params: 操作參數
            
        Returns:
            執行結果
        """
        
        connector = self.get(name)
        if connector is None:
            return {
                "success": False,
                "error": f"Connector not found: {name}",
            }
        
        if connector.status != ConnectionStatus.CONNECTED:
            return {
                "success": False,
                "error": f"Connector not connected: {name}",
            }
        
        start_time = datetime.now()
        
        try:
            # 模擬操作執行
            await asyncio.sleep(0.05)
            
            # 更新統計
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            connector.total_requests += 1
            connector.successful_requests += 1
            connector.last_used_at = end_time
            
            # 更新平均延遲
            total = connector.total_requests
            current_avg = connector.average_latency_ms
            connector.average_latency_ms = (
                (current_avg * (total - 1) + latency_ms) / total
            )
            
            return {
                "success": True,
                "operation": operation,
                "result": params.get("expected_result", {}),
                "latency_ms": latency_ms,
            }
            
        except Exception as e:
            connector.total_requests += 1
            connector.failed_requests += 1
            connector.last_error = str(e)
            connector.last_error_at = datetime.now()
            connector.error_count += 1
            
            return {
                "success": False,
                "error": str(e),
            }
    
    async def health_check(self, name: str) -> Dict[str, Any]:
        """
        執行健康檢查
        
        Args:
            name: 連接器名稱
            
        Returns:
            健康檢查結果
        """
        
        connector = self.get(name)
        if connector is None:
            return {
                "healthy": False,
                "error": f"Connector not found: {name}",
            }
        
        result = {
            "name": name,
            "type": connector.connector_type.value,
            "status": connector.status.value,
            "healthy": False,
            "checks": [],
        }
        
        # 檢查連接狀態
        result["checks"].append({
            "name": "connection_status",
            "passed": connector.status == ConnectionStatus.CONNECTED,
            "message": f"Status: {connector.status.value}",
        })
        
        # 執行自定義健康檢查
        if connector.health_check is not None:
            try:
                custom_result = await connector.health_check()
                result["checks"].append({
                    "name": "custom_health_check",
                    "passed": custom_result,
                    "message": "Custom health check",
                })
            except Exception as e:
                result["checks"].append({
                    "name": "custom_health_check",
                    "passed": False,
                    "message": f"Error: {str(e)}",
                })
        
        # 判斷整體健康狀態
        result["healthy"] = all(check["passed"] for check in result["checks"])
        
        connector.last_health_check = datetime.now()
        connector.is_healthy = result["healthy"]
        
        return result
    
    async def health_check_all(self) -> Dict[str, Any]:
        """對所有連接器執行健康檢查"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "connectors": {},
            "summary": {
                "total": len(self._connectors),
                "healthy": 0,
                "unhealthy": 0,
            },
        }
        
        for name in self._connectors:
            result = await self.health_check(name)
            results["connectors"][name] = result
            
            if result["healthy"]:
                results["summary"]["healthy"] += 1
            else:
                results["summary"]["unhealthy"] += 1
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        
        total = len(self._connectors)
        connected = len([c for c in self._connectors.values() 
                        if c.status == ConnectionStatus.CONNECTED])
        healthy = len([c for c in self._connectors.values() if c.is_healthy])
        
        total_requests = sum(c.total_requests for c in self._connectors.values())
        successful_requests = sum(c.successful_requests for c in self._connectors.values())
        
        return {
            "total_connectors": total,
            "connected_connectors": connected,
            "healthy_connectors": healthy,
            "disconnected_connectors": total - connected,
            "connectors_by_type": {
                t.value: len(names) 
                for t, names in self._type_index.items()
            },
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": (
                round(successful_requests / total_requests, 4) * 100
                if total_requests > 0 else 0
            ),
        }
    
    def register_factory(
        self,
        connector_type: ConnectorType,
        factory: Callable
    ):
        """註冊連接工廠"""
        self._factories[connector_type] = factory
    
    def add_listener(self, listener: Callable):
        """添加事件監聽器"""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable):
        """移除事件監聽器"""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(
        self,
        event: str,
        connector: Connector,
        data: Optional[Dict[str, Any]] = None
    ):
        """通知監聽器"""
        for listener in self._listeners:
            try:
                listener(event, connector, data or {})
            except Exception:
                pass
    
    # ============ 默認連接工廠 ============
    
    async def _create_database_connector(
        self,
        config: ConnectionConfig
    ) -> Dict[str, Any]:
        """創建數據庫連接器"""
        return {
            "type": "database",
            "host": config.host,
            "port": config.port,
            "pool_size": config.pool_size,
        }
    
    async def _create_http_connector(
        self,
        config: ConnectionConfig
    ) -> Dict[str, Any]:
        """創建 HTTP 連接器"""
        return {
            "type": "http",
            "base_url": f"{'https' if config.use_ssl else 'http'}://{config.host}:{config.port}",
            "timeout": config.read_timeout_seconds,
        }
    
    async def _create_kubernetes_connector(
        self,
        config: ConnectionConfig
    ) -> Dict[str, Any]:
        """創建 Kubernetes 連接器"""
        return {
            "type": "kubernetes",
            "api_server": f"{config.host}:{config.port}",
            "namespace": config.extra.get("namespace", "default"),
        }
    
    async def _create_docker_connector(
        self,
        config: ConnectionConfig
    ) -> Dict[str, Any]:
        """創建 Docker 連接器"""
        return {
            "type": "docker",
            "socket": config.extra.get("socket", "/var/run/docker.sock"),
        }
    
    async def _create_filesystem_connector(
        self,
        config: ConnectionConfig
    ) -> Dict[str, Any]:
        """創建文件系統連接器"""
        return {
            "type": "filesystem",
            "base_path": config.extra.get("base_path", "/"),
        }
    
    async def _create_mq_connector(
        self,
        config: ConnectionConfig
    ) -> Dict[str, Any]:
        """創建消息隊列連接器"""
        return {
            "type": "message_queue",
            "broker": f"{config.host}:{config.port}",
            "queue": config.extra.get("queue", "default"),
        }
