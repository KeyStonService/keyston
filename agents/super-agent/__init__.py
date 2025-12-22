"""
AAPS SuperAgent - Multi-Agent Orchestrator

SuperAgent is the central coordinator in the AAPS multi-agent MPC architecture.
It provides:
- Message routing and distribution between agents
- Incident lifecycle state machine management
- Agent coordination and consensus decision making
- Complete audit trail and provenance tracking
- Prometheus-compatible metrics exposition
- Circuit breaker and retry mechanisms for resilience
"""

__version__ = "1.0.0"
__author__ = "AAPS Team"
__all__ = [
    "models",
    "services",
    "utils",
    "config",
]
