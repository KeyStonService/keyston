"""
SynergyMesh Technology Stack Architecture (技術棧架構)

This module provides the recommended technology stack and framework integration
for the SynergyMesh autonomous coordination grid system.

Core Principle: Python (80% of AI agents) + TypeScript (System orchestration)

Based on research findings:
- Python dominates with 51% developer adoption for AI [4]
- LangChain, CrewAI, AutoGen for multi-agent orchestration [2][7]
- Hybrid architecture for best of both worlds
"""

from .architecture_config import (
    ArchitectureLayer,
    FrameworkConfig,
    LanguageConfig,
    TechStackConfig,
    get_recommended_stack,
)
from .framework_integrations import (
    AutoGenIntegration,
    CrewAIIntegration,
    FrameworkIntegration,
    FrameworkOrchestrator,
    LangChainIntegration,
    LangGraphIntegration,
)
from .multi_agent_coordinator import (
    AgentCapability,
    AgentCommunicationBus,
    AgentRole,
    AgentTeam,
    MultiAgentCoordinator,
    TaskRouter,
)
from .python_bridge import (
    PackageManager,
    PythonBridge,
    PythonEnvironment,
    PythonExecutor,
)

__all__ = [
    # Architecture Config
    'TechStackConfig',
    'LanguageConfig',
    'FrameworkConfig',
    'ArchitectureLayer',
    'get_recommended_stack',
    # Framework Integrations
    'FrameworkIntegration',
    'LangChainIntegration',
    'CrewAIIntegration',
    'AutoGenIntegration',
    'LangGraphIntegration',
    'FrameworkOrchestrator',
    # Multi-Agent Coordinator
    'AgentRole',
    'AgentCapability',
    'MultiAgentCoordinator',
    'AgentTeam',
    'TaskRouter',
    'AgentCommunicationBus',
    # Python Bridge
    'PythonBridge',
    'PythonEnvironment',
    'PackageManager',
    'PythonExecutor',
]

__version__ = '1.0.0'
