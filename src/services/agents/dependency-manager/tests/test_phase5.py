"""
Phase 5 單元測試 - 策略模組測試

測試：
- 案例學習引擎
- 策略顧問
- 資源優化器
- 演進追蹤器

Copyright (c) 2024 SynergyMesh
MIT License
"""

import os

# 模擬導入（測試時需要確保路徑正確）
import sys
import unittest
from datetime import datetime

# 添加 src 目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategy.case_study_engine import (
    CaseStudy,
    CaseStudyEngine,
    DevelopmentStrategy,
    EvolutionPhase,
    PhaseType,
)
from strategy.evolution_tracker import (
    DevelopmentPhase,
    EvolutionRoadmap,
    EvolutionTracker,
    MaturityLevel,
    PhaseTransition,
    ProjectMaturity,
)
from strategy.resource_optimizer import (
    AllocationStrategy,
    BudgetAllocation,
    OptimizationResult,
    ResourceOptimizer,
    TeamAllocation,
)
from strategy.strategy_advisor import (
    CapabilityLevel,
    MarketMaturity,
    MarketTimingAnalysis,
    StrategicPriority,
    StrategyAdvisor,
    StrategyRecommendation,
    TechCapability,
    TechCapabilityAssessment,
)


class TestCaseStudyEngine(unittest.TestCase):
    """案例學習引擎測試"""

    def setUp(self):
        """設置測試"""
        self.engine = CaseStudyEngine()

    def test_builtin_cases_loaded(self):
        """測試內建案例載入"""
        cases = self.engine.list_cases()
        self.assertIn('netflix', cases)
        self.assertIn('shopify', cases)
        self.assertIn('stripe', cases)
        self.assertGreaterEqual(len(cases), 3)

    def test_get_case_netflix(self):
        """測試獲取 Netflix 案例"""
        case = self.engine.get_case('netflix')
        self.assertIsNotNone(case)
        self.assertEqual(case.company_name, "Netflix")
        self.assertEqual(case.founding_year, 1997)
        self.assertGreater(len(case.evolution_phases), 0)
        self.assertGreater(len(case.lessons_learned), 0)

    def test_get_case_shopify(self):
        """測試獲取 Shopify 案例"""
        case = self.engine.get_case('shopify')
        self.assertIsNotNone(case)
        self.assertEqual(case.company_name, "Shopify")
        self.assertIn('電子商務', case.industry)

    def test_get_case_stripe(self):
        """測試獲取 Stripe 案例"""
        case = self.engine.get_case('stripe')
        self.assertIsNotNone(case)
        self.assertEqual(case.company_name, "Stripe")
        self.assertIn('支付', case.industry)

    def test_get_nonexistent_case(self):
        """測試獲取不存在的案例"""
        case = self.engine.get_case('nonexistent')
        self.assertIsNone(case)

    def test_find_cases_by_industry(self):
        """測試根據產業查找案例"""
        cases = self.engine.find_cases_by_industry('電商')
        # Shopify 應該匹配
        self.assertGreater(len(cases), 0)

    def test_find_cases_by_strategy(self):
        """測試根據策略查找案例"""
        results = self.engine.find_cases_by_strategy(
            DevelopmentStrategy.COMMERCIAL_ORIENTED
        )
        self.assertGreater(len(results), 0)

        # 結果應該包含案例和階段
        case, phase = results[0]
        self.assertIsInstance(case, CaseStudy)
        self.assertIsInstance(phase, EvolutionPhase)

    def test_evolution_phase_structure(self):
        """測試演進階段結構"""
        case = self.engine.get_case('netflix')
        phase = case.evolution_phases[0]

        self.assertIsInstance(phase.phase_type, PhaseType)
        self.assertIsInstance(phase.strategy, DevelopmentStrategy)
        self.assertIsNotNone(phase.description)
        self.assertGreater(len(phase.key_actions), 0)
        self.assertGreater(len(phase.success_metrics), 0)

    def test_lesson_learned_structure(self):
        """測試學習要點結構"""
        case = self.engine.get_case('netflix')
        lesson = case.lessons_learned[0]

        self.assertIsNotNone(lesson.category)
        self.assertIsNotNone(lesson.title)
        self.assertIsNotNone(lesson.description)
        self.assertGreater(len(lesson.implementation_tips), 0)
        self.assertGreater(len(lesson.common_mistakes), 0)

    def test_get_strategy_sequence(self):
        """測試獲取策略序列"""
        case = self.engine.get_case('netflix')
        sequence = case.get_strategy_sequence()

        self.assertGreater(len(sequence), 0)
        for strategy in sequence:
            self.assertIsInstance(strategy, DevelopmentStrategy)

    def test_analyze_strategy_patterns(self):
        """測試分析策略模式"""
        patterns = self.engine.analyze_strategy_patterns()

        self.assertIn('common_sequences', patterns)
        self.assertIn('strategy_frequency', patterns)
        self.assertIn('phase_duration_avg', patterns)
        self.assertIn('success_factors_frequency', patterns)

        # 應該有策略頻率數據
        self.assertGreater(len(patterns['strategy_frequency']), 0)

    def test_recommend_strategy_sequence(self):
        """測試推薦策略序列"""
        recommendations = self.engine.recommend_strategy_sequence(
            industry='SaaS',
            current_stage=PhaseType.INITIAL,
            resources='moderate'
        )

        self.assertGreater(len(recommendations), 0)
        for rec in recommendations:
            self.assertIn('stage', rec)
            self.assertIn('recommended_strategies', rec)

    def test_generate_report(self):
        """測試生成報告"""
        report = self.engine.generate_report('netflix')

        self.assertIn('Netflix', report)
        self.assertIn('案例分析報告', report)
        self.assertIn('發展演進', report)
        self.assertIn('學習要點', report)

    def test_add_custom_case(self):
        """測試添加自定義案例"""
        custom_case = CaseStudy(
            company_name="TestCo",
            industry="測試產業",
            description="測試案例",
            founding_year=2020,
            evolution_phases=[],
            lessons_learned=[],
            key_success_factors=["測試因素"],
            technology_stack=["Python"],
            business_model="測試模式",
            market_position="測試定位"
        )

        self.engine.add_case('testco', custom_case)

        retrieved = self.engine.get_case('testco')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.company_name, "TestCo")


