"""
SynergyMesh Governance Automation System

This package provides the governance automation framework including:
- Main launcher coordinating 14 automation engines
- Individual engines for each governance dimension
- Task coordination and metrics collection
- Integration with existing systems
"""

__version__ = "1.0.0"
__author__ = "SynergyMesh Team"

from .governance_automation_launcher import (
    GovernanceAutomationLauncher,
    GovernanceAutomationEngine,
    AutomationTask,
    EngineStatus,
    HealthLevel,
)

__all__ = [
    "GovernanceAutomationLauncher",
    "GovernanceAutomationEngine",
    "AutomationTask",
    "EngineStatus",
    "HealthLevel",
]
