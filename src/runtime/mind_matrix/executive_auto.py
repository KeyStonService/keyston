# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh Executive Autonomy Controller
#                    自動化執行長控制器 - 決策→執行→證明→修復→演化 全自動
# ═══════════════════════════════════════════════════════════════════════════════
"""
Executive Autonomy Controller Module.

自動化執行長控制器：實現決策→執行→證明→修復→演化的完整自動化閉環。
This module provides the ExecutiveAutoController class that implements
a fully autonomous executive loop: perceive → reason → policy_gate → execute
→ prove → heal → evolve.

Architecture layers:
- L1 感知 (Perception): Telemetry, drift detection, anomaly identification
- L2 推理 (Reasoning): Causal graph building, risk scoring, decision generation
- L3 策略合成 (Policy Synthesis): Governance alignment, action filtering
- L4 執行協作 (Execution): Multi-agent coordination via tool pipeline
- L5 證據固化 (Evidence Freezing): Audit chain, SLSA, SBOM, signature
- L6 自愈閉環 (Self-Healing): IssueOps (/autofix, /rerun, /assign, /close)
- L7 驗證與回滾 (Verification & Rollback): Checkpoint generation, auto-rollback
- L8 演化學習 (Evolution): Meta-RL/MAML-RL driven policy improvement
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

# Support both absolute and relative imports
try:
    from runtime.mind_matrix.main import MindMatrix
except ImportError:
    from main import MindMatrix


class ExecutiveAutoController:
    """
    自動化執行長控制器 (Executive Autonomy Controller).

    Implements a fully autonomous executive loop that orchestrates:
    - Perception of system signals and metrics
    - Reasoning and decision candidate generation
    - Policy gate alignment with governance principles
    - Execution via the 8-stage tool pipeline
    - Evidence freezing and checkpoint generation
    - Self-healing via IssueOps automation
    - Evolution through performance-driven learning

    All operations are recorded in an immutable audit log for traceability.
    """

    # Allowed actions whitelist for policy gate
    ALLOWED_ACTIONS = frozenset({
        "progressive_deploy",
        "rollback_and_rerun",
        "observe_only",
        "scale_up",
        "scale_down",
        "circuit_break",
        "health_check",
    })

    # Required governance principles
    REQUIRED_PRINCIPLES = frozenset({
        "depth_first",
        "verifiability_first",
        "security_first",
        "automation_first",
        "traceability_first",
    })

    def __init__(
        self,
        topology_file: Optional[str] = None,
        max_heal_attempts: int = 3,
    ) -> None:
        """
        初始化自動化執行長控制器 (Initialize Executive Auto Controller).

        Args:
            topology_file: Path to the topology configuration file.
                          Defaults to "config/topology-mind-matrix.yaml".
            max_heal_attempts: Maximum number of self-healing attempts before escalation.
        """
        if topology_file is None:
            # Try to find config relative to current directory or module location
            possible_paths = [
                Path("config/topology-mind-matrix.yaml"),
                Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml",
            ]
            for path in possible_paths:
                if path.exists():
                    topology_file = str(path)
                    break
            else:
                topology_file = "config/topology-mind-matrix.yaml"

        try:
            with open(topology_file, encoding="utf-8") as f:
                topology = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Topology configuration file not found: {topology_file}"
            ) from e
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in topology file: {topology_file}") from e

        self.mm = MindMatrix(topology)
        self.max_heal_attempts = max_heal_attempts
        self.audit_log: list[dict[str, Any]] = []
        self._heal_attempt_count = 0

    def perceive(self, signals: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        L1 感知：聚合遙測/健康/異常指標 (Perception Layer).

        Aggregates telemetry, health metrics, and anomaly indicators.
        In production, this would connect to monitoring agents (Prometheus, etc.).

        Args:
            signals: Optional override signals for testing.
                    If None, uses default demonstration signals.

        Returns:
            Dictionary containing system signals and metrics.
        """
        if signals is None:
            # Default demonstration signals (in production, fetch from monitoring)
            signals = {
                "latency_ms": 120,
                "error_rate": 0.02,
                "deploy_pending": True,
                "policy_violations": 0,
                "cpu_utilization": 0.65,
                "memory_utilization": 0.70,
                "active_connections": 1500,
                "circuit_breaker_open": False,
            }

        self._evidence("perceive", signals)
        return signals

    def reason(self, signals: dict[str, Any]) -> dict[str, Any]:
        """
        L2 推理：生成決策候選與風險分數 (Reasoning Layer).

        Generates decision candidates based on system signals and risk scoring.
        Uses rule-based logic (in production, could use ML models).

        Args:
            signals: System signals from the perception layer.

        Returns:
            Plan dictionary containing decisions with risk scores.
        """
        decisions: list[dict[str, Any]] = []

        # Rule-based decision generation
        if signals.get("deploy_pending"):
            decisions.append({
                "action": "progressive_deploy",
                "risk": 0.3,
                "reason": "Pending deployment detected",
            })

        error_rate = signals.get("error_rate", 0)
        if error_rate > 0.05:
            decisions.append({
                "action": "rollback_and_rerun",
                "risk": 0.2,
                "reason": f"High error rate: {error_rate:.2%}",
            })
        elif error_rate > 0.03:
            decisions.append({
                "action": "health_check",
                "risk": 0.1,
                "reason": f"Elevated error rate: {error_rate:.2%}",
            })

        cpu_util = signals.get("cpu_utilization", 0)
        if cpu_util > 0.85:
            decisions.append({
                "action": "scale_up",
                "risk": 0.2,
                "reason": f"High CPU utilization: {cpu_util:.2%}",
            })
        elif cpu_util < 0.3:
            decisions.append({
                "action": "scale_down",
                "risk": 0.1,
                "reason": f"Low CPU utilization: {cpu_util:.2%}",
            })

        if signals.get("circuit_breaker_open"):
            decisions.append({
                "action": "circuit_break",
                "risk": 0.4,
                "reason": "Circuit breaker is open",
            })

        # Default to observation if no actions needed
        if not decisions:
            decisions.append({
                "action": "observe_only",
                "risk": 0.1,
                "reason": "System stable, no action required",
            })

        plan = {
            "decisions": decisions,
            "timestamp": datetime.utcnow().isoformat(),
            "signal_summary": {
                "error_rate": error_rate,
                "cpu_utilization": cpu_util,
                "deploy_pending": signals.get("deploy_pending", False),
            },
        }

        self._evidence("reason", plan)
        return plan

    def policy_gate(self, plan: dict[str, Any]) -> dict[str, Any]:
        """
        L3 策略閘：對齊治理原則，拒絕不合規操作 (Policy Gate).

        Validates plan against governance principles and filters
        any non-compliant actions.

        Args:
            plan: Plan dictionary from the reasoning layer.

        Returns:
            Gated plan with only compliant actions.

        Raises:
            AssertionError: If governance principles are not fully covered.
        """
        # Verify governance principles coverage
        gp = set(self.mm.model.governance_principles)
        missing = self.REQUIRED_PRINCIPLES - gp
        if missing:
            raise AssertionError(f"治理原則未覆蓋: {missing}")

        # Filter to only allowed actions
        filtered_decisions = [
            d for d in plan["decisions"]
            if d["action"] in self.ALLOWED_ACTIONS
        ]

        # Log any blocked actions
        blocked = [
            d for d in plan["decisions"]
            if d["action"] not in self.ALLOWED_ACTIONS
        ]
        if blocked:
            self._evidence("policy_blocked", {"blocked_actions": blocked})

        gated = {
            **plan,
            "decisions": filtered_decisions,
            "policy_applied": True,
            "governance_version": self.mm.model.version,
        }

        self._evidence("policy_gate", gated)
        return gated

    def execute(self, gated_plan: dict[str, Any]) -> dict[str, Any]:
        """
        L4 執行：映射到工具管線 (Execution Layer).

        Maps decisions to tool pipeline stages and executes them.
        In production, this would connect to actual execution backends
        (Shell/REST/gRPC/MQ).

        Args:
            gated_plan: Policy-approved plan from the policy gate.

        Returns:
            Execution results dictionary.
        """
        results: list[dict[str, Any]] = []

        for decision in gated_plan["decisions"]:
            action = decision["action"]

            if action == "progressive_deploy":
                results.append(self._run_tool(
                    "tool_execution",
                    {"op": "deploy", "mode": "rolling", "canary_percent": 10},
                ))
            elif action == "rollback_and_rerun":
                results.append(self._run_tool(
                    "tool_execution",
                    {"op": "rollback", "target": "previous_stable"},
                ))
                results.append(self._run_tool(
                    "tool_execution",
                    {"op": "rerun", "pipeline": "validation"},
                ))
            elif action == "scale_up":
                results.append(self._run_tool(
                    "tool_execution",
                    {"op": "scale", "direction": "up", "increment": 2},
                ))
            elif action == "scale_down":
                results.append(self._run_tool(
                    "tool_execution",
                    {"op": "scale", "direction": "down", "decrement": 1},
                ))
            elif action == "circuit_break":
                results.append(self._run_tool(
                    "tool_execution",
                    {"op": "circuit_break", "action": "isolate"},
                ))
            elif action == "health_check":
                results.append(self._run_tool(
                    "tool_execution",
                    {"op": "health_check", "deep": True},
                ))
            else:  # observe_only or unknown
                results.append({
                    "op": "observe",
                    "status": "noop",
                    "timestamp": datetime.utcnow().isoformat(),
                })

        exec_result = {
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
            "decisions_executed": len(gated_plan["decisions"]),
        }

        self._evidence("execute", exec_result)
        return exec_result

    def prove_and_freeze(self, exec_result: dict[str, Any]) -> dict[str, Any]:
        """
        L5/L7 證據固化與回滾點生成 (Evidence Freezing & Checkpointing).

        Creates an immutable checkpoint and freezes execution evidence
        for audit trail and potential rollback.

        Args:
            exec_result: Execution results from the execution layer.

        Returns:
            Checkpoint metadata.
        """
        checkpoint = {
            "checkpoint": True,
            "checkpoint_id": f"cp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "result": exec_result,
            "timestamp": datetime.utcnow().isoformat(),
            "slsa_level": self.mm.get_slsa_level(),
            "rollback_available": True,
        }

        self._evidence("history_freeze", checkpoint)
        return checkpoint

    def heal_loop(self, exec_result: dict[str, Any]) -> dict[str, Any]:
        """
        L6 自癒：若執行失敗則觸發自動修復 (Self-Healing Loop).

        Implements IssueOps automation:
        - /autofix: Generate fix and submit PR
        - /rerun: Re-execute validation pipeline
        - /assign: Auto-assign responsibility (if human oversight needed)
        - /close: Auto-close on successful verification

        Args:
            exec_result: Execution results from the execution layer.

        Returns:
            Healing outcome dictionary.
        """
        failures = [
            r for r in exec_result["results"]
            if r.get("status") == "failed"
        ]

        outcome = {
            "autofix": False,
            "rerun": False,
            "pr_generated": False,
            "escalated": False,
            "failures_detected": len(failures),
            "timestamp": datetime.utcnow().isoformat(),
        }

        if failures:
            self._heal_attempt_count += 1

            if self._heal_attempt_count > self.max_heal_attempts:
                # Escalate after max attempts
                outcome["escalated"] = True
                self._evidence("heal_escalation", {
                    "reason": f"Max heal attempts ({self.max_heal_attempts}) exceeded",
                    "failures": failures,
                })
            else:
                # Attempt auto-fix
                outcome["autofix"] = True
                self._evidence("issueops_autofix", {
                    "attempt": self._heal_attempt_count,
                    "failure_count": len(failures),
                    "failures": failures,
                })

                # Generate fix PR (simulated)
                outcome["pr_generated"] = True
                self._evidence("issueops_pr", {
                    "pr": f"fix-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    "status": "generated",
                })

                # Rerun validation
                outcome["rerun"] = True
                self._evidence("issueops_rerun", {
                    "pipeline": "validation",
                    "status": "triggered",
                })
        else:
            # Reset heal counter on success
            self._heal_attempt_count = 0

        self._evidence("heal_loop", outcome)
        return outcome

    def evolve(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """
        L8 演化：將績效送入策略學習 (Evolution Layer).

        Records performance metrics for strategy learning.
        In production, this would feed into Meta-RL/MAML-RL modules
        for policy improvement.

        Args:
            metrics: Performance metrics from the current cycle.

        Returns:
            Evolution outcome dictionary.
        """
        evolution_data = {
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
            "learning_target": "policy_weights",
            "feedback_type": "performance",
        }

        self._evidence("evolve", evolution_data)
        return evolution_data

    def run_once(
        self,
        signals: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        單次完整自動執行長閉環 (Single Autonomous Executive Cycle).

        Executes a complete autonomous cycle:
        perceive → reason → policy_gate → execute → prove → heal → evolve

        Args:
            signals: Optional override signals for testing.

        Returns:
            Complete cycle report including all stages and audit log.
        """
        s = self.perceive(signals)
        p = self.reason(s)
        g = self.policy_gate(p)
        e = self.execute(g)
        checkpoint = self.prove_and_freeze(e)
        h = self.heal_loop(e)
        ev = self.evolve({
            "latency_ms": s.get("latency_ms", 0),
            "error_rate": s.get("error_rate", 0),
            "cpu_utilization": s.get("cpu_utilization", 0),
            "decisions_made": len(g["decisions"]),
            "executions_success": sum(
                1 for r in e["results"] if r.get("status") == "success"
            ),
        })

        return {
            "signals": s,
            "plan": p,
            "gated": g,
            "exec": e,
            "checkpoint": checkpoint,
            "heal": h,
            "evolve": ev,
            "audit": self.audit_log.copy(),
            "cycle_complete": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_audit_log(self) -> list[dict[str, Any]]:
        """
        取得審計日誌 (Get Audit Log).

        Returns:
            Copy of the immutable audit log.
        """
        return self.audit_log.copy()

    def clear_audit_log(self) -> None:
        """
        清除審計日誌（用於測試）(Clear Audit Log - for testing).

        WARNING: Only use in test environments.
        """
        self.audit_log.clear()
        self._heal_attempt_count = 0

    # --- Internal Tools & Audit ---

    def _run_tool(self, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        內部工具執行 (Internal Tool Execution).

        Validates stage against tool pipeline and simulates execution.

        Args:
            stage: Tool pipeline stage name.
            payload: Execution payload.

        Returns:
            Tool execution result.

        Raises:
            AssertionError: If stage is not in the tool pipeline.
        """
        valid_stages = self.mm.get_tool_pipeline_stages()
        if stage not in valid_stages:
            raise AssertionError(f"工具管線階段不存在: {stage}")

        # Simulate tool execution (in production, map to actual backends)
        result = {
            "stage": stage,
            "payload": payload,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._evidence(f"tool_{stage}", result)
        return result

    def _evidence(self, stage: str, data: dict[str, Any]) -> None:
        """
        記錄審計證據 (Record Audit Evidence).

        Appends evidence to the immutable audit log.

        Args:
            stage: Stage name for the evidence.
            data: Evidence data to record.
        """
        self.audit_log.append({
            "stage": stage,
            "data": data,
            "ts": datetime.utcnow().isoformat(),
        })
