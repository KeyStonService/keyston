#!/usr/bin/env python3
"""
Master Orchestrator - 主控引擎啟動器

根目錄級別的全自動化引擎調度中心。
100% 機器自主操作，負責：

1. 引擎生命週期管理
2. 引擎自動發現與註冊
3. 任務調度與分發
4. 管道編排
5. 健康監控與自我修復
6. 事件總線協調

Usage:
    # 啟動主控
    python master_orchestrator.py start

    # 啟動所有引擎
    python master_orchestrator.py start-all

    # 查看狀態
    python master_orchestrator.py status

Version: 1.0.0
"""

import asyncio
import json
import yaml
import sys
import signal
import importlib
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Type, Set, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import logging
import argparse

from engine_base import (
    BaseEngine, EngineConfig, EngineState, EngineType,
    ExecutionMode, Priority, EngineEvent, TaskResult, HealthStatus
)

# ============================================================================
# 常數定義
# ============================================================================

BASE_PATH = Path(__file__).parent.parent.parent
CONFIG_PATH = BASE_PATH / "config" / "automation"
ENGINES_PATH = BASE_PATH / "tools" / "automation" / "engines"
STATE_PATH = BASE_PATH / ".automation_state"

# ============================================================================
# 配置資料結構
# ============================================================================

@dataclass
class OrchestratorConfig:
    """主控配置"""
    name: str = "SynergyMesh-Orchestrator"
    version: str = "1.0.0"

    # 自動化設定
    auto_discover: bool = True              # 自動發現引擎
    auto_start_engines: bool = True         # 自動啟動引擎
    auto_recover: bool = True               # 自動恢復
    auto_scale: bool = False                # 自動擴縮

    # 執行設定
    max_concurrent_engines: int = 50        # 最大並行引擎數
    health_check_interval: float = 30.0     # 健康檢查間隔
    garbage_collect_interval: float = 300.0 # 垃圾回收間隔

    # 路徑配置
    engines_paths: List[str] = field(default_factory=lambda: [
        "tools/automation/engines",
        "tools/refactor",
    ])
    config_path: str = "config/automation"
    state_path: str = ".automation_state"

    # 事件設定
    event_queue_size: int = 10000
    event_retention_hours: int = 24

@dataclass
class PipelineConfig:
    """管道配置"""
    pipeline_id: str
    name: str
    description: str = ""
    stages: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True

@dataclass
class EngineRegistration:
    """引擎註冊資訊"""
    engine_id: str
    engine_name: str
    engine_class: str
    engine_type: EngineType
    module_path: str
    config: EngineConfig
    instance: Optional[BaseEngine] = None
    registered_at: str = ""
    last_health_check: str = ""
    healthy: bool = False

# ============================================================================
# 事件總線
# ============================================================================

class EventBus:
    """
    事件總線 - 引擎間通信中心
    """

    def __init__(self, max_size: int = 10000):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[EngineEvent] = []
        self._max_history = 1000
        self._running = False
        self._logger = logging.getLogger("event_bus")

    async def start(self):
        """啟動事件總線"""
        self._running = True
        asyncio.create_task(self._dispatch_loop())
        self._logger.info("事件總線已啟動")

    async def stop(self):
        """停止事件總線"""
        self._running = False

    async def publish(self, event: EngineEvent):
        """發布事件"""
        await self._queue.put(event)

        # 記錄歷史
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def subscribe(self, event_type: str, handler: Callable):
        """訂閱事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable):
        """取消訂閱"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

    async def _dispatch_loop(self):
        """事件分發循環"""
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._logger.error(f"事件分發錯誤: {e}")

    async def _dispatch(self, event: EngineEvent):
        """分發單一事件"""
        handlers = self._subscribers.get(event.event_type, [])
        handlers.extend(self._subscribers.get("*", []))  # 全局訂閱者

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self._logger.error(f"事件處理錯誤: {e}")

    def get_history(self, event_type: str = None, limit: int = 100) -> List[EngineEvent]:
        """獲取事件歷史"""
        events = self._history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

# ============================================================================
# 引擎註冊中心
# ============================================================================

