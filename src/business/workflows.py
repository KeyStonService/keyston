"""
MachineNativeOps Business Workflows
業務工作流引擎 - 基於新架構的業務流程管理
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from enum import Enum

try:
    from ..new.automation.workflow_engine import WorkflowEngine, WorkflowTask
    from ..new.core import get_core_engine
    from ..new.security.auth import get_current_user
except ImportError:
    # 為測試目的提供模擬實現
    class WorkflowTask:
        def __init__(self, id, name, config):
            self.id = id
            self.name = name
            self.config = config
    
    class WorkflowEngine:
        async def initialize(self):
            pass
        async def create_workflow(self, name, description, tasks):
            class MockWorkflow:
                id = "test-workflow-id"
            return MockWorkflow()
    
    def get_core_engine():
        class MockEngine:
            async def emit_event(self, event, data):
                pass
        return MockEngine()
    
    def get_current_user():
        return "admin"
from .models import BusinessStatus, Task, Project
from .services import get_business_service_manager


class WorkflowType(str, Enum):
    """工作流類型"""
    PROJECT_LIFECYCLE = "project_lifecycle"
    TASK_APPROVAL = "task_approval"
    RESOURCE_ALLOCATION = "resource_allocation"
    QUALITY_CHECK = "quality_check"
    PERFORMANCE_MONITORING = "performance_monitoring"


class BusinessWorkflowEngine:
    """業務工作流引擎"""
    
    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        self.business_service = get_business_service_manager()
        self.custom_workflows: Dict[str, List[WorkflowTask]] = {}
        
    async def initialize(self):
        """初始化工作流引擎"""
        await self.workflow_engine.initialize()
        await self._register_default_workflows()
        
    async def _register_default_workflows(self):
        """註冊默認工作流"""
        
        # 項目生命周期工作流
        project_workflow = [
            WorkflowTask(
                id="validate_project",
                name="驗證項目",
                config={"type": "validation", "target": "project"}
            ),
            WorkflowTask(
                id="allocate_resources",
                name="分配資源",
                config={"type": "resource_allocation"}
            ),
            WorkflowTask(
                id="setup_monitoring",
                name="設置監控",
                config={"type": "monitoring_setup"}
            ),
            WorkflowTask(
                id="notify_stakeholders",
                name="通知相關方",
                config={"type": "notification", "recipients": ["owner", "team"]}
            )
        ]
        
        # 任務審批工作流
        task_approval_workflow = [
            WorkflowTask(
                id="validate_dependencies",
                name="驗證依賴",
                config={"type": "dependency_check"}
            ),
            WorkflowTask(
                id="check_resources",
                name="檢查資源",
                config={"type": "resource_check"}
            ),
            WorkflowTask(
                id="security_review",
                name="安全審核",
                config={"type": "security_check"}
            ),
            WorkflowTask(
                id="approve_task",
                name="審批任務",
                config={"type": "approval", "requires_approval": True}
            )
        ]
        
        # 資源分配工作流
        resource_workflow = [
            WorkflowTask(
                id="assess_requirements",
                name="評估需求",
                config={"type": "requirements_assessment"}
            ),
            WorkflowTask(
                id="check_availability",
                name="檢查可用性",
                config={"type": "availability_check"}
            ),
            WorkflowTask(
                id="allocate",
                name="分配資源",
                config={"type": "allocation"}
            ),
            WorkflowTask(
                id="update_inventory",
                name="更新庫存",
                config={"type": "inventory_update"}
            )
        ]
        
        # 質量檢查工作流
        quality_workflow = [
            WorkflowTask(
                id="code_analysis",
                name="代碼分析",
                config={"type": "static_analysis"}
            ),
            WorkflowTask(
                id="security_scan",
                name="安全掃描",
                config={"type": "security_scan"}
            ),
            WorkflowTask(
                id="performance_test",
                name="性能測試",
                config={"type": "performance_test"}
            ),
            WorkflowTask(
                id="generate_report",
                name="生成報告",
                config={"type": "report_generation"}
            )
        ]
        
        # 註冊工作流
        await self.workflow_engine.create_workflow(
            WorkflowType.PROJECT_LIFECYCLE.value,
            "項目生命周期管理",
            project_workflow
        )
        
        await self.workflow_engine.create_workflow(
            WorkflowType.TASK_APPROVAL.value,
            "任務審批流程",
            task_approval_workflow
        )
        
        await self.workflow_engine.create_workflow(
            WorkflowType.RESOURCE_ALLOCATION.value,
            "資源分配流程",
            resource_workflow
        )
        
        await self.workflow_engine.create_workflow(
            WorkflowType.QUALITY_CHECK.value,
            "質量檢查流程",
            quality_workflow
        )
    
    async def execute_project_workflow(self, project_id: str) -> Dict[str, Any]:
        """執行項目工作流"""
        project = await self.business_service.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # 準備工作流參數
        parameters = {
            "project_id": project_id,
            "project_name": project.name,
            "owner": project.owner,
            "priority": project.priority,
            "deadline": project.deadline.isoformat() if project.deadline else None
        }
        
        # 執行工作流
        execution = await self.business_service.execute_workflow(
            WorkflowType.PROJECT_LIFECYCLE.value,
            f"Project Setup: {project.name}",
            await get_current_user(),
            parameters
        )
        
        # 更新項目狀態
        if execution.status == BusinessStatus.COMPLETED:
            await self.business_service.update_project(project_id, {
                "status": BusinessStatus.ACTIVE
            })
        
        return {
            "execution_id": execution.id,
            "status": execution.status,
            "project_id": project_id,
            "completed_at": execution.completed_at
        }
    
    async def execute_task_approval_workflow(self, task_id: str) -> Dict[str, Any]:
        """執行任務審批工作流"""
        task = await self.business_service.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # 準備工作流參數
        parameters = {
            "task_id": task_id,
            "task_name": task.name,
            "project_id": task.project_id,
            "assignee": task.assignee,
            "priority": task.priority,
            "dependencies": task.dependencies,
            "estimated_hours": task.estimated_hours
        }
        
        # 執行工作流
        execution = await self.business_service.execute_workflow(
            WorkflowType.TASK_APPROVAL.value,
            f"Task Approval: {task.name}",
            await get_current_user(),
            parameters
        )
        
        # 更新任務狀態
        if execution.status == BusinessStatus.COMPLETED:
            await self.business_service.update_task(task_id, {
                "status": BusinessStatus.ACTIVE
            })
        elif execution.status == BusinessStatus.FAILED:
            await self.business_service.update_task(task_id, {
                "status": BusinessStatus.CANCELLED
            })
        
        return {
            "execution_id": execution.id,
            "status": execution.status,
            "task_id": task_id,
            "completed_at": execution.completed_at,
            "error_message": execution.error_message
        }
    
    async def execute_resource_allocation_workflow(self, project_id: str, 
                                                 resource_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """執行資源分配工作流"""
        project = await self.business_service.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # 準備工作流參數
        parameters = {
            "project_id": project_id,
            "project_name": project.name,
            "resource_requirements": resource_requirements,
            "priority": project.priority
        }
        
        # 執行工作流
        execution = await self.business_service.execute_workflow(
            WorkflowType.RESOURCE_ALLOCATION.value,
            f"Resource Allocation: {project.name}",
            await get_current_user(),
            parameters
        )
        
        return {
            "execution_id": execution.id,
            "status": execution.status,
            "project_id": project_id,
            "allocated_resources": execution.results.get("allocated_resources", {}),
            "completed_at": execution.completed_at
        }
    
    async def execute_quality_check_workflow(self, task_id: str) -> Dict[str, Any]:
        """執行質量檢查工作流"""
        task = await self.business_service.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # 準備工作流參數
        parameters = {
            "task_id": task_id,
            "task_name": task.name,
            "project_id": task.project_id,
            "task_type": task.metadata.get("type", "general")
        }
        
        # 執行工作流
        execution = await self.business_service.execute_workflow(
            WorkflowType.QUALITY_CHECK.value,
            f"Quality Check: {task.name}",
            await get_current_user(),
            parameters
        )
        
        # 更新任務質量標記
        if execution.status == BusinessStatus.COMPLETED:
            quality_score = execution.results.get("quality_score", 0)
            await self.business_service.update_task(task_id, {
                "metadata": {
                    **task.metadata,
                    "quality_score": quality_score,
                    "quality_checked_at": datetime.now().isoformat()
                }
            })
        
        return {
            "execution_id": execution.id,
            "status": execution.status,
            "task_id": task_id,
            "quality_score": execution.results.get("quality_score", 0),
            "quality_report": execution.results.get("quality_report", {}),
            "completed_at": execution.completed_at
        }
    
    async def create_custom_workflow(self, name: str, description: str, 
                                   tasks: List[Dict[str, Any]]) -> str:
        """創建自定義工作流"""
        workflow_tasks = []
        
        for task_config in tasks:
            workflow_task = WorkflowTask(
                id=task_config["id"],
                name=task_config["name"],
                config=task_config.get("config", {})
            )
            workflow_tasks.append(workflow_task)
        
        workflow_id = f"custom_{name.lower().replace(' ', '_')}"
        
        await self.workflow_engine.create_workflow(
            workflow_id,
            description,
            workflow_tasks
        )
        
        self.custom_workflows[workflow_id] = workflow_tasks
        
        return workflow_id
    
    async def execute_custom_workflow(self, workflow_id: str, 
                                    execution_name: str, 
                                    parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """執行自定義工作流"""
        if workflow_id not in self.custom_workflows:
            raise ValueError(f"Custom workflow {workflow_id} not found")
        
        execution = await self.business_service.execute_workflow(
            workflow_id,
            execution_name,
            await get_current_user(),
            parameters or {}
        )
        
        return {
            "execution_id": execution.id,
            "status": execution.status,
            "workflow_id": workflow_id,
            "results": execution.results,
            "completed_at": execution.completed_at,
            "error_message": execution.error_message
        }
    
    async def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """獲取工作流執行狀態"""
        execution = await self.business_service.get_workflow_execution(execution_id)
        if not execution:
            return None
        
        return {
            "execution_id": execution.id,
            "workflow_id": execution.workflow_id,
            "name": execution.name,
            "status": execution.status,
            "progress": execution.progress,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "results": execution.results,
            "error_message": execution.error_message
        }
    
    async def list_workflow_executions(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出工作流執行"""
        executions = []
        
        for execution in self.business_service.workflows.values():
            if workflow_id is None or execution.workflow_id == workflow_id:
                executions.append({
                    "execution_id": execution.id,
                    "workflow_id": execution.workflow_id,
                    "name": execution.name,
                    "status": execution.status,
                    "progress": execution.progress,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
                })
        
        # 按開始時間降序排序
        executions.sort(key=lambda x: x["started_at"], reverse=True)
        
        return executions
    
    async def cancel_workflow_execution(self, execution_id: str) -> bool:
        """取消工作流執行"""
        execution = await self.business_service.get_workflow_execution(execution_id)
        if not execution:
            return False
        
        if execution.status in [BusinessStatus.COMPLETED, BusinessStatus.FAILED, BusinessStatus.CANCELLED]:
            return False
        
        # 更新狀態為已取消
        execution.status = BusinessStatus.CANCELLED
        execution.completed_at = datetime.now()
        
        return True
    
    async def retry_workflow_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """重試工作流執行"""
        execution = await self.business_service.get_workflow_execution(execution_id)
        if not execution:
            return None
        
        if execution.status != BusinessStatus.FAILED:
            raise ValueError("Can only retry failed executions")
        
        # 重新執行工作流
        new_execution = await self.business_service.execute_workflow(
            execution.workflow_id,
            f"Retry: {execution.name}",
            execution.triggered_by,
            execution.metadata
        )
        
        return {
            "execution_id": new_execution.id,
            "status": new_execution.status,
            "retry_of": execution_id,
            "completed_at": new_execution.completed_at
        }


# 全局業務工作流引擎實例
_business_workflow_engine = None


def get_business_workflow_engine() -> BusinessWorkflowEngine:
    """獲取業務工作流引擎單例"""
    global _business_workflow_engine
    if _business_workflow_engine is None:
        _business_workflow_engine = BusinessWorkflowEngine()
    return _business_workflow_engine