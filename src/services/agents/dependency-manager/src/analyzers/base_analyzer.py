"""
基礎分析器 - Base Analyzer
所有生態系統分析器的基類
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from ..models.dependency import Dependency, DependencyAnalysis, Ecosystem

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    基礎分析器抽象類
    
    所有生態系統分析器必須繼承此類並實現抽象方法。
    """

    def __init__(self, ecosystem: Ecosystem):
        """
        初始化分析器
        
        Args:
            ecosystem: 生態系統類型
        """
        self.ecosystem = ecosystem
        logger.info(f"初始化 {ecosystem.value} 分析器")

    @abstractmethod
    def get_manifest_files(self) -> list[str]:
        """
        獲取清單文件名稱列表
        
        Returns:
            清單文件名稱列表 (例如 ['package.json'])
        """
        pass

    @abstractmethod
    async def parse_manifest(self, manifest_path: Path) -> list[Dependency]:
        """
        解析清單文件
        
        Args:
            manifest_path: 清單文件路徑
            
        Returns:
            依賴項列表
        """
        pass

    @abstractmethod
    async def get_latest_version(self, package_name: str) -> str | None:
        """
        獲取套件最新版本
        
        Args:
            package_name: 套件名稱
            
        Returns:
            最新版本號，如果無法獲取則返回 None
        """
        pass

    def find_manifest(self, project_path: Path) -> Path | None:
        """
        在專案目錄中查找清單文件
        
        Args:
            project_path: 專案路徑
            
        Returns:
            清單文件路徑，如果找不到則返回 None
        """
        for manifest_name in self.get_manifest_files():
            manifest_path = project_path / manifest_name
            if manifest_path.exists():
                logger.info(f"找到清單文件: {manifest_path}")
                return manifest_path

        logger.warning(f"在 {project_path} 中未找到 {self.ecosystem.value} 清單文件")
        return None

    async def analyze(self, project_path: Path, analysis_id: str) -> DependencyAnalysis | None:
        """
        分析專案依賴
        
        Args:
            project_path: 專案路徑
            analysis_id: 分析 ID
            
        Returns:
            依賴分析結果
        """
        manifest_path = self.find_manifest(project_path)
        if not manifest_path:
            return None

        logger.info(f"開始分析 {self.ecosystem.value} 依賴: {manifest_path}")

        # 解析清單文件
        dependencies = await self.parse_manifest(manifest_path)

        # 創建分析結果
        analysis = DependencyAnalysis(
            analysis_id=analysis_id,
            project=project_path.name,
            ecosystem=self.ecosystem
        )

        # 檢查每個依賴的最新版本
        for dep in dependencies:
            latest = await self.get_latest_version(dep.name)
            if latest:
                dep.latest_version = latest

            analysis.add_dependency(dep)

        logger.info(f"分析完成: 共 {analysis.total_count} 個依賴項, {analysis.outdated_count} 個過時")

        return analysis