class EngineRegistry:
    """
    引擎註冊中心 - 管理所有引擎的註冊與發現
    """

    def __init__(self):
        self._engines: Dict[str, EngineRegistration] = {}
        self._engine_classes: Dict[str, Type[BaseEngine]] = {}
        self._logger = logging.getLogger("engine_registry")

    def register_class(self, name: str, engine_class: Type[BaseEngine]):
        """註冊引擎類"""
        self._engine_classes[name] = engine_class
        self._logger.info(f"引擎類已註冊: {name}")

    def register_engine(self, registration: EngineRegistration):
        """註冊引擎實例"""
        registration.registered_at = datetime.now().isoformat()
        self._engines[registration.engine_id] = registration
        self._logger.info(f"引擎已註冊: {registration.engine_name} ({registration.engine_id})")

    def unregister_engine(self, engine_id: str):
        """取消註冊引擎"""
        if engine_id in self._engines:
            del self._engines[engine_id]
            self._logger.info(f"引擎已取消註冊: {engine_id}")

    def get_engine(self, engine_id: str) -> Optional[EngineRegistration]:
        """獲取引擎"""
        return self._engines.get(engine_id)

    def get_all_engines(self) -> List[EngineRegistration]:
        """獲取所有引擎"""
        return list(self._engines.values())

    def get_engines_by_type(self, engine_type: EngineType) -> List[EngineRegistration]:
        """按類型獲取引擎"""
        return [e for e in self._engines.values() if e.engine_type == engine_type]

    def get_healthy_engines(self) -> List[EngineRegistration]:
        """獲取健康的引擎"""
        return [e for e in self._engines.values() if e.healthy]

    def get_engine_class(self, name: str) -> Optional[Type[BaseEngine]]:
        """獲取引擎類"""
        return self._engine_classes.get(name)

    def discover_engines(self, search_paths: List[Path]) -> List[Dict[str, Any]]:
        """發現引擎"""
        discovered = []

        for search_path in search_paths:
            if not search_path.exists():
                continue

            # 搜尋 Python 模組
            for py_file in search_path.rglob("*.py"):
                if py_file.name.startswith('_'):
                    continue

                try:
                    engine_info = self._inspect_module(py_file)
                    if engine_info:
                        discovered.extend(engine_info)
                except Exception as e:
                    self._logger.debug(f"檢查模組失敗 {py_file}: {e}")

            # 搜尋配置檔
            for config_file in search_path.rglob("engine.yaml"):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    if config:
                        config['config_path'] = str(config_file)
                        discovered.append(config)
                except Exception as e:
                    self._logger.debug(f"讀取配置失敗 {config_file}: {e}")

        return discovered

    def _inspect_module(self, module_path: Path) -> List[Dict[str, Any]]:
        """檢查模組中的引擎類"""
        engines = []

        try:
            spec = importlib.util.spec_from_file_location(
                module_path.stem, module_path
            )
            if spec is None or spec.loader is None:
                return engines

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 尋找 BaseEngine 子類
            for name, obj in vars(module).items():
                if (isinstance(obj, type) and
                    issubclass(obj, BaseEngine) and
                    obj is not BaseEngine and
                    not name.startswith('_')):

                    # 獲取引擎資訊
                    engines.append({
                        "class_name": name,
                        "module_path": str(module_path),
                        "engine_type": getattr(obj, 'ENGINE_TYPE', EngineType.EXECUTION).value,
                    })

        except Exception as e:
            pass

        return engines

# ============================================================================
# 引擎調度器
# ============================================================================