class TestStrategyAdvisor(unittest.TestCase):
    """策略顧問測試"""

    def setUp(self):
        """設置測試"""
        self.advisor = StrategyAdvisor()

    def test_assess_capabilities(self):
        """測試能力評估"""
        team_profile = {
            'skills': {
                'backend': {
                    'level': 'advanced',
                    'team_members': 5,
                    'experience_years': 3.0,
                    'certifications': ['AWS'],
                    'tools': {'Python': 'expert'}
                },
                'frontend': {
                    'level': 'intermediate',
                    'team_members': 3,
                    'experience_years': 2.0
                }
            },
            'infrastructure': {
                'has_cloud': True,
                'has_ci_cd': True,
                'has_monitoring': True
            },
            'process': {
                'has_agile': True,
                'has_code_review': True,
                'has_testing': True
            },
            'culture': {
                'innovation_mindset': 0.7,
                'customer_focus': 0.8
            }
        }

        assessment = self.advisor.assess_capabilities(team_profile)

        self.assertIsInstance(assessment, TechCapabilityAssessment)
        self.assertGreater(assessment.get_overall_score(), 0)
        self.assertIn('backend', assessment.capabilities)

    def test_capability_scoring(self):
        """測試能力分數計算"""
        cap = TechCapability(
            name='test',
            level=CapabilityLevel.ADVANCED,
            team_members=5,
            experience_years=3.0,
            certifications=['Cert1', 'Cert2']
        )

        score = cap.get_score()
        self.assertGreater(score, 70)  # Advanced 基礎分 80
        self.assertLessEqual(score, 100)

    def test_analyze_market_timing(self):
        """測試市場時機分析"""
        analysis = self.advisor.analyze_market_timing('saas')

        self.assertIsInstance(analysis, MarketTimingAnalysis)
        self.assertEqual(analysis.market_name, 'saas')
        self.assertGreater(analysis.timing_score, 0)
        self.assertIsInstance(analysis.maturity, MarketMaturity)

    def test_market_timing_recommendation(self):
        """測試市場進入建議"""
        analysis = self.advisor.analyze_market_timing('ai_ml')
        recommendation = analysis.get_recommendation()

        self.assertIsInstance(recommendation, str)
        self.assertGreater(len(recommendation), 0)

    def test_generate_recommendations(self):
        """測試生成策略推薦"""
        # 創建評估數據
        capabilities = {
            'engineering': TechCapability(
                name='engineering',
                level=CapabilityLevel.ADVANCED,
                team_members=10,
                experience_years=5.0
            )
        }

        cap_assessment = TechCapabilityAssessment(
            assessed_at=datetime.now(),
            capabilities=capabilities,
            infrastructure_readiness=0.8,
            process_maturity=0.7,
            culture_alignment=0.75
        )

        market_analysis = self.advisor.analyze_market_timing('saas')

        recommendations = self.advisor.generate_recommendations(
            cap_assessment,
            market_analysis,
            business_goals=['growth', 'innovation'],
            constraints={'budget': 1000000}
        )

        self.assertGreater(len(recommendations), 0)
        for rec in recommendations:
            self.assertIsInstance(rec, StrategyRecommendation)
            self.assertIsInstance(rec.priority, StrategicPriority)

    def test_strategy_report_generation(self):
        """測試策略報告生成"""
        capabilities = {
            'engineering': TechCapability(
                name='engineering',
                level=CapabilityLevel.INTERMEDIATE,
                team_members=5,
                experience_years=2.0
            )
        }

        cap = TechCapabilityAssessment(
            assessed_at=datetime.now(),
            capabilities=capabilities,
            infrastructure_readiness=0.6,
            process_maturity=0.5,
            culture_alignment=0.6
        )

        market = self.advisor.analyze_market_timing('fintech')
        recs = self.advisor.generate_recommendations(
            cap, market, ['growth']
        )

        report = self.advisor.generate_report(cap, market, recs)

        self.assertIn('策略顧問報告', report)
        self.assertIn('技術能力評估', report)
        self.assertIn('市場時機分析', report)


