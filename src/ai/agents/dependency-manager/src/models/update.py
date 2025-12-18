"""
更新模型 - Update Model
定義依賴更新的數據結構
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class UpdateType(Enum):
    """更新類型 (語義化版本)"""
    MAJOR = "major"     # 主版本更新 (x.0.0)
    MINOR = "minor"     # 次版本更新 (0.x.0)
    PATCH = "patch"     # 修補版本更新 (0.0.x)
    SECURITY = "security"  # 安全更新
    UNKNOWN = "unknown"


class UpdateStatus(Enum):
    """更新狀態"""
    PENDING = "pending"         # 待處理
    IN_PROGRESS = "in_progress" # 進行中
    SUCCESS = "success"         # 成功
    FAILED = "failed"           # 失敗
    SKIPPED = "skipped"         # 跳過
    ROLLED_BACK = "rolled_back" # 已回滾


class UpdatePolicy(Enum):
    """更新策略"""
    AUTO = "auto"       # 自動更新
    PR = "pr"           # 建立 PR
    MANUAL = "manual"   # 手動更新
    SKIP = "skip"       # 跳過


@dataclass
class Update:
    """
    依賴更新數據結構
    
    Attributes:
        package: 套件名稱
        from_version: 原版本
        to_version: 目標版本
        update_type: 更新類型
        status: 更新狀態
        policy: 更新策略
        is_security_fix: 是否為安全修復
        changelog_url: 更新日誌連結
        breaking_changes: 是否有破壞性變更
    """
    package: str
    from_version: str
    to_version: str
    update_type: UpdateType = UpdateType.UNKNOWN
    status: UpdateStatus = UpdateStatus.PENDING
    policy: UpdatePolicy = UpdatePolicy.MANUAL
    is_security_fix: bool = False
    changelog_url: Optional[str] = None
    breaking_changes: bool = False
    error_message: Optional[str] = None
    
    def is_major_update(self) -> bool:
        """檢查是否為主版本更新"""
        return self.update_type == UpdateType.MAJOR
    
    def requires_review(self) -> bool:
        """檢查是否需要人工審查"""
        return self.update_type == UpdateType.MAJOR or self.breaking_changes
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "package": self.package,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "update_type": self.update_type.value,
            "status": self.status.value,
            "policy": self.policy.value,
            "is_security_fix": self.is_security_fix,
            "changelog_url": self.changelog_url,
            "breaking_changes": self.breaking_changes,
            "error_message": self.error_message
        }
    
    def __str__(self) -> str:
        return f"{self.package}: {self.from_version} -> {self.to_version}"


@dataclass 
class UpdateResult:
    """
    更新結果
    
    Attributes:
        result_id: 結果 ID
        timestamp: 更新時間
        updates: 更新列表
        success_count: 成功數
        failed_count: 失敗數
        skipped_count: 跳過數
        pr_created: 是否建立了 PR
        pr_url: PR 連結
    """
    result_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    updates: List[Update] = field(default_factory=list)
    success_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    pr_created: bool = False
    pr_url: Optional[str] = None
    
    def add_update(self, update: Update) -> None:
        """添加更新結果"""
        self.updates.append(update)
        
        if update.status == UpdateStatus.SUCCESS:
            self.success_count += 1
        elif update.status == UpdateStatus.FAILED:
            self.failed_count += 1
        elif update.status == UpdateStatus.SKIPPED:
            self.skipped_count += 1
    
    def has_failures(self) -> bool:
        """檢查是否有失敗"""
        return self.failed_count > 0
    
    def get_successful_updates(self) -> List[Update]:
        """獲取成功的更新"""
        return [u for u in self.updates if u.status == UpdateStatus.SUCCESS]
    
    def get_failed_updates(self) -> List[Update]:
        """獲取失敗的更新"""
        return [u for u in self.updates if u.status == UpdateStatus.FAILED]
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "result_id": self.result_id,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total": len(self.updates),
                "success": self.success_count,
                "failed": self.failed_count,
                "skipped": self.skipped_count
            },
            "updates": [u.to_dict() for u in self.updates],
            "pr_created": self.pr_created,
            "pr_url": self.pr_url
        }
