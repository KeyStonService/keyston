"""
MachineNativeOps Business Models
業務數據模型和驗證
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class BusinessStatus(str, Enum):
    """業務狀態枚舉"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    """優先級枚舉"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Project(BaseModel):
    """項目模型"""
    id: str = Field(..., description="項目唯一標識")
    name: str = Field(..., description="項目名稱")
    description: Optional[str] = Field(None, description="項目描述")
    owner: str = Field(..., description="項目負責人")
    status: BusinessStatus = Field(BusinessStatus.PENDING, description="項目狀態")
    priority: Priority = Field(Priority.MEDIUM, description="優先級")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")
    deadline: Optional[datetime] = Field(None, description="截止時間")
    tags: List[str] = Field(default_factory=list, description="標籤")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Task(BaseModel):
    """任務模型"""
    id: str = Field(..., description="任務唯一標識")
    project_id: str = Field(..., description="所屬項目ID")
    name: str = Field(..., description="任務名稱")
    description: Optional[str] = Field(None, description="任務描述")
    assignee: Optional[str] = Field(None, description="執行人")
    status: BusinessStatus = Field(BusinessStatus.PENDING, description="任務狀態")
    priority: Priority = Field(Priority.MEDIUM, description="優先級")
    progress: int = Field(0, ge=0, le=100, description="進度百分比")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")
    started_at: Optional[datetime] = Field(None, description="開始時間")
    completed_at: Optional[datetime] = Field(None, description="完成時間")
    dependencies: List[str] = Field(default_factory=list, description="依賴任務ID")
    estimated_hours: Optional[float] = Field(None, description="預估工時")
    actual_hours: Optional[float] = Field(None, description="實際工時")
    tags: List[str] = Field(default_factory=list, description="標籤")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Resource(BaseModel):
    """資源模型"""
    id: str = Field(..., description="資源唯一標識")
    name: str = Field(..., description="資源名稱")
    type: str = Field(..., description="資源類型")
    capacity: Optional[float] = Field(None, description="容量")
    availability: float = Field(1.0, ge=0, le=1, description="可用性")
    cost_per_hour: Optional[float] = Field(None, description="每小時成本")
    location: Optional[str] = Field(None, description="位置")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkflowExecution(BaseModel):
    """工作流執行模型"""
    id: str = Field(..., description="執行唯一標識")
    workflow_id: str = Field(..., description="工作流ID")
    name: str = Field(..., description="執行名稱")
    status: BusinessStatus = Field(BusinessStatus.PENDING, description="執行狀態")
    triggered_by: str = Field(..., description="觸發者")
    started_at: datetime = Field(default_factory=datetime.now, description="開始時間")
    completed_at: Optional[datetime] = Field(None, description="完成時間")
    progress: int = Field(0, ge=0, le=100, description="進度百分比")
    results: Dict[str, Any] = Field(default_factory=dict, description="執行結果")
    error_message: Optional[str] = Field(None, description="錯誤信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BusinessMetrics(BaseModel):
    """業務指標模型"""
    total_projects: int = Field(0, description="項目總數")
    active_projects: int = Field(0, description="活躍項目數")
    completed_projects: int = Field(0, description="已完成項目數")
    total_tasks: int = Field(0, description="任務總數")
    completed_tasks: int = Field(0, description="已完成任務數")
    average_completion_time: Optional[float] = Field(None, description="平均完成時間（小時）")
    resource_utilization: float = Field(0.0, ge=0, le=1, description="資源利用率")
    cost_efficiency: Optional[float] = Field(None, description="成本效率")
    quality_score: float = Field(0.0, ge=0, le=100, description="質量分數")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 響應模型
class ProjectListResponse(BaseModel):
    """項目列表響應"""
    projects: List[Project]
    total: int
    page: int
    page_size: int


class TaskListResponse(BaseModel):
    """任務列表響應"""
    tasks: List[Task]
    total: int
    page: int
    page_size: int


class WorkflowExecutionListResponse(BaseModel):
    """工作流執行列表響應"""
    executions: List[WorkflowExecution]
    total: int
    page: int
    page_size: int


# 請求模型
class CreateProjectRequest(BaseModel):
    """創建項目請求"""
    name: str = Field(..., min_length=1, max_length=100, description="項目名稱")
    description: Optional[str] = Field(None, max_length=500, description="項目描述")
    owner: str = Field(..., description="項目負責人")
    priority: Priority = Field(Priority.MEDIUM, description="優先級")
    deadline: Optional[datetime] = Field(None, description="截止時間")
    tags: List[str] = Field(default_factory=list, description="標籤")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")


class CreateTaskRequest(BaseModel):
    """創建任務請求"""
    project_id: str = Field(..., description="所屬項目ID")
    name: str = Field(..., min_length=1, max_length=100, description="任務名稱")
    description: Optional[str] = Field(None, max_length=500, description="任務描述")
    assignee: Optional[str] = Field(None, description="執行人")
    priority: Priority = Field(Priority.MEDIUM, description="優先級")
    dependencies: List[str] = Field(default_factory=list, description="依賴任務ID")
    estimated_hours: Optional[float] = Field(None, gt=0, description="預估工時")
    tags: List[str] = Field(default_factory=list, description="標籤")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")


class UpdateTaskRequest(BaseModel):
    """更新任務請求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="任務名稱")
    description: Optional[str] = Field(None, max_length=500, description="任務描述")
    assignee: Optional[str] = Field(None, description="執行人")
    status: Optional[BusinessStatus] = Field(None, description="任務狀態")
    priority: Optional[Priority] = Field(None, description="優先級")
    progress: Optional[int] = Field(None, ge=0, le=100, description="進度百分比")
    actual_hours: Optional[float] = Field(None, gt=0, description="實際工時")
    tags: Optional[List[str]] = Field(None, description="標籤")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元數據")


# 查詢模型
class ProjectQuery(BaseModel):
    """項目查詢"""
    status: Optional[BusinessStatus] = Field(None, description="狀態篩選")
    owner: Optional[str] = Field(None, description="負責人篩選")
    priority: Optional[Priority] = Field(None, description="優先級篩選")
    tags: Optional[List[str]] = Field(None, description="標籤篩選")
    created_after: Optional[datetime] = Field(None, description="創建時間篩選（之）")
    created_before: Optional[datetime] = Field(None, description="創建時間篩選（前）")
    page: int = Field(1, ge=1, description="頁碼")
    page_size: int = Field(20, ge=1, le=100, description="每頁大小")


class TaskQuery(BaseModel):
    """任務查詢"""
    project_id: Optional[str] = Field(None, description="項目ID篩選")
    status: Optional[BusinessStatus] = Field(None, description="狀態篩選")
    assignee: Optional[str] = Field(None, description="執行人篩選")
    priority: Optional[Priority] = Field(None, description="優先級篩選")
    tags: Optional[List[str]] = Field(None, description="標籤篩選")
    created_after: Optional[datetime] = Field(None, description="創建時間篩選（之）")
    created_before: Optional[datetime] = Field(None, description="創建時間篩選（前）")
    page: int = Field(1, ge=1, description="頁碼")
    page_size: int = Field(20, ge=1, le=100, description="每頁大小")