class TestResourceOptimizer(unittest.TestCase):
    """資源優化器測試"""

    def setUp(self):
        """設置測試"""
        self.optimizer = ResourceOptimizer()

    def test_optimize_budget_balanced(self):
        """測試平衡策略預算優化"""
        allocation = self.optimizer.optimize_budget(
            total_budget=1000000,
            strategy=AllocationStrategy.BALANCED
        )

        self.assertIsInstance(allocation, BudgetAllocation)
        self.assertEqual(allocation.total_budget, 1000000)
        self.assertGreater(len(allocation.allocations), 0)

        # 確認總和等於總預算
        total = sum(cat.amount for cat in allocation.allocations.values())
        self.assertAlmostEqual(total, 1000000, places=0)

    def test_optimize_budget_growth_focused(self):
        """測試增長導向策略"""
        allocation = self.optimizer.optimize_budget(
            total_budget=500000,
            strategy=AllocationStrategy.GROWTH_FOCUSED
        )

        self.assertEqual(allocation.strategy, AllocationStrategy.GROWTH_FOCUSED)

        # 增長導向應該有較多行銷預算
        if 'marketing' in allocation.allocations:
            marketing_ratio = allocation.allocations['marketing'].amount / allocation.total_budget
            self.assertGreater(marketing_ratio, 0.2)

    def test_optimize_budget_with_constraints(self):
        """測試帶約束的預算優化"""
        allocation = self.optimizer.optimize_budget(
            total_budget=1000000,
            strategy=AllocationStrategy.BALANCED,
            constraints={
                'marketing': (200000, 300000)  # 行銷限制在 200K-300K
            }
        )

        if 'marketing' in allocation.allocations:
            marketing = allocation.allocations['marketing'].amount
            self.assertGreaterEqual(marketing, 200000)
            self.assertLessEqual(marketing, 350000)  # 允許一些調整

    def test_optimize_team_startup(self):
        """測試創業階段團隊優化"""
        team = self.optimizer.optimize_team(
            target_headcount=10,
            budget_constraint=1200000,
            stage='startup'
        )

        self.assertIsInstance(team, TeamAllocation)
        self.assertGreater(team.total_headcount, 0)
        self.assertLessEqual(team.total_cost, 1200000)

        # 創業階段應有關鍵角色
        critical = team.get_by_criticality('critical')
        self.assertGreater(len(critical), 0)

    def test_optimize_team_enterprise(self):
        """測試企業階段團隊優化"""
        team = self.optimizer.optimize_team(
            target_headcount=50,
            budget_constraint=8000000,
            stage='enterprise'
        )

        self.assertIsInstance(team, TeamAllocation)
        self.assertGreater(team.total_headcount, 10)

        # 企業階段應有更多角色
        self.assertGreater(len(team.roles), 4)

    def test_team_hiring_plan(self):
        """測試招聘計畫生成"""
        team = self.optimizer.optimize_team(
            target_headcount=15,
            budget_constraint=2000000,
            stage='growth'
        )

        self.assertGreater(len(team.hiring_plan), 0)

        # 招聘計畫應按優先級排序
        priorities = [h['priority'] for h in team.hiring_plan]
        self.assertEqual(priorities, sorted(priorities))

    def test_generate_optimization(self):
        """測試完整優化方案生成"""
        result = self.optimizer.generate_optimization(
            total_budget=2000000,
            target_headcount=20,
            strategy=AllocationStrategy.BALANCED,
            stage='growth',
            business_goals=['growth', 'efficiency']
        )

        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.budget_allocation, BudgetAllocation)
        self.assertIsInstance(result.team_allocation, TeamAllocation)
        self.assertGreater(result.projected_roi, 0)
        self.assertGreater(result.payback_months, 0)
        self.assertLessEqual(result.risk_score, 100)
        self.assertGreater(len(result.recommendations), 0)

    def test_sensitivity_analysis(self):
        """測試敏感度分析"""
        result = self.optimizer.generate_optimization(
            total_budget=1000000,
            target_headcount=10,
            strategy=AllocationStrategy.BALANCED
        )

        sensitivity = result.sensitivity_analysis
        self.assertIn('budget_sensitivity', sensitivity)
        self.assertIn('headcount_sensitivity', sensitivity)
        self.assertIn('market_scenarios', sensitivity)

    def test_resource_report_generation(self):
        """測試資源優化報告生成"""
        result = self.optimizer.generate_optimization(
            total_budget=1500000,
            target_headcount=15
        )

        report = self.optimizer.generate_report(result)

        self.assertIn('資源優化報告', report)
        self.assertIn('預算分配', report)
        self.assertIn('團隊配置', report)
        self.assertIn('投資回報預測', report)


