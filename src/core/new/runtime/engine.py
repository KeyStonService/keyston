"""
MachineNativeOps Runtime Engine
統一運行時引擎 - 核心組件
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """任務定義"""
    id: str
    name: str
    handler: Callable
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class MachineNativeOpsEngine:
    """MachineNativeOps 主引擎"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.is_running = False
        self.version = "1.0.0"
        
    async def start(self):
        """啟動引擎"""
        if self.is_running:
            logger.warning("⚠️ 引擎已在運行中")
            return
        
        logger.info("🚀 啟動 MachineNativeOps 引擎 v%s", self.version)
        self.is_running = True
        logger.info("✅ 引擎啟動完成")
    
    async def stop(self):
        """停止引擎"""
        if not self.is_running:
            return
        
        logger.info("🛑 停止 MachineNativeOps 引擎")
        self.is_running = False
        logger.info("✅ 引擎已停止")
    
    async def submit_task(self, name: str, handler: Callable, 
                         parameters: Dict[str, Any] = None) -> str:
        """提交任務"""
        task = Task(
            id=str(uuid.uuid4()),
            name=name,
            handler=handler,
            parameters=parameters or {}
        )
        
        self.tasks[task.id] = task
        
        # 執行任務
        asyncio.create_task(self._execute_task(task))
        
        return task.id
    
    async def _execute_task(self, task: Task):
        """執行任務"""
        logger.info(f"🏃 執行任務: {task.name}")
        
        task.status = TaskStatus.RUNNING
        
        try:
            if asyncio.iscoroutinefunction(task.handler):
                result = await task.handler(**task.parameters)
            else:
                result = task.handler(**task.parameters)
            
            task.status = TaskStatus.COMPLETED
            logger.info(f"✅ 任務完成: {task.name}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            logger.error(f"❌ 任務失敗: {task.name} - {e}")

# 全局引擎實例
engine = MachineNativeOpsEngine()