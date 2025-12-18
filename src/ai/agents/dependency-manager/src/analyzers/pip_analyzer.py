"""
pip 分析器 - pip Analyzer
Python/pip 生態系統的依賴分析器
"""

import re
import logging
from typing import List, Optional, Dict
from pathlib import Path

from .base_analyzer import BaseAnalyzer
from ..models.dependency import Dependency, DependencyType, Ecosystem

logger = logging.getLogger(__name__)


class PipAnalyzer(BaseAnalyzer):
    """
    pip 依賴分析器
    
    支援分析 requirements.txt 和 pyproject.toml 文件
    """
    
    def __init__(self):
        """初始化 pip 分析器"""
        super().__init__(Ecosystem.PIP)
        self._pypi_url = "https://pypi.org/pypi"
    
    def get_manifest_files(self) -> List[str]:
        """獲取 pip 清單文件列表"""
        return ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]
    
    async def parse_manifest(self, manifest_path: Path) -> List[Dependency]:
        """
        解析 Python 依賴文件
        
        Args:
            manifest_path: 依賴文件路徑
            
        Returns:
            依賴項列表
        """
        filename = manifest_path.name.lower()
        
        if filename == "requirements.txt":
            return await self._parse_requirements_txt(manifest_path)
        elif filename == "pyproject.toml":
            return await self._parse_pyproject_toml(manifest_path)
        elif filename == "pipfile":
            return await self._parse_pipfile(manifest_path)
        else:
            logger.warning(f"不支援的文件類型: {filename}")
            return []
    
    async def _parse_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """
        解析 requirements.txt 文件
        
        支援格式:
        - package==1.0.0
        - package>=1.0.0
        - package~=1.0.0
        - package[extra]==1.0.0
        - -r other-requirements.txt (引用)
        
        Args:
            file_path: requirements.txt 路徑
            
        Returns:
            依賴項列表
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                # 跳過空行和註釋
                if not line or line.startswith('#'):
                    continue
                
                # 跳過選項行
                if line.startswith('-'):
                    continue
                
                # 解析依賴規範
                dep = self._parse_requirement_line(line)
                if dep:
                    dependencies.append(dep)
            
            logger.info(f"從 {file_path} 解析出 {len(dependencies)} 個依賴項")
            
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
        except UnicodeDecodeError as e:
            logger.error(f"編碼錯誤: {e}")
        
        return dependencies
    
    def _parse_requirement_line(self, line: str) -> Optional[Dependency]:
        """
        解析單行依賴規範
        
        Args:
            line: 依賴規範行
            
        Returns:
            依賴項對象
        """
        # 移除行內註釋
        if '#' in line:
            line = line.split('#')[0].strip()
        
        # 移除環境標記 (例如 ; python_version >= "3.8")
        if ';' in line:
            line = line.split(';')[0].strip()
        
        # 匹配依賴規範
        # 支援格式: package[extras]<operator>version
        pattern = r'^([a-zA-Z0-9_-]+)(?:\[([^\]]+)\])?(?:([<>=!~]+)(.+))?$'
        match = re.match(pattern, line.replace(' ', ''))
        
        if not match:
            logger.debug(f"無法解析依賴規範: {line}")
            return None
        
        name = match.group(1)
        # extras = match.group(2)  # 可選的 extras
        operator = match.group(3)
        version = match.group(4)
        
        # 清理版本號
        if version:
            version = self._clean_version(version)
        else:
            version = "latest"
        
        return Dependency(
            name=name,
            current_version=version,
            ecosystem=Ecosystem.PIP,
            dep_type=DependencyType.DIRECT
        )
    
    async def _parse_pyproject_toml(self, file_path: Path) -> List[Dependency]:
        """
        解析 pyproject.toml 文件
        
        支援 PEP 621 格式和 Poetry 格式
        
        Args:
            file_path: pyproject.toml 路徑
            
        Returns:
            依賴項列表
        """
        dependencies = []
        
        try:
            # 嘗試使用 tomllib (Python 3.11+) 或 tomli
            try:
                import tomllib
                with open(file_path, 'rb') as f:
                    data = tomllib.load(f)
            except ImportError:
                # 回退到手動解析
                data = self._parse_toml_simple(file_path)
            
            # PEP 621 格式 [project.dependencies]
            if 'project' in data and 'dependencies' in data['project']:
                for dep_str in data['project']['dependencies']:
                    dep = self._parse_requirement_line(dep_str)
                    if dep:
                        dependencies.append(dep)
            
            # Poetry 格式 [tool.poetry.dependencies]
            if 'tool' in data and 'poetry' in data['tool']:
                poetry_deps = data['tool']['poetry'].get('dependencies', {})
                for name, version_spec in poetry_deps.items():
                    if name == 'python':
                        continue
                    
                    version = self._extract_poetry_version(version_spec)
                    dep = Dependency(
                        name=name,
                        current_version=version,
                        ecosystem=Ecosystem.PIP,
                        dep_type=DependencyType.DIRECT
                    )
                    dependencies.append(dep)
                
                # Poetry 開發依賴
                dev_deps = data['tool']['poetry'].get('dev-dependencies', {})
                for name, version_spec in dev_deps.items():
                    version = self._extract_poetry_version(version_spec)
                    dep = Dependency(
                        name=name,
                        current_version=version,
                        ecosystem=Ecosystem.PIP,
                        dep_type=DependencyType.DEV
                    )
                    dependencies.append(dep)
            
            logger.info(f"從 {file_path} 解析出 {len(dependencies)} 個依賴項")
            
        except Exception as e:
            logger.error(f"解析 pyproject.toml 失敗: {e}")
        
        return dependencies
    
    def _parse_toml_simple(self, file_path: Path) -> Dict:
        """
        簡單的 TOML 解析器（回退方案）
        
        Args:
            file_path: TOML 文件路徑
            
        Returns:
            解析後的字典
        """
        # 這是一個簡化實現，實際使用時建議安裝 tomli
        logger.warning("使用簡化 TOML 解析器，建議安裝 tomli 套件")
        return {}
    
    def _extract_poetry_version(self, version_spec) -> str:
        """
        從 Poetry 版本規範提取版本號
        
        Poetry 支援多種格式:
        - "^1.0.0"
        - "~1.0.0"
        - {version = "^1.0.0", optional = true}
        - {git = "...", branch = "main"}
        
        Args:
            version_spec: 版本規範
            
        Returns:
            版本號字符串
        """
        if isinstance(version_spec, str):
            return self._clean_version(version_spec)
        elif isinstance(version_spec, dict):
            if 'version' in version_spec:
                return self._clean_version(version_spec['version'])
            elif 'git' in version_spec:
                return "git"
            elif 'path' in version_spec:
                return "local"
        
        return "unknown"
    
    async def _parse_pipfile(self, file_path: Path) -> List[Dependency]:
        """
        解析 Pipfile 文件
        
        Args:
            file_path: Pipfile 路徑
            
        Returns:
            依賴項列表
        """
        # Pipfile 使用 TOML 格式
        dependencies = []
        
        try:
            try:
                import tomllib
                with open(file_path, 'rb') as f:
                    data = tomllib.load(f)
            except ImportError:
                data = self._parse_toml_simple(file_path)
            
            # [packages] 區段
            for name, version_spec in data.get('packages', {}).items():
                version = self._extract_pipfile_version(version_spec)
                dep = Dependency(
                    name=name,
                    current_version=version,
                    ecosystem=Ecosystem.PIP,
                    dep_type=DependencyType.DIRECT
                )
                dependencies.append(dep)
            
            # [dev-packages] 區段
            for name, version_spec in data.get('dev-packages', {}).items():
                version = self._extract_pipfile_version(version_spec)
                dep = Dependency(
                    name=name,
                    current_version=version,
                    ecosystem=Ecosystem.PIP,
                    dep_type=DependencyType.DEV
                )
                dependencies.append(dep)
            
            logger.info(f"從 {file_path} 解析出 {len(dependencies)} 個依賴項")
            
        except Exception as e:
            logger.error(f"解析 Pipfile 失敗: {e}")
        
        return dependencies
    
    def _extract_pipfile_version(self, version_spec) -> str:
        """
        從 Pipfile 版本規範提取版本號
        
        Args:
            version_spec: 版本規範
            
        Returns:
            版本號字符串
        """
        if version_spec == "*":
            return "latest"
        elif isinstance(version_spec, str):
            return self._clean_version(version_spec)
        elif isinstance(version_spec, dict):
            if 'version' in version_spec:
                return self._clean_version(version_spec['version'])
            elif 'git' in version_spec:
                return "git"
        
        return "unknown"
    
    def _clean_version(self, version_spec: str) -> str:
        """
        清理版本規範
        
        Args:
            version_spec: 版本規範字符串
            
        Returns:
            清理後的版本號
        """
        # 移除常見的版本前綴
        prefixes = ['^', '~', '>=', '<=', '>', '<', '==', '!=', '~=']
        cleaned = version_spec.strip()
        
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break
        
        # 移除空格
        cleaned = cleaned.strip()
        
        # 處理版本範圍 (例如 >=1.0,<2.0)
        if ',' in cleaned:
            cleaned = cleaned.split(',')[0]
        
        return cleaned
    
    async def get_latest_version(self, package_name: str) -> Optional[str]:
        """
        從 PyPI 獲取套件最新版本
        
        Args:
            package_name: 套件名稱
            
        Returns:
            最新版本號
        """
        # 注意：實際實現需要 HTTP 請求
        # 實際使用時會發送請求到:
        # f"{self._pypi_url}/{package_name}/json"
        logger.debug(f"獲取 {package_name} 最新版本 (需要網路請求實現)")
        return None
