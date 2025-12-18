"""
跨平台整合模組
Cross-platform Integration Module

Phase 9: Web3、IoT、AR/VR 整合以及風險管控系統
"""

from .arvr_integration import ARVRIntegration, ImmersiveExperience, MetaversePlatform, MixedReality
from .emergency_response import EmergencyResponse, PlanType, TriggerCondition
from .iot_integration import DeviceInterconnection, EdgeComputing, Industry40, IoTIntegration
from .risk_assessment import MitigationStrategy, RiskAssessment, RiskCategory
from .tech_stack_matrix import StackRecommendation, TechStackMatrix
from .web3_integration import DAppAssessment, NFTStrategy, SmartContractDev, Web3Integration

__all__ = [
    'Web3Integration', 'DAppAssessment', 'NFTStrategy', 'SmartContractDev',
    'IoTIntegration', 'EdgeComputing', 'DeviceInterconnection', 'Industry40',
    'ARVRIntegration', 'ImmersiveExperience', 'MixedReality', 'MetaversePlatform',
    'TechStackMatrix', 'StackRecommendation',
    'RiskAssessment', 'RiskCategory', 'MitigationStrategy',
    'EmergencyResponse', 'PlanType', 'TriggerCondition'
]
