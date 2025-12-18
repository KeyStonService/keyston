"""
SynergyMesh v2-multi-islands 套件

多語言自動化無人之島系統 - 高階應用整合層
"""

__version__ = "2.0.0"
__author__ = "SynergyMesh Team"

# 使用延遲導入以避免循環依賴
def get_islands():
    """取得島嶼類別"""
    from .islands import (
        BaseIsland,
        GoIsland,
        JavaIsland,
        PythonIsland,
        RustIsland,
        TypeScriptIsland,
    )
    return BaseIsland, RustIsland, GoIsland, TypeScriptIsland, PythonIsland, JavaIsland

def get_orchestrator():
    """取得協調器類別"""
    from .orchestrator import IslandOrchestrator
    return IslandOrchestrator

def get_config():
    """取得配置類別"""
    from .config import IslandConfig
    return IslandConfig

__all__ = [
    "__version__",
    "__author__",
    "get_islands",
    "get_orchestrator",
    "get_config",
]
