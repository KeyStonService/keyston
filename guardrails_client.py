"""Shared guardrails-first OpenAI client helper.

This module centralizes OpenAI client creation. It prefers GuardrailsOpenAI when
available, falls back to OpenAI otherwise, and exposes a small surface:
    - get_api_key(): read configured API key (AI_INTEGRATIONS_OPENAI_API_KEY preferred)
    - client_available(): detect whether a usable client can be built
    - build_client(): return a configured client instance
    - chat_completion(): convenience wrapper for chat completions
"""

import os
from typing import Any, Dict, List, Optional, Tuple


def _safe_import(module_name: str, attr: str) -> Tuple[Optional[Any], bool]:
    try:
        module = __import__(module_name, fromlist=[attr])
        return getattr(module, attr), True
    except ImportError:
        return None, False


GuardrailsOpenAI, HAS_GUARDRAILS_CLIENT = _safe_import("guardrails.hub", "GuardrailsOpenAI")
if GuardrailsOpenAI is None:
    GuardrailsOpenAI, HAS_GUARDRAILS_CLIENT = _safe_import("guardrails", "GuardrailsOpenAI")
OpenAI, HAS_OPENAI_CLIENT = _safe_import("openai", "OpenAI")

DEFAULT_MODEL = (
    os.environ.get("AI_INTEGRATIONS_OPENAI_MODEL")
    or os.environ.get("OPENAI_MODEL")
    or "gpt-4o-mini"
)


def _get_api_key() -> Optional[str]:
    return os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY") or os.environ.get(
        "OPENAI_API_KEY"
    )


def get_api_key() -> Optional[str]:
    """Public helper to fetch the configured AI API key from environment."""
    return _get_api_key()


def _get_base_url() -> Optional[str]:
    return os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL") or os.environ.get(
        "OPENAI_BASE_URL"
    )


def client_available(api_key: Optional[str] = None) -> bool:
    key = api_key or _get_api_key()
    return bool(key) and (HAS_GUARDRAILS_CLIENT or HAS_OPENAI_CLIENT)


def is_client_available(api_key: Optional[str] = None) -> bool:
    """Alias for client_available for readability."""
    return client_available(api_key=api_key)


def build_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> Any:
    """Build a Guardrails-enabled OpenAI client.

    Returns:
        GuardrailsOpenAI when available, otherwise an OpenAI client.

    Raises:
        ImportError: if neither guardrails nor openai packages are installed.
        ValueError: if no API key is provided.
    """
    api_key = api_key or _get_api_key()
    base_url = base_url or _get_base_url()

    if not api_key:
        raise ValueError(
            "API key is required to build the AI client. Set AI_INTEGRATIONS_OPENAI_API_KEY (preferred, checked first) "
            "or OPENAI_API_KEY."
        )

    client_kwargs: Dict[str, Any] = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    if HAS_GUARDRAILS_CLIENT:
        return GuardrailsOpenAI(**client_kwargs)

    if not HAS_OPENAI_CLIENT:
        raise ImportError(
            "openai package is required to build the AI client when guardrails is unavailable. "
            "Install via `pip install openai`."
        )

    return OpenAI(**client_kwargs)


def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """Send a chat completion request through the configured AI client."""
    client = build_client(api_key=api_key, base_url=base_url)
    payload: Dict[str, Any] = {"model": model or DEFAULT_MODEL, "messages": messages}

    if tools:
        payload["tools"] = tools

    payload.update(kwargs)
    return client.chat.completions.create(**payload)
