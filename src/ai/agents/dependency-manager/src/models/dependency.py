"""
依賴項模型 - Dependency Model
定義依賴項的數據結構和分析結果
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class DependencyType(Enum):
    """依賴類型"""
    DIRECT = "direct"           # 直接依賴
    TRANSITIVE = "transitive"   # 傳遞依賴
    DEV = "dev"                 # 開發依賴
    PEER = "peer"               # 對等依賴
    OPTIONAL = "optional"       # 可選依賴


class DependencyStatus(Enum):
    """依賴狀態"""
    UP_TO_DATE = "up_to_date"   # 最新版本
    OUTDATED = "outdated"       # 版本過時
    VULNERABLE = "vulnerable"   # 存在漏洞
    DEPRECATED = "deprecated"   # 已棄用
    UNKNOWN = "unknown"         # 未知狀態


class Ecosystem(Enum):
    """生態系統類型"""
    NPM = "npm"
    PIP = "pip"
    GO = "go"
    MAVEN = "maven"
    CARGO = "cargo"
    GRADLE = "gradle"


@dataclass
class Dependency:
    """
    依賴項數據結構
    
    Attributes:
        name: 套件名稱
        current_version: 當前版本
        latest_version: 最新版本
        ecosystem: 生態系統
        dep_type: 依賴類型
        status: 依賴狀態
        license: 許可證
        has_vulnerability: 是否存在漏洞
        vulnerability_count: 漏洞數量
    """
    name: str
    current_version: str
    ecosystem: Ecosystem
    latest_version: Optional[str] = None
    dep_type: DependencyType = DependencyType.DIRECT
    status: DependencyStatus = DependencyStatus.UNKNOWN
    license: Optional[str] = None
    has_vulnerability: bool = False
    vulnerability_count: int = 0
    
    def is_outdated(self) -> bool:
        """檢查是否過時"""
        if not self.latest_version:
            return False
        return self.current_version != self.latest_version
    
    def __str__(self) -> str:
        return f"{self.name}@{self.current_version}"


@dataclass
class DependencyAnalysis:
    """
    依賴分析結果
    
    Attributes:
        analysis_id: 分析 ID
        project: 專案名稱
        ecosystem: 生態系統
        timestamp: 分析時間
        dependencies: 依賴項列表
        total_count: 總依賴數
        direct_count: 直接依賴數
        transitive_count: 傳遞依賴數
        outdated_count: 過時依賴數
        vulnerable_count: 有漏洞的依賴數
    """
    analysis_id: str
    project: str
    ecosystem: Ecosystem
    timestamp: datetime = field(default_factory=datetime.utcnow)
    dependencies: List[Dependency] = field(default_factory=list)
    total_count: int = 0
    direct_count: int = 0
    transitive_count: int = 0
    outdated_count: int = 0
    vulnerable_count: int = 0
    
    def add_dependency(self, dep: Dependency) -> None:
        """添加依賴項"""
        self.dependencies.append(dep)
        self.total_count += 1
        
        if dep.dep_type == DependencyType.DIRECT:
            self.direct_count += 1
        elif dep.dep_type == DependencyType.TRANSITIVE:
            self.transitive_count += 1
            
        if dep.is_outdated():
            self.outdated_count += 1
            
        if dep.has_vulnerability:
            self.vulnerable_count += 1
    
    def get_outdated_dependencies(self) -> List[Dependency]:
        """獲取過時的依賴項"""
        return [d for d in self.dependencies if d.is_outdated()]
    
    def get_vulnerable_dependencies(self) -> List[Dependency]:
        """獲取有漏洞的依賴項"""
        return [d for d in self.dependencies if d.has_vulnerability]
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            "analysis_id": self.analysis_id,
            "project": self.project,
            "ecosystem": self.ecosystem.value,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total_dependencies": self.total_count,
                "direct_dependencies": self.direct_count,
                "transitive_dependencies": self.transitive_count,
                "outdated": self.outdated_count,
                "vulnerable": self.vulnerable_count
            },
            "dependencies": [
                {
                    "name": d.name,
                    "current_version": d.current_version,
                    "latest_version": d.latest_version,
                    "type": d.dep_type.value,
                    "status": d.status.value,
                    "license": d.license
                }
                for d in self.dependencies
            ]
        }
