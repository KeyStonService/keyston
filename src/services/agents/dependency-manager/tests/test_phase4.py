"""
Phase 4 企業級功能單元測試

測試內容：
- 企業整合模組
- 商業分析模組
- 智能推薦引擎
- 下世代安全模組
"""

import os
import sys
import unittest

# 添加路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from enterprise.analytics import (
    CommercialAnalytics,
    CostCategory,
    TechDebtItem,
    TechDebtType,
)
from enterprise.integration import (
    AuthMethod,
    EnterpriseIntegration,
    IntegrationConfig,
    IntegrationType,
    WebhookEvent,
)
from enterprise.recommendation import (
    IntelligentRecommendation,
    RecommendationType,
    RiskLevel,
)
from enterprise.security import (
    ComplianceFramework,
    NextGenSecurity,
    SBOMFormat,
    SupplyChainRisk,
    TrustLevel,
)


class TestEnterpriseIntegration(unittest.TestCase):
    """企業整合模組測試"""

    def setUp(self):
        self.integration = EnterpriseIntegration()

    def test_register_integration(self):
        """測試註冊整合"""
        config = IntegrationConfig(
            type=IntegrationType.SLACK,
            name="slack-alerts",
            endpoint="https://hooks.slack.com/services/xxx",
            auth_method=AuthMethod.API_KEY
        )

        result = self.integration.register_integration(config)
        self.assertTrue(result)

        # 重複註冊應失敗
        result2 = self.integration.register_integration(config)
        self.assertFalse(result2)

    def test_list_integrations(self):
        """測試列出整合"""
        configs = [
            IntegrationConfig(
                type=IntegrationType.SLACK,
                name="slack",
                endpoint="https://slack.com",
                auth_method=AuthMethod.API_KEY,
                enabled=True
            ),
            IntegrationConfig(
                type=IntegrationType.GITHUB,
                name="github",
                endpoint="https://api.github.com",
                auth_method=AuthMethod.OAUTH2,
                enabled=False
            )
        ]

        for config in configs:
            self.integration.register_integration(config)

        # 列出所有
        all_integrations = self.integration.list_integrations()
        self.assertEqual(len(all_integrations), 2)

        # 僅啟用
        enabled = self.integration.list_integrations(enabled_only=True)
        self.assertEqual(len(enabled), 1)

        # 按類型
        slack_only = self.integration.list_integrations(
            integration_type=IntegrationType.SLACK
        )
        self.assertEqual(len(slack_only), 1)

    def test_webhook_handler(self):
        """測試 Webhook 處理"""
        received_events = []

        def handler(event: WebhookEvent):
            received_events.append(event)

        self.integration.register_webhook_handler("push", handler)

        result = self.integration.process_webhook(
            event_type="push",
            payload={"repo": "test", "ref": "main"}
        )

        self.assertTrue(result.success)
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].event_type, "push")

    def test_send_notification(self):
        """測試發送通知"""
        config = IntegrationConfig(
            type=IntegrationType.SLACK,
            name="slack",
            endpoint="https://hooks.slack.com",
            auth_method=AuthMethod.API_KEY,
            enabled=True
        )
        self.integration.register_integration(config)

        result = self.integration.send_notification(
            integration_name="slack",
            message="Test notification",
            channel="#alerts"
        )

        self.assertTrue(result.success)

    def test_generate_report(self):
        """測試報告生成"""
        config = IntegrationConfig(
            type=IntegrationType.GITHUB,
            name="github",
            endpoint="https://api.github.com",
            auth_method=AuthMethod.OAUTH2
        )
        self.integration.register_integration(config)

        report = self.integration.generate_integration_report()

        self.assertEqual(report["total_integrations"], 1)
        self.assertIn("github", report["integrations_by_type"])

    def test_format_report_zh_tw(self):
        """測試繁體中文報告格式化"""
        report = self.integration.generate_integration_report()
        formatted = self.integration.format_report_zh_tw(report)

        self.assertIn("企業整合狀態報告", formatted)


