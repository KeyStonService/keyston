"""
═══════════════════════════════════════════════════════════
        Capability Registry - 能力註冊表
        追蹤和管理系統的實際執行能力
═══════════════════════════════════════════════════════════

核心功能：
1. 註冊系統能力
2. 驗證能力狀態
3. 追蹤能力依賴
4. 動態能力發現
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
import uuid


class CapabilityStatus(Enum):
    """能力狀態"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    INITIALIZING = "initializing"
    ERROR = "error"


@dataclass
class CapabilityRequirement:
    """能力需求"""
    
    name: str
    description: str = ""
    required: bool = True
    
    # 版本要求
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    
    # 替代方案
    alternatives: List[str] = field(default_factory=list)


@dataclass
class Capability:
    """能力定義"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = ""
    
    # 狀態
    status: CapabilityStatus = CapabilityStatus.UNAVAILABLE
    
    # 版本
    version: str = "1.0.0"
    
    # 依賴
    requirements: List[CapabilityRequirement] = field(default_factory=list)
    
    # 健康檢查
    health_check: Optional[Callable] = None
    last_health_check: Optional[datetime] = None
    health_check_interval_seconds: int = 60
    
    # 執行器
    executor: Optional[Callable] = None
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 統計
    invocation_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_latency_ms: float = 0.0


class CapabilityRegistry:
    """
    能力註冊表 - 管理系統的實際執行能力
    
    核心問題：知識不等於能力
    - 有知識不代表能執行
    - 需要實際的執行器和連接器
    - 需要驗證能力是否可用
    """
    
    def __init__(self):
        """初始化能力註冊表"""
        
        # 能力存儲
        self._capabilities: Dict[str, Capability] = {}
        
        # 類別索引
        self._category_index: Dict[str, Set[str]] = {}
        
        # 依賴圖
        self._dependency_graph: Dict[str, Set[str]] = {}
        
        # 能力監聽器
        self._listeners: List[Callable] = []
        
        # 初始化默認能力
        self._register_default_capabilities()
    
    def _register_default_capabilities(self):
        """註冊默認能力"""
        
        # 數據庫能力
        self.register(Capability(
            name="database.query",
            description="執行數據庫查詢",
            category="database",
            status=CapabilityStatus.AVAILABLE,
            requirements=[
                CapabilityRequirement(
                    name="database_connection",
                    description="數據庫連接",
                    required=True,
                ),
            ],
        ))
        
        self.register(Capability(
            name="database.write",
            description="執行數據庫寫入",
            category="database",
            status=CapabilityStatus.AVAILABLE,
            requirements=[
                CapabilityRequirement(
                    name="database_connection",
                    description="數據庫連接",
                    required=True,
                ),
                CapabilityRequirement(
                    name="write_permission",
                    description="寫入權限",
                    required=True,
                ),
            ],
        ))
        
        # 部署能力
        self.register(Capability(
            name="deployment.execute",
            description="執行應用部署",
            category="deployment",
            status=CapabilityStatus.AVAILABLE,
            requirements=[
                CapabilityRequirement(
                    name="container_runtime",
                    description="容器運行時",
                    required=True,
                    alternatives=["docker", "podman", "containerd"],
                ),
            ],
        ))
        
        # 文件系統能力
        self.register(Capability(
            name="filesystem.read",
            description="讀取文件系統",
            category="filesystem",
            status=CapabilityStatus.AVAILABLE,
        ))
        
        self.register(Capability(
            name="filesystem.write",
            description="寫入文件系統",
            category="filesystem",
            status=CapabilityStatus.AVAILABLE,
            requirements=[
                CapabilityRequirement(
                    name="write_permission",
                    description="寫入權限",
                    required=True,
                ),
            ],
        ))
        
        # API 調用能力
        self.register(Capability(
            name="api.call",
            description="執行 API 調用",
            category="network",
            status=CapabilityStatus.AVAILABLE,
            requirements=[
                CapabilityRequirement(
                    name="network_access",
                    description="網絡訪問",
                    required=True,
                ),
            ],
        ))
        
        # 配置管理能力
        self.register(Capability(
            name="config.read",
            description="讀取配置",
            category="configuration",
            status=CapabilityStatus.AVAILABLE,
        ))
        
        self.register(Capability(
            name="config.write",
            description="寫入配置",
            category="configuration",
            status=CapabilityStatus.AVAILABLE,
        ))
        
        # 監控能力
        self.register(Capability(
            name="monitoring.collect",
            description="收集監控數據",
            category="monitoring",
            status=CapabilityStatus.AVAILABLE,
        ))
    
    def register(self, capability: Capability) -> str:
        """
        註冊能力
        
        Args:
            capability: 能力定義
            
        Returns:
            能力 ID
        """
        
        # 存儲能力
        self._capabilities[capability.name] = capability
        
        # 更新類別索引
        if capability.category not in self._category_index:
            self._category_index[capability.category] = set()
        self._category_index[capability.category].add(capability.name)
        
        # 更新依賴圖
        self._dependency_graph[capability.name] = set()
        for req in capability.requirements:
            self._dependency_graph[capability.name].add(req.name)
        
        # 通知監聽器
        self._notify_listeners("registered", capability)
        
        return capability.id
    
    def unregister(self, name: str) -> bool:
        """
        註銷能力
        
        Args:
            name: 能力名稱
            
        Returns:
            是否成功
        """
        
        if name not in self._capabilities:
            return False
        
        capability = self._capabilities.pop(name)
        
        # 更新類別索引
        if capability.category in self._category_index:
            self._category_index[capability.category].discard(name)
        
        # 更新依賴圖
        if name in self._dependency_graph:
            del self._dependency_graph[name]
        
        # 通知監聽器
        self._notify_listeners("unregistered", capability)
        
        return True
    
    def get(self, name: str) -> Optional[Capability]:
        """獲取能力"""
        return self._capabilities.get(name)
    
    def has(self, name: str) -> bool:
        """檢查是否有能力"""
        return name in self._capabilities
    
    def is_available(self, name: str) -> bool:
        """檢查能力是否可用"""
        capability = self.get(name)
        if capability is None:
            return False
        return capability.status == CapabilityStatus.AVAILABLE
    
    def get_by_category(self, category: str) -> List[Capability]:
        """按類別獲取能力"""
        names = self._category_index.get(category, set())
        return [self._capabilities[name] for name in names if name in self._capabilities]
    
    def get_all(self) -> List[Capability]:
        """獲取所有能力"""
        return list(self._capabilities.values())
    
    def get_available(self) -> List[Capability]:
        """獲取所有可用能力"""
        return [
            cap for cap in self._capabilities.values()
            if cap.status == CapabilityStatus.AVAILABLE
        ]
    
    def check_requirements(self, name: str) -> Dict[str, Any]:
        """
        檢查能力需求
        
        Args:
            name: 能力名稱
            
        Returns:
            檢查結果
        """
        
        capability = self.get(name)
        if capability is None:
            return {
                "satisfied": False,
                "error": f"Capability not found: {name}",
            }
        
        result = {
            "capability": name,
            "satisfied": True,
            "requirements": [],
        }
        
        for req in capability.requirements:
            req_result = {
                "name": req.name,
                "required": req.required,
                "satisfied": True,  # 默認滿足（模擬）
                "message": "Requirement satisfied",
            }
            
            # 檢查是否有對應的能力或連接器
            # 這裡簡化處理，實際應該檢查真實的依賴
            if not self._check_requirement(req):
                req_result["satisfied"] = False
                req_result["message"] = f"Requirement not met: {req.name}"
                
                if req.required:
                    result["satisfied"] = False
            
            result["requirements"].append(req_result)
        
        return result
    
    def _check_requirement(self, requirement: CapabilityRequirement) -> bool:
        """檢查單個需求"""
        # 簡化實現：默認返回 True
        # 實際應該檢查連接器、權限等
        return True
    
    def update_status(self, name: str, status: CapabilityStatus) -> bool:
        """
        更新能力狀態
        
        Args:
            name: 能力名稱
            status: 新狀態
            
        Returns:
            是否成功
        """
        
        capability = self.get(name)
        if capability is None:
            return False
        
        old_status = capability.status
        capability.status = status
        
        # 通知監聯器
        if old_status != status:
            self._notify_listeners("status_changed", capability, {
                "old_status": old_status,
                "new_status": status,
            })
        
        return True
    
    def record_invocation(
        self,
        name: str,
        success: bool,
        latency_ms: float
    ) -> bool:
        """
        記錄能力調用
        
        Args:
            name: 能力名稱
            success: 是否成功
            latency_ms: 延遲（毫秒）
            
        Returns:
            是否成功
        """
        
        capability = self.get(name)
        if capability is None:
            return False
        
        capability.invocation_count += 1
        
        if success:
            capability.success_count += 1
        else:
            capability.failure_count += 1
        
        # 更新平均延遲
        total = capability.invocation_count
        current_avg = capability.average_latency_ms
        capability.average_latency_ms = (
            (current_avg * (total - 1) + latency_ms) / total
        )
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        
        total = len(self._capabilities)
        available = len([c for c in self._capabilities.values() 
                        if c.status == CapabilityStatus.AVAILABLE])
        
        return {
            "total_capabilities": total,
            "available_capabilities": available,
            "unavailable_capabilities": total - available,
            "categories": list(self._category_index.keys()),
            "capabilities_by_category": {
                cat: len(caps) 
                for cat, caps in self._category_index.items()
            },
        }
    
    def add_listener(self, listener: Callable):
        """添加監聽器"""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable):
        """移除監聽器"""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(
        self,
        event: str,
        capability: Capability,
        data: Optional[Dict[str, Any]] = None
    ):
        """通知監聽器"""
        for listener in self._listeners:
            try:
                listener(event, capability, data or {})
            except Exception:
                pass  # 忽略監聽器錯誤
    
    def get_dependency_tree(self, name: str) -> Dict[str, Any]:
        """
        獲取能力依賴樹
        
        Args:
            name: 能力名稱
            
        Returns:
            依賴樹
        """
        
        visited = set()
        
        def build_tree(cap_name: str) -> Dict[str, Any]:
            if cap_name in visited:
                return {"name": cap_name, "circular": True}
            
            visited.add(cap_name)
            
            capability = self.get(cap_name)
            if capability is None:
                return {"name": cap_name, "exists": False}
            
            tree = {
                "name": cap_name,
                "status": capability.status.value,
                "dependencies": [],
            }
            
            for req in capability.requirements:
                dep_tree = build_tree(req.name)
                tree["dependencies"].append(dep_tree)
            
            return tree
        
        return build_tree(name)
