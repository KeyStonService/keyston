"""
SynergyMesh Main System Integration (Phase 14)
主系統整合 - 統一所有 13 個階段

將所有階段整合成統一的自動化系統
"""

from .automation_pipeline import (
    AutomationPipeline,
    PipelineConfig,
    PipelineTask,
    TaskResult,
)
from .phase_orchestrator import (
    ExecutionMode,
    PhaseDefinition,
    PhaseOrchestrator,
    PhaseTransition,
)
from .synergymesh_core import (
    PhaseStatus,
    SynergyMeshCore,
    SystemConfig,
    SystemHealth,
)
from .system_bootstrap import (
    BootstrapConfig,
    DependencyInjector,
    ServiceRegistry,
    SystemBootstrap,
)

__all__ = [
    # Core
    'SynergyMeshCore',
    'SystemConfig',
    'PhaseStatus',
    'SystemHealth',
    # Bootstrap
    'SystemBootstrap',
    'BootstrapConfig',
    'ServiceRegistry',
    'DependencyInjector',
    # Orchestrator
    'PhaseOrchestrator',
    'PhaseDefinition',
    'PhaseTransition',
    'ExecutionMode',
    # Pipeline
    'AutomationPipeline',
    'PipelineTask',
    'TaskResult',
    'PipelineConfig',
]
