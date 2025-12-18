"""
Core Modules - Unified Module Management
統一模組管理入口

整合的模組列表:
- mind_matrix: 心智矩陣 (執行系統、多代理超圖)
- training_system: 訓練系統 (知識庫、技能訓練)
- virtual_experts: 虛擬專家 (領域專家、專家團隊)
- ci_error_handler: CI 錯誤處理 (自動修復、狀態追蹤)
- cloud_agent_delegation: 雲端代理委派 (負載均衡、任務路由)
- main_system: 主系統 (自動化管線、階段編排)
- mcp_servers_enhanced: 增強型 MCP 服務器
- tech_stack: 技術棧 (框架整合、多代理協調)
- ai_constitution: AI 憲法 (基本法則、護欄)
- execution_architecture: 執行架構 (代理編排、工具系統)
- monitoring_system: 監控系統 (自動診斷、智能監控)
- yaml_module_system: YAML 模組系統
- execution_engine: 執行引擎
"""

from typing import Any

# 模組註冊表
MODULE_REGISTRY: dict[str, dict[str, Any]] = {
    "mind_matrix": {
        "description": "心智矩陣 - 執行系統與多代理超圖",
        "entry_point": "core.modules.mind_matrix.main",
        "dependencies": ["training_system", "virtual_experts"],
    },
    "training_system": {
        "description": "訓練系統 - 知識庫與技能訓練",
        "entry_point": "core.modules.training_system.knowledge_base",
        "dependencies": [],
    },
    "virtual_experts": {
        "description": "虛擬專家 - 領域專家與專家團隊",
        "entry_point": "core.modules.virtual_experts.expert_team",
        "dependencies": ["training_system"],
    },
    "ci_error_handler": {
        "description": "CI 錯誤處理 - 自動修復與狀態追蹤",
        "entry_point": "core.modules.ci_error_handler.auto_fix_engine",
        "dependencies": ["monitoring_system"],
    },
    "cloud_agent_delegation": {
        "description": "雲端代理委派 - 負載均衡與任務路由",
        "entry_point": "core.modules.cloud_agent_delegation.delegation_manager",
        "dependencies": ["execution_architecture"],
    },
    "main_system": {
        "description": "主系統 - 自動化管線與階段編排",
        "entry_point": "core.modules.main_system.synergymesh_core",
        "dependencies": ["mind_matrix", "ai_constitution"],
    },
    "mcp_servers_enhanced": {
        "description": "增強型 MCP 服務器 - 工具註冊與工作流編排",
        "entry_point": "core.modules.mcp_servers_enhanced.mcp_server_manager",
        "dependencies": ["execution_architecture"],
    },
    "tech_stack": {
        "description": "技術棧 - 框架整合與多代理協調",
        "entry_point": "core.modules.tech_stack.framework_integrations",
        "dependencies": [],
    },
    "ai_constitution": {
        "description": "AI 憲法 - 基本法則、護欄與策略提示",
        "entry_point": "core.modules.ai_constitution.constitution_engine",
        "dependencies": [],
    },
    "execution_architecture": {
        "description": "執行架構 - 代理編排、工具系統與 MCP 整合",
        "entry_point": "core.modules.execution_architecture.agent_orchestration",
        "dependencies": ["tech_stack"],
    },
    "monitoring_system": {
        "description": "監控系統 - 自動診斷、智能監控與異常檢測",
        "entry_point": "core.modules.monitoring_system.observability_platform",
        "dependencies": [],
    },
    "yaml_module_system": {
        "description": "YAML 模組系統 - 配置驅動的模組載入",
        "entry_point": "core.modules.yaml_module_system",
        "dependencies": [],
    },
    "execution_engine": {
        "description": "執行引擎 - 任務執行與結果處理",
        "entry_point": "core.modules.execution_engine",
        "dependencies": ["execution_architecture"],
    },
}


def get_module_info(module_name: str) -> dict[str, Any] | None:
    """取得模組資訊"""
    return MODULE_REGISTRY.get(module_name)


def list_modules() -> list[str]:
    """列出所有可用模組"""
    return list(MODULE_REGISTRY.keys())


def get_module_dependencies(module_name: str) -> list[str]:
    """取得模組依賴"""
    info = get_module_info(module_name)
    return info.get("dependencies", []) if info else []


__all__ = [
    "MODULE_REGISTRY",
    "get_module_info",
    "list_modules",
    "get_module_dependencies",
]
