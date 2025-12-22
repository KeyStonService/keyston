"""
Metrics Collector

Prometheus-compatible metrics for observability:
- Business metrics (runs, findings, etc.)
- System metrics (latency, errors, etc.)
- Resource metrics (queue depth, memory, etc.)

Essential for operating at scale and delivering SLA.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"       # Monotonically increasing
    GAUGE = "gauge"           # Can go up or down
    HISTOGRAM = "histogram"   # Distribution of values
    SUMMARY = "summary"       # Similar to histogram


@dataclass
class MetricLabels:
    """
    Metric labels for dimensionality

    Common labels used across metrics.
    """
    org_id: str | None = None
    repo: str | None = None
    run_type: str | None = None
    provider: str | None = None
    status: str | None = None
    error_type: str | None = None
    tool: str | None = None
    queue: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to label dictionary"""
        return {
            k: v for k, v in {
                "org_id": self.org_id,
                "repo": self.repo,
                "run_type": self.run_type,
                "provider": self.provider,
                "status": self.status,
                "error_type": self.error_type,
                "tool": self.tool,
                "queue": self.queue,
            }.items() if v is not None
        }


class MetricsBackend(Protocol):
    """Interface for metrics backend (e.g., Prometheus)"""

    def counter_inc(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        ...

    def gauge_set(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        ...

    def histogram_observe(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        ...


@dataclass
class Counter:
    """
    Counter metric

    Monotonically increasing counter.
    """
    name: str
    description: str = ""
    labels: list[str] = field(default_factory=list)
    _backend: MetricsBackend | None = None

    def inc(
        self,
        value: float = 1.0,
        labels: MetricLabels | None = None,
    ) -> None:
        """Increment the counter"""
        if self._backend:
            self._backend.counter_inc(
                self.name,
                value,
                labels.to_dict() if labels else None,
            )


@dataclass
class Gauge:
    """
    Gauge metric

    Value that can go up or down.
    """
    name: str
    description: str = ""
    labels: list[str] = field(default_factory=list)
    _backend: MetricsBackend | None = None

    def set(
        self,
        value: float,
        labels: MetricLabels | None = None,
    ) -> None:
        """Set the gauge value"""
        if self._backend:
            self._backend.gauge_set(
                self.name,
                value,
                labels.to_dict() if labels else None,
            )

    def inc(
        self,
        value: float = 1.0,
        labels: MetricLabels | None = None,
    ) -> None:
        """Increment the gauge"""
        # Note: Actual implementation would track current value
        pass

    def dec(
        self,
        value: float = 1.0,
        labels: MetricLabels | None = None,
    ) -> None:
        """Decrement the gauge"""
        pass


@dataclass
class Histogram:
    """
    Histogram metric

    Distribution of values with configurable buckets.
    """
    name: str
    description: str = ""
    labels: list[str] = field(default_factory=list)
    buckets: list[float] = field(default_factory=lambda: [
        0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0
    ])
    _backend: MetricsBackend | None = None

    def observe(
        self,
        value: float,
        labels: MetricLabels | None = None,
    ) -> None:
        """Observe a value"""
        if self._backend:
            self._backend.histogram_observe(
                self.name,
                value,
                labels.to_dict() if labels else None,
            )

    def time(self, labels: MetricLabels | None = None):
        """Context manager for timing operations"""
        return HistogramTimer(self, labels)


@dataclass
class HistogramTimer:
    """Context manager for timing with histogram"""
    histogram: Histogram
    labels: MetricLabels | None = None
    _start: float = 0.0

    def __enter__(self) -> "HistogramTimer":
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        duration = time.monotonic() - self._start
        self.histogram.observe(duration, self.labels)


@dataclass
class MetricsCollector:
    """
    Metrics Collector

    Central registry for all application metrics.
    """

    backend: MetricsBackend | None = None

    # Metric prefix
    prefix: str = "mno"

    # ------------------------------------------------------------------
    # Registered Metrics
    # ------------------------------------------------------------------

    # Analysis metrics
    runs_total: Counter = field(default=None)
    runs_duration_seconds: Histogram = field(default=None)
    runs_in_progress: Gauge = field(default=None)
    findings_total: Counter = field(default=None)

    # Webhook metrics
    webhooks_received_total: Counter = field(default=None)
    webhooks_processed_total: Counter = field(default=None)
    webhooks_failed_total: Counter = field(default=None)
    webhook_processing_seconds: Histogram = field(default=None)

    # Queue metrics
    queue_depth: Gauge = field(default=None)
    queue_latency_seconds: Histogram = field(default=None)
    jobs_processed_total: Counter = field(default=None)
    jobs_failed_total: Counter = field(default=None)

    # Provider API metrics
    provider_api_requests_total: Counter = field(default=None)
    provider_api_errors_total: Counter = field(default=None)
    provider_api_latency_seconds: Histogram = field(default=None)
    provider_rate_limit_remaining: Gauge = field(default=None)

    # Gate metrics
    gate_checks_total: Counter = field(default=None)
    gate_passed_total: Counter = field(default=None)
    gate_failed_total: Counter = field(default=None)
    gate_duration_seconds: Histogram = field(default=None)

    # Resource metrics
    concurrent_runs: Gauge = field(default=None)
    quota_usage_percent: Gauge = field(default=None)

    # Error metrics
    errors_total: Counter = field(default=None)

    def __post_init__(self):
        """Initialize all metrics"""
        self._init_metrics()

    def _init_metrics(self):
        """Initialize metric instances"""
        # Analysis metrics
        self.runs_total = Counter(
            name=f"{self.prefix}_runs_total",
            description="Total number of analysis runs",
            labels=["org_id", "repo", "run_type", "status"],
            _backend=self.backend,
        )

        self.runs_duration_seconds = Histogram(
            name=f"{self.prefix}_runs_duration_seconds",
            description="Duration of analysis runs in seconds",
            labels=["org_id", "run_type"],
            buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800],
            _backend=self.backend,
        )

        self.runs_in_progress = Gauge(
            name=f"{self.prefix}_runs_in_progress",
            description="Number of runs currently in progress",
            labels=["org_id", "run_type"],
            _backend=self.backend,
        )

        self.findings_total = Counter(
            name=f"{self.prefix}_findings_total",
            description="Total number of findings",
            labels=["org_id", "repo", "severity", "tool"],
            _backend=self.backend,
        )

        # Webhook metrics
        self.webhooks_received_total = Counter(
            name=f"{self.prefix}_webhooks_received_total",
            description="Total webhooks received",
            labels=["provider", "event_type"],
            _backend=self.backend,
        )

        self.webhooks_processed_total = Counter(
            name=f"{self.prefix}_webhooks_processed_total",
            description="Total webhooks successfully processed",
            labels=["provider", "event_type"],
            _backend=self.backend,
        )

        self.webhooks_failed_total = Counter(
            name=f"{self.prefix}_webhooks_failed_total",
            description="Total webhooks failed to process",
            labels=["provider", "event_type", "error_type"],
            _backend=self.backend,
        )

        self.webhook_processing_seconds = Histogram(
            name=f"{self.prefix}_webhook_processing_seconds",
            description="Webhook processing duration",
            labels=["provider", "event_type"],
            _backend=self.backend,
        )

        # Queue metrics
        self.queue_depth = Gauge(
            name=f"{self.prefix}_queue_depth",
            description="Current queue depth",
            labels=["queue"],
            _backend=self.backend,
        )

        self.queue_latency_seconds = Histogram(
            name=f"{self.prefix}_queue_latency_seconds",
            description="Time jobs spend in queue",
            labels=["queue"],
            buckets=[0.1, 0.5, 1, 5, 10, 30, 60, 300],
            _backend=self.backend,
        )

        self.jobs_processed_total = Counter(
            name=f"{self.prefix}_jobs_processed_total",
            description="Total jobs processed",
            labels=["queue", "job_type", "status"],
            _backend=self.backend,
        )

        self.jobs_failed_total = Counter(
            name=f"{self.prefix}_jobs_failed_total",
            description="Total jobs failed",
            labels=["queue", "job_type", "error_type"],
            _backend=self.backend,
        )

        # Provider API metrics
        self.provider_api_requests_total = Counter(
            name=f"{self.prefix}_provider_api_requests_total",
            description="Total API requests to providers",
            labels=["provider", "endpoint", "method"],
            _backend=self.backend,
        )

        self.provider_api_errors_total = Counter(
            name=f"{self.prefix}_provider_api_errors_total",
            description="Total API errors from providers",
            labels=["provider", "endpoint", "status_code"],
            _backend=self.backend,
        )

        self.provider_api_latency_seconds = Histogram(
            name=f"{self.prefix}_provider_api_latency_seconds",
            description="Provider API latency",
            labels=["provider", "endpoint"],
            _backend=self.backend,
        )

        self.provider_rate_limit_remaining = Gauge(
            name=f"{self.prefix}_provider_rate_limit_remaining",
            description="Remaining rate limit for provider API",
            labels=["provider", "org_id"],
            _backend=self.backend,
        )

        # Gate metrics
        self.gate_checks_total = Counter(
            name=f"{self.prefix}_gate_checks_total",
            description="Total gate checks performed",
            labels=["org_id", "repo"],
            _backend=self.backend,
        )

        self.gate_passed_total = Counter(
            name=f"{self.prefix}_gate_passed_total",
            description="Total gate checks passed",
            labels=["org_id", "repo"],
            _backend=self.backend,
        )

        self.gate_failed_total = Counter(
            name=f"{self.prefix}_gate_failed_total",
            description="Total gate checks failed",
            labels=["org_id", "repo"],
            _backend=self.backend,
        )

        self.gate_duration_seconds = Histogram(
            name=f"{self.prefix}_gate_duration_seconds",
            description="Gate check duration",
            labels=["org_id"],
            buckets=[1, 5, 10, 30, 60, 120, 300],
            _backend=self.backend,
        )

        # Resource metrics
        self.concurrent_runs = Gauge(
            name=f"{self.prefix}_concurrent_runs",
            description="Current concurrent runs",
            labels=["org_id"],
            _backend=self.backend,
        )

        self.quota_usage_percent = Gauge(
            name=f"{self.prefix}_quota_usage_percent",
            description="Quota usage percentage",
            labels=["org_id", "resource_type"],
            _backend=self.backend,
        )

        # Error metrics
        self.errors_total = Counter(
            name=f"{self.prefix}_errors_total",
            description="Total errors",
            labels=["component", "error_type"],
            _backend=self.backend,
        )

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def record_run_started(
        self,
        org_id: str,
        repo: str,
        run_type: str,
    ) -> None:
        """Record that a run has started"""
        labels = MetricLabels(org_id=org_id, repo=repo, run_type=run_type)
        self.runs_in_progress.inc(1, labels)

    def record_run_completed(
        self,
        org_id: str,
        repo: str,
        run_type: str,
        status: str,
        duration_seconds: float,
        findings_count: int = 0,
    ) -> None:
        """Record that a run has completed"""
        labels = MetricLabels(
            org_id=org_id, repo=repo, run_type=run_type, status=status
        )
        self.runs_total.inc(1, labels)
        self.runs_in_progress.dec(1, MetricLabels(org_id=org_id, run_type=run_type))
        self.runs_duration_seconds.observe(
            duration_seconds,
            MetricLabels(org_id=org_id, run_type=run_type)
        )

    def record_webhook_received(
        self,
        provider: str,
        event_type: str,
    ) -> None:
        """Record webhook reception"""
        labels = MetricLabels(provider=provider)
        self.webhooks_received_total.inc(1, labels)

    def record_gate_result(
        self,
        org_id: str,
        repo: str,
        passed: bool,
        duration_seconds: float,
    ) -> None:
        """Record gate check result"""
        labels = MetricLabels(org_id=org_id, repo=repo)
        self.gate_checks_total.inc(1, labels)

        if passed:
            self.gate_passed_total.inc(1, labels)
        else:
            self.gate_failed_total.inc(1, labels)

        self.gate_duration_seconds.observe(
            duration_seconds,
            MetricLabels(org_id=org_id)
        )

    def record_error(
        self,
        component: str,
        error_type: str,
    ) -> None:
        """Record an error"""
        if self.backend:
            self.backend.counter_inc(
                f"{self.prefix}_errors_total",
                1,
                {"component": component, "error_type": error_type},
            )

    def update_queue_depth(
        self,
        queue: str,
        depth: int,
    ) -> None:
        """Update queue depth gauge"""
        labels = MetricLabels(queue=queue)
        self.queue_depth.set(float(depth), labels)
