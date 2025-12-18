# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh Mind Matrix Runtime Module
#                    心智矩陣運行時模組
# ═══════════════════════════════════════════════════════════════════════════════
"""
Mind Matrix Runtime Module.

This module provides the core MindMatrix class for managing the topology
configuration with strict schema validation using Pydantic, and the
ExecutiveAutoController for fully autonomous executive operations.
"""

from runtime.mind_matrix.executive_auto import ExecutiveAutoController
from runtime.mind_matrix.main import (
    ExecutiveLayer,
    ExecutiveRole,
    MindMatrix,
    MindMatrixModel,
    ToolPipeline,
    YamlValidationPipeline,
)

__all__ = [
    "MindMatrix",
    "MindMatrixModel",
    "ExecutiveRole",
    "ExecutiveLayer",
    "ToolPipeline",
    "YamlValidationPipeline",
    "ExecutiveAutoController",
]

__version__ = "1.0.0"
