"""
Smart Anomaly Detector (智能異常檢測器)

AI-driven anomaly detection without manual thresholds

Reference: AI-enhanced observability with automatic anomaly detection [4]
"""

import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AnomalyDetectionStrategy(Enum):
    """Strategies for detecting anomalies"""
    STATISTICAL = "statistical"     # Z-score based detection
    THRESHOLD = "threshold"         # Fixed threshold based
    RATE_LIMIT = "rate_limit"       # Rate of change based
    PATTERN = "pattern"             # Pattern matching based
    ML = "ml"                       # Machine learning based
    HYBRID = "hybrid"               # Combination of strategies


class AnomalyCategory(Enum):
    """Categories of anomalies"""
    PERFORMANCE = "performance"     # Performance degradation
    AVAILABILITY = "availability"   # Service availability issues
    SECURITY = "security"           # Security-related anomalies
    RESOURCE = "resource"           # Resource exhaustion
    ERROR = "error"                 # Error rate anomalies
    LATENCY = "latency"             # Latency anomalies
    TRAFFIC = "traffic"             # Traffic anomalies
    UNKNOWN = "unknown"             # Unknown category


class AnomalySeverity(Enum):
    """Severity levels for anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectedAnomaly:
    """A detected anomaly"""
    anomaly_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    category: AnomalyCategory = AnomalyCategory.UNKNOWN
    severity: AnomalySeverity = AnomalySeverity.MEDIUM
    strategy_used: AnomalyDetectionStrategy = AnomalyDetectionStrategy.STATISTICAL
    current_value: float = 0.0
    expected_value: float = 0.0
    deviation: float = 0.0
    confidence: float = 0.0
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    context: dict[str, Any] = field(default_factory=dict)
    recommended_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'anomaly_id': self.anomaly_id,
            'metric_name': self.metric_name,
            'category': self.category.value,
            'severity': self.severity.value,
            'strategy_used': self.strategy_used.value,
            'current_value': self.current_value,
            'expected_value': self.expected_value,
            'deviation': self.deviation,
            'confidence': self.confidence,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'recommended_actions': self.recommended_actions
        }


class SmartAnomalyDetector:
    """
    Smart Anomaly Detector (智能異常檢測器)
    
    AI-driven anomaly detection without manual thresholds
    
    Reference: AI-enhanced observability with automatic anomaly detection [4]
    """

    def __init__(
        self,
        default_strategy: AnomalyDetectionStrategy = AnomalyDetectionStrategy.STATISTICAL,
        sensitivity: float = 2.0,  # Z-score threshold
        min_samples: int = 10
    ):
        self._default_strategy = default_strategy
        self._sensitivity = sensitivity
        self._min_samples = min_samples
        self._baselines: dict[str, dict[str, float]] = {}
        self._history: dict[str, list[float]] = {}
        self._anomalies: list[DetectedAnomaly] = []
        self._category_rules: dict[str, AnomalyCategory] = {}

    def set_baseline(
        self,
        metric_name: str,
        mean: float,
        stdev: float,
        min_val: float | None = None,
        max_val: float | None = None
    ) -> None:
        """Set baseline statistics for a metric"""
        self._baselines[metric_name] = {
            'mean': mean,
            'stdev': stdev,
            'min': min_val,
            'max': max_val
        }

    def learn_baseline(self, metric_name: str, values: list[float]) -> dict[str, float]:
        """Learn baseline from historical data"""
        if not values:
            return {}

        baseline = {
            'mean': statistics.mean(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values)
        }
        self._baselines[metric_name] = baseline
        self._history[metric_name] = values.copy()
        return baseline

    def add_sample(self, metric_name: str, value: float) -> None:
        """Add a sample to the history"""
        if metric_name not in self._history:
            self._history[metric_name] = []
        self._history[metric_name].append(value)

        # Keep only recent samples
        max_samples = 1000
        if len(self._history[metric_name]) > max_samples:
            self._history[metric_name] = self._history[metric_name][-max_samples:]

        # Update baseline if enough samples
        if len(self._history[metric_name]) >= self._min_samples:
            self.learn_baseline(metric_name, self._history[metric_name])

    def set_category_rule(self, metric_pattern: str, category: AnomalyCategory) -> None:
        """Set category rule for metric patterns"""
        self._category_rules[metric_pattern] = category

    def _get_category(self, metric_name: str) -> AnomalyCategory:
        """Determine category based on metric name"""
        metric_lower = metric_name.lower()

        # Check custom rules first
        for pattern, category in self._category_rules.items():
            if pattern in metric_lower:
                return category

        # Default categorization
        if any(kw in metric_lower for kw in ['cpu', 'memory', 'disk', 'network']):
            return AnomalyCategory.RESOURCE
        elif any(kw in metric_lower for kw in ['latency', 'response_time', 'duration']):
            return AnomalyCategory.LATENCY
        elif any(kw in metric_lower for kw in ['error', 'failure', 'exception']):
            return AnomalyCategory.ERROR
        elif any(kw in metric_lower for kw in ['request', 'traffic', 'throughput']):
            return AnomalyCategory.TRAFFIC
        elif any(kw in metric_lower for kw in ['uptime', 'availability', 'health']):
            return AnomalyCategory.AVAILABILITY
        elif any(kw in metric_lower for kw in ['auth', 'security', 'login']):
            return AnomalyCategory.SECURITY
        else:
            return AnomalyCategory.UNKNOWN

    def _calculate_severity(self, deviation: float, confidence: float) -> AnomalySeverity:
        """Calculate severity based on deviation and confidence"""
        score = deviation * confidence

        if score > 4.0:
            return AnomalySeverity.CRITICAL
        elif score > 3.0:
            return AnomalySeverity.HIGH
        elif score > 2.0:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def detect_statistical(
        self,
        metric_name: str,
        value: float
    ) -> DetectedAnomaly | None:
        """Detect anomaly using statistical method (Z-score)"""
        baseline = self._baselines.get(metric_name)
        if not baseline or baseline['stdev'] == 0:
            return None

        z_score = abs((value - baseline['mean']) / baseline['stdev'])

        if z_score > self._sensitivity:
            deviation = z_score
            confidence = min(1.0, z_score / 5.0)

            return DetectedAnomaly(
                metric_name=metric_name,
                category=self._get_category(metric_name),
                severity=self._calculate_severity(deviation, confidence),
                strategy_used=AnomalyDetectionStrategy.STATISTICAL,
                current_value=value,
                expected_value=baseline['mean'],
                deviation=deviation,
                confidence=confidence,
                description=f"Statistical anomaly: {metric_name} = {value:.2f} (expected {baseline['mean']:.2f}, z-score {z_score:.2f})"
            )

        return None

    def detect_threshold(
        self,
        metric_name: str,
        value: float,
        min_threshold: float | None = None,
        max_threshold: float | None = None
    ) -> DetectedAnomaly | None:
        """Detect anomaly using threshold-based method"""
        baseline = self._baselines.get(metric_name, {})

        min_val = min_threshold if min_threshold is not None else baseline.get('min')
        max_val = max_threshold if max_threshold is not None else baseline.get('max')

        violation = None
        if min_val is not None and value < min_val:
            violation = ('below', min_val)
        elif max_val is not None and value > max_val:
            violation = ('above', max_val)

        if violation:
            direction, threshold = violation
            deviation = abs(value - threshold) / max(abs(threshold), 1.0)

            return DetectedAnomaly(
                metric_name=metric_name,
                category=self._get_category(metric_name),
                severity=self._calculate_severity(deviation, 0.9),
                strategy_used=AnomalyDetectionStrategy.THRESHOLD,
                current_value=value,
                expected_value=threshold,
                deviation=deviation,
                confidence=0.9,
                description=f"Threshold violation: {metric_name} = {value:.2f} is {direction} threshold {threshold:.2f}"
            )

        return None

    def detect_rate_change(
        self,
        metric_name: str,
        value: float,
        max_rate_change: float = 0.5  # 50% change
    ) -> DetectedAnomaly | None:
        """Detect anomaly based on rate of change"""
        history = self._history.get(metric_name, [])
        if len(history) < 2:
            return None

        prev_value = history[-1]
        if prev_value == 0:
            return None

        rate_change = abs(value - prev_value) / abs(prev_value)

        if rate_change > max_rate_change:
            return DetectedAnomaly(
                metric_name=metric_name,
                category=self._get_category(metric_name),
                severity=self._calculate_severity(rate_change * 2, 0.8),
                strategy_used=AnomalyDetectionStrategy.RATE_LIMIT,
                current_value=value,
                expected_value=prev_value,
                deviation=rate_change,
                confidence=0.8,
                description=f"Rate change anomaly: {metric_name} changed {rate_change*100:.1f}% from {prev_value:.2f} to {value:.2f}"
            )

        return None

    def detect(
        self,
        metric_name: str,
        value: float,
        strategy: AnomalyDetectionStrategy | None = None
    ) -> DetectedAnomaly | None:
        """
        Detect anomaly using specified or default strategy
        
        For HYBRID strategy, uses all available methods and returns most confident result
        """
        strategy = strategy or self._default_strategy

        # Add sample to history
        self.add_sample(metric_name, value)

        if strategy == AnomalyDetectionStrategy.STATISTICAL:
            return self.detect_statistical(metric_name, value)
        elif strategy == AnomalyDetectionStrategy.THRESHOLD:
            return self.detect_threshold(metric_name, value)
        elif strategy == AnomalyDetectionStrategy.RATE_LIMIT:
            return self.detect_rate_change(metric_name, value)
        elif strategy == AnomalyDetectionStrategy.HYBRID:
            # Try all strategies and return most confident
            anomalies = []

            result = self.detect_statistical(metric_name, value)
            if result:
                anomalies.append(result)

            result = self.detect_threshold(metric_name, value)
            if result:
                anomalies.append(result)

            result = self.detect_rate_change(metric_name, value)
            if result:
                anomalies.append(result)

            if anomalies:
                # Return most confident
                return max(anomalies, key=lambda a: a.confidence)

        return None

    def get_anomalies(self) -> list[DetectedAnomaly]:
        """Get all detected anomalies"""
        return self._anomalies.copy()


class AnomalyClassifier:
    """
    Anomaly Classifier
    
    Classifies anomalies by severity and category
    """

    def __init__(self):
        self._severity_weights: dict[AnomalyCategory, float] = {
            AnomalyCategory.SECURITY: 1.5,
            AnomalyCategory.AVAILABILITY: 1.3,
            AnomalyCategory.ERROR: 1.2,
            AnomalyCategory.PERFORMANCE: 1.0,
            AnomalyCategory.RESOURCE: 1.0,
            AnomalyCategory.LATENCY: 0.9,
            AnomalyCategory.TRAFFIC: 0.8,
            AnomalyCategory.UNKNOWN: 0.7
        }

    def classify(self, anomaly: DetectedAnomaly) -> DetectedAnomaly:
        """Classify an anomaly with adjusted severity"""
        weight = self._severity_weights.get(anomaly.category, 1.0)
        adjusted_deviation = anomaly.deviation * weight

        # Recalculate severity
        score = adjusted_deviation * anomaly.confidence

        if score > 4.0:
            anomaly.severity = AnomalySeverity.CRITICAL
        elif score > 3.0:
            anomaly.severity = AnomalySeverity.HIGH
        elif score > 2.0:
            anomaly.severity = AnomalySeverity.MEDIUM
        else:
            anomaly.severity = AnomalySeverity.LOW

        # Add recommended actions based on category
        anomaly.recommended_actions = self._get_recommendations(anomaly)

        return anomaly

    def _get_recommendations(self, anomaly: DetectedAnomaly) -> list[str]:
        """Get recommended actions for an anomaly"""
        recommendations = []

        if anomaly.category == AnomalyCategory.RESOURCE:
            recommendations = [
                "Check resource utilization trends",
                "Consider scaling resources",
                "Investigate potential memory leaks or CPU-intensive processes"
            ]
        elif anomaly.category == AnomalyCategory.LATENCY:
            recommendations = [
                "Check network connectivity",
                "Review database query performance",
                "Check for bottlenecks in dependent services"
            ]
        elif anomaly.category == AnomalyCategory.ERROR:
            recommendations = [
                "Review error logs for details",
                "Check recent deployments",
                "Verify external service dependencies"
            ]
        elif anomaly.category == AnomalyCategory.AVAILABILITY:
            recommendations = [
                "Check service health endpoints",
                "Verify infrastructure status",
                "Review recent changes"
            ]
        elif anomaly.category == AnomalyCategory.SECURITY:
            recommendations = [
                "Review security logs immediately",
                "Check for unauthorized access attempts",
                "Verify authentication systems"
            ]
        elif anomaly.category == AnomalyCategory.TRAFFIC:
            recommendations = [
                "Check for traffic spikes",
                "Verify load balancing configuration",
                "Consider rate limiting if needed"
            ]
        else:
            recommendations = [
                "Investigate the anomaly",
                "Review related metrics",
                "Check system logs"
            ]

        return recommendations
