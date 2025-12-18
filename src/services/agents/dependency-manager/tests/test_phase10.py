"""
Phase 10 單元測試 - 實施路徑與行動指南模組測試
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

# 添加模組路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestImplementationPlan(unittest.TestCase):
    """測試實施計劃"""

    def test_import(self):
        """測試模組導入"""
        from implementation.implementation_plan import (
            ImplementationPlan,
        )
        self.assertIsNotNone(ImplementationPlan)

    def test_create_plan(self):
        """測試創建實施計劃"""
        from implementation.implementation_plan import ImplementationPlan

        plan = ImplementationPlan("測試專案")
        self.assertEqual(plan.project_name, "測試專案")
        self.assertEqual(len(plan.phases), 4)

    def test_default_phases(self):
        """測試預設階段"""
        from implementation.implementation_plan import ImplementationPlan, PhaseType

        plan = ImplementationPlan("測試專案")

        # 檢查 4 個階段
        self.assertEqual(len(plan.phases), 4)

        # 檢查階段類型
        phase_types = [p.phase_type for p in plan.phases]
        self.assertIn(PhaseType.FOUNDATION, phase_types)
        self.assertIn(PhaseType.CAPABILITY, phase_types)
        self.assertIn(PhaseType.SCALING, phase_types)
        self.assertIn(PhaseType.OPTIMIZATION, phase_types)

    def test_phase_duration(self):
        """測試階段持續時間"""
        from implementation.implementation_plan import ImplementationPlan

        plan = ImplementationPlan("測試專案")

        # 每個階段應該是 3 個月
        for phase in plan.phases:
            self.assertEqual(phase.duration_months(), 3)

    def test_task_creation(self):
        """測試任務創建"""
        from implementation.implementation_plan import Task, TaskPriority, TaskStatus

        task = Task(
            id="task_1",
            name="測試任務",
            description="這是一個測試任務",
            priority=TaskPriority.HIGH,
            estimated_hours=40
        )

        self.assertEqual(task.name, "測試任務")
        self.assertEqual(task.status, TaskStatus.NOT_STARTED)
        self.assertEqual(task.priority, TaskPriority.HIGH)

    def test_task_progress(self):
        """測試任務進度"""
        from implementation.implementation_plan import Task

        task = Task(
            id="task_1",
            name="測試任務",
            description="測試",
            estimated_hours=40,
            actual_hours=20
        )

        self.assertEqual(task.progress_percentage(), 50.0)

    def test_milestone_creation(self):
        """測試里程碑創建"""
        from implementation.implementation_plan import Milestone

        milestone = Milestone(
            id="ms_1",
            name="里程碑 1",
            description="測試里程碑",
            target_date=datetime.now() + timedelta(days=30),
            deliverables=["交付物 1", "交付物 2"]
        )

        self.assertEqual(milestone.name, "里程碑 1")
        self.assertFalse(milestone.completed)

    def test_overall_progress(self):
        """測試整體進度"""
        from implementation.implementation_plan import ImplementationPlan

        plan = ImplementationPlan("測試專案")

        # 初始進度應該是 0
        self.assertEqual(plan.overall_progress(), 0.0)

    def test_generate_report(self):
        """測試報告生成"""
        from implementation.implementation_plan import ImplementationPlan

        plan = ImplementationPlan("測試專案")

        # Markdown 報告
        md_report = plan.generate_report("markdown")
        self.assertIn("測試專案", md_report)
        self.assertIn("基礎建設期", md_report)

        # Text 報告
        text_report = plan.generate_report("text")
        self.assertIn("測試專案", text_report)


class TestSuccessMetrics(unittest.TestCase):
    """測試成功指標追蹤器"""

    def test_import(self):
        """測試模組導入"""
        from implementation.success_metrics import (
            SuccessMetricsTracker,
        )
        self.assertIsNotNone(SuccessMetricsTracker)

    def test_create_tracker(self):
        """測試創建追蹤器"""
        from implementation.success_metrics import SuccessMetricsTracker

        tracker = SuccessMetricsTracker()

        # 應該有預設指標
        self.assertGreater(len(tracker.technical_metrics), 0)
        self.assertGreater(len(tracker.business_metrics), 0)
        self.assertGreater(len(tracker.organizational_metrics), 0)

    def test_default_technical_metrics(self):
        """測試預設技術指標"""
        from implementation.success_metrics import SuccessMetricsTracker

        tracker = SuccessMetricsTracker()

        self.assertIn("code_quality", tracker.technical_metrics)
        self.assertIn("performance", tracker.technical_metrics)
        self.assertIn("tech_debt_ratio", tracker.technical_metrics)
        self.assertIn("test_coverage", tracker.technical_metrics)

    def test_default_business_metrics(self):
        """測試預設商業指標"""
        from implementation.success_metrics import SuccessMetricsTracker

        tracker = SuccessMetricsTracker()

        self.assertIn("cac", tracker.business_metrics)
        self.assertIn("ltv", tracker.business_metrics)
        self.assertIn("mrr_growth", tracker.business_metrics)

    def test_record_value(self):
        """測試記錄指標值"""
        from implementation.success_metrics import MetricCategory, SuccessMetricsTracker

        tracker = SuccessMetricsTracker()

        result = tracker.record_value(
            MetricCategory.TECHNICAL,
            "code_quality",
            85.0,
            "測試記錄"
        )

        self.assertTrue(result)
        self.assertEqual(
            tracker.technical_metrics["code_quality"].current_value(),
            85.0
        )

    def test_metric_status(self):
        """測試指標狀態"""
        from implementation.success_metrics import MetricStatus, TechnicalMetric

        metric = TechnicalMetric(
            id="test",
            name="測試指標",
            description="測試",
            unit="分",
            target_value=80,
            warning_threshold=60,
            critical_threshold=40,
            higher_is_better=True
        )

        # 添加達標值
        metric.add_data_point(85)
        self.assertEqual(metric.get_status(), MetricStatus.ON_TARGET)

        # 創建新指標測試警告狀態
        metric2 = TechnicalMetric(
            id="test2",
            name="測試指標2",
            description="測試",
            unit="分",
            target_value=80,
            warning_threshold=60,
            critical_threshold=40,
            higher_is_better=True
        )
        metric2.add_data_point(65)
        self.assertEqual(metric2.get_status(), MetricStatus.WARNING)

    def test_dashboard_summary(self):
        """測試儀表板摘要"""
        from implementation.success_metrics import SuccessMetricsTracker

        tracker = SuccessMetricsTracker()
        summary = tracker.get_dashboard_summary()

        self.assertIn("technical", summary)
        self.assertIn("business", summary)
        self.assertIn("organizational", summary)

    def test_generate_report(self):
        """測試生成報告"""
        from implementation.success_metrics import SuccessMetricsTracker

        tracker = SuccessMetricsTracker()

        # Markdown 報告
        md_report = tracker.generate_report("markdown")
        self.assertIn("成功指標追蹤報告", md_report)
        self.assertIn("技術指標", md_report)

        # Text 報告
        text_report = tracker.generate_report("text")
        self.assertIn("成功指標追蹤報告", text_report)


class TestActionGuide(unittest.TestCase):
    """測試行動指南"""

    def test_import(self):
        """測試模組導入"""
        from implementation.action_guide import (
            ActionGuide,
        )
        self.assertIsNotNone(ActionGuide)

    def test_create_guide(self):
        """測試創建行動指南"""
        from implementation.action_guide import ActionGuide

        guide = ActionGuide()

        # 應該有預設建議
        self.assertGreater(len(guide.recommendations), 0)

    def test_success_keys(self):
        """測試成功關鍵要素"""
        from implementation.action_guide import ActionGuide

        guide = ActionGuide()

        self.assertEqual(len(guide.SUCCESS_KEYS), 5)

        key_ids = [k['id'] for k in guide.SUCCESS_KEYS]
        self.assertIn('understanding', key_ids)
        self.assertIn('quantitative', key_ids)
        self.assertIn('combination', key_ids)
        self.assertIn('agility', key_ids)
        self.assertIn('risk_control', key_ids)

    def test_strategy_evaluator(self):
        """測試策略評估器"""
        from implementation.action_guide import StrategyEvaluator

        evaluator = StrategyEvaluator()

        # 評估各標準
        evaluator.evaluate_criterion('understanding', 8.0, "良好理解")
        evaluator.evaluate_criterion('quantitative', 7.0, "有量化評估")
        evaluator.evaluate_criterion('combination', 9.0, "優秀組合策略")
        evaluator.evaluate_criterion('agility', 6.0, "需要加強敏捷性")
        evaluator.evaluate_criterion('risk_control', 7.5, "風險管控良好")

        # 計算總分
        overall = evaluator.calculate_overall_score()
        self.assertGreater(overall, 0)

        # 獲取等級
        grade = evaluator.get_grade()
        self.assertIn(grade, ['A', 'B', 'C', 'D', 'F'])

    def test_action_item_creation(self):
        """測試行動項目創建"""
        from implementation.action_guide import ActionItem, ActionPriority, ActionStatus

        action = ActionItem(
            id="action_1",
            title="測試行動",
            description="這是一個測試行動項目",
            priority=ActionPriority.HIGH,
            estimated_effort="2 週"
        )

        self.assertEqual(action.title, "測試行動")
        self.assertEqual(action.status, ActionStatus.PENDING)
        self.assertEqual(action.priority, ActionPriority.HIGH)

    def test_recommendation_creation(self):
        """測試建議創建"""
        from implementation.action_guide import ActionPriority, Recommendation, RecommendationType

        rec = Recommendation(
            id="rec_1",
            type=RecommendationType.STRATEGY,
            title="測試建議",
            description="這是一個測試建議",
            rationale="測試原因",
            expected_impact="提升效率 20%",
            effort_level="medium",
            priority=ActionPriority.HIGH
        )

        self.assertEqual(rec.title, "測試建議")
        self.assertEqual(rec.type, RecommendationType.STRATEGY)

    def test_get_recommendations_by_priority(self):
        """測試根據優先級獲取建議"""
        from implementation.action_guide import ActionGuide, ActionPriority

        guide = ActionGuide()

        high_priority = guide.get_recommendations_by_priority(ActionPriority.HIGH)
        self.assertGreater(len(high_priority), 0)

    def test_generate_summary_report(self):
        """測試生成總結報告"""
        from implementation.action_guide import ActionGuide

        guide = ActionGuide()

        # Markdown 報告
        md_report = guide.generate_summary_report("markdown")
        self.assertIn("總結與行動指南", md_report)
        self.assertIn("深度理解", md_report)
        self.assertIn("量化評估", md_report)

        # Text 報告
        text_report = guide.generate_summary_report("text")
        self.assertIn("總結與行動指南", text_report)

    def test_to_dict(self):
        """測試轉換為字典"""
        from implementation.action_guide import ActionGuide

        guide = ActionGuide()
        data = guide.to_dict()

        self.assertIn('success_keys', data)
        self.assertIn('recommendations', data)
        self.assertIn('strategy_evaluation', data)


class TestIntegration(unittest.TestCase):
    """整合測試"""

    def test_full_workflow(self):
        """測試完整工作流程"""
        from implementation.action_guide import ActionGuide
        from implementation.implementation_plan import ImplementationPlan
        from implementation.success_metrics import MetricCategory, SuccessMetricsTracker

        # 1. 創建實施計劃
        plan = ImplementationPlan("依賴管理代理專案")
        self.assertEqual(len(plan.phases), 4)

        # 2. 設置成功指標追蹤
        tracker = SuccessMetricsTracker()
        tracker.record_value(MetricCategory.TECHNICAL, "code_quality", 85.0)
        tracker.record_value(MetricCategory.BUSINESS, "ltv", 450.0)

        # 3. 生成行動指南
        guide = ActionGuide()
        guide.evaluator.evaluate_criterion('understanding', 8.0)
        guide.evaluator.evaluate_criterion('quantitative', 7.5)

        # 4. 驗證整合
        self.assertGreater(plan.overall_progress(), -1)  # 進度 >= 0
        self.assertGreater(len(tracker.technical_metrics), 0)
        self.assertGreater(guide.evaluator.calculate_overall_score(), 0)

        # 5. 生成報告
        plan_report = plan.generate_report("markdown")
        metrics_report = tracker.generate_report("markdown")
        action_report = guide.generate_summary_report("markdown")

        self.assertIn("依賴管理代理專案", plan_report)
        self.assertIn("成功指標追蹤報告", metrics_report)
        self.assertIn("總結與行動指南", action_report)


if __name__ == '__main__':
    unittest.main()
