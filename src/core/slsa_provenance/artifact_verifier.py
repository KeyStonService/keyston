"""
Artifact Verifier - Verify artifact integrity

This module provides functionality to verify the integrity and provenance
of build artifacts using SLSA framework requirements.
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class IntegrityStatus(Enum):
    """Artifact integrity status"""
    VERIFIED = 'verified'
    UNVERIFIED = 'unverified'
    TAMPERED = 'tampered'
    MISSING = 'missing'
    UNKNOWN = 'unknown'


class ProvenanceStatus(Enum):
    """Provenance verification status"""
    VERIFIED = 'verified'
    UNVERIFIED = 'unverified'
    INVALID = 'invalid'
    MISSING = 'missing'


@dataclass
class ArtifactMetadata:
    """Metadata about an artifact"""
    name: str
    digest: Dict[str, str]
    size: Optional[int] = None
    media_type: Optional[str] = None
    uri: Optional[str] = None
    created_at: Optional[datetime] = None
    annotations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'name': self.name,
            'digest': self.digest
        }
        if self.size is not None:
            result['size'] = self.size
        if self.media_type:
            result['mediaType'] = self.media_type
        if self.uri:
            result['uri'] = self.uri
        if self.created_at:
            result['createdAt'] = self.created_at.isoformat()
        if self.annotations:
            result['annotations'] = self.annotations
        return result


@dataclass
class VerificationResult:
    """Result of artifact verification"""
    artifact: ArtifactMetadata
    integrity_status: IntegrityStatus
    provenance_status: ProvenanceStatus
    slsa_level: int = 0
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verification_id: str = field(default_factory=lambda: str(uuid4()))
    checks: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    policy_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'verificationId': self.verification_id,
            'artifact': self.artifact.to_dict(),
            'integrityStatus': self.integrity_status.value,
            'provenanceStatus': self.provenance_status.value,
            'slsaLevel': self.slsa_level,
            'verifiedAt': self.verified_at.isoformat(),
            'checks': self.checks,
            'errors': self.errors,
            'warnings': self.warnings,
            'policyResults': self.policy_results,
            'metadata': self.metadata
        }
        
    @property
    def is_verified(self) -> bool:
        """Check if artifact is fully verified"""
        return (
            self.integrity_status == IntegrityStatus.VERIFIED and
            self.provenance_status == ProvenanceStatus.VERIFIED
        )


@dataclass
class VerificationPolicy:
    """Policy for artifact verification"""
    name: str
    min_slsa_level: int = 1
    require_signature: bool = True
    require_transparency_log: bool = True
    allowed_builders: List[str] = field(default_factory=list)
    allowed_sources: List[str] = field(default_factory=list)
    digest_algorithms: List[str] = field(default_factory=lambda: ['sha256'])
    custom_checks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'minSlsaLevel': self.min_slsa_level,
            'requireSignature': self.require_signature,
            'requireTransparencyLog': self.require_transparency_log,
            'allowedBuilders': self.allowed_builders,
            'allowedSources': self.allowed_sources,
            'digestAlgorithms': self.digest_algorithms,
            'customChecks': self.custom_checks
        }


class ArtifactVerifier:
    """
    Verifier for artifact integrity and provenance
    
    Provides comprehensive verification of build artifacts including:
    - Digest verification
    - Provenance validation
    - SLSA level assessment
    - Policy compliance checking
    """
    
    def __init__(
        self,
        default_policy: Optional[VerificationPolicy] = None
    ):
        """
        Initialize the verifier
        
        Args:
            default_policy: Default verification policy
        """
        self.default_policy = default_policy or self._create_default_policy()
        self._verification_cache: Dict[str, VerificationResult] = {}
        
    def verify_artifact(
        self,
        artifact_path: Optional[str] = None,
        artifact_content: Optional[bytes] = None,
        artifact_name: Optional[str] = None,
        expected_digest: Optional[Dict[str, str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
        policy: Optional[VerificationPolicy] = None
    ) -> VerificationResult:
        """
        Verify an artifact
        
        Args:
            artifact_path: Path to artifact file
            artifact_content: Artifact content bytes
            artifact_name: Name of the artifact
            expected_digest: Expected digest(s)
            provenance: SLSA provenance data
            policy: Verification policy
            
        Returns:
            VerificationResult with verification status
        """
        active_policy = policy or self.default_policy
        
        # Get artifact metadata
        if artifact_path:
            metadata = self._get_file_metadata(artifact_path)
        elif artifact_content:
            metadata = self._get_content_metadata(
                artifact_content,
                artifact_name or 'unknown'
            )
        elif expected_digest and artifact_name:
            metadata = ArtifactMetadata(
                name=artifact_name,
                digest=expected_digest
            )
        else:
            raise ValueError('Must provide artifact_path, artifact_content, or expected_digest')
            
        result = VerificationResult(
            artifact=metadata,
            integrity_status=IntegrityStatus.UNKNOWN,
            provenance_status=ProvenanceStatus.MISSING
        )
        
        # Step 1: Verify integrity
        integrity_result = self._verify_integrity(
            metadata,
            expected_digest,
            active_policy
        )
        result.integrity_status = integrity_result['status']
        result.checks.extend(integrity_result['checks'])
        
        if integrity_result.get('errors'):
            result.errors.extend(integrity_result['errors'])
            
        # Step 2: Verify provenance
        if provenance:
            provenance_result = self._verify_provenance(
                metadata,
                provenance,
                active_policy
            )
            result.provenance_status = provenance_result['status']
            result.slsa_level = provenance_result.get('slsa_level', 0)
            result.checks.extend(provenance_result['checks'])
            
            if provenance_result.get('errors'):
                result.errors.extend(provenance_result['errors'])
            if provenance_result.get('warnings'):
                result.warnings.extend(provenance_result['warnings'])
                
        # Step 3: Check policy compliance
        policy_result = self._check_policy_compliance(result, active_policy)
        result.policy_results = policy_result
        
        if not policy_result.get('compliant', True):
            result.warnings.append('Artifact does not meet policy requirements')
            
        # Cache result
        cache_key = self._get_cache_key(metadata)
        self._verification_cache[cache_key] = result
        
        logger.info(f'Verified artifact: {metadata.name} - {result.integrity_status.value}')
        return result
        
    def verify_artifact_batch(
        self,
        artifacts: List[Dict[str, Any]],
        policy: Optional[VerificationPolicy] = None
    ) -> List[VerificationResult]:
        """
        Verify multiple artifacts
        
        Args:
            artifacts: List of artifact specifications
            policy: Verification policy
            
        Returns:
            List of verification results
        """
        results = []
        for artifact in artifacts:
            result = self.verify_artifact(
                artifact_path=artifact.get('path'),
                artifact_content=artifact.get('content'),
                artifact_name=artifact.get('name'),
                expected_digest=artifact.get('digest'),
                provenance=artifact.get('provenance'),
                policy=policy
            )
            results.append(result)
        return results
        
    def verify_provenance_chain(
        self,
        artifact_metadata: ArtifactMetadata,
        provenance_chain: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify a chain of provenance
        
        Args:
            artifact_metadata: Artifact to verify
            provenance_chain: List of provenance records in chain
            
        Returns:
            Chain verification result
        """
        result = {
            'valid': True,
            'chain_length': len(provenance_chain),
            'verifications': [],
            'errors': []
        }
        
        current_digest = artifact_metadata.digest.get('sha256', '')
        
        for i, provenance in enumerate(provenance_chain):
            # Verify each link in the chain
            subjects = provenance.get('subject', [])
            
            # Check if artifact is a subject in this provenance
            found = False
            for subject in subjects:
                subject_digest = subject.get('digest', {}).get('sha256', '')
                if subject_digest == current_digest:
                    found = True
                    break
                    
            if not found and i == 0:
                result['errors'].append(f'Artifact not found in provenance at position {i}')
                result['valid'] = False
                continue
                
            # Verify provenance structure
            predicate = provenance.get('predicate', {})
            build_def = predicate.get('buildDefinition', {})
            run_details = predicate.get('runDetails', {})
            
            link_result = {
                'position': i,
                'valid': True,
                'builder': run_details.get('builder', {}).get('id', 'unknown'),
                'build_type': build_def.get('buildType', 'unknown'),
                'has_signature': bool(provenance.get('signature'))
            }
            
            if not run_details.get('metadata', {}).get('invocationId'):
                link_result['valid'] = False
                link_result['error'] = 'Missing invocation ID'
                result['valid'] = False
                
            result['verifications'].append(link_result)
            
            # Get dependencies for next iteration
            deps = build_def.get('resolvedDependencies', [])
            if deps:
                # Use first dependency's digest as next current
                first_dep = deps[0]
                current_digest = first_dep.get('digest', {}).get('sha256', current_digest)
                
        return result
        
    def get_cached_result(
        self,
        artifact_name: str,
        digest: Dict[str, str]
    ) -> Optional[VerificationResult]:
        """Get cached verification result"""
        metadata = ArtifactMetadata(name=artifact_name, digest=digest)
        cache_key = self._get_cache_key(metadata)
        return self._verification_cache.get(cache_key)
        
    def clear_cache(self) -> None:
        """Clear verification cache"""
        self._verification_cache.clear()
        
    def create_verification_summary(
        self,
        results: List[VerificationResult],
        policy: Optional[VerificationPolicy] = None
    ) -> Dict[str, Any]:
        """
        Create a verification summary for multiple results
        
        Args:
            results: List of verification results
            policy: Policy used for verification
            
        Returns:
            Summary dictionary
        """
        verified_count = sum(1 for r in results if r.is_verified)
        failed_count = len(results) - verified_count
        
        slsa_levels = [r.slsa_level for r in results]
        min_level = min(slsa_levels) if slsa_levels else 0
        
        all_errors = []
        for r in results:
            all_errors.extend(r.errors)
            
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_artifacts': len(results),
            'verified_count': verified_count,
            'failed_count': failed_count,
            'verification_rate': verified_count / len(results) if results else 0,
            'min_slsa_level': min_level,
            'policy_name': (policy or self.default_policy).name,
            'errors': all_errors,
            'artifacts': [r.to_dict() for r in results]
        }
        
    def _create_default_policy(self) -> VerificationPolicy:
        """Create default verification policy"""
        return VerificationPolicy(
            name='default',
            min_slsa_level=1,
            require_signature=False,
            require_transparency_log=False,
            digest_algorithms=['sha256']
        )
        
    def _get_file_metadata(self, file_path: str) -> ArtifactMetadata:
        """Get metadata for a file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        digest = {
            'sha256': hashlib.sha256(content).hexdigest()
        }
        
        return ArtifactMetadata(
            name=os.path.basename(file_path),
            digest=digest,
            size=len(content),
            uri=f'file://{os.path.abspath(file_path)}'
        )
        
    def _get_content_metadata(
        self,
        content: bytes,
        name: str
    ) -> ArtifactMetadata:
        """Get metadata for content bytes"""
        digest = {
            'sha256': hashlib.sha256(content).hexdigest()
        }
        
        return ArtifactMetadata(
            name=name,
            digest=digest,
            size=len(content)
        )
        
    def _verify_integrity(
        self,
        metadata: ArtifactMetadata,
        expected_digest: Optional[Dict[str, str]],
        policy: VerificationPolicy
    ) -> Dict[str, Any]:
        """Verify artifact integrity"""
        result = {
            'status': IntegrityStatus.VERIFIED,
            'checks': [],
            'errors': []
        }
        
        # Check digest presence
        if not metadata.digest:
            result['status'] = IntegrityStatus.UNVERIFIED
            result['checks'].append({
                'name': 'digest_presence',
                'passed': False,
                'error': 'No digest available'
            })
            return result
            
        result['checks'].append({
            'name': 'digest_presence',
            'passed': True
        })
        
        # Check against expected digest
        if expected_digest:
            for alg, expected_hash in expected_digest.items():
                actual_hash = metadata.digest.get(alg)
                if actual_hash != expected_hash:
                    result['status'] = IntegrityStatus.TAMPERED
                    result['checks'].append({
                        'name': f'digest_match_{alg}',
                        'passed': False,
                        'error': f'Digest mismatch for {alg}'
                    })
                    result['errors'].append(f'Digest mismatch: expected {expected_hash}, got {actual_hash}')
                else:
                    result['checks'].append({
                        'name': f'digest_match_{alg}',
                        'passed': True
                    })
                    
        # Check required algorithms
        for alg in policy.digest_algorithms:
            if alg not in metadata.digest:
                result['checks'].append({
                    'name': f'digest_algorithm_{alg}',
                    'passed': False,
                    'error': f'Missing required digest algorithm: {alg}'
                })
                
        return result
        
    def _verify_provenance(
        self,
        metadata: ArtifactMetadata,
        provenance: Dict[str, Any],
        policy: VerificationPolicy
    ) -> Dict[str, Any]:
        """Verify provenance data"""
        result = {
            'status': ProvenanceStatus.UNVERIFIED,
            'slsa_level': 0,
            'checks': [],
            'errors': [],
            'warnings': []
        }
        
        # Check provenance structure
        if not provenance:
            result['status'] = ProvenanceStatus.MISSING
            return result
            
        # Check artifact is in subjects
        subjects = provenance.get('subject', [])
        artifact_found = False
        
        for subject in subjects:
            subject_digest = subject.get('digest', {})
            for alg, hash_value in metadata.digest.items():
                if subject_digest.get(alg) == hash_value:
                    artifact_found = True
                    break
                    
        if not artifact_found:
            result['status'] = ProvenanceStatus.INVALID
            result['errors'].append('Artifact not found in provenance subjects')
            return result
            
        result['checks'].append({
            'name': 'subject_match',
            'passed': True
        })
        
        # Check predicate
        predicate = provenance.get('predicate', {})
        build_def = predicate.get('buildDefinition', {})
        run_details = predicate.get('runDetails', {})
        
        # Determine SLSA level
        slsa_level = self._determine_slsa_level(build_def, run_details, policy)
        result['slsa_level'] = slsa_level
        
        # Check builder
        builder_id = run_details.get('builder', {}).get('id', '')
        if policy.allowed_builders and builder_id not in policy.allowed_builders:
            result['warnings'].append(f'Builder {builder_id} not in allowed list')
            
        result['checks'].append({
            'name': 'builder_check',
            'passed': True,
            'builder': builder_id
        })
        
        # Check source (from external parameters)
        source = build_def.get('externalParameters', {}).get('source', {})
        source_uri = source.get('uri', '')
        if policy.allowed_sources and source_uri:
            source_allowed = any(
                allowed in source_uri for allowed in policy.allowed_sources
            )
            if not source_allowed:
                result['warnings'].append(f'Source {source_uri} not in allowed list')
                
        result['status'] = ProvenanceStatus.VERIFIED
        return result
        
    def _determine_slsa_level(
        self,
        build_def: Dict[str, Any],
        run_details: Dict[str, Any],
        policy: VerificationPolicy
    ) -> int:
        """Determine SLSA level achieved"""
        level = 0
        
        # Level 1: Documentation of build process
        if build_def.get('buildType'):
            level = 1
            
        # Level 2: Build service tamper resistance
        builder = run_details.get('builder', {})
        if builder.get('id') and build_def.get('resolvedDependencies'):
            level = 2
            
        # Level 3: Hardened build platform
        metadata = run_details.get('metadata', {})
        if metadata.get('invocationId') and metadata.get('startedOn'):
            level = 3
            
        # Level 4: Hermetic, reproducible
        deps = build_def.get('resolvedDependencies', [])
        params = build_def.get('externalParameters', {})
        if deps and params.get('reviewers'):
            level = 4
            
        return level
        
    def _check_policy_compliance(
        self,
        result: VerificationResult,
        policy: VerificationPolicy
    ) -> Dict[str, Any]:
        """Check if result meets policy requirements"""
        compliance = {
            'policy_name': policy.name,
            'compliant': True,
            'checks': []
        }
        
        # Check SLSA level
        if result.slsa_level < policy.min_slsa_level:
            compliance['compliant'] = False
            compliance['checks'].append({
                'name': 'min_slsa_level',
                'passed': False,
                'required': policy.min_slsa_level,
                'actual': result.slsa_level
            })
        else:
            compliance['checks'].append({
                'name': 'min_slsa_level',
                'passed': True
            })
            
        # Check integrity status
        if result.integrity_status != IntegrityStatus.VERIFIED:
            compliance['compliant'] = False
            compliance['checks'].append({
                'name': 'integrity',
                'passed': False,
                'status': result.integrity_status.value
            })
        else:
            compliance['checks'].append({
                'name': 'integrity',
                'passed': True
            })
            
        return compliance
        
    def _get_cache_key(self, metadata: ArtifactMetadata) -> str:
        """Generate cache key for artifact"""
        digest_str = json.dumps(metadata.digest, sort_keys=True)
        return f'{metadata.name}:{hashlib.sha256(digest_str.encode()).hexdigest()[:16]}'


# Factory functions
def create_artifact_verifier(
    policy: Optional[VerificationPolicy] = None
) -> ArtifactVerifier:
    """Create a new ArtifactVerifier instance"""
    return ArtifactVerifier(policy)


def create_verification_policy(name: str, **kwargs) -> VerificationPolicy:
    """Create a new VerificationPolicy"""
    return VerificationPolicy(name=name, **kwargs)
