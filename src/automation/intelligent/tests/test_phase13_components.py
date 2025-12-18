"""
Phase 13 Tests: Deep Verifiable YAML Module System
"""

import pytest
from datetime import datetime
from typing import Dict, Any

# Import Phase 13 components
import sys
sys.path.insert(0, '/home/runner/work/SynergyMesh/SynergyMesh')

from core.yaml_module_system.yaml_module_definition import (
    YAMLModuleDefinition,
    ModuleMetadata,
    ModuleOwner,
    ModuleLifecycle,
    LifecycleState,
    TestVector,
    TestVectorType,
    ChangelogEntry,
)
from core.yaml_module_system.yaml_schema_validator import (
    YAMLSchemaValidator,
    ValidationResult,
    ValidationError,
    SchemaRegistry,
    ValidationErrorType,
)
from core.yaml_module_system.policy_gate import (
    PolicyGate,
    PolicyRule,
    PolicySeverity,
    PolicyCategory,
    PolicyAction,
    PolicyViolation,
    PolicyEvaluationResult,
)
from core.yaml_module_system.ci_verification_pipeline import (
    CIVerificationPipeline,
    PipelineStage,
    PipelineStageType,
    StageResult,
    StageStatus,
    VerificationReport,
    EvidenceCollector,
    Evidence,
)
from core.yaml_module_system.slsa_compliance import (
    SLSAProvenanceGenerator,
    SLSAProvenance,
    ArtifactSigner,
    SignedArtifact,
    SBOMGenerator,
    SBOM,
    SLSALevel,
    SignatureAlgorithm,
)
from core.yaml_module_system.audit_trail import (
    AuditLogger,
    AuditEntry,
    AuditAction,
    AuditLevel,
    ChangeTracker,
    ChangeRecord,
)


# ============ YAML Module Definition Tests ============

class TestYAMLModuleDefinition:
    """Test YAML Module Definition"""
    
    def test_create_module_definition(self):
        """Test creating a module definition"""
        owner = ModuleOwner(
            team="platform",
            contacts=["admin@example.com"],
            approvers=["lead@example.com"],
        )
        
        metadata = ModuleMetadata(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            labels=["production", "critical"],
            compliance_tags=["pci-dss", "soc2"],
        )
        
        module = YAMLModuleDefinition(
            id="mod-001",
            kind="ConfigModule",
            version="1.0.0",
            name="Database Config",
            description="Database configuration module",
            owner=owner,
            metadata=metadata,
            schema={"type": "object"},
        )
        
        assert module.id == "mod-001"
        assert module.kind == "ConfigModule"
        assert module.version == "1.0.0"
        assert module.owner.team == "platform"
        assert len(module.metadata.compliance_tags) == 2
    
    def test_lifecycle_transitions(self):
        """Test lifecycle state transitions"""
        lifecycle = ModuleLifecycle(state=LifecycleState.DRAFT)
        
        # Valid transition: DRAFT -> REVIEW
        assert lifecycle.transition_to(LifecycleState.REVIEW, "user1")
        assert lifecycle.state == LifecycleState.REVIEW
        
        # Valid transition: REVIEW -> APPROVED
        assert lifecycle.transition_to(LifecycleState.APPROVED, "approver1")
        assert lifecycle.state == LifecycleState.APPROVED
        assert lifecycle.approved_by == "approver1"
        
        # Invalid transition: APPROVED -> DRAFT (not allowed)
        assert not lifecycle.transition_to(LifecycleState.DRAFT, "user1")
        assert lifecycle.state == LifecycleState.APPROVED
    
    def test_test_vectors(self):
        """Test test vector management"""
        owner = ModuleOwner(team="test", contacts=["test@example.com"])
        metadata = ModuleMetadata(created_at=datetime.now(), updated_at=datetime.now())
        
        module = YAMLModuleDefinition(
            id="mod-002",
            kind="TestModule",
            version="1.0.0",
            name="Test Module",
            description="Test",
            owner=owner,
            metadata=metadata,
            schema={},
        )
        
        tv1 = TestVector(
            id="tv-001",
            name="Valid Input Test",
            type=TestVectorType.VALID,
            description="Test with valid input",
            input_data={"key": "value"},
            expected_result={"status": "ok"},
        )
        
        tv2 = TestVector(
            id="tv-002",
            name="Invalid Input Test",
            type=TestVectorType.INVALID,
            description="Test with invalid input",
            input_data={},
            expected_result={"status": "error"},
        )
        
        module.add_test_vector(tv1)
        module.add_test_vector(tv2)
        
        assert len(module.test_vectors) == 2
        assert len(module.get_test_vectors_by_type(TestVectorType.VALID)) == 1
        assert len(module.get_test_vectors_by_type(TestVectorType.INVALID)) == 1