class EngineScheduler:
    """
    引擎調度器 - 任務調度與分發
    """

    def __init__(self, registry: EngineRegistry, event_bus: EventBus):
        self._registry = registry
        self._event_bus = event_bus
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._running = False
        self._logger = logging.getLogger("engine_scheduler")

    async def start(self):
        """啟動調度器"""
        self._running = True
        asyncio.create_task(self._schedule_loop())
        self._logger.info("調度器已啟動")

    async def stop(self):
        """停止調度器"""
        self._running = False

    async def schedule_task(self, task: Dict[str, Any], priority: Priority = Priority.NORMAL):
        """調度任務"""
        await self._task_queue.put((priority.value, task))

    async def _schedule_loop(self):
        """調度循環"""
        while self._running:
            try:
                _, task = await asyncio.wait_for(self._task_queue.get(), timeout=1.0)
                await self._dispatch_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._logger.error(f"調度錯誤: {e}")

    async def _dispatch_task(self, task: Dict[str, Any]):
        """分發任務"""
        target_engine_id = task.get("target_engine_id")
        target_engine_type = task.get("target_engine_type")

        # 找到合適的引擎
        if target_engine_id:
            reg = self._registry.get_engine(target_engine_id)
            if reg and reg.instance and reg.healthy:
                await reg.instance.submit_task(task)
                return

        elif target_engine_type:
            engines = self._registry.get_engines_by_type(EngineType(target_engine_type))
            healthy_engines = [e for e in engines if e.healthy and e.instance]
            if healthy_engines:
                # 負載均衡 (簡單輪詢)
                engine = healthy_engines[0]
                await engine.instance.submit_task(task)
                return

        self._logger.warning(f"找不到合適的引擎執行任務: {task.get('task_id')}")

# ============================================================================
# 管道執行器
# ============================================================================

class PipelineExecutor:
    """
    管道執行器 - 編排多引擎工作流
    """

    def __init__(self, registry: EngineRegistry, scheduler: EngineScheduler):
        self._registry = registry
        self._scheduler = scheduler
        self._pipelines: Dict[str, PipelineConfig] = {}
        self._running_pipelines: Dict[str, Dict] = {}
        self._logger = logging.getLogger("pipeline_executor")

    def register_pipeline(self, config: PipelineConfig):
        """註冊管道"""
        self._pipelines[config.pipeline_id] = config
        self._logger.info(f"管道已註冊: {config.name}")

    async def execute_pipeline(self, pipeline_id: str, input_data: Dict = None) -> Dict[str, Any]:
        """執行管道"""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return {"success": False, "error": f"管道不存在: {pipeline_id}"}

        if not pipeline.enabled:
            return {"success": False, "error": "管道已停用"}

        execution_id = f"{pipeline_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self._running_pipelines[execution_id] = {
            "pipeline_id": pipeline_id,
            "started_at": datetime.now().isoformat(),
            "current_stage": 0,
            "status": "running",
        }

        results = []
        current_data = input_data or {}

        try:
            for i, stage in enumerate(pipeline.stages):
                self._running_pipelines[execution_id]["current_stage"] = i

                stage_result = await self._execute_stage(stage, current_data)
                results.append(stage_result)

                if not stage_result.get("success"):
                    self._running_pipelines[execution_id]["status"] = "failed"
                    return {
                        "success": False,
                        "error": f"階段 {i} 失敗",
                        "results": results,
                    }

                # 傳遞數據到下一階段
                current_data = stage_result.get("output", current_data)

            self._running_pipelines[execution_id]["status"] = "completed"
            return {
                "success": True,
                "execution_id": execution_id,
                "results": results,
            }

        except Exception as e:
            self._running_pipelines[execution_id]["status"] = "error"
            return {
                "success": False,
                "error": str(e),
                "results": results,
            }

    async def _execute_stage(self, stage: Dict[str, Any], input_data: Dict) -> Dict[str, Any]:
        """執行單一階段"""
        engine_id = stage.get("engine_id")
        engine_type = stage.get("engine_type")
        operation = stage.get("operation")

        # 找到引擎
        engine = None
        if engine_id:
            reg = self._registry.get_engine(engine_id)
            if reg and reg.instance:
                engine = reg.instance
        elif engine_type:
            engines = self._registry.get_engines_by_type(EngineType(engine_type))
            healthy = [e for e in engines if e.healthy and e.instance]
            if healthy:
                engine = healthy[0].instance

        if not engine:
            return {"success": False, "error": "找不到引擎"}

        # 執行任務
        task = {
            "operation": operation,
            "input": input_data,
            **stage.get("params", {}),
        }

        result = await engine.execute_now(task)
        return {
            "success": result.success,
            "output": result.result,
            "error": result.error,
            "duration_ms": result.duration_ms,
        }

# ============================================================================
# 健康監控器
# ============================================================================

