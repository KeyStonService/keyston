#!/usr/bin/env python3
"""
Island AI Runtime - 島嶼 AI 運行時
Core Runtime Orchestrator

整合所有模組，提供統一的 AI 運行時環境
"""

import os
from dataclasses import dataclass, field
from typing import Any

import yaml

from .agent_framework import AgentFramework, Task
from .knowledge_engine import KnowledgeEngine
from .model_gateway import CompletionRequest, ModelGateway
from .safety_constitution import SafetyConstitution, SafetyResult
from .session_memory import MessageRole, SessionMemory
from .tool_executor import ExecutionResult, ToolExecutor


@dataclass
class RuntimeConfig:
    """運行時配置"""

    name: str = "Island AI Runtime"
    version: str = "1.0.0"
    model_gateway: dict[str, Any] = field(default_factory=dict)
    agent_framework: dict[str, Any] = field(default_factory=dict)
    knowledge_engine: dict[str, Any] = field(default_factory=dict)
    safety_constitution: dict[str, Any] = field(default_factory=dict)
    tool_executor: dict[str, Any] = field(default_factory=dict)
    session_memory: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeStatus:
    """運行時狀態"""

    initialized: bool = False
    modules_loaded: list[str] = field(default_factory=list)
    active_sessions: int = 0
    total_requests: int = 0
    errors: list[str] = field(default_factory=list)


class IslandAIRuntime:
    """
    Island AI 運行時

    統一的 AI 運行時環境，整合：
    - Model Gateway: LLM 提供者路由
    - Agent Framework: 多代理協作
    - Knowledge Engine: 知識檢索
    - Safety Constitution: 安全保障
    - Tool Executor: 工具執行
    - Session Memory: 會話記憶

    用法：
        runtime = IslandAIRuntime.from_config("config/island-ai-runtime.yaml")
        await runtime.initialize()

        response = await runtime.complete("Hello, world!")
        result = await runtime.execute_task("Build a feature")
    """

    VERSION = "1.0.0"

    def __init__(self, config: RuntimeConfig | None = None):
        self.config = config or RuntimeConfig()
        self.status = RuntimeStatus()

        # 初始化各模組
        self.model_gateway = ModelGateway(self.config.model_gateway)
        self.agent_framework = AgentFramework(self.config.agent_framework)
        self.knowledge_engine = KnowledgeEngine(self.config.knowledge_engine)
        self.safety_constitution = SafetyConstitution(self.config.safety_constitution)
        self.tool_executor = ToolExecutor(self.config.tool_executor)
        self.session_memory = SessionMemory(self.config.session_memory)

    @classmethod
    def from_config(cls, config_path: str) -> "IslandAIRuntime":
        """從配置文件創建運行時"""
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)

        config = RuntimeConfig(
            name=config_dict.get("name", "Island AI Runtime"),
            version=config_dict.get("version", "1.0.0"),
            model_gateway=config_dict.get("model_gateway", {}),
            agent_framework=config_dict.get("agent_framework", {}),
            knowledge_engine=config_dict.get("knowledge_engine", {}),
            safety_constitution=config_dict.get("safety_constitution", {}),
            tool_executor=config_dict.get("tool_executor", {}),
            session_memory=config_dict.get("session_memory", {}),
        )

        return cls(config)

    @classmethod
    def from_env(cls) -> "IslandAIRuntime":
        """從環境變數創建運行時"""
        config = RuntimeConfig(
            model_gateway={
                "default_provider": os.getenv("ISLAND_AI_DEFAULT_PROVIDER", "openai"),
                "providers": {
                    "openai": {
                        "api_key": os.getenv("OPENAI_API_KEY"),
                        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                    },
                    "anthropic": {
                        "api_key": os.getenv("ANTHROPIC_API_KEY"),
                        "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                    },
                },
            }
        )

        return cls(config)

    async def initialize(self) -> bool:
        """初始化運行時"""
        try:
            # 標記各模組已載入
            self.status.modules_loaded = [
                "model_gateway",
                "agent_framework",
                "knowledge_engine",
                "safety_constitution",
                "tool_executor",
                "session_memory",
            ]

            self.status.initialized = True
            return True

        except Exception as e:
            self.status.errors.append(str(e))
            return False

    async def complete(self, prompt: str, system_prompt: str | None = None, **kwargs: Any) -> str:
        """執行 LLM 完成"""
        # 安全檢查
        safety_result = self.safety_constitution.check_content(prompt)
        if not safety_result.is_safe:
            return f"[BLOCKED] {safety_result.violations[0].recommendation}"

        # 添加到記憶
        self.session_memory.add_message(MessageRole.USER, prompt)

        # 獲取上下文
        context = self.session_memory.get_context()

        # 創建請求
        request = CompletionRequest(messages=context, system_prompt=system_prompt, **kwargs)

        # 調用 Model Gateway
        response = await self.model_gateway.complete(request)

        # 添加回應到記憶
        self.session_memory.add_message(MessageRole.ASSISTANT, response.content)

        self.status.total_requests += 1
        return response.content

    async def execute_task(
        self, task_description: str, task_type: str = "development"
    ) -> dict[str, Any]:
        """執行任務"""
        # 創建任務
        task = Task(
            id=f"task_{self.status.total_requests}",
            name=task_description,
            description=task_description,
        )

        # 使用代理框架編排
        results = await self.agent_framework.orchestrate([task])

        self.status.total_requests += 1
        return results

    async def search_knowledge(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """搜索知識庫"""
        results = await self.knowledge_engine.search(query, top_k)
        return [
            {"path": r.node.path, "name": r.node.name, "score": r.score, "context": r.context}
            for r in results
        ]

    async def execute_code(self, code: str, language: str = "python") -> ExecutionResult:
        """執行代碼"""
        # 安全檢查
        safety_result = self.safety_constitution.check_content(code)
        if not safety_result.is_safe:
            from .tool_executor import ExecutionResult, ExecutionStatus

            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                error=f"Code blocked: {safety_result.violations[0].recommendation}",
            )

        return await self.tool_executor.execute_code(code, language)

    def check_safety(self, content: str) -> SafetyResult:
        """檢查內容安全性"""
        return self.safety_constitution.check_content(content)

    def get_status(self) -> dict[str, Any]:
        """獲取運行時狀態"""
        return {
            "name": self.config.name,
            "version": self.VERSION,
            "initialized": self.status.initialized,
            "modules_loaded": self.status.modules_loaded,
            "active_sessions": self.status.active_sessions,
            "total_requests": self.status.total_requests,
            "errors": self.status.errors,
            "memory_summary": self.session_memory.summarize(),
        }

    def reset(self) -> None:
        """重置運行時"""
        self.session_memory.clear()
        self.status.active_sessions = 0
        self.status.errors.clear()


# 便捷函數
async def create_runtime(config_path: str | None = None) -> IslandAIRuntime:
    """創建並初始化運行時"""
    if config_path:
        runtime = IslandAIRuntime.from_config(config_path)
    else:
        runtime = IslandAIRuntime.from_env()

    await runtime.initialize()
    return runtime
