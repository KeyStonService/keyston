#!/usr/bin/env python3
"""
SynergyMesh Orchestrator - 統一協調系統

主要職責：
1. 統一協調所有 Agent（自動化代理）
2. 統一協調所有 Island（語言平台）
3. 管理系統的整體生命週期
4. 提供統一的執行接口和監控
5. 實現 Phase 14 統一系統集成

這是 MachineNativeOps 重構後的核心協調器。
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """執行狀態"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class ComponentType(Enum):
    """組件類型"""
    AGENT = "agent"
    ISLAND = "island"
    BRIDGE = "bridge"


@dataclass
class ExecutionResult:
    """執行結果"""
    component_id: str
    component_type: ComponentType
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class SystemStatus:
    """系統狀態"""
    timestamp: datetime
    total_components: int
    active_components: int
    successful_executions: int
    failed_executions: int
    results: List[ExecutionResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_components": self.total_components,
            "active_components": self.active_components,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "results": [r.to_dict() for r in self.results]
        }


class SynergyMeshOrchestrator:
    """
    SynergyMesh 統一協調器

    核心職責：
    - 管理 Agent 編隊（Drone System）
    - 管理 Island 系統（Multi-language Platform）
    - 協調跨組件的執行
    - 監控和報告系統狀態
    - 實現 Phase 14 的統一系統集成

    架構：
    ┌─────────────────────────────────┐
    │ SynergyMeshOrchestrator         │
    │ (統一協調器)                      │
    ├─────────────────────────────────┤
    │ Agent System    │ Island System   │
    │ ─────────────────────────────── │
    │ Coordinator     │ Python Island   │
    │ Autopilot       │ Rust Island     │
    │ Deployment      │ Go Island       │
    │                 │ TypeScript      │
    │                 │ Java Island     │
    └─────────────────────────────────┘
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化協調器

        Args:
            project_root: 項目根目錄
        """
        self.project_root = project_root or Path.cwd()
        self.agents: Dict[str, Any] = {}
        self.islands: Dict[str, Any] = {}
        self.bridges: Dict[str, Any] = {}
        self.execution_results: List[ExecutionResult] = []
        self.is_running = False
        self.start_time: Optional[datetime] = None

        logger.info("🔧 SynergyMeshOrchestrator 初始化完成")

    def register_agent(
        self,
        agent_id: str,
        agent: Any,
        auto_start: bool = False
    ) -> bool:
        """
        註冊 Agent

        Args:
            agent_id: Agent ID
            agent: Agent 實例
            auto_start: 是否自動啟動

        Returns:
            是否註冊成功
        """
        try:
            self.agents[agent_id] = {
                'instance': agent,
                'auto_start': auto_start,
                'registered_at': datetime.now(),
                'status': 'initialized'
            }
            logger.info(f"✅ Agent 已註冊: {agent_id}")

            if auto_start:
                agent.start()
                logger.info(f"✅ Agent 已啟動: {agent_id}")

            return True
        except Exception as e:
            logger.error(f"❌ 註冊 Agent 失敗 {agent_id}: {e}")
            return False

    def register_island(
        self,
        island_id: str,
        island: Any,
        auto_activate: bool = False
    ) -> bool:
        """
        註冊 Island

        Args:
            island_id: Island ID
            island: Island 實例
            auto_activate: 是否自動啟動

        Returns:
            是否註冊成功
        """
        try:
            self.islands[island_id] = {
                'instance': island,
                'auto_activate': auto_activate,
                'registered_at': datetime.now(),
                'status': 'dormant'
            }
            logger.info(f"✅ Island 已註冊: {island_id}")

            if auto_activate:
                island.activate()
                logger.info(f"✅ Island 已啟動: {island_id}")

            return True
        except Exception as e:
            logger.error(f"❌ 註冊 Island 失敗 {island_id}: {e}")
            return False

    def register_bridge(
        self,
        bridge_id: str,
        bridge: Any
    ) -> bool:
        """
        註冊 Bridge

        Args:
            bridge_id: Bridge ID
            bridge: Bridge 實例

        Returns:
            是否註冊成功
        """
        try:
            self.bridges[bridge_id] = {
                'instance': bridge,
                'registered_at': datetime.now(),
                'status': 'ready'
            }
            logger.info(f"✅ Bridge 已註冊: {bridge_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 註冊 Bridge 失敗 {bridge_id}: {e}")
            return False

    async def execute_agent(self, agent_id: str) -> ExecutionResult:
        """
        執行指定 Agent

        Args:
            agent_id: Agent ID

        Returns:
            執行結果
        """
        if agent_id not in self.agents:
            return ExecutionResult(
                component_id=agent_id,
                component_type=ComponentType.AGENT,
                status=ExecutionStatus.FAILED,
                start_time=datetime.now(),
                error=f"Agent {agent_id} 未註冊"
            )

        agent_info = self.agents[agent_id]
        agent = agent_info['instance']
        start_time = datetime.now()

        result = ExecutionResult(
            component_id=agent_id,
            component_type=ComponentType.AGENT,
            status=ExecutionStatus.PENDING,
            start_time=start_time
        )

        try:
            logger.info(f"🚀 執行 Agent: {agent_id}")

            if not hasattr(agent, 'start'):
                raise AttributeError(f"Agent {agent_id} 不支援 start() 方法")

            agent.start()
            output = agent.execute() if hasattr(agent, 'execute') else None

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            result.status = ExecutionStatus.SUCCESS
            result.output = output
            result.end_time = end_time
            result.duration_ms = duration

            logger.info(f"✅ Agent 執行完成: {agent_id} ({duration:.0f}ms)")

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            result.end_time = end_time
            result.duration_ms = duration

            logger.error(f"❌ Agent 執行失敗 {agent_id}: {e}")

        self.execution_results.append(result)
        return result

    async def execute_island(self, island_id: str) -> ExecutionResult:
        """
        執行指定 Island

        Args:
            island_id: Island ID

        Returns:
            執行結果
        """
        if island_id not in self.islands:
            return ExecutionResult(
                component_id=island_id,
                component_type=ComponentType.ISLAND,
                status=ExecutionStatus.FAILED,
                start_time=datetime.now(),
                error=f"Island {island_id} 未註冊"
            )

        island_info = self.islands[island_id]
        island = island_info['instance']
        start_time = datetime.now()

        result = ExecutionResult(
            component_id=island_id,
            component_type=ComponentType.ISLAND,
            status=ExecutionStatus.PENDING,
            start_time=start_time
        )

        try:
            logger.info(f"🏝️ 執行 Island: {island_id}")

            if not hasattr(island, 'activate'):
                raise AttributeError(f"Island {island_id} 不支援 activate() 方法")

            island.activate()
            output = island.execute() if hasattr(island, 'execute') else None

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            result.status = ExecutionStatus.SUCCESS
            result.output = output
            result.end_time = end_time
            result.duration_ms = duration

            logger.info(f"✅ Island 執行完成: {island_id} ({duration:.0f}ms)")

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            result.end_time = end_time
            result.duration_ms = duration

            logger.error(f"❌ Island 執行失敗 {island_id}: {e}")

        self.execution_results.append(result)
        return result

    async def execute_all(self) -> Dict[str, Any]:
        """
        執行所有組件

        Returns:
            執行結果匯總
        """
        self.is_running = True
        self.start_time = datetime.now()

        logger.info(f"\n{'='*60}")
        logger.info("🎯 SynergyMesh 統一系統開始執行")
        logger.info(f"{'='*60}\n")

        # 執行所有 Agent
        agent_tasks = []
        for agent_id in self.agents.keys():
            agent_tasks.append(self.execute_agent(agent_id))

        # 執行所有 Island
        island_tasks = []
        for island_id in self.islands.keys():
            island_tasks.append(self.execute_island(island_id))

        # 併行執行
        await asyncio.gather(*agent_tasks, *island_tasks)

        self.is_running = False

        return self._generate_report()

    async def execute_auto_mode(self) -> Dict[str, Any]:
        """
        自動模式執行（執行所有已註冊的組件）

        Returns:
            執行結果
        """
        return await self.execute_all()

    async def execute_manual_mode(
        self,
        target_ids: List[str]
    ) -> Dict[str, Any]:
        """
        手動模式執行（執行指定的組件）

        Args:
            target_ids: 目標組件 ID 列表

        Returns:
            執行結果
        """
        tasks = []

        for target_id in target_ids:
            if target_id in self.agents:
                tasks.append(self.execute_agent(target_id))
            elif target_id in self.islands:
                tasks.append(self.execute_island(target_id))
            else:
                logger.warning(f"⚠️ 未知組件: {target_id}")

        if tasks:
            await asyncio.gather(*tasks)

        return self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """生成執行報告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0

        successful = sum(1 for r in self.execution_results if r.status == ExecutionStatus.SUCCESS)
        failed = sum(1 for r in self.execution_results if r.status == ExecutionStatus.FAILED)

        report = {
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "total_executions": len(self.execution_results),
            "successful": successful,
            "failed": failed,
            "agents_registered": len(self.agents),
            "islands_registered": len(self.islands),
            "results": [r.to_dict() for r in self.execution_results[-20:]]  # 最後 20 個結果
        }

        logger.info(f"\n{'='*60}")
        logger.info("📊 執行報告")
        logger.info(f"{'='*60}")
        logger.info(f"⏱️  總耗時: {duration:.2f}s")
        logger.info(f"✅ 成功: {successful}")
        logger.info(f"❌ 失敗: {failed}")
        logger.info(f"📦 已註冊 Agent: {len(self.agents)}")
        logger.info(f"🏝️  已註冊 Island: {len(self.islands)}")
        logger.info(f"{'='*60}\n")

        return report

    def get_status(self) -> SystemStatus:
        """
        獲取系統狀態

        Returns:
            系統狀態
        """
        successful = sum(1 for r in self.execution_results if r.status == ExecutionStatus.SUCCESS)
        failed = sum(1 for r in self.execution_results if r.status == ExecutionStatus.FAILED)

        return SystemStatus(
            timestamp=datetime.now(),
            total_components=len(self.agents) + len(self.islands),
            active_components=len([a for a in self.agents.values() if a['status'] != 'stopped']) + \
                             len([i for i in self.islands.values() if i['status'] != 'dormant']),
            successful_executions=successful,
            failed_executions=failed,
            results=self.execution_results
        )

    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有 Agent"""
        return [
            {
                "agent_id": agent_id,
                "type": type(info['instance']).__name__,
                "status": info['status'],
                "auto_start": info['auto_start'],
                "registered_at": info['registered_at'].isoformat()
            }
            for agent_id, info in self.agents.items()
        ]

    def list_islands(self) -> List[Dict[str, Any]]:
        """列出所有 Island"""
        return [
            {
                "island_id": island_id,
                "type": type(info['instance']).__name__,
                "status": info['status'],
                "auto_activate": info['auto_activate'],
                "registered_at": info['registered_at'].isoformat()
            }
            for island_id, info in self.islands.items()
        ]

    def shutdown(self) -> None:
        """關閉協調器"""
        logger.info("🛑 關閉協調器...")

        # 停止所有 Agent
        for agent_id, agent_info in self.agents.items():
            agent = agent_info['instance']
            if hasattr(agent, 'stop'):
                try:
                    agent.stop()
                    logger.info(f"✅ Agent 已停止: {agent_id}")
                except Exception as e:
                    logger.error(f"❌ 停止 Agent 失敗 {agent_id}: {e}")

        # 停止所有 Island
        for island_id, island_info in self.islands.items():
            island = island_info['instance']
            if hasattr(island, 'deactivate'):
                try:
                    island.deactivate()
                    logger.info(f"✅ Island 已停止: {island_id}")
                except Exception as e:
                    logger.error(f"❌ 停止 Island 失敗 {island_id}: {e}")

        self.is_running = False
        logger.info("✅ 協調器已關閉")


# 導出類
__all__ = [
    "SynergyMeshOrchestrator",
    "ExecutionResult",
    "SystemStatus",
    "ExecutionStatus",
    "ComponentType"
]