class TestEvolutionTracker(unittest.TestCase):
    """演進追蹤器測試"""

    def setUp(self):
        """設置測試"""
        self.tracker = EvolutionTracker()

    def test_assess_maturity(self):
        """測試成熟度評估"""
        project_data = {
            'technology': {'score': 70, 'evidence': ['CI/CD 已建立']},
            'process': {'score': 60, 'evidence': ['Agile 導入']},
            'team': {'score': 65, 'evidence': ['核心團隊到位']},
            'product': {'score': 55, 'evidence': ['MVP 已發布']},
            'market': {'score': 50, 'evidence': ['初步驗證']},
            'governance': {'score': 45, 'evidence': []},
            'finance': {'score': 40, 'evidence': []},
            'culture': {'score': 60, 'evidence': ['文化建設中']},
            'revenue': 50000,
            'customers': 20,
            'team_size': 8,
            'has_mvp': True
        }

        maturity = self.tracker.assess_maturity(project_data)

        self.assertIsInstance(maturity, ProjectMaturity)
        self.assertIsInstance(maturity.overall_level, MaturityLevel)
        self.assertGreater(maturity.overall_score, 0)
        self.assertLessEqual(maturity.overall_score, 100)
        self.assertIsInstance(maturity.current_phase, DevelopmentPhase)

    def test_maturity_dimensions(self):
        """測試成熟度維度評估"""
        project_data = {
            'technology': {'score': 80},
            'process': {'score': 70}
        }

        maturity = self.tracker.assess_maturity(project_data)

        self.assertGreater(len(maturity.dimensions), 0)

        # 獲取最強/最弱維度
        strongest = maturity.get_strongest_dimension()
        weakest = maturity.get_weakest_dimension()

        self.assertIsInstance(strongest, str)
        self.assertIsInstance(weakest, str)

    def test_phase_detection(self):
        """測試階段檢測"""
        # 初期階段
        early_data = {'has_mvp': False, 'customers': 0}
        early_maturity = self.tracker.assess_maturity(early_data)
        self.assertEqual(early_maturity.current_phase, DevelopmentPhase.IDEATION)

        # 驗證階段
        validation_data = {'has_mvp': True, 'customers': 5, 'revenue': 1000}
        validation_maturity = self.tracker.assess_maturity(validation_data)
        self.assertIn(validation_maturity.current_phase,
                     [DevelopmentPhase.VALIDATION, DevelopmentPhase.EFFICIENCY])

    def test_identify_blockers_accelerators(self):
        """測試識別阻礙和加速因素"""
        project_data = {
            'technology': {'score': 85},  # 高分 - 加速
            'process': {'score': 30},      # 低分 - 阻礙
            'runway_months': 3,            # 資金不足 - 阻礙
            'customer_nps': 60             # 高 NPS - 加速
        }

        maturity = self.tracker.assess_maturity(project_data)

        self.assertGreater(len(maturity.blockers), 0)
        self.assertGreater(len(maturity.accelerators), 0)

    def test_evaluate_transition(self):
        """測試階段轉換評估"""
        project_data = {
            'technology': {'score': 65},
            'process': {'score': 60},
            'team': {'score': 60},
            'has_mvp': True,
            'customers': 15,
            'revenue': 10000
        }

        maturity = self.tracker.assess_maturity(project_data)
        transition = self.tracker.evaluate_transition(maturity)

        self.assertIsInstance(transition, PhaseTransition)
        self.assertIsInstance(transition.from_phase, DevelopmentPhase)
        self.assertIsInstance(transition.to_phase, DevelopmentPhase)
        self.assertGreater(transition.readiness_score, 0)
        self.assertGreater(len(transition.prerequisites), 0)

    def test_transition_to_specific_phase(self):
        """測試轉換到指定階段"""
        maturity = self.tracker.assess_maturity({
            'has_mvp': True,
            'customers': 5
        })

        transition = self.tracker.evaluate_transition(
            maturity,
            target_phase=DevelopmentPhase.SCALE
        )

        self.assertEqual(transition.to_phase, DevelopmentPhase.SCALE)

    def test_create_roadmap(self):
        """測試創建演進路線圖"""
        project_data = {
            'technology': {'score': 60},
            'process': {'score': 55},
            'has_mvp': True,
            'customers': 10
        }

        maturity = self.tracker.assess_maturity(project_data)
        roadmap = self.tracker.create_roadmap(
            maturity,
            target_phase=DevelopmentPhase.SCALE
        )

        self.assertIsInstance(roadmap, EvolutionRoadmap)
        self.assertEqual(roadmap.target_phase, DevelopmentPhase.SCALE)
        self.assertGreater(roadmap.total_timeline_months, 0)
        self.assertGreater(roadmap.investment_required, 0)
        self.assertGreater(roadmap.success_probability, 0)
        self.assertGreater(len(roadmap.milestones), 0)

    def test_roadmap_milestones(self):
        """測試路線圖里程碑"""
        maturity = self.tracker.assess_maturity({
            'has_mvp': False
        })

        roadmap = self.tracker.create_roadmap(
            maturity,
            target_phase=DevelopmentPhase.EFFICIENCY
        )

        for milestone in roadmap.milestones:
            self.assertIn('phase', milestone)
            self.assertIn('target_date', milestone)
            self.assertIn('key_metrics', milestone)

    def test_evolution_report_generation(self):
        """測試演進報告生成"""
        project_data = {
            'technology': {'score': 70},
            'process': {'score': 60},
            'team': {'score': 65},
            'has_mvp': True,
            'customers': 20
        }

        maturity = self.tracker.assess_maturity(project_data)
        transition = self.tracker.evaluate_transition(maturity)
        roadmap = self.tracker.create_roadmap(
            maturity,
            target_phase=DevelopmentPhase.EXPANSION
        )

        report = self.tracker.generate_report(maturity, transition, roadmap)

        self.assertIn('專案演進追蹤報告', report)
        self.assertIn('成熟度評估', report)
        self.assertIn('階段轉換評估', report)
        self.assertIn('演進路線圖', report)


