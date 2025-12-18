"""
Tests for Phase 20: SLSA L3 Provenance System
"""

import asyncio
import pytest
import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from slsa_provenance import (
    ProvenanceGenerator,
    Provenance,
    BuildDefinition,
    SignatureVerifier,
    VerificationPolicy,
    SignatureType,
    AttestationManager,
    AttestationType,
    ArtifactVerifier,
    VerificationResult
)
from slsa_provenance.provenance_generator import SLSALevel, Subject


class TestProvenanceGenerator:
    """Tests for ProvenanceGenerator"""
    
    @pytest.fixture
    def generator(self):
        return ProvenanceGenerator(
            builder_id='https://synergymesh.dev/builder',
            builder_version='1.0.0'
        )
        
    def test_start_build(self, generator):
        """Test starting a build"""
        invocation_id = generator.start_build(
            build_type='https://synergymesh.dev/build',
            external_parameters={'source': 'git://repo'}
        )
        
        assert invocation_id is not None
        assert generator._current_build is not None
        
    def test_add_subject(self, generator):
        """Test adding a subject to build"""
        generator.start_build(
            build_type='test-build',
            external_parameters={}
        )
        
        digest = generator.add_subject(
            name='artifact.zip',
            content=b'test content'
        )
        
        assert 'sha256' in digest
        assert len(generator._current_build['subjects']) == 1
        
    def test_finish_build(self, generator):
        """Test finishing a build and generating provenance"""
        generator.start_build(
            build_type='test-build',
            external_parameters={'source': 'test'}
        )
        
        generator.add_subject(
            name='artifact.zip',
            content=b'test content'
        )
        
        provenance = generator.finish_build()
        
        assert isinstance(provenance, Provenance)
        assert len(provenance.subjects) == 1
        assert provenance.build_definition.build_type == 'test-build'
        
    def test_generate_provenance(self, generator):
        """Test generating provenance in one call"""
        provenance = generator.generate_provenance(
            subjects=[{
                'name': 'test.zip',
                'digest': {'sha256': 'abc123'}
            }],
            build_type='test-build',
            external_parameters={'source': 'git'}
        )
        
        assert isinstance(provenance, Provenance)
        assert provenance.subjects[0].name == 'test.zip'
        
    def test_validate_provenance(self, generator):
        """Test provenance validation"""
        provenance = generator.generate_provenance(
            subjects=[{
                'name': 'test.zip',
                'digest': {'sha256': 'abc123'}
            }],
            build_type='test-build',
            external_parameters={'source': 'git'}
        )
        
        result = generator.validate_provenance(provenance, SLSALevel.L1)
        
        assert 'valid' in result
        assert 'issues' in result


class TestSignatureVerifier:
    """Tests for SignatureVerifier"""
    
    @pytest.fixture
    def verifier(self):
        return SignatureVerifier()
        
    def test_verify_signature(self, verifier):
        """Test signature verification"""
        import base64
        
        result = verifier.verify_signature(
            artifact_digest='abc123',
            signature=base64.b64encode(b'test signature').decode()
        )
        
        assert result is not None
        assert hasattr(result, 'status')
        
    def test_create_policy(self, verifier):
        """Test creating verification policy"""
        policy = verifier.create_policy(
            name='test-policy',
            require_transparency_log=True
        )
        
        assert policy.name == 'test-policy'
        assert policy.require_transparency_log is True
        
    def test_verify_provenance_signature(self, verifier):
        """Test verifying provenance signature"""
        import base64
        
        provenance = {
            '_type': 'https://in-toto.io/Statement/v1',
            'predicateType': 'https://slsa.dev/provenance/v1',
            'subject': [{'name': 'test', 'digest': {'sha256': 'abc'}}],
            'predicate': {}
        }
        
        result = verifier.verify_provenance_signature(
            provenance=provenance,
            signature=base64.b64encode(b'signature').decode()
        )
        
        assert result is not None


