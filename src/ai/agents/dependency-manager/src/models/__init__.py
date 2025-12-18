"""
數據模型 - Data Models
依賴管理代理的核心數據結構
"""

from .dependency import Dependency, DependencyAnalysis
from .vulnerability import Vulnerability, VulnerabilitySeverity
from .update import Update, UpdateResult, UpdateType

__all__ = [
    "Dependency",
    "DependencyAnalysis", 
    "Vulnerability",
    "VulnerabilitySeverity",
    "Update",
    "UpdateResult",
    "UpdateType"
]
