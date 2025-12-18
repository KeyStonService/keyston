"""
Security Scanner - 安全漏洞掃描器
檢測常見安全漏洞和風險
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """安全問題數據類"""
    type: str
    severity: str  # critical, high, medium, low
    message: str
    file: str
    line: int
    cwe_id: Optional[str] = None
    recommendation: Optional[str] = None


class SecurityScanner:
    """
    安全漏洞掃描器
    
    檢測常見安全問題：
    - 硬編碼密鑰和敏感信息
    - SQL 注入風險
    - XSS 漏洞
    - 不安全的加密算法
    - 路徑遍歷漏洞
    - CSRF 風險
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化安全掃描器
        
        Args:
            config: 掃描配置
        """
        self.config = config or {}
        self._init_patterns()
        logger.info('SecurityScanner initialized')
    
    def _init_patterns(self):
        """初始化安全檢測模式"""
        # 硬編碼密鑰模式
        self.secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'hardcoded-password', 'Hardcoded password detected'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'hardcoded-api-key', 'Hardcoded API key detected'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'hardcoded-secret', 'Hardcoded secret detected'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'hardcoded-token', 'Hardcoded token detected'),
            (r'private[_-]?key\s*=\s*["\'][^"\']+["\']', 'hardcoded-private-key', 'Hardcoded private key detected'),
        ]
        
        # SQL 注入模式
        self.sql_injection_patterns = [
            (r'execute\s*\(\s*["\'].*?\+.*?["\']', 'sql-injection', 'Potential SQL injection vulnerability'),
            (r'query\s*\(\s*["\'].*?%s.*?["\']', 'sql-injection', 'Potential SQL injection vulnerability'),
            (r'raw\s*\(\s*["\'].*?\+.*?["\']', 'sql-injection', 'Potential SQL injection vulnerability'),
        ]
        
        # XSS 模式
        self.xss_patterns = [
            (r'innerHTML\s*=\s*', 'xss', 'Potential XSS vulnerability via innerHTML'),
            (r'document\.write\s*\(', 'xss', 'Potential XSS vulnerability via document.write'),
            (r'eval\s*\(', 'eval-usage', 'Use of eval() can lead to code injection'),
        ]
        
        # 不安全的加密
        self.crypto_patterns = [
            (r'MD5\s*\(', 'weak-crypto', 'MD5 is cryptographically broken'),
            (r'SHA1\s*\(', 'weak-crypto', 'SHA1 is cryptographically weak'),
            (r'DES\s*\(', 'weak-crypto', 'DES is insecure'),
        ]
        
        # 路徑遍歷
        self.path_traversal_patterns = [
            (r'open\s*\([^)]*\.\./[^)]*\)', 'path-traversal', 'Potential path traversal vulnerability'),
            (r'file\s*\([^)]*\.\./[^)]*\)', 'path-traversal', 'Potential path traversal vulnerability'),
        ]
    
    async def scan(
        self,
        code_path: str,
        severity_filter: Optional[List[str]] = None
    ) -> List[SecurityIssue]:
        """
        執行安全掃描
        
        Args:
            code_path: 代碼文件或目錄路徑
            severity_filter: 嚴重程度過濾 (可選)
            
        Returns:
            List[SecurityIssue]: 安全問題列表
        """
        logger.info(f'Starting security scan for: {code_path}')
        
        path = Path(code_path)
        issues = []
        
        if path.is_file():
            issues.extend(await self._scan_file(path))
        elif path.is_dir():
            for file_path in self._get_scannable_files(path):
                issues.extend(await self._scan_file(file_path))
        
        # 過濾嚴重程度
        if severity_filter:
            issues = [i for i in issues if i.severity in severity_filter]
        
        logger.info(f'Security scan completed. Found {len(issues)} issues')
        
        return issues
    
    async def _scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """
        掃描單個文件
        
        Args:
            file_path: 文件路徑
            
        Returns:
            List[SecurityIssue]: 安全問題列表
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # 檢查硬編碼密鑰
                issues.extend(self._check_secrets(line, file_path, line_num))
                
                # 檢查 SQL 注入
                issues.extend(self._check_sql_injection(line, file_path, line_num))
                
                # 檢查 XSS
                issues.extend(self._check_xss(line, file_path, line_num))
                
                # 檢查不安全的加密
                issues.extend(self._check_crypto(line, file_path, line_num))
                
                # 檢查路徑遍歷
                issues.extend(self._check_path_traversal(line, file_path, line_num))
        
        except Exception as e:
            logger.error(f'Error scanning file {file_path}: {e}')
        
        return issues
    
    def _check_secrets(
        self,
        line: str,
        file_path: Path,
        line_num: int
    ) -> List[SecurityIssue]:
        """檢查硬編碼密鑰"""
        issues = []
        
        for pattern, issue_type, message in self.secret_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(SecurityIssue(
                    type=issue_type,
                    severity='critical',
                    message=message,
                    file=str(file_path),
                    line=line_num,
                    cwe_id='CWE-798',
                    recommendation='Use environment variables or secure vaults for sensitive data'
                ))
        
        return issues
    
    def _check_sql_injection(
        self,
        line: str,
        file_path: Path,
        line_num: int
    ) -> List[SecurityIssue]:
        """檢查 SQL 注入風險"""
        issues = []
        
        for pattern, issue_type, message in self.sql_injection_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(SecurityIssue(
                    type=issue_type,
                    severity='high',
                    message=message,
                    file=str(file_path),
                    line=line_num,
                    cwe_id='CWE-89',
                    recommendation='Use parameterized queries or ORM to prevent SQL injection'
                ))
        
        return issues
    
    def _check_xss(
        self,
        line: str,
        file_path: Path,
        line_num: int
    ) -> List[SecurityIssue]:
        """檢查 XSS 風險"""
        issues = []
        
        for pattern, issue_type, message in self.xss_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                severity = 'critical' if 'eval' in issue_type else 'high'
                cwe = 'CWE-95' if 'eval' in issue_type else 'CWE-79'
                
                issues.append(SecurityIssue(
                    type=issue_type,
                    severity=severity,
                    message=message,
                    file=str(file_path),
                    line=line_num,
                    cwe_id=cwe,
                    recommendation='Sanitize user input and use safe DOM manipulation methods'
                ))
        
        return issues
    
    def _check_crypto(
        self,
        line: str,
        file_path: Path,
        line_num: int
    ) -> List[SecurityIssue]:
        """檢查不安全的加密算法"""
        issues = []
        
        for pattern, issue_type, message in self.crypto_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(SecurityIssue(
                    type=issue_type,
                    severity='high',
                    message=message,
                    file=str(file_path),
                    line=line_num,
                    cwe_id='CWE-327',
                    recommendation='Use SHA-256 or stronger cryptographic algorithms'
                ))
        
        return issues
    
    def _check_path_traversal(
        self,
        line: str,
        file_path: Path,
        line_num: int
    ) -> List[SecurityIssue]:
        """檢查路徑遍歷風險"""
        issues = []
        
        for pattern, issue_type, message in self.path_traversal_patterns:
            if re.search(pattern, line):
                issues.append(SecurityIssue(
                    type=issue_type,
                    severity='high',
                    message=message,
                    file=str(file_path),
                    line=line_num,
                    cwe_id='CWE-22',
                    recommendation='Validate and sanitize file paths, use whitelisting'
                ))
        
        return issues
    
    def _get_scannable_files(self, directory: Path) -> List[Path]:
        """獲取可掃描的文件"""
        scannable_extensions = {
            '.py', '.js', '.ts', '.java', '.go', '.rs',
            '.cpp', '.c', '.php', '.rb', '.cs'
        }
        
        files = []
        import os
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.suffix in scannable_extensions:
                    files.append(file_path)
        
        return files
    
    def generate_report(self, issues: List[SecurityIssue]) -> Dict:
        """
        生成安全掃描報告
        
        Args:
            issues: 安全問題列表
            
        Returns:
            Dict: 掃描報告
        """
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        return {
            'total_issues': len(issues),
            'severity_counts': severity_counts,
            'issues_by_type': self._group_by_type(issues),
            'critical_files': self._get_critical_files(issues),
            'recommendations': self._get_recommendations(issues)
        }
    
    def _group_by_type(self, issues: List[SecurityIssue]) -> Dict[str, int]:
        """按類型分組問題"""
        type_counts = {}
        for issue in issues:
            type_counts[issue.type] = type_counts.get(issue.type, 0) + 1
        return type_counts
    
    def _get_critical_files(self, issues: List[SecurityIssue]) -> List[str]:
        """獲取包含嚴重問題的文件"""
        critical_files = set()
        for issue in issues:
            if issue.severity == 'critical':
                critical_files.add(issue.file)
        return list(critical_files)
    
    def _get_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """獲取修復建議"""
        recommendations = set()
        for issue in issues:
            if issue.recommendation:
                recommendations.add(issue.recommendation)
        return list(recommendations)


# 便利函數
async def scan_for_security_issues(
    code_path: str,
    config: Optional[Dict] = None
) -> List[SecurityIssue]:
    """
    便利函數：執行安全掃描
    
    Args:
        code_path: 代碼路徑
        config: 配置
        
    Returns:
        List[SecurityIssue]: 安全問題列表
    """
    scanner = SecurityScanner(config)
    return await scanner.scan(code_path)
