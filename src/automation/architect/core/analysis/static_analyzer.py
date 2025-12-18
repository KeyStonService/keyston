"""
Static Analyzer - 靜態代碼分析器
提供多維度靜態代碼分析能力
"""

import ast
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """分析結果數據類"""
    file_path: str
    issues: List[Dict]
    metrics: Dict
    severity_counts: Dict[str, int]
    analysis_time_ms: float


@dataclass
class CodeMetrics:
    """代碼指標數據類"""
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    comment_ratio: float
    function_count: int
    class_count: int


class StaticAnalyzer:
    """
    靜態代碼分析器
    
    提供多維度代碼質量分析：
    - 代碼複雜度分析
    - 代碼風格檢查
    - 代碼重複檢測
    - 可維護性評估
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化靜態分析器
        
        Args:
            config: 分析配置字典
        """
        self.config = config or {}
        self.supported_extensions = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.cpp'}
        logger.info('StaticAnalyzer initialized')
    
    async def analyze(
        self,
        code_path: str,
        language: Optional[str] = None,
        rules: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        執行靜態代碼分析
        
        Args:
            code_path: 代碼文件或目錄路徑
            language: 編程語言 (可選)
            rules: 分析規則列表 (可選)
            
        Returns:
            AnalysisResult: 分析結果
        """
        import time
        start_time = time.time()
        
        logger.info(f'Starting static analysis for: {code_path}')
        
        path = Path(code_path)
        issues = []
        all_metrics = {}
        
        if path.is_file():
            file_issues, file_metrics = await self._analyze_file(path, language)
            issues.extend(file_issues)
            all_metrics[str(path)] = file_metrics
        elif path.is_dir():
            for file_path in self._get_code_files(path):
                file_issues, file_metrics = await self._analyze_file(file_path, language)
                issues.extend(file_issues)
                all_metrics[str(file_path)] = file_metrics
        else:
            logger.error(f'Invalid path: {code_path}')
            raise ValueError(f'Invalid path: {code_path}')
        
        # 統計嚴重程度
        severity_counts = self._count_severities(issues)
        
        analysis_time = (time.time() - start_time) * 1000  # 毫秒
        
        result = AnalysisResult(
            file_path=code_path,
            issues=issues,
            metrics=all_metrics,
            severity_counts=severity_counts,
            analysis_time_ms=analysis_time
        )
        
        logger.info(f'Analysis completed in {analysis_time:.2f}ms')
        logger.info(f'Found {len(issues)} issues: {severity_counts}')
        
        return result
    
    async def _analyze_file(
        self,
        file_path: Path,
        language: Optional[str] = None
    ) -> Tuple[List[Dict], CodeMetrics]:
        """
        分析單個文件
        
        Args:
            file_path: 文件路徑
            language: 編程語言
            
        Returns:
            Tuple[List[Dict], CodeMetrics]: 問題列表和代碼指標
        """
        issues = []
        
        # 檢測語言
        if language is None:
            language = self._detect_language(file_path)
        
        logger.debug(f'Analyzing file: {file_path} (language: {language})')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 計算代碼指標
            metrics = self._calculate_metrics(code, language)
            
            # 執行各種檢查
            if language == 'python':
                issues.extend(self._check_python_code(code, file_path))
            elif language in ['javascript', 'typescript']:
                issues.extend(self._check_javascript_code(code, file_path))
            
            # 通用檢查
            issues.extend(self._check_complexity(code, metrics, file_path))
            issues.extend(self._check_style(code, language, file_path))
            
        except Exception as e:
            logger.error(f'Error analyzing file {file_path}: {e}')
            issues.append({
                'type': 'analysis-error',
                'severity': 'error',
                'message': f'Failed to analyze file: {str(e)}',
                'file': str(file_path),
                'line': 0
            })
            metrics = CodeMetrics(0, 0, 0.0, 0.0, 0, 0)
        
        return issues, metrics
    
    def _calculate_metrics(self, code: str, language: str) -> CodeMetrics:
        """
        計算代碼指標
        
        Args:
            code: 源代碼
            language: 編程語言
            
        Returns:
            CodeMetrics: 代碼指標
        """
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # 簡化的循環複雜度計算
        complexity = self._calculate_cyclomatic_complexity(code, language)
        
        # 註釋比例
        comment_lines = len([line for line in lines if line.strip().startswith('#') or line.strip().startswith('//')])
        comment_ratio = comment_lines / max(loc, 1)
        
        # 函數和類計數 (Python)
        function_count = 0
        class_count = 0
        if language == 'python':
            try:
                tree = ast.parse(code)
                function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
                class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            except SyntaxError:
                pass
        
        # 可維護性指數 (簡化版)
        maintainability = max(0, 100 - complexity * 2 - (100 - comment_ratio * 100) * 0.5)
        
        return CodeMetrics(
            lines_of_code=loc,
            cyclomatic_complexity=complexity,
            maintainability_index=maintainability,
            comment_ratio=comment_ratio,
            function_count=function_count,
            class_count=class_count
        )
    
    def _calculate_cyclomatic_complexity(self, code: str, language: str) -> int:
        """
        計算循環複雜度
        
        Args:
            code: 源代碼
            language: 編程語言
            
        Returns:
            int: 循環複雜度
        """
        # 簡化的複雜度計算：計算決策點
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', '&&', '||', '?']
        complexity = 1  # 基礎複雜度
        
        for keyword in decision_keywords:
            complexity += code.count(keyword)
        
        return complexity
    
    def _check_python_code(self, code: str, file_path: Path) -> List[Dict]:
        """
        檢查 Python 代碼
        
        Args:
            code: 源代碼
            file_path: 文件路徑
            
        Returns:
            List[Dict]: 問題列表
        """
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # 檢查長函數
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 50:
                        issues.append({
                            'type': 'long-function',
                            'severity': 'warning',
                            'message': f'Function "{node.name}" is too long ({func_lines} lines)',
                            'file': str(file_path),
                            'line': node.lineno
                        })
                
                # 檢查過多參數
                if isinstance(node, ast.FunctionDef):
                    param_count = len(node.args.args)
                    if param_count > 5:
                        issues.append({
                            'type': 'too-many-parameters',
                            'severity': 'info',
                            'message': f'Function "{node.name}" has too many parameters ({param_count})',
                            'file': str(file_path),
                            'line': node.lineno
                        })
        
        except SyntaxError as e:
            issues.append({
                'type': 'syntax-error',
                'severity': 'critical',
                'message': f'Syntax error: {str(e)}',
                'file': str(file_path),
                'line': e.lineno or 0
            })
        
        return issues
    
    def _check_javascript_code(self, code: str, file_path: Path) -> List[Dict]:
        """
        檢查 JavaScript/TypeScript 代碼
        
        Args:
            code: 源代碼
            file_path: 文件路徑
            
        Returns:
            List[Dict]: 問題列表
        """
        issues = []
        
        # 簡單檢查
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # 檢查 console.log
            if 'console.log' in line:
                issues.append({
                    'type': 'console-log',
                    'severity': 'info',
                    'message': 'Remove console.log before production',
                    'file': str(file_path),
                    'line': i
                })
            
            # 檢查 var 使用
            if line.strip().startswith('var '):
                issues.append({
                    'type': 'use-const-let',
                    'severity': 'warning',
                    'message': 'Use "const" or "let" instead of "var"',
                    'file': str(file_path),
                    'line': i
                })
        
        return issues
    
    def _check_complexity(
        self,
        code: str,
        metrics: CodeMetrics,
        file_path: Path
    ) -> List[Dict]:
        """
        檢查代碼複雜度
        
        Args:
            code: 源代碼
            metrics: 代碼指標
            file_path: 文件路徑
            
        Returns:
            List[Dict]: 問題列表
        """
        issues = []
        
        # 檢查循環複雜度
        threshold = self.config.get('complexity_threshold', 10)
        if metrics.cyclomatic_complexity > threshold:
            issues.append({
                'type': 'high-complexity',
                'severity': 'warning',
                'message': f'High cyclomatic complexity: {metrics.cyclomatic_complexity} (threshold: {threshold})',
                'file': str(file_path),
                'line': 0
            })
        
        # 檢查可維護性
        if metrics.maintainability_index < 60:
            issues.append({
                'type': 'low-maintainability',
                'severity': 'warning',
                'message': f'Low maintainability index: {metrics.maintainability_index:.2f}',
                'file': str(file_path),
                'line': 0
            })
        
        return issues
    
    def _check_style(
        self,
        code: str,
        language: str,
        file_path: Path
    ) -> List[Dict]:
        """
        檢查代碼風格
        
        Args:
            code: 源代碼
            language: 編程語言
            file_path: 文件路徑
            
        Returns:
            List[Dict]: 問題列表
        """
        issues = []
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 檢查行長度
            if len(line) > 100:
                issues.append({
                    'type': 'line-too-long',
                    'severity': 'info',
                    'message': f'Line too long: {len(line)} characters (max: 100)',
                    'file': str(file_path),
                    'line': i
                })
            
            # 檢查尾部空格
            if line.rstrip() != line:
                issues.append({
                    'type': 'trailing-whitespace',
                    'severity': 'info',
                    'message': 'Trailing whitespace',
                    'file': str(file_path),
                    'line': i
                })
        
        return issues
    
    def _detect_language(self, file_path: Path) -> str:
        """
        檢測文件編程語言
        
        Args:
            file_path: 文件路徑
            
        Returns:
            str: 編程語言
        """
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp'
        }
        return language_map.get(ext, 'unknown')
    
    def _get_code_files(self, directory: Path) -> List[Path]:
        """
        獲取目錄中的所有代碼文件
        
        Args:
            directory: 目錄路徑
            
        Returns:
            List[Path]: 代碼文件路徑列表
        """
        code_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.supported_extensions:
                    code_files.append(file_path)
        return code_files
    
    def _count_severities(self, issues: List[Dict]) -> Dict[str, int]:
        """
        統計問題嚴重程度
        
        Args:
            issues: 問題列表
            
        Returns:
            Dict[str, int]: 嚴重程度計數
        """
        counts = {'critical': 0, 'high': 0, 'warning': 0, 'info': 0, 'error': 0}
        for issue in issues:
            severity = issue.get('severity', 'info')
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def get_summary(self, result: AnalysisResult) -> Dict:
        """
        獲取分析摘要
        
        Args:
            result: 分析結果
            
        Returns:
            Dict: 分析摘要
        """
        total_issues = len(result.issues)
        
        return {
            'file_path': result.file_path,
            'total_issues': total_issues,
            'severity_counts': result.severity_counts,
            'analysis_time_ms': result.analysis_time_ms,
            'metrics': result.metrics
        }


# 便利函數
async def analyze_code(
    code_path: str,
    config: Optional[Dict] = None
) -> AnalysisResult:
    """
    便利函數：執行代碼分析
    
    Args:
        code_path: 代碼路徑
        config: 配置
        
    Returns:
        AnalysisResult: 分析結果
    """
    analyzer = StaticAnalyzer(config)
    return await analyzer.analyze(code_path)
