#!/usr/bin/env python3
"""
Retry Mechanism for SuperAgent

Provides configurable retry with:
- Exponential backoff
- Jitter
- Configurable exceptions
- Backpressure control
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar


T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    non_retryable_exceptions: Tuple[Type[Exception], ...] = ()

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt."""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            jitter_range = delay * self.jitter_factor
            delay = delay + random.uniform(-jitter_range, jitter_range)

        return max(0, delay)


@dataclass
class RetryStatistics:
    """Statistics for retry operations."""

    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    retries_needed: int = 0
    total_delay: float = 0.0
    last_error: Optional[str] = None
    errors_by_type: dict = field(default_factory=dict)


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, message: str, last_exception: Exception, attempts: int):
        super().__init__(message)
        self.last_exception = last_exception
        self.attempts = attempts


async def retry_async(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
    **kwargs,
) -> T:
    """
    Execute an async function with retry.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        config: Retry configuration
        on_retry: Callback called before each retry (attempt, exception, delay)
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Raises:
        RetryExhaustedError: When all retries are exhausted
    """
    if config is None:
        config = RetryConfig()

    last_exception: Optional[Exception] = None

    for attempt in range(config.max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return result

        except config.non_retryable_exceptions as e:
            # Don't retry these
            raise

        except config.retryable_exceptions as e:
            last_exception = e

            if attempt < config.max_attempts - 1:
                delay = config.calculate_delay(attempt)

                if on_retry:
                    on_retry(attempt + 1, e, delay)

                await asyncio.sleep(delay)
            else:
                break

    raise RetryExhaustedError(
        f"Retry exhausted after {config.max_attempts} attempts",
        last_exception,
        config.max_attempts,
    )


def retry(config: Optional[RetryConfig] = None):
    """Decorator for retrying async functions."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(func, *args, config=config, **kwargs)
        return wrapper

    return decorator


class BackpressureController:
    """
    Backpressure controller for rate limiting.

    Implements token bucket algorithm with:
    - Configurable rate
    - Burst capacity
    - Async wait for tokens
    """

    def __init__(
        self,
        rate: float = 10.0,  # tokens per second
        burst: int = 20,      # maximum burst
    ):
        self.rate = rate
        self.burst = burst
        self._tokens = float(burst)
        self._last_update = time.time()
        self._lock = asyncio.Lock()

        # Statistics
        self._total_requests = 0
        self._total_waits = 0
        self._total_wait_time = 0.0

    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, waiting if necessary.

        Returns the time waited.
        """
        async with self._lock:
            self._refill()
            self._total_requests += 1

            if self._tokens >= tokens:
                self._tokens -= tokens
                return 0.0

            # Calculate wait time
            needed = tokens - self._tokens
            wait_time = needed / self.rate

            self._total_waits += 1
            self._total_wait_time += wait_time

        # Wait outside lock
        await asyncio.sleep(wait_time)

        async with self._lock:
            self._refill()
            self._tokens -= tokens

        return wait_time

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_update
        self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
        self._last_update = now

    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens without waiting."""
        async with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                self._total_requests += 1
                return True
            return False

    def get_statistics(self) -> dict:
        """Get controller statistics."""
        return {
            "rate": self.rate,
            "burst": self.burst,
            "current_tokens": self._tokens,
            "total_requests": self._total_requests,
            "total_waits": self._total_waits,
            "total_wait_time": self._total_wait_time,
            "wait_rate": self._total_waits / self._total_requests * 100 if self._total_requests > 0 else 0,
        }


class RateLimiter:
    """
    Rate limiter with sliding window.

    Provides:
    - Per-key rate limiting
    - Sliding window algorithm
    - Async support
    """

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: float = 60.0,
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict = {}  # key -> list of timestamps
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str = "default") -> bool:
        """Check if request is allowed."""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Clean old requests
            if key in self._requests:
                self._requests[key] = [
                    ts for ts in self._requests[key] if ts > window_start
                ]
            else:
                self._requests[key] = []

            # Check limit
            if len(self._requests[key]) < self.max_requests:
                self._requests[key].append(now)
                return True

            return False

    async def wait_if_needed(self, key: str = "default") -> float:
        """Wait if rate limit exceeded, return wait time."""
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            if key in self._requests:
                self._requests[key] = [
                    ts for ts in self._requests[key] if ts > window_start
                ]
            else:
                self._requests[key] = []

            if len(self._requests[key]) < self.max_requests:
                self._requests[key].append(now)
                return 0.0

            # Calculate wait time until oldest request expires
            oldest = min(self._requests[key])
            wait_time = oldest + self.window_seconds - now

        if wait_time > 0:
            await asyncio.sleep(wait_time)
            async with self._lock:
                self._requests[key].append(time.time())

        return max(0, wait_time)

    def get_remaining(self, key: str = "default") -> int:
        """Get remaining requests in current window."""
        now = time.time()
        window_start = now - self.window_seconds

        if key not in self._requests:
            return self.max_requests

        active = [ts for ts in self._requests[key] if ts > window_start]
        return max(0, self.max_requests - len(active))
