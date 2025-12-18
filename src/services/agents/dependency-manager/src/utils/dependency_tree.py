"""
依賴樹模組 - Dependency Tree
依賴關係樹狀視覺化
"""

import logging
from dataclasses import dataclass, field
from enum import Enum

from ..models.dependency import Dependency, DependencyStatus

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """風險等級"""
    NONE = "none"       # 無風險
    LOW = "low"         # 低風險
    MEDIUM = "medium"   # 中風險
    HIGH = "high"       # 高風險
    CRITICAL = "critical"  # 嚴重風險


@dataclass
class TreeNode:
    """
    依賴樹節點
    
    Attributes:
        dependency: 依賴項
        children: 子依賴列表
        depth: 在樹中的深度
        risk_level: 風險等級
    """
    dependency: Dependency
    children: list["TreeNode"] = field(default_factory=list)
    depth: int = 0
    risk_level: RiskLevel = RiskLevel.NONE

    def add_child(self, child: "TreeNode") -> None:
        """添加子依賴"""
        child.depth = self.depth + 1
        self.children.append(child)

    def get_descendants_count(self) -> int:
        """獲取所有後代數量"""
        count = len(self.children)
        for child in self.children:
            count += child.get_descendants_count()
        return count

    def has_vulnerable_descendants(self) -> bool:
        """檢查是否有有漏洞的後代"""
        for child in self.children:
            if child.dependency.has_vulnerability:
                return True
            if child.has_vulnerable_descendants():
                return True
        return False


