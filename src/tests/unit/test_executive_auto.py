# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh Executive Auto Controller Tests
#                    自動化執行長控制器測試
# ═══════════════════════════════════════════════════════════════════════════════
"""
Tests for the Executive Autonomy Controller.

Tests the complete autonomous executive loop:
perceive → reason → policy_gate → execute → prove → heal → evolve
"""

import sys
from pathlib import Path

import pytest

# Add runtime to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.mind_matrix.executive_auto import ExecutiveAutoController


class TestExecutiveAutoController:
    """Tests for ExecutiveAutoController initialization and configuration."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_initialization(self, controller: ExecutiveAutoController) -> None:
        """Test controller initializes correctly."""
        assert controller.mm is not None
        assert controller.audit_log == []
        assert controller.max_heal_attempts == 3

    def test_custom_heal_attempts(self) -> None:
        """Test controller with custom max_heal_attempts."""
        controller = ExecutiveAutoController(max_heal_attempts=5)
        assert controller.max_heal_attempts == 5


class TestPerceiveLayer:
    """Tests for L1 Perception Layer."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_perceive_default_signals(self, controller: ExecutiveAutoController) -> None:
        """Test perception with default signals."""
        signals = controller.perceive()

        assert "latency_ms" in signals
        assert "error_rate" in signals
        assert "deploy_pending" in signals
        assert "policy_violations" in signals

    def test_perceive_custom_signals(self, controller: ExecutiveAutoController) -> None:
        """Test perception with custom signals."""
        custom_signals = {
            "latency_ms": 500,
            "error_rate": 0.1,
            "deploy_pending": False,
        }

        signals = controller.perceive(custom_signals)

        assert signals["latency_ms"] == 500
        assert signals["error_rate"] == 0.1
        assert signals["deploy_pending"] is False

    def test_perceive_creates_evidence(self, controller: ExecutiveAutoController) -> None:
        """Test that perception creates audit evidence."""
        controller.perceive()

        assert len(controller.audit_log) == 1
        assert controller.audit_log[0]["stage"] == "perceive"


class TestReasonLayer:
    """Tests for L2 Reasoning Layer."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_reason_with_deploy_pending(self, controller: ExecutiveAutoController) -> None:
        """Test reasoning suggests progressive_deploy when deploy_pending."""
        signals = {"deploy_pending": True, "error_rate": 0.01}

        plan = controller.reason(signals)

        actions = [d["action"] for d in plan["decisions"]]
        assert "progressive_deploy" in actions

    def test_reason_with_high_error_rate(self, controller: ExecutiveAutoController) -> None:
        """Test reasoning suggests rollback_and_rerun on high error rate."""
        signals = {"deploy_pending": False, "error_rate": 0.1}

        plan = controller.reason(signals)

        actions = [d["action"] for d in plan["decisions"]]
        assert "rollback_and_rerun" in actions

    def test_reason_with_elevated_error_rate(self, controller: ExecutiveAutoController) -> None:
        """Test reasoning suggests health_check on elevated error rate."""
        signals = {"deploy_pending": False, "error_rate": 0.04}

        plan = controller.reason(signals)

        actions = [d["action"] for d in plan["decisions"]]
        assert "health_check" in actions

    def test_reason_with_high_cpu(self, controller: ExecutiveAutoController) -> None:
        """Test reasoning suggests scale_up on high CPU."""
        signals = {"deploy_pending": False, "error_rate": 0.01, "cpu_utilization": 0.9}

        plan = controller.reason(signals)

        actions = [d["action"] for d in plan["decisions"]]
        assert "scale_up" in actions

    def test_reason_with_low_cpu(self, controller: ExecutiveAutoController) -> None:
        """Test reasoning suggests scale_down on low CPU."""
        signals = {"deploy_pending": False, "error_rate": 0.01, "cpu_utilization": 0.2}

        plan = controller.reason(signals)

        actions = [d["action"] for d in plan["decisions"]]
        assert "scale_down" in actions

    def test_reason_observe_only(self, controller: ExecutiveAutoController) -> None:
        """Test reasoning suggests observe_only when system is stable."""
        signals = {
            "deploy_pending": False,
            "error_rate": 0.01,
            "cpu_utilization": 0.5,
            "circuit_breaker_open": False,
        }

        plan = controller.reason(signals)

        actions = [d["action"] for d in plan["decisions"]]
        assert "observe_only" in actions

    def test_reason_creates_evidence(self, controller: ExecutiveAutoController) -> None:
        """Test that reasoning creates audit evidence."""
        signals = {"deploy_pending": False, "error_rate": 0.01}
        controller.reason(signals)

        assert any(ev["stage"] == "reason" for ev in controller.audit_log)


class TestPolicyGate:
    """Tests for L3 Policy Gate."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_policy_gate_allows_valid_actions(self, controller: ExecutiveAutoController) -> None:
        """Test policy gate allows whitelisted actions."""
        plan = {
            "decisions": [
                {"action": "progressive_deploy", "risk": 0.3},
                {"action": "observe_only", "risk": 0.1},
            ],
            "timestamp": "2024-01-01T00:00:00",
        }

        gated = controller.policy_gate(plan)

        assert len(gated["decisions"]) == 2
        assert gated["policy_applied"] is True

    def test_policy_gate_blocks_invalid_actions(self, controller: ExecutiveAutoController) -> None:
        """Test policy gate blocks non-whitelisted actions."""
        plan = {
            "decisions": [
                {"action": "progressive_deploy", "risk": 0.3},
                {"action": "dangerous_action", "risk": 0.9},
            ],
            "timestamp": "2024-01-01T00:00:00",
        }

        gated = controller.policy_gate(plan)

        actions = [d["action"] for d in gated["decisions"]]
        assert "progressive_deploy" in actions
        assert "dangerous_action" not in actions

    def test_policy_gate_creates_evidence(self, controller: ExecutiveAutoController) -> None:
        """Test policy gate creates audit evidence."""
        plan = {"decisions": [], "timestamp": "2024-01-01T00:00:00"}
        controller.policy_gate(plan)

        assert any(ev["stage"] == "policy_gate" for ev in controller.audit_log)


