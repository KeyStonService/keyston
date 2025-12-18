"""
第二階段功能測試
Phase 2 Tests - Analyzers and Utils
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# 添加 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from analyzers.go_analyzer import GoAnalyzer
from analyzers.pip_analyzer import PipAnalyzer
from models.dependency import Dependency, DependencyType, Ecosystem
from utils.audit_logger import AuditEventType, AuditLogger, AuditSeverity
from utils.dependency_tree import DependencyTree, RiskLevel


class TestPipAnalyzer:
    """pip 分析器測試"""

    def test_clean_version(self):
        """測試版本號清理"""
        analyzer = PipAnalyzer()

        assert analyzer._clean_version("==1.0.0") == "1.0.0"
        assert analyzer._clean_version(">=2.0.0") == "2.0.0"
        assert analyzer._clean_version("~=1.4.2") == "1.4.2"
        assert analyzer._clean_version("^3.0.0") == "3.0.0"
        assert analyzer._clean_version("1.0.0") == "1.0.0"

    def test_parse_requirement_line(self):
        """測試解析單行依賴"""
        analyzer = PipAnalyzer()

        # 基本格式
        dep = analyzer._parse_requirement_line("requests==2.28.0")
        assert dep is not None
        assert dep.name == "requests"
        assert dep.current_version == "2.28.0"

        # 帶 extras
        dep = analyzer._parse_requirement_line("requests[security]>=2.0.0")
        assert dep is not None
        assert dep.name == "requests"

        # 無版本
        dep = analyzer._parse_requirement_line("flask")
        assert dep is not None
        assert dep.name == "flask"
        assert dep.current_version == "latest"

    @pytest.mark.asyncio
    async def test_parse_requirements_txt(self):
        """測試解析 requirements.txt"""
        analyzer = PipAnalyzer()

        # 創建臨時文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Test requirements\n")
            f.write("requests==2.28.0\n")
            f.write("flask>=2.0.0\n")
            f.write("django~=4.0\n")
            f.write("\n")
            f.write("# Comment line\n")
            f.write("numpy\n")
            temp_path = f.name

        try:
            deps = await analyzer._parse_requirements_txt(Path(temp_path))

            assert len(deps) == 4
            names = [d.name for d in deps]
            assert "requests" in names
            assert "flask" in names
            assert "django" in names
            assert "numpy" in names
        finally:
            os.unlink(temp_path)

    def test_extract_poetry_version(self):
        """測試提取 Poetry 版本"""
        analyzer = PipAnalyzer()

        assert analyzer._extract_poetry_version("^1.0.0") == "1.0.0"
        assert analyzer._extract_poetry_version({"version": "^2.0.0"}) == "2.0.0"
        assert analyzer._extract_poetry_version({"git": "https://github.com/..."}) == "git"
        assert analyzer._extract_poetry_version("*") == "*"


class TestGoAnalyzer:
    """Go 分析器測試"""

    def test_clean_version(self):
        """測試版本號清理"""
        analyzer = GoAnalyzer()

        assert analyzer._clean_version("v1.0.0") == "1.0.0"
        assert analyzer._clean_version("v0.0.0-20210101-abcdef") == "0.0.0-20210101-abcdef"
        assert analyzer._clean_version("1.2.3") == "1.2.3"

    def test_parse_require_line(self):
        """測試解析 require 行"""
        analyzer = GoAnalyzer()

        # 正常依賴
        dep = analyzer._parse_require_line("github.com/pkg/errors v0.9.1")
        assert dep is not None
        assert dep.name == "github.com/pkg/errors"
        assert dep.current_version == "0.9.1"
        assert dep.dep_type == DependencyType.DIRECT

        # 間接依賴
        dep = analyzer._parse_require_line("golang.org/x/sys v0.0.0-123 // indirect")
        assert dep is not None
        assert dep.dep_type == DependencyType.TRANSITIVE

        # 空行
        dep = analyzer._parse_require_line("")
        assert dep is None

        # 註釋行
        dep = analyzer._parse_require_line("// comment")
        assert dep is None

    @pytest.mark.asyncio
    async def test_parse_go_mod(self):
        """測試解析 go.mod"""
        analyzer = GoAnalyzer()

        # 創建臨時 go.mod 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mod', delete=False) as f:
            f.write("module github.com/test/project\n\n")
            f.write("go 1.21\n\n")
            f.write("require (\n")
            f.write("\tgithub.com/pkg/errors v0.9.1\n")
            f.write("\tgithub.com/stretchr/testify v1.8.0\n")
            f.write("\tgolang.org/x/sys v0.0.0-20210101 // indirect\n")
            f.write(")\n")
            temp_path = f.name

        try:
            deps = await analyzer.parse_manifest(Path(temp_path))

            assert len(deps) == 3
            names = [d.name for d in deps]
            assert "github.com/pkg/errors" in names
            assert "github.com/stretchr/testify" in names
            assert "golang.org/x/sys" in names

            # 檢查間接依賴標記
            sys_dep = next(d for d in deps if "sys" in d.name)
            assert sys_dep.dep_type == DependencyType.TRANSITIVE
        finally:
            os.unlink(temp_path)


class TestDependencyTree:
    """依賴樹測試"""

    def test_create_tree(self):
        """測試創建依賴樹"""
        tree = DependencyTree("test-project")

        deps = [
            Dependency(name="express", current_version="4.18.0", ecosystem=Ecosystem.NPM),
            Dependency(name="lodash", current_version="4.17.21", ecosystem=Ecosystem.NPM),
        ]

        tree.build_tree(deps)

        assert len(tree.root_nodes) == 2
        assert len(tree._all_nodes) == 2

    def test_risk_calculation(self):
        """測試風險計算"""
        tree = DependencyTree("test-project")

        # 有漏洞的依賴
        vulnerable_dep = Dependency(
            name="vulnerable-pkg",
            current_version="1.0.0",
            ecosystem=Ecosystem.NPM,
            has_vulnerability=True,
            vulnerability_count=3
        )

        risk = tree._calculate_risk(vulnerable_dep)
        assert risk == RiskLevel.CRITICAL

        # 過時的依賴
        outdated_dep = Dependency(
            name="outdated-pkg",
            current_version="1.0.0",
            latest_version="2.0.0",
            ecosystem=Ecosystem.NPM
        )

        risk = tree._calculate_risk(outdated_dep)
        assert risk == RiskLevel.LOW

    def test_render_text(self):
        """測試文字渲染"""
        tree = DependencyTree("test-project")

        deps = [
            Dependency(name="express", current_version="4.18.0", ecosystem=Ecosystem.NPM),
        ]

        tree.build_tree(deps)
        output = tree.render_text()

        assert "test-project" in output
        assert "express" in output
        assert "4.18.0" in output

    def test_get_statistics(self):
        """測試統計資訊"""
        tree = DependencyTree("test-project")

        deps = [
            Dependency(name="pkg1", current_version="1.0.0", ecosystem=Ecosystem.NPM),
            Dependency(
                name="pkg2",
                current_version="1.0.0",
                latest_version="2.0.0",
                ecosystem=Ecosystem.NPM
            ),
            Dependency(
                name="pkg3",
                current_version="1.0.0",
                ecosystem=Ecosystem.NPM,
                has_vulnerability=True
            ),
        ]

        tree.build_tree(deps)
        stats = tree.get_statistics()

        assert stats["total_dependencies"] == 3
        assert stats["outdated_count"] == 1
        assert stats["vulnerable_count"] == 1


class TestAuditLogger:
    """審計日誌測試"""

    def test_log_event(self):
        """測試記錄事件"""
        audit = AuditLogger()

        event = audit.log(
            event_type=AuditEventType.ANALYSIS_STARTED,
            target="test-project",
            details="開始分析"
        )

        assert event.event_type == AuditEventType.ANALYSIS_STARTED
        assert event.target == "test-project"
        assert event.severity == AuditSeverity.INFO

    def test_log_analysis_lifecycle(self):
        """測試分析生命週期記錄"""
        audit = AuditLogger()

        # 開始
        event1 = audit.log_analysis_started("test-project", "npm")
        assert event1.event_type == AuditEventType.ANALYSIS_STARTED

        # 完成
        event2 = audit.log_analysis_completed("test-project", 100, 10, 5)
        assert event2.event_type == AuditEventType.ANALYSIS_COMPLETED
        assert event2.metadata["total_dependencies"] == 100
        assert event2.metadata["outdated_count"] == 10
        assert event2.metadata["vulnerable_count"] == 5

    def test_log_vulnerability(self):
        """測試漏洞記錄"""
        audit = AuditLogger()

        event = audit.log_vulnerability_detected(
            package="lodash",
            vulnerability_id="CVE-2021-23337",
            severity="CRITICAL"
        )

        assert event.event_type == AuditEventType.VULNERABILITY_DETECTED
        assert event.severity == AuditSeverity.CRITICAL
        assert event.metadata["vulnerability_id"] == "CVE-2021-23337"

    def test_get_events_filtered(self):
        """測試過濾事件"""
        audit = AuditLogger()

        audit.log_analysis_started("project1", "npm")
        audit.log_vulnerability_detected("pkg1", "CVE-001", "HIGH")
        audit.log_analysis_completed("project1", 50, 5, 1)

        # 按類型過濾
        vuln_events = audit.get_events(event_type=AuditEventType.VULNERABILITY_DETECTED)
        assert len(vuln_events) == 1

        # 所有事件
        all_events = audit.get_events()
        assert len(all_events) == 3

    def test_get_summary(self):
        """測試摘要資訊"""
        audit = AuditLogger()

        audit.log_analysis_started("project1", "npm")
        audit.log_vulnerability_detected("pkg1", "CVE-001", "CRITICAL")
        audit.log_update_started("pkg1", "1.0.0", "2.0.0")
        audit.log_update_completed("pkg1", "1.0.0", "2.0.0")

        summary = audit.get_summary()

        assert summary["total_events"] == 4
        assert AuditEventType.ANALYSIS_STARTED.value in summary["by_type"]
        assert AuditSeverity.INFO.value in summary["by_severity"]

    def test_file_logging(self):
        """測試文件記錄"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_path = f.name

        try:
            audit = AuditLogger(log_file=temp_path)

            audit.log_analysis_started("test-project", "npm")
            audit.log_analysis_completed("test-project", 10, 1, 0)

            # 驗證文件內容
            with open(temp_path, encoding='utf-8') as f:
                lines = f.readlines()

            assert len(lines) == 2
            assert "analysis_started" in lines[0]
            assert "analysis_completed" in lines[1]
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
