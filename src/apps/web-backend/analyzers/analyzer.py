#!/usr/bin/env python3
"""
============================================================================
代碼分析服務 - 核心模塊 (Code Analysis Service - Core Module)
============================================================================
Project: SLASolve - Senior Automation Architect & Code Intelligence Engineer
Version: 1.0.0
============================================================================
"""

import asyncio
import hashlib
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ============================================================================
# 數據模型 (Data Models)
# ============================================================================


class SeverityLevel(str, Enum):
    """漏洞嚴重程度"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class IssueType(str, Enum):
    """問題類型"""

    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    CODE_QUALITY = "CODE_QUALITY"
    MAINTAINABILITY = "MAINTAINABILITY"
    DEPENDENCY = "DEPENDENCY"


@dataclass
class CodeIssue:
    """代碼問題"""

    id: str
    type: IssueType
    severity: SeverityLevel
    file: str
    line: int
    column: int
    message: str
    description: str
    suggestion: str | None = None
    tags: list[str] = field(default_factory=list)
    timestamp: datetime | None = None
    evidence_hash: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.evidence_hash is None:
            # 生成完整的 SHA256 證據哈希以符合 SLSA 合規要求
            evidence = f"{self.file}:{self.line}:{self.message}"
            self.evidence_hash = hashlib.sha256(evidence.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        result = asdict(self)
        result["type"] = self.type.value
        result["severity"] = self.severity.value
        result["timestamp"] = self.timestamp.isoformat() if self.timestamp else None
        return result


@dataclass
class AnalysisResult:
    """分析結果"""

    repository: str
    commit_hash: str
    analysis_timestamp: datetime
    duration: float
    issues: list[CodeIssue]
    metrics: dict[str, Any]

    @property
    def total_issues(self) -> int:
        """總問題數"""
        return len(self.issues)

    @property
    def critical_issues(self) -> int:
        """嚴重問題數"""
        return sum(1 for i in self.issues if i.severity == SeverityLevel.CRITICAL)

    @property
    def high_issues(self) -> int:
        """高危問題數"""
        return sum(1 for i in self.issues if i.severity == SeverityLevel.HIGH)

    @property
    def quality_score(self) -> float:
        """
        計算代碼質量評分 (0-100)

        Returns:
            float: 質量分數
        """
        if not self.issues:
            return 100.0

        severity_weights = {
            SeverityLevel.CRITICAL: 10,
            SeverityLevel.HIGH: 5,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 1,
            SeverityLevel.INFO: 0.5,
        }

        total_weight = sum(severity_weights.get(issue.severity, 0) for issue in self.issues)

        return max(0, 100 - total_weight)

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            "repository": self.repository,
            "commit_hash": self.commit_hash,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "duration": self.duration,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "quality_score": self.quality_score,
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics,
        }


# ============================================================================
# 分析器基類 (Base Analyzer)
# ============================================================================


class BaseAnalyzer:
    """分析器基類"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    async def analyze(self, code: str, file_path: str) -> list[CodeIssue]:
        """
        分析代碼 - 子類必須實現此方法

        Args:
            code: 代碼內容
            file_path: 文件路徑

        Returns:
            List[CodeIssue]: 問題列表
        """
        # Default implementation for base analyzer
        # Subclasses should override this method
        self.logger.warning(f"{self.__class__.__name__}.analyze() called but not implemented")
        return []


# ============================================================================
# 靜態分析器 (Static Analyzer)
# ============================================================================


