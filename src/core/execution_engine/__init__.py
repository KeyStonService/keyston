"""
═══════════════════════════════════════════════════════════
        SynergyMesh Execution Engine (Phase 8)
        執行引擎 - 連接理論與現實的橋樑
═══════════════════════════════════════════════════════════

核心理念：知識 ≠ 能力，代碼 ≠ 執行
將「知道如何做」轉換為「能夠實際做」

This module provides the execution layer that bridges:
- Knowledge → Capability
- Theory → Practice
- Code → Real Actions
"""

from .execution_engine import (
    ExecutionEngine,
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    ActionType,
)

from .capability_registry import (
    CapabilityRegistry,
    Capability,
    CapabilityStatus,
    CapabilityRequirement,
)

from .connector_manager import (
    ConnectorManager,
    Connector,
    ConnectorType,
    ConnectionStatus,
)

from .action_executor import (
    ActionExecutor,
    ActionPlan,
    ActionStep,
    StepResult,
)

from .verification_engine import (
    VerificationEngine,
    VerificationResult,
    VerificationStrategy,
)

from .rollback_manager import (
    RollbackManager,
    RollbackPlan,
    RollbackStatus,
    Checkpoint,
)

__all__ = [
    # Execution Engine
    'ExecutionEngine',
    'ExecutionContext',
    'ExecutionResult',
    'ExecutionStatus',
    'ActionType',
    # Capability Registry
    'CapabilityRegistry',
    'Capability',
    'CapabilityStatus',
    'CapabilityRequirement',
    # Connector Manager
    'ConnectorManager',
    'Connector',
    'ConnectorType',
    'ConnectionStatus',
    # Action Executor
    'ActionExecutor',
    'ActionPlan',
    'ActionStep',
    'StepResult',
    # Verification Engine
    'VerificationEngine',
    'VerificationResult',
    'VerificationStrategy',
    # Rollback Manager
    'RollbackManager',
    'RollbackPlan',
    'RollbackStatus',
    'Checkpoint',
]

__version__ = '1.0.0'
