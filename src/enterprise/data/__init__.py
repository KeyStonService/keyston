"""
Data Layer and Observability Module

Essential for operations and SLA delivery:
- Primary Database: Transaction data (orgs, repos, users, policies, runs)
- Result/Report Storage: OLAP-ready for analytics
- Object Storage: Reports, artifacts, raw results
- Observability: Metrics (Prometheus), Logs, Tracing (OpenTelemetry)
- Audit Log: Who changed what when (enterprise hard requirement)
"""

from enterprise.data.audit import (
    AuditAction,
    AuditEntry,
    AuditLogger,
)
from enterprise.data.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricLabels,
    MetricsCollector,
)
from enterprise.data.storage import (
    ObjectStorage,
    StorageLocation,
    StorageObject,
)
from enterprise.data.tracing import (
    Span,
    SpanContext,
    Tracer,
)

__all__ = [
    # Audit
    "AuditLogger",
    "AuditEntry",
    "AuditAction",
    # Metrics
    "MetricsCollector",
    "Counter",
    "Gauge",
    "Histogram",
    "MetricLabels",
    # Storage
    "ObjectStorage",
    "StorageObject",
    "StorageLocation",
    # Tracing
    "Tracer",
    "Span",
    "SpanContext",
]
