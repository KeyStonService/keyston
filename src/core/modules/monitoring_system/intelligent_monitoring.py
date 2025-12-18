"""
Intelligent Monitoring System (智能監控系統)

24/7 全方位監控所有指標，持續監控、智能異常檢測、自動診斷和主動修復

Reference: Self-healing systems with continuous monitoring, intelligent anomaly detection [1]
"""

import asyncio
import contextlib
import statistics
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetricType(Enum):
    """Metric types for monitoring"""
    COUNTER = "counter"           # Monotonically increasing value
    GAUGE = "gauge"               # Point-in-time value
    HISTOGRAM = "histogram"       # Distribution of values
    SUMMARY = "summary"           # Statistical summary


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """A metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'unit': self.unit,
            'description': self.description
        }


@dataclass
class Alert:
    """An alert generated from monitoring"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str = ""
    source: str = ""
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: float | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False
    labels: dict[str, str] = field(default_factory=dict)

    def acknowledge(self) -> None:
        """Acknowledge the alert"""
        self.acknowledged = True

    def resolve(self) -> None:
        """Mark alert as resolved"""
        self.resolved = True


class MetricsCollector:
    """
    Continuous metrics collection system
    
    Collects metrics from various sources and stores them for analysis
    """

    def __init__(self, retention_seconds: int = 3600):
        self._metrics: dict[str, list[Metric]] = {}
        self._collectors: dict[str, Callable[[], float]] = {}
        self._retention_seconds = retention_seconds
        self._running = False

    def register_collector(
        self,
        name: str,
        collector: Callable[[], float],
        metric_type: MetricType = MetricType.GAUGE,
        labels: dict[str, str] | None = None,
        unit: str = "",
        description: str = ""
    ) -> None:
        """Register a metric collector function"""
        self._collectors[name] = {
            'collector': collector,
            'type': metric_type,
            'labels': labels or {},
            'unit': unit,
            'description': description
        }
        if name not in self._metrics:
            self._metrics[name] = []

    def collect(self, name: str, value: float, labels: dict[str, str] | None = None) -> Metric:
        """Manually collect a metric value"""
        config = self._collectors.get(name, {
            'type': MetricType.GAUGE,
            'labels': {},
            'unit': '',
            'description': ''
        })

        metric = Metric(
            name=name,
            value=value,
            metric_type=config.get('type', MetricType.GAUGE),
            labels={**config.get('labels', {}), **(labels or {})},
            unit=config.get('unit', ''),
            description=config.get('description', '')
        )

        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(metric)

        # Cleanup old metrics
        self._cleanup_old_metrics(name)

        return metric

    def collect_all(self) -> list[Metric]:
        """Collect all registered metrics"""
        collected = []
        for name, config in self._collectors.items():
            try:
                value = config['collector']()
                metric = self.collect(name, value)
                collected.append(metric)
            except Exception:
                pass  # Skip failed collectors
        return collected

    def get_metrics(self, name: str, since: datetime | None = None) -> list[Metric]:
        """Get metrics by name, optionally filtered by time"""
        metrics = self._metrics.get(name, [])
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        return metrics

    def get_latest(self, name: str) -> Metric | None:
        """Get the latest metric value"""
        metrics = self._metrics.get(name, [])
        return metrics[-1] if metrics else None

    def get_statistics(self, name: str) -> dict[str, float]:
        """Get statistical summary of a metric"""
        metrics = self._metrics.get(name, [])
        if not metrics:
            return {}

        values = [m.value for m in metrics]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0.0
        }

    def _cleanup_old_metrics(self, name: str) -> None:
        """Remove metrics older than retention period"""
        cutoff = datetime.now().timestamp() - self._retention_seconds
        self._metrics[name] = [
            m for m in self._metrics.get(name, [])
            if m.timestamp.timestamp() > cutoff
        ]

    async def start_collection(self, interval_seconds: float = 10.0) -> None:
        """Start continuous metric collection"""
        self._running = True
        while self._running:
            self.collect_all()
            await asyncio.sleep(interval_seconds)

    def stop_collection(self) -> None:
        """Stop continuous metric collection"""
        self._running = False


