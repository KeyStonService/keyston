"""
SynergyMesh Deep Verifiable YAML Module System
Phase 13: YAML Schema Validation, DevSecOps Policy Gate, SLSA Compliance

核心理念：
1. 將碎片化 YAML 提升為深度可驗證模組
2. 整合 DevSecOps Policy Gate 機制
3. 完整的 CI/CD 驗證流程
4. SLSA L3 合規性
5. 自動化證據生成
"""

from .audit_trail import (
    AuditAction,
    AuditEntry,
    AuditLogger,
    ChangeRecord,
    ChangeTracker,
)
from .ci_verification_pipeline import (
    CIVerificationPipeline,
    EvidenceCollector,
    PipelineStage,
    StageResult,
    VerificationReport,
)
from .policy_gate import (
    PolicyCategory,
    PolicyEvaluationResult,
    PolicyGate,
    PolicyRule,
    PolicySeverity,
    PolicyViolation,
)
from .slsa_compliance import (
    SBOM,
    ArtifactSigner,
    SBOMGenerator,
    SignedArtifact,
    SLSALevel,
    SLSAProvenance,
    SLSAProvenanceGenerator,
)
from .yaml_module_definition import (
    ChangelogEntry,
    LifecycleState,
    ModuleLifecycle,
    ModuleMetadata,
    ModuleOwner,
    TestVector,
    TestVectorType,
    YAMLModuleDefinition,
)
from .yaml_schema_validator import (
    SchemaRegistry,
    ValidationError,
    ValidationResult,
    YAMLSchemaValidator,
)

__all__ = [
    # YAML Module Definition
    'YAMLModuleDefinition',
    'ModuleMetadata',
    'ModuleOwner',
    'ModuleLifecycle',
    'LifecycleState',
    'TestVector',
    'TestVectorType',
    'ChangelogEntry',

    # Schema Validation
    'YAMLSchemaValidator',
    'ValidationResult',
    'ValidationError',
    'SchemaRegistry',

    # Policy Gate
    'PolicyGate',
    'PolicyRule',
    'PolicySeverity',
    'PolicyCategory',
    'PolicyEvaluationResult',
    'PolicyViolation',

    # CI Verification
    'CIVerificationPipeline',
    'PipelineStage',
    'StageResult',
    'VerificationReport',
    'EvidenceCollector',

    # SLSA Compliance
    'SLSAProvenanceGenerator',
    'SLSAProvenance',
    'ArtifactSigner',
    'SignedArtifact',
    'SBOMGenerator',
    'SBOM',
    'SLSALevel',

    # Audit Trail
    'AuditLogger',
    'AuditEntry',
    'AuditAction',
    'ChangeTracker',
    'ChangeRecord',
]
