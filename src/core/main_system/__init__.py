"""
SynergyMesh Main System Integration (Phase 14)
主系統整合 - 統一所有 13 個階段

將所有階段整合成統一的自動化系統
"""

from .synergymesh_core import (
    SynergyMeshCore,
    SystemConfig,
    PhaseStatus,
    SystemHealth,
)
from .system_bootstrap import (
    SystemBootstrap,
    BootstrapConfig,
    ServiceRegistry,
    DependencyInjector,
)
from .phase_orchestrator import (
    PhaseOrchestrator,
    PhaseDefinition,
    PhaseTransition,
    ExecutionMode,
)
from .automation_pipeline import (
    AutomationPipeline,
    PipelineTask,
    TaskResult,
    PipelineConfig,
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
