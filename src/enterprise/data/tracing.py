"""
Distributed Tracing (OpenTelemetry)

Provides request tracing across services:
- Trace context propagation
- Span creation and management
- Integration with Jaeger/Zipkin/etc.

Essential for debugging distributed operations.
"""

import logging
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol

logger = logging.getLogger(__name__)


# Context variable for current span
_current_span: ContextVar[Optional["Span"]] = ContextVar("current_span", default=None)


class SpanKind(Enum):
    """Types of spans"""
    INTERNAL = "internal"       # Internal operation
    SERVER = "server"          # Server handling request
    CLIENT = "client"          # Client making request
    PRODUCER = "producer"      # Message producer
    CONSUMER = "consumer"      # Message consumer


class SpanStatus(Enum):
    """Span status codes"""
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    """
    Span context for propagation

    Contains trace/span IDs for propagating context across services.
    W3C Trace Context compatible.
    """
    trace_id: str = ""         # 32-char hex
    span_id: str = ""          # 16-char hex
    trace_flags: int = 0       # Sampling flag
    trace_state: str = ""      # Vendor-specific state

    @property
    def is_valid(self) -> bool:
        """Check if context is valid"""
        return bool(self.trace_id and self.span_id)

    @property
    def is_sampled(self) -> bool:
        """Check if trace is sampled"""
        return bool(self.trace_flags & 0x01)

    def to_traceparent(self) -> str:
        """Convert to W3C traceparent header"""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags:02x}"

    @classmethod
    def from_traceparent(cls, header: str) -> Optional["SpanContext"]:
        """Parse W3C traceparent header"""
        try:
            parts = header.split("-")
            if len(parts) != 4 or parts[0] != "00":
                return None

            return cls(
                trace_id=parts[1],
                span_id=parts[2],
                trace_flags=int(parts[3], 16),
            )
        except Exception:
            return None

    @classmethod
    def generate(cls) -> "SpanContext":
        """Generate a new span context"""
        import secrets
        return cls(
            trace_id=secrets.token_hex(16),
            span_id=secrets.token_hex(8),
            trace_flags=1,  # Sampled
        )


