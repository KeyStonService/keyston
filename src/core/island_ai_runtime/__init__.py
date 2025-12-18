#!/usr/bin/env python3
"""
Island AI Runtime - 核心 AI 執行層
Core AI Execution Layer v1.0

統一的智能自動化平台，整合多模型、多代理、知識引擎等功能。
"""

from .agent_framework import Agent, AgentFramework
from .knowledge_engine import KnowledgeEngine
from .model_gateway import ModelGateway
from .runtime import IslandAIRuntime
from .safety_constitution import SafetyConstitution
from .session_memory import SessionMemory
from .tool_executor import ToolExecutor

__all__ = [
    "IslandAIRuntime",
    "ModelGateway",
    "AgentFramework",
    "Agent",
    "KnowledgeEngine",
    "SafetyConstitution",
    "ToolExecutor",
    "SessionMemory",
]

__version__ = "1.0.0"
__author__ = "SynergyMesh Team"
