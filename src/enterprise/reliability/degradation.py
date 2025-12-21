"""
Degradation Strategy

Defines behavior when gate times out or dependencies fail:
- Fail-closed: Block merge on any failure (strictest)
- Fail-neutral: Mark as neutral + alert (softer)
- Fail-open: Allow merge + alert (least strict)

Also includes:
- Circuit breaker for external dependencies
- Health checks for services
- Graceful degradation patterns
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, Callable, Awaitable, Protocol
from uuid import UUID
from enum import Enum
import asyncio
from datetime import datetime
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
from uuid import UUID

logger = logging.getLogger(__name__)


class DegradationMode(Enum):
    """Gate degradation modes"""
    FAIL_CLOSED = "fail_closed"     # Block on any failure (strictest)
    FAIL_NEUTRAL = "fail_neutral"   # Mark neutral + alert
    FAIL_OPEN = "fail_open"         # Allow + alert (least strict)


class ServiceHealth(Enum):
    """Service health states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing fast
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class FallbackResult:
    """Result of a fallback operation"""
    success: bool
    used_fallback: bool = False
    fallback_reason: str | None = None
    original_error: str | None = None
    result: Any = None
    duration_ms: float = 0.0


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service_name: str
    status: ServiceHealth
    latency_ms: float = 0.0
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.utcnow)


class AlertPublisher(Protocol):
    """Interface for publishing degradation alerts"""

    async def publish_alert(
        self,
        severity: str,
        title: str,
        message: str,
        details: dict[str, Any],
    ) -> None:
        ...


