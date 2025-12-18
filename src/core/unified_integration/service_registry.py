"""
═══════════════════════════════════════════════════════════════════════════════
                    SynergyMesh Service Registry
                    統一服務註冊表 - 系統元件發現與管理
═══════════════════════════════════════════════════════════════════════════════

This module provides a unified service registry for discovering, managing,
and coordinating all system components across the SynergyMesh platform.

Core Capabilities:
- Service registration and discovery (服務註冊與發現)
- Health monitoring integration (健康監控整合)
- Dependency resolution (依賴解析)
- Load balancing support (負載均衡支援)
- Configuration synchronization (配置同步)

Design Principles:
- Single source of truth for service metadata
- Real-time service status tracking
- Graceful degradation support
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    UNHEALTHY = 'unhealthy'
    UNKNOWN = 'unknown'
    STARTING = 'starting'
    STOPPING = 'stopping'
    STOPPED = 'stopped'


class ServiceCategory(Enum):
    """Categories of services in the system"""
    CORE = 'core'
    INTEGRATION = 'integration'
    EXECUTION = 'execution'
    MONITORING = 'monitoring'
    SECURITY = 'security'
    ORCHESTRATION = 'orchestration'
    STORAGE = 'storage'
    GATEWAY = 'gateway'


@dataclass
class ServiceEndpoint:
    """Service endpoint information"""
    protocol: str  # http, grpc, ws, internal
    host: str
    port: int
    path: str = '/'
    tls_enabled: bool = False
    
    @property
    def url(self) -> str:
        """Get full URL for the endpoint"""
        scheme = self.protocol
        if self.tls_enabled and self.protocol == 'http':
            scheme = 'https'
        return f"{scheme}://{self.host}:{self.port}{self.path}"


@dataclass
class ServiceHealth:
    """Service health information"""
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    latency_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceMetadata:
    """Service metadata and configuration"""
    service_id: str
    name: str
    version: str
    category: ServiceCategory
    description: str = ''
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    health: ServiceHealth = field(default_factory=ServiceHealth)
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'service_id': self.service_id,
            'name': self.name,
            'version': self.version,
            'category': self.category.value,
            'description': self.description,
            'endpoints': [
                {
                    'protocol': ep.protocol,
                    'host': ep.host,
                    'port': ep.port,
                    'path': ep.path,
                    'tls_enabled': ep.tls_enabled,
                    'url': ep.url
                }
                for ep in self.endpoints
            ],
            'dependencies': self.dependencies,
            'provides': self.provides,
            'tags': list(self.tags),
            'health': {
                'status': self.health.status.value,
                'last_check': self.health.last_check.isoformat() if self.health.last_check else None,
                'consecutive_failures': self.health.consecutive_failures,
                'latency_ms': self.health.latency_ms,
                'details': self.health.details
            },
            'registered_at': self.registered_at.isoformat(),
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'config': self.config
        }


@dataclass
class RegistryConfig:
    """Configuration for the service registry"""
    name: str = 'synergymesh-registry'
    health_check_interval_seconds: int = 30
    heartbeat_timeout_seconds: int = 90
    max_consecutive_failures: int = 3
    enable_auto_deregistration: bool = True
    auto_deregister_after_seconds: int = 300


class ServiceRegistry:
    """
    Service Registry - 統一服務註冊表
    
    Central registry for all SynergyMesh services providing:
    - Service registration and discovery
    - Health monitoring and status tracking
    - Dependency resolution and validation
    - Service metadata management
    
    Usage:
        registry = ServiceRegistry()
        await registry.start()
        
        # Register a service
        service_id = registry.register_service(
            name='execution-engine',
            version='1.0.0',
            category=ServiceCategory.EXECUTION,
            endpoints=[ServiceEndpoint('http', 'localhost', 8080)]
        )
        
        # Discover services
        services = registry.discover_by_category(ServiceCategory.EXECUTION)
    """
    
    def __init__(self, config: Optional[RegistryConfig] = None):
        """Initialize the service registry"""
        self.config = config or RegistryConfig()
        
        # Service storage
        self._services: Dict[str, ServiceMetadata] = {}
        self._services_by_name: Dict[str, Set[str]] = {}
        self._services_by_category: Dict[ServiceCategory, Set[str]] = {}
        self._services_by_capability: Dict[str, Set[str]] = {}
        
        # Health checkers
        self._health_checkers: Dict[str, Callable] = {}
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # State
        self._is_running = False
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            'registrations': 0,
            'deregistrations': 0,
            'health_checks': 0,
            'discoveries': 0
        }
        
        # Initialize category sets
        for category in ServiceCategory:
            self._services_by_category[category] = set()
            
        logger.info("ServiceRegistry initialized - 服務註冊表已初始化")
    
    async def start(self) -> None:
        """Start the service registry"""
        if self._is_running:
            return
            
        self._is_running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        await self._emit_event('registry_started', {'timestamp': datetime.now(timezone.utc)})
        logger.info("ServiceRegistry started - 服務註冊表已啟動")
    
    async def stop(self) -> None:
        """Stop the service registry"""
        self._is_running = False
        
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
                
        await self._emit_event('registry_stopped', {'timestamp': datetime.now(timezone.utc)})
        logger.info("ServiceRegistry stopped - 服務註冊表已停止")
    
    def register_service(
        self,
        name: str,
        version: str,
        category: ServiceCategory,
        description: str = '',
        endpoints: Optional[List[ServiceEndpoint]] = None,
        dependencies: Optional[List[str]] = None,
        provides: Optional[List[str]] = None,
        tags: Optional[Set[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        health_checker: Optional[Callable] = None,
        service_id: Optional[str] = None
    ) -> str:
        """
        Register a service with the registry
        
        註冊服務到註冊表
        
        Args:
            name: Service name
            version: Service version
            category: Service category
            description: Service description
            endpoints: Service endpoints
            dependencies: Service dependencies
            provides: Capabilities provided by the service
            tags: Service tags for filtering
            config: Service configuration
            health_checker: Custom health check function
            service_id: Optional service ID (auto-generated if not provided)
            
        Returns:
            Service ID
        """
        service_id = service_id or f"{name}-{uuid4().hex[:8]}"
        
        service = ServiceMetadata(
            service_id=service_id,
            name=name,
            version=version,
            category=category,
            description=description,
            endpoints=endpoints or [],
            dependencies=dependencies or [],
            provides=provides or [],
            tags=tags or set(),
            config=config or {}
        )
        
        # Store service
        self._services[service_id] = service
        
        # Index by name
        if name not in self._services_by_name:
            self._services_by_name[name] = set()
        self._services_by_name[name].add(service_id)
        
        # Index by category
        self._services_by_category[category].add(service_id)
        
        # Index by capabilities
        for capability in service.provides:
            if capability not in self._services_by_capability:
                self._services_by_capability[capability] = set()
            self._services_by_capability[capability].add(service_id)
        
        # Register health checker
        if health_checker:
            self._health_checkers[service_id] = health_checker
        
        # Update statistics
        self._stats['registrations'] += 1
        
        # Emit event (safely handle case when no event loop is running)
        self._safe_emit_event('service_registered', {
            'service_id': service_id,
            'name': name,
            'category': category.value
        })
        
        logger.info(f"Service registered: {name} ({service_id}) - 服務已註冊")
        return service_id
    
    def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service from the registry
        
        從註冊表取消註冊服務
        
        Args:
            service_id: Service ID to deregister
            
        Returns:
            True if deregistered, False if not found
        """
        service = self._services.pop(service_id, None)
        if not service:
            return False
        
        # Remove from indexes
        if service.name in self._services_by_name:
            self._services_by_name[service.name].discard(service_id)
            if not self._services_by_name[service.name]:
                del self._services_by_name[service.name]
        
        self._services_by_category[service.category].discard(service_id)
        
        for capability in service.provides:
            if capability in self._services_by_capability:
                self._services_by_capability[capability].discard(service_id)
        
        # Remove health checker
        self._health_checkers.pop(service_id, None)
        
        # Update statistics
        self._stats['deregistrations'] += 1
        
        # Emit event (safely handle case when no event loop is running)
        self._safe_emit_event('service_deregistered', {
            'service_id': service_id,
            'name': service.name
        })
        
        logger.info(f"Service deregistered: {service.name} ({service_id}) - 服務已取消註冊")
        return True
    
    def get_service(self, service_id: str) -> Optional[ServiceMetadata]:
        """Get service by ID"""
        return self._services.get(service_id)
    
    def discover_by_name(self, name: str) -> List[ServiceMetadata]:
        """
        Discover services by name
        
        按名稱發現服務
        """
        self._stats['discoveries'] += 1
        service_ids = self._services_by_name.get(name, set())
        return [self._services[sid] for sid in service_ids if sid in self._services]
    
    def discover_by_category(self, category: ServiceCategory) -> List[ServiceMetadata]:
        """
        Discover services by category
        
        按類別發現服務
        """
        self._stats['discoveries'] += 1
        service_ids = self._services_by_category.get(category, set())
        return [self._services[sid] for sid in service_ids if sid in self._services]
    
    def discover_by_capability(self, capability: str) -> List[ServiceMetadata]:
        """
        Discover services by capability
        
        按能力發現服務
        """
        self._stats['discoveries'] += 1
        service_ids = self._services_by_capability.get(capability, set())
        return [self._services[sid] for sid in service_ids if sid in self._services]
    
    def discover_by_tag(self, tag: str) -> List[ServiceMetadata]:
        """
        Discover services by tag
        
        按標籤發現服務
        """
        self._stats['discoveries'] += 1
        return [
            service for service in self._services.values()
            if tag in service.tags
        ]
    
    def discover_healthy(self, category: Optional[ServiceCategory] = None) -> List[ServiceMetadata]:
        """
        Discover healthy services
        
        發現健康的服務
        """
        self._stats['discoveries'] += 1
        services = self._services.values()
        
        if category:
            service_ids = self._services_by_category.get(category, set())
            services = [self._services[sid] for sid in service_ids if sid in self._services]
        
        return [
            service for service in services
            if service.health.status == ServiceStatus.HEALTHY
        ]
    
    def heartbeat(self, service_id: str) -> bool:
        """
        Update service heartbeat
        
        更新服務心跳
        
        Args:
            service_id: Service ID
            
        Returns:
            True if heartbeat accepted, False if service not found
        """
        service = self._services.get(service_id)
        if not service:
            return False
        
        service.last_heartbeat = datetime.now(timezone.utc)
        return True
    
    def update_health(
        self,
        service_id: str,
        status: ServiceStatus,
        latency_ms: float = 0.0,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update service health status
        
        更新服務健康狀態
        """
        service = self._services.get(service_id)
        if not service:
            return False
        
        old_status = service.health.status
        service.health.status = status
        service.health.last_check = datetime.now(timezone.utc)
        service.health.latency_ms = latency_ms
        
        if details:
            service.health.details = details
        
        if status == ServiceStatus.HEALTHY:
            service.health.consecutive_failures = 0
        else:
            service.health.consecutive_failures += 1
        
        # Emit status change event (safely handle case when no event loop is running)
        if old_status != status:
            self._safe_emit_event('health_status_changed', {
                'service_id': service_id,
                'old_status': old_status.value,
                'new_status': status.value
            })
        
        return True
    
    def resolve_dependencies(self, service_id: str) -> Dict[str, Optional[ServiceMetadata]]:
        """
        Resolve dependencies for a service
        
        解析服務的依賴
        
        Returns:
            Dictionary mapping dependency names to resolved services
        """
        service = self._services.get(service_id)
        if not service:
            return {}
        
        resolved = {}
        for dep_name in service.dependencies:
            candidates = self.discover_healthy()
            matching = [
                s for s in candidates
                if s.name == dep_name or dep_name in s.provides
            ]
            resolved[dep_name] = matching[0] if matching else None
        
        return resolved
    
    def validate_dependencies(self, service_id: str) -> Dict[str, bool]:
        """
        Validate that all dependencies are available
        
        驗證所有依賴是否可用
        
        Returns:
            Dictionary mapping dependency names to availability status
        """
        resolved = self.resolve_dependencies(service_id)
        return {dep: service is not None for dep, service in resolved.items()}
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the service dependency graph
        
        獲取服務依賴圖
        """
        return {
            service_id: service.dependencies
            for service_id, service in self._services.items()
        }
    
    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def list_all_services(self) -> List[ServiceMetadata]:
        """List all registered services"""
        return list(self._services.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        status_counts = {}
        for service in self._services.values():
            status = service.health.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        category_counts = {
            category.value: len(service_ids)
            for category, service_ids in self._services_by_category.items()
        }
        
        return {
            'total_services': len(self._services),
            'registrations': self._stats['registrations'],
            'deregistrations': self._stats['deregistrations'],
            'health_checks': self._stats['health_checks'],
            'discoveries': self._stats['discoveries'],
            'status_counts': status_counts,
            'category_counts': category_counts,
            'is_running': self._is_running
        }
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while self._is_running:
            try:
                await self._run_health_checks()
                await self._check_heartbeat_timeouts()
                await asyncio.sleep(self.config.health_check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)
    
    async def _run_health_checks(self) -> None:
        """Run health checks for all services"""
        for service_id, service in list(self._services.items()):
            self._stats['health_checks'] += 1
            
            checker = self._health_checkers.get(service_id)
            if checker:
                try:
                    start_time = asyncio.get_event_loop().time()
                    
                    if asyncio.iscoroutinefunction(checker):
                        result = await checker()
                    else:
                        result = checker()
                    
                    latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
                    
                    if isinstance(result, bool):
                        status = ServiceStatus.HEALTHY if result else ServiceStatus.UNHEALTHY
                    elif isinstance(result, dict):
                        status = ServiceStatus(result.get('status', 'healthy'))
                    else:
                        status = ServiceStatus.HEALTHY
                    
                    self.update_health(service_id, status, latency_ms)
                    
                except Exception as e:
                    logger.warning(f"Health check failed for {service_id}: {e}")
                    self.update_health(
                        service_id,
                        ServiceStatus.UNHEALTHY,
                        details={'error': str(e)}
                    )
    
    async def _check_heartbeat_timeouts(self) -> None:
        """Check for heartbeat timeouts and deregister stale services"""
        if not self.config.enable_auto_deregistration:
            return
        
        now = datetime.now(timezone.utc)
        timeout = timedelta(seconds=self.config.auto_deregister_after_seconds)
        
        stale_services = []
        for service_id, service in self._services.items():
            if service.last_heartbeat:
                if now - service.last_heartbeat > timeout:
                    stale_services.append(service_id)
        
        for service_id in stale_services:
            logger.warning(f"Deregistering stale service: {service_id}")
            self.deregister_service(service_id)
    
    def _safe_emit_event(self, event: str, data: Any) -> None:
        """
        Safely emit an event, handling the case when no event loop is running.
        
        安全地發出事件，處理沒有事件循環運行的情況。
        """
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._emit_event(event, data))
        except RuntimeError:
            # No running event loop - emit synchronously to sync handlers only
            handlers = self._event_handlers.get(event, [])
            for handler in handlers:
                if not asyncio.iscoroutinefunction(handler):
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Sync event handler error for {event}: {e}")
    
    async def _emit_event(self, event: str, data: Any) -> None:
        """Emit an event to handlers"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Event handler error for {event}: {e}")


# Factory function
def create_service_registry(config: Optional[RegistryConfig] = None) -> ServiceRegistry:
    """Create a new ServiceRegistry instance"""
    return ServiceRegistry(config)


# Pre-defined service registrations for core components
def register_core_services(registry: ServiceRegistry) -> None:
    """
    Register core SynergyMesh services
    
    註冊 SynergyMesh 核心服務
    """
    # Mind Matrix Service
    registry.register_service(
        name='mind-matrix',
        version='1.0.0',
        category=ServiceCategory.CORE,
        description='核心心智矩陣服務',
        provides=['cognitive-processing', 'governance-validation'],
        tags={'core', 'critical'}
    )
    
    # Execution Engine
    registry.register_service(
        name='execution-engine',
        version='1.0.0',
        category=ServiceCategory.EXECUTION,
        description='執行引擎服務',
        provides=['action-execution', 'rollback'],
        dependencies=['mind-matrix'],
        tags={'core', 'execution'}
    )
    
    # System Orchestrator
    registry.register_service(
        name='system-orchestrator',
        version='1.0.0',
        category=ServiceCategory.ORCHESTRATION,
        description='系統編排服務',
        provides=['workflow-management', 'task-scheduling'],
        dependencies=['execution-engine'],
        tags={'core', 'orchestration'}
    )
    
    # Integration Hub
    registry.register_service(
        name='integration-hub',
        version='1.0.0',
        category=ServiceCategory.INTEGRATION,
        description='整合中樞服務',
        provides=['message-routing', 'event-pub-sub'],
        tags={'core', 'integration'}
    )
    
    # Configuration Manager
    registry.register_service(
        name='configuration-manager',
        version='1.0.0',
        category=ServiceCategory.CORE,
        description='配置管理服務',
        provides=['config-management', 'secret-management'],
        tags={'core', 'config'}
    )
    
    # SLSA Provenance Service
    registry.register_service(
        name='slsa-provenance',
        version='1.0.0',
        category=ServiceCategory.SECURITY,
        description='SLSA 溯源認證服務',
        provides=['attestation', 'signature-verification'],
        tags={'security', 'slsa'}
    )
    
    # Contracts L1 Service
    registry.register_service(
        name='contracts-l1',
        version='1.0.0',
        category=ServiceCategory.CORE,
        description='L1 合約管理服務',
        endpoints=[ServiceEndpoint('http', 'localhost', 3000)],
        provides=['contract-management', 'provenance-attestation'],
        dependencies=['slsa-provenance'],
        tags={'core', 'contracts'}
    )
    
    logger.info("Core services registered - 核心服務已註冊")
