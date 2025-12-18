"""
Audit Trail System (審計追蹤系統)

記錄所有模組操作和變更，確保完整的審計追蹤。

Reference: DevSecOps audit requirements [2] [5]
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json
import hashlib


class AuditAction(Enum):
    """審計動作類型"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    VALIDATE = "validate"
    SIGN = "sign"
    VERIFY = "verify"
    EXPORT = "export"
    IMPORT = "import"


class AuditLevel(Enum):
    """審計級別"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """審計條目"""
    id: str
    timestamp: datetime
    action: AuditAction
    actor: str
    resource_type: str
    resource_id: str
    level: AuditLevel = AuditLevel.INFO
    details: Dict[str, Any] = field(default_factory=dict)
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action.value,
            'actor': self.actor,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'level': self.level.value,
            'details': self.details,
            'previous_state': self.previous_state,
            'new_state': self.new_state,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'correlation_id': self.correlation_id,
        }
    
    def get_hash(self) -> str:
        """獲取條目哈希值（用於完整性驗證）"""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class AuditLogger:
    """
    審計日誌記錄器
    
    記錄所有系統操作的完整審計追蹤。
    """
    
    def __init__(self, storage_backend: Optional[str] = None):
        self._entries: List[AuditEntry] = []
        self._storage_backend = storage_backend
        self._retention_days = 365  # 默認保留 365 天
    
    def log(self, 
            action: AuditAction,
            actor: str,
            resource_type: str,
            resource_id: str,
            level: AuditLevel = AuditLevel.INFO,
            details: Optional[Dict[str, Any]] = None,
            previous_state: Optional[Dict[str, Any]] = None,
            new_state: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None) -> AuditEntry:
        """
        記錄審計事件
        
        Args:
            action: 操作類型
            actor: 執行者
            resource_type: 資源類型
            resource_id: 資源 ID
            level: 審計級別
            details: 詳細信息
            previous_state: 操作前狀態
            new_state: 操作後狀態
            correlation_id: 關聯 ID（用於追蹤相關事件）
        
        Returns:
            AuditEntry: 審計條目
        """
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            action=action,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            level=level,
            details=details or {},
            previous_state=previous_state,
            new_state=new_state,
            correlation_id=correlation_id,
        )
        
        self._entries.append(entry)
        return entry
    
    def log_create(self, actor: str, resource_type: str, resource_id: str,
                   new_state: Dict[str, Any], details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """記錄創建操作"""
        return self.log(
            action=AuditAction.CREATE,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            new_state=new_state,
            details=details,
        )
    
    def log_update(self, actor: str, resource_type: str, resource_id: str,
                   previous_state: Dict[str, Any], new_state: Dict[str, Any],
                   details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """記錄更新操作"""
        return self.log(
            action=AuditAction.UPDATE,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            previous_state=previous_state,
            new_state=new_state,
            details=details,
        )
    
    def log_delete(self, actor: str, resource_type: str, resource_id: str,
                   previous_state: Dict[str, Any], details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """記錄刪除操作"""
        return self.log(
            action=AuditAction.DELETE,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            level=AuditLevel.WARNING,
            previous_state=previous_state,
            details=details,
        )
    
    def log_approve(self, actor: str, resource_type: str, resource_id: str,
                    details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """記錄審批操作"""
        return self.log(
            action=AuditAction.APPROVE,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )
    
    def log_deploy(self, actor: str, resource_type: str, resource_id: str,
                   details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """記錄部署操作"""
        return self.log(
            action=AuditAction.DEPLOY,
            actor=actor,
            resource_type=resource_type,
            resource_id=resource_id,
            level=AuditLevel.CRITICAL,
            details=details,
        )
    
    def get_entries(self, 
                    resource_type: Optional[str] = None,
                    resource_id: Optional[str] = None,
                    action: Optional[AuditAction] = None,
                    actor: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    limit: int = 100) -> List[AuditEntry]:
        """
        查詢審計記錄
        
        Args:
            resource_type: 資源類型過濾
            resource_id: 資源 ID 過濾
            action: 操作類型過濾
            actor: 執行者過濾
            start_time: 開始時間
            end_time: 結束時間
            limit: 最大返回數量
        
        Returns:
            List[AuditEntry]: 審計條目列表
        """
        entries = self._entries.copy()
        
        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]
        
        if resource_id:
            entries = [e for e in entries if e.resource_id == resource_id]
        
        if action:
            entries = [e for e in entries if e.action == action]
        
        if actor:
            entries = [e for e in entries if e.actor == actor]
        
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]
        
        # 按時間倒序排列
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        return entries[:limit]
    
    def get_resource_history(self, resource_type: str, resource_id: str) -> List[AuditEntry]:
        """獲取資源的完整歷史"""
        return self.get_entries(resource_type=resource_type, resource_id=resource_id, limit=1000)
    
    def export(self, format: str = "json") -> str:
        """導出審計日誌"""
        if format == "json":
            return json.dumps([e.to_dict() for e in self._entries], indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


@dataclass
class ChangeRecord:
    """變更記錄"""
    id: str
    timestamp: datetime
    resource_type: str
    resource_id: str
    change_type: str  # added, modified, removed
    field_path: str
    old_value: Any = None
    new_value: Any = None
    actor: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'change_type': self.change_type,
            'field_path': self.field_path,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'actor': self.actor,
        }


class ChangeTracker:
    """
    變更追蹤器
    
    追蹤資源的詳細變更歷史。
    """
    
    def __init__(self):
        self._records: List[ChangeRecord] = []
    
    def track_changes(self, 
                      resource_type: str,
                      resource_id: str,
                      old_state: Optional[Dict[str, Any]],
                      new_state: Optional[Dict[str, Any]],
                      actor: str = "") -> List[ChangeRecord]:
        """
        追蹤變更
        
        Args:
            resource_type: 資源類型
            resource_id: 資源 ID
            old_state: 舊狀態
            new_state: 新狀態
            actor: 執行者
        
        Returns:
            List[ChangeRecord]: 變更記錄列表
        """
        records = []
        timestamp = datetime.now()
        
        if old_state is None and new_state is not None:
            # 創建
            for key, value in self._flatten_dict(new_state):
                record = ChangeRecord(
                    id=str(uuid.uuid4()),
                    timestamp=timestamp,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    change_type='added',
                    field_path=key,
                    new_value=value,
                    actor=actor,
                )
                records.append(record)
        
        elif old_state is not None and new_state is None:
            # 刪除
            for key, value in self._flatten_dict(old_state):
                record = ChangeRecord(
                    id=str(uuid.uuid4()),
                    timestamp=timestamp,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    change_type='removed',
                    field_path=key,
                    old_value=value,
                    actor=actor,
                )
                records.append(record)
        
        else:
            # 更新
            old_flat = dict(self._flatten_dict(old_state or {}))
            new_flat = dict(self._flatten_dict(new_state or {}))
            
            all_keys = set(old_flat.keys()) | set(new_flat.keys())
            
            for key in all_keys:
                old_value = old_flat.get(key)
                new_value = new_flat.get(key)
                
                if old_value != new_value:
                    if key not in old_flat:
                        change_type = 'added'
                    elif key not in new_flat:
                        change_type = 'removed'
                    else:
                        change_type = 'modified'
                    
                    record = ChangeRecord(
                        id=str(uuid.uuid4()),
                        timestamp=timestamp,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        change_type=change_type,
                        field_path=key,
                        old_value=old_value,
                        new_value=new_value,
                        actor=actor,
                    )
                    records.append(record)
        
        self._records.extend(records)
        return records
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> List[tuple]:
        """展平字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key))
            else:
                items.append((new_key, v))
        return items
    
    def get_changes(self, 
                    resource_type: Optional[str] = None,
                    resource_id: Optional[str] = None,
                    change_type: Optional[str] = None,
                    limit: int = 100) -> List[ChangeRecord]:
        """獲取變更記錄"""
        records = self._records.copy()
        
        if resource_type:
            records = [r for r in records if r.resource_type == resource_type]
        
        if resource_id:
            records = [r for r in records if r.resource_id == resource_id]
        
        if change_type:
            records = [r for r in records if r.change_type == change_type]
        
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:limit]
    
    def get_field_history(self, resource_type: str, resource_id: str, field_path: str) -> List[ChangeRecord]:
        """獲取特定字段的歷史"""
        records = [
            r for r in self._records
            if r.resource_type == resource_type 
            and r.resource_id == resource_id
            and r.field_path == field_path
        ]
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records
