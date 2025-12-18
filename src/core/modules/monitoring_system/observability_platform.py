"""
Observability Platform (可觀測性平台)

Unified observability with metrics, logs, and traces

Reference: Uber's uMonitor - AI anomaly detection pinpoints faulty services in real-time [10]
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TraceStatus(Enum):
    """Trace span status"""
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class EventType(Enum):
    """Types of events"""
    DEPLOYMENT = "deployment"
    CONFIG_CHANGE = "config_change"
    INCIDENT = "incident"
    ALERT = "alert"
    REMEDIATION = "remediation"
    SCALE = "scale"
    MAINTENANCE = "maintenance"


@dataclass
class LogEntry:
    """A log entry"""
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: LogLevel = LogLevel.INFO
    message: str = ""
    service: str = ""
    component: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    trace_id: str | None = None
    span_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'log_id': self.log_id,
            'level': self.level.value,
            'message': self.message,
            'service': self.service,
            'component': self.component,
            'timestamp': self.timestamp.isoformat(),
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'attributes': self.attributes
        }


@dataclass
class TraceSpan:
    """A trace span"""
    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: str | None = None
    name: str = ""
    service: str = ""
    operation: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    status: TraceStatus = TraceStatus.UNSET
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def end(self, status: TraceStatus = TraceStatus.OK) -> None:
        """End the span"""
        self.end_time = datetime.now()
        self.status = status

    def duration_ms(self) -> float | None:
        """Get duration in milliseconds"""
        if not self.end_time:
            return None
        return (self.end_time - self.start_time).total_seconds() * 1000

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add an event to the span"""
        self.events.append({
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'attributes': attributes or {}
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            'span_id': self.span_id,
            'trace_id': self.trace_id,
            'parent_span_id': self.parent_span_id,
            'name': self.name,
            'service': self.service,
            'operation': self.operation,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_ms': self.duration_ms(),
            'status': self.status.value,
            'attributes': self.attributes,
            'events': self.events
        }


@dataclass
class CorrelatedEvent:
    """An event correlated across systems"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.INCIDENT
    title: str = ""
    description: str = ""
    source: str = ""
    severity: str = "info"
    timestamp: datetime = field(default_factory=datetime.now)
    related_services: list[str] = field(default_factory=list)
    related_logs: list[str] = field(default_factory=list)
    related_traces: list[str] = field(default_factory=list)
    related_metrics: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            'event_id': self.event_id,
            'type': self.event_type.value,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'related_services': self.related_services,
            'related_logs': self.related_logs,
            'related_traces': self.related_traces,
            'related_metrics': self.related_metrics
        }


class CorrelationEngine:
    """
    Correlation Engine
    
    Correlates events across metrics, logs, and traces
    """

    def __init__(self, time_window_seconds: int = 300):
        self._time_window = time_window_seconds
        self._events: list[CorrelatedEvent] = []

    def correlate_by_time(
        self,
        logs: list[LogEntry],
        traces: list[TraceSpan],
        metric_names: list[str],
        reference_time: datetime
    ) -> CorrelatedEvent:
        """Correlate events by time proximity"""
        event = CorrelatedEvent(
            event_type=EventType.INCIDENT,
            title="Time-correlated event",
            timestamp=reference_time
        )

        # Find logs within time window
        for log in logs:
            time_diff = abs((log.timestamp - reference_time).total_seconds())
            if time_diff <= self._time_window:
                event.related_logs.append(log.log_id)
                if log.service and log.service not in event.related_services:
                    event.related_services.append(log.service)

        # Find traces within time window
        for trace in traces:
            time_diff = abs((trace.start_time - reference_time).total_seconds())
            if time_diff <= self._time_window:
                event.related_traces.append(trace.trace_id)
                if trace.service and trace.service not in event.related_services:
                    event.related_services.append(trace.service)

        event.related_metrics = metric_names

        self._events.append(event)
        return event

    def correlate_by_trace(
        self,
        logs: list[LogEntry],
        traces: list[TraceSpan],
        trace_id: str
    ) -> CorrelatedEvent:
        """Correlate events by trace ID"""
        event = CorrelatedEvent(
            event_type=EventType.INCIDENT,
            title=f"Trace-correlated event: {trace_id}"
        )

        # Find all spans in trace
        trace_spans = [t for t in traces if t.trace_id == trace_id]
        for span in trace_spans:
            if span.span_id not in event.related_traces:
                event.related_traces.append(span.span_id)
            if span.service and span.service not in event.related_services:
                event.related_services.append(span.service)

        # Find logs with matching trace ID
        for log in logs:
            if log.trace_id == trace_id:
                event.related_logs.append(log.log_id)

        self._events.append(event)
        return event

    def get_correlated_events(self) -> list[CorrelatedEvent]:
        """Get all correlated events"""
        return self._events.copy()


class ObservabilityPlatform:
    """
    Observability Platform (可觀測性平台)
    
    Unified observability with metrics, logs, and traces
    
    Reference: Uber's uMonitor for real-time AI anomaly detection [10]
    """

    def __init__(self):
        self._logs: list[LogEntry] = []
        self._traces: dict[str, list[TraceSpan]] = {}  # trace_id -> spans
        self._events: list[CorrelatedEvent] = []
        self._correlation_engine = CorrelationEngine()
        self._max_retention = 10000  # Max entries to retain

    @property
    def correlation_engine(self) -> CorrelationEngine:
        return self._correlation_engine

    # === Logging ===

    def log(
        self,
        level: LogLevel,
        message: str,
        service: str = "",
        component: str = "",
        trace_id: str | None = None,
        span_id: str | None = None,
        attributes: dict[str, Any] | None = None
    ) -> LogEntry:
        """Log a message"""
        entry = LogEntry(
            level=level,
            message=message,
            service=service,
            component=component,
            trace_id=trace_id,
            span_id=span_id,
            attributes=attributes or {}
        )
        self._logs.append(entry)
        self._cleanup_logs()
        return entry

    def log_info(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.INFO, message, **kwargs)

    def log_warning(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.WARNING, message, **kwargs)

    def log_error(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.ERROR, message, **kwargs)

    def get_logs(
        self,
        service: str | None = None,
        level: LogLevel | None = None,
        since: datetime | None = None
    ) -> list[LogEntry]:
        """Get logs with optional filters"""
        logs = self._logs

        if service:
            logs = [l for l in logs if l.service == service]
        if level:
            logs = [l for l in logs if l.level == level]
        if since:
            logs = [l for l in logs if l.timestamp >= since]

        return logs

    def _cleanup_logs(self) -> None:
        """Clean up old logs"""
        if len(self._logs) > self._max_retention:
            self._logs = self._logs[-self._max_retention:]

    # === Tracing ===

    def start_trace(
        self,
        name: str,
        service: str = "",
        operation: str = "",
        attributes: dict[str, Any] | None = None
    ) -> TraceSpan:
        """Start a new trace"""
        span = TraceSpan(
            name=name,
            service=service,
            operation=operation,
            attributes=attributes or {}
        )

        if span.trace_id not in self._traces:
            self._traces[span.trace_id] = []
        self._traces[span.trace_id].append(span)

        return span

    def start_span(
        self,
        trace_id: str,
        parent_span_id: str,
        name: str,
        service: str = "",
        operation: str = "",
        attributes: dict[str, Any] | None = None
    ) -> TraceSpan:
        """Start a child span"""
        span = TraceSpan(
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=name,
            service=service,
            operation=operation,
            attributes=attributes or {}
        )

        if trace_id not in self._traces:
            self._traces[trace_id] = []
        self._traces[trace_id].append(span)

        return span

    def end_span(self, span: TraceSpan, status: TraceStatus = TraceStatus.OK) -> None:
        """End a span"""
        span.end(status)

    def get_trace(self, trace_id: str) -> list[TraceSpan]:
        """Get all spans in a trace"""
        return self._traces.get(trace_id, [])

    def get_slow_traces(self, threshold_ms: float = 1000) -> list[TraceSpan]:
        """Get traces slower than threshold"""
        slow = []
        for _trace_id, spans in self._traces.items():
            # Find root span
            root = next((s for s in spans if s.parent_span_id is None), None)
            if root and root.duration_ms() and root.duration_ms() > threshold_ms:
                slow.append(root)
        return slow

    # === Events ===

    def record_event(
        self,
        event_type: EventType,
        title: str,
        description: str = "",
        source: str = "",
        severity: str = "info",
        related_services: list[str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> CorrelatedEvent:
        """Record an event"""
        event = CorrelatedEvent(
            event_type=event_type,
            title=title,
            description=description,
            source=source,
            severity=severity,
            related_services=related_services or [],
            metadata=metadata or {}
        )
        self._events.append(event)
        return event

    def get_events(
        self,
        event_type: EventType | None = None,
        since: datetime | None = None
    ) -> list[CorrelatedEvent]:
        """Get events with optional filters"""
        events = self._events

        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if since:
            events = [e for e in events if e.timestamp >= since]

        return events

    # === Analysis ===

    def get_service_health(self, service: str) -> dict[str, Any]:
        """Get health summary for a service"""
        # Count error logs
        error_logs = self.get_logs(service=service, level=LogLevel.ERROR)
        warning_logs = self.get_logs(service=service, level=LogLevel.WARNING)

        # Get traces for service
        service_traces = []
        for _trace_id, spans in self._traces.items():
            for span in spans:
                if span.service == service:
                    service_traces.append(span)
                    break

        error_traces = [t for t in service_traces if t.status == TraceStatus.ERROR]

        # Calculate health score
        total_traces = len(service_traces)
        error_rate = len(error_traces) / total_traces if total_traces > 0 else 0

        if error_rate > 0.1 or len(error_logs) > 10:
            status = "UNHEALTHY"
        elif error_rate > 0.05 or len(warning_logs) > 10:
            status = "DEGRADED"
        else:
            status = "HEALTHY"

        return {
            'service': service,
            'status': status,
            'error_logs': len(error_logs),
            'warning_logs': len(warning_logs),
            'total_traces': total_traces,
            'error_traces': len(error_traces),
            'error_rate': error_rate,
            'timestamp': datetime.now().isoformat()
        }

    def get_platform_summary(self) -> dict[str, Any]:
        """Get overall platform summary"""
        services = set()
        for spans in self._traces.values():
            for span in spans:
                if span.service:
                    services.add(span.service)
        for log in self._logs:
            if log.service:
                services.add(log.service)

        return {
            'total_logs': len(self._logs),
            'total_traces': len(self._traces),
            'total_events': len(self._events),
            'services': list(services),
            'timestamp': datetime.now().isoformat()
        }