class StaticAnalyzer(BaseAnalyzer):
    """靜態代碼分析"""

    async def analyze(self, code: str, file_path: str) -> list[CodeIssue]:
        """
        執行靜態分析

        Args:
            code: 代碼內容
            file_path: 文件路徑

        Returns:
            List[CodeIssue]: 問題列表
        """
        issues = []

        # 檢測安全漏洞
        security_issues = await self._check_security(code, file_path)
        issues.extend(security_issues)

        # 檢測代碼質量
        quality_issues = await self._check_code_quality(code, file_path)
        issues.extend(quality_issues)

        # 檢測性能問題
        performance_issues = await self._check_performance(code, file_path)
        issues.extend(performance_issues)

        return issues

    async def _check_security(self, code: str, file_path: str) -> list[CodeIssue]:
        """
        檢測安全漏洞

        Args:
            code: 代碼內容
            file_path: 文件路徑

        Returns:
            List[CodeIssue]: 安全問題列表
        """
        issues = []

        # 檢測硬編碼密鑰
        if self._contains_hardcoded_secrets(code):
            issues.append(
                CodeIssue(
                    id="SEC-001",
                    type=IssueType.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    file=file_path,
                    line=self._find_line_number(code, r"password\s*=\s*['\"]"),
                    column=1,
                    message="Hardcoded secrets detected",
                    description="代碼中檢測到硬編碼的密鑰或敏感信息",
                    suggestion="使用環境變量或密鑰管理服務",
                    tags=["security", "secrets", "credentials"],
                )
            )

        # 檢測 SQL 注入
        if self._contains_sql_injection_risk(code):
            issues.append(
                CodeIssue(
                    id="SEC-002",
                    type=IssueType.SECURITY,
                    severity=SeverityLevel.HIGH,
                    file=file_path,
                    line=self._find_line_number(code, r"(query|execute|sql)\s*=\s*['\"].*\+"),
                    column=1,
                    message="SQL injection risk detected",
                    description="檢測到潛在的 SQL 注入風險",
                    suggestion="使用參數化查詢或 ORM",
                    tags=["security", "sql-injection", "database"],
                )
            )

        # 檢測 XSS 漏洞
        if self._contains_xss_risk(code):
            issues.append(
                CodeIssue(
                    id="SEC-003",
                    type=IssueType.SECURITY,
                    severity=SeverityLevel.HIGH,
                    file=file_path,
                    line=self._find_line_number(code, r"innerHTML\s*="),
                    column=1,
                    message="XSS vulnerability detected",
                    description="檢測到跨站腳本攻擊漏洞",
                    suggestion="使用 textContent 或 DOMPurify 進行清理",
                    tags=["security", "xss", "web"],
                )
            )

        return issues

    async def _check_code_quality(self, code: str, file_path: str) -> list[CodeIssue]:
        """
        檢測代碼質量問題

        Args:
            code: 代碼內容
            file_path: 文件路徑

        Returns:
            List[CodeIssue]: 質量問題列表
        """
        issues = []

        # 計算圈複雜度
        complexity = self._calculate_cyclomatic_complexity(code)
        if complexity > 10:
            issues.append(
                CodeIssue(
                    id="CQ-001",
                    type=IssueType.CODE_QUALITY,
                    severity=SeverityLevel.MEDIUM,
                    file=file_path,
                    line=1,
                    column=1,
                    message=f"High cyclomatic complexity: {complexity}",
                    description=f"函數複雜度為 {complexity}，建議值為 10 以下",
                    suggestion="考慮將函數分解為更小的單元",
                    tags=["quality", "complexity", "maintainability"],
                )
            )

        # 檢測代碼重複
        duplication_ratio = self._calculate_duplication_ratio(code)
        if duplication_ratio > 0.05:
            issues.append(
                CodeIssue(
                    id="CQ-002",
                    type=IssueType.CODE_QUALITY,
                    severity=SeverityLevel.LOW,
                    file=file_path,
                    line=1,
                    column=1,
                    message=f"Code duplication: {duplication_ratio*100:.1f}%",
                    description=f"檢測到 {duplication_ratio*100:.1f}% 的代碼重複",
                    suggestion="提取公共代碼到共享模塊",
                    tags=["quality", "duplication", "refactoring"],
                )
            )

        # 檢測缺少類型註解
        if self._missing_type_hints(code, file_path):
            issues.append(
                CodeIssue(
                    id="CQ-003",
                    type=IssueType.CODE_QUALITY,
                    severity=SeverityLevel.LOW,
                    file=file_path,
                    line=1,
                    column=1,
                    message="Missing type hints",
                    description="函數缺少類型註解",
                    suggestion="添加類型註解以提高代碼可讀性和類型安全",
                    tags=["quality", "type-hints", "documentation"],
                )
            )

        return issues

    async def _check_performance(self, code: str, file_path: str) -> list[CodeIssue]:
        """
        檢測性能問題

        Args:
            code: 代碼內容
            file_path: 文件路徑

        Returns:
            List[CodeIssue]: 性能問題列表
        """
        issues = []

        # 檢測 N+1 查詢
        if self._contains_n_plus_one_query(code):
            issues.append(
                CodeIssue(
                    id="PERF-001",
                    type=IssueType.PERFORMANCE,
                    severity=SeverityLevel.HIGH,
                    file=file_path,
                    line=self._find_line_number(code, r"for\s+\w+\s+in\s+.*:.*query"),
                    column=1,
                    message="N+1 query pattern detected",
                    description="檢測到 N+1 查詢模式，可能導致性能問題",
                    suggestion="使用 JOIN 或批量查詢優化",
                    tags=["performance", "database", "n-plus-one"],
                )
            )

        # 檢測低效循環
        if self._contains_inefficient_loop(code):
            issues.append(
                CodeIssue(
                    id="PERF-002",
                    type=IssueType.PERFORMANCE,
                    severity=SeverityLevel.MEDIUM,
                    file=file_path,
                    line=self._find_line_number(code, r"for\s+\w+\s+in\s+.*:\s*for"),
                    column=1,
                    message="Inefficient nested loop detected",
                    description="檢測到低效的嵌套循環",
                    suggestion="考慮使用哈希表或集合優化查找",
                    tags=["performance", "algorithm", "optimization"],
                )
            )

        return issues

    # ========================================================================
    # 輔助方法 (Helper Methods)
    # ========================================================================

    def _contains_hardcoded_secrets(self, code: str) -> bool:
        """檢測硬編碼密鑰"""
        secret_patterns = [
            r"password\s*=\s*['\"][\w\W]+['\"]",
            r"api_key\s*=\s*['\"][\w\W]+['\"]",
            r"secret\s*=\s*['\"][\w\W]+['\"]",
            r"token\s*=\s*['\"][\w\W]+['\"]",
        ]
        return any(re.search(pattern, code, re.IGNORECASE) for pattern in secret_patterns)

    def _contains_sql_injection_risk(self, code: str) -> bool:
        """檢測 SQL 注入風險"""
        # 檢測字符串連接的 SQL 查詢
        patterns = [
            r"(query|execute|sql)\s*=\s*['\"].*\+",
            r"(query|execute|sql)\s*=\s*.*%\s*\(",
            r"cursor\.execute\([^)]*\+[^)]*\)",
        ]
        return any(re.search(pattern, code, re.IGNORECASE) for pattern in patterns)

    def _contains_xss_risk(self, code: str) -> bool:
        """檢測 XSS 風險"""
        patterns = [r"innerHTML\s*=\s*[^(]", r"document\.write\(", r"\.html\([^)]*\+[^)]*\)"]
        return any(re.search(pattern, code, re.IGNORECASE) for pattern in patterns)

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """計算圈複雜度"""
        # 簡化計算：計算控制流關鍵字
        keywords = ["if", "elif", "else", "for", "while", "except", "and", "or", "case"]
        complexity = 1
        for keyword in keywords:
            complexity += len(re.findall(rf"\b{keyword}\b", code, re.IGNORECASE))
        return complexity

    def _calculate_duplication_ratio(self, code: str) -> float:
        """計算代碼重複率"""
        lines = code.split("\n")
        # 過濾空行和註釋
        lines = [
            line.strip() for line in lines if line.strip() and not line.strip().startswith("#")
        ]
        if len(lines) < 10:
            return 0.0

        # 簡化計算：檢查重複行
        unique_lines = len(set(lines))
        return max(0, 1 - (unique_lines / len(lines)))

    def _missing_type_hints(self, code: str, file_path: str) -> bool:
        """檢查是否缺少類型註解"""
        # 只檢查 Python 文件
        if not file_path.endswith(".py"):
            return False

        # 檢查函數定義是否有類型註解
        function_pattern = r"def\s+\w+\s*\([^)]*\)\s*:"
        functions = re.findall(function_pattern, code)
        if not functions:
            return False

        # 檢查是否有 -> 返回類型註解
        typed_functions = re.findall(r"def\s+\w+\s*\([^)]*\)\s*->", code)

        return len(typed_functions) < len(functions)

    def _contains_n_plus_one_query(self, code: str) -> bool:
        """檢測 N+1 查詢"""
        # 檢測循環中的查詢
        pattern = r"for\s+\w+\s+in\s+.*:\s*.*\.(query|filter|get)\("
        return bool(re.search(pattern, code, re.DOTALL))

    def _contains_inefficient_loop(self, code: str) -> bool:
        """檢測低效循環"""
        # 檢測嵌套循環
        pattern = r"for\s+\w+\s+in\s+.*:\s*.*for\s+\w+\s+in"
        return bool(re.search(pattern, code, re.DOTALL))

    def _find_line_number(self, code: str, pattern: str) -> int:
        """查找模式所在行號"""
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                return i
        return 1


