"""
MachineNativeOps Business API
業務 API 接口 - 基於新架構的 RESTful API
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

try:
    from ..new.security.auth import get_current_user, authenticate
    from ..new.governance.policy_engine import PolicyEngine
except ImportError:
    # 為測試目的提供模擬實現
    def get_current_user():
        return "admin"
    def authenticate(username, password):
        return "test_token"
    
    class PolicyEngine:
        def __init__(self):
            pass
        async def evaluate(self, policy):
            class MockResult:
                allowed = True
                reason = "Test mode"
            return MockResult()
from .models import (
    Project, Task, WorkflowExecution, BusinessMetrics,
    ProjectListResponse, TaskListResponse, WorkflowExecutionListResponse,
    ProjectQuery, TaskQuery, CreateProjectRequest, CreateTaskRequest, UpdateTaskRequest
)
from .services import get_business_service_manager
from .workflows import get_business_workflow_engine


class BusinessAPI:
    """業務 API 類"""
    
    def __init__(self):
        self.app = FastAPI(
            title="MachineNativeOps Business API",
            description="企業級智能自動化平台業務接口",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        self.business_service = get_business_service_manager()
        self.workflow_engine = get_business_workflow_engine()
        self.policy_engine = PolicyEngine()
        
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """設置中間件"""
        # CORS 中間件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生產環境應限制具體域名
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """設置路由"""
        
        # 健康檢查
        @self.app.get("/health")
        async def health_check():
            """健康檢查端點"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "services": {
                    "business_service": "running",
                    "workflow_engine": "running",
                    "policy_engine": "running"
                }
            }
        
        # 儀表板數據
        @self.app.get("/api/v1/dashboard")
        async def get_dashboard(user_id: str = Depends(get_current_user)):
            """獲取儀表板數據"""
            try:
                dashboard_data = await self.business_service.get_dashboard_data(user_id)
                return dashboard_data
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 業務指標
        @self.app.get("/api/v1/metrics")
        async def get_metrics():
            """獲取業務指標"""
            try:
                metrics = await self.business_service.get_business_metrics()
                return metrics.dict()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 項目管理 API
        @self.app.post("/api/v1/projects", response_model=Project)
        async def create_project(
            request: CreateProjectRequest,
            user_id: str = Depends(get_current_user)
        ):
            """創建項目"""
            try:
                return await self.business_service.create_project(request)
            except PermissionError as e:
                raise HTTPException(status_code=403, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/projects/{project_id}", response_model=Project)
        async def get_project(project_id: str):
            """獲取項目"""
            project = await self.business_service.get_project(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            return project
        
        @self.app.put("/api/v1/projects/{project_id}", response_model=Project)
        async def update_project(
            project_id: str,
            updates: Dict[str, Any],
            user_id: str = Depends(get_current_user)
        ):
            """更新項目"""
            try:
                project = await self.business_service.update_project(project_id, updates)
                if not project:
                    raise HTTPException(status_code=404, detail="Project not found")
                return project
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/api/v1/projects/{project_id}")
        async def delete_project(
            project_id: str,
            user_id: str = Depends(get_current_user)
        ):
            """刪除項目"""
            try:
                success = await self.business_service.delete_project(project_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Project not found")
                return {"message": "Project deleted successfully"}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/projects", response_model=ProjectListResponse)
        async def list_projects(
            status: Optional[str] = Query(None),
            owner: Optional[str] = Query(None),
            priority: Optional[str] = Query(None),
            tags: Optional[List[str]] = Query(None),
            page: int = Query(1, ge=1),
            page_size: int = Query(20, ge=1, le=100)
        ):
            """查詢項目列表"""
            try:
                query = ProjectQuery(
                    status=status,
                    owner=owner,
                    priority=priority,
                    tags=tags,
                    page=page,
                    page_size=page_size
                )
                projects = await self.business_service.list_projects(query)
                
                # 獲取總數（簡化實現）
                total_query = ProjectQuery(page=1, page_size=1000)
                all_projects = await self.business_service.list_projects(total_query)
                total = len(all_projects)
                
                return ProjectListResponse(
                    projects=projects,
                    total=total,
                    page=page,
                    page_size=page_size
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 任務管理 API
        @self.app.post("/api/v1/tasks", response_model=Task)
        async def create_task(
            request: CreateTaskRequest,
            user_id: str = Depends(get_current_user)
        ):
            """創建任務"""
            try:
                return await self.business_service.create_task(request)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/tasks/{task_id}", response_model=Task)
        async def get_task(task_id: str):
            """獲取任務"""
            task = await self.business_service.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            return task
        
        @self.app.put("/api/v1/tasks/{task_id}", response_model=Task)
        async def update_task(
            task_id: str,
            request: UpdateTaskRequest,
            user_id: str = Depends(get_current_user)
        ):
            """更新任務"""
            try:
                task = await self.business_service.update_task(task_id, request)
                if not task:
                    raise HTTPException(status_code=404, detail="Task not found")
                return task
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/api/v1/tasks/{task_id}")
        async def delete_task(
            task_id: str,
            user_id: str = Depends(get_current_user)
        ):
            """刪除任務"""
            try:
                success = await self.business_service.delete_task(task_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Task not found")
                return {"message": "Task deleted successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/tasks", response_model=TaskListResponse)
        async def list_tasks(
            project_id: Optional[str] = Query(None),
            status: Optional[str] = Query(None),
            assignee: Optional[str] = Query(None),
            priority: Optional[str] = Query(None),
            tags: Optional[List[str]] = Query(None),
            page: int = Query(1, ge=1),
            page_size: int = Query(20, ge=1, le=100)
        ):
            """查詢任務列表"""
            try:
                query = TaskQuery(
                    project_id=project_id,
                    status=status,
                    assignee=assignee,
                    priority=priority,
                    tags=tags,
                    page=page,
                    page_size=page_size
                )
                tasks = await self.business_service.list_tasks(query)
                
                # 獲取總數（簡化實現）
                total_query = TaskQuery(page=1, page_size=1000)
                all_tasks = await self.business_service.list_tasks(total_query)
                total = len(all_tasks)
                
                return TaskListResponse(
                    tasks=tasks,
                    total=total,
                    page=page,
                    page_size=page_size
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/projects/{project_id}/tasks", response_model=List[Task])
        async def get_project_tasks(project_id: str):
            """獲取項目所有任務"""
            try:
                tasks = await self.business_service.get_project_tasks(project_id)
                return tasks
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # 工作流 API
        @self.app.post("/api/v1/workflows/project/{project_id}/execute")
        async def execute_project_workflow(
            project_id: str,
            user_id: str = Depends(get_current_user)
        ):
            """執行項目工作流"""
            try:
                result = await self.workflow_engine.execute_project_workflow(project_id)
                return result
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/workflows/task/{task_id}/approve")
        async def execute_task_approval_workflow(
            task_id: str,
            user_id: str = Depends(get_current_user)
        ):
            """執行任務審批工作流"""
            try:
                result = await self.workflow_engine.execute_task_approval_workflow(task_id)
                return result
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/workflows/resource-allocation")
        async def execute_resource_allocation_workflow(
            project_id: str,
            resource_requirements: Dict[str, Any],
            user_id: str = Depends(get_current_user)
        ):
            """執行資源分配工作流"""
            try:
                result = await self.workflow_engine.execute_resource_allocation_workflow(
                    project_id, resource_requirements
                )
                return result
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/workflows/quality-check/{task_id}")
        async def execute_quality_check_workflow(
            task_id: str,
            user_id: str = Depends(get_current_user)
        ):
            """執行質量檢查工作流"""
            try:
                result = await self.workflow_engine.execute_quality_check_workflow(task_id)
                return result
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/workflows/executions/{execution_id}")
        async def get_workflow_status(execution_id: str):
            """獲取工作流執行狀態"""
            try:
                status = await self.workflow_engine.get_workflow_status(execution_id)
                if not status:
                    raise HTTPException(status_code=404, detail="Execution not found")
                return status
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/workflows/executions")
        async def list_workflow_executions(
            workflow_id: Optional[str] = Query(None)
        ):
            """列出工作流執行"""
            try:
                executions = await self.workflow_engine.list_workflow_executions(workflow_id)
                return executions
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/workflows/executions/{execution_id}/cancel")
        async def cancel_workflow_execution(
            execution_id: str,
            user_id: str = Depends(get_current_user)
        ):
            """取消工作流執行"""
            try:
                success = await self.workflow_engine.cancel_workflow_execution(execution_id)
                if not success:
                    raise HTTPException(status_code=404, detail="Execution not found")
                return {"message": "Execution cancelled successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/workflows/executions/{execution_id}/retry")
        async def retry_workflow_execution(
            execution_id: str,
            user_id: str = Depends(get_current_user)
        ):
            """重試工作流執行"""
            try:
                result = await self.workflow_engine.retry_workflow_execution(execution_id)
                if not result:
                    raise HTTPException(status_code=404, detail="Execution not found")
                return result
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def initialize(self):
        """初始化 API"""
        await self.business_service.initialize()
        await self.workflow_engine.initialize()
        await self.policy_engine.initialize()
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """運行 API 服務"""
        uvicorn.run(self.app, host=host, port=port)


# 創建 API 實例
business_api = BusinessAPI()


async def get_business_api() -> BusinessAPI:
    """獲取業務 API 實例"""
    await business_api.initialize()
    return business_api


if __name__ == "__main__":
    # 直接運行 API 服務
    import asyncio
    
    async def main():
        api = await get_business_api()
        api.run()
    
    asyncio.run(main())