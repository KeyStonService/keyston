"""
Phase 20: SLSA L3 Provenance System

This module provides comprehensive SLSA (Supply-chain Levels for Software Artifacts)
Level 3 compliance including:
- Provenance generation
- Signature verification with Sigstore
- Build attestation
- Artifact verification

Key Components:
- ProvenanceGenerator: Generate SLSA-compliant provenance
- SignatureVerifier: Verify signatures using Sigstore
- AttestationManager: Manage build attestations
- ArtifactVerifier: Verify artifact integrity
"""

from .provenance_generator import ProvenanceGenerator, Provenance, BuildDefinition, SLSALevel
from .signature_verifier import SignatureVerifier, SignatureResult, VerificationPolicy, SignatureType
from .attestation_manager import AttestationManager, Attestation, AttestationType
from .artifact_verifier import ArtifactVerifier, VerificationResult, ArtifactMetadata

__all__ = [
    'ProvenanceGenerator',
    'Provenance',
    'BuildDefinition',
    'SLSALevel',
    'SignatureVerifier',
    'SignatureResult',
    'VerificationPolicy',
    'SignatureType',
    'AttestationManager',
    'Attestation',
    'AttestationType',
    'ArtifactVerifier',
    'VerificationResult',
    'ArtifactMetadata',
]

__version__ = '1.0.0'
__author__ = 'SynergyMesh Team'
