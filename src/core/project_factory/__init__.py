"""
═══════════════════════════════════════════════════════════
    Project Factory - 專案生成工廠
    One-Click Complete Project Generation System
═══════════════════════════════════════════════════════════

This module provides automated project generation capabilities,
creating complete deliverable matrices including source code, tests,
Docker, Kubernetes, CI/CD, and governance documentation.

本模組提供自動化專案生成能力，創建完整的交付物矩陣，包括源代碼、
測試、Docker、Kubernetes、CI/CD 和治理文檔。

Core Capabilities:
- Complete deliverable matrix generation
- Governance-compliant output
- Multiple language and framework support
- Automated validation and verification

Version: 1.0.0
Author: SynergyMesh Platform Team
"""

from .factory import ProjectFactory
from .spec import ProjectSpec, FeatureSpec, GovernanceSpec
from .generator import ProjectGenerator
from .templates import TemplateEngine
from .validator import GovernanceValidator

__all__ = [
    'ProjectFactory',
    'ProjectSpec',
    'FeatureSpec',
    'GovernanceSpec',
    'ProjectGenerator',
    'TemplateEngine',
    'GovernanceValidator',
]

__version__ = '1.0.0'
