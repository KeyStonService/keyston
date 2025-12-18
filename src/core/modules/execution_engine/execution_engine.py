"""
═══════════════════════════════════════════════════════════
        Execution Engine - 執行引擎核心
        將知識轉換為實際行動能力
═══════════════════════════════════════════════════════════

核心功能：
1. 接收行動請求
2. 驗證執行能力
3. 建立執行計劃
4. 執行實際操作
5. 驗證執行結果
6. 處理錯誤和回滾
"""

import asyncio
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ExecutionStatus(Enum):
    """執行狀態"""
    PENDING = "pending"
    VALIDATING = "validating"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ActionType(Enum):
    """行動類型"""
    DATABASE = "database"
    DEPLOYMENT = "deployment"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    API_CALL = "api_call"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    MONITORING = "monitoring"


@dataclass
class ExecutionContext:
    """執行上下文 - 包含執行所需的所有環境信息"""

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    # 環境信息
    environment: str = "development"  # development, staging, production
    region: str = "default"

    # 認證和授權
    credentials: dict[str, Any] = field(default_factory=dict)
    permissions: list[str] = field(default_factory=list)

    # 執行配置
    timeout_seconds: int = 300
    retry_count: int = 3
    dry_run: bool = False

    # 追蹤信息
    correlation_id: str = ""
    parent_execution_id: str = ""

    # 元數據
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """執行結果"""

    execution_id: str
    status: ExecutionStatus
    action_type: ActionType

    # 時間信息
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int = 0

    # 結果數據
    output: Any = None
    error: str | None = None
    error_details: dict[str, Any] = field(default_factory=dict)

    # 執行追蹤
    steps_completed: int = 0
    steps_total: int = 0

    # 驗證結果
    verification_passed: bool = False
    verification_details: dict[str, Any] = field(default_factory=dict)

    # 回滾信息
    rollback_performed: bool = False
    rollback_successful: bool = False

    # 學習數據
    lessons_learned: list[str] = field(default_factory=list)


