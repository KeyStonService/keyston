#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
數據庫模型 (Database Models)
============================================================================
用於持久化分析結果的數據庫模型
============================================================================
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import (
    Column, String, Integer, Float, JSON, DateTime,
    Text, Enum as SQLEnum, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class AnalysisStatus(str, enum.Enum):
    """分析狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityLevel(str, enum.Enum):
    """嚴重程度"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class IssueType(str, enum.Enum):
    """問題類型"""
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    CODE_QUALITY = "CODE_QUALITY"
    MAINTAINABILITY = "MAINTAINABILITY"
    DEPENDENCY = "DEPENDENCY"
    ACCESSIBILITY = "ACCESSIBILITY"
    COMPLIANCE = "COMPLIANCE"


class AnalysisRecord(Base):
    """分析記錄"""
    __tablename__ = "analysis_records"
    
    # 主鍵
    id = Column(String(36), primary_key=True)
    
    # 基本信息
    repository = Column(String(500), nullable=False, index=True)
    commit_hash = Column(String(40), nullable=False, index=True)
    branch = Column(String(100), default="main")
    
    # 狀態信息
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, index=True)
    strategy = Column(String(50), default="STANDARD")
    
    # 時間戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Float, default=0.0)
    
    # 結果統計
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    info_issues = Column(Integer, default=0)
    
    # 質量指標
    quality_score = Column(Float, default=100.0)
    risk_level = Column(String(20), default="LOW")
    
    # 分析統計
    files_analyzed = Column(Integer, default=0)
    lines_of_code = Column(Integer, default=0)
    
    # 其他數據
    languages_detected = Column(JSON, default=list)
    metrics = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    
    # 關聯
    issues = relationship("IssueRecord", back_populates="analysis", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_repo_commit', 'repository', 'commit_hash'),
        Index('idx_status_created', 'status', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "repository": self.repository,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "status": self.status.value if self.status else None,
            "strategy": self.strategy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.duration,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "quality_score": self.quality_score,
            "risk_level": self.risk_level,
            "files_analyzed": self.files_analyzed,
            "lines_of_code": self.lines_of_code,
            "languages_detected": self.languages_detected,
        }


class IssueRecord(Base):
    """問題記錄"""
    __tablename__ = "issue_records"
    
    # 主鍵
    id = Column(String(36), primary_key=True)
    
    # 外鍵
    analysis_id = Column(String(36), ForeignKey("analysis_records.id"), nullable=False, index=True)
    
    # 問題分類
    type = Column(SQLEnum(IssueType), nullable=False, index=True)
    severity = Column(SQLEnum(SeverityLevel), nullable=False, index=True)
    
    # 位置信息
    file = Column(String(500), nullable=False)
    line = Column(Integer, default=0)
    column = Column(Integer, default=0)
    
    # 描述信息
    message = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=True)
    
    # 元數據
    tags = Column(JSON, default=list)
    confidence = Column(Float, default=0.95)
    repair_difficulty = Column(String(20), default="MEDIUM")
    estimated_repair_time = Column(Integer, default=0)
    
    # 時間戳
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 關聯
    analysis = relationship("AnalysisRecord", back_populates="issues")
    
    # 索引
    __table_args__ = (
        Index('idx_analysis_severity', 'analysis_id', 'severity'),
        Index('idx_type_severity', 'type', 'severity'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "type": self.type.value if self.type else None,
            "severity": self.severity.value if self.severity else None,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "description": self.description,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "tags": self.tags,
            "confidence": self.confidence,
            "repair_difficulty": self.repair_difficulty,
            "estimated_repair_time": self.estimated_repair_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# ============================================================================
# 數據庫會話管理
# ============================================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

class DatabaseManager:
    """數據庫管理器"""
    
    def __init__(self, database_url: str = "sqlite:///./code_analysis.db"):
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """創建所有表"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """刪除所有表"""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """獲取數據庫會話"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# ============================================================================
# 數據訪問層 (DAO)
# ============================================================================

class AnalysisDAO:
    """分析數據訪問對象"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_analysis(self, analysis_data: Dict[str, Any]) -> AnalysisRecord:
        """創建分析記錄"""
        with self.db_manager.get_session() as session:
            analysis = AnalysisRecord(**analysis_data)
            session.add(analysis)
            session.flush()
            return analysis
    
    def get_analysis(self, analysis_id: str) -> Optional[AnalysisRecord]:
        """獲取分析記錄"""
        with self.db_manager.get_session() as session:
            return session.query(AnalysisRecord).filter_by(id=analysis_id).first()
    
    def update_analysis(self, analysis_id: str, updates: Dict[str, Any]):
        """更新分析記錄"""
        with self.db_manager.get_session() as session:
            session.query(AnalysisRecord).filter_by(id=analysis_id).update(updates)
    
    def delete_analysis(self, analysis_id: str):
        """刪除分析記錄"""
        with self.db_manager.get_session() as session:
            session.query(AnalysisRecord).filter_by(id=analysis_id).delete()
    
    def list_analyses(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[AnalysisStatus] = None
    ) -> List[AnalysisRecord]:
        """列出分析記錄"""
        with self.db_manager.get_session() as session:
            query = session.query(AnalysisRecord)
            
            if status:
                query = query.filter_by(status=status)
            
            query = query.order_by(AnalysisRecord.created_at.desc())
            query = query.limit(limit).offset(offset)
            
            return query.all()
    
    def add_issue(self, issue_data: Dict[str, Any]) -> IssueRecord:
        """添加問題記錄"""
        with self.db_manager.get_session() as session:
            issue = IssueRecord(**issue_data)
            session.add(issue)
            session.flush()
            return issue
    
    def get_issues_by_analysis(self, analysis_id: str) -> List[IssueRecord]:
        """獲取分析的所有問題"""
        with self.db_manager.get_session() as session:
            return session.query(IssueRecord).filter_by(analysis_id=analysis_id).all()
