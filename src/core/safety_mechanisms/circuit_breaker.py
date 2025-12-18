"""
Circuit Breaker System (斷路器系統)

When anomalies are detected, automatically cut off operations to prevent disaster spread.

Reference: Circuit breakers trigger automatically when AI executes unauthorized operations [2]
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import time


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation - allowing requests
    OPEN = "open"          # Tripped - blocking all requests
    HALF_OPEN = "half_open"  # Testing - allowing limited requests


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    name: str = "default"
    failure_threshold: int = 5          # Number of failures before opening
    success_threshold: int = 2          # Successes needed to close from half-open
    timeout: float = 60.0               # Seconds before trying half-open
    monitoring_period: float = 10.0     # Window for counting failures
    slow_call_threshold: float = 5.0    # Seconds to consider a call "slow"
    slow_call_rate_threshold: float = 0.5  # Rate of slow calls to trigger
    excluded_exceptions: List[type] = field(default_factory=list)


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    slow_calls: int = 0
    rejected_calls: int = 0
    state_changes: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_state_change: Optional[datetime] = None


T = TypeVar('T')


class CircuitBreaker(Generic[T]):
    """
    Circuit Breaker System
    
    Automatically cuts off operations when anomalies are detected,
    preventing disaster spread.
    
    States:
    - CLOSED: Normal operation, requests flow through
    - OPEN: Tripped, all requests are blocked
    - HALF_OPEN: Testing recovery, limited requests allowed
    
    Example:
        breaker = CircuitBreaker(CircuitBreakerConfig(name="database"))
        result = await breaker.execute(lambda: db.query("SELECT * FROM users"))
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._last_state_change_time = time.time()
        self._metrics = CircuitBreakerMetrics()
        self._listeners: List[Callable[[CircuitBreakerState, CircuitBreakerState], None]] = []
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitBreakerState:
        """Get current state"""
        return self._state
    
    @property
    def metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics"""
        return self._metrics
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)"""
        return self._state == CircuitBreakerState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking)"""
        return self._state == CircuitBreakerState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing)"""
        return self._state == CircuitBreakerState.HALF_OPEN
    
    def add_state_change_listener(
        self, 
        listener: Callable[[CircuitBreakerState, CircuitBreakerState], None]
    ) -> None:
        """Add listener for state changes"""
        self._listeners.append(listener)
    
    def _notify_state_change(
        self, 
        old_state: CircuitBreakerState, 
        new_state: CircuitBreakerState
    ) -> None:
        """Notify listeners of state change"""
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception:
                pass  # Don't let listener errors affect circuit breaker
    
    def _transition_to(self, new_state: CircuitBreakerState) -> None:
        """Transition to a new state"""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._last_state_change_time = time.time()
            self._metrics.state_changes += 1
            self._metrics.last_state_change = datetime.now()
            
            # Reset counters on state change
            if new_state == CircuitBreakerState.HALF_OPEN:
                self._success_count = 0
            elif new_state == CircuitBreakerState.CLOSED:
                self._failure_count = 0
            
            self._notify_state_change(old_state, new_state)
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should try to reset from OPEN to HALF_OPEN"""
        if self._state != CircuitBreakerState.OPEN:
            return False
        
        time_since_open = time.time() - self._last_state_change_time
        return time_since_open >= self.config.timeout
    
    def _record_success(self) -> None:
        """Record a successful call"""
        self._metrics.successful_calls += 1
        self._metrics.last_success_time = datetime.now()
        
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._transition_to(CircuitBreakerState.CLOSED)
    
    def _record_failure(self, exception: Exception) -> None:
        """Record a failed call"""
        # Check if exception is excluded
        if any(isinstance(exception, exc) for exc in self.config.excluded_exceptions):
            return
        
        self._metrics.failed_calls += 1
        self._metrics.last_failure_time = datetime.now()
        self._last_failure_time = time.time()
        
        if self._state == CircuitBreakerState.HALF_OPEN:
            # Any failure in half-open goes back to open
            self._transition_to(CircuitBreakerState.OPEN)
        elif self._state == CircuitBreakerState.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitBreakerState.OPEN)
    
    def _record_slow_call(self, duration: float) -> None:
        """Record a slow call"""
        if duration >= self.config.slow_call_threshold:
            self._metrics.slow_calls += 1
    
    async def execute(
        self, 
        operation: Callable[[], T],
        fallback: Optional[Callable[[], T]] = None
    ) -> T:
        """
        Execute operation with circuit breaker protection
        
        Args:
            operation: The operation to execute
            fallback: Optional fallback function if circuit is open
            
        Returns:
            Result of the operation or fallback
            
        Raises:
            CircuitBreakerOpenError: If circuit is open and no fallback provided
        """
        async with self._lock:
            self._metrics.total_calls += 1
            
            # Check if we should try to reset
            if self._should_attempt_reset():
                self._transition_to(CircuitBreakerState.HALF_OPEN)
            
            # If open, reject or use fallback
            if self._state == CircuitBreakerState.OPEN:
                self._metrics.rejected_calls += 1
                if fallback:
                    return fallback()
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.config.name}' is OPEN"
                )
            
            # Execute the operation
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = operation()
                
                duration = time.time() - start_time
                self._record_slow_call(duration)
                self._record_success()
                return result
                
            except Exception as e:
                self._record_failure(e)
                if fallback:
                    return fallback()
                raise
    
    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state"""
        self._transition_to(CircuitBreakerState.CLOSED)
        self._failure_count = 0
        self._success_count = 0
    
    def trip(self) -> None:
        """Manually trip the circuit breaker to OPEN state"""
        self._transition_to(CircuitBreakerState.OPEN)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.config.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "metrics": {
                "total_calls": self._metrics.total_calls,
                "successful_calls": self._metrics.successful_calls,
                "failed_calls": self._metrics.failed_calls,
                "slow_calls": self._metrics.slow_calls,
                "rejected_calls": self._metrics.rejected_calls,
                "state_changes": self._metrics.state_changes,
            }
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and operation is rejected"""
    pass


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers
    
    Example:
        registry = CircuitBreakerRegistry()
        registry.register("database", CircuitBreakerConfig(failure_threshold=3))
        await registry.execute("database", lambda: db.query(...))
    """
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def register(
        self, 
        name: str, 
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Register a new circuit breaker"""
        if config is None:
            config = CircuitBreakerConfig(name=name)
        else:
            config.name = name
        
        breaker = CircuitBreaker(config)
        self._breakers[name] = breaker
        return breaker
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name"""
        return self._breakers.get(name)
    
    def get_or_create(
        self, 
        name: str, 
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker"""
        if name not in self._breakers:
            return self.register(name, config)
        return self._breakers[name]
    
    async def execute(
        self, 
        name: str, 
        operation: Callable[[], T],
        fallback: Optional[Callable[[], T]] = None
    ) -> T:
        """Execute operation through named circuit breaker"""
        breaker = self.get_or_create(name)
        return await breaker.execute(operation, fallback)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all circuit breakers"""
        return {name: breaker.get_stats() for name, breaker in self._breakers.items()}
    
    def reset_all(self) -> None:
        """Reset all circuit breakers"""
        for breaker in self._breakers.values():
            breaker.reset()
    
    def trip_all(self) -> None:
        """Trip all circuit breakers (emergency stop)"""
        for breaker in self._breakers.values():
            breaker.trip()
