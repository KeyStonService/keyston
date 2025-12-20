"""
AI Agents Network for Instant Generation
即時生成AI代理網絡

6個專業化AI代理實現並行處理，每個代理專注於特定領域
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    """代理類型枚舉"""
    INPUT_ANALYSIS = "input_analysis"
    CODE_GENERATION = "code_generation"
    ARCHITECTURE_DESIGN = "architecture_design"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    OPTIMIZATION = "optimization"

@dataclass
class AgentTask:
    """代理任務數據結構"""
    task_id: str
    agent_type: AgentType
    input_data: Dict[str, Any]
    priority: int = 1
    timeout: int = 300  # 5分鐘超時
    dependencies: List[str] = None

@dataclass
class AgentResult:
    """代理執行結果"""
    task_id: str
    agent_type: AgentType
    success: bool
    output_data: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None

class BaseAgent(ABC):
    """基礎代理抽象類"""
    
    def __init__(self, agent_type: AgentType, config: Dict[str, Any] = None):
        self.agent_type = agent_type
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{agent_type.value}")
        
    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResult:
        """處理任務的抽象方法"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據"""
        pass
    
    async def execute_with_timeout(self, task: AgentTask) -> AgentResult:
        """帶超時控制的任務執行"""
        try:
            result = await asyncio.wait_for(
                self.process_task(task),
                timeout=task.timeout
            )
            return result
        except asyncio.TimeoutError:
            self.logger.error(f"Task {task.task_id} timed out")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=False,
                output_data={},
                execution_time=task.timeout,
                error_message="Task execution timeout"
            )
        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=False,
                output_data={},
                execution_time=0,
                error_message=str(e)
            )

# Import specific agent implementations
from .input_analysis_agent import InputAnalysisAgent
from .code_generation_agent import CodeGenerationAgent
from .architecture_design_agent import ArchitectureDesignAgent
from .testing_agent import TestingAgent
from .deployment_agent import DeploymentAgent
from .optimization_agent import OptimizationAgent

# Agent registry for dynamic loading
AGENT_REGISTRY = {
    AgentType.INPUT_ANALYSIS: InputAnalysisAgent,
    AgentType.CODE_GENERATION: CodeGenerationAgent,
    AgentType.ARCHITECTURE_DESIGN: ArchitectureDesignAgent,
    AgentType.TESTING: TestingAgent,
    AgentType.DEPLOYMENT: DeploymentAgent,
    AgentType.OPTIMIZATION: OptimizationAgent
}

def create_agent(agent_type: AgentType, config: Dict[str, Any] = None) -> BaseAgent:
    """工廠方法：創建指定類型的代理"""
    agent_class = AGENT_REGISTRY.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return agent_class(agent_type, config)

__all__ = [
    "BaseAgent",
    "AgentTask",
    "AgentResult",
    "AgentType",
    "create_agent",
    "AGENT_REGISTRY",
    "InputAnalysisAgent",
    "CodeGenerationAgent",
    "ArchitectureDesignAgent",
    "TestingAgent",
    "DeploymentAgent",
    "OptimizationAgent"
]