# ============ Schema Validator Tests ============

class TestYAMLSchemaValidator:
    """Test YAML Schema Validator"""
    
    def test_type_validation(self):
        """Test type validation"""
        validator = YAMLSchemaValidator()
        
        schema = {"type": "string"}
        
        # Valid
        result = validator.validate("hello", schema)
        assert result.valid
        
        # Invalid
        result = validator.validate(123, schema)
        assert not result.valid
        assert len(result.errors) == 1
        assert result.errors[0].error_type == ValidationErrorType.TYPE_MISMATCH
    
    def test_required_properties(self):
        """Test required properties validation"""
        validator = YAMLSchemaValidator()
        
        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            }
        }
        
        # Valid
        result = validator.validate({"name": "test", "version": "1.0.0"}, schema)
        assert result.valid
        
        # Missing required property
        result = validator.validate({"name": "test"}, schema)
        assert not result.valid
        assert any(e.error_type == ValidationErrorType.REQUIRED_FIELD_MISSING for e in result.errors)
    
    def test_string_validation(self):
        """Test string validation"""
        validator = YAMLSchemaValidator()
        
        schema = {
            "type": "string",
            "minLength": 3,
            "maxLength": 10,
            "pattern": "^[a-z]+$"
        }
        
        # Valid
        result = validator.validate("hello", schema)
        assert result.valid
        
        # Too short
        result = validator.validate("ab", schema)
        assert not result.valid
        
        # Pattern mismatch
        result = validator.validate("Hello", schema)
        assert not result.valid
    
    def test_array_validation(self):
        """Test array validation"""
        validator = YAMLSchemaValidator()
        
        schema = {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": {"type": "string"}
        }
        
        # Valid
        result = validator.validate(["a", "b", "c"], schema)
        assert result.valid
        
        # Empty array
        result = validator.validate([], schema)
        assert not result.valid
        
        # Wrong item type
        result = validator.validate([1, 2, 3], schema)
        assert not result.valid


# ============ Policy Gate Tests ============

class TestPolicyGate:
    """Test Policy Gate"""
    
    def test_policy_evaluation(self):
        """Test policy evaluation"""
        gate = PolicyGate()
        
        rule = PolicyRule(
            id="test-rule",
            name="Test Rule",
            description="Test description",
            severity=PolicySeverity.HIGH,
            category=PolicyCategory.SECURITY,
            action=PolicyAction.BLOCK,
            condition="exists owner.team",
        )
        
        gate.add_rule(rule)
        
        # Pass
        result = gate.evaluate({"owner": {"team": "platform"}})
        assert result.passed
        
        # Fail
        result = gate.evaluate({"owner": {}})
        assert not result.passed
        assert len(result.violations) == 1
    
    def test_default_security_rules(self):
        """Test default security rules"""
        rules = PolicyGate.create_default_security_rules()
        assert len(rules) >= 4
        assert all(r.category == PolicyCategory.SECURITY for r in rules)
    
    def test_policy_exceptions(self):
        """Test policy exceptions"""
        gate = PolicyGate()
        
        rule = PolicyRule(
            id="exc-rule",
            name="Exception Rule",
            description="Rule with exception",
            severity=PolicySeverity.CRITICAL,
            category=PolicyCategory.SECURITY,
            action=PolicyAction.BLOCK,
            validator=lambda x: False,  # Always fails
        )
        
        gate.add_rule(rule)
        
        # Without exception - fails
        result = gate.evaluate({}, module_id="mod-001")
        assert not result.passed
        
        # Add exception
        gate.add_exception("exc-rule", "mod-001", "Test exception", "admin")
        
        # With exception - passes
        result = gate.evaluate({}, module_id="mod-001")
        assert result.passed