# ============================================================================
# 代碼分析引擎 (Code Analysis Engine)
# ============================================================================


class CodeAnalysisEngine:
    """代碼分析引擎"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.analyzers: list[BaseAnalyzer] = [StaticAnalyzer(config)]

    async def analyze_file(self, file_path: str) -> list[CodeIssue]:
        """
        分析單個文件

        Args:
            file_path: 文件路徑

        Returns:
            List[CodeIssue]: 問題列表
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                code = f.read()

            all_issues = []
            for analyzer in self.analyzers:
                issues = await analyzer.analyze(code, file_path)
                all_issues.extend(issues)

            return all_issues
        except Exception as e:
            self.logger.error(f"分析文件失敗 {file_path}: {e}")
            return []

    async def analyze_repository(self, repo_path: str, commit_hash: str) -> AnalysisResult:
        """
        分析整個代碼庫

        Args:
            repo_path: 代碼庫路徑
            commit_hash: 提交哈希

        Returns:
            AnalysisResult: 分析結果
        """
        start_time = datetime.utcnow()
        all_issues: list[CodeIssue] = []

        # 這裡應該實現實際的文件掃描邏輯
        # 為示例目的，暫時返回空結果

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        return AnalysisResult(
            repository=repo_path,
            commit_hash=commit_hash,
            analysis_timestamp=start_time,
            duration=duration,
            issues=all_issues,
            metrics={"files_analyzed": 0, "lines_of_code": 0, "total_issues": len(all_issues)},
        )


# ============================================================================
# 主程序入口 (Main Entry Point)
# ============================================================================


async def main() -> None:
    """主程序"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    print("代碼分析引擎已初始化")


if __name__ == "__main__":
    asyncio.run(main())
