"""
審計日誌模組 - Audit Logger
追蹤所有依賴管理操作的審計日誌
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """審計事件類型"""
    # 分析事件
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"
    
    # 漏洞掃描事件
    VULNERABILITY_SCAN_STARTED = "vulnerability_scan_started"
    VULNERABILITY_SCAN_COMPLETED = "vulnerability_scan_completed"
    VULNERABILITY_DETECTED = "vulnerability_detected"
    
    # 許可證掃描事件
    LICENSE_SCAN_STARTED = "license_scan_started"
    LICENSE_SCAN_COMPLETED = "license_scan_completed"
    LICENSE_VIOLATION_DETECTED = "license_violation_detected"
    
    # 更新事件
    UPDATE_STARTED = "update_started"
    UPDATE_COMPLETED = "update_completed"
    UPDATE_FAILED = "update_failed"
    UPDATE_ROLLED_BACK = "update_rolled_back"
    
    # PR 事件
    PR_CREATED = "pr_created"
    PR_MERGED = "pr_merged"
    PR_CLOSED = "pr_closed"
    
    # 配置變更
    CONFIG_CHANGED = "config_changed"
    POLICY_CHANGED = "policy_changed"
    
    # 例外事件
    EXCEPTION_ADDED = "exception_added"
    EXCEPTION_REMOVED = "exception_removed"


class AuditSeverity(Enum):
    """審計事件嚴重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """
    審計事件
    
    Attributes:
        event_id: 事件 ID
        event_type: 事件類型
        timestamp: 事件時間
        severity: 嚴重程度
        actor: 操作者（用戶或系統）
        target: 操作目標
        details: 詳細資訊
        metadata: 額外元數據
    """
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    severity: AuditSeverity = AuditSeverity.INFO
    actor: str = "system"
    target: str = ""
    details: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "actor": self.actor,
            "target": self.target,
            "details": self.details,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLogger:
    """
    審計日誌記錄器
    
    提供 append-only 審計日誌功能，確保所有依賴管理操作可追溯
    """
    
    def __init__(
        self, 
        log_file: Optional[str] = None,
        retention_days: int = 90
    ):
        """
        初始化審計日誌記錄器
        
        Args:
            log_file: 日誌文件路徑
            retention_days: 日誌保留天數
        """
        self.log_file = Path(log_file) if log_file else None
        self.retention_days = retention_days
        self._events: List[AuditEvent] = []
        self._initialized = False
        
        if self.log_file:
            self._ensure_log_file()
        
        logger.info("審計日誌記錄器初始化完成")
    
    def _ensure_log_file(self) -> None:
        """確保日誌文件存在"""
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.log_file.exists():
                self.log_file.touch()
            self._initialized = True
    
    def log(
        self,
        event_type: AuditEventType,
        target: str = "",
        details: str = "",
        severity: AuditSeverity = AuditSeverity.INFO,
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """
        記錄審計事件
        
        Args:
            event_type: 事件類型
            target: 操作目標
            details: 詳細描述
            severity: 嚴重程度
            actor: 操作者
            metadata: 額外元數據
            
        Returns:
            審計事件對象
        """
        event = AuditEvent(
            event_id=f"audit-{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            timestamp=datetime.utcnow(),
            severity=severity,
            actor=actor,
            target=target,
            details=details,
            metadata=metadata or {}
        )
        
        self._events.append(event)
        
        # 寫入文件（append-only）
        if self.log_file and self._initialized:
            self._append_to_file(event)
        
        # 記錄到標準日誌
        log_level = {
            AuditSeverity.INFO: logging.INFO,
            AuditSeverity.WARNING: logging.WARNING,
            AuditSeverity.ERROR: logging.ERROR,
            AuditSeverity.CRITICAL: logging.CRITICAL
        }.get(severity, logging.INFO)
        
        logger.log(
            log_level, 
            f"[AUDIT] {event_type.value}: {target} - {details}"
        )
        
        return event
    
    def _append_to_file(self, event: AuditEvent) -> None:
        """
        追加事件到文件（append-only）
        
        Args:
            event: 審計事件
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(event.to_json() + '\n')
        except Exception as e:
            logger.error(f"寫入審計日誌失敗: {e}")
    
    def log_analysis_started(
        self, 
        project: str, 
        ecosystem: str
    ) -> AuditEvent:
        """記錄分析開始"""
        return self.log(
            event_type=AuditEventType.ANALYSIS_STARTED,
            target=project,
            details=f"開始分析 {ecosystem} 依賴",
            metadata={"ecosystem": ecosystem}
        )
    
    def log_analysis_completed(
        self, 
        project: str, 
        total_deps: int,
        outdated: int,
        vulnerable: int
    ) -> AuditEvent:
        """記錄分析完成"""
        return self.log(
            event_type=AuditEventType.ANALYSIS_COMPLETED,
            target=project,
            details=f"分析完成: {total_deps} 個依賴, {outdated} 個過時, {vulnerable} 個有漏洞",
            metadata={
                "total_dependencies": total_deps,
                "outdated_count": outdated,
                "vulnerable_count": vulnerable
            }
        )
    
    def log_vulnerability_detected(
        self, 
        package: str, 
        vulnerability_id: str,
        severity: str
    ) -> AuditEvent:
        """記錄發現漏洞"""
        audit_severity = AuditSeverity.CRITICAL if severity == "CRITICAL" else AuditSeverity.WARNING
        
        return self.log(
            event_type=AuditEventType.VULNERABILITY_DETECTED,
            target=package,
            details=f"發現漏洞 {vulnerability_id} (嚴重程度: {severity})",
            severity=audit_severity,
            metadata={
                "vulnerability_id": vulnerability_id,
                "vulnerability_severity": severity
            }
        )
    
    def log_update_started(
        self, 
        package: str, 
        from_version: str,
        to_version: str
    ) -> AuditEvent:
        """記錄更新開始"""
        return self.log(
            event_type=AuditEventType.UPDATE_STARTED,
            target=package,
            details=f"開始更新 {from_version} -> {to_version}",
            metadata={
                "from_version": from_version,
                "to_version": to_version
            }
        )
    
    def log_update_completed(
        self, 
        package: str, 
        from_version: str,
        to_version: str
    ) -> AuditEvent:
        """記錄更新完成"""
        return self.log(
            event_type=AuditEventType.UPDATE_COMPLETED,
            target=package,
            details=f"更新完成 {from_version} -> {to_version}",
            metadata={
                "from_version": from_version,
                "to_version": to_version
            }
        )
    
    def log_update_failed(
        self, 
        package: str, 
        error: str
    ) -> AuditEvent:
        """記錄更新失敗"""
        return self.log(
            event_type=AuditEventType.UPDATE_FAILED,
            target=package,
            details=f"更新失敗: {error}",
            severity=AuditSeverity.ERROR,
            metadata={"error": error}
        )
    
    def log_pr_created(
        self, 
        pr_url: str, 
        packages: List[str]
    ) -> AuditEvent:
        """記錄 PR 建立"""
        return self.log(
            event_type=AuditEventType.PR_CREATED,
            target=pr_url,
            details=f"建立 PR 更新 {len(packages)} 個套件",
            metadata={"packages": packages}
        )
    
    def log_license_violation(
        self, 
        package: str, 
        license_id: str
    ) -> AuditEvent:
        """記錄許可證違規"""
        return self.log(
            event_type=AuditEventType.LICENSE_VIOLATION_DETECTED,
            target=package,
            details=f"許可證違規: {license_id}",
            severity=AuditSeverity.WARNING,
            metadata={"license": license_id}
        )
    
    def log_config_changed(
        self, 
        setting: str, 
        old_value: Any,
        new_value: Any,
        actor: str = "system"
    ) -> AuditEvent:
        """記錄配置變更"""
        return self.log(
            event_type=AuditEventType.CONFIG_CHANGED,
            target=setting,
            details=f"配置變更: {old_value} -> {new_value}",
            actor=actor,
            metadata={
                "old_value": str(old_value),
                "new_value": str(new_value)
            }
        )
    
    def get_events(
        self,
        event_type: Optional[AuditEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[AuditSeverity] = None
    ) -> List[AuditEvent]:
        """
        獲取審計事件
        
        Args:
            event_type: 過濾事件類型
            start_time: 開始時間
            end_time: 結束時間
            severity: 過濾嚴重程度
            
        Returns:
            過濾後的事件列表
        """
        filtered = self._events
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
        
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
        
        if severity:
            filtered = [e for e in filtered if e.severity == severity]
        
        return filtered
    
    def get_summary(self) -> Dict[str, Any]:
        """
        獲取審計摘要
        
        Returns:
            摘要資訊
        """
        summary = {
            "total_events": len(self._events),
            "by_type": {},
            "by_severity": {},
            "time_range": {
                "start": None,
                "end": None
            }
        }
        
        for event in self._events:
            # 按類型統計
            type_key = event.event_type.value
            summary["by_type"][type_key] = summary["by_type"].get(type_key, 0) + 1
            
            # 按嚴重程度統計
            sev_key = event.severity.value
            summary["by_severity"][sev_key] = summary["by_severity"].get(sev_key, 0) + 1
            
            # 時間範圍
            if not summary["time_range"]["start"] or event.timestamp < summary["time_range"]["start"]:
                summary["time_range"]["start"] = event.timestamp
            if not summary["time_range"]["end"] or event.timestamp > summary["time_range"]["end"]:
                summary["time_range"]["end"] = event.timestamp
        
        # 轉換時間格式
        if summary["time_range"]["start"]:
            summary["time_range"]["start"] = summary["time_range"]["start"].isoformat()
        if summary["time_range"]["end"]:
            summary["time_range"]["end"] = summary["time_range"]["end"].isoformat()
        
        return summary
    
    def export_events(self, output_path: str) -> None:
        """
        導出所有事件到文件
        
        Args:
            output_path: 輸出文件路徑
        """
        events_data = [e.to_dict() for e in self._events]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "export_time": datetime.utcnow().isoformat(),
                "total_events": len(events_data),
                "events": events_data
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已導出 {len(events_data)} 個審計事件到 {output_path}")
