#!/usr/bin/env python3
"""
Tests for SuperAgent Utilities.

Tests cover:
- Prometheus metrics (Counter, Gauge, Histogram)
- Circuit breaker pattern
- Retry mechanism with backoff
- Rate limiting and backpressure
"""

import asyncio
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.metrics import Counter, Gauge, Histogram, MetricsCollector
from utils.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitOpenError,
    CircuitBreakerRegistry,
)
from utils.retry import (
    RetryConfig,
    retry_async,
    RetryExhaustedError,
    BackpressureController,
    RateLimiter,
)


class TestCounter:
    """Tests for Counter metric."""

    @pytest.fixture
    def counter(self):
        """Create a Counter instance."""
        return Counter(
            "test_requests_total",
            "Total test requests",
            labels=["method", "status"],
        )

    @pytest.mark.asyncio
    async def test_increment(self, counter):
        """Test counter increment."""
        await counter.inc(method="GET", status="200")
        await counter.inc(method="GET", status="200")
        await counter.inc(method="POST", status="201")

        metrics = counter.collect()
        assert len(metrics) == 2

        get_200 = [m for m in metrics if m["labels"]["method"] == "GET"][0]
        assert get_200["value"] == 2.0

    @pytest.mark.asyncio
    async def test_increment_by_value(self, counter):
        """Test counter increment by specific value."""
        await counter.inc(5.0, method="GET", status="200")

        metrics = counter.collect()
        assert metrics[0]["value"] == 5.0

    def test_prometheus_format(self, counter):
        """Test Prometheus exposition format."""
        asyncio.run(counter.inc(method="GET", status="200"))

        output = counter.prometheus_format()
        assert "# HELP test_requests_total" in output
        assert "# TYPE test_requests_total counter" in output
        assert 'method="GET"' in output


class TestGauge:
    """Tests for Gauge metric."""

    @pytest.fixture
    def gauge(self):
        """Create a Gauge instance."""
        return Gauge(
            "test_connections_active",
            "Active connections",
            labels=["server"],
        )

    @pytest.mark.asyncio
    async def test_set_value(self, gauge):
        """Test gauge set value."""
        await gauge.set(10, server="server-1")
        await gauge.set(20, server="server-2")

        metrics = gauge.collect()
        assert len(metrics) == 2

    @pytest.mark.asyncio
    async def test_increment_decrement(self, gauge):
        """Test gauge increment and decrement."""
        await gauge.set(10, server="main")
        await gauge.inc(5, server="main")
        await gauge.dec(3, server="main")

        metrics = gauge.collect()
        assert metrics[0]["value"] == 12  # 10 + 5 - 3

    def test_prometheus_format(self, gauge):
        """Test Prometheus exposition format."""
        asyncio.run(gauge.set(42, server="main"))

        output = gauge.prometheus_format()
        assert "# TYPE test_connections_active gauge" in output
        assert "42" in output


class TestHistogram:
    """Tests for Histogram metric."""

    @pytest.fixture
    def histogram(self):
        """Create a Histogram instance."""
        return Histogram(
            "test_request_duration_seconds",
            "Request duration",
            labels=["endpoint"],
            buckets=(0.1, 0.5, 1.0, 5.0),
        )

    @pytest.mark.asyncio
    async def test_observe(self, histogram):
        """Test histogram observation."""
        await histogram.observe(0.05, endpoint="/api")
        await histogram.observe(0.3, endpoint="/api")
        await histogram.observe(2.0, endpoint="/api")

        metrics = histogram.collect()
        assert len(metrics) == 1
        assert metrics[0]["count"] == 3
        assert metrics[0]["sum"] == pytest.approx(2.35)

    @pytest.mark.asyncio
    async def test_buckets(self, histogram):
        """Test histogram buckets."""
        await histogram.observe(0.05, endpoint="/api")  # <= 0.1
        await histogram.observe(0.3, endpoint="/api")   # <= 0.5
        await histogram.observe(2.0, endpoint="/api")   # <= 5.0

        metrics = histogram.collect()
        buckets = metrics[0]["buckets"]

        assert buckets[0.1] == 1
        assert buckets[0.5] == 1
        assert buckets[1.0] == 0
        assert buckets[5.0] == 1


