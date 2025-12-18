"""
NPM 分析器 - NPM Analyzer
Node.js/npm 生態系統的依賴分析器
"""

import json
import logging
from typing import List, Optional
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from ..models.dependency import Dependency, DependencyType, Ecosystem

logger = logging.getLogger(__name__)


class NpmAnalyzer(BaseAnalyzer):
    """
    NPM 依賴分析器
    
    支援分析 package.json 和 package-lock.json 文件
    """
    
    def __init__(self):
        """初始化 NPM 分析器"""
        super().__init__(Ecosystem.NPM)
        self._registry_url = "https://registry.npmjs.org"
    
    def get_manifest_files(self) -> List[str]:
        """獲取 NPM 清單文件列表"""
        return ["package.json"]
    
    async def parse_manifest(self, manifest_path: Path) -> List[Dependency]:
        """
        解析 package.json 文件
        
        Args:
            manifest_path: package.json 文件路徑
            
        Returns:
            依賴項列表
        """
        dependencies = []
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # 解析生產依賴
            if 'dependencies' in package_data:
                for name, version in package_data['dependencies'].items():
                    dep = self._create_dependency(name, version, DependencyType.DIRECT)
                    dependencies.append(dep)
            
            # 解析開發依賴
            if 'devDependencies' in package_data:
                for name, version in package_data['devDependencies'].items():
                    dep = self._create_dependency(name, version, DependencyType.DEV)
                    dependencies.append(dep)
            
            # 解析對等依賴
            if 'peerDependencies' in package_data:
                for name, version in package_data['peerDependencies'].items():
                    dep = self._create_dependency(name, version, DependencyType.PEER)
                    dependencies.append(dep)
            
            # 解析可選依賴
            if 'optionalDependencies' in package_data:
                for name, version in package_data['optionalDependencies'].items():
                    dep = self._create_dependency(name, version, DependencyType.OPTIONAL)
                    dependencies.append(dep)
            
            logger.info(f"從 {manifest_path} 解析出 {len(dependencies)} 個依賴項")
            
        except json.JSONDecodeError as e:
            logger.error(f"解析 package.json 失敗: {e}")
        except FileNotFoundError:
            logger.error(f"文件不存在: {manifest_path}")
        
        return dependencies
    
    def _create_dependency(
        self, 
        name: str, 
        version_spec: str, 
        dep_type: DependencyType
    ) -> Dependency:
        """
        創建依賴項對象
        
        Args:
            name: 套件名稱
            version_spec: 版本規範 (例如 ^1.0.0, ~2.1.0, 1.0.0)
            dep_type: 依賴類型
            
        Returns:
            依賴項對象
        """
        # 清理版本規範，獲取實際版本號
        version = self._clean_version(version_spec)
        
        return Dependency(
            name=name,
            current_version=version,
            ecosystem=Ecosystem.NPM,
            dep_type=dep_type
        )
    
    def _clean_version(self, version_spec: str) -> str:
        """
        清理版本規範
        
        移除版本前綴如 ^, ~, >=, <=, >, <
        
        Args:
            version_spec: 版本規範字符串
            
        Returns:
            清理後的版本號
        """
        # 移除常見的版本前綴
        prefixes = ['^', '~', '>=', '<=', '>', '<', '=']
        cleaned = version_spec.strip()
        
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        
        # 處理範圍版本 (例如 1.0.0 - 2.0.0)
        if ' - ' in cleaned:
            cleaned = cleaned.split(' - ')[0]
        
        # 處理 || 語法
        if ' || ' in cleaned:
            cleaned = cleaned.split(' || ')[0]
        
        return cleaned.strip()
    
    async def get_latest_version(self, package_name: str) -> Optional[str]:
        """
        從 NPM Registry 獲取套件最新版本
        
        Args:
            package_name: 套件名稱
            
        Returns:
            最新版本號
        """
        # 注意：實際實現需要 HTTP 請求
        # 這裡提供基礎框架，完整實現需要 aiohttp 或類似庫
        logger.debug(f"獲取 {package_name} 最新版本 (需要網路請求實現)")
        
        # 返回 None 表示需要實際 HTTP 實現
        # 實際使用時會發送請求到:
        # f"{self._registry_url}/{package_name}/latest"
        return None
    
    async def parse_lock_file(self, lock_path: Path) -> List[Dependency]:
        """
        解析 package-lock.json 獲取完整依賴樹
        
        Args:
            lock_path: package-lock.json 文件路徑
            
        Returns:
            包含傳遞依賴的完整依賴列表
        """
        dependencies = []
        
        try:
            with open(lock_path, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            
            # 處理 npm v7+ 的 packages 格式
            if 'packages' in lock_data:
                for pkg_path, pkg_info in lock_data['packages'].items():
                    if not pkg_path:  # 跳過根專案
                        continue
                    
                    # 從路徑提取套件名稱
                    name = pkg_path.replace('node_modules/', '').split('/')[-1]
                    version = pkg_info.get('version', '')
                    
                    if name and version:
                        dep = Dependency(
                            name=name,
                            current_version=version,
                            ecosystem=Ecosystem.NPM,
                            dep_type=DependencyType.TRANSITIVE
                        )
                        dependencies.append(dep)
            
            # 處理舊版本的 dependencies 格式
            elif 'dependencies' in lock_data:
                self._parse_nested_dependencies(
                    lock_data['dependencies'], 
                    dependencies
                )
            
            logger.info(f"從 lock 文件解析出 {len(dependencies)} 個依賴項")
            
        except json.JSONDecodeError as e:
            logger.error(f"解析 package-lock.json 失敗: {e}")
        except FileNotFoundError:
            logger.error(f"文件不存在: {lock_path}")
        
        return dependencies
    
    def _parse_nested_dependencies(
        self, 
        deps_dict: dict, 
        result: List[Dependency],
        depth: int = 0
    ) -> None:
        """
        遞歸解析嵌套的依賴結構
        
        Args:
            deps_dict: 依賴字典
            result: 結果列表
            depth: 當前深度
        """
        for name, info in deps_dict.items():
            version = info.get('version', '')
            
            dep = Dependency(
                name=name,
                current_version=version,
                ecosystem=Ecosystem.NPM,
                dep_type=DependencyType.DIRECT if depth == 0 else DependencyType.TRANSITIVE
            )
            result.append(dep)
            
            # 遞歸處理子依賴
            if 'dependencies' in info:
                self._parse_nested_dependencies(
                    info['dependencies'], 
                    result, 
                    depth + 1
                )