class HealthMonitor:
    """
    健康監控器 - 監控所有引擎健康狀態
    """

    def __init__(self, registry: EngineRegistry, event_bus: EventBus):
        self._registry = registry
        self._event_bus = event_bus
        self._running = False
        self._check_interval = 30.0
        self._logger = logging.getLogger("health_monitor")

    async def start(self, interval: float = 30.0):
        """啟動監控"""
        self._running = True
        self._check_interval = interval
        asyncio.create_task(self._monitor_loop())
        self._logger.info("健康監控已啟動")

    async def stop(self):
        """停止監控"""
        self._running = False

    async def _monitor_loop(self):
        """監控循環"""
        while self._running:
            try:
                await self._check_all_engines()
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                self._logger.error(f"監控錯誤: {e}")

    async def _check_all_engines(self):
        """檢查所有引擎"""
        for reg in self._registry.get_all_engines():
            try:
                if reg.instance:
                    health = reg.instance.get_health()
                    reg.healthy = health.healthy
                    reg.last_health_check = datetime.now().isoformat()

                    if not health.healthy:
                        await self._handle_unhealthy(reg, health)
                else:
                    reg.healthy = False

            except Exception as e:
                self._logger.error(f"檢查引擎 {reg.engine_id} 失敗: {e}")
                reg.healthy = False

    async def _handle_unhealthy(self, reg: EngineRegistration, health: HealthStatus):
        """處理不健康的引擎"""
        self._logger.warning(f"引擎不健康: {reg.engine_name} - {health.state.name}")

        event = EngineEvent.create("engine.unhealthy", reg.engine_id, {
            "health": asdict(health),
        })
        await self._event_bus.publish(event)

        # 自動恢復嘗試
        if reg.instance and reg.config.auto_recover:
            if health.state == EngineState.ERROR:
                self._logger.info(f"嘗試恢復引擎: {reg.engine_name}")
                await reg.instance._recover()

    def get_system_health(self) -> Dict[str, Any]:
        """獲取系統健康概覽"""
        engines = self._registry.get_all_engines()
        healthy = [e for e in engines if e.healthy]

        return {
            "total_engines": len(engines),
            "healthy_engines": len(healthy),
            "unhealthy_engines": len(engines) - len(healthy),
            "health_ratio": len(healthy) / len(engines) if engines else 1.0,
            "engines": [
                {
                    "id": e.engine_id,
                    "name": e.engine_name,
                    "healthy": e.healthy,
                    "state": e.instance.state.name if e.instance else "N/A",
                }
                for e in engines
            ],
        }

# ============================================================================
# 主控協調器
# ============================================================================

