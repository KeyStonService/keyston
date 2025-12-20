"""
MachineNativeOps Business Services
業務服務層 - 核心業務邏輯實現
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

try:
    from ..new.core import get_core_engine
    from ..new.governance.policy_engine import PolicyEngine
    from ..new.security.auth import get_current_user
except ImportError:
    # 為測試目的提供模擬實現
    class MockCoreEngine:
        async def initialize(self):
            pass
        async def emit_event(self, event, data):
            pass
    
    def get_core_engine():
        return MockCoreEngine()
    
    class PolicyEngine:
        async def initialize(self):
            pass
        async def evaluate(self, policy):
            class MockResult:
                allowed = True
                reason = "Test mode"
            return MockResult()
    
    def get_current_user():
        return "admin"
from .models import (
    Project, Task, Resource, WorkflowExecution,
    BusinessMetrics, BusinessStatus, Priority,
    ProjectQuery, TaskQuery, CreateProjectRequest, 
    CreateTaskRequest, UpdateTaskRequest
)


class BusinessServiceManager:
    """業務服務管理器"""
    
    def __init__(self):
        self.core_engine = get_core_engine()
        self.policy_engine = PolicyEngine()
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.resources: Dict[str, Resource] = {}
        self.workflows: Dict[str, WorkflowExecution] = {}
        self.project_tasks: Dict[str, List[str]] = defaultdict(list)
        
    async def initialize(self):
        """初始化業務服務"""
        await self.core_engine.initialize()
        await self.policy_engine.initialize()
        await self._load_default_resources()
        
    async def _load_default_resources(self):
        """加載默認資源"""
        default_resources = [
            Resource(
                id="compute-standard",
                name="Standard Compute",
                type="compute",
                capacity=100.0,
                cost_per_hour=0.50
            ),
            Resource(
                id="compute-premium",
                name="Premium Compute", 
                type="compute",
                capacity=200.0,
                cost_per_hour=1.20
            ),
            Resource(
                id="storage-standard",
                name="Standard Storage",
                type="storage",
                capacity=1000.0,
                cost_per_hour=0.01
            )
        ]
        
        for resource in default_resources:
            self.resources[resource.id] = resource
    
    # 項目管理
    async def create_project(self, request: CreateProjectRequest) -> Project:
        """創建項目"""
        # 治理檢查
        policy_check = await self.policy_engine.evaluate({
            "action": "create_project",
            "user": await get_current_user(),
            "project_data": request.dict()
        })
        
        if not policy_check.allowed:
            raise PermissionError(f"Policy violation: {policy_check.reason}")
        
        project = Project(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            owner=request.owner,
            priority=request.priority,
            deadline=request.deadline,
            tags=request.tags,
            metadata=request.metadata
        )
        
        self.projects[project.id] = project
        
        # 觸發核心引擎事件
        await self.core_engine.emit_event("project_created", {
            "project_id": project.id,
            "owner": project.owner
        })
        
        return project
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """獲取項目"""
        return self.projects.get(project_id)
    
    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        """更新項目"""
        if project_id not in self.projects:
            return None
            
        project = self.projects[project_id]
        
        # 更新字段
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.updated_at = datetime.now()
        
        # 觸發核心引擎事件
        await self.core_engine.emit_event("project_updated", {
            "project_id": project_id
        })
        
        return project
    
    async def delete_project(self, project_id: str) -> bool:
        """刪除項目"""
        if project_id not in self.projects:
            return False
        
        # 檢查是否有任務
        if self.project_tasks[project_id]:
            raise ValueError("Cannot delete project with existing tasks")
        
        del self.projects[project_id]
        
        # 觸發核心引擎事件
        await self.core_engine.emit_event("project_deleted", {
            "project_id": project_id
        })
        
        return True
    
    async def list_projects(self, query: ProjectQuery) -> List[Project]:
        """查詢項目列表"""
        projects = list(self.projects.values())
        
        # 應用篩選條件
        if query.status:
            projects = [p for p in projects if p.status == query.status]
        
        if query.owner:
            projects = [p for p in projects if p.owner == query.owner]
            
        if query.priority:
            projects = [p for p in projects if p.priority == query.priority]
            
        if query.tags:
            projects = [p for p in projects if any(tag in p.tags for tag in query.tags)]
            
        if query.created_after:
            projects = [p for p in projects if p.created_at >= query.created_after]
            
        if query.created_before:
            projects = [p for p in projects if p.created_at <= query.created_before]
        
        # 排序（按更新時間降序）
        projects.sort(key=lambda x: x.updated_at, reverse=True)
        
        # 分頁
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        
        return projects[start:end]
    
    # 任務管理
    async def create_task(self, request: CreateTaskRequest) -> Task:
        """創建任務"""
        # 驗證項目存在
        if request.project_id not in self.projects:
            raise ValueError(f"Project {request.project_id} not found")
        
        # 驗證依賴任務存在
        for dep_id in request.dependencies:
            if dep_id not in self.tasks:
                raise ValueError(f"Dependency task {dep_id} not found")
        
        task = Task(
            id=str(uuid.uuid4()),
            project_id=request.project_id,
            name=request.name,
            description=request.description,
            assignee=request.assignee,
            priority=request.priority,
            dependencies=request.dependencies,
            estimated_hours=request.estimated_hours,
            tags=request.tags,
            metadata=request.metadata
        )
        
        self.tasks[task.id] = task
        self.project_tasks[request.project_id].append(task.id)
        
        # 觸發核心引擎事件
        await self.core_engine.emit_event("task_created", {
            "task_id": task.id,
            "project_id": task.project_id
        })
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """獲取任務"""
        return self.tasks.get(task_id)
    
    async def update_task(self, task_id: str, request: UpdateTaskRequest) -> Optional[Task]:
        """更新任務"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # 更新字段
        update_data = request.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        
        # 如果狀態變更為進行中，設置開始時間
        if task.status == BusinessStatus.ACTIVE and not task.started_at:
            task.started_at = datetime.now()
        
        # 如果狀態變更為完成，設置完成時間
        if task.status == BusinessStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.now()
            task.progress = 100
        
        # 觸發核心引擎事件
        await self.core_engine.emit_event("task_updated", {
            "task_id": task_id,
            "status": task.status
        })
        
        return task
    
    async def delete_task(self, task_id: str) -> bool:
        """刪除任務"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # 從項目任務列表中移除
        if task.project_id in self.project_tasks:
            self.project_tasks[task.project_id].remove(task_id)
        
        del self.tasks[task_id]
        
        # 觸發核心引擎事件
        await self.core_engine.emit_event("task_deleted", {
            "task_id": task_id,
            "project_id": task.project_id
        })
        
        return True
    
    async def list_tasks(self, query: TaskQuery) -> List[Task]:
        """查詢任務列表"""
        tasks = list(self.tasks.values())
        
        # 應用篩選條件
        if query.project_id:
            tasks = [t for t in tasks if t.project_id == query.project_id]
        
        if query.status:
            tasks = [t for t in tasks if t.status == query.status]
            
        if query.assignee:
            tasks = [t for t in tasks if t.assignee == query.assignee]
            
        if query.priority:
            tasks = [t for t in tasks if t.priority == query.priority]
            
        if query.tags:
            tasks = [t for t in tasks if any(tag in t.tags for tag in query.tags)]
            
        if query.created_after:
            tasks = [t for t in tasks if t.created_at >= query.created_after]
            
        if query.created_before:
            tasks = [t for t in tasks if t.created_at <= query.created_before]
        
        # 排序（按優先級和創建時間）
        priority_order = {Priority.CRITICAL: 0, Priority.HIGH: 1, 
                         Priority.MEDIUM: 2, Priority.LOW: 3}
        tasks.sort(key=lambda x: (priority_order[x.priority], x.created_at), reverse=True)
        
        # 分頁
        start = (query.page - 1) * query.page_size
        end = start + query.page_size
        
        return tasks[start:end]
    
    async def get_project_tasks(self, project_id: str) -> List[Task]:
        """獲取項目所有任務"""
        if project_id not in self.project_tasks:
            return []
        
        task_ids = self.project_tasks[project_id]
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]
    
    # 工作流管理
    async def execute_workflow(self, workflow_id: str, name: str, 
                             triggered_by: str, parameters: Dict[str, Any] = None) -> WorkflowExecution:
        """執行工作流"""
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            name=name,
            triggered_by=triggered_by,
            metadata=parameters or {}
        )
        
        self.workflows[execution.id] = execution
        
        # 觸發核心引擎工作流
        try:
            await self.core_engine.execute_workflow(workflow_id, parameters or {})
            execution.status = BusinessStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.progress = 100
        except Exception as e:
            execution.status = BusinessStatus.FAILED
            execution.error_message = str(e)
        
        return execution
    
    async def get_workflow_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """獲取工作流執行"""
        return self.workflows.get(execution_id)
    
    # 業務指標
    async def get_business_metrics(self) -> BusinessMetrics:
        """獲取業務指標"""
        projects = list(self.projects.values())
        tasks = list(self.tasks.values())
        
        # 計算項目指標
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.status == BusinessStatus.ACTIVE])
        completed_projects = len([p for p in projects if p.status == BusinessStatus.COMPLETED])
        
        # 計算任務指標
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == BusinessStatus.COMPLETED])
        
        # 計算平均完成時間
        completed_tasks_with_time = [t for t in tasks 
                                   if t.status == BusinessStatus.COMPLETED 
                                   and t.started_at and t.completed_at]
        
        avg_completion_time = None
        if completed_tasks_with_time:
            total_time = sum([(t.completed_at - t.started_at).total_seconds() / 3600 
                            for t in completed_tasks_with_time])
            avg_completion_time = total_time / len(completed_tasks_with_time)
        
        # 計算資源利用率（簡化計算）
        active_tasks = [t for t in tasks if t.status == BusinessStatus.ACTIVE]
        resource_utilization = min(len(active_tasks) / 10.0, 1.0)  # 假設最大容量10個任務
        
        # 計算質量分數（基於完成率）
        quality_score = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return BusinessMetrics(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            average_completion_time=avg_completion_time,
            resource_utilization=resource_utilization,
            quality_score=quality_score
        )
    
    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """獲取儀表板數據"""
        # 獲取用戶相關項目
        user_projects = [p for p in self.projects.values() if p.owner == user_id]
        user_tasks = [t for t in self.tasks.values() 
                     if t.assignee == user_id or t.project_id in [p.id for p in user_projects]]
        
        # 統計數據
        metrics = await self.get_business_metrics()
        
        return {
            "user_projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status,
                    "progress": self._calculate_project_progress(p.id),
                    "deadline": p.deadline.isoformat() if p.deadline else None
                } for p in user_projects
            ],
            "user_tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "status": t.status,
                    "priority": t.priority,
                    "progress": t.progress,
                    "project_name": self.projects[t.project_id].name if t.project_id in self.projects else "Unknown"
                } for t in user_tasks[:10]  # 最近10個任務
            ],
            "metrics": metrics.dict(),
            "recent_activities": await self._get_recent_activities(user_id)
        }
    
    async def _calculate_project_progress(self, project_id: str) -> float:
        """計算項目進度"""
        tasks = await self.get_project_tasks(project_id)
        if not tasks:
            return 0.0
        
        total_progress = sum(t.progress for t in tasks)
        return total_progress / len(tasks)
    
    async def _get_recent_activities(self, user_id: str) -> List[Dict[str, Any]]:
        """獲取最近活動"""
        # 簡化實現，實際應從事件日誌中獲取
        return [
            {"type": "project_created", "message": "新項目已創建", "timestamp": datetime.now().isoformat()},
            {"type": "task_completed", "message": "任務已完成", "timestamp": datetime.now().isoformat()}
        ]


# 全局業務服務管理器實例
_business_service_manager = None


def get_business_service_manager() -> BusinessServiceManager:
    """獲取業務服務管理器單例"""
    global _business_service_manager
    if _business_service_manager is None:
        _business_service_manager = BusinessServiceManager()
    return _business_service_manager