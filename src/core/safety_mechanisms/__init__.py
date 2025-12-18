"""
SynergyMesh Safety Mechanisms System (Phase 10)
安全機制系統 - 防止災難

Core Components:
- CircuitBreaker - 斷路器系統
- EscalationLadder - 升級階梯系統
- RollbackSystem - 回滾系統
- AnomalyDetector - 異常檢測器
- EmergencyStop - 緊急停止系統
- SafetyNet - 多層安全網

Design Principles:
1. 預防勝於治療 - Prevention over cure
2. 多層防護 - Multi-layer protection
3. 快速回滾 - Fast rollback
4. 持續學習 - Continuous learning
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerConfig,
    CircuitBreakerRegistry,
)

from .escalation_ladder import (
    EscalationLadder,
    EscalationLevel,
    EscalationAction,
    EscalationConfig,
)

from .rollback_system import (
    RollbackSystem,
    Snapshot,
    SnapshotType,
    RollbackStrategy,
    RollbackResult,
)

from .anomaly_detector import (
    AnomalyDetector,
    AnomalyType,
    AnomalySeverity,
    AnomalyAlert,
    DetectionStrategy,
)

from .emergency_stop import (
    EmergencyStop,
    StopReason,
    StopScope,
    EmergencyStopResult,
)

from .safety_net import (
    SafetyNet,
    SafetyLayer,
    SafetyCheck,
    SafetyCheckResult,
    SafetyNetConfig,
)

__all__ = [
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerState',
    'CircuitBreakerConfig',
    'CircuitBreakerRegistry',
    # Escalation Ladder
    'EscalationLadder',
    'EscalationLevel',
    'EscalationAction',
    'EscalationConfig',
    # Rollback System
    'RollbackSystem',
    'Snapshot',
    'SnapshotType',
    'RollbackStrategy',
    'RollbackResult',
    # Anomaly Detector
    'AnomalyDetector',
    'AnomalyType',
    'AnomalySeverity',
    'AnomalyAlert',
    'DetectionStrategy',
    # Emergency Stop
    'EmergencyStop',
    'StopReason',
    'StopScope',
    'EmergencyStopResult',
    # Safety Net
    'SafetyNet',
    'SafetyLayer',
    'SafetyCheck',
    'SafetyCheckResult',
    'SafetyNetConfig',
]