class TestExecuteLayer:
    """Tests for L4 Execution Layer."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_execute_progressive_deploy(self, controller: ExecutiveAutoController) -> None:
        """Test execution of progressive_deploy action."""
        gated_plan = {
            "decisions": [{"action": "progressive_deploy", "risk": 0.3}],
        }

        result = controller.execute(gated_plan)

        assert len(result["results"]) >= 1
        assert any(r["payload"]["op"] == "deploy" for r in result["results"])

    def test_execute_rollback_and_rerun(self, controller: ExecutiveAutoController) -> None:
        """Test execution of rollback_and_rerun action."""
        gated_plan = {
            "decisions": [{"action": "rollback_and_rerun", "risk": 0.2}],
        }

        result = controller.execute(gated_plan)

        # Should have both rollback and rerun operations
        ops = [r["payload"]["op"] for r in result["results"] if "payload" in r]
        assert "rollback" in ops
        assert "rerun" in ops

    def test_execute_observe_only(self, controller: ExecutiveAutoController) -> None:
        """Test execution of observe_only action."""
        gated_plan = {
            "decisions": [{"action": "observe_only", "risk": 0.1}],
        }

        result = controller.execute(gated_plan)

        assert len(result["results"]) == 1
        assert result["results"][0]["status"] == "noop"

    def test_execute_creates_evidence(self, controller: ExecutiveAutoController) -> None:
        """Test execution creates audit evidence."""
        gated_plan = {"decisions": [{"action": "observe_only", "risk": 0.1}]}
        controller.execute(gated_plan)

        assert any(ev["stage"] == "execute" for ev in controller.audit_log)


class TestProveAndFreeze:
    """Tests for L5/L7 Evidence Freezing & Checkpointing."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_prove_and_freeze_creates_checkpoint(
        self, controller: ExecutiveAutoController
    ) -> None:
        """Test checkpoint creation."""
        exec_result = {"results": [{"status": "success"}]}

        checkpoint = controller.prove_and_freeze(exec_result)

        assert checkpoint["checkpoint"] is True
        assert "checkpoint_id" in checkpoint
        assert checkpoint["rollback_available"] is True

    def test_prove_and_freeze_creates_evidence(
        self, controller: ExecutiveAutoController
    ) -> None:
        """Test evidence is recorded for checkpoint."""
        exec_result = {"results": []}
        controller.prove_and_freeze(exec_result)

        evidence = [ev for ev in controller.audit_log if ev["stage"] == "history_freeze"]
        assert len(evidence) == 1
        assert evidence[0]["data"]["checkpoint"] is True


