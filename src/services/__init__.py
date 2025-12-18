"""
Services - 統一服務管理入口
Unified Services Management Entry Point

整合的服務:
- agents/: Agent 服務 (auto-repair, code-analyzer, dependency-manager, etc.)
- mcp/: MCP 服務器
"""

from typing import Any

# 服務註冊表
SERVICE_REGISTRY: dict[str, dict[str, Any]] = {
    # Agent 服務
    "auto-repair": {
        "type": "agent",
        "path": "services/agents/auto-repair",
        "description": "自動修復代理 - 自動檢測並修復代碼問題",
        "status": "active",
    },
    "code-analyzer": {
        "type": "agent",
        "path": "services/agents/code-analyzer",
        "description": "代碼分析器 - 靜態分析和代碼品質檢測",
        "status": "active",
    },
    "dependency-manager": {
        "type": "agent",
        "path": "services/agents/dependency-manager",
        "description": "依賴管理器 - 自動更新和漏洞掃描",
        "status": "active",
    },
    "vulnerability-detector": {
        "type": "agent",
        "path": "services/agents/vulnerability-detector",
        "description": "漏洞檢測器 - 安全漏洞掃描",
        "status": "active",
    },
    "orchestrator": {
        "type": "agent",
        "path": "services/agents/orchestrator",
        "description": "編排器 - 多代理協調",
        "status": "active",
    },
    # MCP 服務
    "mcp-servers": {
        "type": "mcp",
        "path": "services/mcp",
        "description": "MCP 服務器 - Model Context Protocol 實現",
        "status": "active",
        "entry_point": "npm start",
    },
}


def list_services(service_type: str | None = None) -> list[str]:
    """列出所有服務或指定類型的服務"""
    if service_type:
        return [name for name, info in SERVICE_REGISTRY.items() if info.get("type") == service_type]
    return list(SERVICE_REGISTRY.keys())


def get_service_info(service_name: str) -> dict[str, Any]:
    """獲取服務資訊"""
    return SERVICE_REGISTRY.get(service_name, {})


def get_agents() -> list[str]:
    """列出所有 Agent 服務"""
    return list_services("agent")


def get_mcp_servers() -> list[str]:
    """列出所有 MCP 服務"""
    return list_services("mcp")


__all__ = [
    "SERVICE_REGISTRY",
    "list_services",
    "get_service_info",
    "get_agents",
    "get_mcp_servers",
]
