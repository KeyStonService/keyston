"""
Phase 8 單元測試
Tests for Advanced Prompt Combination Strategy Modules
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from combination.combination_templates import (
    CombinationTemplateManager,
    CompanyStage,
)
from combination.core_satellite import (
    CoreSatelliteArchitecture,
)
from combination.dynamic_adjuster import (
    AdjustmentTrigger,
    DynamicAdjuster,
)
from combination.quarterly_review import (
    QuarterlyReviewEngine,
    ReviewCategory,
    ReviewStatus,
)


class TestCoreSatelliteArchitecture(unittest.TestCase):
    """核心-衛星架構測試"""

    def setUp(self):
        self.architecture = CoreSatelliteArchitecture()

    def test_list_presets(self):
        """測試列出預設配置"""
        presets = self.architecture.list_presets()
        self.assertIn('steady_growth', presets)
        self.assertIn('rapid_monetization', presets)
        self.assertIn('tech_leadership', presets)

    def test_get_preset_steady_growth(self):
        """測試獲取穩健成長型配置"""
        config = self.architecture.get_preset('steady_growth')
        self.assertIsNotNone(config)
        self.assertEqual(config.name, "穩健成長型")
        self.assertEqual(config.core_allocation.allocation_percentage, 70.0)

    def test_configuration_validation(self):
        """測試配置驗證"""
        config = self.architecture.get_preset('steady_growth')
        self.assertTrue(config.is_valid())
        self.assertAlmostEqual(config.get_total_allocation(), 100.0, places=1)

    def test_recommend_configuration_startup(self):
        """測試初創公司推薦"""
        config = self.architecture.recommend_configuration('startup', 'high', 'low')
        self.assertEqual(config.name, "快速變現型")

    def test_recommend_configuration_tech_focus(self):
        """測試技術導向推薦"""
        config = self.architecture.recommend_configuration('growth', 'medium', 'high')
        self.assertEqual(config.name, "技術領先型")

    def test_analyze_configuration(self):
        """測試配置分析"""
        config = self.architecture.get_preset('steady_growth')
        analysis = self.architecture.analyze_configuration(config)

        self.assertEqual(analysis['name'], "穩健成長型")
        self.assertTrue(analysis['is_valid'])
        self.assertEqual(analysis['core_percentage'], 70.0)
        self.assertEqual(analysis['satellite_count'], 2)


class TestCombinationTemplateManager(unittest.TestCase):
    """組合範本管理器測試"""

    def setUp(self):
        self.manager = CombinationTemplateManager()

    def test_list_templates(self):
        """測試列出範本"""
        templates = self.manager.list_templates()
        self.assertTrue(len(templates) > 0)
        self.assertIn('id', templates[0])
        self.assertIn('name', templates[0])

    def test_get_template(self):
        """測試獲取範本"""
        template = self.manager.get_template('steady_a')
        self.assertIsNotNone(template)
        self.assertEqual(template.name, '穩健成長型 A')

    def test_template_allocation(self):
        """測試範本分配總和"""
        template = self.manager.get_template('steady_a')
        total = template.get_total_allocation()
        self.assertAlmostEqual(total, 100.0, places=1)

    def test_recommend_template(self):
        """測試範本推薦"""
        template = self.manager.recommend_template(CompanyStage.STARTUP, 'growth')
        self.assertIsNotNone(template)


class TestDynamicAdjuster(unittest.TestCase):
    """動態調整器測試"""

    def setUp(self):
        self.adjuster = DynamicAdjuster()

    def test_register_kpi(self):
        """測試註冊 KPI"""
        self.adjuster.register_kpi('revenue', 1000000, 800000, 'USD')
        analysis = self.adjuster.analyze_kpis()

        self.assertEqual(len(analysis['metrics']), 1)
        self.assertAlmostEqual(analysis['metrics'][0]['deviation'], -20.0, places=1)

    def test_kpi_on_track(self):
        """測試 KPI 達標判斷"""
        self.adjuster.register_kpi('growth', 100, 95)  # 5% 偏差
        analysis = self.adjuster.analyze_kpis()

        self.assertTrue(analysis['metrics'][0]['on_track'])

    def test_kpi_trigger_adjustment(self):
        """測試 KPI 觸發調整"""
        self.adjuster.register_kpi('revenue', 100, 50)  # 50% 偏差
        analysis = self.adjuster.analyze_kpis()

        self.assertTrue(analysis['trigger_adjustment'])

    def test_evaluate_market(self):
        """測試市場評估"""
        result = self.adjuster.evaluate_market(
            satisfaction=55,
            competitor_moves=['新產品', '降價'],
            trends=['技術革新']
        )

        self.assertIn('severity_score', result)
        self.assertTrue(result['severity_score'] > 0)

    def test_generate_recommendations(self):
        """測試生成建議"""
        kpi = {'trigger_adjustment': True, 'overall_deviation': -25}
        market = {'trigger_adjustment': False, 'severity_score': 20}
        financial = {'trigger_adjustment': False}

        recs = self.adjuster.generate_recommendations(kpi, market, financial)
        self.assertTrue(len(recs) > 0)
        self.assertEqual(recs[0].trigger, AdjustmentTrigger.KPI_DEVIATION)


class TestQuarterlyReviewEngine(unittest.TestCase):
    """季度審查引擎測試"""

    def setUp(self):
        self.engine = QuarterlyReviewEngine()

    def test_create_review(self):
        """測試創建審查"""
        review = self.engine.create_review('2024Q1')

        self.assertEqual(review.quarter, '2024Q1')
        self.assertEqual(review.status, ReviewStatus.SCHEDULED)

    def test_add_review_item(self):
        """測試添加審查項目"""
        self.engine.create_review('2024Q2')
        self.engine.add_review_item(
            '2024Q2',
            ReviewCategory.FINANCIAL_PERFORMANCE,
            'ROI',
            100.0,
            85.0,
            '%'
        )

        review = self.engine.get_review('2024Q2')
        self.assertEqual(len(review.items), 1)
        self.assertEqual(review.items[0].metric_name, 'ROI')

    def test_complete_review(self):
        """測試完成審查"""
        self.engine.create_review('2024Q3')
        self.engine.add_review_item('2024Q3', ReviewCategory.MARKET_FEEDBACK, '滿意度', 80, 70, '%')

        review = self.engine.complete_review('2024Q3')

        self.assertEqual(review.status, ReviewStatus.COMPLETED)
        self.assertTrue(len(review.recommendations) > 0)

    def test_generate_markdown_report(self):
        """測試生成 Markdown 報告"""
        self.engine.create_review('2024Q4')
        self.engine.add_review_item('2024Q4', ReviewCategory.INTERNAL_CAPABILITY, '技能成長', 15, 12, '%')
        self.engine.complete_review('2024Q4')

        report = self.engine.generate_report('2024Q4', 'markdown')

        self.assertIn('# 季度審查報告', report)
        self.assertIn('2024Q4', report)

    def test_list_reviews(self):
        """測試列出審查"""
        self.engine.create_review('2025Q1')
        reviews = self.engine.list_reviews()

        self.assertTrue(len(reviews) > 0)
        self.assertIn('quarter', reviews[0])


class TestIntegration(unittest.TestCase):
    """整合測試"""

    def test_full_workflow(self):
        """測試完整工作流程"""
        # 1. 選擇架構配置
        architecture = CoreSatelliteArchitecture()
        config = architecture.recommend_configuration('startup', 'high', 'low')

        # 2. 獲取範本
        template_manager = CombinationTemplateManager()
        template = template_manager.recommend_template(CompanyStage.STARTUP, 'monetization')

        # 3. 設置動態調整
        adjuster = DynamicAdjuster()
        adjuster.register_kpi('revenue', 100000, 80000)
        adjuster.register_kpi('growth', 30, 25)

        # 4. 創建季度審查
        review_engine = QuarterlyReviewEngine()
        review_engine.create_review('2025Q1')
        review_engine.add_review_item('2025Q1', ReviewCategory.FINANCIAL_PERFORMANCE, 'ROI', 100, 90, '%')

        # 驗證工作流程
        self.assertIsNotNone(config)
        self.assertIsNotNone(template)

        kpi_analysis = adjuster.analyze_kpis()
        self.assertTrue(len(kpi_analysis['metrics']) == 2)

        review = review_engine.get_review('2025Q1')
        self.assertEqual(len(review.items), 1)


if __name__ == '__main__':
    unittest.main()
