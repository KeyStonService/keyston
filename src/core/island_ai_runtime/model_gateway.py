#!/usr/bin/env python3
"""
Model Gateway - 模型閘道
LLM Provider Selection and Routing

支援多種 LLM 提供者：OpenAI, Anthropic, Local, BYOM
"""

import os
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ModelProvider(Enum):
    """模型提供者枚舉"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    BYOM = "byom"


class RoutingStrategy(Enum):
    """路由策略枚舉"""

    COST_OPTIMIZED = "cost-optimized"
    PERFORMANCE = "performance"
    ROUND_ROBIN = "round-robin"


@dataclass
class ModelConfig:
    """模型配置"""

    id: str
    provider: ModelProvider
    type: str  # chat, reasoning, code, embedding
    max_tokens: int
    default: bool = False


@dataclass
class CompletionRequest:
    """完成請求"""

    messages: list[dict[str, str]]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stream: bool = False


@dataclass
class CompletionResponse:
    """完成回應"""

    content: str
    model: str
    usage: dict[str, int]
    finish_reason: str


class BaseModelClient(ABC):
    """模型客戶端基類"""

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """執行完成請求"""
        pass

    @abstractmethod
    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """執行串流完成請求"""
        pass


class OpenAIClient(BaseModelClient):
    """OpenAI 客戶端"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """執行 OpenAI 完成請求"""
        # 實際實現會使用 openai 套件
        return CompletionResponse(
            content="",
            model=request.model or "gpt-4o",
            usage={"prompt_tokens": 0, "completion_tokens": 0},
            finish_reason="stop",
        )

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """執行 OpenAI 串流請求"""
        yield ""


class AnthropicClient(BaseModelClient):
    """Anthropic 客戶端"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """執行 Anthropic 完成請求"""
        return CompletionResponse(
            content="",
            model=request.model or "claude-sonnet-4-20250514",
            usage={"prompt_tokens": 0, "completion_tokens": 0},
            finish_reason="stop",
        )

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """執行 Anthropic 串流請求"""
        yield ""


class ModelGateway:
    """
    模型閘道

    負責管理和路由 LLM 請求到適當的提供者。

    功能：
    - 多模型路由
    - 負載均衡
    - 模型切換
    - 成本優化
    - 故障轉移
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.clients: dict[ModelProvider, BaseModelClient] = {}
        self.models: dict[str, ModelConfig] = {}
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """初始化模型客戶端"""
        providers = self.config.get("providers", {})

        if providers.get("openai", {}).get("enabled", True):
            self.clients[ModelProvider.OPENAI] = OpenAIClient()

        if providers.get("anthropic", {}).get("enabled", True):
            self.clients[ModelProvider.ANTHROPIC] = AnthropicClient()

    def get_default_model(self) -> str:
        """獲取預設模型"""
        return self.config.get("default_provider", "openai")

    async def complete(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs: Any
    ) -> CompletionResponse:
        """
        執行完成請求

        Args:
            messages: 對話訊息列表
            model: 指定模型 ID
            **kwargs: 其他參數

        Returns:
            CompletionResponse: 完成回應
        """
        request = CompletionRequest(messages=messages, model=model, **kwargs)

        # 根據模型選擇客戶端
        provider = self._get_provider_for_model(model)
        client = self.clients.get(provider)

        if not client:
            raise ValueError(f"Provider not available: {provider}")

        return await client.complete(request)

    async def stream(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs: Any
    ) -> AsyncIterator[str]:
        """執行串流完成請求"""
        request = CompletionRequest(messages=messages, model=model, stream=True, **kwargs)

        provider = self._get_provider_for_model(model)
        client = self.clients.get(provider)

        if not client:
            raise ValueError(f"Provider not available: {provider}")

        async for chunk in client.stream(request):
            yield chunk

    def _get_provider_for_model(self, model: str | None) -> ModelProvider:
        """根據模型 ID 獲取提供者"""
        if not model:
            return ModelProvider.OPENAI

        if model.startswith("gpt") or model.startswith("o1"):
            return ModelProvider.OPENAI
        elif model.startswith("claude"):
            return ModelProvider.ANTHROPIC
        else:
            return ModelProvider.OPENAI

    def list_models(self) -> list[str]:
        """列出所有可用模型"""
        models = []
        for provider_config in self.config.get("providers", {}).values():
            if provider_config.get("enabled", False):
                for model in provider_config.get("models", []):
                    models.append(model.get("id", ""))
        return models