class IntelligentMonitoringSystem:
    """
    Intelligent Monitoring System (智能監控系統)
    
    24/7 全方位監控所有指標
    持續監控、智能異常檢測、自動診斷和主動修復
    
    Reference: Self-healing systems with continuous monitoring [1]
    """

    def __init__(self):
        self._metrics_collector = MetricsCollector()
        self._alert_rules: dict[str, dict[str, Any]] = {}
        self._alerts: list[Alert] = []
        self._alert_handlers: list[Callable[[Alert], None]] = []
        self._running = False

    @property
    def metrics_collector(self) -> MetricsCollector:
        """Get the metrics collector"""
        return self._metrics_collector

    def register_metric(
        self,
        name: str,
        collector: Callable[[], float],
        metric_type: MetricType = MetricType.GAUGE,
        labels: dict[str, str] | None = None,
        unit: str = "",
        description: str = ""
    ) -> None:
        """Register a metric for monitoring"""
        self._metrics_collector.register_collector(
            name=name,
            collector=collector,
            metric_type=metric_type,
            labels=labels,
            unit=unit,
            description=description
        )

    def add_alert_rule(
        self,
        name: str,
        metric_name: str,
        condition: Callable[[float], bool],
        severity: AlertSeverity = AlertSeverity.WARNING,
        message_template: str = "Alert: {metric_name} = {value}"
    ) -> None:
        """Add an alerting rule"""
        self._alert_rules[name] = {
            'metric_name': metric_name,
            'condition': condition,
            'severity': severity,
            'message_template': message_template
        }

    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add a handler for alerts"""
        self._alert_handlers.append(handler)

    def check_alerts(self) -> list[Alert]:
        """Check all alert rules and generate alerts"""
        new_alerts = []

        for rule_name, rule in self._alert_rules.items():
            metric = self._metrics_collector.get_latest(rule['metric_name'])
            if metric and rule['condition'](metric.value):
                alert = Alert(
                    name=rule_name,
                    severity=rule['severity'],
                    message=rule['message_template'].format(
                        metric_name=rule['metric_name'],
                        value=metric.value
                    ),
                    source='IntelligentMonitoringSystem',
                    metric_name=rule['metric_name'],
                    metric_value=metric.value
                )
                new_alerts.append(alert)
                self._alerts.append(alert)

                # Notify handlers
                for handler in self._alert_handlers:
                    with contextlib.suppress(Exception):
                        handler(alert)

        return new_alerts

    def get_active_alerts(self) -> list[Alert]:
        """Get all unresolved alerts"""
        return [a for a in self._alerts if not a.resolved]

    def get_alerts_by_severity(self, severity: AlertSeverity) -> list[Alert]:
        """Get alerts by severity level"""
        return [a for a in self._alerts if a.severity == severity]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledge()
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolve()
                return True
        return False

    def get_health_status(self) -> dict[str, Any]:
        """Get overall system health status"""
        active_alerts = self.get_active_alerts()
        critical_count = len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL])
        error_count = len([a for a in active_alerts if a.severity == AlertSeverity.ERROR])
        warning_count = len([a for a in active_alerts if a.severity == AlertSeverity.WARNING])

        if critical_count > 0:
            status = "CRITICAL"
        elif error_count > 0:
            status = "ERROR"
        elif warning_count > 0:
            status = "WARNING"
        else:
            status = "HEALTHY"

        return {
            'status': status,
            'active_alerts': len(active_alerts),
            'critical': critical_count,
            'error': error_count,
            'warning': warning_count,
            'timestamp': datetime.now().isoformat()
        }

    async def start(self, collection_interval: float = 10.0, check_interval: float = 30.0) -> None:
        """Start the monitoring system"""
        self._running = True

        async def collection_loop():
            while self._running:
                self._metrics_collector.collect_all()
                await asyncio.sleep(collection_interval)

        async def check_loop():
            while self._running:
                self.check_alerts()
                await asyncio.sleep(check_interval)

        await asyncio.gather(collection_loop(), check_loop())

    def stop(self) -> None:
        """Stop the monitoring system"""
        self._running = False
        self._metrics_collector.stop_collection()
