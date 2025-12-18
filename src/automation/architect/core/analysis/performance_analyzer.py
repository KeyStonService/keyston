"""
Performance Analyzer - 性能分析器
分析代碼性能問題和優化機會
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class PerformanceIssue:
    """性能問題數據類"""
    type: str
    severity: str
    message: str
    file: str
    line: int
    suggestion: Optional[str] = None


class PerformanceAnalyzer:
    """
    性能分析器
    
    分析代碼性能問題：
    - 時間複雜度
    - 空間複雜度
    - 算法效率
    - 潛在瓶頸
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化性能分析器"""
        self.config = config or {}
        logger.info('PerformanceAnalyzer initialized')
    
    async def analyze(
        self,
        code_path: str,
        profiling: bool = False
    ) -> List[PerformanceIssue]:
        """
        執行性能分析
        
        Args:
            code_path: 代碼路徑
            profiling: 是否執行性能分析
            
        Returns:
            List[PerformanceIssue]: 性能問題列表
        """
        logger.info(f'Starting performance analysis for: {code_path}')
        
        issues = []
        path = Path(code_path)
        
        if path.is_file():
            issues.extend(await self._analyze_file(path))
        elif path.is_dir():
            for file_path in self._get_code_files(path):
                issues.extend(await self._analyze_file(file_path))
        
        logger.info(f'Performance analysis completed. Found {len(issues)} issues')
        return issues
    
    async def _analyze_file(self, file_path: Path) -> List[PerformanceIssue]:
        """分析單個文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # 檢查常見性能問題
                if 'for' in line and 'for' in lines[line_num] if line_num < len(lines) else False:
                    issues.append(PerformanceIssue(
                        type='nested-loops',
                        severity='warning',
                        message='Nested loops detected - potential O(n²) complexity',
                        file=str(file_path),
                        line=line_num,
                        suggestion='Consider using more efficient algorithms'
                    ))
        
        except Exception as e:
            logger.error(f'Error analyzing file {file_path}: {e}')
        
        return issues
    
    def _get_code_files(self, directory: Path) -> List[Path]:
        """獲取代碼文件"""
        extensions = {'.py', '.js', '.ts', '.go', '.rs', '.java'}
        files = []
        import os
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.suffix in extensions:
                    files.append(file_path)
        return files
