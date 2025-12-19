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

# ===== 工具函數：動態導入 kebab-case 模塊 =====
def _import_kebab_module(module_name: str, file_name: str):
    """動態導入 kebab-case 的 Python 模塊"""
    module_path = Path(__file__).parent / file_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    return None

# ===== 基礎協調器 =====
synergy_mesh = _import_kebab_module("synergy_mesh_orchestrator", "synergy-mesh-orchestrator.py")
if synergy_mesh:
    SynergyMeshOrchestrator = synergy_mesh.SynergyMeshOrchestrator
    ExecutionResult = synergy_mesh.ExecutionResult
    SystemStatus = synergy_mesh.SystemStatus
    ExecutionStatus = synergy_mesh.ExecutionStatus
    ComponentType = synergy_mesh.ComponentType
else:
    raise ImportError("Failed to import synergy-mesh-orchestrator.py")

# ===== 企業級協調器 =====
enterprise_mesh = _import_kebab_module("enterprise_synergy_mesh_orchestrator", "enterprise-synergy-mesh-orchestrator.py")
if enterprise_mesh:
    EnterpriseSynergyMeshOrchestrator = enterprise_mesh.EnterpriseSynergyMeshOrchestrator
    TenantConfig = enterprise_mesh.TenantConfig
    TenantTier = enterprise_mesh.TenantTier
    ResourceQuota = enterprise_mesh.ResourceQuota
    RetryPolicy = enterprise_mesh.RetryPolicy
    AuditLog = enterprise_mesh.AuditLog
else:
    raise ImportError("Failed to import enterprise-synergy-mesh-orchestrator.py")

# ===== 依賴解析 =====
dependency_resolver = _import_kebab_module("dependency_resolver", "dependency-resolver.py")
if dependency_resolver:
    DependencyResolver = dependency_resolver.DependencyResolver
    DependencyNode = dependency_resolver.DependencyNode
    ExecutionPhase = dependency_resolver.ExecutionPhase
else:
    raise ImportError("Failed to import dependency-resolver.py")

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
