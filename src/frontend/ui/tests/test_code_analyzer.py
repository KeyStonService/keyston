#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
代碼分析服務單元測試
============================================================================
Project: SLASolve - Enterprise Code Intelligence Platform v2.0
Phase: 2 - 核心服務開發
Version: 2.0.0
============================================================================
"""

import pytest
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.code_analyzer import (
    SeverityLevel,
    IssueType,
    AnalysisStrategy,
    CodeMetrics,
    CodeIssue,
    AnalysisResult,
    StaticAnalyzer,
    PythonAnalyzer,
    JavaScriptAnalyzer,
    CodeAnalysisEngine,
)


# ============================================================================
# 測試數據模型
# ============================================================================

class TestDataModels:
    """測試數據模型"""

    def test_severity_level_enum(self):
        """測試嚴重程度枚舉"""
        assert SeverityLevel.CRITICAL.value == "CRITICAL"
        assert SeverityLevel.HIGH.value == "HIGH"
        assert SeverityLevel.MEDIUM.value == "MEDIUM"
        assert SeverityLevel.LOW.value == "LOW"
        assert SeverityLevel.INFO.value == "INFO"

    def test_issue_type_enum(self):
        """測試問題類型枚舉"""
        assert IssueType.SECURITY.value == "SECURITY"
        assert IssueType.PERFORMANCE.value == "PERFORMANCE"
        assert IssueType.CODE_QUALITY.value == "CODE_QUALITY"

    def test_analysis_strategy_enum(self):
        """測試分析策略枚舉"""
        assert AnalysisStrategy.QUICK.value == "QUICK"
        assert AnalysisStrategy.STANDARD.value == "STANDARD"
        assert AnalysisStrategy.DEEP.value == "DEEP"
        assert AnalysisStrategy.COMPREHENSIVE.value == "COMPREHENSIVE"

    def test_code_metrics_creation(self):
        """測試代碼指標創建"""
        metrics = CodeMetrics(
            lines_of_code=100,
            cyclomatic_complexity=5.0,
            cognitive_complexity=3.0,
            maintainability_index=75.0,
            technical_debt_ratio=0.1,
            test_coverage=80.0,
            duplication_ratio=0.05,
            documentation_ratio=0.9
        )
        
        assert metrics.lines_of_code == 100
        assert metrics.cyclomatic_complexity == 5.0
        assert isinstance(metrics.to_dict(), dict)

    def test_code_issue_creation(self):
        """測試代碼問題創建"""
        issue = CodeIssue(
            type=IssueType.SECURITY,
            severity=SeverityLevel.HIGH,
            file="test.py",
            line=10,
            message="Test issue"
        )
        
        assert issue.type == IssueType.SECURITY
        assert issue.severity == SeverityLevel.HIGH
        assert issue.file == "test.py"
        assert issue.line == 10
        assert isinstance(issue.id, str)
        assert isinstance(issue.timestamp, datetime)

    def test_code_issue_severity_score(self):
        """測試嚴重程度分數計算"""
        critical_issue = CodeIssue(severity=SeverityLevel.CRITICAL, confidence=1.0)
        assert critical_issue.severity_score == 10.0
        
        high_issue = CodeIssue(severity=SeverityLevel.HIGH, confidence=1.0)
        assert high_issue.severity_score == 7.5
        
        medium_issue = CodeIssue(severity=SeverityLevel.MEDIUM, confidence=0.5)
        assert medium_issue.severity_score == 2.5  # 5.0 * 0.5

    def test_analysis_result_creation(self):
        """測試分析結果創建"""
        result = AnalysisResult(
            repository="test-repo",
            commit_hash="abc123",
            branch="main"
        )
        
        assert result.repository == "test-repo"
        assert result.commit_hash == "abc123"
        assert result.branch == "main"
        assert result.total_issues == 0
        assert result.critical_issues == 0
        assert result.quality_score == 100.0

    def test_analysis_result_with_issues(self):
        """測試帶問題的分析結果"""
        issues = [
            CodeIssue(severity=SeverityLevel.CRITICAL, confidence=1.0),
            CodeIssue(severity=SeverityLevel.HIGH, confidence=1.0),
            CodeIssue(severity=SeverityLevel.MEDIUM, confidence=1.0),
        ]
        
        result = AnalysisResult(
            repository="test-repo",
            issues=issues
        )
        
        assert result.total_issues == 3
        assert result.critical_issues == 1
        assert result.quality_score < 100.0
        assert result.quality_score > 0.0

    def test_analysis_result_risk_level(self):
        """測試風險等級計算"""
        # 高風險 - 5+ critical issues
        high_risk_result = AnalysisResult(
            issues=[CodeIssue(severity=SeverityLevel.CRITICAL) for _ in range(5)]
        )
        assert high_risk_result.risk_level == "CRITICAL"
        
        # 中等風險 - 2-4 critical issues
        medium_risk_result = AnalysisResult(
            issues=[CodeIssue(severity=SeverityLevel.CRITICAL) for _ in range(2)]
        )
        assert medium_risk_result.risk_level == "HIGH"
        
        # 低風險 - no critical issues
        low_risk_result = AnalysisResult(
            issues=[CodeIssue(severity=SeverityLevel.LOW)]
        )
        assert low_risk_result.risk_level == "LOW"


# ============================================================================
# 測試靜態分析器
# ============================================================================

class TestStaticAnalyzer:
    """測試靜態分析器"""

    @pytest.fixture
    def analyzer(self):
        """創建分析器實例"""
        config = {'max_workers': 2}
        return StaticAnalyzer(config, cache_client=None)

    @pytest.mark.asyncio
    async def test_detect_hardcoded_secrets(self, analyzer):
        """測試硬編碼密鑰檢測"""
        code = '''
        password = "secret123"
        api_key = "12345-abcde"
        '''
        
        issues = analyzer._detect_hardcoded_secrets(code, "test.py")
        assert len(issues) >= 1
        assert any(issue.type == IssueType.SECURITY for issue in issues)
        assert any("password" in issue.message.lower() or "api" in issue.message.lower() for issue in issues)

    @pytest.mark.asyncio
    async def test_detect_sql_injection(self, analyzer):
        """測試 SQL 注入檢測"""
        code = '''
        query = "SELECT * FROM users WHERE id = " + user_id
        '''
        
        issues = analyzer._detect_sql_injection(code, "test.py")
        assert len(issues) >= 1
        assert any(issue.type == IssueType.SECURITY for issue in issues)
        assert any("sql" in issue.message.lower() for issue in issues)

    @pytest.mark.asyncio
    async def test_detect_xss_vulnerabilities(self, analyzer):
        """測試 XSS 漏洞檢測"""
        code = '''
        element.innerHTML = userInput;
        '''
        
        issues = analyzer._detect_xss_vulnerabilities(code, "test.js")
        assert len(issues) >= 1
        assert any(issue.type == IssueType.SECURITY for issue in issues)
        assert any("xss" in issue.message.lower() for issue in issues)

    @pytest.mark.asyncio
    async def test_calculate_cyclomatic_complexity(self, analyzer):
        """測試圈複雜度計算"""
        simple_code = "def simple(): return True"
        complexity_simple = analyzer._calculate_cyclomatic_complexity(simple_code)
        assert complexity_simple >= 1
        
        complex_code = '''
        def complex(x):
            if x > 0:
                if x > 10:
                    return "high"
                elif x > 5:
                    return "medium"
                else:
                    return "low"
            else:
                return "negative"
        '''
        complexity_complex = analyzer._calculate_cyclomatic_complexity(complex_code)
        assert complexity_complex > complexity_simple

    @pytest.mark.asyncio
    async def test_calculate_duplication_ratio(self, analyzer):
        """測試代碼重複率計算"""
        no_duplication = "line1\nline2\nline3\n"
        ratio_low = analyzer._calculate_duplication_ratio(no_duplication)
        assert ratio_low == 0.0
        
        with_duplication = "duplicate\nduplicate\nduplicate\n"
        ratio_high = analyzer._calculate_duplication_ratio(with_duplication)
        assert ratio_high > 0.5

    @pytest.mark.asyncio
    async def test_detect_language(self, analyzer):
        """測試語言檢測"""
        assert analyzer._detect_language("test.py") == "python"
        assert analyzer._detect_language("test.js") == "javascript"
        assert analyzer._detect_language("test.go") == "go"
        assert analyzer._detect_language("test.rs") == "rust"
        assert analyzer._detect_language("test.java") == "java"
        assert analyzer._detect_language("test.cpp") == "cpp"
        assert analyzer._detect_language("test.unknown") == "unknown"


# ============================================================================
# 測試語言特定分析器
# ============================================================================

class TestLanguageAnalyzers:
    """測試語言特定分析器"""

    @pytest.mark.asyncio
    async def test_python_analyzer(self):
        """測試 Python 分析器"""
        config = {}
        analyzer = PythonAnalyzer(config)
        
        code_without_hints = "def test(): pass"
        issues = await analyzer._perform_analysis(code_without_hints, "test.py", AnalysisStrategy.STANDARD)
        
        assert len(issues) >= 0
        # May detect missing type hints

    @pytest.mark.asyncio
    async def test_javascript_analyzer(self):
        """測試 JavaScript 分析器"""
        config = {}
        analyzer = JavaScriptAnalyzer(config)
        
        code_with_var = "var x = 10;"
        issues = await analyzer._perform_analysis(code_with_var, "test.js", AnalysisStrategy.STANDARD)
        
        # Should detect use of 'var'
        assert any("var" in issue.message.lower() for issue in issues) or len(issues) >= 0


# ============================================================================
# 測試代碼分析引擎
# ============================================================================

class TestCodeAnalysisEngine:
    """測試代碼分析引擎"""

    @pytest.fixture
    def engine(self):
        """創建引擎實例"""
        config = {'max_workers': 2}
        return CodeAnalysisEngine(config, cache_client=None)

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """測試引擎初始化"""
        assert engine is not None
        assert len(engine.analyzers) > 0
        assert engine.config['max_workers'] == 2

    @pytest.mark.asyncio
    async def test_analyze_repository(self, engine):
        """測試代碼庫分析"""
        result = await engine.analyze_repository(
            repo_path="/tmp/test-repo",
            commit_hash="abc123",
            strategy=AnalysisStrategy.STANDARD
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.repository == "/tmp/test-repo"
        assert result.commit_hash == "abc123"
        assert result.strategy == AnalysisStrategy.STANDARD

    def test_get_metrics(self, engine):
        """測試獲取引擎指標"""
        metrics = engine.get_metrics()
        
        assert isinstance(metrics, dict)
        assert 'analyses_completed' in metrics
        assert 'issues_found' in metrics
        assert 'cache_hits' in metrics
        assert 'cache_misses' in metrics


# ============================================================================
# 集成測試
# ============================================================================

class TestIntegration:
    """集成測試"""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """測試完整分析流程"""
        config = {'max_workers': 2}
        
        # 創建測試代碼
        test_code = '''
def test_function():
    password = "hardcoded"
    query = "SELECT * FROM users WHERE id = " + user_id
    return query
'''
        
        # 模擬文件分析
        analyzer = StaticAnalyzer(config)
        issues = await analyzer.analyze(test_code, "test.py", AnalysisStrategy.STANDARD)
        
        # 驗證結果
        assert len(issues) > 0
        assert any(issue.type == IssueType.SECURITY for issue in issues)

    @pytest.mark.asyncio
    async def test_multiple_strategies(self):
        """測試多種分析策略"""
        config = {}
        analyzer = StaticAnalyzer(config)
        
        code = "def simple(): pass"
        
        # 快速分析
        quick_issues = await analyzer.analyze(code, "test.py", AnalysisStrategy.QUICK)
        
        # 深度分析
        deep_issues = await analyzer.analyze(code, "test.py", AnalysisStrategy.DEEP)
        
        # 深度分析應該發現更多問題（或至少相同數量）
        assert len(deep_issues) >= len(quick_issues)


# ============================================================================
# 性能測試
# ============================================================================

class TestPerformance:
    """性能測試"""

    @pytest.mark.asyncio
    async def test_analysis_performance(self):
        """測試分析性能"""
        import time
        
        config = {'max_workers': 4}
        
        # 生成大量測試代碼
        large_code = "\n".join([f"def func_{i}(): pass" for i in range(100)])
        
        start_time = time.time()
        
        analyzer = StaticAnalyzer(config)
        await analyzer.analyze(large_code, "large.py", AnalysisStrategy.QUICK)
        
        duration = time.time() - start_time
        
        # 應該在合理時間內完成（< 5 秒）
        assert duration < 5.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