class TestCommercialAnalytics(unittest.TestCase):
    """商業分析模組測試"""

    def setUp(self):
        self.analytics = CommercialAnalytics(hourly_rate=100.0)

    def test_calculate_roi(self):
        """測試 ROI 計算"""
        investment = 10000.0
        returns = [2000.0] * 12  # 每月 2000 回報

        roi = self.analytics.calculate_roi(investment, returns)

        self.assertGreater(roi.roi_percentage, 0)
        self.assertLess(roi.payback_period_months, 12)
        self.assertIsNotNone(roi.net_present_value)

    def test_analyze_dependency_cost(self):
        """測試依賴成本分析"""
        costs = self.analytics.analyze_dependency_cost(
            dependency_name="express",
            version="4.18.0",
            is_outdated=True,
            has_vulnerabilities=2,
            has_license_risk=False,
            monthly_maintenance_hours=2.0
        )

        self.assertGreater(len(costs), 0)

        # 應有維護成本
        maintenance_costs = [c for c in costs if c.category == CostCategory.MAINTENANCE]
        self.assertEqual(len(maintenance_costs), 1)

        # 應有升級成本
        upgrade_costs = [c for c in costs if c.category == CostCategory.UPGRADE]
        self.assertEqual(len(upgrade_costs), 1)

        # 應有安全成本
        security_costs = [c for c in costs if c.category == CostCategory.SECURITY]
        self.assertEqual(len(security_costs), 1)

    def test_tech_debt_tracking(self):
        """測試技術債務追蹤"""
        debt = TechDebtItem(
            debt_type=TechDebtType.OUTDATED_DEPENDENCY,
            dependency_name="lodash",
            severity="medium",
            estimated_fix_hours=4.0,
            hourly_rate=100.0
        )

        self.analytics.register_tech_debt(debt)

        summary = self.analytics.get_tech_debt_summary()

        self.assertGreater(summary["total_principal"], 0)
        self.assertEqual(summary["affected_dependencies"], 1)

    def test_debt_payoff_plan(self):
        """測試債務還款計畫"""
        debts = [
            TechDebtItem(
                debt_type=TechDebtType.SECURITY_VULNERABILITY,
                dependency_name="pkg1",
                severity="critical",
                estimated_fix_hours=8.0
            ),
            TechDebtItem(
                debt_type=TechDebtType.OUTDATED_DEPENDENCY,
                dependency_name="pkg2",
                severity="low",
                estimated_fix_hours=2.0
            )
        ]

        for debt in debts:
            self.analytics.register_tech_debt(debt)

        plan = self.analytics.calculate_debt_payoff_plan(
            monthly_budget=500.0,
            strategy="critical_first"
        )

        self.assertGreater(len(plan), 0)
        # 關鍵優先策略應先處理 critical
        self.assertEqual(plan[0]["severity"], "critical")

    def test_comprehensive_analysis(self):
        """測試綜合分析"""
        dependencies = [
            {"name": "express", "version": "4.18.0", "outdated": True, "vulnerabilities": 1},
            {"name": "lodash", "version": "4.17.21", "outdated": False, "vulnerabilities": 0},
        ]

        analysis = self.analytics.comprehensive_analysis(dependencies)

        self.assertIn("summary", analysis)
        self.assertIn("roi_analysis", analysis)
        self.assertIn("tech_debt", analysis)
        self.assertIn("recommendations", analysis)

    def test_format_report_zh_tw(self):
        """測試繁體中文報告"""
        dependencies = [{"name": "test", "version": "1.0.0"}]
        analysis = self.analytics.comprehensive_analysis(dependencies)
        formatted = self.analytics.format_report_zh_tw(analysis)

        self.assertIn("商業分析報告", formatted)
        self.assertIn("ROI", formatted)


