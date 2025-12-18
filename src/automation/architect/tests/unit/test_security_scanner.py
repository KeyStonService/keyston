"""
Unit tests for SecurityScanner
安全掃描器單元測試
"""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.analysis.security_scanner import SecurityScanner, SecurityIssue


@pytest.fixture
def scanner():
    """創建掃描器實例"""
    return SecurityScanner()


@pytest.fixture
def vulnerable_python_file():
    """創建包含安全問題的 Python 文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
# 硬編碼密鑰
password = "secret123"
api_key = "sk-1234567890"
secret = "my-secret-token"

# SQL 注入風險
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    return execute(query)

# XSS 風險
def render_page(user_input):
    document.innerHTML = user_input

# 不安全的加密
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
""")
        return Path(f.name)


@pytest.mark.asyncio
async def test_scanner_initialization(scanner):
    """測試掃描器初始化"""
    assert scanner is not None
    assert len(scanner.secret_patterns) > 0
    assert len(scanner.sql_injection_patterns) > 0
    assert len(scanner.xss_patterns) > 0
    assert len(scanner.crypto_patterns) > 0


@pytest.mark.asyncio
async def test_scan_file(scanner, vulnerable_python_file):
    """測試掃描文件"""
    issues = await scanner.scan(str(vulnerable_python_file))
    
    assert len(issues) > 0
    assert all(isinstance(issue, SecurityIssue) for issue in issues)


@pytest.mark.asyncio
async def test_detect_hardcoded_secrets(scanner, vulnerable_python_file):
    """測試檢測硬編碼密鑰"""
    issues = await scanner.scan(str(vulnerable_python_file))
    
    # 應該檢測到硬編碼密鑰
    secret_issues = [i for i in issues if 'hardcoded' in i.type]
    assert len(secret_issues) > 0
    
    # 檢查嚴重程度
    for issue in secret_issues:
        assert issue.severity == 'critical'
        assert issue.cwe_id == 'CWE-798'


@pytest.mark.asyncio
async def test_detect_sql_injection(scanner, vulnerable_python_file):
    """測試檢測 SQL 注入"""
    issues = await scanner.scan(str(vulnerable_python_file))
    
    # 應該檢測到 SQL 注入風險
    sql_issues = [i for i in issues if i.type == 'sql-injection']
    assert len(sql_issues) > 0
    
    for issue in sql_issues:
        assert issue.severity == 'high'
        assert issue.cwe_id == 'CWE-89'


@pytest.mark.asyncio
async def test_detect_weak_crypto(scanner, vulnerable_python_file):
    """測試檢測不安全的加密"""
    issues = await scanner.scan(str(vulnerable_python_file))
    
    # 應該檢測到弱加密算法
    crypto_issues = [i for i in issues if i.type == 'weak-crypto']
    assert len(crypto_issues) > 0
    
    for issue in crypto_issues:
        assert issue.severity == 'high'
        assert issue.cwe_id == 'CWE-327'


@pytest.mark.asyncio
async def test_severity_filter(scanner, vulnerable_python_file):
    """測試嚴重程度過濾"""
    # 只獲取 critical 問題
    critical_issues = await scanner.scan(
        str(vulnerable_python_file),
        severity_filter=['critical']
    )
    
    assert all(issue.severity == 'critical' for issue in critical_issues)


@pytest.mark.asyncio
async def test_generate_report(scanner, vulnerable_python_file):
    """測試生成報告"""
    issues = await scanner.scan(str(vulnerable_python_file))
    report = scanner.generate_report(issues)
    
    assert report is not None
    assert 'total_issues' in report
    assert 'severity_counts' in report
    assert 'issues_by_type' in report
    assert 'critical_files' in report
    assert 'recommendations' in report


def test_group_by_type(scanner):
    """測試按類型分組"""
    issues = [
        SecurityIssue('hardcoded-password', 'critical', 'msg', 'file.py', 1),
        SecurityIssue('hardcoded-api-key', 'critical', 'msg', 'file.py', 2),
        SecurityIssue('sql-injection', 'high', 'msg', 'file.py', 3),
    ]
    
    type_counts = scanner._group_by_type(issues)
    
    assert type_counts['hardcoded-password'] == 1
    assert type_counts['hardcoded-api-key'] == 1
    assert type_counts['sql-injection'] == 1


def test_get_critical_files(scanner):
    """測試獲取嚴重問題文件"""
    issues = [
        SecurityIssue('issue1', 'critical', 'msg', 'file1.py', 1),
        SecurityIssue('issue2', 'high', 'msg', 'file2.py', 1),
        SecurityIssue('issue3', 'critical', 'msg', 'file1.py', 2),
    ]
    
    critical_files = scanner._get_critical_files(issues)
    
    assert 'file1.py' in critical_files
    assert 'file2.py' not in critical_files


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
