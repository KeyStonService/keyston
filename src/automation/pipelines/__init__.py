"""
Automation Pipelines Package - 自動化管線套件
===========================================

Reusable automation pipelines for SynergyMesh
"""

from .instant_execution_pipeline import (
    InstantExecutionPipeline,
    PipelineContext,
    PipelineStage,
    StageStatus,
    StageResult,
)

__all__ = [
    "InstantExecutionPipeline",
    "PipelineContext",
    "PipelineStage",
    "StageStatus",
    "StageResult",
]
