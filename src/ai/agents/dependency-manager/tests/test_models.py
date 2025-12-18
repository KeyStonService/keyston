"""
依賴管理器測試
Tests for Dependency Manager Agent
"""

import pytest
from pathlib import Path
import sys

# 添加 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from models.dependency import (
    Dependency,
    DependencyAnalysis,
    DependencyType,
    DependencyStatus,
    Ecosystem
)
from models.vulnerability import (
    Vulnerability,
    VulnerabilitySeverity,
    VulnerabilitySource
)
from models.update import (
    Update,
    UpdateResult,
    UpdateType,
    UpdateStatus,
    UpdatePolicy
)


class TestDependencyModel:
    """依賴項模型測試"""
    
    def test_create_dependency(self):
        """測試創建依賴項"""
        dep = Dependency(
            name="express",
            current_version="4.18.0",
            ecosystem=Ecosystem.NPM,
            latest_version="4.21.2"
        )
        
        assert dep.name == "express"
        assert dep.current_version == "4.18.0"
        assert dep.latest_version == "4.21.2"
        assert dep.ecosystem == Ecosystem.NPM
    
    def test_is_outdated(self):
        """測試版本過時檢查"""
        dep = Dependency(
            name="lodash",
            current_version="4.17.0",
            ecosystem=Ecosystem.NPM,
            latest_version="4.17.21"
        )
        
        assert dep.is_outdated() is True
        
        # 最新版本
        dep_current = Dependency(
            name="axios",
            current_version="1.6.0",
            ecosystem=Ecosystem.NPM,
            latest_version="1.6.0"
        )
        
        assert dep_current.is_outdated() is False
    
    def test_dependency_analysis(self):
        """測試依賴分析"""
        analysis = DependencyAnalysis(
            analysis_id="test-123",
            project="test-project",
            ecosystem=Ecosystem.NPM
        )
        
        # 添加依賴項
        dep1 = Dependency(
            name="express",
            current_version="4.18.0",
            ecosystem=Ecosystem.NPM,
            latest_version="4.21.2",
            dep_type=DependencyType.DIRECT
        )
        
        dep2 = Dependency(
            name="lodash",
            current_version="4.17.21",
            ecosystem=Ecosystem.NPM,
            latest_version="4.17.21",
            dep_type=DependencyType.TRANSITIVE
        )
        
        analysis.add_dependency(dep1)
        analysis.add_dependency(dep2)
        
        assert analysis.total_count == 2
        assert analysis.direct_count == 1
        assert analysis.transitive_count == 1
        assert analysis.outdated_count == 1


class TestVulnerabilityModel:
    """漏洞模型測試"""
    
    def test_create_vulnerability(self):
        """測試創建漏洞"""
        vuln = Vulnerability(
            id="CVE-2021-23337",
            package="lodash",
            severity=VulnerabilitySeverity.HIGH,
            title="Prototype Pollution",
            fixed_version="4.17.21"
        )
        
        assert vuln.id == "CVE-2021-23337"
        assert vuln.severity == VulnerabilitySeverity.HIGH
        assert vuln.has_fix() is True
    
    def test_severity_from_cvss(self):
        """測試 CVSS 分數轉換"""
        assert VulnerabilitySeverity.from_cvss(9.5) == VulnerabilitySeverity.CRITICAL
        assert VulnerabilitySeverity.from_cvss(7.5) == VulnerabilitySeverity.HIGH
        assert VulnerabilitySeverity.from_cvss(5.0) == VulnerabilitySeverity.MEDIUM
        assert VulnerabilitySeverity.from_cvss(2.0) == VulnerabilitySeverity.LOW
    
    def test_is_critical(self):
        """測試嚴重漏洞檢查"""
        critical_vuln = Vulnerability(
            id="CVE-2024-0001",
            package="test",
            severity=VulnerabilitySeverity.CRITICAL
        )
        
        low_vuln = Vulnerability(
            id="CVE-2024-0002",
            package="test",
            severity=VulnerabilitySeverity.LOW
        )
        
        assert critical_vuln.is_critical() is True
        assert low_vuln.is_critical() is False


class TestUpdateModel:
    """更新模型測試"""
    
    def test_create_update(self):
        """測試創建更新"""
        update = Update(
            package="express",
            from_version="4.18.0",
            to_version="4.21.2",
            update_type=UpdateType.MINOR,
            is_security_fix=False
        )
        
        assert update.package == "express"
        assert update.update_type == UpdateType.MINOR
        assert update.requires_review() is False
    
    def test_major_update_requires_review(self):
        """測試主版本更新需要審查"""
        update = Update(
            package="typescript",
            from_version="4.9.5",
            to_version="5.0.0",
            update_type=UpdateType.MAJOR
        )
        
        assert update.is_major_update() is True
        assert update.requires_review() is True
    
    def test_update_result(self):
        """測試更新結果"""
        result = UpdateResult(result_id="update-123")
        
        success_update = Update(
            package="axios",
            from_version="1.5.0",
            to_version="1.6.0",
            status=UpdateStatus.SUCCESS
        )
        
        failed_update = Update(
            package="moment",
            from_version="2.29.0",
            to_version="2.30.0",
            status=UpdateStatus.FAILED
        )
        
        result.add_update(success_update)
        result.add_update(failed_update)
        
        assert result.success_count == 1
        assert result.failed_count == 1
        assert result.has_failures() is True


class TestNpmAnalyzer:
    """NPM 分析器測試"""
    
    def test_clean_version(self):
        """測試版本號清理"""
        from analyzers.npm_analyzer import NpmAnalyzer
        
        analyzer = NpmAnalyzer()
        
        assert analyzer._clean_version("^1.0.0") == "1.0.0"
        assert analyzer._clean_version("~2.1.0") == "2.1.0"
        assert analyzer._clean_version(">=3.0.0") == "3.0.0"
        assert analyzer._clean_version("1.0.0") == "1.0.0"


class TestAutoUpdater:
    """自動更新器測試"""
    
    def test_classify_update(self):
        """測試更新類型分類"""
        from updaters.auto_updater import AutoUpdater
        
        updater = AutoUpdater()
        
        assert updater._classify_update("1.0.0", "2.0.0") == UpdateType.MAJOR
        assert updater._classify_update("1.0.0", "1.1.0") == UpdateType.MINOR
        assert updater._classify_update("1.0.0", "1.0.1") == UpdateType.PATCH
    
    def test_parse_version(self):
        """測試版本解析"""
        from updaters.auto_updater import AutoUpdater
        
        updater = AutoUpdater()
        
        parts = updater._parse_version("1.2.3")
        assert parts.major == 1
        assert parts.minor == 2
        assert parts.patch == 3
        
        parts_v = updater._parse_version("v2.0.0")
        assert parts_v.major == 2
        
        parts_pre = updater._parse_version("1.0.0-beta.1")
        assert parts_pre.prerelease == "beta.1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
