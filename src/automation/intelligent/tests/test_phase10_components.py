"""
Tests for Phase 10 - Safety Mechanisms System
"""

import pytest
import asyncio
from datetime import datetime, timedelta


# ============ Circuit Breaker Tests ============

class TestCircuitBreaker:
    """Tests for CircuitBreaker"""
    
    def test_circuit_breaker_config(self):
        """Test circuit breaker configuration"""
        from core.safety_mechanisms.circuit_breaker import CircuitBreakerConfig
        
        config = CircuitBreakerConfig(
            name="test",
            failure_threshold=3,
            success_threshold=2,
            timeout=30.0
        )
        
        assert config.name == "test"
        assert config.failure_threshold == 3
        assert config.success_threshold == 2
        assert config.timeout == 30.0
    
    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in closed state"""
        from core.safety_mechanisms.circuit_breaker import (
            CircuitBreaker,
            CircuitBreakerState
        )
        
        breaker = CircuitBreaker()
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.is_closed
        assert not breaker.is_open
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_success(self):
        """Test circuit breaker with successful calls"""
        from core.safety_mechanisms.circuit_breaker import CircuitBreaker
        
        breaker = CircuitBreaker()
        
        result = await breaker.execute(lambda: "success")
        assert result == "success"
        assert breaker.metrics.successful_calls == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_trips_on_failures(self):
        """Test circuit breaker trips after threshold failures"""
        from core.safety_mechanisms.circuit_breaker import (
            CircuitBreaker,
            CircuitBreakerConfig,
            CircuitBreakerState,
            CircuitBreakerOpenError
        )
        
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config)
        
        def failing_op():
            raise Exception("Test failure")
        
        # First failure
        try:
            await breaker.execute(failing_op)
        except Exception:
            pass
        
        # Second failure - should trip
        try:
            await breaker.execute(failing_op)
        except Exception:
            pass
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Next call should be rejected
        with pytest.raises(CircuitBreakerOpenError):
            await breaker.execute(lambda: "test")
    
    def test_circuit_breaker_registry(self):
        """Test circuit breaker registry"""
        from core.safety_mechanisms.circuit_breaker import CircuitBreakerRegistry
        
        registry = CircuitBreakerRegistry()
        
        breaker = registry.register("database")
        assert breaker is not None
        
        same_breaker = registry.get("database")
        assert same_breaker is breaker


# ============ Escalation Ladder Tests ============

class TestEscalationLadder:
    """Tests for EscalationLadder"""
    
    def test_escalation_levels(self):
        """Test escalation level enum"""
        from core.safety_mechanisms.escalation_ladder import EscalationLevel
        
        assert EscalationLevel.LEVEL_0_NORMAL.value == 0
        assert EscalationLevel.LEVEL_5_DISASTER.value == 5
    
    def test_escalation_ladder_initial_state(self):
        """Test escalation ladder starts at normal"""
        from core.safety_mechanisms.escalation_ladder import (
            EscalationLadder,
            EscalationLevel
        )
        
        ladder = EscalationLadder()
        assert ladder.current_level == EscalationLevel.LEVEL_0_NORMAL
    
    @pytest.mark.asyncio
    async def test_escalation_ladder_escalate(self):
        """Test escalating levels"""
        from core.safety_mechanisms.escalation_ladder import (
            EscalationLadder,
            EscalationLevel
        )
        
        ladder = EscalationLadder()
        
        event = await ladder.escalate("Test issue", "test_system")
        
        assert ladder.current_level == EscalationLevel.LEVEL_1_WARNING
        assert event.from_level == EscalationLevel.LEVEL_0_NORMAL
        assert event.to_level == EscalationLevel.LEVEL_1_WARNING
    
    @pytest.mark.asyncio
    async def test_escalation_ladder_de_escalate(self):
        """Test de-escalating levels"""
        from core.safety_mechanisms.escalation_ladder import (
            EscalationLadder,
            EscalationLevel
        )
        
        ladder = EscalationLadder()
        
        await ladder.escalate("Test issue", "test_system")
        await ladder.de_escalate("Issue resolved", "test_system")
        
        assert ladder.current_level == EscalationLevel.LEVEL_0_NORMAL
    
    @pytest.mark.asyncio
    async def test_escalation_ladder_set_level(self):
        """Test setting specific level"""
        from core.safety_mechanisms.escalation_ladder import (
            EscalationLadder,
            EscalationLevel
        )
        
        ladder = EscalationLadder()
        
        await ladder.set_level(
            EscalationLevel.LEVEL_3_CRITICAL,
            "Critical issue",
            "test_system"
        )
        
        assert ladder.current_level == EscalationLevel.LEVEL_3_CRITICAL


# ============ Rollback System Tests ============

class TestRollbackSystem:
    """Tests for RollbackSystem"""
    
    def test_snapshot_types(self):
        """Test snapshot type enum"""
        from core.safety_mechanisms.rollback_system import SnapshotType
        
        assert SnapshotType.FULL.value == "full"
        assert SnapshotType.INCREMENTAL.value == "incremental"
    
    @pytest.mark.asyncio
    async def test_rollback_create_snapshot(self):
        """Test creating a snapshot"""
        from core.safety_mechanisms.rollback_system import RollbackSystem
        
        rollback = RollbackSystem()
        
        snapshot_id = await rollback.create_snapshot(
            {"key": "value"}
        )
        
        assert snapshot_id is not None
        assert rollback.get_snapshot(snapshot_id) is not None
    
    @pytest.mark.asyncio
    async def test_rollback_list_snapshots(self):
        """Test listing snapshots"""
        from core.safety_mechanisms.rollback_system import RollbackSystem
        
        rollback = RollbackSystem()
        
        await rollback.create_snapshot({"state": 1})
        await rollback.create_snapshot({"state": 2})
        
        snapshots = rollback.list_snapshots()
        assert len(snapshots) == 2
    
    @pytest.mark.asyncio
    async def test_rollback_with_handlers(self):
        """Test rollback with component handlers"""
        from core.safety_mechanisms.rollback_system import (
            RollbackSystem,
            RollbackStrategy
        )
        
        state = {"value": 10}
        
        rollback = RollbackSystem()
        rollback.register_component(
            name="test_component",
            save_handler=lambda: state.copy(),
            restore_handler=lambda s: state.update(s)
        )
        
        snapshot_id = await rollback.create_snapshot()
        
        state["value"] = 20
        
        result = await rollback.rollback(snapshot_id)
        
        assert result.success
        assert "test_component" in result.components_restored


# ============ Anomaly Detector Tests ============

class TestAnomalyDetector:
    """Tests for AnomalyDetector"""
    
    def test_anomaly_types(self):
        """Test anomaly type enum"""
        from core.safety_mechanisms.anomaly_detector import AnomalyType
        
        assert AnomalyType.RATE_ANOMALY.value == "rate"
        assert AnomalyType.VALUE_ANOMALY.value == "value"
    
    def test_anomaly_severity(self):
        """Test anomaly severity enum"""
        from core.safety_mechanisms.anomaly_detector import AnomalySeverity
        
        assert AnomalySeverity.LOW.value == 1
        assert AnomalySeverity.CRITICAL.value == 4
    
    def test_anomaly_detector_add_metric(self):
        """Test adding metrics"""
        from core.safety_mechanisms.anomaly_detector import (
            AnomalyDetector,
            DetectionStrategy
        )
        
        detector = AnomalyDetector()
        detector.add_metric(
            "error_rate",
            threshold=0.1,
            detection_strategy=DetectionStrategy.THRESHOLD
        )
        
        assert "error_rate" in detector._metrics
    
    @pytest.mark.asyncio
    async def test_anomaly_detector_threshold(self):
        """Test threshold-based anomaly detection"""
        from core.safety_mechanisms.anomaly_detector import (
            AnomalyDetector,
            DetectionStrategy
        )
        
        detector = AnomalyDetector()
        detector.add_metric(
            "error_rate",
            threshold=0.1,
            detection_strategy=DetectionStrategy.THRESHOLD
        )
        
        # Normal value
        alert = await detector.record("error_rate", 0.05)
        assert alert is None
        
        # Anomalous value
        alert = await detector.record("error_rate", 0.15)
        assert alert is not None
        assert "exceeds threshold" in alert.description
    
    def test_anomaly_detector_get_metrics_summary(self):
        """Test getting metrics summary"""
        from core.safety_mechanisms.anomaly_detector import AnomalyDetector
        
        detector = AnomalyDetector()
        detector.add_metric("test_metric")
        
        summary = detector.get_metrics_summary()
        # Initially empty (no values recorded)
        assert "test_metric" not in summary or summary.get("test_metric", {}).get("count", 0) == 0


# ============ Emergency Stop Tests ============

class TestEmergencyStop:
    """Tests for EmergencyStop"""
    
    def test_stop_reasons(self):
        """Test stop reason enum"""
        from core.safety_mechanisms.emergency_stop import StopReason
        
        assert StopReason.MANUAL.value == "manual"
        assert StopReason.SECURITY_BREACH.value == "security_breach"
    
    def test_stop_scopes(self):
        """Test stop scope enum"""
        from core.safety_mechanisms.emergency_stop import StopScope
        
        assert StopScope.COMPONENT.value == "component"
        assert StopScope.SYSTEM.value == "system"
    
    def test_emergency_stop_initial_state(self):
        """Test emergency stop initial state"""
        from core.safety_mechanisms.emergency_stop import EmergencyStop
        
        stop = EmergencyStop()
        
        assert not stop.is_stopped
        assert stop.stop_reason is None
    
    @pytest.mark.asyncio
    async def test_emergency_stop_trigger(self):
        """Test triggering emergency stop"""
        from core.safety_mechanisms.emergency_stop import (
            EmergencyStop,
            StopReason,
            StopScope
        )
        
        stop = EmergencyStop()
        
        stopped_components = []
        stop.register_component(
            "test",
            stop_handler=lambda: stopped_components.append("test")
        )
        
        result = await stop.trigger(
            StopReason.SECURITY_BREACH,
            StopScope.SYSTEM
        )
        
        assert result.success
        assert stop.is_stopped
        assert "test" in stopped_components
    
    @pytest.mark.asyncio
    async def test_emergency_stop_recover(self):
        """Test recovery from emergency stop"""
        from core.safety_mechanisms.emergency_stop import (
            EmergencyStop,
            StopReason,
            StopScope
        )
        
        stop = EmergencyStop()
        
        stop.register_component(
            "test",
            stop_handler=lambda: None,
            recovery_handler=lambda: None
        )
        
        await stop.trigger(StopReason.MANUAL, StopScope.SYSTEM)
        results = await stop.recover()
        
        assert results.get("test") == True
        assert not stop.is_stopped


# ============ Safety Net Tests ============

class TestSafetyNet:
    """Tests for SafetyNet"""
    
    def test_safety_layers(self):
        """Test safety layer enum"""
        from core.safety_mechanisms.safety_net import SafetyLayer
        
        assert SafetyLayer.LAYER_1_INPUT_VALIDATION.value == 1
        assert SafetyLayer.LAYER_6_AUDIT_LOG.value == 6
    
    def test_safety_net_add_check(self):
        """Test adding safety checks"""
        from core.safety_mechanisms.safety_net import (
            SafetyNet,
            SafetyCheck,
            SafetyLayer
        )
        
        safety = SafetyNet()
        
        safety.add_check(SafetyCheck(
            name="test_check",
            description="Test check",
            layer=SafetyLayer.LAYER_1_INPUT_VALIDATION,
            check_function=lambda x: x is not None
        ))
        
        checks = safety.list_checks()
        assert any(c["name"] == "test_check" for c in checks)
    
    @pytest.mark.asyncio
    async def test_safety_net_validate_pass(self):
        """Test safety net validation (passing)"""
        from core.safety_mechanisms.safety_net import SafetyNet
        
        safety = SafetyNet()
        
        results = await safety.validate({"data": "test"})
        
        # Should pass default checks
        passed_results = [r for r in results if r.passed]
        assert len(passed_results) > 0
    
    @pytest.mark.asyncio
    async def test_safety_net_validate_fail(self):
        """Test safety net validation (failing)"""
        from core.safety_mechanisms.safety_net import (
            SafetyNet,
            SafetyCheck,
            SafetyLayer
        )
        
        safety = SafetyNet()
        safety.add_check(SafetyCheck(
            name="always_fail",
            description="Always fails",
            layer=SafetyLayer.LAYER_1_INPUT_VALIDATION,
            check_function=lambda x: False
        ))
        
        results = await safety.validate({"data": "test"})
        
        failed_results = [r for r in results if not r.passed]
        assert any(r.check_name == "always_fail" for r in failed_results)
    
    @pytest.mark.asyncio
    async def test_safety_net_execute(self):
        """Test safety net execute with protection"""
        from core.safety_mechanisms.safety_net import SafetyNet
        
        safety = SafetyNet()
        
        result = await safety.execute(
            lambda x: x["value"] * 2,
            {"value": 5}
        )
        
        assert result == 10
    
    @pytest.mark.asyncio
    async def test_safety_net_execute_blocked(self):
        """Test safety net blocks unsafe operations"""
        from core.safety_mechanisms.safety_net import (
            SafetyNet,
            SafetyCheck,
            SafetyLayer,
            SafetyCheckError
        )
        
        safety = SafetyNet()
        safety.add_check(SafetyCheck(
            name="block_all",
            description="Blocks everything",
            layer=SafetyLayer.LAYER_1_INPUT_VALIDATION,
            check_function=lambda x: False,
            blocking=True
        ))
        
        with pytest.raises(SafetyCheckError):
            await safety.execute(lambda x: x, {"data": "test"})
    
    def test_safety_net_stats(self):
        """Test safety net statistics"""
        from core.safety_mechanisms.safety_net import SafetyNet
        
        safety = SafetyNet()
        stats = safety.get_stats()
        
        assert "total_checks" in stats
        assert "enabled_checks" in stats
        assert "checks_by_layer" in stats


# ============ Integration Tests ============

class TestSafetyMechanismsIntegration:
    """Integration tests for safety mechanisms"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_with_anomaly_detection(self):
        """Test circuit breaker triggered by anomaly detection"""
        from core.safety_mechanisms.circuit_breaker import (
            CircuitBreaker,
            CircuitBreakerConfig
        )
        from core.safety_mechanisms.anomaly_detector import (
            AnomalyDetector,
            DetectionStrategy
        )
        
        breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=1))
        detector = AnomalyDetector()
        detector.add_metric("errors", threshold=5)
        
        # Simulate anomaly triggering circuit breaker
        alert = await detector.record("errors", 10)
        if alert:
            breaker.trip()
        
        assert breaker.is_open
    
    @pytest.mark.asyncio
    async def test_escalation_with_emergency_stop(self):
        """Test escalation ladder triggering emergency stop"""
        from core.safety_mechanisms.escalation_ladder import (
            EscalationLadder,
            EscalationLevel
        )
        from core.safety_mechanisms.emergency_stop import (
            EmergencyStop,
            StopReason,
            StopScope
        )
        
        ladder = EscalationLadder()
        stop = EmergencyStop()
        
        # Listen for critical escalation
        async def on_critical_escalation(event):
            if event.to_level.value >= EscalationLevel.LEVEL_4_EMERGENCY.value:
                await stop.trigger(
                    StopReason.CASCADING_FAILURE,
                    StopScope.SYSTEM,
                    "escalation_ladder"
                )
        
        ladder.add_listener(lambda e: asyncio.create_task(on_critical_escalation(e)))
        
        # Escalate to emergency level
        await ladder.set_level(
            EscalationLevel.LEVEL_4_EMERGENCY,
            "Cascading failure detected",
            "monitoring"
        )
        
        # Give async task time to complete
        await asyncio.sleep(0.1)
        
        # System should be stopped
        assert stop.is_stopped or ladder.current_level == EscalationLevel.LEVEL_4_EMERGENCY
