"""
Workflows for Instant Generation
即時生成工作流

實現DAG工作流編排、並行處理和優化調度
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from ..agents import BaseAgent, AgentTask, AgentResult, AgentType, create_agent

class WorkflowStatus(Enum):
    """工作流狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """任務狀態枚舉"""
    WAITING = "waiting"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowTask:
    """工作流任務"""
    task_id: str
    agent_type: AgentType
    input_data: Dict[str, Any]
    dependencies: Set[str] = field(default_factory=set)
    priority: int = 1
    timeout: int = 300
    status: TaskStatus = TaskStatus.WAITING
    result: Optional[AgentResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class Workflow:
    """工作流定義"""
    workflow_id: str
    name: str
    tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, AgentResult] = field(default_factory=dict)

class DAGOrchestrator:
    """DAG編排器 - 處理有向無環圖工作流"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.workflows: Dict[str, Workflow] = {}
        self.task_dependencies: Dict[str, Set[str]] = {}
        
    def create_workflow(self, workflow_id: str, name: str) -> Workflow:
        """創建新工作流"""
        workflow = Workflow(workflow_id=workflow_id, name=name)
        self.workflows[workflow_id] = workflow
        return workflow
    
    def add_task(self, workflow_id: str, task: WorkflowTask) -> None:
        """添加任務到工作流"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.tasks[task.task_id] = task
        
        # 更新依賴關係
        self.task_dependencies[task.task_id] = task.dependencies
    
    def validate_workflow(self, workflow_id: str) -> bool:
        """驗證工作流是否有循環依賴"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        # 使用DFS檢查循環依賴
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep in self.task_dependencies.get(task_id, set()):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        for task_id in workflow.tasks:
            if task_id not in visited:
                if has_cycle(task_id):
                    self.logger.error(f"Cycle detected in workflow {workflow_id}")
                    return False
        
        return True
    
    def get_ready_tasks(self, workflow_id: str) -> List[WorkflowTask]:
        """獲取準備執行的任務"""
        if workflow_id not in self.workflows:
            return []
        
        workflow = self.workflows[workflow_id]
        ready_tasks = []
        
        for task in workflow.tasks.values():
            if task.status != TaskStatus.WAITING:
                continue
            
            # 檢查所有依賴是否已完成
            dependencies_completed = True
            for dep_id in task.dependencies:
                if dep_id in workflow.tasks:
                    dependency_task = workflow.tasks[dep_id]
                    if dependency_task.status != TaskStatus.COMPLETED:
                        dependencies_completed = False
                        break
            
            if dependencies_completed:
                task.status = TaskStatus.READY
                ready_tasks.append(task)
        
        return sorted(ready_tasks, key=lambda t: t.priority, reverse=True)

class ParallelProcessor:
    """並行處理器 - 管理多代理並行執行"""
    
    def __init__(self, max_workers: int = 6, config: Dict[str, Any] = None):
        self.max_workers = max_workers
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.agents: Dict[AgentType, BaseAgent] = {}
        
        # 初始化代理
        self._initialize_agents()
    
    def _initialize_agents(self) -> None:
        """初始化所有代理"""
        for agent_type in AgentType:
            try:
                agent = create_agent(agent_type, self.config)
                self.agents[agent_type] = agent
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {agent_type}: {e}")
    
    async def execute_tasks(self, tasks: List[WorkflowTask]) -> List[AgentResult]:
        """並行執行任務列表"""
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def execute_with_semaphore(task: WorkflowTask) -> AgentResult:
            async with semaphore:
                return await self._execute_single_task(task)
        
        # 創建並行執行任務
        execution_tasks = [execute_with_semaphore(task) for task in tasks]
        
        # 等待所有任務完成
        results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # 處理異常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Task {tasks[i].task_id} failed with exception: {result}")
                processed_results.append(AgentResult(
                    task_id=tasks[i].task_id,
                    agent_type=tasks[i].agent_type,
                    success=False,
                    output_data={},
                    execution_time=0,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_single_task(self, task: WorkflowTask) -> AgentResult:
        """執行單個任務"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            agent = self.agents.get(task.agent_type)
            if not agent:
                raise ValueError(f"Agent {task.agent_type} not available")
            
            # 創建代理任務
            agent_task = AgentTask(
                task_id=task.task_id,
                agent_type=task.agent_type,
                input_data=task.input_data,
                priority=task.priority,
                timeout=task.timeout,
                dependencies=list(task.dependencies)
            )
            
            # 執行任務
            result = await agent.execute_with_timeout(agent_task)
            
            task.result = result
            task.completed_at = datetime.now()
            
            if result.success:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task {task.task_id} execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            
            return AgentResult(
                task_id=task.task_id,
                agent_type=task.agent_type,
                success=False,
                output_data={},
                execution_time=0,
                error_message=str(e)
            )

