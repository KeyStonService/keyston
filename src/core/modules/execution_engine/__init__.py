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

from .action_executor import (
    ActionExecutor,
    ActionPlan,
    ActionStep,
    StepResult,
)
from .capability_registry import (
    Capability,
    CapabilityRegistry,
    CapabilityRequirement,
    CapabilityStatus,
)
from .connector_manager import (
    ConnectionStatus,
    Connector,
    ConnectorManager,
    ConnectorType,
)
from .execution_engine import (
    ActionType,
    ExecutionContext,
    ExecutionEngine,
    ExecutionResult,
    ExecutionStatus,
)
from .rollback_manager import (
    Checkpoint,
    RollbackManager,
    RollbackPlan,
    RollbackStatus,
)
from .verification_engine import (
    VerificationEngine,
    VerificationResult,
    VerificationStrategy,
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
