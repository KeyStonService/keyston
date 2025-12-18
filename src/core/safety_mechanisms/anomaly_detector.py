"""
Anomaly Detector (異常檢測器)

Detect anomalies in system behavior and trigger appropriate responses.

Reference: Organizations will leverage AI-driven infrastructure that can
detect anomalies, neutralize risks, and learn from each incident [5]
"""

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
import asyncio


class AnomalyType(Enum):
    """Types of anomalies"""
    RATE_ANOMALY = "rate"           # Unusual rate of events
    VALUE_ANOMALY = "value"         # Unusual values
    PATTERN_ANOMALY = "pattern"     # Unusual patterns
    SEQUENCE_ANOMALY = "sequence"   # Unusual sequences
    BEHAVIOR_ANOMALY = "behavior"   # Unusual behavior
    RESOURCE_ANOMALY = "resource"   # Resource usage anomaly
    SECURITY_ANOMALY = "security"   # Security-related anomaly


class AnomalySeverity(Enum):
    """Severity levels for anomalies"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class DetectionStrategy(Enum):
    """Strategies for anomaly detection"""
    STATISTICAL = "statistical"     # Statistical methods (std dev, z-score)
    THRESHOLD = "threshold"         # Simple threshold-based
    RATE_LIMIT = "rate_limit"      # Rate limiting
    PATTERN = "pattern"            # Pattern matching
    MACHINE_LEARNING = "ml"        # ML-based detection
    HYBRID = "hybrid"              # Combination of methods


@dataclass
class AnomalyAlert:
    """Alert generated when anomaly is detected"""
    id: str
    type: AnomalyType
    severity: AnomalySeverity
    timestamp: datetime
    source: str
    description: str
    details: Dict[str, Any]
    strategy_used: DetectionStrategy
    recommended_action: Optional[str] = None
    acknowledged: bool = False


@dataclass
class MetricWindow:
    """Sliding window of metric values"""
    values: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    max_size: int = 1000
    
    def add(self, value: float, timestamp: Optional[datetime] = None) -> None:
        """Add a value to the window"""
        self.values.append(value)
        self.timestamps.append(timestamp or datetime.now())
        
        # Trim if needed
        if len(self.values) > self.max_size:
            self.values = self.values[-self.max_size:]
            self.timestamps = self.timestamps[-self.max_size:]
    
    def get_recent(self, seconds: float) -> List[float]:
        """Get values from the last N seconds"""
        cutoff = datetime.now() - timedelta(seconds=seconds)
        return [
            v for v, t in zip(self.values, self.timestamps)
            if t >= cutoff
        ]
    
    @property
    def mean(self) -> float:
        """Calculate mean of values"""
        return statistics.mean(self.values) if self.values else 0.0
    
    @property
    def std_dev(self) -> float:
        """Calculate standard deviation"""
        return statistics.stdev(self.values) if len(self.values) > 1 else 0.0


class AnomalyDetector:
    """
    Anomaly Detection System
    
    Monitors system metrics and behaviors to detect anomalies,
    triggering appropriate responses when issues are found.
    
    Features:
    - Multiple detection strategies
    - Configurable thresholds
    - Severity classification
    - Automatic alerting
    
    Example:
        detector = AnomalyDetector()
        detector.add_metric("error_rate", threshold=0.1)
        await detector.record("error_rate", 0.15)  # Triggers alert
    """
    
    def __init__(self):
        self._metrics: Dict[str, MetricWindow] = {}
        self._thresholds: Dict[str, Dict[str, Any]] = {}
        self._alerts: List[AnomalyAlert] = []
        self._handlers: Dict[AnomalyType, List[Callable[[AnomalyAlert], None]]] = {
            t: [] for t in AnomalyType
        }
        self._global_handlers: List[Callable[[AnomalyAlert], None]] = []
        self._alert_counter = 0
    
    def add_metric(
        self,
        name: str,
        threshold: Optional[float] = None,
        min_threshold: Optional[float] = None,
        max_threshold: Optional[float] = None,
        std_dev_factor: float = 2.0,
        rate_limit: Optional[Tuple[int, float]] = None,  # (count, seconds)
        detection_strategy: DetectionStrategy = DetectionStrategy.HYBRID,
        window_size: int = 1000
    ) -> None:
        """
        Add a metric to monitor
        
        Args:
            name: Metric name
            threshold: Simple threshold (exceeded = anomaly)
            min_threshold: Minimum acceptable value
            max_threshold: Maximum acceptable value
            std_dev_factor: Number of std deviations for statistical detection
            rate_limit: Rate limit as (count, seconds)
            detection_strategy: Strategy to use
            window_size: Size of sliding window
        """
        self._metrics[name] = MetricWindow(max_size=window_size)
        self._thresholds[name] = {
            "threshold": threshold,
            "min": min_threshold,
            "max": max_threshold,
            "std_dev_factor": std_dev_factor,
            "rate_limit": rate_limit,
            "strategy": detection_strategy
        }
    
    def add_handler(
        self,
        handler: Callable[[AnomalyAlert], None],
        anomaly_type: Optional[AnomalyType] = None
    ) -> None:
        """
        Add a handler for anomaly alerts
        
        Args:
            handler: Function to call when anomaly detected
            anomaly_type: Optional specific type to handle (None = all)
        """
        if anomaly_type:
            self._handlers[anomaly_type].append(handler)
        else:
            self._global_handlers.append(handler)
    
    async def record(
        self,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AnomalyAlert]:
        """
        Record a metric value and check for anomalies
        
        Args:
            metric_name: Name of the metric
            value: Value to record
            metadata: Optional metadata
            
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = MetricWindow()
            self._thresholds[metric_name] = {
                "strategy": DetectionStrategy.STATISTICAL,
                "std_dev_factor": 2.0
            }
        
        window = self._metrics[metric_name]
        config = self._thresholds[metric_name]
        
        # Record the value
        window.add(value)
        
        # Check for anomalies
        anomaly = await self._detect_anomaly(metric_name, value, config, metadata)
        
        if anomaly:
            self._alerts.append(anomaly)
            await self._notify_handlers(anomaly)
        
        return anomaly
    
    async def _detect_anomaly(
        self,
        metric_name: str,
        value: float,
        config: Dict[str, Any],
        metadata: Optional[Dict[str, Any]]
    ) -> Optional[AnomalyAlert]:
        """Detect if value is anomalous"""
        strategy = config.get("strategy", DetectionStrategy.STATISTICAL)
        window = self._metrics[metric_name]
        
        is_anomaly = False
        anomaly_type = AnomalyType.VALUE_ANOMALY
        description = ""
        details = {"value": value, "metric": metric_name}
        
        # Threshold check
        threshold = config.get("threshold")
        if threshold is not None and value > threshold:
            is_anomaly = True
            description = f"Value {value} exceeds threshold {threshold}"
            details["threshold"] = threshold
        
        # Min/max check
        min_val = config.get("min")
        max_val = config.get("max")
        if min_val is not None and value < min_val:
            is_anomaly = True
            description = f"Value {value} below minimum {min_val}"
            details["min_threshold"] = min_val
        if max_val is not None and value > max_val:
            is_anomaly = True
            description = f"Value {value} above maximum {max_val}"
            details["max_threshold"] = max_val
        
        # Statistical check
        if strategy in [DetectionStrategy.STATISTICAL, DetectionStrategy.HYBRID]:
            if len(window.values) >= 10:
                mean = window.mean
                std_dev = window.std_dev
                factor = config.get("std_dev_factor", 2.0)
                
                if std_dev > 0:
                    z_score = abs(value - mean) / std_dev
                    if z_score > factor:
                        is_anomaly = True
                        description = f"Value {value} is {z_score:.2f} std devs from mean"
                        details["z_score"] = z_score
                        details["mean"] = mean
                        details["std_dev"] = std_dev
        
        # Rate limit check
        rate_limit = config.get("rate_limit")
        if rate_limit:
            count, seconds = rate_limit
            recent = window.get_recent(seconds)
            if len(recent) > count:
                is_anomaly = True
                anomaly_type = AnomalyType.RATE_ANOMALY
                description = f"Rate limit exceeded: {len(recent)} events in {seconds}s (limit: {count})"
                details["rate_count"] = len(recent)
                details["rate_limit"] = count
                details["rate_window"] = seconds
        
        if not is_anomaly:
            return None
        
        # Determine severity
        severity = self._classify_severity(value, config, details)
        
        # Create alert
        self._alert_counter += 1
        alert = AnomalyAlert(
            id=f"ANOMALY-{self._alert_counter:06d}",
            type=anomaly_type,
            severity=severity,
            timestamp=datetime.now(),
            source=metric_name,
            description=description,
            details={**details, **(metadata or {})},
            strategy_used=strategy,
            recommended_action=self._get_recommended_action(anomaly_type, severity)
        )
        
        return alert
    
    def _classify_severity(
        self,
        value: float,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> AnomalySeverity:
        """Classify anomaly severity"""
        # Based on z-score
        z_score = details.get("z_score", 0)
        if z_score > 5:
            return AnomalySeverity.CRITICAL
        elif z_score > 4:
            return AnomalySeverity.HIGH
        elif z_score > 3:
            return AnomalySeverity.MEDIUM
        
        # Based on threshold exceedance
        threshold = config.get("threshold")
        if threshold and value > threshold:
            ratio = value / threshold
            if ratio > 2:
                return AnomalySeverity.CRITICAL
            elif ratio > 1.5:
                return AnomalySeverity.HIGH
            elif ratio > 1.2:
                return AnomalySeverity.MEDIUM
        
        return AnomalySeverity.LOW
    
    def _get_recommended_action(
        self,
        anomaly_type: AnomalyType,
        severity: AnomalySeverity
    ) -> str:
        """Get recommended action based on anomaly type and severity"""
        actions = {
            (AnomalyType.RATE_ANOMALY, AnomalySeverity.CRITICAL): "Immediately throttle or stop operations",
            (AnomalyType.RATE_ANOMALY, AnomalySeverity.HIGH): "Enable rate limiting",
            (AnomalyType.VALUE_ANOMALY, AnomalySeverity.CRITICAL): "Trigger circuit breaker",
            (AnomalyType.VALUE_ANOMALY, AnomalySeverity.HIGH): "Alert on-call team",
            (AnomalyType.SECURITY_ANOMALY, AnomalySeverity.CRITICAL): "Emergency stop all operations",
            (AnomalyType.SECURITY_ANOMALY, AnomalySeverity.HIGH): "Isolate affected components",
            (AnomalyType.RESOURCE_ANOMALY, AnomalySeverity.CRITICAL): "Scale resources immediately",
        }
        
        return actions.get(
            (anomaly_type, severity),
            "Monitor and investigate"
        )
    
    async def _notify_handlers(self, alert: AnomalyAlert) -> None:
        """Notify registered handlers of an anomaly"""
        # Type-specific handlers
        for handler in self._handlers[alert.type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception:
                pass
        
        # Global handlers
        for handler in self._global_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception:
                pass
    
    def get_alerts(
        self,
        since: Optional[datetime] = None,
        severity: Optional[AnomalySeverity] = None,
        anomaly_type: Optional[AnomalyType] = None,
        limit: int = 100
    ) -> List[AnomalyAlert]:
        """Get alerts with optional filters"""
        alerts = self._alerts
        
        if since:
            alerts = [a for a in alerts if a.timestamp >= since]
        if severity:
            alerts = [a for a in alerts if a.severity.value >= severity.value]
        if anomaly_type:
            alerts = [a for a in alerts if a.type == anomaly_type]
        
        return alerts[-limit:]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def get_metrics_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all monitored metrics"""
        summary = {}
        for name, window in self._metrics.items():
            if window.values:
                summary[name] = {
                    "count": len(window.values),
                    "mean": window.mean,
                    "std_dev": window.std_dev,
                    "min": min(window.values),
                    "max": max(window.values),
                    "latest": window.values[-1] if window.values else None
                }
        return summary
    
    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self._alerts.clear()
