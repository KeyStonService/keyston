"""
System Bootstrap - 系統啟動器
Initialize and configure all subsystems

系統初始化和配置
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ServiceLifecycle(Enum):
    """Service lifecycle states"""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    READY = "ready"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ServiceDefinition:
    """Service definition for registration"""
    name: str
    service_class: type
    dependencies: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    singleton: bool = True
    lazy: bool = False


@dataclass
class ServiceInstance:
    """Service instance information"""
    definition: ServiceDefinition
    instance: Any | None = None
    lifecycle: ServiceLifecycle = ServiceLifecycle.REGISTERED
    initialized_at: datetime | None = None
    error_message: str | None = None


@dataclass
class BootstrapConfig:
    """Bootstrap configuration"""
    # Initialization
    parallel_init: bool = False
    init_timeout_seconds: int = 60

    # Health checks
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30

    # Error handling
    fail_fast: bool = False
    retry_failed_services: bool = True
    max_retries: int = 3

    # Logging
    log_level: str = "INFO"


class DependencyInjector:
    """
    Dependency Injector - 依賴注入器
    
    Manages service dependencies and injection
    """

    def __init__(self):
        """Initialize dependency injector"""
        self._bindings: dict[str, type] = {}
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}
        self.logger = logging.getLogger("DependencyInjector")

    def bind(self, interface: str, implementation: type) -> None:
        """Bind an interface to an implementation"""
        self._bindings[interface] = implementation
        self.logger.debug(f"Bound {interface} to {implementation.__name__}")

    def bind_instance(self, interface: str, instance: Any) -> None:
        """Bind an interface to a specific instance"""
        self._instances[interface] = instance
        self.logger.debug(f"Bound {interface} to instance")

    def bind_factory(self, interface: str, factory: Callable) -> None:
        """Bind an interface to a factory function"""
        self._factories[interface] = factory
        self.logger.debug(f"Bound {interface} to factory")

    def resolve(self, interface: str) -> Any:
        """Resolve a dependency"""
        # Check for cached instance
        if interface in self._instances:
            return self._instances[interface]

        # Check for factory
        if interface in self._factories:
            instance = self._factories[interface]()
            self._instances[interface] = instance
            return instance

        # Check for binding
        if interface in self._bindings:
            implementation = self._bindings[interface]
            instance = implementation()
            self._instances[interface] = instance
            return instance

        raise ValueError(f"No binding found for {interface}")

    def has_binding(self, interface: str) -> bool:
        """Check if a binding exists"""
        return (
            interface in self._bindings or
            interface in self._instances or
            interface in self._factories
        )

    def clear(self) -> None:
        """Clear all bindings and instances"""
        self._bindings.clear()
        self._instances.clear()
        self._factories.clear()


class ServiceRegistry:
    """
    Service Registry - 服務註冊表
    
    Central registry for all services
    """

    def __init__(self):
        """Initialize service registry"""
        self._services: dict[str, ServiceInstance] = {}
        self._initialization_order: list[str] = []
        self.logger = logging.getLogger("ServiceRegistry")

    def register(self, definition: ServiceDefinition) -> None:
        """Register a service"""
        if definition.name in self._services:
            self.logger.warning(f"Service {definition.name} already registered")
            return

        self._services[definition.name] = ServiceInstance(definition=definition)
        self.logger.info(f"Service registered: {definition.name}")

    def get(self, name: str) -> Any | None:
        """Get a service instance"""
        service = self._services.get(name)
        if service and service.instance:
            return service.instance
        return None

    def get_definition(self, name: str) -> ServiceDefinition | None:
        """Get a service definition"""
        service = self._services.get(name)
        if service:
            return service.definition
        return None

    def get_all(self) -> dict[str, ServiceInstance]:
        """Get all services"""
        return self._services.copy()

    def get_dependencies(self, name: str) -> list[str]:
        """Get dependencies for a service"""
        service = self._services.get(name)
        if service:
            return service.definition.dependencies
        return []

    def set_instance(self, name: str, instance: Any) -> None:
        """Set a service instance"""
        if name in self._services:
            self._services[name].instance = instance
            self._services[name].lifecycle = ServiceLifecycle.READY
            self._services[name].initialized_at = datetime.now()

    def set_lifecycle(self, name: str, lifecycle: ServiceLifecycle) -> None:
        """Set a service lifecycle state"""
        if name in self._services:
            self._services[name].lifecycle = lifecycle

    def set_error(self, name: str, error: str) -> None:
        """Set error state for a service"""
        if name in self._services:
            self._services[name].lifecycle = ServiceLifecycle.ERROR
            self._services[name].error_message = error

    def compute_initialization_order(self) -> list[str]:
        """Compute initialization order based on dependencies"""
        visited = set()
        order = []

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)

            service = self._services.get(name)
            if service:
                for dep in service.definition.dependencies:
                    visit(dep)
                order.append(name)

        for name in self._services:
            visit(name)

        self._initialization_order = order
        return order


class SystemBootstrap:
    """
    System Bootstrap - 系統啟動器
    
    Initialize and configure all subsystems
    """

    def __init__(self, config: BootstrapConfig | None = None):
        """Initialize system bootstrap"""
        self.config = config or BootstrapConfig()
        self.registry = ServiceRegistry()
        self.injector = DependencyInjector()
        self.logger = logging.getLogger("SystemBootstrap")

        self._initialized = False
        self._startup_time: datetime | None = None
        self._shutdown_time: datetime | None = None

        # Health check callbacks
        self._health_checks: dict[str, Callable] = {}

    def register_service(self, definition: ServiceDefinition) -> None:
        """Register a service"""
        self.registry.register(definition)

    def register_health_check(self, name: str, check: Callable[[], bool]) -> None:
        """Register a health check"""
        self._health_checks[name] = check

    def initialize(self) -> bool:
        """
        Initialize all services
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            self.logger.warning("System already initialized")
            return True

        self.logger.info("Starting system bootstrap...")
        self._startup_time = datetime.now()

        try:
            # Compute initialization order
            order = self.registry.compute_initialization_order()
            self.logger.info(f"Initialization order: {order}")

            # Initialize services
            for service_name in order:
                if not self._initialize_service(service_name):
                    if self.config.fail_fast:
                        self.logger.error(f"Failed to initialize {service_name}, failing fast")
                        return False

            self._initialized = True
            self.logger.info("System bootstrap complete")
            return True

        except Exception as e:
            self.logger.error(f"Bootstrap failed: {e}")
            return False

    def _initialize_service(self, name: str) -> bool:
        """Initialize a single service"""
        definition = self.registry.get_definition(name)
        if not definition:
            return False

        self.logger.info(f"Initializing service: {name}")
        self.registry.set_lifecycle(name, ServiceLifecycle.INITIALIZING)

        try:
            # Resolve dependencies
            deps = {}
            for dep_name in definition.dependencies:
                dep_instance = self.registry.get(dep_name)
                if not dep_instance:
                    raise ValueError(f"Dependency {dep_name} not available")
                deps[dep_name] = dep_instance

            # Create instance
            if definition.config:
                instance = definition.service_class(**definition.config, **deps)
            else:
                instance = definition.service_class(**deps) if deps else definition.service_class()

            # Register instance
            self.registry.set_instance(name, instance)
            self.injector.bind_instance(name, instance)

            self.logger.info(f"Service initialized: {name}")
            return True

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Failed to initialize {name}: {error_msg}")
            self.registry.set_error(name, error_msg)
            return False

    def shutdown(self) -> bool:
        """
        Shutdown all services
        
        Returns:
            True if shutdown successful
        """
        if not self._initialized:
            self.logger.warning("System not initialized")
            return True

        self.logger.info("Shutting down system...")

        try:
            # Shutdown in reverse order
            order = self.registry.compute_initialization_order()
            for service_name in reversed(order):
                self._shutdown_service(service_name)

            self._initialized = False
            self._shutdown_time = datetime.now()
            self.logger.info("System shutdown complete")
            return True

        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")
            return False

    def _shutdown_service(self, name: str) -> bool:
        """Shutdown a single service"""
        service = self.registry.get(name)
        if not service:
            return True

        self.logger.info(f"Shutting down service: {name}")
        self.registry.set_lifecycle(name, ServiceLifecycle.STOPPING)

        try:
            # Call shutdown method if available
            if hasattr(service, 'shutdown'):
                service.shutdown()
            elif hasattr(service, 'stop'):
                service.stop()
            elif hasattr(service, 'close'):
                service.close()

            self.registry.set_lifecycle(name, ServiceLifecycle.STOPPED)
            return True

        except Exception as e:
            self.logger.error(f"Failed to shutdown {name}: {e}")
            return False

    def health_check(self) -> dict[str, Any]:
        """
        Perform health check on all services
        
        Returns:
            Health check results
        """
        results = {
            "healthy": True,
            "services": {},
            "checks": {},
            "timestamp": datetime.now().isoformat()
        }

        # Check service states
        for name, service in self.registry.get_all().items():
            is_healthy = service.lifecycle in [
                ServiceLifecycle.READY,
                ServiceLifecycle.RUNNING
            ]
            results["services"][name] = {
                "healthy": is_healthy,
                "lifecycle": service.lifecycle.value,
                "error": service.error_message
            }
            if not is_healthy:
                results["healthy"] = False

        # Run custom health checks
        for name, check in self._health_checks.items():
            try:
                is_healthy = check()
                results["checks"][name] = {"healthy": is_healthy}
                if not is_healthy:
                    results["healthy"] = False
            except Exception as e:
                results["checks"][name] = {"healthy": False, "error": str(e)}
                results["healthy"] = False

        return results

    def get_service(self, name: str) -> Any | None:
        """Get a service instance"""
        return self.registry.get(name)

    @property
    def is_initialized(self) -> bool:
        """Check if system is initialized"""
        return self._initialized

    @property
    def uptime_seconds(self) -> float | None:
        """Get system uptime in seconds"""
        if not self._startup_time:
            return None
        end = self._shutdown_time or datetime.now()
        return (end - self._startup_time).total_seconds()