# ============ CI Verification Pipeline Tests ============

class TestCIVerificationPipeline:
    """Test CI Verification Pipeline"""
    
    def test_pipeline_execution(self):
        """Test pipeline execution"""
        pipeline = CIVerificationPipeline.create_default_pipeline()
        
        data = {"name": "test", "version": "1.0.0"}
        report = pipeline.run(data, module_id="mod-001", module_version="1.0.0")
        
        assert report.passed
        assert len(report.stages) >= 4
        assert all(s.status in [StageStatus.PASSED, StageStatus.SKIPPED] for s in report.stages)
    
    def test_stage_dependencies(self):
        """Test stage dependencies"""
        pipeline = CIVerificationPipeline()
        
        def failing_executor(data, context):
            result = StageResult(
                stage_id="fail",
                stage_type=PipelineStageType.LINT,
                status=StageStatus.FAILED,
                started_at=datetime.now(),
            )
            result.errors.append("Intentional failure")
            return result
        
        pipeline.add_stage(PipelineStage(
            id="fail-stage",
            name="Failing Stage",
            stage_type=PipelineStageType.LINT,
            description="This stage fails",
            executor=failing_executor,
            required=True,
        ))
        
        pipeline.add_stage(PipelineStage(
            id="dependent-stage",
            name="Dependent Stage",
            stage_type=PipelineStageType.TEST,
            description="Depends on failing stage",
            depends_on=["fail-stage"],
        ))
        
        report = pipeline.run({}, "mod-001", "1.0.0")
        
        assert not report.passed
        assert report.stages[1].status == StageStatus.SKIPPED
    
    def test_evidence_collection(self):
        """Test evidence collection"""
        collector = EvidenceCollector()
        
        evidence = collector.collect(
            type="test",
            name="Test Evidence",
            description="Test description",
            data={"key": "value"},
        )
        
        assert evidence.type == "test"
        assert evidence.hash is not None
        assert len(collector.get_all()) == 1


# ============ SLSA Compliance Tests ============

class TestSLSACompliance:
    """Test SLSA Compliance"""
    
    def test_provenance_generation(self):
        """Test provenance generation"""
        generator = SLSAProvenanceGenerator(
            builder_id="synergymesh/builder",
            builder_version="1.0.0",
        )
        
        provenance = generator.generate(
            artifact_name="test-artifact",
            artifact_digest="abc123",
            build_type="yaml-module",
            external_parameters={"env": "production"},
        )
        
        assert provenance.id is not None
        assert len(provenance.subjects) == 1
        assert provenance.slsa_level == SLSALevel.LEVEL_3
        
        # Test serialization
        data = provenance.to_dict()
        assert data['_type'] == 'https://in-toto.io/Statement/v1'
    
    def test_artifact_signing(self):
        """Test artifact signing"""
        signer = ArtifactSigner(
            key_id="test-key-001",
            algorithm=SignatureAlgorithm.ECDSA_P256,
        )
        
        signed = signer.sign(
            artifact_name="test-artifact",
            artifact_data={"content": "test"},
        )
        
        assert signed.signature is not None
        assert signed.signature_algorithm == SignatureAlgorithm.ECDSA_P256
        assert signed.key_id == "test-key-001"
    
    def test_sbom_generation(self):
        """Test SBOM generation"""
        generator = SBOMGenerator(author="test-author")
        
        sbom = generator.generate(
            name="test-software",
            version="1.0.0",
            dependencies=[
                {"name": "dep1", "version": "1.0.0"},
                {"name": "dep2", "version": "2.0.0"},
            ],
        )
        
        assert sbom.name == "test-software"
        assert len(sbom.components) == 2
        
        # Test CycloneDX format
        data = sbom.to_dict()
        assert data['bomFormat'] == 'CycloneDX'


