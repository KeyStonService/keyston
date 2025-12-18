"""
Unit tests for StaticAnalyzer
靜態分析器單元測試
"""

import pytest
import tempfile
from pathlib import Path
import sys

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.analysis.static_analyzer import StaticAnalyzer, AnalysisResult


@pytest.fixture
def analyzer():
    """創建分析器實例"""
    return StaticAnalyzer()


@pytest.fixture
def sample_python_file():
    """創建示例 Python 文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def long_function():
    # This is a very long function
    x = 1
    y = 2
    z = 3
    # ... many more lines
    for i in range(100):
        for j in range(100):
            for k in range(100):
                pass
    return x + y + z

def function_with_many_params(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g

password = "secret123"
""")
        return Path(f.name)


@pytest.mark.asyncio
async def test_analyzer_initialization(analyzer):
    """測試分析器初始化"""
    assert analyzer is not None
    assert analyzer.config == {}
    assert len(analyzer.supported_extensions) > 0


@pytest.mark.asyncio
async def test_analyze_python_file(analyzer, sample_python_file):
    """測試分析 Python 文件"""
    result = await analyzer.analyze(str(sample_python_file))
    
    assert isinstance(result, AnalysisResult)
    assert result.file_path == str(sample_python_file)
    assert len(result.issues) > 0
    assert result.analysis_time_ms > 0


@pytest.mark.asyncio
async def test_detect_long_function(analyzer, sample_python_file):
    """測試檢測長函數"""
    result = await analyzer.analyze(str(sample_python_file))
    
    # 應該檢測到長函數問題
    long_func_issues = [i for i in result.issues if i['type'] == 'long-function']
    assert len(long_func_issues) > 0


@pytest.mark.asyncio
async def test_detect_many_parameters(analyzer, sample_python_file):
    """測試檢測過多參數"""
    result = await analyzer.analyze(str(sample_python_file))
    
    # 應該檢測到參數過多問題
    param_issues = [i for i in result.issues if i['type'] == 'too-many-parameters']
    assert len(param_issues) > 0


@pytest.mark.asyncio
async def test_calculate_metrics(analyzer, sample_python_file):
    """測試代碼指標計算"""
    result = await analyzer.analyze(str(sample_python_file))
    
    assert result.metrics is not None
    assert len(result.metrics) > 0
    
    # 檢查指標內容
    for file_path, metrics in result.metrics.items():
        assert metrics.lines_of_code > 0
        assert metrics.cyclomatic_complexity > 0


@pytest.mark.asyncio
async def test_severity_counts(analyzer, sample_python_file):
    """測試嚴重程度統計"""
    result = await analyzer.analyze(str(sample_python_file))
    
    assert result.severity_counts is not None
    assert isinstance(result.severity_counts, dict)
    assert 'critical' in result.severity_counts
    assert 'warning' in result.severity_counts
    assert 'info' in result.severity_counts


@pytest.mark.asyncio
async def test_get_summary(analyzer, sample_python_file):
    """測試獲取分析摘要"""
    result = await analyzer.analyze(str(sample_python_file))
    summary = analyzer.get_summary(result)
    
    assert summary is not None
    assert 'file_path' in summary
    assert 'total_issues' in summary
    assert 'severity_counts' in summary
    assert 'analysis_time_ms' in summary


@pytest.mark.asyncio
async def test_detect_language():
    """測試語言檢測"""
    analyzer = StaticAnalyzer()
    
    assert analyzer._detect_language(Path('test.py')) == 'python'
    assert analyzer._detect_language(Path('test.js')) == 'javascript'
    assert analyzer._detect_language(Path('test.ts')) == 'typescript'
    assert analyzer._detect_language(Path('test.go')) == 'go'
    assert analyzer._detect_language(Path('test.rs')) == 'rust'


def test_count_severities():
    """測試嚴重程度統計"""
    analyzer = StaticAnalyzer()
    
    issues = [
        {'severity': 'critical'},
        {'severity': 'critical'},
        {'severity': 'warning'},
        {'severity': 'info'},
        {'severity': 'info'},
        {'severity': 'info'},
    ]
    
    counts = analyzer._count_severities(issues)
    
    assert counts['critical'] == 2
    assert counts['warning'] == 1
    assert counts['info'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