class TestAttestationManager:
    """Tests for AttestationManager"""
    
    @pytest.fixture
    def manager(self):
        return AttestationManager()
        
    def test_create_attestation(self, manager):
        """Test creating an attestation"""
        attestation = manager.create_attestation(
            attestation_type=AttestationType.SLSA_PROVENANCE,
            subjects=[{
                'name': 'artifact.zip',
                'digest': {'sha256': 'abc123'}
            }],
            predicate={'buildType': 'test'}
        )
        
        assert attestation is not None
        assert attestation.type == AttestationType.SLSA_PROVENANCE
        assert len(attestation.subjects) == 1
        
    def test_get_attestation(self, manager):
        """Test retrieving an attestation"""
        attestation = manager.create_attestation(
            attestation_type=AttestationType.SLSA_PROVENANCE,
            subjects=[{'name': 'test', 'digest': {'sha256': 'abc'}}],
            predicate={}
        )
        
        retrieved = manager.get_attestation(attestation.id)
        
        assert retrieved is not None
        assert retrieved.id == attestation.id
        
    def test_verify_attestation(self, manager):
        """Test attestation verification"""
        attestation = manager.create_attestation(
            attestation_type=AttestationType.SLSA_PROVENANCE,
            subjects=[{'name': 'test', 'digest': {'sha256': 'abc'}}],
            predicate={}
        )
        
        result = manager.verify_attestation(attestation.id)
        
        assert 'valid' in result
        assert 'checks' in result
        
    def test_create_bundle(self, manager):
        """Test creating attestation bundle"""
        attestation = manager.create_attestation(
            attestation_type=AttestationType.SLSA_PROVENANCE,
            subjects=[{'name': 'test', 'digest': {'sha256': 'abc'}}],
            predicate={}
        )
        
        bundle = manager.create_bundle(attestation.id)
        
        assert bundle is not None
        assert bundle.attestation.id == attestation.id


class TestArtifactVerifier:
    """Tests for ArtifactVerifier"""
    
    @pytest.fixture
    def verifier(self):
        return ArtifactVerifier()
        
    def test_verify_artifact_content(self, verifier):
        """Test verifying artifact from content"""
        content = b'test artifact content'
        
        result = verifier.verify_artifact(
            artifact_content=content,
            artifact_name='test.zip'
        )
        
        assert isinstance(result, VerificationResult)
        assert result.artifact.name == 'test.zip'
        
    def test_verify_artifact_with_expected_digest(self, verifier):
        """Test verifying artifact with expected digest"""
        import hashlib
        
        content = b'test content'
        expected_digest = {'sha256': hashlib.sha256(content).hexdigest()}
        
        result = verifier.verify_artifact(
            artifact_content=content,
            artifact_name='test.zip',
            expected_digest=expected_digest
        )
        
        assert result.integrity_status.value == 'verified'
        
    def test_verify_artifact_with_provenance(self, verifier):
        """Test verifying artifact with provenance"""
        import hashlib
        
        content = b'test content'
        digest = hashlib.sha256(content).hexdigest()
        
        provenance = {
            'subject': [{'name': 'test.zip', 'digest': {'sha256': digest}}],
            'predicate': {
                'buildDefinition': {
                    'buildType': 'test',
                    'resolvedDependencies': []
                },
                'runDetails': {
                    'builder': {'id': 'test-builder'},
                    'metadata': {
                        'invocationId': 'inv-123',
                        'startedOn': '2024-01-01T00:00:00Z'
                    }
                }
            }
        }
        
        result = verifier.verify_artifact(
            artifact_content=content,
            artifact_name='test.zip',
            provenance=provenance
        )
        
        assert result.slsa_level >= 1
        
    def test_create_verification_summary(self, verifier):
        """Test creating verification summary"""
        content = b'test'
        
        result1 = verifier.verify_artifact(
            artifact_content=content,
            artifact_name='test1.zip'
        )
        result2 = verifier.verify_artifact(
            artifact_content=content,
            artifact_name='test2.zip'
        )
        
        summary = verifier.create_verification_summary([result1, result2])
        
        assert summary['total_artifacts'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
