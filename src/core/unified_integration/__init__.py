"""
Phase 22: Unified System Integration
═══════════════════════════════════════════════════════════════════════════════
                    SynergyMesh 統一系統整合
═══════════════════════════════════════════════════════════════════════════════

This module provides the unified integration layer that connects all SynergyMesh
components into a cohesive, production-ready system. It bridges phases 1-21 into
a seamless operational framework.

Key Components:
- UnifiedSystemController: Central orchestration for all phases
- IntegrationHub: Cross-phase communication and coordination
- SystemOrchestrator: High-level system management
- ConfigurationManager: Unified configuration management
- ServiceRegistry: Unified service discovery and management
- EnhancedCognitiveProcessor: Multi-layer cognitive processing
- ConfigurationOptimizer: Intelligent configuration optimization
- WorkConfigurationManager: Work configuration and policy integration (NEW)

Architecture Overview:
┌─────────────────────────────────────────────────────────────────────┐
│                    Unified System Integration                        │
├─────────────────┬───────────────────┬───────────────────────────────┤
│ ServiceRegistry │ IntegrationHub    │ ConfigurationManager          │
│ (Discovery)     │ (Communication)   │ (Settings)                    │
├─────────────────┴───────────────────┴───────────────────────────────┤
│                    WorkConfigurationManager (NEW)                    │
│  (Module Mapping | Strategy Policies | Cross-Reference Validation)  │
├─────────────────────────────────────────────────────────────────────┤
│                    EnhancedCognitiveProcessor                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐      │
│  │ L1 Perception│ L2 Reasoning │ L3 Execution │ L4 Proof     │      │
│  └──────────────┴──────────────┴──────────────┴──────────────┘      │
├─────────────────────────────────────────────────────────────────────┤
│                    ConfigurationOptimizer                            │
│  (Validation, Drift Detection, Recommendations)                      │
├─────────────────────────────────────────────────────────────────────┤
│                    SystemOrchestrator                                │
│  (Workflows, Task Scheduling, Health Monitoring)                     │
└─────────────────────────────────────────────────────────────────────┘
"""

from .unified_controller import UnifiedSystemController
from .integration_hub import IntegrationHub, IntegrationConfig
from .system_orchestrator import SystemOrchestrator, OrchestratorConfig
from .configuration_manager import ConfigurationManager, SystemConfiguration
from .service_registry import (
    ServiceRegistry,
    RegistryConfig,
    ServiceMetadata,
    ServiceEndpoint,
    ServiceHealth,
    ServiceStatus,
    ServiceCategory,
    create_service_registry,
    register_core_services
)
from .cognitive_processor import (
    EnhancedCognitiveProcessor,
    ProcessorConfig,
    CognitiveSignal,
    CognitiveContext,
    Decision,
    RiskAssessment,
    CognitiveLayer,
    SignalType,
    DecisionConfidence,
    RiskLevel,
    PerceptionLayer,
    ReasoningLayer,
    ExecutionLayer,
    ProofLayer,
    create_cognitive_processor
)
from .configuration_optimizer import (
    ConfigurationOptimizer,
    OptimizerConfig,
    ConfigurationRule,
    ValidationResult,
    OptimizationRecommendation,
    DriftReport,
    ConfigurationSnapshot,
    OptimizationCategory,
    RecommendationPriority,
    ConfigurationScope,
    ValidationSeverity,
    create_configuration_optimizer
)
from .work_configuration_manager import (
    WorkConfigurationManager,
    WorkConfigManagerConfig,
    WorkConfiguration,
    WorkConfigurationStatus,
    ConfigurationReference,
    ReferenceType,
    StrategyPolicy,
    CapabilityMapping,
    CrossReferenceReport,
    IntegrityLevel,
    create_work_configuration_manager
)

__all__ = [
    # Core Controllers
    'UnifiedSystemController',
    
    # Integration Hub
    'IntegrationHub',
    'IntegrationConfig',
    
    # System Orchestrator
    'SystemOrchestrator',
    'OrchestratorConfig',
    
    # Configuration Manager
    'ConfigurationManager',
    'SystemConfiguration',
    
    # Service Registry (NEW)
    'ServiceRegistry',
    'RegistryConfig',
    'ServiceMetadata',
    'ServiceEndpoint',
    'ServiceHealth',
    'ServiceStatus',
    'ServiceCategory',
    'create_service_registry',
    'register_core_services',
    
    # Cognitive Processor (NEW)
    'EnhancedCognitiveProcessor',
    'ProcessorConfig',
    'CognitiveSignal',
    'CognitiveContext',
    'Decision',
    'RiskAssessment',
    'CognitiveLayer',
    'SignalType',
    'DecisionConfidence',
    'RiskLevel',
    'PerceptionLayer',
    'ReasoningLayer',
    'ExecutionLayer',
    'ProofLayer',
    'create_cognitive_processor',
    
    # Configuration Optimizer (NEW)
    'ConfigurationOptimizer',
    'OptimizerConfig',
    'ConfigurationRule',
    'ValidationResult',
    'OptimizationRecommendation',
    'DriftReport',
    'ConfigurationSnapshot',
    'OptimizationCategory',
    'RecommendationPriority',
    'ConfigurationScope',
    'ValidationSeverity',
    'create_configuration_optimizer',

    # Work Configuration Manager (NEW)
    'WorkConfigurationManager',
    'WorkConfigManagerConfig',
    'WorkConfiguration',
    'WorkConfigurationStatus',
    'ConfigurationReference',
    'ReferenceType',
    'StrategyPolicy',
    'CapabilityMapping',
    'CrossReferenceReport',
    'IntegrityLevel',
    'create_work_configuration_manager',
]

__version__ = '1.2.0'
__author__ = 'SynergyMesh Team'
