"""
Phase 7 測試 - SMART-V 評估框架

測試 SMART-V 量化評估系統的各項功能。
"""

import os
import sys
import unittest

# 添加 src 目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluation.evaluation_report import EvaluationReportGenerator
from evaluation.smartv_framework import (
    AchievabilityEvaluator,
    EvaluationDimension,
    MarketFitEvaluator,
    ROIEvaluator,
    ScalabilityEvaluator,
    SMARTVFramework,
    TechnologyMaturityEvaluator,
    ValueCreationEvaluator,
)
from evaluation.weight_config import CompanyStage, WeightConfigManager


class TestScalabilityEvaluator(unittest.TestCase):
    """可擴展性評估器測試"""

    def setUp(self):
        self.evaluator = ScalabilityEvaluator()

    def test_high_scalability(self):
        """測試高可擴展性評估"""
        data = {
            "microservices": True,
            "containerized": True,
            "cloud_native": True,
            "growth_rate": 100,
            "current_rps": 100,
            "max_rps": 1000,
            "auto_scaling": True,
            "load_balancer": True,
            "stateless": True
        }
        result = self.evaluator.evaluate(data)
        self.assertGreaterEqual(result.score, 8.0)

    def test_low_scalability(self):
        """測試低可擴展性評估"""
        data = {
            "microservices": False,
            "containerized": False,
            "cloud_native": False,
            "growth_rate": 5,
            "current_rps": 900,
            "max_rps": 1000,
            "auto_scaling": False,
            "load_balancer": False
        }
        result = self.evaluator.evaluate(data)
        self.assertLess(result.score, 5.0)


class TestMarketFitEvaluator(unittest.TestCase):
    """市場適配度評估器測試"""

    def setUp(self):
        self.evaluator = MarketFitEvaluator()

    def test_growing_market(self):
        """測試成長市場評估"""
        data = {
            "user_needs_score": 9,
            "market_maturity": "growing",
            "competitor_count": 3,
            "differentiation_level": "high",
            "som": 100_000_000
        }
        result = self.evaluator.evaluate(data)
        self.assertGreaterEqual(result.score, 7.0)

    def test_declining_market(self):
        """測試衰退市場評估"""
        data = {
            "user_needs_score": 4,
            "market_maturity": "declining",
            "competitor_count": 20,
            "differentiation_level": "low",
            "som": 500_000
        }
        result = self.evaluator.evaluate(data)
        self.assertLess(result.score, 5.0)


class TestAchievabilityEvaluator(unittest.TestCase):
    """可實現性評估器測試"""

    def setUp(self):
        self.evaluator = AchievabilityEvaluator()

    def test_high_achievability(self):
        """測試高可實現性"""
        data = {
            "skill_coverage": 90,
            "experience_years": 7,
            "budget_adequate": True,
            "timeline_realistic": True,
            "buffer_percentage": 25,
            "risk_level": "low",
            "mitigation_plans": ["Plan A", "Plan B"],
            "resource_availability_score": 9
        }
        result = self.evaluator.evaluate(data)
        self.assertGreaterEqual(result.score, 8.0)


class TestROIEvaluator(unittest.TestCase):
    """ROI 評估器測試"""

    def setUp(self):
        self.evaluator = ROIEvaluator()

    def test_high_roi(self):
        """測試高 ROI"""
        data = {
            "roi_percentage": 300,
            "payback_months": 6,
            "npv": 1000000,
            "irr": 30,
            "productivity_gain": 50,
            "automation_level": 80
        }
        result = self.evaluator.evaluate(data)
        self.assertGreaterEqual(result.score, 8.0)


class TestTechnologyMaturityEvaluator(unittest.TestCase):
    """技術成熟度評估器測試"""

    def setUp(self):
        self.evaluator = TechnologyMaturityEvaluator()

    def test_mature_technology(self):
        """測試成熟技術"""
        data = {
            "tech_age_years": 10,
            "breaking_changes_yearly": 1,
            "library_count": 50000,
            "community_size": 2000000,
            "enterprise_adoption": 80,
            "documentation_quality": "excellent",
            "avg_onboarding_days": 7
        }
        result = self.evaluator.evaluate(data)
        self.assertGreaterEqual(result.score, 8.0)


class TestValueCreationEvaluator(unittest.TestCase):
    """價值創造評估器測試"""

    def setUp(self):
        self.evaluator = ValueCreationEvaluator()

    def test_high_value_creation(self):
        """測試高價值創造"""
        data = {
            "moat_strength": "very_high",
            "switching_cost": "high",
            "network_effects": True,
            "brand_recognition": 80,
            "customer_loyalty": 85,
            "nps_score": 60,
            "patents": 15,
            "industry_first": True,
            "tech_leadership": True
        }
        result = self.evaluator.evaluate(data)
        self.assertGreaterEqual(result.score, 8.0)