class InstantGenerationWorkflow:
    """即時生成工作流 - 主工作流實現"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.orchestrator = DAGOrchestrator(config)
        self.processor = ParallelProcessor(config=config)
        
        # 工作流統計
        self.workflow_stats = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_execution_time": 0.0
        }
    
    async def execute_instant_generation(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """執行完整的即時生成工作流"""
        workflow_id = f"instant_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 創建工作流
            workflow = self.orchestrator.create_workflow(
                workflow_id=workflow_id,
                name="Instant Generation Workflow"
            )
            
            # 創建任務序列
            tasks = self._create_instant_generation_tasks(user_input, context)
            
            # 添加任務到工作流
            for task in tasks:
                self.orchestrator.add_task(workflow_id, task)
            
            # 驗證工作流
            if not self.orchestrator.validate_workflow(workflow_id):
                raise ValueError("Invalid workflow: contains cycles")
            
            # 執行工作流
            result = await self._execute_workflow(workflow_id)
            
            # 更新統計
            self._update_stats(workflow, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Instant generation workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    def _create_instant_generation_tasks(self, user_input: str, context: Dict[str, Any]) -> List[WorkflowTask]:
        """創建即時生成任務序列"""
        tasks = []
        
        # 任務1: 輸入分析
        input_analysis_task = WorkflowTask(
            task_id="input_analysis",
            agent_type=AgentType.INPUT_ANALYSIS,
            input_data={"user_input": user_input, "context": context or {}},
            dependencies=set(),
            priority=10
        )
        tasks.append(input_analysis_task)
        
        # 任務2: 架構設計 (依賴輸入分析)
        architecture_task = WorkflowTask(
            task_id="architecture_design",
            agent_type=AgentType.ARCHITECTURE_DESIGN,
            input_data={},  # 將在執行時填充
            dependencies={"input_analysis"},
            priority=9
        )
        tasks.append(architecture_task)
        
        # 任務3: 代碼生成 (依賴輸入分析和架構設計)
        code_generation_task = WorkflowTask(
            task_id="code_generation",
            agent_type=AgentType.CODE_GENERATION,
            input_data={},  # 將在執行時填充
            dependencies={"input_analysis", "architecture_design"},
            priority=8
        )
        tasks.append(code_generation_task)
        
        # 任務4: 測試 (依賴代碼生成)
        testing_task = WorkflowTask(
            task_id="testing",
            agent_type=AgentType.TESTING,
            input_data={},  # 將在執行時填充
            dependencies={"code_generation"},
            priority=7
        )
        tasks.append(testing_task)
        
        # 任務5: 部署 (依賴測試)
        deployment_task = WorkflowTask(
            task_id="deployment",
            agent_type=AgentType.DEPLOYMENT,
            input_data={},  # 將在執行時填充
            dependencies={"testing"},
            priority=6
        )
        tasks.append(deployment_task)
        
        # 任務6: 優化 (依賴部署)
        optimization_task = WorkflowTask(
            task_id="optimization",
            agent_type=AgentType.OPTIMIZATION,
            input_data={},  # 將在執行時填充
            dependencies={"deployment"},
            priority=5
        )
        tasks.append(optimization_task)
        
        return tasks
    
    async def _execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """執行工作流"""
        workflow = self.orchestrator.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        results = {}
        
        try:
            while True:
                # 獲取準備執行的任務
                ready_tasks = self.orchestrator.get_ready_tasks(workflow_id)
                
                if not ready_tasks:
                    # 檢查是否所有任務都已完成
                    all_completed = all(
                        task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED]
                        for task in workflow.tasks.values()
                    )
                    
                    if all_completed:
                        break
                    else:
                        # 等待正在運行的任務
                        await asyncio.sleep(0.1)
                        continue
                
                # 更新任務輸入數據
                for task in ready_tasks:
                    task.input_data = self._prepare_task_input(task, results)
                
                # 並行執行準備好的任務
                task_results = await self.processor.execute_tasks(ready_tasks)
                
                # 處理結果
                for result in task_results:
                    results[result.task_id] = result
                    
                    if result.task_id in workflow.tasks:
                        workflow.tasks[result.task_id].result = result
                
                # 檢查是否有失敗的關鍵任務
                critical_failures = [
                    task_id for task_id, result in results.items()
                    if not result.success and self._is_critical_task(task_id)
                ]
                
                if critical_failures:
                    raise RuntimeError(f"Critical tasks failed: {critical_failures}")
            
            # 工作流完成
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.results = results
            
            execution_time = (workflow.completed_at - workflow.started_at).total_seconds()
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "execution_time_seconds": execution_time,
                "results": results,
                "summary": self._generate_summary(results)
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            self.logger.error(f"Workflow {workflow_id} failed: {e}")
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "partial_results": results
            }
    
    def _prepare_task_input(self, task: WorkflowTask, previous_results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """準備任務輸入數據"""
        base_input = task.input_data.copy()
        
        # 添加依賴任務的結果
        for dep_id in task.dependencies:
            if dep_id in previous_results:
                dep_result = previous_results[dep_id]
                if dep_result.success:
                    base_input[dep_id] = dep_result.output_data
        
        return base_input
    
    def _is_critical_task(self, task_id: str) -> bool:
        """檢查是否是關鍵任務"""
        critical_tasks = {"input_analysis", "architecture_design", "code_generation"}
        return task_id in critical_tasks
    
    def _generate_summary(self, results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """生成執行摘要"""
        successful_tasks = sum(1 for r in results.values() if r.success)
        total_tasks = len(results)
        total_time = sum(r.execution_time for r in results.values())
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": total_tasks - successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "total_execution_time": total_time,
            "average_task_time": total_time / total_tasks if total_tasks > 0 else 0
        }
    
    def _update_stats(self, workflow: Workflow, result: Dict[str, Any]) -> None:
        """更新工作流統計"""
        self.workflow_stats["total_workflows"] += 1
        
        if result.get("success", False):
            self.workflow_stats["successful_workflows"] += 1
        else:
            self.workflow_stats["failed_workflows"] += 1
        
        # 更新平均執行時間
        execution_time = result.get("execution_time_seconds", 0)
        total_successful = self.workflow_stats["successful_workflows"]
        if total_successful > 0:
            current_avg = self.workflow_stats["average_execution_time"]
            self.workflow_stats["average_execution_time"] = (
                (current_avg * (total_successful - 1) + execution_time) / total_successful
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取工作流統計信息"""
        return self.workflow_stats.copy()

__all__ = [
    "InstantGenerationWorkflow",
    "DAGOrchestrator", 
    "ParallelProcessor",
    "Workflow",
    "WorkflowTask",
    "WorkflowStatus",
    "TaskStatus"
]