class TestIntelligentRecommendation(unittest.TestCase):
    """智能推薦引擎測試"""

    def setUp(self):
        self.engine = IntelligentRecommendation()

    def test_calculate_health_score(self):
        """測試健康度評分"""
        score = self.engine.calculate_health_score(
            dependency_name="express",
            version="4.18.0",
            metadata={
                "last_update_days": 15,
                "vulnerability_count": 0,
                "stars": 50000,
                "weekly_downloads": 20000000,
                "has_documentation": True,
                "license": "MIT"
            }
        )

        self.assertGreater(score.overall_score, 70)
        self.assertIn(score.grade, ["A", "B", "C"])

    def test_health_score_deprecated(self):
        """測試已棄用套件健康度"""
        score = self.engine.calculate_health_score(
            dependency_name="moment",
            version="2.29.0",
            metadata={}
        )

        # 已棄用套件應有較低分數
        self.assertLessEqual(score.overall_score, 50)

    def test_find_alternatives(self):
        """測試替代方案發現"""
        alternatives = self.engine.find_alternatives(
            dependency_name="moment",
            current_version="2.29.0"
        )

        self.assertGreater(len(alternatives), 0)

        # 應找到 dayjs, date-fns 等替代
        alt_names = [a.name for a in alternatives]
        self.assertTrue(any(name in alt_names for name in ["dayjs", "date-fns"]))

    def test_plan_upgrade_path(self):
        """測試升級路徑規劃"""
        path = self.engine.plan_upgrade_path(
            dependency_name="express",
            current_version="3.0.0",
            target_version="5.0.0"
        )

        self.assertEqual(path.current_version, "3.0.0")
        self.assertEqual(path.target_version, "5.0.0")
        self.assertEqual(path.risk_level, RiskLevel.HIGH)  # 主版本升級
        self.assertGreater(len(path.breaking_changes), 0)

    def test_predict_risks(self):
        """測試風險預測"""
        dependencies = [
            {"name": "moment", "version": "2.29.0"},
            {"name": "express", "version": "0.1.0"},
        ]

        risks = self.engine.predict_risks(dependencies)

        self.assertGreater(len(risks), 0)

        # moment 應有棄用風險
        moment_risks = [r for r in risks if r.dependency_name == "moment"]
        self.assertGreater(len(moment_risks), 0)

    def test_generate_recommendations(self):
        """測試建議生成"""
        dependencies = [
            {"name": "lodash", "version": "4.0.0", "outdated": True, "vulnerabilities": 0},
            {"name": "moment", "version": "2.29.0", "outdated": False, "vulnerabilities": 0},
        ]

        recommendations = self.engine.generate_recommendations(dependencies)

        self.assertGreater(len(recommendations), 0)

        # moment 應有替換建議
        replace_recs = [r for r in recommendations if r.rec_type == RecommendationType.REPLACE]
        self.assertGreater(len(replace_recs), 0)

    def test_generate_insight_report(self):
        """測試洞察報告生成"""
        dependencies = [
            {"name": "express", "version": "4.18.0"},
        ]

        report = self.engine.generate_insight_report(dependencies)

        self.assertIn("summary", report)
        self.assertIn("health_scores", report)
        self.assertIn("risks", report)
        self.assertIn("recommendations", report)

    def test_format_report_zh_tw(self):
        """測試繁體中文報告"""
        dependencies = [{"name": "express", "version": "4.18.0"}]
        report = self.engine.generate_insight_report(dependencies)
        formatted = self.engine.format_report_zh_tw(report)

        self.assertIn("智能洞察報告", formatted)
        self.assertIn("健康度評分", formatted)


