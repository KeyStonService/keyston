"""
SynergyMesh Core - 無人化自主協同網格系統
Autonomous Coordination Grid System

This module provides the core components for SynergyMesh's revolutionary
fully autonomous system grid that enables:

Phase 1 - Core Components:
1. Zero Technical Barrier - Natural language interface
2. Fully Autonomous - 24/7 self-operating capabilities
3. Intelligent Adaptation - Automatic learning and adjustment
4. Ecosystem Coordination - Independent yet coordinated subsystems

Phase 2 - Advanced Interaction & Orchestration:
5. Multi-modal Natural Language Interaction Layer (NLI)
6. Intent Understanding & Task Orchestration Layer

設計哲學: 讓程式服務於人類，而非人類服務於程式
"""

# Phase 1: Core Components
from .natural_language_processor import NaturalLanguageProcessor
from .autonomous_coordinator import AutonomousCoordinator
from .self_evolution_engine import SelfEvolutionEngine
from .ecosystem_orchestrator import EcosystemOrchestrator

# Phase 2: Advanced Interaction & Orchestration
from .nli_layer import NaturalLanguageInteractionLayer
from .orchestration_layer import IntentUnderstandingEngine, TaskOrchestrationEngine

__all__ = [
    # Phase 1
    "NaturalLanguageProcessor",
    "AutonomousCoordinator",
    "SelfEvolutionEngine",
    "EcosystemOrchestrator",
    # Phase 2
    "NaturalLanguageInteractionLayer",
    "IntentUnderstandingEngine",
    "TaskOrchestrationEngine",
]

__version__ = "2.0.0"