class MasterOrchestrator:
    """
    主控協調器 - 根目錄級別的自動化引擎啟動器

    職責：
    1. 引擎自動發現與註冊
    2. 引擎生命週期管理
    3. 任務調度與分發
    4. 管道編排執行
    5. 健康監控與自我修復
    6. 事件協調與日誌
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()

        # 核心組件
        self.event_bus = EventBus(max_size=self.config.event_queue_size)
        self.registry = EngineRegistry()
        self.scheduler = EngineScheduler(self.registry, self.event_bus)
        self.pipeline_executor = PipelineExecutor(self.registry, self.scheduler)
        self.health_monitor = HealthMonitor(self.registry, self.event_bus)

        # 狀態
        self._running = False
        self._start_time: Optional[datetime] = None

        # 日誌
        self._logger = logging.getLogger("master_orchestrator")
        self._setup_logging()

    def _setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    # ========================================================================
    # 生命週期
    # ========================================================================

    async def start(self) -> bool:
        """啟動主控"""
        self._logger.info("=" * 60)
        self._logger.info("SynergyMesh 自動化主控啟動中...")
        self._logger.info("=" * 60)

        try:
            # 啟動事件總線
            await self.event_bus.start()

            # 啟動調度器
            await self.scheduler.start()

            # 啟動健康監控
            await self.health_monitor.start(self.config.health_check_interval)

            # 自動發現引擎
            if self.config.auto_discover:
                await self._discover_and_register_engines()

            # 自動啟動引擎
            if self.config.auto_start_engines:
                await self._start_all_engines()

            # 載入管道配置
            await self._load_pipelines()

            self._running = True
            self._start_time = datetime.now()

            self._logger.info("=" * 60)
            self._logger.info("主控啟動完成")
            self._logger.info(f"  已註冊引擎: {len(self.registry.get_all_engines())}")
            self._logger.info(f"  已載入管道: {len(self.pipeline_executor._pipelines)}")
            self._logger.info("=" * 60)

            # 設置信號處理
            self._setup_signal_handlers()

            return True

        except Exception as e:
            self._logger.error(f"啟動失敗: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def stop(self):
        """停止主控"""
        self._logger.info("正在停止主控...")

        # 停止所有引擎
        await self._stop_all_engines()

        # 停止組件
        await self.health_monitor.stop()
        await self.scheduler.stop()
        await self.event_bus.stop()

        self._running = False
        self._logger.info("主控已停止")

    async def run_forever(self):
        """持續運行"""
        while self._running:
            await asyncio.sleep(1)

    def _setup_signal_handlers(self):
        """設置信號處理"""
        def handle_signal(sig, frame):
            self._logger.info(f"收到信號 {sig}，準備停止...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    # ========================================================================
    # 引擎管理
    # ========================================================================

    async def _discover_and_register_engines(self):
        """發現並註冊引擎"""
        self._logger.info("發現引擎中...")

        search_paths = [BASE_PATH / p for p in self.config.engines_paths]
        discovered = self.registry.discover_engines(search_paths)

        self._logger.info(f"發現 {len(discovered)} 個引擎")

        for engine_info in discovered:
            try:
                await self._register_engine_from_info(engine_info)
            except Exception as e:
                self._logger.error(f"註冊引擎失敗: {e}")

    async def _register_engine_from_info(self, info: Dict[str, Any]):
        """從資訊註冊引擎"""
        module_path = info.get("module_path")
        class_name = info.get("class_name")

        if not module_path or not class_name:
            return

        try:
            # 動態載入模組
            spec = importlib.util.spec_from_file_location(
                Path(module_path).stem, module_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 獲取引擎類
            engine_class = getattr(module, class_name)

            # 建立配置
            config = EngineConfig(
                engine_name=class_name,
                engine_type=EngineType(info.get("engine_type", "execution")),
                execution_mode=ExecutionMode.AUTONOMOUS,
            )

            # 建立實例
            instance = engine_class(config)

            # 註冊
            registration = EngineRegistration(
                engine_id=config.engine_id,
                engine_name=class_name,
                engine_class=class_name,
                engine_type=config.engine_type,
                module_path=module_path,
                config=config,
                instance=instance,
            )

            self.registry.register_engine(registration)

        except Exception as e:
            self._logger.error(f"載入引擎 {class_name} 失敗: {e}")

    async def _start_all_engines(self):
        """啟動所有引擎"""
        self._logger.info("啟動所有引擎...")

        for reg in self.registry.get_all_engines():
            if reg.instance:
                try:
                    success = await reg.instance.start()
                    if success:
                        reg.healthy = True
                        self._logger.info(f"  ✓ {reg.engine_name}")
                    else:
                        self._logger.warning(f"  ✗ {reg.engine_name} 啟動失敗")
                except Exception as e:
                    self._logger.error(f"  ✗ {reg.engine_name}: {e}")

    async def _stop_all_engines(self):
        """停止所有引擎"""
        self._logger.info("停止所有引擎...")

        for reg in self.registry.get_all_engines():
            if reg.instance:
                try:
                    await reg.instance.stop()
                    self._logger.info(f"  ✓ {reg.engine_name} 已停止")
                except Exception as e:
                    self._logger.error(f"  ✗ {reg.engine_name}: {e}")

    async def start_engine(self, engine_id: str) -> bool:
        """啟動指定引擎"""
        reg = self.registry.get_engine(engine_id)
        if not reg or not reg.instance:
            return False
        return await reg.instance.start()

    async def stop_engine(self, engine_id: str) -> bool:
        """停止指定引擎"""
        reg = self.registry.get_engine(engine_id)
        if not reg or not reg.instance:
            return False
        return await reg.instance.stop()

    # ========================================================================
    # 管道管理
    # ========================================================================

    async def _load_pipelines(self):
        """載入管道配置"""
        config_path = BASE_PATH / self.config.config_path / "pipelines"
        if not config_path.exists():
            return

        for pipeline_file in config_path.glob("*.yaml"):
            try:
                with open(pipeline_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                pipeline = PipelineConfig(
                    pipeline_id=data.get("pipeline_id", pipeline_file.stem),
                    name=data.get("name", pipeline_file.stem),
                    description=data.get("description", ""),
                    stages=data.get("stages", []),
                    triggers=data.get("triggers", []),
                    enabled=data.get("enabled", True),
                )

                self.pipeline_executor.register_pipeline(pipeline)

            except Exception as e:
                self._logger.error(f"載入管道失敗 {pipeline_file}: {e}")

    async def execute_pipeline(self, pipeline_id: str, input_data: Dict = None) -> Dict:
        """執行管道"""
        return await self.pipeline_executor.execute_pipeline(pipeline_id, input_data)

    # ========================================================================
    # 任務調度
    # ========================================================================

    async def submit_task(self, task: Dict[str, Any], priority: Priority = Priority.NORMAL):
        """提交任務"""
        await self.scheduler.schedule_task(task, priority)

    async def execute_task(self, engine_id: str, task: Dict[str, Any]) -> TaskResult:
        """直接執行任務"""
        reg = self.registry.get_engine(engine_id)
        if not reg or not reg.instance:
            return TaskResult(
                task_id=task.get("task_id", ""),
                success=False,
                error="引擎不存在或未啟動",
            )
        return await reg.instance.execute_now(task)

    # ========================================================================
    # 狀態查詢
    # ========================================================================

    def get_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        uptime = datetime.now() - self._start_time if self._start_time else timedelta(0)

        return {
            "name": self.config.name,
            "version": self.config.version,
            "running": self._running,
            "uptime_seconds": uptime.total_seconds(),
            "started_at": self._start_time.isoformat() if self._start_time else None,
            "health": self.health_monitor.get_system_health(),
            "engines": [
                {
                    "id": e.engine_id,
                    "name": e.engine_name,
                    "type": e.engine_type.value,
                    "healthy": e.healthy,
                    "state": e.instance.state.name if e.instance else "N/A",
                }
                for e in self.registry.get_all_engines()
            ],
            "pipelines": list(self.pipeline_executor._pipelines.keys()),
        }

# ============================================================================
# CLI 入口
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="SynergyMesh Master Orchestrator - 主控引擎啟動器"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # start 命令
    start_parser = subparsers.add_parser("start", help="啟動主控")
    start_parser.add_argument("--config", "-c", help="配置檔案")

    # start-all 命令
    start_all_parser = subparsers.add_parser("start-all", help="啟動所有引擎")

    # stop 命令
    stop_parser = subparsers.add_parser("stop", help="停止主控")

    # status 命令
    status_parser = subparsers.add_parser("status", help="查看狀態")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出引擎")

    # execute 命令
    execute_parser = subparsers.add_parser("execute", help="執行管道")
    execute_parser.add_argument("--pipeline", "-p", required=True, help="管道 ID")
    execute_parser.add_argument("--input", "-i", help="輸入數據 (JSON)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    orchestrator = MasterOrchestrator()

    if args.command == "start":
        success = await orchestrator.start()
        if success:
            await orchestrator.run_forever()

    elif args.command == "start-all":
        await orchestrator.start()
        status = orchestrator.get_status()
        print(yaml.dump(status, allow_unicode=True, default_flow_style=False))
        await orchestrator.run_forever()

    elif args.command == "status":
        await orchestrator.start()
        status = orchestrator.get_status()
        print(yaml.dump(status, allow_unicode=True, default_flow_style=False))
        await orchestrator.stop()

    elif args.command == "list":
        await orchestrator.start()
        for engine in orchestrator.registry.get_all_engines():
            print(f"- {engine.engine_name} ({engine.engine_id}): {engine.engine_type.value}")
        await orchestrator.stop()

    elif args.command == "execute":
        await orchestrator.start()
        input_data = json.loads(args.input) if args.input else {}
        result = await orchestrator.execute_pipeline(args.pipeline, input_data)
        print(yaml.dump(result, allow_unicode=True, default_flow_style=False))
        await orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(main())
