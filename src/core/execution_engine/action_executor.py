"""
═══════════════════════════════════════════════════════════
        Action Executor - 行動執行器
        將計劃轉換為實際執行步驟
═══════════════════════════════════════════════════════════

核心功能：
1. 解析執行計劃
2. 執行步驟序列
3. 處理步驟依賴
4. 管理執行狀態
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Awaitable
from datetime import datetime
import asyncio
import uuid


class StepStatus(Enum):
    """步驟狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class ActionStep:
    """行動步驟"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # 執行
    handler: Optional[Callable] = None
    params: Dict[str, Any] = field(default_factory=dict)
    
    # 依賴
    depends_on: List[str] = field(default_factory=list)
    
    # 狀態
    status: StepStatus = StepStatus.PENDING
    
    # 時間
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    
    # 結果
    output: Any = None
    error: Optional[str] = None
    
    # 重試
    retry_count: int = 0
    max_retries: int = 3
    
    # 條件
    condition: Optional[Callable] = None
    skip_on_failure: bool = False
    
    # 回滾
    rollback_handler: Optional[Callable] = None
    rollback_completed: bool = False


@dataclass
class StepResult:
    """步驟執行結果"""
    
    step_id: str
    step_name: str
    status: StepStatus
    
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    
    output: Any = None
    error: Optional[str] = None
    
    retry_count: int = 0


@dataclass
class ActionPlan:
    """行動計劃"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # 步驟
    steps: List[ActionStep] = field(default_factory=list)
    
    # 狀態
    status: str = "pending"
    
    # 時間
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 執行配置
    parallel: bool = False
    stop_on_failure: bool = True
    
    # 結果
    results: List[StepResult] = field(default_factory=list)
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)


