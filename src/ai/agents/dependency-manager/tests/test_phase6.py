# -*- coding: utf-8 -*-
"""
第六階段單元測試 (Phase 6 Unit Tests)

測試範圍：
- 永續發展分析器
- 低代碼整合
- 隱私優先框架
- 發展追蹤器
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# 添加源碼路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSustainableAnalyzer(unittest.TestCase):
    """永續發展分析器測試"""
    
    def setUp(self):
        """測試前準備"""
        from future.sustainable_analyzer import (
            SustainableAnalyzer, CarbonFootprint, EnergyEfficiency,
            GreenScore, ImpactLevel, EnergyGrade
        )
        self.SustainableAnalyzer = SustainableAnalyzer
        self.CarbonFootprint = CarbonFootprint
        self.EnergyEfficiency = EnergyEfficiency
        self.GreenScore = GreenScore
        self.ImpactLevel = ImpactLevel
        self.EnergyGrade = EnergyGrade
    
    def test_carbon_footprint_calculation(self):
        """測試碳足跡計算"""
        footprint = self.CarbonFootprint(
            dependency_name="express",
            version="4.18.2",
            build_emissions=0.005,
            runtime_emissions=0.001,
            transfer_emissions=0.0002
        )
        
        self.assertGreater(footprint.total_emissions, 0)
        self.assertIsInstance(footprint.impact_level, self.ImpactLevel)
    
    def test_energy_efficiency_grade(self):
        """測試能源效率等級"""
        efficiency = self.EnergyEfficiency(
            component_name="api-server",
            component_type="dependency",
            efficiency_score=85
        )
        
        self.assertEqual(efficiency.energy_grade, self.EnergyGrade.A)
    
    def test_analyze_dependency(self):
        """測試依賴項分析"""
        analyzer = self.SustainableAnalyzer()
        
        footprint = analyzer.analyze_dependency(
            name="lodash",
            version="4.17.21",
            ecosystem="npm",
            size_mb=1.5,
            dependencies_count=0
        )
        
        self.assertEqual(footprint.dependency_name, "lodash")
        self.assertGreater(footprint.total_emissions, 0)
    
    def test_green_score_calculation(self):
        """測試綠色評分計算"""
        analyzer = self.SustainableAnalyzer()
        
        dependencies = [
            {'name': 'express', 'version': '4.18.2', 'ecosystem': 'npm', 'size_mb': 2.0, 'dependencies_count': 30},
            {'name': 'lodash', 'version': '4.17.21', 'ecosystem': 'npm', 'size_mb': 1.5, 'dependencies_count': 0},
        ]
        
        green_score = analyzer.calculate_green_score("test-project", dependencies)
        
        self.assertIsInstance(green_score, self.GreenScore)
        self.assertGreaterEqual(green_score.overall_score, 0)
        self.assertLessEqual(green_score.overall_score, 100)
    
    def test_generate_report(self):
        """測試報告生成"""
        analyzer = self.SustainableAnalyzer()
        
        dependencies = [
            {'name': 'axios', 'version': '1.6.0', 'ecosystem': 'npm', 'size_mb': 0.5, 'dependencies_count': 2},
        ]
        
        analyzer.calculate_green_score("test-project", dependencies)
        
        report = analyzer.generate_report(format='text')
        self.assertIn("永續發展分析報告", report)
        
        report_md = analyzer.generate_report(format='markdown')
        self.assertIn("# 🌍", report_md)
        
        report_json = analyzer.generate_report(format='json')
        self.assertIn("overall", report_json)
    
    def test_get_recommendations(self):
        """測試獲取建議"""
        analyzer = self.SustainableAnalyzer()
        
        dependencies = [
            {'name': 'huge-lib', 'version': '1.0.0', 'ecosystem': 'npm', 'size_mb': 50.0, 'dependencies_count': 100},
        ]
        
        analyzer.calculate_green_score("test-project", dependencies)
        recommendations = analyzer.get_recommendations()
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)


class TestLowCodeIntegration(unittest.TestCase):
    """低代碼整合測試"""
    
    def setUp(self):
        """測試前準備"""
        from future.lowcode_integration import (
            LowCodeIntegration, CitizenDeveloper, VisualWorkflow,
            WorkflowNode, WorkflowNodeType, SkillLevel, AutoGenerator
        )
        self.LowCodeIntegration = LowCodeIntegration
        self.CitizenDeveloper = CitizenDeveloper
        self.VisualWorkflow = VisualWorkflow
        self.WorkflowNode = WorkflowNode
        self.WorkflowNodeType = WorkflowNodeType
        self.SkillLevel = SkillLevel
        self.AutoGenerator = AutoGenerator
    
    def test_create_citizen_developer(self):
        """測試創建公民開發者"""
        platform = self.LowCodeIntegration()
        
        user = platform.create_citizen_developer(
            user_id="user_001",
            name="張小明",
            skill_level=self.SkillLevel.BEGINNER
        )
        
        self.assertEqual(user.user_id, "user_001")
        self.assertEqual(user.name, "張小明")
        self.assertTrue(user.can_view)
        self.assertFalse(user.can_edit)
    
    def test_skill_upgrade(self):
        """測試技能升級"""
        user = self.CitizenDeveloper(
            user_id="user_002",
            name="李小華",
            skill_level=self.SkillLevel.BEGINNER
        )
        
        result = user.upgrade_skill()
        self.assertTrue(result)
        self.assertEqual(user.skill_level, self.SkillLevel.INTERMEDIATE)
    
    def test_create_workflow(self):
        """測試創建工作流"""
        platform = self.LowCodeIntegration()
        
        workflow = platform.create_workflow(
            workflow_id="wf_001",
            name="安全掃描工作流",
            description="定期掃描依賴項漏洞"
        )
        
        self.assertEqual(workflow.workflow_id, "wf_001")
        self.assertEqual(workflow.name, "安全掃描工作流")
    
    def test_workflow_validation(self):
        """測試工作流驗證"""
        workflow = self.VisualWorkflow(
            workflow_id="wf_002",
            name="測試工作流"
        )
        
        # 空工作流應該有錯誤
        errors = workflow.validate()
        self.assertGreater(len(errors), 0)
        
        # 添加觸發器和輸出
        trigger = self.WorkflowNode(
            node_id="trigger_1",
            node_type=self.WorkflowNodeType.TRIGGER,
            name="觸發器"
        )
        workflow.add_node(trigger)
        
        output = self.WorkflowNode(
            node_id="output_1",
            node_type=self.WorkflowNodeType.OUTPUT,
            name="輸出"
        )
        workflow.add_node(output)
        workflow.connect_nodes("trigger_1", "output_1")
        
        errors = workflow.validate()
        self.assertEqual(len(errors), 0)
    
    def test_apply_template(self):
        """測試應用模板"""
        platform = self.LowCodeIntegration()
        
        workflow = platform.apply_template(
            template_id="security-scan",
            workflow_id="wf_security_001"
        )
        
        self.assertIn("安全掃描", workflow.name)
        self.assertGreater(len(workflow.nodes), 0)
    
    def test_code_generation(self):
        """測試代碼生成"""
        generator = self.AutoGenerator()
        
        config = {
            'name': 'Test Workflow',
            'dependencies': [
                {'name': 'express', 'version': '4.18.2'}
            ],
            'actions': [
                {'type': 'scan'}
            ],
            'ecosystem': 'npm'
        }
        
        # 測試各種格式
        yaml_output = generator.generate(config, 'yaml')
        self.assertIn('name:', yaml_output)
        
        json_output = generator.generate(config, 'json')
        self.assertIn('"name":', json_output)
        
        python_output = generator.generate(config, 'python')
        self.assertIn('def install_dependencies', python_output)
        
        bash_output = generator.generate(config, 'bash')
        self.assertIn('#!/bin/bash', bash_output)
    
    def test_get_templates_for_user(self):
        """測試獲取適合用戶的模板"""
        platform = self.LowCodeIntegration()
        
        platform.create_citizen_developer(
            user_id="user_003",
            name="王小花",
            skill_level=self.SkillLevel.BEGINNER
        )
        
        templates = platform.get_templates_for_user("user_003")
        
        # 初學者應該只能看到 BEGINNER 難度的模板
        for template in templates:
            self.assertIn(
                template.difficulty,
                [self.SkillLevel.BEGINNER]
            )


class TestPrivacyFramework(unittest.TestCase):
    """隱私優先框架測試"""
    
    def setUp(self):
        """測試前準備"""
        from future.privacy_framework import (
            PrivacyFramework, PrivacyByDesign, DataSovereignty,
            ConsentManager, DataField, DataSensitivity, DataCategory,
            ConsentType, ComplianceFramework
        )
        self.PrivacyFramework = PrivacyFramework
        self.PrivacyByDesign = PrivacyByDesign
        self.DataSovereignty = DataSovereignty
        self.ConsentManager = ConsentManager
        self.DataField = DataField
        self.DataSensitivity = DataSensitivity
        self.DataCategory = DataCategory
        self.ConsentType = ConsentType
        self.ComplianceFramework = ComplianceFramework
    
    def test_data_field_creation(self):
        """測試數據欄位創建"""
        field = self.DataField(
            field_name="email",
            field_type="string",
            sensitivity=self.DataSensitivity.CONFIDENTIAL,
            category=self.DataCategory.PERSONAL,
            is_pii=True,
            is_encrypted=True,
            requires_consent=True
        )
        
        self.assertEqual(field.field_name, "email")
        self.assertTrue(field.is_pii)
        self.assertTrue(field.is_encrypted)
    
    def test_privacy_by_design_assessment(self):
        """測試隱私設計評估"""
        design = self.PrivacyByDesign(project_name="test-project")
        
        # 添加數據欄位
        design.add_data_field(self.DataField(
            field_name="user_id",
            field_type="string",
            is_pii=False,
            is_encrypted=True
        ))
        
        design.add_data_field(self.DataField(
            field_name="email",
            field_type="string",
            is_pii=True,
            is_encrypted=True,
            requires_consent=True
        ))
        
        scores = design.assess()
        
        self.assertIn('overall', scores)
        self.assertGreaterEqual(scores['overall'], 0)
        self.assertLessEqual(scores['overall'], 100)
    
    def test_consent_management(self):
        """測試同意管理"""
        manager = self.ConsentManager()
        
        consent = manager.record_consent(
            user_id="user_001",
            purpose="marketing",
            consent_type=self.ConsentType.EXPLICIT,
            data_categories=[self.DataCategory.PERSONAL, self.DataCategory.BEHAVIORAL],
            expires_days=365,
            source="web"
        )
        
        self.assertTrue(consent.is_valid())
        
        # 檢查同意
        has_consent = manager.check_consent(
            user_id="user_001",
            purpose="marketing",
            data_category=self.DataCategory.PERSONAL
        )
        self.assertTrue(has_consent)
        
        # 撤銷同意
        manager.revoke_consent(consent.consent_id)
        self.assertFalse(consent.is_valid())
    
    def test_data_sovereignty(self):
        """測試數據主權"""
        sovereignty = self.DataSovereignty(organization_id="org_001")
        
        sovereignty.register_data_location(
            data_type="customer_data",
            location="taiwan-dc",
            jurisdiction="TW"
        )
        
        sovereignty.add_cross_border_rule(
            source="TW",
            target="EU",
            allowed=True,
            conditions=["需要標準合約條款"],
            documentation=["傳輸影響評估"]
        )
        
        # 檢查傳輸
        result = sovereignty.check_transfer_allowed(
            data_type="customer_data",
            source_jurisdiction="TW",
            target_jurisdiction="EU"
        )
        
        self.assertTrue(result['allowed'])
        self.assertGreater(len(result['conditions']), 0)
    
    def test_compliance_check(self):
        """測試合規檢查"""
        framework = self.PrivacyFramework("test-project")
        
        # 添加數據欄位
        framework.add_data_field(self.DataField(
            field_name="email",
            field_type="string",
            is_pii=True,
            is_encrypted=True,
            requires_consent=True
        ))
        
        framework.add_data_field(self.DataField(
            field_name="name",
            field_type="string",
            is_pii=True,
            is_encrypted=True,
            requires_consent=True
        ))
        
        # 記錄同意
        framework.record_consent(
            user_id="user_001",
            purpose="service",
            consent_type=self.ConsentType.EXPLICIT,
            data_categories=[self.DataCategory.PERSONAL]
        )
        
        # 檢查 GDPR 合規
        compliance = framework.check_compliance(self.ComplianceFramework.GDPR)
        
        self.assertIn('compliance_score', compliance)
        self.assertIn('is_compliant', compliance)
        self.assertIn('issues', compliance)
    
    def test_privacy_impact_assessment(self):
        """測試隱私影響評估"""
        framework = self.PrivacyFramework("test-project")
        
        # 添加敏感數據
        framework.add_data_field(self.DataField(
            field_name="ssn",
            field_type="string",
            sensitivity=self.DataSensitivity.RESTRICTED,
            is_pii=True,
            is_encrypted=False  # 故意不加密以觸發風險
        ))
        
        pia = framework.perform_privacy_impact_assessment()
        
        self.assertIn('risk_assessment', pia)
        self.assertIn('risk_level', pia['risk_assessment'])
        self.assertIn('mitigation_measures', pia)
    
    def test_full_report_generation(self):
        """測試完整報告生成"""
        framework = self.PrivacyFramework("test-project")
        
        framework.add_data_field(self.DataField(
            field_name="email",
            field_type="string",
            is_pii=True,
            is_encrypted=True
        ))
        
        report = framework.generate_full_report()
        
        self.assertIn("隱私優先框架", report)
        self.assertIn("隱私設計評分", report)


class TestDevelopmentTracker(unittest.TestCase):
    """發展追蹤器測試"""
    
    def setUp(self):
        """測試前準備"""
        from future.development_tracker import (
            DevelopmentTracker, Strategy321, StrategyItem, StrategyPriority,
            TeamCapability, SkillCategory, ContinuousOptimization, ReviewCycle
        )
        self.DevelopmentTracker = DevelopmentTracker
        self.Strategy321 = Strategy321
        self.StrategyItem = StrategyItem
        self.StrategyPriority = StrategyPriority
        self.TeamCapability = TeamCapability
        self.SkillCategory = SkillCategory
        self.ContinuousOptimization = ContinuousOptimization
        self.ReviewCycle = ReviewCycle
    
    def test_strategy_321_creation(self):
        """測試 3-2-1 策略創建"""
        strategy = self.Strategy321(organization_id="org_001")
        
        self.assertEqual(strategy.max_current, 3)
        self.assertEqual(strategy.max_preparing, 2)
        self.assertEqual(strategy.max_researching, 1)
    
    def test_add_strategy(self):
        """測試添加策略"""
        strategy_321 = self.Strategy321(organization_id="org_001")
        
        item = self.StrategyItem(
            strategy_id="s_001",
            name="企業級應用開發",
            description="建立穩固的技術基礎",
            priority=self.StrategyPriority.CURRENT
        )
        
        success, message = strategy_321.add_strategy(item)
        
        self.assertTrue(success)
        self.assertEqual(len(strategy_321.current_strategies), 1)
    
    def test_strategy_limit(self):
        """測試策略數量限制"""
        strategy_321 = self.Strategy321(organization_id="org_001")
        
        # 添加 3 個當前策略
        for i in range(3):
            item = self.StrategyItem(
                strategy_id=f"s_{i}",
                name=f"策略 {i}",
                description="測試策略",
                priority=self.StrategyPriority.CURRENT
            )
            strategy_321.add_strategy(item)
        
        # 第 4 個應該失敗
        item = self.StrategyItem(
            strategy_id="s_4",
            name="策略 4",
            description="測試策略",
            priority=self.StrategyPriority.CURRENT
        )
        success, message = strategy_321.add_strategy(item)
        
        self.assertFalse(success)
        self.assertIn("上限", message)
    
    def test_promote_strategy(self):
        """測試策略提升"""
        strategy_321 = self.Strategy321(organization_id="org_001")
        
        # 添加研究中策略
        item = self.StrategyItem(
            strategy_id="s_research",
            name="未來技術研究",
            description="研究新技術",
            priority=self.StrategyPriority.RESEARCHING
        )
        strategy_321.add_strategy(item)
        
        # 提升到準備中
        success, message = strategy_321.promote_strategy("s_research")
        
        self.assertTrue(success)
        self.assertEqual(len(strategy_321.researching_strategies), 0)
        self.assertEqual(len(strategy_321.preparing_strategies), 1)
    
    def test_team_capability_assessment(self):
        """測試團隊能力評估"""
        team = self.TeamCapability(
            team_id="team_001",
            team_name="開發團隊",
            team_size=10
        )
        
        assessment = team.assess_skill(
            category=self.SkillCategory.SECURITY,
            current_level=60,
            target_level=85,
            members_with_skill=4
        )
        
        self.assertEqual(assessment.skill_category, self.SkillCategory.SECURITY)
        self.assertEqual(assessment.current_level, 60)
        self.assertEqual(assessment.target_level, 85)
        self.assertGreater(assessment.training_hours_needed, 0)
    
    def test_capability_gaps(self):
        """測試能力差距分析"""
        team = self.TeamCapability(
            team_id="team_001",
            team_name="開發團隊",
            team_size=10
        )
        
        team.assess_skill(self.SkillCategory.SECURITY, 50, 80, 3)
        team.assess_skill(self.SkillCategory.CLOUD, 70, 90, 6)
        team.assess_skill(self.SkillCategory.AI_ML, 30, 70, 2)
        
        gaps = team.get_capability_gaps()
        
        self.assertEqual(len(gaps), 3)
        # 應該按差距大小排序
        self.assertEqual(gaps[0]['skill'], 'ai_ml')  # 差距最大
    
    def test_continuous_optimization_review(self):
        """測試持續優化審查"""
        tracker = self.DevelopmentTracker(
            organization_id="org_001",
            team_name="測試團隊",
            team_size=8
        )
        
        # 添加策略
        tracker.add_strategy(
            strategy_id="s_001",
            name="商業導向開發",
            description="確保投資回報",
            priority=self.StrategyPriority.CURRENT
        )
        
        # 評估技能
        tracker.assess_team_skill(
            category=self.SkillCategory.BACKEND,
            current_level=70,
            target_level=85,
            members_with_skill=5
        )
        
        # 執行審查
        review = tracker.conduct_quarterly_review()
        
        self.assertIsNotNone(review)
        self.assertGreater(review.strategies_reviewed, 0)
    
    def test_full_report_generation(self):
        """測試完整報告生成"""
        tracker = self.DevelopmentTracker(
            organization_id="org_001",
            team_name="測試團隊",
            team_size=8
        )
        
        tracker.add_strategy(
            strategy_id="s_001",
            name="商業導向開發",
            description="確保投資回報",
            priority=self.StrategyPriority.CURRENT
        )
        
        report = tracker.generate_full_report()
        
        self.assertIn("發展追蹤器", report)
        self.assertIn("3-2-1 策略狀態", report)
        self.assertIn("團隊能力", report)
    
    def test_alert_system(self):
        """測試警報系統"""
        optimization = self.ContinuousOptimization()
        
        optimization.set_alert(
            metric_name="team_capability_score",
            threshold=60,
            comparison="below"
        )
        
        triggered = optimization.check_alerts({
            'team_capability_score': 50,
            'active_strategies': 2
        })
        
        self.assertEqual(len(triggered), 1)
        self.assertIn("低於閾值", triggered[0]['message'])


if __name__ == '__main__':
    unittest.main()
