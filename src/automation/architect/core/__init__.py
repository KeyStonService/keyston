"""
Automation Architect - Core Module
企業級自動化代碼分析與修復系統 - 核心模組
"""

__version__ = "2.0.0"
__author__ = "SLASolve Team"
__license__ = "MIT"

from .analysis import StaticAnalyzer, SecurityScanner, PerformanceAnalyzer
from .repair import RuleEngine, ASTTransformer, RepairVerifier
from .orchestration import AnalysisPipeline, EventBus

__all__ = [
    "StaticAnalyzer",
    "SecurityScanner",
    "PerformanceAnalyzer",
    "RuleEngine",
    "ASTTransformer",
    "RepairVerifier",
    "AnalysisPipeline",
    "EventBus",
]