class ActionExecutor:
    """
    行動執行器 - 將計劃轉換為實際執行
    
    核心職責：
    1. 解析執行計劃中的步驟
    2. 按照依賴順序執行
    3. 處理並行和串行執行
    4. 管理錯誤和重試
    """
    
    def __init__(self):
        """初始化行動執行器"""
        
        # 步驟處理器
        self._handlers: Dict[str, Callable] = {}
        
        # 執行中的計劃
        self._running_plans: Dict[str, ActionPlan] = {}
        
        # 執行歷史
        self._execution_history: List[ActionPlan] = []
        
        # 統計
        self._stats = {
            "total_plans": 0,
            "successful_plans": 0,
            "failed_plans": 0,
            "total_steps": 0,
            "successful_steps": 0,
            "failed_steps": 0,
        }
        
        # 註冊默認處理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """註冊默認步驟處理器"""
        
        self._handlers["default"] = self._default_handler
        self._handlers["connect"] = self._connect_handler
        self._handlers["backup"] = self._backup_handler
        self._handlers["execute_sql"] = self._execute_sql_handler
        self._handlers["verify"] = self._verify_handler
        self._handlers["deploy"] = self._deploy_handler
        self._handlers["health_check"] = self._health_check_handler
        self._handlers["prepare"] = self._prepare_handler
        self._handlers["build"] = self._build_handler
        self._handlers["test"] = self._test_handler
    
    async def execute_plan(self, plan: ActionPlan) -> ActionPlan:
        """
        執行行動計劃
        
        Args:
            plan: 行動計劃
            
        Returns:
            執行後的計劃（包含結果）
        """
        
        plan.started_at = datetime.now()
        plan.status = "running"
        self._running_plans[plan.id] = plan
        
        try:
            if plan.parallel:
                await self._execute_parallel(plan)
            else:
                await self._execute_sequential(plan)
            
            # 判斷整體結果
            failed_steps = [r for r in plan.results if r.status == StepStatus.FAILED]
            if failed_steps:
                plan.status = "failed"
            else:
                plan.status = "completed"
                
        except Exception as e:
            plan.status = "failed"
            # 記錄錯誤
            
        finally:
            plan.completed_at = datetime.now()
            
            # 從運行中移除
            if plan.id in self._running_plans:
                del self._running_plans[plan.id]
            
            # 添加到歷史
            self._execution_history.append(plan)
            
            # 更新統計
            self._update_stats(plan)
        
        return plan
    
    async def _execute_sequential(self, plan: ActionPlan):
        """串行執行步驟"""
        
        completed_steps: Dict[str, StepResult] = {}
        
        for step in plan.steps:
            # 檢查依賴
            if not self._check_dependencies(step, completed_steps):
                if plan.stop_on_failure:
                    break
                continue
            
            # 檢查條件
            if step.condition is not None:
                try:
                    should_run = await self._safe_call(step.condition, completed_steps)
                    if not should_run:
                        step.status = StepStatus.SKIPPED
                        result = StepResult(
                            step_id=step.id,
                            step_name=step.name,
                            status=StepStatus.SKIPPED,
                            started_at=datetime.now(),
                        )
                        plan.results.append(result)
                        completed_steps[step.id] = result
                        continue
                except Exception:
                    pass
            
            # 執行步驟
            result = await self._execute_step(step, completed_steps)
            plan.results.append(result)
            completed_steps[step.id] = result
            
            # 檢查是否需要停止
            if result.status == StepStatus.FAILED and plan.stop_on_failure:
                break
    
    async def _execute_parallel(self, plan: ActionPlan):
        """並行執行步驟"""
        
        # 分層：按依賴關係分組
        layers = self._build_execution_layers(plan.steps)
        completed_steps: Dict[str, StepResult] = {}
        
        for layer in layers:
            # 並行執行同一層的步驟
            tasks = []
            for step in layer:
                task = self._execute_step(step, completed_steps)
                tasks.append(task)
            
            # 等待所有任務完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 處理結果
            for i, result in enumerate(results):
                step = layer[i]
                
                if isinstance(result, Exception):
                    step_result = StepResult(
                        step_id=step.id,
                        step_name=step.name,
                        status=StepStatus.FAILED,
                        started_at=datetime.now(),
                        error=str(result),
                    )
                else:
                    step_result = result
                
                plan.results.append(step_result)
                completed_steps[step.id] = step_result
            
            # 檢查是否有失敗
            if plan.stop_on_failure:
                failed = any(r.status == StepStatus.FAILED for r in results 
                            if isinstance(r, StepResult))
                if failed:
                    break
    
    def _build_execution_layers(
        self,
        steps: List[ActionStep]
    ) -> List[List[ActionStep]]:
        """構建執行層次（按依賴關係）"""
        
        # 計算每個步驟的依賴數
        in_degree: Dict[str, int] = {}
        step_map: Dict[str, ActionStep] = {}
        
        for step in steps:
            step_map[step.id] = step
            in_degree[step.id] = len(step.depends_on)
        
        # 拓撲排序
        layers: List[List[ActionStep]] = []
        remaining = set(step.id for step in steps)
        
        while remaining:
            # 找出沒有未滿足依賴的步驟
            layer = []
            for step_id in list(remaining):
                step = step_map[step_id]
                deps_satisfied = all(
                    dep not in remaining 
                    for dep in step.depends_on
                )
                if deps_satisfied:
                    layer.append(step)
            
            if not layer:
                # 有循環依賴
                break
            
            layers.append(layer)
            
            for step in layer:
                remaining.discard(step.id)
        
        return layers
    
    async def _execute_step(
        self,
        step: ActionStep,
        completed_steps: Dict[str, StepResult]
    ) -> StepResult:
        """執行單個步驟"""
        
        step.started_at = datetime.now()
        step.status = StepStatus.RUNNING
        
        result = StepResult(
            step_id=step.id,
            step_name=step.name,
            status=StepStatus.RUNNING,
            started_at=step.started_at,
        )
        
        try:
            # 獲取處理器
            handler = step.handler or self._handlers.get(
                step.name, self._handlers["default"]
            )
            
            # 執行處理器
            output = await self._safe_call(handler, step.params, completed_steps)
            
            step.output = output
            step.status = StepStatus.COMPLETED
            result.status = StepStatus.COMPLETED
            result.output = output
            
        except Exception as e:
            # 重試邏輯
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                result.retry_count = step.retry_count
                
                # 等待後重試
                await asyncio.sleep(0.1 * step.retry_count)
                return await self._execute_step(step, completed_steps)
            
            step.error = str(e)
            step.status = StepStatus.FAILED
            result.status = StepStatus.FAILED
            result.error = str(e)
        
        finally:
            step.completed_at = datetime.now()
            step.duration_ms = int(
                (step.completed_at - step.started_at).total_seconds() * 1000
            )
            
            result.completed_at = step.completed_at
            result.duration_ms = step.duration_ms
        
        return result
    
    def _check_dependencies(
        self,
        step: ActionStep,
        completed_steps: Dict[str, StepResult]
    ) -> bool:
        """檢查步驟依賴是否滿足"""
        
        for dep_id in step.depends_on:
            if dep_id not in completed_steps:
                return False
            
            dep_result = completed_steps[dep_id]
            if dep_result.status != StepStatus.COMPLETED:
                if not step.skip_on_failure:
                    return False
        
        return True
    
    async def rollback_plan(self, plan: ActionPlan) -> Dict[str, Any]:
        """
        回滾行動計劃
        
        Args:
            plan: 行動計劃
            
        Returns:
            回滾結果
        """
        
        rollback_results = {
            "plan_id": plan.id,
            "steps_rolled_back": 0,
            "errors": [],
        }
        
        # 反向執行回滾
        for step in reversed(plan.steps):
            if step.status != StepStatus.COMPLETED:
                continue
            
            if step.rollback_handler is None:
                continue
            
            try:
                await self._safe_call(step.rollback_handler, step.output)
                step.rollback_completed = True
                rollback_results["steps_rolled_back"] += 1
            except Exception as e:
                rollback_results["errors"].append({
                    "step": step.name,
                    "error": str(e),
                })
        
        return rollback_results
    
    def cancel_plan(self, plan_id: str) -> bool:
        """
        取消執行中的計劃
        
        Args:
            plan_id: 計劃 ID
            
        Returns:
            是否成功
        """
        
        if plan_id not in self._running_plans:
            return False
        
        plan = self._running_plans[plan_id]
        plan.status = "cancelled"
        
        # 標記所有未完成的步驟為取消
        for step in plan.steps:
            if step.status in [StepStatus.PENDING, StepStatus.RUNNING]:
                step.status = StepStatus.CANCELLED
        
        return True
    
    def create_plan(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        **kwargs
    ) -> ActionPlan:
        """
        創建行動計劃
        
        Args:
            name: 計劃名稱
            steps: 步驟定義列表
            **kwargs: 其他配置
            
        Returns:
            行動計劃
        """
        
        plan = ActionPlan(
            name=name,
            description=kwargs.get("description", ""),
            parallel=kwargs.get("parallel", False),
            stop_on_failure=kwargs.get("stop_on_failure", True),
            metadata=kwargs.get("metadata", {}),
        )
        
        for step_def in steps:
            step = ActionStep(
                name=step_def.get("name", ""),
                description=step_def.get("description", ""),
                params=step_def.get("params", {}),
                depends_on=step_def.get("depends_on", []),
                max_retries=step_def.get("max_retries", 3),
            )
            plan.steps.append(step)
        
        return plan
    
    def register_handler(self, name: str, handler: Callable):
        """註冊步驟處理器"""
        self._handlers[name] = handler
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return self._stats.copy()
    
    def get_running_plans(self) -> List[ActionPlan]:
        """獲取執行中的計劃"""
        return list(self._running_plans.values())
    
    def get_history(self, limit: int = 100) -> List[ActionPlan]:
        """獲取執行歷史"""
        return self._execution_history[-limit:]
    
    def _update_stats(self, plan: ActionPlan):
        """更新統計信息"""
        
        self._stats["total_plans"] += 1
        
        if plan.status == "completed":
            self._stats["successful_plans"] += 1
        else:
            self._stats["failed_plans"] += 1
        
        self._stats["total_steps"] += len(plan.steps)
        
        for result in plan.results:
            if result.status == StepStatus.COMPLETED:
                self._stats["successful_steps"] += 1
            elif result.status == StepStatus.FAILED:
                self._stats["failed_steps"] += 1
    
    async def _safe_call(self, func: Callable, *args, **kwargs) -> Any:
        """安全調用函數"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    # ============ 默認處理器實現 ============
    
    async def _default_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """默認處理器"""
        await asyncio.sleep(0.01)
        return {"status": "completed", "params": params}
    
    async def _connect_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """連接處理器"""
        await asyncio.sleep(0.05)
        return {
            "connected": True,
            "database": params.get("database", "default"),
        }
    
    async def _backup_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """備份處理器"""
        await asyncio.sleep(0.1)
        return {
            "backup_id": str(uuid.uuid4()),
            "table": params.get("table"),
        }
    
    async def _execute_sql_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """SQL 執行處理器"""
        await asyncio.sleep(0.05)
        return {
            "rows_affected": 1,
            "operation": params.get("operation"),
        }
    
    async def _verify_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """驗證處理器"""
        await asyncio.sleep(0.02)
        return {
            "verified": True,
            "expected": params.get("expected"),
        }
    
    async def _deploy_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """部署處理器"""
        await asyncio.sleep(0.2)
        return {
            "deployed": True,
            "strategy": params.get("strategy", "rolling"),
            "replicas": params.get("replicas", 1),
        }
    
    async def _health_check_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """健康檢查處理器"""
        await asyncio.sleep(0.05)
        return {
            "healthy": True,
            "checks_passed": 3,
        }
    
    async def _prepare_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """準備處理器"""
        await asyncio.sleep(0.05)
        return {
            "prepared": True,
            "environment": params.get("environment"),
        }
    
    async def _build_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """構建處理器"""
        await asyncio.sleep(0.1)
        return {
            "built": True,
            "version": params.get("version"),
        }
    
    async def _test_handler(
        self,
        params: Dict[str, Any],
        completed_steps: Dict[str, StepResult]
    ) -> Any:
        """測試處理器"""
        await asyncio.sleep(0.1)
        return {
            "tests_passed": True,
            "test_suite": params.get("test_suite", "smoke"),
        }