class TestHealLoop:
    """Tests for L6 Self-Healing Loop."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_heal_loop_no_failures(self, controller: ExecutiveAutoController) -> None:
        """Test heal loop with no failures."""
        exec_result = {"results": [{"status": "success"}]}

        outcome = controller.heal_loop(exec_result)

        assert outcome["autofix"] is False
        assert outcome["failures_detected"] == 0

    def test_heal_loop_with_failures(self, controller: ExecutiveAutoController) -> None:
        """Test heal loop triggers autofix on failures."""
        exec_result = {"results": [{"status": "failed"}]}

        outcome = controller.heal_loop(exec_result)

        assert outcome["autofix"] is True
        assert outcome["pr_generated"] is True
        assert outcome["rerun"] is True
        assert outcome["failures_detected"] == 1

    def test_heal_loop_escalation(self, controller: ExecutiveAutoController) -> None:
        """Test heal loop escalates after max attempts."""
        controller.max_heal_attempts = 2
        exec_result = {"results": [{"status": "failed"}]}

        # First two attempts should not escalate
        controller.heal_loop(exec_result)
        controller.heal_loop(exec_result)

        # Third attempt should escalate
        outcome = controller.heal_loop(exec_result)

        assert outcome["escalated"] is True

    def test_heal_loop_resets_on_success(self, controller: ExecutiveAutoController) -> None:
        """Test heal counter resets on success."""
        controller._heal_attempt_count = 2

        exec_result = {"results": [{"status": "success"}]}
        controller.heal_loop(exec_result)

        assert controller._heal_attempt_count == 0


class TestEvolveLayer:
    """Tests for L8 Evolution Layer."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_evolve_records_metrics(self, controller: ExecutiveAutoController) -> None:
        """Test evolution records metrics."""
        metrics = {"latency_ms": 100, "error_rate": 0.01}

        result = controller.evolve(metrics)

        assert result["metrics"] == metrics
        assert result["learning_target"] == "policy_weights"

    def test_evolve_creates_evidence(self, controller: ExecutiveAutoController) -> None:
        """Test evolution creates audit evidence."""
        controller.evolve({"latency_ms": 100})

        assert any(ev["stage"] == "evolve" for ev in controller.audit_log)


class TestAutonomousCycle:
    """Tests for the complete autonomous cycle."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_run_once_complete_cycle(self, controller: ExecutiveAutoController) -> None:
        """Test complete autonomous cycle execution."""
        report = controller.run_once()

        assert "signals" in report
        assert "plan" in report
        assert "gated" in report
        assert "exec" in report
        assert "checkpoint" in report
        assert "heal" in report
        assert "evolve" in report
        assert "audit" in report
        assert report["cycle_complete"] is True

    def test_run_once_audit_coverage(self, controller: ExecutiveAutoController) -> None:
        """Test audit log covers all stages."""
        report = controller.run_once()

        stages = {ev["stage"] for ev in report["audit"]}

        # Should have evidence from each layer
        assert "perceive" in stages
        assert "reason" in stages
        assert "policy_gate" in stages
        assert "execute" in stages
        assert "history_freeze" in stages
        assert "heal_loop" in stages
        assert "evolve" in stages

    def test_run_once_minimum_audit_events(self, controller: ExecutiveAutoController) -> None:
        """Test minimum audit events are generated."""
        report = controller.run_once()

        # Should have at least events from 7 main stages
        assert len(report["audit"]) >= 7

    def test_run_once_with_custom_signals(self, controller: ExecutiveAutoController) -> None:
        """Test autonomous cycle with custom signals."""
        custom_signals = {
            "latency_ms": 500,
            "error_rate": 0.1,
            "deploy_pending": False,
            "cpu_utilization": 0.5,
        }

        report = controller.run_once(signals=custom_signals)

        assert report["signals"]["latency_ms"] == 500
        assert report["signals"]["error_rate"] == 0.1


class TestAuditLog:
    """Tests for audit log functionality."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_get_audit_log_returns_copy(self, controller: ExecutiveAutoController) -> None:
        """Test get_audit_log returns a copy."""
        controller.perceive()

        log = controller.get_audit_log()
        log.clear()

        # Original should not be affected
        assert len(controller.audit_log) == 1

    def test_clear_audit_log(self, controller: ExecutiveAutoController) -> None:
        """Test clearing audit log."""
        controller.perceive()
        controller.clear_audit_log()

        assert len(controller.audit_log) == 0
        assert controller._heal_attempt_count == 0


class TestToolPipelineValidation:
    """Tests for tool pipeline validation."""

    @pytest.fixture
    def controller(self) -> ExecutiveAutoController:
        """Create ExecutiveAutoController instance."""
        return ExecutiveAutoController()

    def test_run_tool_valid_stage(self, controller: ExecutiveAutoController) -> None:
        """Test running tool with valid stage."""
        result = controller._run_tool("tool_execution", {"op": "test"})

        assert result["status"] == "success"
        assert result["stage"] == "tool_execution"

    def test_run_tool_invalid_stage(self, controller: ExecutiveAutoController) -> None:
        """Test running tool with invalid stage raises error."""
        with pytest.raises(AssertionError, match="invalid_stage"):
            controller._run_tool("invalid_stage", {"op": "test"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
