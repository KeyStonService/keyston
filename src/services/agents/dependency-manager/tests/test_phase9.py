"""
Phase 9 單元測試
Cross-platform Integration & Risk Management Tests
"""

import os
import sys
import unittest

# 添加路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crossplatform.arvr_integration import (
    ARVRIntegration,
    HardwareRequirement,
    ImmersiveExperience,
    InteractionMode,
    MetaversePlatform,
    MixedReality,
    XRType,
)
from crossplatform.emergency_response import (
    EmergencyResponse,
    PlanType,
    TriggerCategory,
)
from crossplatform.iot_integration import (
    DeviceInterconnection,
    EdgeComputing,
    EdgeComputingType,
    Industry40,
    Industry40Component,
    IoTIntegration,
    IoTProtocol,
)
from crossplatform.risk_assessment import RiskAssessment, RiskCategory, RiskType
from crossplatform.tech_stack_matrix import (
    BackendArch,
    DataProcessing,
    DeploymentStrategy,
    FrontendTech,
    TechStackMatrix,
)
from crossplatform.web3_integration import (
    BlockchainType,
    ConsensusType,
    DAppAssessment,
    NFTAssetType,
    NFTStrategy,
    SmartContractDev,
    Web3Integration,
)


class TestWeb3Integration(unittest.TestCase):
    """Web3 整合測試"""

    def setUp(self):
        self.integration = Web3Integration()

    def test_dapp_assessment(self):
        """測試 DApp 評估"""
        assessment = DAppAssessment(
            project_name="TestDApp",
            blockchain=BlockchainType.ETHEREUM,
            consensus=ConsensusType.PROOF_OF_STAKE,
            use_case="DeFi",
            decentralization_level=8,
            gas_optimization_needed=True,
            smart_contract_complexity="medium",
            estimated_tps_requirement=50
        )

        result = self.integration.assess_dapp(assessment)

        self.assertIsNotNone(result.feasibility_score)
        self.assertGreater(result.feasibility_score, 0)
        self.assertIsNotNone(result.recommended_blockchain)
        self.assertIsInstance(result.recommendations, list)

    def test_nft_strategy(self):
        """測試 NFT 策略評估"""
        strategy = NFTStrategy(
            asset_type=NFTAssetType.GAMING,
            marketplace_strategy="hybrid",
            royalty_percentage=5.0,
            minting_approach="lazy",
            storage_type="ipfs"
        )

        result = self.integration.evaluate_nft_strategy(strategy)

        self.assertGreater(result.market_potential_score, 0)
        self.assertIsNotNone(result.technical_complexity)

    def test_smart_contract_evaluation(self):
        """測試智能合約評估"""
        contract = SmartContractDev(
            contract_type="defi",
            programming_language="solidity",
            security_audit_required=True,
            upgrade_pattern="proxy"
        )

        result = self.integration.evaluate_smart_contract(contract)

        self.assertGreater(result.estimated_development_hours, 0)
        self.assertGreater(result.estimated_audit_cost, 0)
        self.assertIsInstance(result.security_risks, list)
        self.assertIsInstance(result.best_practices, list)

    def test_web3_report(self):
        """測試報告生成"""
        # 先添加一些評估
        assessment = DAppAssessment(
            project_name="Test",
            blockchain=BlockchainType.POLYGON,
            consensus=ConsensusType.PROOF_OF_STAKE,
            use_case="NFT Marketplace",
            decentralization_level=7,
            gas_optimization_needed=False,
            smart_contract_complexity="low",
            estimated_tps_requirement=100
        )
        self.integration.assess_dapp(assessment)

        report = self.integration.generate_web3_report()

        self.assertIn('summary', report)
        self.assertIn('dapp_assessments', report)


class TestIoTIntegration(unittest.TestCase):
    """IoT 整合測試"""

    def setUp(self):
        self.integration = IoTIntegration()

    def test_edge_computing_assessment(self):
        """測試邊緣運算評估"""
        edge = EdgeComputing(
            computing_type=EdgeComputingType.FOG_COMPUTING,
            latency_requirement_ms=20,
            bandwidth_requirement_mbps=100,
            local_processing_percentage=70,
            data_privacy_requirement="high"
        )

        result = self.integration.assess_edge_computing(edge)

        self.assertGreater(result.suitability_score, 0)
        self.assertIsNotNone(result.recommended_type)
        self.assertIsInstance(result.hardware_recommendations, list)

    def test_device_interconnection(self):
        """測試設備互聯策略"""
        device = DeviceInterconnection(
            protocol=IoTProtocol.MQTT,
            device_count=5000,
            message_frequency_hz=10,
            security_level="standard",
            scalability_requirement="high"
        )

        result = self.integration.evaluate_device_interconnection(device)

        self.assertGreater(result.throughput_estimate, 0)
        self.assertIsNotNone(result.recommended_protocol)
        self.assertIsInstance(result.security_measures, list)

    def test_industry40_planning(self):
        """測試工業 4.0 規劃"""
        plan = Industry40(
            component=Industry40Component.PREDICTIVE_MAINTENANCE,
            automation_level=4,
            data_integration_scope="departmental",
            roi_target_months=18
        )

        result = self.integration.plan_industry40(plan)

        self.assertGreater(result.estimated_roi, 0)
        self.assertIsInstance(result.key_technologies, list)
        self.assertIsInstance(result.implementation_phases, list)

    def test_iot_report(self):
        """測試報告生成"""
        edge = EdgeComputing(
            computing_type=EdgeComputingType.EDGE_GATEWAY,
            latency_requirement_ms=100,
            bandwidth_requirement_mbps=50,
            local_processing_percentage=30,
            data_privacy_requirement="low"
        )
        self.integration.assess_edge_computing(edge)

        report = self.integration.generate_iot_report()

        self.assertIn('summary', report)
        self.assertIn('edge_computing_assessments', report)