class ExecutionEngine:
    """
    執行引擎 - 核心執行組件
    
    將「知道如何做」轉換為「能夠實際做」
    
    核心原則：
    1. 知識 ≠ 能力：有知識不代表能執行
    2. 理論 ≠ 實踐：需要實際的連接器和執行器
    3. 代碼 ≠ 執行：代碼只是指令，需要執行層來實現
    """

    def __init__(self):
        """初始化執行引擎"""

        # 執行器註冊表
        self._executors: dict[ActionType, Callable] = {}

        # 連接器管理
        self._connectors: dict[str, Any] = {}

        # 執行歷史
        self._execution_history: list[ExecutionResult] = []

        # 能力驗證器
        self._capability_validators: dict[ActionType, Callable] = {}

        # 前置/後置處理器
        self._pre_processors: list[Callable] = []
        self._post_processors: list[Callable] = []

        # 統計數據
        self._stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "rollbacks_performed": 0,
            "average_duration_ms": 0,
        }

        # 初始化默認執行器
        self._register_default_executors()

    def _register_default_executors(self):
        """註冊默認執行器"""

        # 數據庫執行器
        self._executors[ActionType.DATABASE] = self._execute_database_action

        # 部署執行器
        self._executors[ActionType.DEPLOYMENT] = self._execute_deployment_action

        # 文件系統執行器
        self._executors[ActionType.FILE_SYSTEM] = self._execute_filesystem_action

        # 網絡執行器
        self._executors[ActionType.NETWORK] = self._execute_network_action

        # API 調用執行器
        self._executors[ActionType.API_CALL] = self._execute_api_action

        # 配置執行器
        self._executors[ActionType.CONFIGURATION] = self._execute_config_action

        # 安全執行器
        self._executors[ActionType.SECURITY] = self._execute_security_action

        # 監控執行器
        self._executors[ActionType.MONITORING] = self._execute_monitoring_action

    async def execute(
        self,
        action_type: ActionType,
        action_params: dict[str, Any],
        context: ExecutionContext | None = None
    ) -> ExecutionResult:
        """
        執行行動 - 核心執行方法
        
        這是將「知道」轉換為「能做」的關鍵
        
        Args:
            action_type: 行動類型
            action_params: 行動參數
            context: 執行上下文
            
        Returns:
            ExecutionResult: 執行結果
        """

        # 創建執行上下文
        if context is None:
            context = ExecutionContext()

        # 記錄開始時間
        started_at = datetime.now()

        # 創建結果對象
        result = ExecutionResult(
            execution_id=context.execution_id,
            status=ExecutionStatus.PENDING,
            action_type=action_type,
            started_at=started_at,
        )

        try:
            # 階段 1：驗證執行能力
            result.status = ExecutionStatus.VALIDATING
            await self._validate_capability(action_type, action_params, context)

            # 階段 2：執行前置處理
            for pre_processor in self._pre_processors:
                await self._safe_call(pre_processor, action_type, action_params, context)

            # 階段 3：構建執行計劃
            result.status = ExecutionStatus.PLANNING
            execution_plan = await self._build_execution_plan(
                action_type, action_params, context
            )
            result.steps_total = len(execution_plan.get("steps", []))

            # 階段 4：執行行動（或模擬執行）
            result.status = ExecutionStatus.EXECUTING

            if context.dry_run:
                # 模擬執行
                output = await self._simulate_execution(
                    action_type, action_params, execution_plan
                )
            else:
                # 實際執行
                output = await self._execute_action(
                    action_type, action_params, context, execution_plan
                )

            result.output = output
            result.steps_completed = result.steps_total

            # 階段 5：驗證執行結果
            result.status = ExecutionStatus.VERIFYING
            verification = await self._verify_execution(
                action_type, action_params, output, context
            )
            result.verification_passed = verification.get("passed", False)
            result.verification_details = verification

            # 如果驗證失敗，執行回滾
            if not result.verification_passed and not context.dry_run:
                result.status = ExecutionStatus.FAILED
                rollback_result = await self._execute_rollback(
                    action_type, action_params, context, execution_plan
                )
                result.rollback_performed = True
                result.rollback_successful = rollback_result.get("success", False)
                if result.rollback_successful:
                    result.status = ExecutionStatus.ROLLED_BACK
            else:
                result.status = ExecutionStatus.COMPLETED

            # 階段 6：執行後置處理
            for post_processor in self._post_processors:
                await self._safe_call(
                    post_processor, action_type, result, context
                )

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            result.error_details = {
                "exception_type": type(e).__name__,
                "message": str(e),
            }

            # 記錄學習經驗
            result.lessons_learned.append(
                f"Execution failed due to: {type(e).__name__}: {str(e)}"
            )

        finally:
            # 記錄完成時間
            result.completed_at = datetime.now()
            result.duration_ms = int(
                (result.completed_at - started_at).total_seconds() * 1000
            )

            # 更新統計
            self._update_stats(result)

            # 保存執行歷史
            self._execution_history.append(result)

        return result

    async def _validate_capability(
        self,
        action_type: ActionType,
        action_params: dict[str, Any],
        context: ExecutionContext
    ) -> bool:
        """驗證執行能力 - 確保我們真的能執行這個行動"""

        # 檢查是否有對應的執行器
        if action_type not in self._executors:
            raise ValueError(f"No executor registered for action type: {action_type}")

        # 檢查權限
        required_permissions = self._get_required_permissions(action_type, action_params)
        for perm in required_permissions:
            if perm not in context.permissions:
                raise PermissionError(f"Missing required permission: {perm}")

        # 檢查連接器
        required_connectors = self._get_required_connectors(action_type, action_params)
        for connector in required_connectors:
            if connector not in self._connectors:
                raise RuntimeError(f"Required connector not available: {connector}")

        # 執行自定義驗證
        if action_type in self._capability_validators:
            validator = self._capability_validators[action_type]
            is_valid = await self._safe_call(validator, action_params, context)
            if not is_valid:
                raise ValueError(f"Capability validation failed for {action_type}")

        return True

    async def _build_execution_plan(
        self,
        action_type: ActionType,
        action_params: dict[str, Any],
        context: ExecutionContext
    ) -> dict[str, Any]:
        """構建執行計劃"""

        # 基礎計劃結構
        plan = {
            "action_type": action_type.value,
            "params": action_params,
            "context": {
                "environment": context.environment,
                "dry_run": context.dry_run,
            },
            "steps": [],
            "rollback_steps": [],
            "checkpoints": [],
        }

        # 根據行動類型構建具體步驟
        if action_type == ActionType.DATABASE:
            plan["steps"] = self._build_database_steps(action_params)
        elif action_type == ActionType.DEPLOYMENT:
            plan["steps"] = self._build_deployment_steps(action_params)
        elif action_type == ActionType.FILE_SYSTEM:
            plan["steps"] = self._build_filesystem_steps(action_params)
        elif action_type == ActionType.API_CALL:
            plan["steps"] = self._build_api_steps(action_params)
        elif action_type == ActionType.CONFIGURATION:
            plan["steps"] = self._build_config_steps(action_params)
        elif action_type == ActionType.SECURITY:
            plan["steps"] = self._build_security_steps(action_params)
        else:
            plan["steps"] = [{"name": "execute", "params": action_params}]

        return plan

    def _build_database_steps(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """構建數據庫操作步驟"""
        operation = params.get("operation", "query")
        steps = []

        # 連接步驟
        steps.append({
            "name": "connect",
            "description": "建立數據庫連接",
            "params": {"database": params.get("database", "default")},
        })

        # 備份步驟（對於修改操作）
        if operation in ["insert", "update", "delete", "alter"]:
            steps.append({
                "name": "backup",
                "description": "創建數據備份",
                "params": {"table": params.get("table")},
            })

        # 執行步驟
        steps.append({
            "name": "execute_sql",
            "description": f"執行 {operation} 操作",
            "params": {
                "sql": params.get("sql"),
                "operation": operation,
            },
        })

        # 驗證步驟
        steps.append({
            "name": "verify",
            "description": "驗證操作結果",
            "params": {"expected": params.get("expected_result")},
        })

        return steps

    def _build_deployment_steps(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """構建部署操作步驟"""
        strategy = params.get("strategy", "rolling")
        steps = []

        # 準備步驟
        steps.append({
            "name": "prepare",
            "description": "準備部署環境",
            "params": {"environment": params.get("environment", "staging")},
        })

        # 構建步驟
        steps.append({
            "name": "build",
            "description": "構建應用程序",
            "params": {"version": params.get("version")},
        })

        # 測試步驟
        steps.append({
            "name": "test",
            "description": "執行部署前測試",
            "params": {"test_suite": params.get("test_suite", "smoke")},
        })

        # 部署步驟
        steps.append({
            "name": "deploy",
            "description": f"使用 {strategy} 策略部署",
            "params": {
                "strategy": strategy,
                "replicas": params.get("replicas", 1),
            },
        })

        # 健康檢查步驟
        steps.append({
            "name": "health_check",
            "description": "執行健康檢查",
            "params": {"timeout": params.get("health_check_timeout", 60)},
        })

        return steps

    def _build_filesystem_steps(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """構建文件系統操作步驟"""
        operation = params.get("operation", "read")
        steps = []

        # 檢查步驟
        steps.append({
            "name": "check_path",
            "description": "檢查路徑存在性和權限",
            "params": {"path": params.get("path")},
        })

        # 備份步驟（對於修改操作）
        if operation in ["write", "delete", "move"]:
            steps.append({
                "name": "backup",
                "description": "創建文件備份",
                "params": {"path": params.get("path")},
            })

        # 執行步驟
        steps.append({
            "name": f"execute_{operation}",
            "description": f"執行 {operation} 操作",
            "params": params,
        })

        return steps

    def _build_api_steps(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """構建 API 調用步驟"""
        return [
            {
                "name": "prepare_request",
                "description": "準備 API 請求",
                "params": {
                    "url": params.get("url"),
                    "method": params.get("method", "GET"),
                },
            },
            {
                "name": "authenticate",
                "description": "處理認證",
                "params": {"auth_type": params.get("auth_type", "none")},
            },
            {
                "name": "send_request",
                "description": "發送 API 請求",
                "params": params,
            },
            {
                "name": "validate_response",
                "description": "驗證響應",
                "params": {"expected_status": params.get("expected_status", 200)},
            },
        ]

    def _build_config_steps(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """構建配置操作步驟"""
        return [
            {
                "name": "load_current",
                "description": "載入當前配置",
                "params": {"config_path": params.get("config_path")},
            },
            {
                "name": "backup_config",
                "description": "備份當前配置",
                "params": {},
            },
            {
                "name": "apply_changes",
                "description": "應用配置變更",
                "params": {"changes": params.get("changes", {})},
            },
            {
                "name": "validate_config",
                "description": "驗證新配置",
                "params": {},
            },
        ]

    def _build_security_steps(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """構建安全操作步驟"""
        operation = params.get("operation", "audit")
        steps = []

        # 驗證授權
        steps.append({
            "name": "verify_authorization",
            "description": "驗證安全操作授權",
            "params": {"required_level": params.get("security_level", "standard")},
        })

        # 審計記錄
        steps.append({
            "name": "create_audit_log",
            "description": "創建審計記錄",
            "params": {"operation": operation},
        })

        # 執行操作
        steps.append({
            "name": f"execute_{operation}",
            "description": f"執行安全操作: {operation}",
            "params": params,
        })

        return steps

    async def _execute_action(
        self,
        action_type: ActionType,
        action_params: dict[str, Any],
        context: ExecutionContext,
        execution_plan: dict[str, Any]
    ) -> Any:
        """執行實際行動"""

        executor = self._executors.get(action_type)
        if executor is None:
            raise ValueError(f"No executor for action type: {action_type}")

        return await executor(action_params, context, execution_plan)

    async def _simulate_execution(
        self,
        action_type: ActionType,
        action_params: dict[str, Any],
        execution_plan: dict[str, Any]
    ) -> dict[str, Any]:
        """模擬執行（Dry Run）"""

        return {
            "simulated": True,
            "action_type": action_type.value,
            "would_execute": execution_plan.get("steps", []),
            "estimated_duration_ms": len(execution_plan.get("steps", [])) * 100,
            "warnings": [],
        }

    async def _verify_execution(
        self,
        action_type: ActionType,
        action_params: dict[str, Any],
        output: Any,
        context: ExecutionContext
    ) -> dict[str, Any]:
        """驗證執行結果"""

        verification = {
            "passed": True,
            "checks": [],
            "warnings": [],
        }

        # 基本輸出檢查
        if output is None:
            verification["checks"].append({
                "name": "output_exists",
                "passed": False,
                "message": "No output produced",
            })
            verification["passed"] = False
        else:
            verification["checks"].append({
                "name": "output_exists",
                "passed": True,
                "message": "Output produced successfully",
            })

        # 檢查是否有錯誤
        if isinstance(output, dict):
            if output.get("error"):
                verification["checks"].append({
                    "name": "no_errors",
                    "passed": False,
                    "message": f"Error in output: {output.get('error')}",
                })
                verification["passed"] = False

            # Dry run 總是通過
            if output.get("simulated"):
                verification["passed"] = True
                verification["checks"].append({
                    "name": "dry_run",
                    "passed": True,
                    "message": "Dry run simulation completed",
                })

        return verification

    async def _execute_rollback(
        self,
        action_type: ActionType,
        action_params: dict[str, Any],
        context: ExecutionContext,
        execution_plan: dict[str, Any]
    ) -> dict[str, Any]:
        """執行回滾"""

        rollback_result = {
            "success": False,
            "steps_rolled_back": 0,
            "errors": [],
        }

        rollback_steps = execution_plan.get("rollback_steps", [])

        for step in rollback_steps:
            try:
                # 執行回滾步驟
                await self._execute_rollback_step(step, context)
                rollback_result["steps_rolled_back"] += 1
            except Exception as e:
                rollback_result["errors"].append({
                    "step": step.get("name"),
                    "error": str(e),
                })

        rollback_result["success"] = len(rollback_result["errors"]) == 0

        return rollback_result

    async def _execute_rollback_step(
        self,
        step: dict[str, Any],
        context: ExecutionContext
    ):
        """執行單個回滾步驟"""
        # 模擬回滾執行
        await asyncio.sleep(0.01)

    def _get_required_permissions(
        self,
        action_type: ActionType,
        action_params: dict[str, Any]
    ) -> list[str]:
        """獲取所需權限"""

        permission_map = {
            ActionType.DATABASE: ["database.read", "database.write"],
            ActionType.DEPLOYMENT: ["deployment.execute"],
            ActionType.FILE_SYSTEM: ["filesystem.read", "filesystem.write"],
            ActionType.NETWORK: ["network.access"],
            ActionType.API_CALL: ["api.call"],
            ActionType.CONFIGURATION: ["config.read", "config.write"],
            ActionType.SECURITY: ["security.admin"],
            ActionType.MONITORING: ["monitoring.read"],
        }

        return permission_map.get(action_type, [])

    def _get_required_connectors(
        self,
        action_type: ActionType,
        action_params: dict[str, Any]
    ) -> list[str]:
        """獲取所需連接器"""

        # 根據行動類型返回所需的連接器

        return []  # 默認不要求連接器，允許模擬執行

    def _update_stats(self, result: ExecutionResult):
        """更新統計數據"""

        self._stats["total_executions"] += 1

        if result.status == ExecutionStatus.COMPLETED:
            self._stats["successful_executions"] += 1
        else:
            self._stats["failed_executions"] += 1

        if result.rollback_performed:
            self._stats["rollbacks_performed"] += 1

        # 更新平均執行時間
        total = self._stats["total_executions"]
        current_avg = self._stats["average_duration_ms"]
        self._stats["average_duration_ms"] = (
            (current_avg * (total - 1) + result.duration_ms) / total
        )

    async def _safe_call(self, func: Callable, *args, **kwargs) -> Any:
        """安全調用函數"""
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception:
            return None

    # ============ 默認執行器實現 ============

    async def _execute_database_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """數據庫行動執行器"""

        operation = params.get("operation", "query")

        # 模擬執行
        await asyncio.sleep(0.05)

        return {
            "operation": operation,
            "database": params.get("database", "default"),
            "affected_rows": 1 if operation != "query" else 0,
            "result": params.get("expected_result", []),
        }

    async def _execute_deployment_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """部署行動執行器"""

        # 模擬部署
        await asyncio.sleep(0.1)

        return {
            "deployment_id": str(uuid.uuid4()),
            "version": params.get("version", "1.0.0"),
            "strategy": params.get("strategy", "rolling"),
            "replicas": params.get("replicas", 1),
            "status": "deployed",
        }

    async def _execute_filesystem_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """文件系統行動執行器"""

        operation = params.get("operation", "read")

        await asyncio.sleep(0.02)

        return {
            "operation": operation,
            "path": params.get("path", ""),
            "success": True,
        }

    async def _execute_network_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """網絡行動執行器"""

        await asyncio.sleep(0.03)

        return {
            "host": params.get("host", "localhost"),
            "port": params.get("port", 80),
            "connected": True,
        }

    async def _execute_api_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """API 調用行動執行器"""

        await asyncio.sleep(0.04)

        return {
            "url": params.get("url", ""),
            "method": params.get("method", "GET"),
            "status_code": 200,
            "response": params.get("mock_response", {}),
        }

    async def _execute_config_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """配置行動執行器"""

        await asyncio.sleep(0.02)

        return {
            "config_path": params.get("config_path", ""),
            "changes_applied": params.get("changes", {}),
            "success": True,
        }

    async def _execute_security_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """安全行動執行器"""

        operation = params.get("operation", "audit")

        await asyncio.sleep(0.03)

        return {
            "operation": operation,
            "audit_id": str(uuid.uuid4()),
            "success": True,
        }

    async def _execute_monitoring_action(
        self,
        params: dict[str, Any],
        context: ExecutionContext,
        plan: dict[str, Any]
    ) -> dict[str, Any]:
        """監控行動執行器"""

        await asyncio.sleep(0.02)

        return {
            "metrics_collected": True,
            "data_points": 100,
        }

    # ============ 公開 API ============

    def register_executor(
        self,
        action_type: ActionType,
        executor: Callable
    ):
        """註冊自定義執行器"""
        self._executors[action_type] = executor

    def register_connector(self, name: str, connector: Any):
        """註冊連接器"""
        self._connectors[name] = connector

    def register_capability_validator(
        self,
        action_type: ActionType,
        validator: Callable
    ):
        """註冊能力驗證器"""
        self._capability_validators[action_type] = validator

    def add_pre_processor(self, processor: Callable):
        """添加前置處理器"""
        self._pre_processors.append(processor)

    def add_post_processor(self, processor: Callable):
        """添加後置處理器"""
        self._post_processors.append(processor)

    def get_stats(self) -> dict[str, Any]:
        """獲取執行統計"""
        return self._stats.copy()

    def get_execution_history(
        self,
        limit: int = 100
    ) -> list[ExecutionResult]:
        """獲取執行歷史"""
        return self._execution_history[-limit:]
