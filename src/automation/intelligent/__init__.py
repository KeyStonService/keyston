"""
Intelligent Automation Module
智能自動化模組

High-value capabilities extracted from OJ-agent for autonomous systems.
核心商業價值能力，專為自動化系統設計。
"""

__version__ = "1.0.0"
__author__ = "SLASolve Team"

# Handle both package and standalone imports
try:
    from .pipeline_service import pipeline_service, PipelineService
except ImportError:
    # When running standalone (e.g., in tests), use absolute imports
    try:
        from pipeline_service import pipeline_service, PipelineService
    except ImportError:
        # Module not available in this context
        pipeline_service = None
        PipelineService = None

__all__ = [
    "pipeline_service",
    "PipelineService",
]