class DependencyTree:
    """
    依賴樹
    
    用於視覺化依賴關係和風險傳播
    """

    def __init__(self, project_name: str):
        """
        初始化依賴樹
        
        Args:
            project_name: 專案名稱
        """
        self.project_name = project_name
        self.root_nodes: list[TreeNode] = []
        self._all_nodes: dict[str, TreeNode] = {}

        logger.info(f"初始化依賴樹: {project_name}")

    def build_tree(
        self,
        dependencies: list[Dependency],
        parent_map: dict[str, list[str]] | None = None
    ) -> None:
        """
        建構依賴樹
        
        Args:
            dependencies: 依賴項列表
            parent_map: 父子關係映射 {parent_name: [child_names]}
        """
        # 創建所有節點
        for dep in dependencies:
            node = TreeNode(dependency=dep)
            self._all_nodes[dep.name] = node

            # 計算風險等級
            node.risk_level = self._calculate_risk(dep)

        # 建立關係
        if parent_map:
            for parent_name, children in parent_map.items():
                if parent_name in self._all_nodes:
                    parent_node = self._all_nodes[parent_name]
                    for child_name in children:
                        if child_name in self._all_nodes:
                            child_node = self._all_nodes[child_name]
                            parent_node.add_child(child_node)

        # 找出根節點（沒有父節點的依賴）
        children_set: set[str] = set()
        if parent_map:
            for children in parent_map.values():
                children_set.update(children)

        for name, node in self._all_nodes.items():
            if name not in children_set:
                self.root_nodes.append(node)

        logger.info(f"依賴樹建構完成: {len(self.root_nodes)} 個根節點, {len(self._all_nodes)} 個總節點")

    def _calculate_risk(self, dep: Dependency) -> RiskLevel:
        """
        計算依賴項的風險等級
        
        Args:
            dep: 依賴項
            
        Returns:
            風險等級
        """
        if dep.has_vulnerability and dep.vulnerability_count > 2:
            return RiskLevel.CRITICAL
        elif dep.has_vulnerability:
            return RiskLevel.HIGH
        elif dep.status == DependencyStatus.DEPRECATED:
            return RiskLevel.MEDIUM
        elif dep.is_outdated():
            return RiskLevel.LOW

        return RiskLevel.NONE

    def render_text(self, show_risk: bool = True) -> str:
        """
        渲染文字格式的依賴樹
        
        Args:
            show_risk: 是否顯示風險等級
            
        Returns:
            文字格式的樹狀圖
        """
        lines = [f"📦 {self.project_name}"]

        for i, node in enumerate(self.root_nodes):
            is_last = (i == len(self.root_nodes) - 1)
            lines.extend(self._render_node(node, "", is_last, show_risk))

        return "\n".join(lines)

    def _render_node(
        self,
        node: TreeNode,
        prefix: str,
        is_last: bool,
        show_risk: bool
    ) -> list[str]:
        """
        渲染單個節點
        
        Args:
            node: 樹節點
            prefix: 前綴字符串
            is_last: 是否是最後一個兄弟節點
            show_risk: 是否顯示風險
            
        Returns:
            渲染的行列表
        """
        lines = []

        # 構建節點顯示
        connector = "└── " if is_last else "├── "

        dep = node.dependency
        name_version = f"{dep.name}@{dep.current_version}"

        # 風險指示器
        risk_indicator = ""
        if show_risk:
            risk_indicators = {
                RiskLevel.CRITICAL: " 🔴",
                RiskLevel.HIGH: " 🟠",
                RiskLevel.MEDIUM: " 🟡",
                RiskLevel.LOW: " 🟢",
                RiskLevel.NONE: ""
            }
            risk_indicator = risk_indicators.get(node.risk_level, "")

        # 狀態標記
        status_mark = ""
        if dep.has_vulnerability:
            status_mark = " ⚠️"
        elif dep.is_outdated():
            status_mark = " ⬆️"

        lines.append(f"{prefix}{connector}{name_version}{status_mark}{risk_indicator}")

        # 遞歸渲染子節點
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            child_is_last = (i == len(node.children) - 1)
            lines.extend(self._render_node(child, child_prefix, child_is_last, show_risk))

        return lines

    def render_json(self) -> dict:
        """
        渲染 JSON 格式的依賴樹
        
        Returns:
            JSON 結構
        """
        def node_to_dict(node: TreeNode) -> dict:
            return {
                "name": node.dependency.name,
                "version": node.dependency.current_version,
                "latest_version": node.dependency.latest_version,
                "risk_level": node.risk_level.value,
                "has_vulnerability": node.dependency.has_vulnerability,
                "is_outdated": node.dependency.is_outdated(),
                "children": [node_to_dict(child) for child in node.children]
            }

        return {
            "project": self.project_name,
            "total_dependencies": len(self._all_nodes),
            "root_dependencies": len(self.root_nodes),
            "tree": [node_to_dict(node) for node in self.root_nodes]
        }

    def get_statistics(self) -> dict:
        """
        獲取依賴樹統計資訊
        
        Returns:
            統計資訊字典
        """
        stats = {
            "total_dependencies": len(self._all_nodes),
            "direct_dependencies": len(self.root_nodes),
            "max_depth": 0,
            "risk_summary": {
                RiskLevel.CRITICAL.value: 0,
                RiskLevel.HIGH.value: 0,
                RiskLevel.MEDIUM.value: 0,
                RiskLevel.LOW.value: 0,
                RiskLevel.NONE.value: 0
            },
            "vulnerable_count": 0,
            "outdated_count": 0
        }

        def process_node(node: TreeNode, depth: int = 0):
            stats["max_depth"] = max(stats["max_depth"], depth)
            stats["risk_summary"][node.risk_level.value] += 1

            if node.dependency.has_vulnerability:
                stats["vulnerable_count"] += 1
            if node.dependency.is_outdated():
                stats["outdated_count"] += 1

            for child in node.children:
                process_node(child, depth + 1)

        for root in self.root_nodes:
            process_node(root)

        return stats

    def find_path_to_vulnerable(self) -> list[list[str]]:
        """
        找出到有漏洞依賴的路徑
        
        Returns:
            路徑列表，每個路徑是依賴名稱列表
        """
        paths = []

        def find_paths(node: TreeNode, current_path: list[str]):
            current_path = current_path + [node.dependency.name]

            if node.dependency.has_vulnerability:
                paths.append(current_path)

            for child in node.children:
                find_paths(child, current_path)

        for root in self.root_nodes:
            find_paths(root, [])

        return paths
