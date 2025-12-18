#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
代碼分析 API 服務
============================================================================
提供 RESTful API 接口用於代碼分析服務
============================================================================
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .code_analyzer import (
    CodeAnalysisEngine,
    AnalysisStrategy,
    AnalysisResult,
    CodeIssue,
    SeverityLevel,
    IssueType
)

# ============================================================================
# API 數據模型
# ============================================================================

class AnalysisRequest(BaseModel):
    """分析請求"""
    repository: str = Field(..., description="代碼庫路徑或 URL")
    commit_hash: str = Field(..., description="提交哈希")
    branch: str = Field(default="main", description="分支名稱")
    strategy: str = Field(default="STANDARD", description="分析策略")
    
    class Config:
        schema_extra = {
            "example": {
                "repository": "https://github.com/example/repo",
                "commit_hash": "abc123",
                "branch": "main",
                "strategy": "STANDARD"
            }
        }


class AnalysisResponse(BaseModel):
    """分析回應"""
    analysis_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """健康檢查回應"""
    status: str
    timestamp: str
    version: str
    uptime: float


# ============================================================================
# FastAPI 應用
# ============================================================================

app = FastAPI(
    title="SLASolve Code Analysis API",
    description="Enterprise Code Intelligence Platform v2.0 - Code Analysis Service",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應該設置具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局分析引擎實例
analysis_engine: Optional[CodeAnalysisEngine] = None

# 分析任務存儲（生產環境應使用 Redis 或數據庫）
analysis_tasks: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# 啟動和關閉事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    global analysis_engine
    config = {
        'max_workers': 4,
        'cache_enabled': True,
    }
    analysis_engine = CodeAnalysisEngine(config)
    logging.info("Code Analysis Engine initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logging.info("Code Analysis API shutting down")


# ============================================================================
# API 端點
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """根端點"""
    return {
        "service": "SLASolve Code Analysis API",
        "version": "2.0.0",
        "docs": "/api/docs"
    }


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """健康檢查"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0",
        uptime=0.0  # 實際應計算真實運行時間
    )


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_code(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    提交代碼分析任務
    
    - **repository**: 代碼庫路徑或 URL
    - **commit_hash**: 提交哈希
    - **branch**: 分支名稱（默認 main）
    - **strategy**: 分析策略（QUICK/STANDARD/DEEP/COMPREHENSIVE）
    """
    if not analysis_engine:
        raise HTTPException(status_code=503, detail="Analysis engine not initialized")
    
    # 驗證策略
    try:
        strategy = AnalysisStrategy[request.strategy.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Must be one of: {[s.value for s in AnalysisStrategy]}"
        )
    
    # 生成分析 ID
    import uuid
    analysis_id = str(uuid.uuid4())
    
    # 記錄任務
    analysis_tasks[analysis_id] = {
        "status": "pending",
        "request": request.dict(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    # 在背景執行分析
    background_tasks.add_task(
        run_analysis,
        analysis_id,
        request.repository,
        request.commit_hash,
        strategy
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="pending",
        message="Analysis task submitted successfully"
    )


@app.get("/api/v1/analyze/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_result(analysis_id: str):
    """
    獲取分析結果
    
    - **analysis_id**: 分析任務 ID
    """
    if analysis_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    task = analysis_tasks[analysis_id]
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status=task["status"],
        message=task.get("message", ""),
        result=task.get("result")
    )


@app.get("/api/v1/analyze", response_model=List[Dict[str, Any]])
async def list_analyses(
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    列出分析任務
    
    - **limit**: 返回數量限制（最大 100）
    - **offset**: 偏移量
    """
    tasks = list(analysis_tasks.items())
    tasks.sort(key=lambda x: x[1].get("created_at", ""), reverse=True)
    
    paginated = tasks[offset:offset + limit]
    
    return [
        {
            "analysis_id": task_id,
            "status": task["status"],
            "created_at": task.get("created_at"),
            "repository": task["request"].get("repository")
        }
        for task_id, task in paginated
    ]


@app.delete("/api/v1/analyze/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    刪除分析結果
    
    - **analysis_id**: 分析任務 ID
    """
    if analysis_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_tasks[analysis_id]
    
    return {"message": "Analysis deleted successfully"}


@app.get("/api/v1/metrics")
async def get_metrics():
    """獲取引擎指標"""
    if not analysis_engine:
        raise HTTPException(status_code=503, detail="Analysis engine not initialized")
    
    metrics = analysis_engine.get_metrics()
    
    return {
        "engine_metrics": metrics,
        "task_stats": {
            "total": len(analysis_tasks),
            "pending": sum(1 for t in analysis_tasks.values() if t["status"] == "pending"),
            "running": sum(1 for t in analysis_tasks.values() if t["status"] == "running"),
            "completed": sum(1 for t in analysis_tasks.values() if t["status"] == "completed"),
            "failed": sum(1 for t in analysis_tasks.values() if t["status"] == "failed"),
        }
    }


# ============================================================================
# 背景任務
# ============================================================================

async def run_analysis(
    analysis_id: str,
    repository: str,
    commit_hash: str,
    strategy: AnalysisStrategy
):
    """執行分析任務"""
    try:
        # 更新狀態為運行中
        analysis_tasks[analysis_id]["status"] = "running"
        analysis_tasks[analysis_id]["started_at"] = datetime.utcnow().isoformat()
        
        # 執行分析
        result = await analysis_engine.analyze_repository(
            repo_path=repository,
            commit_hash=commit_hash,
            strategy=strategy
        )
        
        # 轉換結果為可序列化格式
        result_dict = {
            "id": result.id,
            "repository": result.repository,
            "commit_hash": result.commit_hash,
            "branch": result.branch,
            "analysis_timestamp": result.analysis_timestamp.isoformat(),
            "duration": result.duration,
            "strategy": result.strategy.value,
            "total_issues": result.total_issues,
            "critical_issues": result.critical_issues,
            "quality_score": result.quality_score,
            "risk_level": result.risk_level,
            "files_analyzed": result.files_analyzed,
            "languages_detected": list(result.languages_detected),
            "issues": [
                {
                    "id": issue.id,
                    "type": issue.type.value,
                    "severity": issue.severity.value,
                    "file": issue.file,
                    "line": issue.line,
                    "message": issue.message,
                    "description": issue.description,
                    "suggestion": issue.suggestion,
                    "tags": issue.tags,
                    "confidence": issue.confidence,
                }
                for issue in result.issues[:100]  # 限制返回數量
            ],
            "metrics": result.metrics.to_dict()
        }
        
        # 更新狀態為完成
        analysis_tasks[analysis_id]["status"] = "completed"
        analysis_tasks[analysis_id]["result"] = result_dict
        analysis_tasks[analysis_id]["completed_at"] = datetime.utcnow().isoformat()
        analysis_tasks[analysis_id]["message"] = "Analysis completed successfully"
        
    except Exception as e:
        # 更新狀態為失敗
        analysis_tasks[analysis_id]["status"] = "failed"
        analysis_tasks[analysis_id]["error"] = str(e)
        analysis_tasks[analysis_id]["completed_at"] = datetime.utcnow().isoformat()
        analysis_tasks[analysis_id]["message"] = f"Analysis failed: {str(e)}"
        logging.error(f"Analysis {analysis_id} failed: {e}", exc_info=True)


# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
