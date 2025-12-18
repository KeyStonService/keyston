"""
Tests for Phase 11: Intelligent Monitoring and Auto-Remediation System

Tests for:
- IntelligentMonitoringSystem
- SmartAnomalyDetector
- AutoDiagnosisEngine
- AutoRemediationEngine
- SelfLearningEngine
- ObservabilityPlatform
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.monitoring_system import (
    # Intelligent Monitoring
    MetricType, Metric, MetricsCollector, Alert, AlertSeverity,
    IntelligentMonitoringSystem,
    # Smart Anomaly Detection
    AnomalyDetectionStrategy, AnomalyCategory, DetectedAnomaly,
    SmartAnomalyDetector, AnomalyClassifier,
    # Auto Diagnosis
    DiagnosisResult, RootCause, DiagnosisContext,
    AutoDiagnosisEngine, RecommendationGenerator,
    # Auto Remediation
    RemediationAction, RemediationPlaybook, RemediationResult,
    AutoRemediationEngine, RemediationExecutor,
    # Self Learning
    IncidentPattern, LearningOutcome, SelfLearningEngine,
    PatternLearner, EffectivenessTracker,
    # Observability Platform
    LogEntry, TraceSpan, CorrelatedEvent,
    ObservabilityPlatform, CorrelationEngine
)
from core.monitoring_system.intelligent_monitoring import MetricType as MT
from core.monitoring_system.auto_remediation import RemediationType, RemediationStatus
from core.monitoring_system.smart_anomaly_detector import AnomalySeverity
from core.monitoring_system.self_learning import PatternType
from core.monitoring_system.observability_platform import LogLevel, TraceStatus, EventType


# ============ Intelligent Monitoring Tests ============

class TestMetricsCollector:
    """Tests for MetricsCollector"""
    
    def test_collect_metric(self):
        """Test collecting a metric"""
        collector = MetricsCollector()
        metric = collector.collect('cpu_usage', 75.5)
        
        assert metric.name == 'cpu_usage'
        assert metric.value == 75.5
        assert metric.metric_type == MetricType.GAUGE
    
    def test_register_collector(self):
        """Test registering a collector function"""
        collector = MetricsCollector()
        collector.register_collector(
            name='test_metric',
            collector=lambda: 42.0,
            metric_type=MetricType.GAUGE
        )
        
        metrics = collector.collect_all()
        assert len(metrics) == 1
        assert metrics[0].value == 42.0
    
    def test_get_statistics(self):
        """Test getting statistics for a metric"""
        collector = MetricsCollector()
        
        for value in [10, 20, 30, 40, 50]:
            collector.collect('test', value)
        
        stats = collector.get_statistics('test')
        assert stats['count'] == 5
        assert stats['min'] == 10
        assert stats['max'] == 50
        assert stats['mean'] == 30


class TestIntelligentMonitoringSystem:
    """Tests for IntelligentMonitoringSystem"""
    
    def test_register_metric(self):
        """Test registering a metric"""
        monitor = IntelligentMonitoringSystem()
        monitor.register_metric(
            name='memory_usage',
            collector=lambda: 60.0
        )
        
        monitor.metrics_collector.collect_all()
        latest = monitor.metrics_collector.get_latest('memory_usage')
        assert latest is not None
        assert latest.value == 60.0
    
    def test_add_alert_rule(self):
        """Test adding an alert rule"""
        monitor = IntelligentMonitoringSystem()
        monitor.register_metric('cpu', collector=lambda: 95.0)
        monitor.add_alert_rule(
            name='high_cpu',
            metric_name='cpu',
            condition=lambda v: v > 90,
            severity=AlertSeverity.CRITICAL
        )
        
        monitor.metrics_collector.collect_all()
        alerts = monitor.check_alerts()
        
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
    
    def test_health_status(self):
        """Test getting health status"""
        monitor = IntelligentMonitoringSystem()
        status = monitor.get_health_status()
        
        assert 'status' in status
        assert status['status'] == 'HEALTHY'


# ============ Smart Anomaly Detection Tests ============

class TestSmartAnomalyDetector:
    """Tests for SmartAnomalyDetector"""
    
    def test_learn_baseline(self):
        """Test learning baseline from data"""
        detector = SmartAnomalyDetector()
        baseline = detector.learn_baseline('test', [10, 20, 30, 40, 50])
        
        assert baseline['mean'] == 30
        assert baseline['min'] == 10
        assert baseline['max'] == 50
    
    def test_detect_statistical_anomaly(self):
        """Test statistical anomaly detection"""
        detector = SmartAnomalyDetector(sensitivity=2.0)
        detector.learn_baseline('cpu', [50, 52, 48, 51, 49])
        
        # Normal value - no anomaly
        result = detector.detect_statistical('cpu', 53)
        assert result is None
        
        # Anomalous value
        result = detector.detect_statistical('cpu', 100)
        assert result is not None
        assert result.metric_name == 'cpu'
    
    def test_detect_threshold_anomaly(self):
        """Test threshold-based anomaly detection"""
        detector = SmartAnomalyDetector()
        detector.set_baseline('memory', mean=50, stdev=10, min_val=0, max_val=80)
        
        result = detector.detect_threshold('memory', 95)
        assert result is not None
        assert 'above' in result.description
    
    def test_hybrid_detection(self):
        """Test hybrid detection strategy"""
        detector = SmartAnomalyDetector(default_strategy=AnomalyDetectionStrategy.HYBRID)
        detector.learn_baseline('latency', [100, 105, 98, 102, 101])
        
        result = detector.detect('latency', 500)
        assert result is not None


class TestAnomalyClassifier:
    """Tests for AnomalyClassifier"""
    
    def test_classify_anomaly(self):
        """Test classifying an anomaly"""
        classifier = AnomalyClassifier()
        
        anomaly = DetectedAnomaly(
            metric_name='cpu_usage',
            category=AnomalyCategory.RESOURCE,
            deviation=3.0,
            confidence=0.8
        )
        
        classified = classifier.classify(anomaly)
        assert classified.recommended_actions is not None
        assert len(classified.recommended_actions) > 0


# ============ Auto Diagnosis Tests ============

class TestAutoDiagnosisEngine:
    """Tests for AutoDiagnosisEngine"""
    
    def test_diagnose_basic(self):
        """Test basic diagnosis"""
        engine = AutoDiagnosisEngine()
        
        context = DiagnosisContext(
            anomaly_id='test-anomaly',
            metric_name='cpu.usage',
            metric_value=95.0,
            logs=['ERROR: High CPU detected'],
            related_metrics={'cpu.usage': 95.0, 'memory.usage': 60.0}
        )
        
        result = engine.diagnose(context)
        assert result.status.value in ['completed', 'failed']
        assert result.diagnosis_time_ms >= 0
    
    def test_diagnose_with_custom_rule(self):
        """Test diagnosis with custom rule"""
        engine = AutoDiagnosisEngine()
        
        def custom_rule(ctx):
            if ctx.metric_value > 90:
                return [RootCause(
                    description="High metric value",
                    component="test"
                )]
            return []
        
        engine.register_diagnosis_rule('high_value', custom_rule)
        
        context = DiagnosisContext(
            metric_name='test',
            metric_value=95.0
        )
        
        result = engine.diagnose(context)
        assert len(result.root_causes) > 0


class TestRecommendationGenerator:
    """Tests for RecommendationGenerator"""
    
    def test_generate_recommendations(self):
        """Test generating recommendations"""
        generator = RecommendationGenerator()
        
        diagnosis = DiagnosisResult(
            root_causes=[
                RootCause(description="High CPU", component="cpu"),
                RootCause(description="Memory issue", component="memory")
            ]
        )
        
        recommendations = generator.generate(diagnosis)
        assert len(recommendations) > 0
        assert len(recommendations) <= 5


# ============ Auto Remediation Tests ============

class TestRemediationExecutor:
    """Tests for RemediationExecutor"""
    
    @pytest.mark.asyncio
    async def test_execute_restart_action(self):
        """Test executing a restart action"""
        executor = RemediationExecutor()
        
        action = RemediationAction(
            name='restart_service',
            action_type=RemediationType.RESTART,
            target='test-service'
        )
        
        result = await executor.execute(action)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_execute_scale_action(self):
        """Test executing a scale action"""
        executor = RemediationExecutor()
        
        action = RemediationAction(
            name='scale_service',
            action_type=RemediationType.SCALE,
            target='test-service',
            parameters={'scale_factor': 2}
        )
        
        result = await executor.execute(action)
        assert result is True


class TestAutoRemediationEngine:
    """Tests for AutoRemediationEngine"""
    
    def test_register_playbook(self):
        """Test registering a playbook"""
        engine = AutoRemediationEngine()
        
        playbook = RemediationPlaybook(
            name='test_playbook',
            trigger_conditions=['high cpu']
        )
        
        engine.register_playbook(playbook)
        retrieved = engine.get_playbook(playbook.playbook_id)
        assert retrieved is not None
        assert retrieved.name == 'test_playbook'
    
    def test_find_matching_playbooks(self):
        """Test finding matching playbooks"""
        engine = AutoRemediationEngine()
        
        playbook = RemediationPlaybook(
            name='cpu_playbook',
            trigger_conditions=['high cpu', 'cpu overload']
        )
        engine.register_playbook(playbook)
        
        matches = engine.find_matching_playbooks('high cpu detected')
        assert len(matches) == 1
    
    @pytest.mark.asyncio
    async def test_execute_playbook(self):
        """Test executing a playbook"""
        engine = AutoRemediationEngine()
        engine.set_dry_run(True)
        
        playbook = RemediationPlaybook(
            name='test',
            actions=[
                RemediationAction(name='step1', action_type=RemediationType.RESTART)
            ]
        )
        engine.register_playbook(playbook)
        
        result = await engine.execute_playbook(playbook)
        assert result.status == RemediationStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_auto_remediate(self):
        """Test automatic remediation"""
        engine = AutoRemediationEngine()
        engine.set_dry_run(True)
        engine.create_restart_playbook('restart', 'service', ['service down'])
        
        result = await engine.auto_remediate('service down')
        assert result is not None
        assert result.verification_passed


# ============ Self Learning Tests ============

class TestPatternLearner:
    """Tests for PatternLearner"""
    
    def test_learn_new_pattern(self):
        """Test learning a new pattern"""
        learner = PatternLearner()
        
        pattern = learner.learn(
            conditions=[{'metric': 'cpu', 'value': 95}],
            description='High CPU'
        )
        
        assert pattern is not None
        assert pattern.frequency == 1
    
    def test_find_similar_pattern(self):
        """Test finding similar patterns"""
        learner = PatternLearner()
        
        learner.learn(
            conditions=[{'metric': 'cpu', 'value': 95}],
            description='High CPU'
        )
        
        # Learn similar pattern - should increment existing
        pattern = learner.learn(
            conditions=[{'metric': 'cpu', 'value': 90}]
        )
        
        assert pattern.frequency >= 1


class TestEffectivenessTracker:
    """Tests for EffectivenessTracker"""
    
    def test_record_outcome(self):
        """Test recording a remediation outcome"""
        tracker = EffectivenessTracker()
        
        tracker.record_outcome(
            remediation_id='rem-1',
            playbook_id='pb-1',
            success=True,
            execution_time_ms=1000,
            anomaly_resolved=True
        )
        
        effectiveness = tracker.get_playbook_effectiveness('pb-1')
        assert effectiveness['effectiveness'] == 1.0
        assert effectiveness['resolution_rate'] == 1.0


class TestSelfLearningEngine:
    """Tests for SelfLearningEngine"""
    
    def test_learn_from_incident(self):
        """Test learning from an incident"""
        engine = SelfLearningEngine()
        
        pattern = engine.learn_from_incident(
            conditions=[{'type': 'cpu_spike'}],
            description='CPU spike incident'
        )
        
        assert pattern is not None
    
    def test_record_remediation_outcome(self):
        """Test recording remediation outcome"""
        engine = SelfLearningEngine()
        
        engine.record_remediation_outcome(
            remediation_id='rem-1',
            playbook_id='pb-1',
            success=True,
            execution_time_ms=500,
            anomaly_resolved=True
        )
        
        summary = engine.get_learning_summary()
        assert 'total_patterns' in summary


# ============ Observability Platform Tests ============

class TestObservabilityPlatform:
    """Tests for ObservabilityPlatform"""
    
    def test_log_entry(self):
        """Test logging an entry"""
        platform = ObservabilityPlatform()
        
        entry = platform.log_info("Test message", service="test-service")
        
        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
        assert entry.service == "test-service"
    
    def test_get_logs_with_filter(self):
        """Test getting logs with filters"""
        platform = ObservabilityPlatform()
        
        platform.log_info("Info 1", service="svc1")
        platform.log_error("Error 1", service="svc1")
        platform.log_info("Info 2", service="svc2")
        
        svc1_logs = platform.get_logs(service="svc1")
        assert len(svc1_logs) == 2
        
        error_logs = platform.get_logs(level=LogLevel.ERROR)
        assert len(error_logs) == 1
    
    def test_start_trace(self):
        """Test starting a trace"""
        platform = ObservabilityPlatform()
        
        span = platform.start_trace(
            name="test-operation",
            service="test-service"
        )
        
        assert span.trace_id is not None
        assert span.span_id is not None
        assert span.name == "test-operation"
    
    def test_end_span(self):
        """Test ending a span"""
        platform = ObservabilityPlatform()
        
        span = platform.start_trace("test", service="svc")
        platform.end_span(span, TraceStatus.OK)
        
        assert span.end_time is not None
        assert span.status == TraceStatus.OK
        assert span.duration_ms() is not None
    
    def test_record_event(self):
        """Test recording an event"""
        platform = ObservabilityPlatform()
        
        event = platform.record_event(
            event_type=EventType.DEPLOYMENT,
            title="Deploy v1.0",
            source="ci-cd"
        )
        
        assert event.event_type == EventType.DEPLOYMENT
        
        events = platform.get_events(event_type=EventType.DEPLOYMENT)
        assert len(events) == 1
    
    def test_service_health(self):
        """Test getting service health"""
        platform = ObservabilityPlatform()
        
        platform.log_info("OK", service="healthy-svc")
        
        health = platform.get_service_health("healthy-svc")
        assert health['status'] == 'HEALTHY'
    
    def test_platform_summary(self):
        """Test getting platform summary"""
        platform = ObservabilityPlatform()
        
        platform.log_info("Test", service="svc1")
        platform.start_trace("op", service="svc2")
        
        summary = platform.get_platform_summary()
        assert summary['total_logs'] >= 1
        assert summary['total_traces'] >= 1


class TestCorrelationEngine:
    """Tests for CorrelationEngine"""
    
    def test_correlate_by_time(self):
        """Test correlating events by time"""
        engine = CorrelationEngine(time_window_seconds=60)
        
        now = datetime.now()
        logs = [
            LogEntry(message="Test log", service="svc1", timestamp=now)
        ]
        traces = [
            TraceSpan(name="Test trace", service="svc1", start_time=now)
        ]
        
        event = engine.correlate_by_time(logs, traces, ['metric1'], now)
        
        assert len(event.related_logs) > 0
        assert len(event.related_traces) > 0


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
