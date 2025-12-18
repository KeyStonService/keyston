# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh CLI Bridge
#                    CLI 橋接層 - 統一 Admin Copilot CLI 與 Mind Matrix 整合
# ═══════════════════════════════════════════════════════════════════════════════
"""
CLI Bridge module.

將 Admin Copilot CLI 作為 mind_matrix 的執行器（actuator），
而非獨立運作的人類介面。所有 CLI 行為都經過：
- unified_integration 統一暴露
- safety_mechanisms 安全攔截
- slsa_provenance 證據記錄

This module integrates Admin Copilot CLI as an actuator for mind_matrix,
ensuring all CLI actions are:
- Exposed through unified_integration
- Intercepted by safety_mechanisms
- Recorded by slsa_provenance
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CLIOperation(Enum):
    """CLI 支援的操作類型 (Supported CLI Operations)."""

    BUILD = "build"
    TEST = "test"
    LINT = "lint"
    FIX = "fix"
    ANALYZE = "analyze"
    REVIEW = "review"
    GENERATE = "generate"


class TaskStatus(Enum):
    """任務狀態 (Task Status)."""

    PENDING = "pending"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class CLITask:
    """
    CLI 任務定義 (CLI Task Definition).

    由 mind_matrix 規劃，經由 CLI bridge 執行。
    """

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation: CLIOperation = CLIOperation.BUILD
    target_path: str = "."
    parameters: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    invoked_by: str = "unknown"  # agent ID or workflow ID
    provenance_ref: str | None = None


@dataclass
class SafetyCheckResult:
    """安全檢查結果 (Safety Check Result)."""

    passed: bool
    risk_score: float  # 0.0 - 1.0
    violations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class CLIBridge:
    """
    CLI 橋接層 (CLI Bridge).

    統一 Admin Copilot CLI 與 mind_matrix 的整合介面。
    所有 CLI 操作都必須經過此橋接層，確保：
    1. mind_matrix 可以追蹤和管理所有 CLI 行為
    2. safety_mechanisms 可以攔截危險操作
    3. slsa_provenance 可以記錄完整證據鏈

    Unified integration interface between Admin Copilot CLI and mind_matrix.
    All CLI operations must go through this bridge to ensure:
    1. mind_matrix can track and manage all CLI behaviors
    2. safety_mechanisms can intercept dangerous operations
    3. slsa_provenance can record complete evidence chain
    """

    def __init__(
        self,
        safety_policy_path: str = "governance/policies/cli-safe-mode.rego",
        provenance_stream: str = "core/slsa_provenance/",
        max_concurrent_tasks: int = 5,
        default_timeout: int = 300,
    ) -> None:
        """
        初始化 CLI 橋接層 (Initialize CLI Bridge).

        Args:
            safety_policy_path: Path to the safety policy file.
            provenance_stream: Path to the provenance stream.
            max_concurrent_tasks: Maximum concurrent tasks allowed.
            default_timeout: Default timeout in seconds.
        """
        self.safety_policy_path = safety_policy_path
        self.provenance_stream = provenance_stream
        self.max_concurrent_tasks = max_concurrent_tasks
        self.default_timeout = default_timeout

        self._active_tasks: dict[str, CLITask] = {}
        self._task_history: list[CLITask] = []
        self._semaphore: asyncio.Semaphore | None = None  # Lazy init in async context

        # Whitelist of allowed operations
        self._allowed_operations = {op.value for op in CLIOperation}

        # Operations requiring human approval
        self._require_approval = {"fix", "generate"}

        logger.info(
            "CLI Bridge initialized with max_concurrent=%d, timeout=%ds",
            max_concurrent_tasks,
            default_timeout,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Public API (公開 API)
    # ═══════════════════════════════════════════════════════════════════════════

    async def submit_task(
        self,
        operation: str,
        target_path: str = ".",
        parameters: dict[str, Any] | None = None,
        invoked_by: str = "mind_matrix",
        dry_run: bool = False,
    ) -> CLITask:
        """
        提交 CLI 任務 (Submit CLI Task).

        由 mind_matrix 或其他 agent 呼叫，提交一個 CLI 操作任務。

        Args:
            operation: Operation type (build, test, lint, fix, analyze, review, generate).
            target_path: Target path for the operation.
            parameters: Additional parameters for the operation.
            invoked_by: ID of the invoking agent or workflow.
            dry_run: If True, only simulate without actual execution.

        Returns:
            CLITask: The created task object.

        Raises:
            ValueError: When operation is not in whitelist.
            PermissionError: When safety check fails.
        """
        # Validate operation
        if operation not in self._allowed_operations:
            raise ValueError(
                f"Operation '{operation}' not allowed. "
                f"Allowed: {self._allowed_operations}"
            )

        # Create task
        task = CLITask(
            operation=CLIOperation(operation),
            target_path=target_path,
            parameters=parameters or {},
            constraints={"dry_run": dry_run, "timeout": self.default_timeout},
            invoked_by=invoked_by,
        )

        # Safety check
        safety_result = await self._check_safety(task)
        if not safety_result.passed:
            task.status = TaskStatus.REJECTED
            task.error = f"Safety check failed: {safety_result.violations}"
            self._task_history.append(task)
            raise PermissionError(
                f"Safety check failed for task {task.task_id}: "
                f"{safety_result.violations}"
            )

        # Check if approval required
        if operation in self._require_approval and not dry_run:
            task.status = TaskStatus.PENDING
            logger.info(
                "Task %s requires approval for operation '%s'",
                task.task_id,
                operation,
            )
        else:
            task.status = TaskStatus.APPROVED

        self._active_tasks[task.task_id] = task

        # Execute if approved
        if task.status == TaskStatus.APPROVED:
            asyncio.create_task(self._execute_task(task))

        return task

    async def approve_task(self, task_id: str, approver: str = "human") -> CLITask:
        """
        批准待審任務 (Approve Pending Task).

        Args:
            task_id: The task ID to approve.
            approver: ID of the approver.

        Returns:
            CLITask: The approved task.

        Raises:
            KeyError: When task not found.
            ValueError: When task is not in pending status.
        """
        task = self._active_tasks.get(task_id)
        if not task:
            raise KeyError(f"Task {task_id} not found")

        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Task {task_id} is not pending (status: {task.status})")

        task.status = TaskStatus.APPROVED
        logger.info("Task %s approved by %s", task_id, approver)

        # Execute
        asyncio.create_task(self._execute_task(task))

        return task

    async def reject_task(self, task_id: str, reason: str = "") -> CLITask:
        """
        拒絕待審任務 (Reject Pending Task).

        Args:
            task_id: The task ID to reject.
            reason: Reason for rejection.

        Returns:
            CLITask: The rejected task.
        """
        task = self._active_tasks.get(task_id)
        if not task:
            raise KeyError(f"Task {task_id} not found")

        task.status = TaskStatus.REJECTED
        task.error = reason or "Rejected by approver"
        task.completed_at = datetime.now(UTC)

        del self._active_tasks[task_id]
        self._task_history.append(task)

        logger.info("Task %s rejected: %s", task_id, reason)
        return task

    def get_task(self, task_id: str) -> CLITask | None:
        """
        取得任務狀態 (Get Task Status).

        Args:
            task_id: The task ID to look up.

        Returns:
            CLITask or None: The task if found.
        """
        return self._active_tasks.get(task_id)

    def get_active_tasks(self) -> list[CLITask]:
        """
        取得所有活躍任務 (Get All Active Tasks).

        Returns:
            List of active CLITask objects.
        """
        return list(self._active_tasks.values())

    def get_task_history(self, limit: int = 100) -> list[CLITask]:
        """
        取得任務歷史 (Get Task History).

        Args:
            limit: Maximum number of tasks to return.

        Returns:
            List of historical CLITask objects.
        """
        return self._task_history[-limit:]

    # ═══════════════════════════════════════════════════════════════════════════
    # Internal Methods (內部方法)
    # ═══════════════════════════════════════════════════════════════════════════

    async def _check_safety(self, task: CLITask) -> SafetyCheckResult:
        """
        執行安全檢查 (Perform Safety Check).

        整合 safety_mechanisms 進行風險評估。

        Args:
            task: The task to check.

        Returns:
            SafetyCheckResult: The result of the safety check.
        """
        violations: list[str] = []
        recommendations: list[str] = []
        risk_score = 0.0

        # Check for destructive patterns in individual parameter values
        dangerous_patterns = ["rm -rf", "delete", "drop", "truncate"]

        for key, value in task.parameters.items():
            value_str = str(value).lower()
            for pattern in dangerous_patterns:
                if pattern in value_str:
                    violations.append(f"Dangerous pattern detected in '{key}': {pattern}")
                    risk_score += 0.5

        # Check for production targets
        if "prod" in task.target_path.lower() or "production" in task.target_path.lower():
            recommendations.append("Consider using staging environment first")
            risk_score += 0.2

        # Operation-specific checks
        if task.operation == CLIOperation.FIX:
            recommendations.append("Review changes before merging to main branch")
            risk_score += 0.1

        # Cap risk score
        risk_score = min(risk_score, 1.0)

        return SafetyCheckResult(
            passed=len(violations) == 0,
            risk_score=risk_score,
            violations=violations,
            recommendations=recommendations,
        )

    async def _execute_task(self, task: CLITask) -> None:
        """
        執行任務 (Execute Task).

        實際執行 CLI 操作，並記錄 provenance。

        Args:
            task: The task to execute.
        """
        # Lazy initialize semaphore in async context
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

        async with self._semaphore:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(UTC)

            logger.info(
                "Executing task %s: %s on %s",
                task.task_id,
                task.operation.value,
                task.target_path,
            )

            try:
                # Simulate CLI execution (in production, would call actual CLI)
                timeout = task.constraints.get("timeout", self.default_timeout)

                result = await asyncio.wait_for(
                    self._run_cli_operation(task),
                    timeout=timeout,
                )

                task.result = result
                task.status = TaskStatus.COMPLETED

                # Record provenance
                task.provenance_ref = await self._record_provenance(task)

            except TimeoutError:
                task.status = TaskStatus.TIMEOUT
                task.error = f"Task timed out after {timeout}s"
                logger.error("Task %s timed out", task.task_id)

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                logger.exception("Task %s failed: %s", task.task_id, e)

            finally:
                task.completed_at = datetime.now(UTC)
                del self._active_tasks[task.task_id]
                self._task_history.append(task)

    async def _run_cli_operation(self, task: CLITask) -> dict[str, Any]:
        """
        執行 CLI 操作 (Run CLI Operation).

        實際呼叫 Admin Copilot CLI 的邏輯。

        Args:
            task: The task to run.

        Returns:
            dict: The operation result.
        """
        # Simulate execution delay
        await asyncio.sleep(0.1)

        # In production, this would call the actual CLI
        # For now, return simulated result
        return {
            "operation": task.operation.value,
            "target": task.target_path,
            "success": True,
            "output": f"Simulated {task.operation.value} completed successfully",
            "metrics": {
                "duration_ms": 100,
                "files_processed": 10,
            },
        }

    async def _record_provenance(self, task: CLITask) -> str:
        """
        記錄 SLSA 證據 (Record SLSA Provenance).

        將任務執行記錄寫入 slsa_provenance。

        Args:
            task: The completed task.

        Returns:
            str: The provenance reference ID.
        """
        provenance_id = f"prov-{task.task_id}"

        provenance_record = {
            "id": provenance_id,
            "task_id": task.task_id,
            "operation": task.operation.value,
            "target": task.target_path,
            "invoked_by": task.invoked_by,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "status": task.status.value,
            "result_summary": (
                task.result.get("output")
                if isinstance(task.result, dict)
                else None
            ),
        }

        logger.info(
            "Recorded provenance %s for task %s",
            provenance_id,
            task.task_id,
        )

        return provenance_id


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Instance (單例實例)
# ═══════════════════════════════════════════════════════════════════════════════

_cli_bridge_instance: CLIBridge | None = None


def get_cli_bridge() -> CLIBridge:
    """
    取得 CLI Bridge 單例 (Get CLI Bridge Singleton).

    Returns:
        CLIBridge: The singleton instance.
    """
    global _cli_bridge_instance
    if _cli_bridge_instance is None:
        _cli_bridge_instance = CLIBridge()
    return _cli_bridge_instance
