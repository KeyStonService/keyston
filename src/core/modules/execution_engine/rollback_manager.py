"""
═══════════════════════════════════════════════════════════
        Rollback Manager - 回滾管理器
        管理操作回滾和系統恢復
═══════════════════════════════════════════════════════════

核心功能：
1. 創建和管理檢查點
2. 執行操作回滾
3. 管理回滾策略
4. 恢復系統狀態
"""

import asyncio
import copy
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RollbackStatus(Enum):
    """回滾狀態"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class RollbackStrategy(Enum):
    """回滾策略"""
    FULL = "full"  # 完全回滾到檢查點
    INCREMENTAL = "incremental"  # 逐步回滾
    SELECTIVE = "selective"  # 選擇性回滾
    COMPENSATING = "compensating"  # 補償性操作


@dataclass
class Checkpoint:
    """檢查點"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""

    # 時間
    created_at: datetime = field(default_factory=datetime.now)

    # 狀態快照
    state: dict[str, Any] = field(default_factory=dict)

    # 元數據
    metadata: dict[str, Any] = field(default_factory=dict)

    # 關聯的執行
    execution_id: str = ""
    step_id: str = ""

    # 回滾信息
    rollback_handler: Callable | None = None
    rollback_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackStep:
    """回滾步驟"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""

    # 執行
    handler: Callable | None = None
    params: dict[str, Any] = field(default_factory=dict)

    # 狀態
    status: RollbackStatus = RollbackStatus.PENDING

    # 結果
    result: Any = None
    error: str | None = None

    # 時間
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class RollbackPlan:
    """回滾計劃"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""

    # 策略
    strategy: RollbackStrategy = RollbackStrategy.FULL

    # 目標檢查點
    target_checkpoint: Checkpoint | None = None

    # 回滾步驟
    steps: list[RollbackStep] = field(default_factory=list)

    # 狀態
    status: RollbackStatus = RollbackStatus.PENDING

    # 時間
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # 結果
    steps_completed: int = 0
    steps_failed: int = 0
    errors: list[str] = field(default_factory=list)