@dataclass
class CircuitBreaker:
    """
    Circuit Breaker Pattern

    Prevents cascading failures by failing fast when a service is unhealthy.
    """
    name: str
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 3          # Successes to close
    timeout_seconds: float = 30.0       # Timeout for calls
    reset_timeout_seconds: float = 60.0 # Time before half-open

    # State
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: datetime | None = None
    last_state_change: datetime = field(default_factory=datetime.utcnow)

    async def call(
        self,
        operation: Callable[[], Awaitable[Any]],
        fallback: Callable[[], Awaitable[Any]] | None = None,
    ) -> FallbackResult:
        """
        Execute operation through circuit breaker

        Args:
            operation: Async operation to execute
            fallback: Optional fallback if circuit is open

        Returns:
            FallbackResult with operation result or fallback
        """
        start = time.monotonic()

        # Check if should transition from open to half-open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
            elif fallback:
                # Execute fallback
                try:
                    result = await fallback()
                    return FallbackResult(
                        success=True,
                        used_fallback=True,
                        fallback_reason="circuit_open",
                        result=result,
                        duration_ms=(time.monotonic() - start) * 1000,
                    )
                except Exception as e:
                    return FallbackResult(
                        success=False,
                        used_fallback=True,
                        fallback_reason="circuit_open",
                        original_error=str(e),
                        duration_ms=(time.monotonic() - start) * 1000,
                    )
            else:
                return FallbackResult(
                    success=False,
                    used_fallback=False,
                    fallback_reason="circuit_open_no_fallback",
                    duration_ms=(time.monotonic() - start) * 1000,
                )

        # Execute operation
        try:
            result = await asyncio.wait_for(
                operation(),
                timeout=self.timeout_seconds,
            )

            self._record_success()

            return FallbackResult(
                success=True,
                result=result,
                duration_ms=(time.monotonic() - start) * 1000,
            )

        except asyncio.TimeoutError:
            self._record_failure()
            error = f"Operation timed out after {self.timeout_seconds}s"

            if fallback and self.state == CircuitState.OPEN:
                try:
                    result = await fallback()
                    return FallbackResult(
                        success=True,
                        used_fallback=True,
                        fallback_reason="timeout",
                        original_error=error,
                        result=result,
                        duration_ms=(time.monotonic() - start) * 1000,
                    )
                except Exception:
                    pass

            return FallbackResult(
                success=False,
                original_error=error,
                duration_ms=(time.monotonic() - start) * 1000,
            )

        except Exception as e:
            self._record_failure()

            if fallback and self.state == CircuitState.OPEN:
                try:
                    result = await fallback()
                    return FallbackResult(
                        success=True,
                        used_fallback=True,
                        fallback_reason="exception",
                        original_error=str(e),
                        result=result,
                        duration_ms=(time.monotonic() - start) * 1000,
                    )
                except Exception:
                    pass

            return FallbackResult(
                success=False,
                original_error=str(e),
                duration_ms=(time.monotonic() - start) * 1000,
            )

    def _record_success(self) -> None:
        """Record a successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)
        else:
            self.failure_count = 0

    def _record_failure(self) -> None:
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        self.success_count = 0

        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self._transition_to(CircuitState.OPEN)

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt reset from open state"""
        if not self.last_failure_time:
            return True

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.reset_timeout_seconds

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state"""
        old_state = self.state
        self.state = new_state
        self.last_state_change = datetime.utcnow()

        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0

        logger.info(
            f"Circuit breaker '{self.name}' transitioned: "
            f"{old_state.value} → {new_state.value}"
        )


@dataclass
class HealthCheck:
    """
    Service Health Check

    Monitors the health of dependent services.
    """
    name: str
    check_fn: Callable[[], Awaitable[bool]]
    interval_seconds: float = 30.0
    timeout_seconds: float = 10.0
    failure_threshold: int = 3

    # State
    status: ServiceHealth = ServiceHealth.UNKNOWN
    consecutive_failures: int = 0
    last_check: datetime | None = None
    last_success: datetime | None = None

    async def check(self) -> HealthCheckResult:
        """Run health check"""
        start = time.monotonic()

        try:
            result = await asyncio.wait_for(
                self.check_fn(),
                timeout=self.timeout_seconds,
            )

            latency = (time.monotonic() - start) * 1000

            if result:
                self.consecutive_failures = 0
                self.status = ServiceHealth.HEALTHY
                self.last_success = datetime.utcnow()

                return HealthCheckResult(
                    service_name=self.name,
                    status=ServiceHealth.HEALTHY,
                    latency_ms=latency,
                )
            else:
                self._record_failure()

                return HealthCheckResult(
                    service_name=self.name,
                    status=self.status,
                    latency_ms=latency,
                    message="Check returned false",
                )

        except asyncio.TimeoutError:
            self._record_failure()

            return HealthCheckResult(
                service_name=self.name,
                status=self.status,
                message=f"Timeout after {self.timeout_seconds}s",
            )

        except Exception as e:
            self._record_failure()

            return HealthCheckResult(
                service_name=self.name,
                status=self.status,
                message=str(e),
            )

        finally:
            self.last_check = datetime.utcnow()

    def _record_failure(self) -> None:
        """Record a check failure"""
        self.consecutive_failures += 1

        if self.consecutive_failures >= self.failure_threshold:
            self.status = ServiceHealth.UNHEALTHY
        else:
            self.status = ServiceHealth.DEGRADED


@dataclass
class DegradationStrategy:
    """
    Degradation Strategy Manager

    Manages graceful degradation for the gate system.
    """
    # Default mode
    default_mode: DegradationMode = DegradationMode.FAIL_NEUTRAL

    # Per-org overrides
    org_modes: dict[str, DegradationMode] = field(default_factory=dict)

    # Circuit breakers for dependencies
    circuit_breakers: dict[str, CircuitBreaker] = field(default_factory=dict)

    # Health checks
    health_checks: dict[str, HealthCheck] = field(default_factory=dict)

    # Alert publisher
    alert_publisher: AlertPublisher | None = None

    # Configuration
    gate_timeout_seconds: float = 300.0      # 5 minute gate timeout
    degradation_cooldown_seconds: float = 300.0  # Cooldown after degradation

    # State
    is_degraded: bool = False
    degraded_since: datetime | None = None
    degradation_reason: str | None = None

    # ------------------------------------------------------------------
    # Degradation Mode
    # ------------------------------------------------------------------

    def get_mode(self, org_id: UUID) -> DegradationMode:
        """Get degradation mode for an organization"""
        return self.org_modes.get(str(org_id), self.default_mode)

    def set_mode(self, org_id: UUID, mode: DegradationMode) -> None:
        """Set degradation mode for an organization"""
        self.org_modes[str(org_id)] = mode

    # ------------------------------------------------------------------
    # Gate Timeout Handling
    # ------------------------------------------------------------------

    async def handle_gate_timeout(
        self,
        org_id: UUID,
        run_id: UUID,
        elapsed_seconds: float,
    ) -> dict[str, Any]:
        """
        Handle gate timeout

        Returns action to take based on degradation mode.
        """
        mode = self.get_mode(org_id)

        result = {
            "action": "unknown",
            "mode": mode.value,
            "elapsed_seconds": elapsed_seconds,
            "alert_sent": False,
        }

        if mode == DegradationMode.FAIL_CLOSED:
            result["action"] = "block"
            result["conclusion"] = "failure"
            result["message"] = f"Gate timed out after {elapsed_seconds:.0f}s"

        elif mode == DegradationMode.FAIL_NEUTRAL:
            result["action"] = "neutral"
            result["conclusion"] = "neutral"
            result["message"] = (
                f"Gate timed out after {elapsed_seconds:.0f}s. "
                "Marked as neutral - manual review recommended."
            )

        elif mode == DegradationMode.FAIL_OPEN:
            result["action"] = "allow"
            result["conclusion"] = "neutral"
            result["message"] = (
                f"Gate timed out after {elapsed_seconds:.0f}s. "
                "Allowing merge - manual review required."
            )

        # Send alert
        if self.alert_publisher:
            await self.alert_publisher.publish_alert(
                severity="warning",
                title="Gate Timeout",
                message=result["message"],
                details={
                    "org_id": str(org_id),
                    "run_id": str(run_id),
                    "mode": mode.value,
                    "action": result["action"],
                },
            )
            result["alert_sent"] = True

        logger.warning(
            f"Gate timeout: org={org_id} run={run_id} "
            f"mode={mode.value} action={result['action']}"
        )

        return result

    async def handle_dependency_failure(
        self,
        org_id: UUID,
        run_id: UUID,
        dependency: str,
        error: str,
    ) -> dict[str, Any]:
        """
        Handle dependency failure (e.g., provider API down)

        Returns action based on degradation mode.
        """
        mode = self.get_mode(org_id)

        result = {
            "action": "unknown",
            "mode": mode.value,
            "dependency": dependency,
            "error": error,
            "alert_sent": False,
        }

        if mode == DegradationMode.FAIL_CLOSED:
            result["action"] = "block"
            result["conclusion"] = "failure"
            result["message"] = f"Dependency failure ({dependency}): {error}"

        elif mode == DegradationMode.FAIL_NEUTRAL:
            result["action"] = "neutral"
            result["conclusion"] = "neutral"
            result["message"] = (
                f"Dependency failure ({dependency}). "
                "Marked as neutral - retry later."
            )

        elif mode == DegradationMode.FAIL_OPEN:
            result["action"] = "allow"
            result["conclusion"] = "neutral"
            result["message"] = (
                f"Dependency failure ({dependency}). "
                "Allowing merge - verify manually."
            )

        # Enter degraded mode
        self._enter_degraded_mode(f"Dependency failure: {dependency}")

        if self.alert_publisher:
            await self.alert_publisher.publish_alert(
                severity="error",
                title=f"Dependency Failure: {dependency}",
                message=error,
                details={
                    "org_id": str(org_id),
                    "run_id": str(run_id),
                    "dependency": dependency,
                    "mode": mode.value,
                },
            )
            result["alert_sent"] = True

        return result

    # ------------------------------------------------------------------
    # Circuit Breakers
    # ------------------------------------------------------------------

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name=name)
        return self.circuit_breakers[name]

    async def call_with_circuit_breaker(
        self,
        name: str,
        operation: Callable[[], Awaitable[Any]],
        fallback: Callable[[], Awaitable[Any]] | None = None,
    ) -> FallbackResult:
        """Execute operation through circuit breaker"""
        cb = self.get_circuit_breaker(name)
        return await cb.call(operation, fallback)

    # ------------------------------------------------------------------
    # Health Checks
    # ------------------------------------------------------------------

    def register_health_check(
        self,
        name: str,
        check_fn: Callable[[], Awaitable[bool]],
        interval_seconds: float = 30.0,
    ) -> HealthCheck:
        """Register a health check"""
        hc = HealthCheck(
            name=name,
            check_fn=check_fn,
            interval_seconds=interval_seconds,
        )
        self.health_checks[name] = hc
        return hc

    async def run_health_checks(self) -> dict[str, HealthCheckResult]:
        """Run all registered health checks"""
        results = {}

        for name, hc in self.health_checks.items():
            results[name] = await hc.check()

        # Check for degradation
        unhealthy_count = sum(
            1 for r in results.values()
            if r.status == ServiceHealth.UNHEALTHY
        )

        if unhealthy_count > 0 and not self.is_degraded:
            self._enter_degraded_mode(
                f"{unhealthy_count} services unhealthy"
            )
        elif unhealthy_count == 0 and self.is_degraded:
            self._exit_degraded_mode()

        return results

    def get_overall_health(self) -> ServiceHealth:
        """Get overall system health"""
        if not self.health_checks:
            return ServiceHealth.UNKNOWN

        statuses = [hc.status for hc in self.health_checks.values()]

        if all(s == ServiceHealth.HEALTHY for s in statuses):
            return ServiceHealth.HEALTHY
        elif any(s == ServiceHealth.UNHEALTHY for s in statuses):
            return ServiceHealth.UNHEALTHY
        elif any(s == ServiceHealth.DEGRADED for s in statuses):
            return ServiceHealth.DEGRADED

        return ServiceHealth.UNKNOWN

    # ------------------------------------------------------------------
    # Degraded Mode
    # ------------------------------------------------------------------

    def _enter_degraded_mode(self, reason: str) -> None:
        """Enter degraded mode"""
        if self.is_degraded:
            return

        self.is_degraded = True
        self.degraded_since = datetime.utcnow()
        self.degradation_reason = reason

        logger.warning(f"Entering degraded mode: {reason}")

    def _exit_degraded_mode(self) -> None:
        """Exit degraded mode"""
        if not self.is_degraded:
            return

        duration = datetime.utcnow() - self.degraded_since
        logger.info(f"Exiting degraded mode after {duration}")

        self.is_degraded = False
        self.degraded_since = None
        self.degradation_reason = None

    def get_status(self) -> dict[str, Any]:
        """Get current degradation status"""
        return {
            "is_degraded": self.is_degraded,
            "degraded_since": self.degraded_since.isoformat() if self.degraded_since else None,
            "degradation_reason": self.degradation_reason,
            "overall_health": self.get_overall_health().value,
            "circuit_breakers": {
                name: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                }
                for name, cb in self.circuit_breakers.items()
            },
            "health_checks": {
                name: hc.status.value
                for name, hc in self.health_checks.items()
            },
        }
