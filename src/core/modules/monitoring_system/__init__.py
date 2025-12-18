"""
SynergyMesh Intelligent Monitoring and Auto-Remediation System (Phase 11)

Core modules:
- intelligent_monitoring: 24/7 intelligent monitoring system
- smart_anomaly_detector: AI-driven anomaly detection
- auto_diagnosis: Automatic root cause analysis
- auto_remediation: Self-healing capabilities
- self_learning: Continuous improvement from incidents
- observability_platform: Unified observability
"""

from .auto_diagnosis import (
    AutoDiagnosisEngine,
    DiagnosisContext,
    DiagnosisResult,
    RecommendationGenerator,
    RootCause,
)
from .auto_remediation import (
    AutoRemediationEngine,
    RemediationAction,
    RemediationExecutor,
    RemediationPlaybook,
    RemediationResult,
)
from .intelligent_monitoring import (
    Alert,
    AlertSeverity,
    IntelligentMonitoringSystem,
    Metric,
    MetricsCollector,
    MetricType,
)
from .observability_platform import (
    CorrelatedEvent,
    CorrelationEngine,
    LogEntry,
    ObservabilityPlatform,
    TraceSpan,
)
from .self_learning import (
    EffectivenessTracker,
    IncidentPattern,
    LearningOutcome,
    PatternLearner,
    SelfLearningEngine,
)
from .smart_anomaly_detector import (
    AnomalyCategory,
    AnomalyClassifier,
    AnomalyDetectionStrategy,
    DetectedAnomaly,
    SmartAnomalyDetector,
)

__all__ = [
    # Intelligent Monitoring
    'MetricType',
    'Metric',
    'MetricsCollector',
    'Alert',
    'AlertSeverity',
    'IntelligentMonitoringSystem',
    # Smart Anomaly Detection
    'AnomalyDetectionStrategy',
    'AnomalyCategory',
    'DetectedAnomaly',
    'SmartAnomalyDetector',
    'AnomalyClassifier',
    # Auto Diagnosis
    'DiagnosisResult',
    'RootCause',
    'DiagnosisContext',
    'AutoDiagnosisEngine',
    'RecommendationGenerator',
    # Auto Remediation
    'RemediationAction',
    'RemediationPlaybook',
    'RemediationResult',
    'AutoRemediationEngine',
    'RemediationExecutor',
    # Self Learning
    'IncidentPattern',
    'LearningOutcome',
    'SelfLearningEngine',
    'PatternLearner',
    'EffectivenessTracker',
    # Observability Platform
    'LogEntry',
    'TraceSpan',
    'CorrelatedEvent',
    'ObservabilityPlatform',
    'CorrelationEngine',
]