class RollbackManager:
    """
    回滾管理器 - 管理操作回滾和系統恢復
    
    核心職責：
    1. 創建檢查點保存系統狀態
    2. 在失敗時執行回滾
    3. 支持多種回滾策略
    4. 確保系統可恢復性
    """

    def __init__(self):
        """初始化回滾管理器"""

        # 檢查點存儲
        self._checkpoints: dict[str, Checkpoint] = {}

        # 按執行 ID 索引檢查點
        self._execution_checkpoints: dict[str, list[str]] = {}

        # 回滾計劃歷史
        self._rollback_history: list[RollbackPlan] = []

        # 回滾處理器
        self._rollback_handlers: dict[str, Callable] = {}

        # 統計
        self._stats = {
            "total_checkpoints": 0,
            "total_rollbacks": 0,
            "successful_rollbacks": 0,
            "failed_rollbacks": 0,
        }

        # 註冊默認處理器
        self._register_default_handlers()

    def _register_default_handlers(self):
        """註冊默認回滾處理器"""

        self._rollback_handlers["database"] = self._rollback_database
        self._rollback_handlers["file"] = self._rollback_file
        self._rollback_handlers["config"] = self._rollback_config
        self._rollback_handlers["deployment"] = self._rollback_deployment

    def create_checkpoint(
        self,
        name: str,
        state: dict[str, Any],
        execution_id: str = "",
        step_id: str = "",
        rollback_handler: Callable | None = None,
        rollback_params: dict[str, Any] | None = None
    ) -> Checkpoint:
        """
        創建檢查點
        
        Args:
            name: 檢查點名稱
            state: 狀態快照
            execution_id: 關聯的執行 ID
            step_id: 關聯的步驟 ID
            rollback_handler: 回滾處理器
            rollback_params: 回滾參數
            
        Returns:
            創建的檢查點
        """

        checkpoint = Checkpoint(
            name=name,
            state=copy.deepcopy(state),
            execution_id=execution_id,
            step_id=step_id,
            rollback_handler=rollback_handler,
            rollback_params=rollback_params or {},
        )

        # 存儲檢查點
        self._checkpoints[checkpoint.id] = checkpoint

        # 更新執行索引
        if execution_id:
            if execution_id not in self._execution_checkpoints:
                self._execution_checkpoints[execution_id] = []
            self._execution_checkpoints[execution_id].append(checkpoint.id)

        # 更新統計
        self._stats["total_checkpoints"] += 1

        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """獲取檢查點"""
        return self._checkpoints.get(checkpoint_id)

    def get_checkpoints_for_execution(
        self,
        execution_id: str
    ) -> list[Checkpoint]:
        """獲取執行相關的所有檢查點"""

        checkpoint_ids = self._execution_checkpoints.get(execution_id, [])
        return [
            self._checkpoints[cp_id]
            for cp_id in checkpoint_ids
            if cp_id in self._checkpoints
        ]

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """刪除檢查點"""

        if checkpoint_id not in self._checkpoints:
            return False

        checkpoint = self._checkpoints.pop(checkpoint_id)

        # 更新執行索引
        if checkpoint.execution_id:
            exec_checkpoints = self._execution_checkpoints.get(
                checkpoint.execution_id, []
            )
            if checkpoint_id in exec_checkpoints:
                exec_checkpoints.remove(checkpoint_id)

        return True

    def cleanup_old_checkpoints(
        self,
        max_age_hours: int = 24,
        max_count: int = 1000
    ) -> int:
        """
        清理舊檢查點
        
        Args:
            max_age_hours: 最大保留時間（小時）
            max_count: 最大保留數量
            
        Returns:
            清理的數量
        """

        now = datetime.now()
        deleted = 0

        # 按時間排序
        sorted_checkpoints = sorted(
            self._checkpoints.values(),
            key=lambda c: c.created_at
        )

        for checkpoint in sorted_checkpoints:
            # 檢查年齡
            age_hours = (now - checkpoint.created_at).total_seconds() / 3600

            if age_hours > max_age_hours or len(self._checkpoints) > max_count:
                self.delete_checkpoint(checkpoint.id)
                deleted += 1

        return deleted

    async def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        strategy: RollbackStrategy = RollbackStrategy.FULL
    ) -> RollbackPlan:
        """
        回滾到指定檢查點
        
        Args:
            checkpoint_id: 檢查點 ID
            strategy: 回滾策略
            
        Returns:
            回滾計劃
        """

        checkpoint = self.get_checkpoint(checkpoint_id)
        if checkpoint is None:
            plan = RollbackPlan(
                name=f"Rollback to {checkpoint_id}",
                strategy=strategy,
                status=RollbackStatus.FAILED,
            )
            plan.errors.append(f"Checkpoint not found: {checkpoint_id}")
            return plan

        # 創建回滾計劃
        plan = RollbackPlan(
            name=f"Rollback to {checkpoint.name}",
            strategy=strategy,
            target_checkpoint=checkpoint,
        )

        # 構建回滾步驟
        plan.steps = self._build_rollback_steps(checkpoint, strategy)

        # 執行回滾
        await self._execute_rollback_plan(plan)

        # 保存歷史
        self._rollback_history.append(plan)

        # 更新統計
        self._stats["total_rollbacks"] += 1
        if plan.status == RollbackStatus.COMPLETED:
            self._stats["successful_rollbacks"] += 1
        else:
            self._stats["failed_rollbacks"] += 1

        return plan

    async def rollback_execution(
        self,
        execution_id: str,
        strategy: RollbackStrategy = RollbackStrategy.INCREMENTAL
    ) -> RollbackPlan:
        """
        回滾整個執行
        
        Args:
            execution_id: 執行 ID
            strategy: 回滾策略
            
        Returns:
            回滾計劃
        """

        # 獲取執行的所有檢查點
        checkpoints = self.get_checkpoints_for_execution(execution_id)

        if not checkpoints:
            plan = RollbackPlan(
                name=f"Rollback execution {execution_id}",
                strategy=strategy,
                status=RollbackStatus.FAILED,
            )
            plan.errors.append(f"No checkpoints found for execution: {execution_id}")
            return plan

        # 創建回滾計劃
        plan = RollbackPlan(
            name=f"Rollback execution {execution_id}",
            strategy=strategy,
        )

        # 按時間逆序處理檢查點
        sorted_checkpoints = sorted(
            checkpoints,
            key=lambda c: c.created_at,
            reverse=True
        )

        # 構建回滾步驟
        for checkpoint in sorted_checkpoints:
            steps = self._build_rollback_steps(checkpoint, strategy)
            plan.steps.extend(steps)

        # 執行回滾
        await self._execute_rollback_plan(plan)

        # 保存歷史
        self._rollback_history.append(plan)

        # 更新統計
        self._stats["total_rollbacks"] += 1
        if plan.status == RollbackStatus.COMPLETED:
            self._stats["successful_rollbacks"] += 1
        else:
            self._stats["failed_rollbacks"] += 1

        return plan

    def _build_rollback_steps(
        self,
        checkpoint: Checkpoint,
        strategy: RollbackStrategy
    ) -> list[RollbackStep]:
        """構建回滾步驟"""

        steps = []

        if checkpoint.rollback_handler:
            # 使用自定義回滾處理器
            step = RollbackStep(
                name=f"Rollback {checkpoint.name}",
                description=f"Custom rollback for checkpoint {checkpoint.id}",
                handler=checkpoint.rollback_handler,
                params=checkpoint.rollback_params,
            )
            steps.append(step)
        else:
            # 根據狀態類型構建回滾步驟
            state = checkpoint.state

            for key, value in state.items():
                if key.startswith("database_"):
                    step = RollbackStep(
                        name=f"Rollback database state: {key}",
                        handler=self._rollback_handlers.get("database"),
                        params={"key": key, "value": value},
                    )
                    steps.append(step)

                elif key.startswith("file_"):
                    step = RollbackStep(
                        name=f"Rollback file: {key}",
                        handler=self._rollback_handlers.get("file"),
                        params={"key": key, "value": value},
                    )
                    steps.append(step)

                elif key.startswith("config_"):
                    step = RollbackStep(
                        name=f"Rollback config: {key}",
                        handler=self._rollback_handlers.get("config"),
                        params={"key": key, "value": value},
                    )
                    steps.append(step)

        return steps

    async def _execute_rollback_plan(self, plan: RollbackPlan):
        """執行回滾計劃"""

        plan.started_at = datetime.now()
        plan.status = RollbackStatus.IN_PROGRESS

        try:
            for step in plan.steps:
                step.started_at = datetime.now()
                step.status = RollbackStatus.IN_PROGRESS

                try:
                    if step.handler:
                        if asyncio.iscoroutinefunction(step.handler):
                            step.result = await step.handler(step.params)
                        else:
                            step.result = step.handler(step.params)
                    else:
                        # 默認處理
                        await asyncio.sleep(0.01)
                        step.result = {"success": True}

                    step.status = RollbackStatus.COMPLETED
                    plan.steps_completed += 1

                except Exception as e:
                    step.status = RollbackStatus.FAILED
                    step.error = str(e)
                    plan.steps_failed += 1
                    plan.errors.append(f"Step '{step.name}' failed: {str(e)}")

                finally:
                    step.completed_at = datetime.now()

            # 判斷整體結果
            if plan.steps_failed == 0:
                plan.status = RollbackStatus.COMPLETED
            elif plan.steps_completed > 0:
                plan.status = RollbackStatus.PARTIAL
            else:
                plan.status = RollbackStatus.FAILED

        except Exception as e:
            plan.status = RollbackStatus.FAILED
            plan.errors.append(f"Rollback plan error: {str(e)}")

        finally:
            plan.completed_at = datetime.now()

    def create_rollback_plan(
        self,
        name: str,
        steps: list[dict[str, Any]],
        strategy: RollbackStrategy = RollbackStrategy.FULL
    ) -> RollbackPlan:
        """
        創建自定義回滾計劃
        
        Args:
            name: 計劃名稱
            steps: 步驟定義列表
            strategy: 回滾策略
            
        Returns:
            回滾計劃
        """

        plan = RollbackPlan(
            name=name,
            strategy=strategy,
        )

        for step_def in steps:
            step = RollbackStep(
                name=step_def.get("name", ""),
                description=step_def.get("description", ""),
                params=step_def.get("params", {}),
            )

            handler_name = step_def.get("handler")
            if handler_name and handler_name in self._rollback_handlers:
                step.handler = self._rollback_handlers[handler_name]

            plan.steps.append(step)

        return plan

    def register_handler(self, name: str, handler: Callable):
        """註冊回滾處理器"""
        self._rollback_handlers[name] = handler

    def get_stats(self) -> dict[str, Any]:
        """獲取統計信息"""
        return self._stats.copy()

    def get_history(self, limit: int = 100) -> list[RollbackPlan]:
        """獲取回滾歷史"""
        return self._rollback_history[-limit:]

    # ============ 默認回滾處理器 ============

    async def _rollback_database(self, params: dict[str, Any]) -> dict[str, Any]:
        """數據庫回滾處理器"""
        await asyncio.sleep(0.05)
        return {
            "rolled_back": True,
            "type": "database",
            "key": params.get("key"),
        }

    async def _rollback_file(self, params: dict[str, Any]) -> dict[str, Any]:
        """文件回滾處理器"""
        await asyncio.sleep(0.03)
        return {
            "rolled_back": True,
            "type": "file",
            "key": params.get("key"),
        }

    async def _rollback_config(self, params: dict[str, Any]) -> dict[str, Any]:
        """配置回滾處理器"""
        await asyncio.sleep(0.02)
        return {
            "rolled_back": True,
            "type": "config",
            "key": params.get("key"),
        }

    async def _rollback_deployment(self, params: dict[str, Any]) -> dict[str, Any]:
        """部署回滾處理器"""
        await asyncio.sleep(0.1)
        return {
            "rolled_back": True,
            "type": "deployment",
            "version": params.get("previous_version"),
        }
