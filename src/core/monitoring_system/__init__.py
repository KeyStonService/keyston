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

from .intelligent_monitoring import (
    MetricType,
    Metric,
    MetricsCollector,
    Alert,
    AlertSeverity,
    IntelligentMonitoringSystem
)
from .smart_anomaly_detector import (
    AnomalyDetectionStrategy,
    AnomalyCategory,
    DetectedAnomaly,
    SmartAnomalyDetector,
    AnomalyClassifier
)
from .auto_diagnosis import (
    DiagnosisResult,
    RootCause,
    DiagnosisContext,
    AutoDiagnosisEngine,
    RecommendationGenerator
)
from .auto_remediation import (
    RemediationAction,
    RemediationPlaybook,
    RemediationResult,
    AutoRemediationEngine,
    RemediationExecutor
)
from .self_learning import (
    IncidentPattern,
    LearningOutcome,
    SelfLearningEngine,
    PatternLearner,
    EffectivenessTracker
)
from .observability_platform import (
    LogEntry,
    TraceSpan,
    CorrelatedEvent,
    ObservabilityPlatform,
    CorrelationEngine
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