# ============ Audit Trail Tests ============

class TestAuditTrail:
    """Test Audit Trail"""
    
    def test_audit_logging(self):
        """Test audit logging"""
        logger = AuditLogger()
        
        entry = logger.log(
            action=AuditAction.CREATE,
            actor="user@example.com",
            resource_type="module",
            resource_id="mod-001",
            new_state={"name": "test"},
        )
        
        assert entry.action == AuditAction.CREATE
        assert entry.actor == "user@example.com"
        
        entries = logger.get_entries(resource_id="mod-001")
        assert len(entries) == 1
    
    def test_change_tracking(self):
        """Test change tracking"""
        tracker = ChangeTracker()
        
        old_state = {"name": "old", "version": "1.0.0"}
        new_state = {"name": "new", "version": "1.0.0", "added": "field"}
        
        records = tracker.track_changes(
            resource_type="module",
            resource_id="mod-001",
            old_state=old_state,
            new_state=new_state,
            actor="user",
        )
        
        assert len(records) == 2  # name modified, added field added
        
        modified = [r for r in records if r.change_type == 'modified']
        added = [r for r in records if r.change_type == 'added']
        
        assert len(modified) == 1
        assert len(added) == 1
    
    def test_resource_history(self):
        """Test resource history"""
        logger = AuditLogger()
        
        logger.log_create("user1", "module", "mod-001", {"v": 1})
        logger.log_update("user2", "module", "mod-001", {"v": 1}, {"v": 2})
        logger.log_approve("admin", "module", "mod-001")
        
        history = logger.get_resource_history("module", "mod-001")
        assert len(history) == 3


# ============ Integration Tests ============

class TestPhase13Integration:
    """Integration tests for Phase 13"""
    
    def test_full_verification_flow(self):
        """Test full verification flow"""
        # Create module
        owner = ModuleOwner(team="platform", contacts=["admin@example.com"])
        metadata = ModuleMetadata(created_at=datetime.now(), updated_at=datetime.now())
        
        module = YAMLModuleDefinition(
            id="mod-int-001",
            kind="ConfigModule",
            version="1.0.0",
            name="Integration Test Module",
            description="Test module for integration",
            owner=owner,
            metadata=metadata,
            schema={"type": "object", "required": ["name"]},
        )
        
        # Validate schema
        validator = YAMLSchemaValidator()
        validation_result = validator.validate(
            {"name": "test"},
            module.schema,
        )
        assert validation_result.valid
        
        # Run through policy gate
        gate = PolicyGate()
        for rule in PolicyGate.create_default_compliance_rules():
            gate.add_rule(rule)
        
        policy_result = gate.evaluate(module.to_dict())
        # May have warnings but should pass for blocking rules
        
        # Run verification pipeline
        pipeline = CIVerificationPipeline.create_default_pipeline()
        report = pipeline.run(
            module.to_dict(),
            module_id=module.id,
            module_version=module.version,
        )
        
        # Generate SLSA provenance
        provenance_gen = SLSAProvenanceGenerator("synergymesh/builder")
        provenance = provenance_gen.generate_from_module(
            module.to_dict(),
            {"build_type": "yaml-module"},
        )
        
        # Sign the provenance
        signer = ArtifactSigner("signing-key-001")
        signed_provenance = signer.sign_provenance(provenance)
        
        # Generate SBOM
        sbom_gen = SBOMGenerator("synergymesh")
        sbom = sbom_gen.generate_from_module(module.to_dict())
        
        # Log to audit
        logger = AuditLogger()
        logger.log_create(
            actor="system",
            resource_type="module",
            resource_id=module.id,
            new_state=module.to_dict(),
            details={
                "provenance_id": provenance.id,
                "sbom_id": sbom.id,
            },
        )
        
        # Verify everything was created
        assert provenance.id is not None
        assert signed_provenance.signature is not None
        assert sbom.id is not None
        assert len(logger.get_entries()) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
