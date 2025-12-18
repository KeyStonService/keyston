"""
Go 分析器 - Go Analyzer
Go modules 生態系統的依賴分析器
"""

import logging
import re
from pathlib import Path

from ..models.dependency import Dependency, DependencyType, Ecosystem
from .base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class GoAnalyzer(BaseAnalyzer):
    """
    Go 模組依賴分析器
    
    支援分析 go.mod 和 go.sum 文件
    """

    def __init__(self):
        """初始化 Go 分析器"""
        super().__init__(Ecosystem.GO)
        self._proxy_url = "https://proxy.golang.org"

    def get_manifest_files(self) -> list[str]:
        """獲取 Go 清單文件列表"""
        return ["go.mod"]

    async def parse_manifest(self, manifest_path: Path) -> list[Dependency]:
        """
        解析 go.mod 文件
        
        Args:
            manifest_path: go.mod 文件路徑
            
        Returns:
            依賴項列表
        """
        dependencies = []

        try:
            with open(manifest_path, encoding='utf-8') as f:
                content = f.read()

            # 解析 require 區塊
            dependencies.extend(self._parse_require_block(content))

            # 解析單行 require
            dependencies.extend(self._parse_single_requires(content))

            logger.info(f"從 {manifest_path} 解析出 {len(dependencies)} 個依賴項")

        except FileNotFoundError:
            logger.error(f"文件不存在: {manifest_path}")
        except UnicodeDecodeError as e:
            logger.error(f"編碼錯誤: {e}")

        return dependencies

    def _parse_require_block(self, content: str) -> list[Dependency]:
        """
        解析 require (...) 區塊
        
        Args:
            content: go.mod 文件內容
            
        Returns:
            依賴項列表
        """
        dependencies = []

        # 匹配 require (...) 區塊
        require_pattern = r'require\s*\(\s*([\s\S]*?)\s*\)'
        matches = re.finditer(require_pattern, content)

        for match in matches:
            block_content = match.group(1)

            # 解析區塊中的每一行
            for line in block_content.split('\n'):
                dep = self._parse_require_line(line)
                if dep:
                    dependencies.append(dep)

        return dependencies

    def _parse_single_requires(self, content: str) -> list[Dependency]:
        """
        解析單行 require 語句
        
        例如: require github.com/pkg/errors v0.9.1
        
        Args:
            content: go.mod 文件內容
            
        Returns:
            依賴項列表
        """
        dependencies = []

        # 匹配單行 require (不在區塊內)
        single_pattern = r'^require\s+(\S+)\s+(\S+)'

        for line in content.split('\n'):
            line = line.strip()

            # 跳過區塊開始
            if 'require (' in line:
                continue

            match = re.match(single_pattern, line)
            if match:
                module_path = match.group(1)
                version = match.group(2)

                dep = Dependency(
                    name=module_path,
                    current_version=self._clean_version(version),
                    ecosystem=Ecosystem.GO,
                    dep_type=DependencyType.DIRECT
                )
                dependencies.append(dep)

        return dependencies

    def _parse_require_line(self, line: str) -> Dependency | None:
        """
        解析 require 區塊中的單行
        
        格式: module/path v1.2.3 [// indirect]
        
        Args:
            line: 依賴規範行
            
        Returns:
            依賴項對象
        """
        line = line.strip()

        # 跳過空行和註釋
        if not line or line.startswith('//'):
            return None

        # 移除行內註釋
        is_indirect = '// indirect' in line
        if '//' in line:
            line = line.split('//')[0].strip()

        # 解析模組路徑和版本
        parts = line.split()
        if len(parts) < 2:
            return None

        module_path = parts[0]
        version = parts[1]

        # 判斷依賴類型
        dep_type = DependencyType.TRANSITIVE if is_indirect else DependencyType.DIRECT

        return Dependency(
            name=module_path,
            current_version=self._clean_version(version),
            ecosystem=Ecosystem.GO,
            dep_type=dep_type
        )

    def _clean_version(self, version: str) -> str:
        """
        清理版本號
        
        Go 版本格式: v1.2.3, v0.0.0-timestamp-commit
        
        Args:
            version: 版本字符串
            
        Returns:
            清理後的版本號
        """
        # 移除前導 v
        if version.startswith('v'):
            version = version[1:]

        return version.strip()

    async def get_latest_version(self, package_name: str) -> str | None:
        """
        從 Go Proxy 獲取模組最新版本
        
        Args:
            package_name: 模組路徑
            
        Returns:
            最新版本號
        """
        # 注意：實際實現需要 HTTP 請求
        # 實際使用時會發送請求到:
        # f"{self._proxy_url}/{package_name}/@latest"
        logger.debug(f"獲取 {package_name} 最新版本 (需要網路請求實現)")
        return None

    async def parse_go_sum(self, sum_path: Path) -> list[Dependency]:
        """
        解析 go.sum 文件獲取完整依賴樹
        
        go.sum 包含所有依賴的校驗和，包括傳遞依賴
        
        Args:
            sum_path: go.sum 文件路徑
            
        Returns:
            依賴項列表
        """
        dependencies = []
        seen_modules = set()

        try:
            with open(sum_path, encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 格式: module/path v1.2.3 h1:hash=
                # 或: module/path v1.2.3/go.mod h1:hash=
                parts = line.split()
                if len(parts) < 2:
                    continue

                module_path = parts[0]
                version = parts[1]

                # 跳過 go.mod 校驗行
                if version.endswith('/go.mod'):
                    version = version.replace('/go.mod', '')

                # 去重
                module_key = f"{module_path}@{version}"
                if module_key in seen_modules:
                    continue
                seen_modules.add(module_key)

                dep = Dependency(
                    name=module_path,
                    current_version=self._clean_version(version),
                    ecosystem=Ecosystem.GO,
                    dep_type=DependencyType.TRANSITIVE  # go.sum 中的都視為傳遞依賴
                )
                dependencies.append(dep)

            logger.info(f"從 {sum_path} 解析出 {len(dependencies)} 個依賴項")

        except FileNotFoundError:
            logger.warning(f"go.sum 文件不存在: {sum_path}")

        return dependencies

    def get_module_name(self, mod_path: Path) -> str | None:
        """
        從 go.mod 獲取模組名稱
        
        Args:
            mod_path: go.mod 文件路徑
            
        Returns:
            模組名稱
        """
        try:
            with open(mod_path, encoding='utf-8') as f:
                content = f.read()

            # 匹配 module 聲明
            match = re.search(r'^module\s+(\S+)', content, re.MULTILINE)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"讀取模組名稱失敗: {e}")

        return None

    def get_go_version(self, mod_path: Path) -> str | None:
        """
        從 go.mod 獲取 Go 版本要求
        
        Args:
            mod_path: go.mod 文件路徑
            
        Returns:
            Go 版本
        """
        try:
            with open(mod_path, encoding='utf-8') as f:
                content = f.read()

            # 匹配 go 版本聲明
            match = re.search(r'^go\s+(\S+)', content, re.MULTILINE)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"讀取 Go 版本失敗: {e}")

        return None
