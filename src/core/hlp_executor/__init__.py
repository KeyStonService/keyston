"""
HLP Executor Core Plugin - Hard Logic Plugin Async DAG Orchestration Engine

This module provides a sophisticated execution engine for async DAG orchestration
with partial rollback support, state machine management, and retry policies.

Features:
- Async DAG Orchestration with topological sorting
- 3-level Partial Rollback (Phase/Plan-unit/Artifact granularity)
- State Machine with 7-state transition flow
- Dynamic Retry Policies (exponential backoff + jitter + risk-adaptive)
- Quantum backend integration with graceful degradation

Status: P0 core implementation complete.
"""

__version__ = "0.2.0"
__plugin_id__ = "hlp-executor-core"

from typing import Dict, Any

# Import core components
from .dag_engine import DAGEngine, DAGNode, NodeStatus
from .state_machine import (
    StateMachine,
    ExecutionState,
    ExecutionOrchestrator,
    StateTransition,
)
from .partial_rollback import (
    PartialRollbackManager,
    RollbackLevel,
    RollbackStatus,
    Checkpoint,
    RollbackOperation,
)

# Plugin metadata for service discovery
PLUGIN_METADATA: Dict[str, Any] = {
    "plugin_id": __plugin_id__,
    "version": __version__,
    "plugin_type": "executor-engine",
    "security_clearance": "L3-enterprise",
    "compliance_tags": ["SLSA-L3", "quantum-safe", "enterprise-ready"],
    "provides": [
        "runtime-execution-graph",
        "state-machine-orchestration",
        "partial-rollback-management",
        "dynamic-retry-policies",
        "dag-orchestration",
        "state-management",
    ],
    "requires": [
        "kubernetes-api",
        "trust-bundle",
    ],
    "optional": [
        "quantum-scheduler",
    ],
}


def get_plugin_info() -> Dict[str, Any]:
    """
    Get plugin information for service discovery.
    
    Returns:
        dict: Plugin metadata including version, capabilities, and requirements
    """
    return PLUGIN_METADATA.copy()


# Module initialization
__all__ = [
    "get_plugin_info",
    "PLUGIN_METADATA",
    # DAG Engine
    "DAGEngine",
    "DAGNode",
    "NodeStatus",
    # State Machine
    "StateMachine",
    "ExecutionState",
    "ExecutionOrchestrator",
    "StateTransition",
    # Partial Rollback
    "PartialRollbackManager",
    "RollbackLevel",
    "RollbackStatus",
    "Checkpoint",
    "RollbackOperation",
]

