"""
Emergency Stop System (緊急停止系統)

Manual or automatic emergency stop for preventing disaster.

Reference: Can be a manual emergency stop or an automatic circuit breaker
when certain conditions are met (such as detecting AI executing unauthorized operations) [2]
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


class StopReason(Enum):
    """Reasons for emergency stop"""
    MANUAL = "manual"                    # Manual trigger
    SECURITY_BREACH = "security_breach"  # Security issue detected
    RESOURCE_EXHAUSTION = "resource"     # Resource limits exceeded
    CASCADING_FAILURE = "cascade"        # Cascading failure detected
    UNAUTHORIZED_ACTION = "unauthorized" # Unauthorized action attempted
    DATA_CORRUPTION = "data_corruption"  # Data integrity issue
    ANOMALY_DETECTED = "anomaly"         # Anomaly threshold exceeded
    EXTERNAL_SIGNAL = "external"         # External stop signal


class StopScope(Enum):
    """Scope of emergency stop"""
    COMPONENT = "component"    # Single component
    SUBSYSTEM = "subsystem"    # Subsystem
    SERVICE = "service"        # Entire service
    SYSTEM = "system"          # Full system
    GLOBAL = "global"          # Global (all systems)


@dataclass
class EmergencyStopResult:
    """Result of emergency stop execution"""
    success: bool
    timestamp: datetime
    reason: StopReason
    scope: StopScope
    components_stopped: List[str]
    errors: List[str] = field(default_factory=list)
    initiated_by: str = "system"
    duration_ms: float = 0.0


@dataclass 
class StopCondition:
    """Condition that triggers automatic emergency stop"""
    name: str
    description: str
    check: Callable[[], bool]
    reason: StopReason
    scope: StopScope
    enabled: bool = True


class EmergencyStop:
    """
    Emergency Stop System
    
    Provides both manual and automatic emergency stop capabilities
    to prevent disasters.
    
    Features:
    - Manual emergency stop
    - Automatic stop based on conditions
    - Scoped stop (component/subsystem/system)
    - Pre-stop and post-stop hooks
    - Recovery procedures
    
    Example:
        stop = EmergencyStop()
        stop.register_component("database", db_stop_handler)
        await stop.trigger(StopReason.SECURITY_BREACH, StopScope.SYSTEM)
    """
    
    def __init__(self):
        self._is_stopped = False
        self._stop_scope: Optional[StopScope] = None
        self._stop_reason: Optional[StopReason] = None
        self._stop_time: Optional[datetime] = None
        
        self._components: Dict[str, ComponentStopHandler] = {}
        self._stopped_components: Set[str] = set()
        
        self._conditions: List[StopCondition] = []
        self._pre_stop_hooks: List[Callable[[], None]] = []
        self._post_stop_hooks: List[Callable[[], None]] = []
        self._recovery_hooks: List[Callable[[], None]] = []
        
        self._history: List[EmergencyStopResult] = []
        self._monitoring_task: Optional[asyncio.Task] = None
    
    @property
    def is_stopped(self) -> bool:
        """Check if system is in emergency stop state"""
        return self._is_stopped
    
    @property
    def stop_reason(self) -> Optional[StopReason]:
        """Get reason for current stop"""
        return self._stop_reason
    
    @property
    def stop_scope(self) -> Optional[StopScope]:
        """Get scope of current stop"""
        return self._stop_scope
    
    def register_component(
        self,
        name: str,
        stop_handler: Callable[[], None],
        recovery_handler: Optional[Callable[[], None]] = None,
        subsystem: Optional[str] = None
    ) -> None:
        """
        Register a component for emergency stop
        
        Args:
            name: Component name
            stop_handler: Function to stop the component
            recovery_handler: Optional function to recover the component
            subsystem: Optional subsystem this component belongs to
        """
        self._components[name] = ComponentStopHandler(
            name=name,
            stop=stop_handler,
            recover=recovery_handler,
            subsystem=subsystem
        )
    
    def add_stop_condition(self, condition: StopCondition) -> None:
        """Add automatic stop condition"""
        self._conditions.append(condition)
    
    def add_pre_stop_hook(self, hook: Callable[[], None]) -> None:
        """Add hook to run before emergency stop"""
        self._pre_stop_hooks.append(hook)
    
    def add_post_stop_hook(self, hook: Callable[[], None]) -> None:
        """Add hook to run after emergency stop"""
        self._post_stop_hooks.append(hook)
    
    def add_recovery_hook(self, hook: Callable[[], None]) -> None:
        """Add hook to run during recovery"""
        self._recovery_hooks.append(hook)
    
    async def trigger(
        self,
        reason: StopReason,
        scope: StopScope,
        initiated_by: str = "system",
        components: Optional[List[str]] = None
    ) -> EmergencyStopResult:
        """
        Trigger emergency stop
        
        Args:
            reason: Reason for stop
            scope: Scope of stop
            initiated_by: Who/what initiated the stop
            components: Optional specific components (for COMPONENT scope)
            
        Returns:
            EmergencyStopResult
        """
        import time
        start_time = time.time()
        
        errors: List[str] = []
        stopped: List[str] = []
        
        # Run pre-stop hooks
        for hook in self._pre_stop_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                errors.append(f"Pre-stop hook error: {str(e)}")
        
        # Determine components to stop based on scope
        components_to_stop = self._get_components_for_scope(scope, components)
        
        # Stop components
        for name in components_to_stop:
            if name in self._components:
                handler = self._components[name]
                try:
                    if asyncio.iscoroutinefunction(handler.stop):
                        await handler.stop()
                    else:
                        handler.stop()
                    stopped.append(name)
                    self._stopped_components.add(name)
                except Exception as e:
                    errors.append(f"Failed to stop {name}: {str(e)}")
        
        # Update state
        self._is_stopped = True
        self._stop_scope = scope
        self._stop_reason = reason
        self._stop_time = datetime.now()
        
        # Run post-stop hooks
        for hook in self._post_stop_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as e:
                errors.append(f"Post-stop hook error: {str(e)}")
        
        duration_ms = (time.time() - start_time) * 1000
        
        result = EmergencyStopResult(
            success=len(errors) == 0,
            timestamp=datetime.now(),
            reason=reason,
            scope=scope,
            components_stopped=stopped,
            errors=errors,
            initiated_by=initiated_by,
            duration_ms=duration_ms
        )
        
        self._history.append(result)
        return result
    
    def _get_components_for_scope(
        self,
        scope: StopScope,
        specific_components: Optional[List[str]] = None
    ) -> List[str]:
        """Get list of components to stop based on scope"""
        if scope == StopScope.COMPONENT and specific_components:
            return [c for c in specific_components if c in self._components]
        
        if scope == StopScope.SUBSYSTEM and specific_components:
            # specific_components contains subsystem names
            return [
                name for name, handler in self._components.items()
                if handler.subsystem in specific_components
            ]
        
        # For SERVICE, SYSTEM, GLOBAL - stop all components
        return list(self._components.keys())
    
    async def recover(
        self,
        components: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Attempt to recover stopped components
        
        Args:
            components: Optional specific components to recover
            
        Returns:
            Dict mapping component names to recovery success
        """
        results: Dict[str, bool] = {}
        
        # Run recovery hooks
        for hook in self._recovery_hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception:
                pass
        
        # Recover components
        components_to_recover = components or list(self._stopped_components)
        
        for name in components_to_recover:
            if name in self._components:
                handler = self._components[name]
                if handler.recover:
                    try:
                        if asyncio.iscoroutinefunction(handler.recover):
                            await handler.recover()
                        else:
                            handler.recover()
                        self._stopped_components.discard(name)
                        results[name] = True
                    except Exception:
                        results[name] = False
                else:
                    results[name] = False
        
        # Update state if all recovered
        if not self._stopped_components:
            self._is_stopped = False
            self._stop_scope = None
            self._stop_reason = None
        
        return results
    
    async def start_monitoring(self, interval: float = 1.0) -> None:
        """
        Start monitoring stop conditions
        
        Args:
            interval: Check interval in seconds
        """
        async def monitor():
            while True:
                if not self._is_stopped:
                    for condition in self._conditions:
                        if condition.enabled:
                            try:
                                should_stop = condition.check()
                                if asyncio.iscoroutine(should_stop):
                                    should_stop = await should_stop
                                
                                if should_stop:
                                    await self.trigger(
                                        reason=condition.reason,
                                        scope=condition.scope,
                                        initiated_by=f"condition:{condition.name}"
                                    )
                                    break
                            except Exception:
                                pass
                
                await asyncio.sleep(interval)
        
        self._monitoring_task = asyncio.create_task(monitor())
    
    async def stop_monitoring(self) -> None:
        """Stop condition monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current emergency stop status"""
        return {
            "is_stopped": self._is_stopped,
            "stop_reason": self._stop_reason.value if self._stop_reason else None,
            "stop_scope": self._stop_scope.value if self._stop_scope else None,
            "stop_time": self._stop_time.isoformat() if self._stop_time else None,
            "stopped_components": list(self._stopped_components),
            "total_components": len(self._components),
            "active_conditions": len([c for c in self._conditions if c.enabled])
        }
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get emergency stop history"""
        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "reason": r.reason.value,
                "scope": r.scope.value,
                "success": r.success,
                "components_stopped": len(r.components_stopped),
                "initiated_by": r.initiated_by
            }
            for r in self._history[-limit:]
        ]


@dataclass
class ComponentStopHandler:
    """Handler for component stop/recovery"""
    name: str
    stop: Callable[[], None]
    recover: Optional[Callable[[], None]] = None
    subsystem: Optional[str] = None