class TestARVRIntegration(unittest.TestCase):
    """AR/VR 整合測試"""

    def setUp(self):
        self.integration = ARVRIntegration()

    def test_immersive_experience(self):
        """測試沉浸式體驗評估"""
        experience = ImmersiveExperience(
            xr_type=XRType.VR,
            hardware_requirement=HardwareRequirement.STANDALONE,
            target_fov=100,
            target_fps=90,
            interaction_modes=[InteractionMode.CONTROLLER, InteractionMode.HAND_TRACKING],
            use_case="Training Simulation"
        )

        result = self.integration.evaluate_immersive_experience(experience)

        self.assertGreater(result.immersion_score, 0)
        self.assertIsInstance(result.hardware_recommendations, list)
        self.assertIsInstance(result.development_frameworks, list)

    def test_mixed_reality(self):
        """測試虛實融合評估"""
        mr = MixedReality(
            spatial_mapping_required=True,
            occlusion_handling="advanced",
            lighting_estimation=True,
            persistent_anchors=True,
            multi_user_support=True
        )

        result = self.integration.evaluate_mixed_reality(mr)

        self.assertIn(result.complexity_level, ['low', 'medium', 'high', 'very_high'])
        self.assertIsNotNone(result.recommended_sdk)
        self.assertIsInstance(result.integration_considerations, list)

    def test_metaverse_platform(self):
        """測試元宇宙平台規劃"""
        platform = MetaversePlatform(
            identity_system="decentralized",
            economy_model="token_based",
            social_features=['voice_chat', 'avatar', 'events'],
            world_persistence=True,
            user_generated_content=True
        )

        result = self.integration.plan_metaverse_platform(platform)

        self.assertGreater(result.estimated_development_months, 0)
        self.assertIsInstance(result.key_components, list)
        self.assertIsInstance(result.monetization_strategies, list)

    def test_arvr_report(self):
        """測試報告生成"""
        experience = ImmersiveExperience(
            xr_type=XRType.AR,
            hardware_requirement=HardwareRequirement.MOBILE,
            target_fov=60,
            target_fps=60,
            interaction_modes=[InteractionMode.GESTURE],
            use_case="Retail AR"
        )
        self.integration.evaluate_immersive_experience(experience)

        report = self.integration.generate_arvr_report()

        self.assertIn('summary', report)
        self.assertIn('immersive_experiences', report)


class TestTechStackMatrix(unittest.TestCase):
    """技術棧矩陣測試"""

    def setUp(self):
        self.matrix = TechStackMatrix()

    def test_stack_evaluation(self):
        """測試技術棧評估"""
        result = self.matrix.evaluate_stack(
            frontend=FrontendTech.REACT,
            backend=BackendArch.MICROSERVICES,
            data_processing=DataProcessing.REALTIME,
            deployment=DeploymentStrategy.CLOUD_NATIVE
        )

        self.assertGreater(result.compatibility_score, 0)
        self.assertIsNotNone(result.complexity_rating)
        self.assertIsNotNone(result.scalability_rating)
        self.assertIsInstance(result.recommended_tools, dict)

    def test_optimal_stack_recommendation(self):
        """測試最佳技術棧推薦"""
        result = self.matrix.recommend_optimal_stack(
            project_type='startup',
            team_size=8,
            scalability_need='high',
            budget_level='medium'
        )

        self.assertIsNotNone(result.frontend)
        self.assertIsNotNone(result.backend)
        self.assertIsInstance(result.considerations, list)

    def test_stack_comparison(self):
        """測試技術棧比較"""
        stack1 = self.matrix.evaluate_stack(
            FrontendTech.REACT, BackendArch.MICROSERVICES,
            DataProcessing.STREAMING, DeploymentStrategy.CLOUD_NATIVE
        )
        stack2 = self.matrix.evaluate_stack(
            FrontendTech.VUE, BackendArch.MONOLITH,
            DataProcessing.BATCH, DeploymentStrategy.ON_PREMISE
        )

        comparison = self.matrix.compare_stacks([stack1, stack2])

        self.assertIn('stacks', comparison)
        self.assertIn('best_compatibility', comparison)
        self.assertIn('comparison_matrix', comparison)