class TestNextGenSecurity(unittest.TestCase):
    """下世代安全模組測試"""

    def setUp(self):
        self.security = NextGenSecurity()

    def test_generate_sbom(self):
        """測試 SBOM 生成"""
        dependencies = [
            {"name": "express", "version": "4.18.0", "license": "MIT"},
            {"name": "lodash", "version": "4.17.21", "license": "MIT"},
        ]

        sbom = self.security.generate_sbom(
            project_name="test-project",
            version="1.0.0",
            dependencies=dependencies
        )

        self.assertEqual(sbom.name, "test-project")
        self.assertEqual(len(sbom.components), 2)
        self.assertEqual(sbom.format, SBOMFormat.CYCLONEDX)

    def test_export_sbom_cyclonedx(self):
        """測試 SBOM 匯出 (CycloneDX)"""
        dependencies = [
            {"name": "express", "version": "4.18.0", "license": "MIT"}
        ]

        sbom = self.security.generate_sbom("test", "1.0.0", dependencies)
        exported = self.security.export_sbom(sbom)

        self.assertIn("CycloneDX", exported)
        self.assertIn("express", exported)

    def test_export_sbom_spdx(self):
        """測試 SBOM 匯出 (SPDX)"""
        dependencies = [
            {"name": "lodash", "version": "4.17.21", "license": "MIT"}
        ]

        sbom = self.security.generate_sbom(
            "test", "1.0.0", dependencies,
            sbom_format=SBOMFormat.SPDX
        )
        exported = self.security.export_sbom(sbom)

        self.assertIn("SPDX", exported)
        self.assertIn("lodash", exported)

    def test_check_compliance_soc2(self):
        """測試 SOC2 合規檢查"""
        dependencies = [
            {"name": "express", "version": "4.18.0", "vulnerabilities": 0},
        ]

        report = self.security.check_compliance(
            framework=ComplianceFramework.SOC2,
            dependencies=dependencies
        )

        self.assertEqual(report.framework, ComplianceFramework.SOC2)
        self.assertGreater(report.total_requirements, 0)
        self.assertGreaterEqual(report.score, 0)

    def test_check_compliance_iso27001(self):
        """測試 ISO27001 合規檢查"""
        dependencies = [
            {"name": "express", "version": "4.18.0", "supplier": "expressjs"},
        ]

        report = self.security.check_compliance(
            framework=ComplianceFramework.ISO27001,
            dependencies=dependencies
        )

        self.assertEqual(report.framework, ComplianceFramework.ISO27001)
        self.assertGreater(len(report.checks), 0)

    def test_analyze_supply_chain_malicious(self):
        """測試供應鏈分析 - 惡意套件"""
        dependencies = [
            {"name": "event-stream", "version": "3.3.6"},
        ]

        alerts = self.security.analyze_supply_chain(dependencies)

        self.assertGreater(len(alerts), 0)

        malicious_alerts = [a for a in alerts
                          if a.risk_type == SupplyChainRisk.MALICIOUS_PACKAGE]
        self.assertGreater(len(malicious_alerts), 0)

    def test_analyze_supply_chain_unpinned(self):
        """測試供應鏈分析 - 未鎖定版本"""
        dependencies = [
            {"name": "express", "version": "*"},
        ]

        alerts = self.security.analyze_supply_chain(dependencies)

        unpinned_alerts = [a for a in alerts
                         if a.risk_type == SupplyChainRisk.UNPINNED_DEPENDENCY]
        self.assertGreater(len(unpinned_alerts), 0)

    def test_assess_trust(self):
        """測試信任評估"""
        assessment = self.security.assess_trust(
            package_name="express",
            version="4.18.0",
            metadata={
                "from_official_registry": True,
                "has_signature": True,
                "verified_maintainer": True,
                "integrity_verified": True
            }
        )

        self.assertEqual(assessment.trust_level, TrustLevel.VERIFIED)
        self.assertGreater(assessment.score, 80)

    def test_assess_trust_malicious(self):
        """測試信任評估 - 惡意套件"""
        assessment = self.security.assess_trust(
            package_name="event-stream",
            version="3.3.6"
        )

        self.assertEqual(assessment.trust_level, TrustLevel.UNTRUSTED)

    def test_verify_integrity(self):
        """測試完整性驗證"""
        content = b"test content"
        expected = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"

        result = self.security.verify_integrity(
            package_name="test",
            version="1.0.0",
            expected_checksum=expected,
            content=content,
            algorithm="sha256"
        )

        self.assertTrue(result.verified)

    def test_generate_security_report(self):
        """測試安全報告生成"""
        dependencies = [
            {"name": "express", "version": "4.18.0"},
            {"name": "lodash", "version": "4.17.21"},
        ]

        report = self.security.generate_security_report(
            dependencies=dependencies,
            frameworks=[ComplianceFramework.SOC2]
        )

        self.assertIn("summary", report)
        self.assertIn("sbom", report)
        self.assertIn("supply_chain", report)
        self.assertIn("trust_assessments", report)
        self.assertIn("compliance", report)

    def test_format_report_zh_tw(self):
        """測試繁體中文報告"""
        dependencies = [{"name": "express", "version": "4.18.0"}]
        report = self.security.generate_security_report(dependencies)
        formatted = self.security.format_report_zh_tw(report)

        self.assertIn("下世代安全報告", formatted)
        self.assertIn("供應鏈", formatted)


class TestPhase4Integration(unittest.TestCase):
    """Phase 4 整合測試"""

    def test_full_enterprise_workflow(self):
        """測試完整企業工作流程"""
        # 依賴項清單
        dependencies = [
            {
                "name": "express",
                "version": "4.18.0",
                "license": "MIT",
                "outdated": False,
                "vulnerabilities": 0
            },
            {
                "name": "moment",
                "version": "2.29.0",
                "license": "MIT",
                "outdated": True,
                "vulnerabilities": 0
            },
            {
                "name": "lodash",
                "version": "4.17.21",
                "license": "MIT",
                "outdated": False,
                "vulnerabilities": 1
            }
        ]

        # 1. 安全分析
        security = NextGenSecurity()
        security_report = security.generate_security_report(dependencies)
        self.assertIn("summary", security_report)

        # 2. 商業分析
        analytics = CommercialAnalytics()
        business_report = analytics.comprehensive_analysis(dependencies)
        self.assertIn("roi_analysis", business_report)

        # 3. 智能建議
        recommendation = IntelligentRecommendation()
        insight_report = recommendation.generate_insight_report(dependencies)
        self.assertIn("recommendations", insight_report)

        # 4. 企業整合
        integration = EnterpriseIntegration()
        integration_report = integration.generate_integration_report()
        self.assertIn("total_integrations", integration_report)


if __name__ == '__main__':
    unittest.main()
