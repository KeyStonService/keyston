#!/usr/bin/env python3
"""
Prometheus Metrics for SuperAgent

Provides metrics collection and exposition compatible with Prometheus.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from collections import defaultdict
import asyncio


class Counter:
    """Prometheus-style counter metric."""

    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values: Dict[tuple, float] = defaultdict(float)
        self._lock = asyncio.Lock()

    async def inc(self, value: float = 1.0, **label_values) -> None:
        """Increment the counter."""
        key = self._make_key(label_values)
        async with self._lock:
            self._values[key] += value

    def _make_key(self, label_values: Dict[str, str]) -> tuple:
        """Create a key from label values."""
        return tuple(label_values.get(l, "") for l in self.labels)

    def collect(self) -> List[Dict[str, Any]]:
        """Collect all metric values."""
        result = []
        for key, value in self._values.items():
            labels = dict(zip(self.labels, key))
            result.append({
                "name": self.name,
                "type": "counter",
                "value": value,
                "labels": labels,
            })
        return result

    def prometheus_format(self) -> str:
        """Format metrics in Prometheus exposition format."""
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} counter"]
        for key, value in self._values.items():
            labels = dict(zip(self.labels, key))
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items()) if labels else ""
            if label_str:
                lines.append(f"{self.name}{{{label_str}}} {value}")
            else:
                lines.append(f"{self.name} {value}")
        return "\n".join(lines)


class Gauge:
    """Prometheus-style gauge metric."""

    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.labels = labels or []
        self._values: Dict[tuple, float] = {}
        self._lock = asyncio.Lock()

    async def set(self, value: float, **label_values) -> None:
        """Set the gauge value."""
        key = self._make_key(label_values)
        async with self._lock:
            self._values[key] = value

    async def inc(self, value: float = 1.0, **label_values) -> None:
        """Increment the gauge."""
        key = self._make_key(label_values)
        async with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    async def dec(self, value: float = 1.0, **label_values) -> None:
        """Decrement the gauge."""
        await self.inc(-value, **label_values)

    def _make_key(self, label_values: Dict[str, str]) -> tuple:
        """Create a key from label values."""
        return tuple(label_values.get(l, "") for l in self.labels)

    def collect(self) -> List[Dict[str, Any]]:
        """Collect all metric values."""
        result = []
        for key, value in self._values.items():
            labels = dict(zip(self.labels, key))
            result.append({
                "name": self.name,
                "type": "gauge",
                "value": value,
                "labels": labels,
            })
        return result

    def prometheus_format(self) -> str:
        """Format metrics in Prometheus exposition format."""
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} gauge"]
        for key, value in self._values.items():
            labels = dict(zip(self.labels, key))
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items()) if labels else ""
            if label_str:
                lines.append(f"{self.name}{{{label_str}}} {value}")
            else:
                lines.append(f"{self.name} {value}")
        return "\n".join(lines)


class Histogram:
    """Prometheus-style histogram metric."""

    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

    def __init__(
        self,
        name: str,
        description: str,
        labels: Optional[List[str]] = None,
        buckets: Optional[tuple] = None,
    ):
        self.name = name
        self.description = description
        self.labels = labels or []
        self.buckets = buckets or self.DEFAULT_BUCKETS
        self._buckets: Dict[tuple, Dict[float, int]] = defaultdict(lambda: {b: 0 for b in self.buckets})
        self._sums: Dict[tuple, float] = defaultdict(float)
        self._counts: Dict[tuple, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def observe(self, value: float, **label_values) -> None:
        """Observe a value."""
        key = self._make_key(label_values)
        async with self._lock:
            self._sums[key] += value
            self._counts[key] += 1
            for bucket in self.buckets:
                if value <= bucket:
                    self._buckets[key][bucket] += 1

    def _make_key(self, label_values: Dict[str, str]) -> tuple:
        """Create a key from label values."""
        return tuple(label_values.get(l, "") for l in self.labels)

    def collect(self) -> List[Dict[str, Any]]:
        """Collect all metric values."""
        result = []
        for key in set(list(self._sums.keys()) + list(self._counts.keys())):
            labels = dict(zip(self.labels, key))
            result.append({
                "name": self.name,
                "type": "histogram",
                "sum": self._sums[key],
                "count": self._counts[key],
                "buckets": dict(self._buckets[key]),
                "labels": labels,
            })
        return result

    def prometheus_format(self) -> str:
        """Format metrics in Prometheus exposition format."""
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} histogram"]

        for key in set(list(self._sums.keys()) + list(self._counts.keys())):
            labels = dict(zip(self.labels, key))
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())

            # Buckets
            cumulative = 0
            for bucket in sorted(self.buckets):
                cumulative += self._buckets[key].get(bucket, 0)
                if label_str:
                    lines.append(f'{self.name}_bucket{{{label_str},le="{bucket}"}} {cumulative}')
                else:
                    lines.append(f'{self.name}_bucket{{le="{bucket}"}} {cumulative}')

            # +Inf bucket
            if label_str:
                lines.append(f'{self.name}_bucket{{{label_str},le="+Inf"}} {self._counts[key]}')
                lines.append(f"{self.name}_sum{{{label_str}}} {self._sums[key]}")
                lines.append(f"{self.name}_count{{{label_str}}} {self._counts[key]}")
            else:
                lines.append(f'{self.name}_bucket{{le="+Inf"}} {self._counts[key]}')
                lines.append(f"{self.name}_sum {self._sums[key]}")
                lines.append(f"{self.name}_count {self._counts[key]}")

        return "\n".join(lines)


class MetricsCollector:
    """
    Central metrics collector for SuperAgent.

    Provides Prometheus-compatible metrics for:
    - Request counts and latencies
    - Incident statistics
    - Message processing
    - Agent health
    """

    def __init__(self):
        self._start_time = time.time()

        # Request metrics
        self.requests_total = Counter(
            "superagent_requests_total",
            "Total number of requests",
            labels=["method", "endpoint", "status"],
        )
        self.request_duration = Histogram(
            "superagent_request_duration_seconds",
            "Request duration in seconds",
            labels=["method", "endpoint"],
        )

        # Message metrics
        self.messages_received = Counter(
            "superagent_messages_received_total",
            "Total messages received",
            labels=["message_type", "source_agent"],
        )
        self.messages_processed = Counter(
            "superagent_messages_processed_total",
            "Total messages processed",
            labels=["message_type", "status"],
        )
        self.message_processing_duration = Histogram(
            "superagent_message_processing_seconds",
            "Message processing duration",
            labels=["message_type"],
        )

        # Incident metrics
        self.incidents_total = Gauge(
            "superagent_incidents_total",
            "Total number of incidents",
            labels=["state"],
        )
        self.incidents_created = Counter(
            "superagent_incidents_created_total",
            "Total incidents created",
            labels=["severity", "incident_type"],
        )
        self.incident_transitions = Counter(
            "superagent_incident_transitions_total",
            "Total incident state transitions",
            labels=["from_state", "to_state"],
        )

        # Consensus metrics
        self.consensus_requests = Counter(
            "superagent_consensus_requests_total",
            "Total consensus requests",
            labels=["request_type"],
        )
        self.consensus_votes = Counter(
            "superagent_consensus_votes_total",
            "Total consensus votes",
            labels=["vote_type", "agent"],
        )
        self.consensus_results = Counter(
            "superagent_consensus_results_total",
            "Total consensus results",
            labels=["result"],
        )

        # Agent health metrics
        self.agent_health = Gauge(
            "superagent_agent_health",
            "Agent health status (1=healthy, 0=unhealthy)",
            labels=["agent_id"],
        )

        # System metrics
        self.uptime = Gauge(
            "superagent_uptime_seconds",
            "Service uptime in seconds",
        )

        # All metrics for collection
        self._metrics = [
            self.requests_total,
            self.request_duration,
            self.messages_received,
            self.messages_processed,
            self.message_processing_duration,
            self.incidents_total,
            self.incidents_created,
            self.incident_transitions,
            self.consensus_requests,
            self.consensus_votes,
            self.consensus_results,
            self.agent_health,
            self.uptime,
        ]

    async def record_request(
        self,
        method: str,
        endpoint: str,
        status: str,
        duration: float,
    ) -> None:
        """Record an HTTP request."""
        await self.requests_total.inc(method=method, endpoint=endpoint, status=status)
        await self.request_duration.observe(duration, method=method, endpoint=endpoint)

    async def record_message(
        self,
        message_type: str,
        source_agent: str,
        status: str,
        duration: float,
    ) -> None:
        """Record a message processing."""
        await self.messages_received.inc(message_type=message_type, source_agent=source_agent)
        await self.messages_processed.inc(message_type=message_type, status=status)
        await self.message_processing_duration.observe(duration, message_type=message_type)

    async def record_incident_created(
        self,
        severity: str,
        incident_type: str,
    ) -> None:
        """Record an incident creation."""
        await self.incidents_created.inc(severity=severity, incident_type=incident_type)

    async def record_transition(
        self,
        from_state: str,
        to_state: str,
    ) -> None:
        """Record a state transition."""
        await self.incident_transitions.inc(from_state=from_state, to_state=to_state)

    async def update_incidents_by_state(self, states: Dict[str, int]) -> None:
        """Update incident counts by state."""
        for state, count in states.items():
            await self.incidents_total.set(count, state=state)

    async def update_uptime(self) -> None:
        """Update uptime metric."""
        await self.uptime.set(time.time() - self._start_time)

    def get_uptime(self) -> float:
        """Get current uptime."""
        return time.time() - self._start_time

    def collect_all(self) -> List[Dict[str, Any]]:
        """Collect all metrics."""
        result = []
        for metric in self._metrics:
            result.extend(metric.collect())
        return result

    def prometheus_format(self) -> str:
        """Get all metrics in Prometheus exposition format."""
        lines = []
        for metric in self._metrics:
            lines.append(metric.prometheus_format())
        return "\n\n".join(lines) + "\n"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "uptime_seconds": self.get_uptime(),
            "start_time": datetime.fromtimestamp(self._start_time).isoformat(),
            "metrics": self.collect_all(),
        }