class TestIntegration(unittest.TestCase):
    """整合測試"""

    def test_full_strategy_workflow(self):
        """測試完整策略工作流程"""
        # 1. 案例學習
        case_engine = CaseStudyEngine()
        netflix_case = case_engine.get_case('netflix')
        patterns = case_engine.analyze_strategy_patterns()

        self.assertIsNotNone(netflix_case)
        self.assertGreater(len(patterns['strategy_frequency']), 0)

        # 2. 能力與市場分析
        advisor = StrategyAdvisor()
        capabilities = {
            'engineering': TechCapability(
                name='engineering',
                level=CapabilityLevel.INTERMEDIATE,
                team_members=8,
                experience_years=2.5
            )
        }
        cap_assessment = TechCapabilityAssessment(
            assessed_at=datetime.now(),
            capabilities=capabilities,
            infrastructure_readiness=0.7,
            process_maturity=0.6,
            culture_alignment=0.65
        )
        market_analysis = advisor.analyze_market_timing('saas')
        recommendations = advisor.generate_recommendations(
            cap_assessment,
            market_analysis,
            ['growth']
        )

        self.assertGreater(len(recommendations), 0)

        # 3. 資源優化
        optimizer = ResourceOptimizer()
        optimization = optimizer.generate_optimization(
            total_budget=1500000,
            target_headcount=15,
            strategy=AllocationStrategy.GROWTH_FOCUSED
        )

        self.assertIsInstance(optimization, OptimizationResult)

        # 4. 演進追蹤
        tracker = EvolutionTracker()
        maturity = tracker.assess_maturity({
            'technology': {'score': 60},
            'has_mvp': True,
            'customers': 15
        })
        roadmap = tracker.create_roadmap(
            maturity,
            DevelopmentPhase.SCALE
        )

        self.assertIsInstance(roadmap, EvolutionRoadmap)

    def test_data_consistency(self):
        """測試數據一致性"""
        optimizer = ResourceOptimizer()
        result = optimizer.generate_optimization(
            total_budget=1000000,
            target_headcount=10
        )

        # 預算分配總和應等於營運預算部分
        budget_sum = sum(
            cat.amount for cat in result.budget_allocation.allocations.values()
        )
        self.assertAlmostEqual(
            budget_sum,
            result.budget_allocation.total_budget,
            places=0
        )

        # 團隊成本不應超過人力預算
        self.assertLessEqual(
            result.team_allocation.total_cost,
            1000000 * 0.7  # 70% 用於人力
        )


if __name__ == '__main__':
    unittest.main()