class TestMetricsCollector:
    """Tests for MetricsCollector."""

    @pytest.fixture
    def collector(self):
        """Create a MetricsCollector instance."""
        return MetricsCollector()

    @pytest.mark.asyncio
    async def test_record_request(self, collector):
        """Test recording a request."""
        await collector.record_request("GET", "/api/health", "200", 0.05)

        all_metrics = collector.collect_all()
        request_metrics = [m for m in all_metrics if m["name"] == "superagent_requests_total"]
        assert len(request_metrics) > 0

    @pytest.mark.asyncio
    async def test_record_message(self, collector):
        """Test recording a message."""
        await collector.record_message("incident.create", "monitoring-agent", "success", 0.1)

        all_metrics = collector.collect_all()
        msg_metrics = [m for m in all_metrics if "messages" in m["name"]]
        assert len(msg_metrics) > 0

    def test_uptime(self, collector):
        """Test uptime tracking."""
        time.sleep(0.1)
        uptime = collector.get_uptime()
        assert uptime >= 0.1

    def test_prometheus_format_output(self, collector):
        """Test Prometheus format output."""
        output = collector.prometheus_format()
        assert "# HELP" in output
        assert "# TYPE" in output


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    @pytest.fixture
    def breaker(self):
        """Create a CircuitBreaker instance."""
        return CircuitBreaker(
            name="test-breaker",
            failure_threshold=3,
            recovery_timeout=1.0,
            half_open_requests=2,
        )

    def test_initial_state_is_closed(self, breaker):
        """Test that initial state is closed."""
        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed is True

    @pytest.mark.asyncio
    async def test_opens_after_failures(self, breaker):
        """Test that circuit opens after failure threshold."""
        for _ in range(3):
            await breaker.record_failure()

        assert breaker.state == CircuitState.OPEN
        assert breaker.is_open is True

    @pytest.mark.asyncio
    async def test_cannot_execute_when_open(self, breaker):
        """Test that requests fail fast when circuit is open."""
        for _ in range(3):
            await breaker.record_failure()

        can_exec = await breaker.can_execute()
        assert can_exec is False

    @pytest.mark.asyncio
    async def test_half_open_after_timeout(self, breaker):
        """Test transition to half-open after recovery timeout."""
        for _ in range(3):
            await breaker.record_failure()

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(1.1)

        # Check should trigger transition
        await breaker.can_execute()
        assert breaker.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_closes_after_half_open_successes(self, breaker):
        """Test transition to closed after half-open successes."""
        # Open the circuit
        for _ in range(3):
            await breaker.record_failure()

        # Wait for recovery and transition to half-open
        await asyncio.sleep(1.1)
        await breaker.can_execute()

        # Record successful requests
        await breaker.record_success()
        await breaker.record_success()

        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_execute_decorator(self, breaker):
        """Test circuit breaker as decorator."""
        call_count = 0

        @breaker
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await test_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_execute_raises_when_open(self, breaker):
        """Test that execute raises when circuit is open."""
        for _ in range(3):
            await breaker.record_failure()

        async def test_func():
            return "success"

        with pytest.raises(CircuitOpenError):
            await breaker.execute(test_func)

    def test_statistics(self, breaker):
        """Test circuit breaker statistics."""
        stats = breaker.get_statistics()
        assert stats["name"] == "test-breaker"
        assert stats["state"] == "closed"
        assert "failure_count" in stats


class TestCircuitBreakerRegistry:
    """Tests for CircuitBreakerRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a CircuitBreakerRegistry instance."""
        return CircuitBreakerRegistry()

    @pytest.mark.asyncio
    async def test_get_creates_breaker(self, registry):
        """Test that get creates a new breaker if not exists."""
        breaker = await registry.get("service-a")
        assert breaker is not None
        assert breaker.name == "service-a"

    @pytest.mark.asyncio
    async def test_get_returns_same_breaker(self, registry):
        """Test that get returns the same breaker instance."""
        breaker1 = await registry.get("service-a")
        breaker2 = await registry.get("service-a")
        assert breaker1 is breaker2

    @pytest.mark.asyncio
    async def test_reset_all(self, registry):
        """Test resetting all breakers."""
        breaker = await registry.get("service-a")
        for _ in range(5):
            await breaker.record_failure()

        await registry.reset_all()

        assert breaker.state == CircuitState.CLOSED