class TestRiskAssessment(unittest.TestCase):
    """風險評估測試"""

    def setUp(self):
        self.assessment = RiskAssessment()

    def test_add_risk(self):
        """測試添加風險"""
        risk = self.assessment.add_risk(
            risk_type=RiskType.TECHNOLOGY_DEPENDENCY,
            title="高技術依賴風險",
            description="過度依賴特定技術棧",
            probability=7,
            impact=8,
            owner="技術主管"
        )

        self.assertIsNotNone(risk.risk_id)
        self.assertEqual(risk.risk_score, 56)
        self.assertIsInstance(risk.mitigation_strategies, list)

    def test_risk_categorization(self):
        """測試風險分類"""
        # 高風險
        high_risk = self.assessment.add_risk(
            RiskType.SECURITY_VULNERABILITY, "高風險", "測試", 8, 9
        )
        self.assertEqual(high_risk.category, RiskCategory.HIGH)

        # 中風險
        medium_risk = self.assessment.add_risk(
            RiskType.MARKET_ACCEPTANCE, "中風險", "測試", 5, 6
        )
        self.assertEqual(medium_risk.category, RiskCategory.MEDIUM)

        # 低風險
        low_risk = self.assessment.add_risk(
            RiskType.TECHNICAL_DEBT, "低風險", "測試", 3, 4
        )
        self.assertEqual(low_risk.category, RiskCategory.LOW)

    def test_project_risk_assessment(self):
        """測試項目風險評估"""
        risks = self.assessment.assess_project_risks(
            technology_stack=['React', 'Node.js', 'MongoDB', 'Redis', 'Kafka', 'K8s'],
            team_experience='medium',
            market_maturity='emerging',
            regulatory_requirements=['GDPR', 'SOC2']
        )

        self.assertGreater(len(risks), 0)

    def test_risk_report(self):
        """測試風險報告"""
        self.assessment.add_risk(
            RiskType.VENDOR_LOCK_IN, "供應商鎖定", "測試", 6, 7
        )

        markdown_report = self.assessment.generate_risk_report('markdown')
        text_report = self.assessment.generate_risk_report('text')

        self.assertIn('風險評估報告', markdown_report)
        self.assertIn('風險評估報告', text_report)


class TestEmergencyResponse(unittest.TestCase):
    """應急響應測試"""

    def setUp(self):
        self.response = EmergencyResponse()

    def test_default_plans_initialized(self):
        """測試預設預案初始化"""
        self.assertIn(PlanType.PLAN_A, self.response.plans)
        self.assertIn(PlanType.PLAN_B, self.response.plans)
        self.assertIn(PlanType.PLAN_C, self.response.plans)

    def test_default_triggers_initialized(self):
        """測試預設觸發條件初始化"""
        self.assertGreater(len(self.response.triggers), 0)

    def test_activate_plan(self):
        """測試激活預案"""
        plan = self.response.activate_plan(PlanType.PLAN_B)

        self.assertEqual(self.response.active_plan, PlanType.PLAN_B)
        self.assertEqual(plan.plan_type, PlanType.PLAN_B)

    def test_trigger_evaluation(self):
        """測試觸發條件評估"""
        metrics = {
            'market_decline': 25,  # 超過 20% 閾值
            'tech_disruption': 0,
            'competitor_threat': 0
        }

        triggered = self.response.evaluate_triggers(metrics)

        # 應該觸發市場變化相關的條件
        self.assertGreater(len(triggered), 0)

    def test_plan_recommendation(self):
        """測試預案推薦"""
        # 正常情況
        normal_metrics = {
            'market_decline': 5,
            'tech_disruption': 0,
            'resource_reduction': 10
        }
        self.assertEqual(
            self.response.recommend_plan(normal_metrics),
            PlanType.PLAN_A
        )

        # 需要調整
        adjust_metrics = {
            'market_decline': 25,
            'tech_disruption': 0,
            'resource_reduction': 10
        }
        self.assertEqual(
            self.response.recommend_plan(adjust_metrics),
            PlanType.PLAN_B
        )

    def test_add_custom_trigger(self):
        """測試添加自定義觸發條件"""
        trigger = self.response.add_trigger(
            category=TriggerCategory.PERFORMANCE_DECLINE,
            name="用戶流失",
            description="月活躍用戶下降超過閾值",
            threshold=15,
            target_plan=PlanType.PLAN_B
        )

        self.assertIn(trigger.trigger_id, self.response.triggers)

    def test_response_report(self):
        """測試應急響應報告"""
        markdown_report = self.response.generate_response_report('markdown')
        text_report = self.response.generate_response_report('text')

        self.assertIn('應急預案系統報告', markdown_report)
        self.assertIn('應急預案系統報告', text_report)

    def test_to_dict(self):
        """測試轉換為字典"""
        result = self.response.to_dict()

        self.assertIn('active_plan', result)
        self.assertIn('plans', result)
        self.assertIn('triggers', result)


if __name__ == '__main__':
    unittest.main()
