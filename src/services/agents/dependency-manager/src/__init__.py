"""
Dependency Manager Agent - 依賴管理代理
SynergyMesh 智能自動化系統組件

負責管理項目依賴、檢測過時套件、分析依賴漏洞和自動化更新流程。
"""

from .engine import DependencyManager

__version__ = "1.0.0"
__all__ = ["DependencyManager"]
