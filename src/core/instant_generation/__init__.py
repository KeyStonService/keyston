"""
Instant Generation Driven Architecture
革命性即時生成架構核心模組

繞過沙箱服務限制，實現10分鐘內完整系統生成
包含6個AI代理的並行處理網絡、自我修復故障隔離系統
"""

from .agents import (
    InputAnalysisAgent,
    CodeGenerationAgent,
    ArchitectureDesignAgent,
    TestingAgent,
    DeploymentAgent,
    OptimizationAgent
)

from .workflows import (
    InstantGenerationWorkflow,
    DAGOrchestrator,
    ParallelProcessor
)

from .optimization import (
    PerformanceOptimizer,
    ResourceManager,
    SelfHealingSystem
)

from .monitoring import (
    RealTimeMonitor,
    PerformanceTracker,
    AlertSystem
)

__version__ = "1.0.0"
__author__ = "MachineNativeOps Team"
__description__ = "Revolutionary Instant Generation Architecture"

# Core configuration
INSTANT_GENERATION_CONFIG = {
    "target_time": "10_minutes",
    "max_parallel_agents": 6,
    "self_healing_enabled": True,
    "bypass_sandbox": True,
    "fault_tolerance": "high"
}

# Export main classes
__all__ = [
    "InstantGenerationWorkflow",
    "DAGOrchestrator",
    "ParallelProcessor",
    "SelfHealingSystem",
    "RealTimeMonitor",
    "InputAnalysisAgent",
    "CodeGenerationAgent",
    "ArchitectureDesignAgent",
    "TestingAgent",
    "DeploymentAgent",
    "OptimizationAgent"
]