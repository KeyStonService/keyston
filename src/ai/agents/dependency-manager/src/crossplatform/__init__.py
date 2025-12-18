"""
跨平台整合模組
Cross-platform Integration Module

Phase 9: Web3、IoT、AR/VR 整合以及風險管控系統
"""

from .web3_integration import Web3Integration, DAppAssessment, NFTStrategy, SmartContractDev
from .iot_integration import IoTIntegration, EdgeComputing, DeviceInterconnection, Industry40
from .arvr_integration import ARVRIntegration, ImmersiveExperience, MixedReality, MetaversePlatform
from .tech_stack_matrix import TechStackMatrix, StackRecommendation
from .risk_assessment import RiskAssessment, RiskCategory, MitigationStrategy
from .emergency_response import EmergencyResponse, PlanType, TriggerCondition

__all__ = [
    'Web3Integration', 'DAppAssessment', 'NFTStrategy', 'SmartContractDev',
    'IoTIntegration', 'EdgeComputing', 'DeviceInterconnection', 'Industry40',
    'ARVRIntegration', 'ImmersiveExperience', 'MixedReality', 'MetaversePlatform',
    'TechStackMatrix', 'StackRecommendation',
    'RiskAssessment', 'RiskCategory', 'MitigationStrategy',
    'EmergencyResponse', 'PlanType', 'TriggerCondition'
]
