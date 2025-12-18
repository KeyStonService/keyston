"""
Orchestrators Module - 協調器模組

提供統一的系統協調和管理功能：
- 基礎協調器 (SynergyMeshOrchestrator)
- 島嶼協調器 (LanguageIslandOrchestrator)
- 企業級協調器 (EnterpriseSynergyMeshOrchestrator)
- 依賴解析 (DependencyResolver)
"""

import importlib.util
import sys
from pathlib import Path

# ===== 基礎協調器 =====
from .synergy_mesh_orchestrator import (
    SynergyMeshOrchestrator,
    ExecutionResult,
    SystemStatus,
    ExecutionStatus,
    ComponentType
)

# ===== 企業級協調器 =====
from .enterprise_synergy_mesh_orchestrator import (
    EnterpriseSynergyMeshOrchestrator,
    TenantConfig,
    TenantTier,
    ResourceQuota,
    RetryPolicy,
    AuditLog
)

# ===== 依賴解析 =====
from .dependency_resolver import (
    DependencyResolver,
    DependencyNode,
    ExecutionPhase
)

# ===== 島嶼協調器 =====
# 使用 importlib 來處理 kebab-case 的文件名
spec = importlib.util.spec_from_file_location(
    "language_island_orchestrator",
    Path(__file__).parent / "language-island-orchestrator.py"
)
if spec and spec.loader:
    language_island_orchestrator = importlib.util.module_from_spec(spec)
    sys.modules["language_island_orchestrator"] = language_island_orchestrator
    spec.loader.exec_module(language_island_orchestrator)
    LanguageIslandOrchestrator = language_island_orchestrator.LanguageIslandOrchestrator
else:
    # 備用方案：使用絕對導入
    try:
        from .language_island_orchestrator import LanguageIslandOrchestrator
    except ImportError:
        LanguageIslandOrchestrator = None


__all__ = [
    # 基礎
    "SynergyMeshOrchestrator",
    "LanguageIslandOrchestrator",
    "ExecutionResult",
    "SystemStatus",
    "ExecutionStatus",
    "ComponentType",

    # 企業級
    "EnterpriseSynergyMeshOrchestrator",
    "TenantConfig",
    "TenantTier",
    "ResourceQuota",
    "RetryPolicy",
    "AuditLog",

    # 依賴管理
    "DependencyResolver",
    "DependencyNode",
    "ExecutionPhase"
]