class TestRetryMechanism:
    """Tests for retry mechanism."""

    @pytest.mark.asyncio
    async def test_successful_first_attempt(self):
        """Test successful execution on first attempt."""
        async def successful_func():
            return "success"

        result = await retry_async(successful_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test retry on transient failure."""
        attempts = 0

        async def failing_then_success():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Transient error")
            return "success"

        config = RetryConfig(max_attempts=5, base_delay=0.01)
        result = await retry_async(failing_then_success, config=config)

        assert result == "success"
        assert attempts == 3

    @pytest.mark.asyncio
    async def test_exhausted_retries(self):
        """Test RetryExhaustedError when all retries fail."""
        async def always_fails():
            raise ValueError("Permanent error")

        config = RetryConfig(max_attempts=3, base_delay=0.01)

        with pytest.raises(RetryExhaustedError) as exc_info:
            await retry_async(always_fails, config=config)

        assert exc_info.value.attempts == 3

    @pytest.mark.asyncio
    async def test_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        attempts = 0

        async def raises_non_retryable():
            nonlocal attempts
            attempts += 1
            raise KeyError("Non-retryable")

        config = RetryConfig(
            max_attempts=5,
            non_retryable_exceptions=(KeyError,),
        )

        with pytest.raises(KeyError):
            await retry_async(raises_non_retryable, config=config)

        assert attempts == 1

    def test_retry_config_delay_calculation(self):
        """Test delay calculation with exponential backoff."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=60.0, jitter=False)

        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(10) == 60.0  # capped at max_delay


class TestBackpressureController:
    """Tests for BackpressureController."""

    @pytest.fixture
    def controller(self):
        """Create a BackpressureController instance."""
        return BackpressureController(rate=10.0, burst=5)

    @pytest.mark.asyncio
    async def test_acquire_within_burst(self, controller):
        """Test acquiring tokens within burst limit."""
        for _ in range(5):
            wait_time = await controller.acquire()
            assert wait_time == 0.0

    @pytest.mark.asyncio
    async def test_try_acquire(self, controller):
        """Test try_acquire without waiting."""
        for _ in range(5):
            assert await controller.try_acquire() is True

        # Burst exhausted
        assert await controller.try_acquire() is False

    def test_statistics(self, controller):
        """Test controller statistics."""
        stats = controller.get_statistics()
        assert stats["rate"] == 10.0
        assert stats["burst"] == 5


class TestRateLimiter:
    """Tests for RateLimiter."""

    @pytest.fixture
    def limiter(self):
        """Create a RateLimiter instance."""
        return RateLimiter(max_requests=5, window_seconds=1.0)

    @pytest.mark.asyncio
    async def test_allows_within_limit(self, limiter):
        """Test requests allowed within limit."""
        for _ in range(5):
            allowed = await limiter.is_allowed("user-1")
            assert allowed is True

    @pytest.mark.asyncio
    async def test_blocks_over_limit(self, limiter):
        """Test requests blocked over limit."""
        for _ in range(5):
            await limiter.is_allowed("user-1")

        # 6th request should be blocked
        allowed = await limiter.is_allowed("user-1")
        assert allowed is False

    @pytest.mark.asyncio
    async def test_per_key_limiting(self, limiter):
        """Test that limits are per-key."""
        for _ in range(5):
            await limiter.is_allowed("user-1")

        # Different key should have its own limit
        allowed = await limiter.is_allowed("user-2")
        assert allowed is True

    def test_get_remaining(self, limiter):
        """Test getting remaining requests."""
        remaining = limiter.get_remaining("user-1")
        assert remaining == 5
