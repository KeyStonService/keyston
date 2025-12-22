#!/usr/bin/env python3
"""
Circuit Breaker Pattern for SuperAgent

Implements circuit breaker for fault tolerance:
- Closed: Normal operation
- Open: Requests fail fast
- Half-Open: Testing recovery
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar
from functools import wraps


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


T = TypeVar("T")


class CircuitBreaker:
    """
    Circuit breaker implementation.

    Provides:
    - Automatic failure detection
    - Fast fail when open
    - Automatic recovery testing
    - Per-target circuit isolation
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_requests: int = 3,
        name: str = "default",
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_successes = 0
        self._lock = asyncio.Lock()

        # Statistics
        self._total_requests = 0
        self._total_failures = 0
        self._total_successes = 0
        self._state_changes: list = []

    @property
    def state(self) -> CircuitState:
        """Get current state."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self._state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self._state == CircuitState.HALF_OPEN

    async def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        if new_state != self._state:
            old_state = self._state
            self._state = new_state
            self._state_changes.append({
                "from": old_state.value,
                "to": new_state.value,
                "timestamp": datetime.now().isoformat(),
            })

    async def _check_recovery(self) -> None:
        """Check if recovery timeout has passed."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                await self._transition_to(CircuitState.HALF_OPEN)
                self._half_open_successes = 0

    async def can_execute(self) -> bool:
        """Check if request can be executed."""
        async with self._lock:
            await self._check_recovery()

            if self._state == CircuitState.CLOSED:
                return True
            elif self._state == CircuitState.HALF_OPEN:
                return True
            else:  # OPEN
                return False

    async def record_success(self) -> None:
        """Record a successful request."""
        async with self._lock:
            self._total_requests += 1
            self._total_successes += 1

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.half_open_requests:
                    await self._transition_to(CircuitState.CLOSED)
                    self._failure_count = 0
            elif self._state == CircuitState.CLOSED:
                self._success_count += 1
                # Reset failure count on success
                if self._failure_count > 0:
                    self._failure_count = max(0, self._failure_count - 1)

    async def record_failure(self) -> None:
        """Record a failed request."""
        async with self._lock:
            self._total_requests += 1
            self._total_failures += 1
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                await self._transition_to(CircuitState.OPEN)
                self._half_open_successes = 0
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)

    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute a function through the circuit breaker."""
        if not await self.can_execute():
            raise CircuitOpenError(f"Circuit {self.name} is open")

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            await self.record_failure()
            raise

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap a function with circuit breaker."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.execute(func, *args, **kwargs)
        return wrapper

    async def reset(self) -> None:
        """Reset the circuit breaker."""
        async with self._lock:
            await self._transition_to(CircuitState.CLOSED)
            self._failure_count = 0
            self._success_count = 0
            self._half_open_successes = 0
            self._last_failure_time = None

    def get_statistics(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_requests": self._total_requests,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
            "failure_rate": self._total_failures / self._total_requests * 100 if self._total_requests > 0 else 0,
            "last_failure": datetime.fromtimestamp(self._last_failure_time).isoformat() if self._last_failure_time else None,
            "state_changes": self._state_changes[-10:],  # Last 10 changes
        }


class CircuitOpenError(Exception):
    """Exception raised when circuit is open."""
    pass


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(
        self,
        default_failure_threshold: int = 5,
        default_recovery_timeout: float = 60.0,
        default_half_open_requests: int = 3,
    ):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._default_failure_threshold = default_failure_threshold
        self._default_recovery_timeout = default_recovery_timeout
        self._default_half_open_requests = default_half_open_requests
        self._lock = asyncio.Lock()

    async def get(self, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=self._default_failure_threshold,
                    recovery_timeout=self._default_recovery_timeout,
                    half_open_requests=self._default_half_open_requests,
                )
            return self._breakers[name]

    async def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {name: cb.get_statistics() for name, cb in self._breakers.items()}

    async def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for cb in self._breakers.values():
            await cb.reset()

    def __len__(self) -> int:
        """Return number of circuit breakers."""
        return len(self._breakers)
