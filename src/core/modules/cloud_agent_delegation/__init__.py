"""
Phase 21: Cloud Agent Delegation System

This module provides cloud-native multi-agent delegation capabilities
for distributed task execution across multiple cloud providers.

Key Components:
- DelegationManager: Central manager for task delegation
- CloudProviderAdapter: Adapters for different cloud providers
- TaskRouter: Intelligent task routing based on policies
- LoadBalancer: Load balancing across cloud providers
"""

from .cloud_provider_adapter import CloudProviderAdapter, ProviderConfig, ProviderType
from .delegation_manager import DelegationConfig, DelegationManager, DelegationResult
from .load_balancer import BalancingStrategy, LoadBalancer, ProviderHealth
from .task_router import RoutingResult, RoutingRule, RoutingStrategy, TaskRouter

__all__ = [
    'DelegationManager',
    'DelegationConfig',
    'DelegationResult',
    'CloudProviderAdapter',
    'ProviderType',
    'ProviderConfig',
    'TaskRouter',
    'RoutingRule',
    'RoutingResult',
    'RoutingStrategy',
    'LoadBalancer',
    'BalancingStrategy',
    'ProviderHealth',
]

__version__ = '1.0.0'
__author__ = 'SynergyMesh Team'