class TestSMARTVFramework(unittest.TestCase):
    """SMART-V 框架整合測試"""

    def setUp(self):
        self.framework = SMARTVFramework()

    def test_full_evaluation(self):
        """測試完整評估流程"""
        data = {
            "scalability": {
                "microservices": True,
                "containerized": True,
                "growth_rate": 50,
                "auto_scaling": True
            },
            "market_fit": {
                "user_needs_score": 8,
                "market_maturity": "growing",
                "competitor_count": 5
            },
            "achievability": {
                "skill_coverage": 75,
                "experience_years": 4,
                "budget_adequate": True
            },
            "roi": {
                "roi_percentage": 150,
                "payback_months": 12
            },
            "technology_maturity": {
                "tech_age_years": 5,
                "library_count": 10000
            },
            "value_creation": {
                "moat_strength": "medium",
                "brand_recognition": 60
            }
        }

        result = self.framework.evaluate("測試專案", data)

        self.assertEqual(result.project_name, "測試專案")
        self.assertIn(result.overall_grade, ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"])
        self.assertEqual(len(result.scores), 6)
        self.assertGreater(result.weighted_total, 0)

    def test_startup_weights(self):
        """測試初創公司權重配置"""
        weights = self.framework.get_startup_weights()

        # 初創公司應重視市場適配和 ROI
        self.assertEqual(weights[EvaluationDimension.MARKET_FIT], 0.25)
        self.assertEqual(weights[EvaluationDimension.ROI], 0.25)
        # 技術成熟度權重較低
        self.assertEqual(weights[EvaluationDimension.TECHNOLOGY_MATURITY], 0.05)

    def test_enterprise_weights(self):
        """測試成熟企業權重配置"""
        weights = self.framework.get_enterprise_weights()

        # 成熟企業重視可擴展性和技術成熟度
        self.assertEqual(weights[EvaluationDimension.SCALABILITY], 0.25)
        self.assertEqual(weights[EvaluationDimension.TECHNOLOGY_MATURITY], 0.20)
        # 可實現性權重較低（有資源）
        self.assertEqual(weights[EvaluationDimension.ACHIEVABILITY], 0.05)


class TestWeightConfigManager(unittest.TestCase):
    """權重配置管理器測試"""

    def setUp(self):
        self.manager = WeightConfigManager()

    def test_preset_weights(self):
        """測試預設權重獲取"""
        startup_weights = self.manager.get_preset_weights(CompanyStage.STARTUP)
        self.assertEqual(len(startup_weights), 6)
        self.assertAlmostEqual(sum(startup_weights.values()), 1.0, places=2)

    def test_create_custom_profile(self):
        """測試創建自定義配置"""
        weights = {
            "scalability": 0.20,
            "market_fit": 0.20,
            "achievability": 0.15,
            "roi": 0.20,
            "technology_maturity": 0.10,
            "value_creation": 0.15
        }

        profile = self.manager.create_custom_profile(
            name="custom_test",
            stage=CompanyStage.GROWTH,
            weights=weights,
            description="測試配置"
        )

        self.assertEqual(profile.name, "custom_test")
        self.assertEqual(profile.stage, CompanyStage.GROWTH)

    def test_suggest_weights(self):
        """測試權重建議"""
        priorities = {
            "scalability": 3,
            "market_fit": 5,
            "achievability": 2,
            "roi": 4,
            "technology_maturity": 1,
            "value_creation": 3
        }

        suggested = self.manager.suggest_weights(priorities)

        self.assertEqual(len(suggested), 6)
        self.assertAlmostEqual(sum(suggested.values()), 1.0, places=5)
        # 優先級 5 的 market_fit 應該有較高權重
        self.assertGreater(suggested["market_fit"], suggested["technology_maturity"])


class TestEvaluationReportGenerator(unittest.TestCase):
    """報告生成器測試"""

    def setUp(self):
        self.framework = SMARTVFramework()
        self.generator = EvaluationReportGenerator()

        # 準備測試數據
        self.test_data = {
            "scalability": {"microservices": True, "growth_rate": 50},
            "market_fit": {"user_needs_score": 7},
            "achievability": {"skill_coverage": 70},
            "roi": {"roi_percentage": 100},
            "technology_maturity": {"tech_age_years": 5},
            "value_creation": {"moat_strength": "medium"}
        }
        self.result = self.framework.evaluate("報告測試專案", self.test_data)

    def test_markdown_report(self):
        """測試 Markdown 報告生成"""
        report = self.generator.generate(self.result, "markdown")

        self.assertIn("SMART-V 評估報告", report)
        self.assertIn("報告測試專案", report)
        self.assertIn("總體評分", report)
        self.assertIn("維度評分", report)

    def test_text_report(self):
        """測試純文字報告生成"""
        report = self.generator.generate(self.result, "text")

        self.assertIn("SMART-V", report)
        self.assertIn("報告測試專案", report)

    def test_json_report(self):
        """測試 JSON 報告生成"""
        report = self.generator.generate(self.result, "json")

        import json
        data = json.loads(report)
        self.assertEqual(data["project_name"], "報告測試專案")
        self.assertIn("weighted_total", data)

    def test_executive_summary(self):
        """測試執行摘要生成"""
        summary = self.generator.generate_executive_summary(self.result)

        self.assertIn("執行摘要", summary)
        self.assertIn("報告測試專案", summary)


class TestGradeCalculation(unittest.TestCase):
    """等級計算測試"""

    def setUp(self):
        self.framework = SMARTVFramework()

    def test_grade_a_plus(self):
        """測試 A+ 等級"""
        self.assertEqual(self.framework._grade(9.5), "A+")

    def test_grade_b(self):
        """測試 B 等級"""
        self.assertEqual(self.framework._grade(7.0), "B")

    def test_grade_f(self):
        """測試 F 等級"""
        self.assertEqual(self.framework._grade(2.0), "F")


if __name__ == '__main__':
    unittest.main(verbosity=2)
