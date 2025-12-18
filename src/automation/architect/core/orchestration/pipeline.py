"""
Analysis Pipeline - 分析管線
協調整個代碼分析和修復流程
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from ..analysis import (
    StaticAnalyzer,
    SecurityScanner,
    PerformanceAnalyzer,
    ArchitectureAnalyzer
)
from ..repair import RuleEngine, ASTTransformer, RepairVerifier


@dataclass
class PipelineResult:
    """管線執行結果"""
    success: bool
    analysis_results: Dict
    repair_results: Optional[Dict] = None
    verification_results: Optional[Dict] = None
    execution_time_ms: float = 0.0
    message: str = ""


class AnalysisPipeline:
    """
    分析管線
    
    協調代碼分析、修復和驗證的完整流程：
    1. 靜態代碼分析
    2. 安全漏洞掃描
    3. 性能分析
    4. 架構分析
    5. 自動修復（可選）
    6. 修復驗證（可選）
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化分析管線
        
        Args:
            config: 管線配置
        """
        self.config = config or {}
        
        # 初始化各個分析器
        self.static_analyzer = StaticAnalyzer(config)
        self.security_scanner = SecurityScanner(config)
        self.performance_analyzer = PerformanceAnalyzer(config)
        self.architecture_analyzer = ArchitectureAnalyzer(config)
        
        # 初始化修復工具
        self.rule_engine = RuleEngine(config)
        self.ast_transformer = ASTTransformer(config)
        self.repair_verifier = RepairVerifier(config)
        
        logger.info('AnalysisPipeline initialized')
    
    async def analyze(
        self,
        code_path: str,
        scenario: str = 'general',
        enable_repair: bool = False,
        enable_verification: bool = False
    ) -> PipelineResult:
        """
        執行完整的分析管線
        
        Args:
            code_path: 代碼路徑
            scenario: 應用場景 (general, drone-systems, autonomous-driving, automation-iteration)
            enable_repair: 是否啟用自動修復
            enable_verification: 是否啟用驗證
            
        Returns:
            PipelineResult: 管線執行結果
        """
        import time
        start_time = time.time()
        
        logger.info(f'Starting analysis pipeline for: {code_path} (scenario: {scenario})')
        
        try:
            # 階段 1: 並行執行各種分析
            analysis_tasks = [
                self._run_static_analysis(code_path),
                self._run_security_scan(code_path),
                self._run_performance_analysis(code_path),
                self._run_architecture_analysis(code_path)
            ]
            
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            results_dict = {
                'static_analysis': analysis_results[0] if not isinstance(analysis_results[0], Exception) else None,
                'security_scan': analysis_results[1] if not isinstance(analysis_results[1], Exception) else None,
                'performance_analysis': analysis_results[2] if not isinstance(analysis_results[2], Exception) else None,
                'architecture_analysis': analysis_results[3] if not isinstance(analysis_results[3], Exception) else None
            }
            
            # 階段 2: 自動修復（如果啟用）
            repair_results = None
            if enable_repair:
                repair_results = await self._run_repair(code_path, results_dict)
            
            # 階段 3: 驗證（如果啟用）
            verification_results = None
            if enable_verification and repair_results:
                verification_results = await self._run_verification(code_path)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = PipelineResult(
                success=True,
                analysis_results=results_dict,
                repair_results=repair_results,
                verification_results=verification_results,
                execution_time_ms=execution_time,
                message='Pipeline completed successfully'
            )
            
            logger.info(f'Pipeline completed in {execution_time:.2f}ms')
            
            return result
        
        except Exception as e:
            logger.error(f'Pipeline execution failed: {e}')
            execution_time = (time.time() - start_time) * 1000
            
            return PipelineResult(
                success=False,
                analysis_results={},
                execution_time_ms=execution_time,
                message=f'Pipeline failed: {str(e)}'
            )
    
    async def _run_static_analysis(self, code_path: str) -> Dict:
        """執行靜態分析"""
        logger.debug('Running static analysis')
        try:
            result = await self.static_analyzer.analyze(code_path)
            summary = self.static_analyzer.get_summary(result)
            return {
                'status': 'completed',
                'summary': summary,
                'issues': result.issues
            }
        except Exception as e:
            logger.error(f'Static analysis failed: {e}')
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _run_security_scan(self, code_path: str) -> Dict:
        """執行安全掃描"""
        logger.debug('Running security scan')
        try:
            issues = await self.security_scanner.scan(code_path)
            report = self.security_scanner.generate_report(issues)
            return {
                'status': 'completed',
                'report': report,
                'issues': [
                    {
                        'type': issue.type,
                        'severity': issue.severity,
                        'message': issue.message,
                        'file': issue.file,
                        'line': issue.line,
                        'cwe_id': issue.cwe_id
                    }
                    for issue in issues
                ]
            }
        except Exception as e:
            logger.error(f'Security scan failed: {e}')
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _run_performance_analysis(self, code_path: str) -> Dict:
        """執行性能分析"""
        logger.debug('Running performance analysis')
        try:
            issues = await self.performance_analyzer.analyze(code_path)
            return {
                'status': 'completed',
                'issues_count': len(issues),
                'issues': [
                    {
                        'type': issue.type,
                        'severity': issue.severity,
                        'message': issue.message,
                        'file': issue.file,
                        'line': issue.line
                    }
                    for issue in issues
                ]
            }
        except Exception as e:
            logger.error(f'Performance analysis failed: {e}')
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _run_architecture_analysis(self, code_path: str) -> Dict:
        """執行架構分析"""
        logger.debug('Running architecture analysis')
        try:
            issues = await self.architecture_analyzer.analyze(code_path)
            return {
                'status': 'completed',
                'issues_count': len(issues)
            }
        except Exception as e:
            logger.error(f'Architecture analysis failed: {e}')
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _run_repair(self, code_path: str, analysis_results: Dict) -> Dict:
        """執行自動修復"""
        logger.debug('Running auto-repair')
        try:
            result = await self.rule_engine.apply_fixes(code_path, auto_only=True)
            return {
                'status': 'completed',
                'rules_applied': result.rules_applied,
                'changes_made': result.changes_made,
                'success': result.success
            }
        except Exception as e:
            logger.error(f'Auto-repair failed: {e}')
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _run_verification(self, code_path: str) -> Dict:
        """執行驗證"""
        logger.debug('Running verification')
        try:
            result = await self.repair_verifier.verify(code_path)
            return {
                'status': 'completed',
                'passed': result.passed,
                'tests_run': result.tests_run,
                'tests_passed': result.tests_passed
            }
        except Exception as e:
            logger.error(f'Verification failed: {e}')
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict:
        """
        獲取管線統計信息
        
        Returns:
            Dict: 統計信息
        """
        return {
            'pipeline_version': '2.0.0',
            'analyzers': {
                'static_analyzer': 'enabled',
                'security_scanner': 'enabled',
                'performance_analyzer': 'enabled',
                'architecture_analyzer': 'enabled'
            },
            'repair_tools': {
                'rule_engine': 'enabled',
                'ast_transformer': 'enabled',
                'repair_verifier': 'enabled'
            }
        }


# 便利函數
async def run_analysis(
    code_path: str,
    scenario: str = 'general',
    config: Optional[Dict] = None
) -> PipelineResult:
    """
    便利函數：運行代碼分析
    
    Args:
        code_path: 代碼路徑
        scenario: 應用場景
        config: 配置
        
    Returns:
        PipelineResult: 分析結果
    """
    pipeline = AnalysisPipeline(config)
    return await pipeline.analyze(code_path, scenario)
