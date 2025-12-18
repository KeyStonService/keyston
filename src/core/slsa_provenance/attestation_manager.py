"""
Attestation Manager - Manage build attestations

This module provides functionality to create, store, and manage
build attestations in compliance with SLSA and in-toto frameworks.
"""

import base64
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class AttestationType(Enum):
    """Types of attestations"""
    SLSA_PROVENANCE = 'https://slsa.dev/provenance/v1'
    SLSA_VERIFICATION_SUMMARY = 'https://slsa.dev/verification_summary/v1'
    IN_TOTO_LINK = 'https://in-toto.io/Link/v1'
    SPDX = 'https://spdx.dev/Document/v2.3'
    CYCLONEDX = 'https://cyclonedx.org/bom/v1.4'
    CUSTOM = 'custom'


class AttestationStatus(Enum):
    """Status of an attestation"""
    DRAFT = 'draft'
    SIGNED = 'signed'
    VERIFIED = 'verified'
    REVOKED = 'revoked'
    EXPIRED = 'expired'


@dataclass
class AttestationSubject:
    """Subject of an attestation"""
    name: str
    digest: Dict[str, str]
    uri: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'name': self.name,
            'digest': self.digest
        }
        if self.uri:
            result['uri'] = self.uri
        return result


@dataclass
class Attestation:
    """Build attestation"""
    id: str
    type: AttestationType
    subjects: List[AttestationSubject]
    predicate: Dict[str, Any]
    predicate_type: str
    status: AttestationStatus = AttestationStatus.DRAFT
    signature: Optional[str] = None
    certificate: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_statement(self) -> Dict[str, Any]:
        """Convert to in-toto statement format"""
        return {
            '_type': 'https://in-toto.io/Statement/v1',
            'predicateType': self.predicate_type,
            'subject': [s.to_dict() for s in self.subjects],
            'predicate': self.predicate
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with full metadata"""
        return {
            'id': self.id,
            'type': self.type.value,
            'status': self.status.value,
            'statement': self.to_statement(),
            'signature': self.signature,
            'certificate': self.certificate,
            'createdAt': self.created_at.isoformat(),
            'signedAt': self.signed_at.isoformat() if self.signed_at else None,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'metadata': self.metadata
        }
        
    def compute_digest(self) -> str:
        """Compute digest of the attestation statement"""
        statement_json = json.dumps(self.to_statement(), sort_keys=True)
        hasher = hashlib.sha256()
        hasher.update(statement_json.encode())
        return hasher.hexdigest()


@dataclass
class AttestationBundle:
    """Bundle containing attestation with verification material"""
    attestation: Attestation
    dssse_envelope: Optional[Dict[str, Any]] = None
    verification_material: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'mediaType': 'application/vnd.dev.sigstore.bundle+json;version=0.1',
            'attestation': self.attestation.to_dict(),
            'dsseEnvelope': self.dssse_envelope,
            'verificationMaterial': self.verification_material
        }


class AttestationManager:
    """
    Manager for build attestations
    
    Provides functionality to:
    - Create attestations for build artifacts
    - Sign attestations with Sigstore
    - Store and retrieve attestations
    - Verify attestation chains
    """
    
    def __init__(
        self,
        storage_backend: Optional[Any] = None,
        signer: Optional[Callable] = None
    ):
        """
        Initialize the manager
        
        Args:
            storage_backend: Optional storage backend for attestations
            signer: Optional signing function
        """
        self._storage = storage_backend or {}
        self._signer = signer or self._default_signer
        self._attestations: Dict[str, Attestation] = {}
        self._subject_index: Dict[str, List[str]] = {}  # digest -> attestation_ids
        
    def create_attestation(
        self,
        attestation_type: AttestationType,
        subjects: List[Dict[str, Any]],
        predicate: Dict[str, Any],
        predicate_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Attestation:
        """
        Create a new attestation
        
        Args:
            attestation_type: Type of attestation
            subjects: List of subject dictionaries
            predicate: Predicate data
            predicate_type: Override predicate type
            metadata: Optional metadata
            
        Returns:
            Created Attestation object
        """
        attestation_id = str(uuid4())
        
        # Convert subjects
        attestation_subjects = [
            AttestationSubject(
                name=s['name'],
                digest=s['digest'],
                uri=s.get('uri')
            )
            for s in subjects
        ]
        
        attestation = Attestation(
            id=attestation_id,
            type=attestation_type,
            subjects=attestation_subjects,
            predicate=predicate,
            predicate_type=predicate_type or attestation_type.value,
            metadata=metadata or {}
        )
        
        self._attestations[attestation_id] = attestation
        
        # Index by subject digests
        for subject in attestation_subjects:
            for alg, digest in subject.digest.items():
                key = f'{alg}:{digest}'
                if key not in self._subject_index:
                    self._subject_index[key] = []
                self._subject_index[key].append(attestation_id)
                
        logger.info(f'Created attestation: {attestation_id}')
        return attestation
        
    async def sign_attestation(
        self,
        attestation_id: str,
        identity_token: Optional[str] = None
    ) -> Attestation:
        """
        Sign an attestation using Sigstore
        
        Args:
            attestation_id: ID of attestation to sign
            identity_token: Optional OIDC identity token
            
        Returns:
            Signed Attestation object
        """
        attestation = self._attestations.get(attestation_id)
        if not attestation:
            raise ValueError(f'Attestation not found: {attestation_id}')
            
        if attestation.status != AttestationStatus.DRAFT:
            raise ValueError(f'Attestation is not in draft status: {attestation.status}')
            
        # Compute attestation digest
        digest = attestation.compute_digest()
        
        # Sign using configured signer
        signature_result = await self._signer(digest, identity_token)
        
        attestation.signature = signature_result.get('signature')
        attestation.certificate = signature_result.get('certificate')
        attestation.signed_at = datetime.now(timezone.utc)
        attestation.status = AttestationStatus.SIGNED
        
        logger.info(f'Signed attestation: {attestation_id}')
        return attestation
        
    def get_attestation(self, attestation_id: str) -> Optional[Attestation]:
        """Get an attestation by ID"""
        return self._attestations.get(attestation_id)
        
    def get_attestations_for_artifact(
        self,
        digest: str,
        algorithm: str = 'sha256'
    ) -> List[Attestation]:
        """
        Get all attestations for an artifact
        
        Args:
            digest: Artifact digest
            algorithm: Digest algorithm
            
        Returns:
            List of attestations for the artifact
        """
        key = f'{algorithm}:{digest}'
        attestation_ids = self._subject_index.get(key, [])
        return [
            self._attestations[aid]
            for aid in attestation_ids
            if aid in self._attestations
        ]
        
    def list_attestations(
        self,
        attestation_type: Optional[AttestationType] = None,
        status: Optional[AttestationStatus] = None
    ) -> List[Attestation]:
        """
        List attestations with optional filters
        
        Args:
            attestation_type: Optional type filter
            status: Optional status filter
            
        Returns:
            List of matching attestations
        """
        attestations = list(self._attestations.values())
        
        if attestation_type:
            attestations = [a for a in attestations if a.type == attestation_type]
            
        if status:
            attestations = [a for a in attestations if a.status == status]
            
        return attestations
        
    def verify_attestation(
        self,
        attestation_id: str,
        expected_subjects: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Verify an attestation
        
        Args:
            attestation_id: ID of attestation to verify
            expected_subjects: Optional expected subjects to match
            
        Returns:
            Verification result
        """
        attestation = self._attestations.get(attestation_id)
        if not attestation:
            return {
                'valid': False,
                'error': f'Attestation not found: {attestation_id}'
            }
            
        result = {
            'valid': True,
            'attestation_id': attestation_id,
            'checks': []
        }
        
        # Check signature
        if attestation.status not in (AttestationStatus.SIGNED, AttestationStatus.VERIFIED):
            result['valid'] = False
            result['checks'].append({
                'name': 'signature',
                'passed': False,
                'error': 'Attestation is not signed'
            })
        else:
            result['checks'].append({
                'name': 'signature',
                'passed': True
            })
            
        # Check expiration
        if attestation.expires_at and datetime.now(timezone.utc) > attestation.expires_at:
            result['valid'] = False
            result['checks'].append({
                'name': 'expiration',
                'passed': False,
                'error': 'Attestation has expired'
            })
        else:
            result['checks'].append({
                'name': 'expiration',
                'passed': True
            })
            
        # Check subjects match
        if expected_subjects:
            subjects_match = self._verify_subjects(
                attestation.subjects,
                expected_subjects
            )
            result['checks'].append({
                'name': 'subjects',
                'passed': subjects_match,
                'error': None if subjects_match else 'Subjects do not match'
            })
            if not subjects_match:
                result['valid'] = False
                
        return result
        
    def create_bundle(self, attestation_id: str) -> AttestationBundle:
        """
        Create a Sigstore bundle for an attestation
        
        Args:
            attestation_id: ID of attestation
            
        Returns:
            AttestationBundle
        """
        attestation = self._attestations.get(attestation_id)
        if not attestation:
            raise ValueError(f'Attestation not found: {attestation_id}')
            
        # Create DSSE envelope
        statement = attestation.to_statement()
        statement_json = json.dumps(statement, sort_keys=True)
        payload_base64 = base64.b64encode(statement_json.encode()).decode()
        
        dsse_envelope = {
            'payloadType': 'application/vnd.in-toto+json',
            'payload': payload_base64,
            'signatures': []
        }
        
        if attestation.signature:
            dsse_envelope['signatures'].append({
                'keyid': '',
                'sig': attestation.signature
            })
            
        # Create verification material
        verification_material = {}
        if attestation.certificate:
            verification_material['x509CertificateChain'] = {
                'certificates': [
                    {'rawBytes': base64.b64encode(attestation.certificate.encode()).decode()}
                ]
            }
            
        return AttestationBundle(
            attestation=attestation,
            dssse_envelope=dsse_envelope,
            verification_material=verification_material
        )
        
    def revoke_attestation(self, attestation_id: str, reason: str) -> bool:
        """
        Revoke an attestation
        
        Args:
            attestation_id: ID of attestation to revoke
            reason: Revocation reason
            
        Returns:
            True if revoked, False if not found
        """
        attestation = self._attestations.get(attestation_id)
        if not attestation:
            return False
            
        attestation.status = AttestationStatus.REVOKED
        attestation.metadata['revocation_reason'] = reason
        attestation.metadata['revoked_at'] = datetime.now(timezone.utc).isoformat()
        
        logger.info(f'Revoked attestation: {attestation_id}')
        return True
        
    def delete_attestation(self, attestation_id: str) -> bool:
        """
        Delete an attestation
        
        Args:
            attestation_id: ID of attestation to delete
            
        Returns:
            True if deleted, False if not found
        """
        attestation = self._attestations.pop(attestation_id, None)
        if not attestation:
            return False
            
        # Remove from subject index
        for subject in attestation.subjects:
            for alg, digest in subject.digest.items():
                key = f'{alg}:{digest}'
                if key in self._subject_index:
                    self._subject_index[key] = [
                        aid for aid in self._subject_index[key]
                        if aid != attestation_id
                    ]
                    
        logger.info(f'Deleted attestation: {attestation_id}')
        return True
        
    def export_attestations(
        self,
        attestation_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export attestations
        
        Args:
            attestation_ids: Optional list of IDs to export
            
        Returns:
            Export data
        """
        if attestation_ids:
            attestations = [
                self._attestations[aid]
                for aid in attestation_ids
                if aid in self._attestations
            ]
        else:
            attestations = list(self._attestations.values())
            
        return {
            'version': '1.0.0',
            'exportedAt': datetime.now(timezone.utc).isoformat(),
            'attestations': [a.to_dict() for a in attestations],
            'count': len(attestations)
        }
        
    def _verify_subjects(
        self,
        actual: List[AttestationSubject],
        expected: List[Dict[str, Any]]
    ) -> bool:
        """Verify subjects match expected values"""
        if len(actual) != len(expected):
            return False
            
        for exp in expected:
            found = False
            for act in actual:
                if act.name == exp.get('name') and act.digest == exp.get('digest'):
                    found = True
                    break
            if not found:
                return False
                
        return True
        
    async def _default_signer(
        self,
        digest: str,
        identity_token: Optional[str]
    ) -> Dict[str, Any]:
        """Default signing function (for testing)"""
        # Simulate Sigstore signing
        signature_data = f'sig:{digest}'
        signature = base64.b64encode(signature_data.encode()).decode()
        
        return {
            'signature': signature,
            'certificate': f'-----BEGIN CERTIFICATE-----\n{digest[:64]}\n-----END CERTIFICATE-----'
        }


# Factory functions
def create_attestation_manager(
    storage_backend: Optional[Any] = None,
    signer: Optional[Callable] = None
) -> AttestationManager:
    """Create a new AttestationManager instance"""
    return AttestationManager(storage_backend, signer)


def create_provenance_attestation(
    subjects: List[Dict[str, Any]],
    build_type: str,
    builder_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a SLSA provenance attestation predicate
    
    Args:
        subjects: Artifact subjects
        build_type: Build type URI
        builder_id: Builder identifier
        
    Returns:
        Provenance predicate
    """
    return {
        'buildDefinition': {
            'buildType': build_type,
            'externalParameters': kwargs.get('external_parameters', {}),
            'internalParameters': kwargs.get('internal_parameters', {}),
            'resolvedDependencies': kwargs.get('dependencies', [])
        },
        'runDetails': {
            'builder': {
                'id': builder_id,
                'version': kwargs.get('builder_version', {})
            },
            'metadata': {
                'invocationId': kwargs.get('invocation_id', str(uuid4())),
                'startedOn': kwargs.get('started_on', datetime.now(timezone.utc).isoformat()),
                'finishedOn': kwargs.get('finished_on', datetime.now(timezone.utc).isoformat())
            },
            'byproducts': kwargs.get('byproducts', [])
        }
    }