@dataclass
class SpanEvent:
    """Event within a span"""
    name: str
    timestamp: float  # Unix timestamp
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """
    Distributed tracing span

    Represents a single operation within a trace.
    """
    name: str = ""
    context: SpanContext = field(default_factory=SpanContext)
    parent_context: SpanContext | None = None

    # Timing
    start_time: float = 0.0      # Unix timestamp
    end_time: float | None = None
    duration_ms: float | None = None

    # Classification
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""

    # Service info
    service_name: str = "machinenativeops"
    service_version: str = ""

    # Attributes
    attributes: dict[str, Any] = field(default_factory=dict)

    # Events within span
    events: list[SpanEvent] = field(default_factory=list)

    # Links to other spans
    links: list[SpanContext] = field(default_factory=list)

    # Error info
    exception: str | None = None
    exception_stacktrace: str | None = None

    def __post_init__(self):
        if not self.start_time:
            self.start_time = time.time()
        if not self.context.is_valid:
            self.context = SpanContext.generate()

    def set_attribute(self, key: str, value: Any) -> "Span":
        """Set a span attribute"""
        self.attributes[key] = value
        return self

    def set_attributes(self, attributes: dict[str, Any]) -> "Span":
        """Set multiple attributes"""
        self.attributes.update(attributes)
        return self

    def add_event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> "Span":
        """Add an event to the span"""
        event = SpanEvent(
            name=name,
            timestamp=time.time(),
            attributes=attributes or {},
        )
        self.events.append(event)
        return self

    def set_status(
        self,
        status: SpanStatus,
        message: str = "",
    ) -> "Span":
        """Set span status"""
        self.status = status
        self.status_message = message
        return self

    def record_exception(
        self,
        exception: Exception,
    ) -> "Span":
        """Record an exception"""
        import traceback

        self.status = SpanStatus.ERROR
        self.exception = str(exception)
        self.exception_stacktrace = traceback.format_exc()

        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            },
        )

        return self

    def end(self) -> "Span":
        """End the span"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.parent_context.span_id if self.parent_context else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "kind": self.kind.value,
            "status": self.status.value,
            "status_message": self.status_message,
            "service_name": self.service_name,
            "attributes": self.attributes,
            "events": [
                {
                    "name": e.name,
                    "timestamp": e.timestamp,
                    "attributes": e.attributes,
                }
                for e in self.events
            ],
        }


class TracingBackend(Protocol):
    """Interface for tracing backend (e.g., Jaeger)"""

    async def export_span(self, span: Span) -> None:
        """Export a completed span"""
        ...

    async def export_spans(self, spans: list[Span]) -> None:
        """Export multiple spans"""
        ...


@dataclass
class Tracer:
    """
    Distributed Tracer

    Provides span creation and context propagation.
    OpenTelemetry compatible.
    """

    backend: TracingBackend | None = None

    # Configuration
    service_name: str = "machinenativeops"
    service_version: str = "1.0.0"
    enabled: bool = True

    # Sampling
    sample_rate: float = 1.0  # 1.0 = 100% sampling

    # Pending spans for batch export
    _pending_spans: list[Span] = field(default_factory=list)
    _batch_size: int = 100

    # ------------------------------------------------------------------
    # Span Creation
    # ------------------------------------------------------------------

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        parent: SpanContext | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """
        Start a new span

        Args:
            name: Span name
            kind: Span kind
            parent: Parent span context (auto-detected if not provided)
            attributes: Initial attributes

        Returns:
            New span
        """
        # Get parent from context if not provided
        if parent is None:
            current = _current_span.get()
            if current:
                parent = current.context

        # Create new span
        span = Span(
            name=name,
            kind=kind,
            parent_context=parent,
            service_name=self.service_name,
            service_version=self.service_version,
            attributes=attributes or {},
        )

        # Inherit trace ID from parent
        if parent and parent.is_valid:
            span.context.trace_id = parent.trace_id

        # Set as current span
        _current_span.set(span)

        return span

    async def end_span(self, span: Span) -> None:
        """End and export a span"""
        span.end()

        # Restore parent as current
        if span.parent_context:
            # Would need to restore parent span
            pass
        else:
            _current_span.set(None)

        # Export
        if self.enabled and self.backend:
            self._pending_spans.append(span)

            if len(self._pending_spans) >= self._batch_size:
                await self._flush_spans()

    async def _flush_spans(self) -> None:
        """Flush pending spans to backend"""
        if self._pending_spans and self.backend:
            spans = self._pending_spans.copy()
            self._pending_spans.clear()

            try:
                await self.backend.export_spans(spans)
            except Exception as e:
                logger.error(f"Failed to export spans: {e}")

    # ------------------------------------------------------------------
    # Context Propagation
    # ------------------------------------------------------------------

    def extract_context(
        self,
        headers: dict[str, str],
    ) -> SpanContext | None:
        """
        Extract span context from HTTP headers

        Supports W3C Trace Context format.
        """
        traceparent = headers.get("traceparent") or headers.get("Traceparent")
        if not traceparent:
            return None

        context = SpanContext.from_traceparent(traceparent)

        # Also extract tracestate if present
        tracestate = headers.get("tracestate") or headers.get("Tracestate")
        if context and tracestate:
            context.trace_state = tracestate

        return context

    def inject_context(
        self,
        span: Span,
        headers: dict[str, str],
    ) -> dict[str, str]:
        """
        Inject span context into HTTP headers

        Returns headers with trace context added.
        """
        headers["traceparent"] = span.context.to_traceparent()

        if span.context.trace_state:
            headers["tracestate"] = span.context.trace_state

        return headers

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------

    def trace(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] | None = None,
    ) -> "SpanContextManager":
        """
        Context manager for tracing

        Usage:
            async with tracer.trace("operation") as span:
                span.set_attribute("key", "value")
                # do work
        """
        return SpanContextManager(self, name, kind, attributes)

    # ------------------------------------------------------------------
    # Current Span
    # ------------------------------------------------------------------

    def get_current_span(self) -> Span | None:
        """Get the current active span"""
        return _current_span.get()

    def get_current_trace_id(self) -> str | None:
        """Get the current trace ID"""
        span = _current_span.get()
        return span.context.trace_id if span else None

    # ------------------------------------------------------------------
    # Common Operations
    # ------------------------------------------------------------------

    async def trace_operation(
        self,
        name: str,
        operation,
        attributes: dict[str, Any] | None = None,
    ) -> Any:
        """
        Trace an async operation

        Args:
            name: Span name
            operation: Async callable to execute
            attributes: Span attributes

        Returns:
            Operation result
        """
        span = self.start_span(name, attributes=attributes)

        try:
            result = await operation()
            span.set_status(SpanStatus.OK)
            return result

        except Exception as e:
            span.record_exception(e)
            raise

        finally:
            await self.end_span(span)


@dataclass
class SpanContextManager:
    """Async context manager for spans"""
    tracer: Tracer
    name: str
    kind: SpanKind = SpanKind.INTERNAL
    attributes: dict[str, Any] | None = None
    _span: Span | None = None

    async def __aenter__(self) -> Span:
        self._span = self.tracer.start_span(
            self.name,
            self.kind,
            attributes=self.attributes,
        )
        return self._span

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            self._span.record_exception(exc_val)
        else:
            self._span.set_status(SpanStatus.OK)

        await self.tracer.end_span(self._span)


# ------------------------------------------------------------------
# Common Span Attributes
# ------------------------------------------------------------------

class SpanAttributes:
    """Standard attribute names"""
    # HTTP
    HTTP_METHOD = "http.method"
    HTTP_URL = "http.url"
    HTTP_STATUS_CODE = "http.status_code"
    HTTP_HOST = "http.host"
    HTTP_PATH = "http.path"
    HTTP_USER_AGENT = "http.user_agent"

    # Database
    DB_SYSTEM = "db.system"
    DB_NAME = "db.name"
    DB_OPERATION = "db.operation"
    DB_STATEMENT = "db.statement"

    # Messaging
    MESSAGING_SYSTEM = "messaging.system"
    MESSAGING_DESTINATION = "messaging.destination"
    MESSAGING_OPERATION = "messaging.operation"

    # RPC
    RPC_SYSTEM = "rpc.system"
    RPC_SERVICE = "rpc.service"
    RPC_METHOD = "rpc.method"

    # Custom - MNO specific
    ORG_ID = "mno.org_id"
    REPO_ID = "mno.repo_id"
    RUN_ID = "mno.run_id"
    JOB_ID = "mno.job_id"
    PROVIDER = "mno.provider"
    RUN_TYPE = "mno.run_type"
