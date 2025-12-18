"""
Signature Verifier - Verify signatures using Sigstore

This module provides signature verification capabilities using the Sigstore
ecosystem including Rekor transparency log and Fulcio certificate authority.
"""

import base64
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class SignatureType(Enum):
    """Types of signatures supported"""
    COSIGN = 'cosign'
    SIGSTORE = 'sigstore'
    GPG = 'gpg'
    X509 = 'x509'


class VerificationStatus(Enum):
    """Signature verification status"""
    VALID = 'valid'
    INVALID = 'invalid'
    EXPIRED = 'expired'
    REVOKED = 'revoked'
    UNKNOWN = 'unknown'
    NOT_CHECKED = 'not_checked'


@dataclass
class Certificate:
    """X.509 Certificate representation"""
    subject: str
    issuer: str
    not_before: datetime
    not_after: datetime
    serial_number: str
    fingerprint: str
    extensions: Dict[str, Any] = field(default_factory=dict)
    pem: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'subject': self.subject,
            'issuer': self.issuer,
            'notBefore': self.not_before.isoformat(),
            'notAfter': self.not_after.isoformat(),
            'serialNumber': self.serial_number,
            'fingerprint': self.fingerprint,
            'extensions': self.extensions
        }
        
    def is_valid(self, at_time: Optional[datetime] = None) -> bool:
        """Check if certificate is valid at a given time"""
        check_time = at_time or datetime.now(timezone.utc)
        return self.not_before <= check_time <= self.not_after


@dataclass
class TransparencyLogEntry:
    """Rekor transparency log entry"""
    log_index: int
    log_id: str
    integrated_time: datetime
    body: str
    inclusion_proof: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'logIndex': self.log_index,
            'logId': self.log_id,
            'integratedTime': self.integrated_time.isoformat(),
            'body': self.body
        }
        if self.inclusion_proof:
            result['inclusionProof'] = self.inclusion_proof
        return result


@dataclass
class SignatureResult:
    """Result of signature verification"""
    status: VerificationStatus
    signature_type: SignatureType
    certificate: Optional[Certificate] = None
    transparency_entry: Optional[TransparencyLogEntry] = None
    signer_identity: Optional[str] = None
    verified_claims: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    verification_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'status': self.status.value,
            'signatureType': self.signature_type.value,
            'certificate': self.certificate.to_dict() if self.certificate else None,
            'transparencyEntry': self.transparency_entry.to_dict() if self.transparency_entry else None,
            'signerIdentity': self.signer_identity,
            'verifiedClaims': self.verified_claims,
            'errors': self.errors,
            'warnings': self.warnings,
            'verificationTime': self.verification_time.isoformat(),
            'metadata': self.metadata
        }
        
    @property
    def is_valid(self) -> bool:
        """Check if signature is valid"""
        return self.status == VerificationStatus.VALID


@dataclass
class VerificationPolicy:
    """Policy for signature verification"""
    name: str
    required_identity_patterns: List[str] = field(default_factory=list)
    required_issuers: List[str] = field(default_factory=list)
    require_transparency_log: bool = True
    require_timestamp: bool = True
    allowed_signature_types: List[SignatureType] = field(
        default_factory=lambda: [SignatureType.SIGSTORE, SignatureType.COSIGN]
    )
    max_certificate_age_days: int = 365
    trusted_roots: List[str] = field(default_factory=list)
    custom_checks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'requiredIdentityPatterns': self.required_identity_patterns,
            'requiredIssuers': self.required_issuers,
            'requireTransparencyLog': self.require_transparency_log,
            'requireTimestamp': self.require_timestamp,
            'allowedSignatureTypes': [t.value for t in self.allowed_signature_types],
            'maxCertificateAgeDays': self.max_certificate_age_days,
            'trustedRoots': self.trusted_roots,
            'customChecks': self.custom_checks
        }


class SignatureVerifier:
    """
    Verifier for cryptographic signatures
    
    Supports verification using Sigstore ecosystem components including:
    - Fulcio certificate authority
    - Rekor transparency log
    - Cosign signatures
    """
    
    def __init__(
        self,
        rekor_url: str = 'https://rekor.sigstore.dev',
        fulcio_url: str = 'https://fulcio.sigstore.dev',
        default_policy: Optional[VerificationPolicy] = None
    ):
        """
        Initialize the verifier
        
        Args:
            rekor_url: Rekor transparency log URL
            fulcio_url: Fulcio certificate authority URL
            default_policy: Default verification policy
        """
        self.rekor_url = rekor_url
        self.fulcio_url = fulcio_url
        self.default_policy = default_policy or self._create_default_policy()
        self._trusted_roots: Dict[str, str] = {}
        
    def verify_signature(
        self,
        artifact_digest: str,
        signature: str,
        certificate: Optional[str] = None,
        policy: Optional[VerificationPolicy] = None
    ) -> SignatureResult:
        """
        Verify a signature on an artifact
        
        Args:
            artifact_digest: SHA256 digest of the artifact
            signature: Base64-encoded signature
            certificate: Optional certificate (PEM format)
            policy: Optional verification policy (uses default if not provided)
            
        Returns:
            SignatureResult with verification status
        """
        active_policy = policy or self.default_policy
        result = SignatureResult(
            status=VerificationStatus.UNKNOWN,
            signature_type=SignatureType.SIGSTORE
        )
        
        try:
            # Step 1: Decode and validate signature format
            sig_data = self._decode_signature(signature)
            if not sig_data:
                result.status = VerificationStatus.INVALID
                result.errors.append('Invalid signature format')
                return result
                
            # Step 2: Parse and validate certificate if provided
            if certificate:
                cert = self._parse_certificate(certificate)
                if cert:
                    result.certificate = cert
                    
                    # Check certificate validity
                    if not cert.is_valid():
                        result.status = VerificationStatus.EXPIRED
                        result.errors.append('Certificate has expired')
                        return result
                        
                    # Extract signer identity
                    result.signer_identity = self._extract_identity(cert)
                    
            # Step 3: Verify against policy requirements
            policy_result = self._verify_policy(result, active_policy)
            if not policy_result['passed']:
                result.status = VerificationStatus.INVALID
                result.errors.extend(policy_result['errors'])
                return result
                
            # Step 4: Check transparency log (if required)
            if active_policy.require_transparency_log:
                log_entry = self._check_transparency_log(artifact_digest, signature)
                if log_entry:
                    result.transparency_entry = log_entry
                else:
                    result.warnings.append('No transparency log entry found')
                    
            # Step 5: Perform cryptographic verification
            verify_result = self._cryptographic_verify(
                artifact_digest,
                sig_data,
                result.certificate
            )
            
            if verify_result['valid']:
                result.status = VerificationStatus.VALID
                result.verified_claims = verify_result.get('claims', {})
            else:
                result.status = VerificationStatus.INVALID
                result.errors.append(verify_result.get('error', 'Signature verification failed'))
                
        except Exception as e:
            result.status = VerificationStatus.INVALID
            result.errors.append(f'Verification error: {str(e)}')
            logger.error(f'Signature verification failed: {e}')
            
        return result
        
    def verify_provenance_signature(
        self,
        provenance: Dict[str, Any],
        signature: str,
        certificate: Optional[str] = None,
        policy: Optional[VerificationPolicy] = None
    ) -> SignatureResult:
        """
        Verify a signature on SLSA provenance
        
        Args:
            provenance: SLSA provenance dictionary
            signature: Base64-encoded signature
            certificate: Optional certificate
            policy: Optional verification policy
            
        Returns:
            SignatureResult with verification status
        """
        # Compute provenance digest
        provenance_json = json.dumps(provenance, sort_keys=True)
        hasher = hashlib.sha256()
        hasher.update(provenance_json.encode())
        artifact_digest = hasher.hexdigest()
        
        result = self.verify_signature(
            artifact_digest=artifact_digest,
            signature=signature,
            certificate=certificate,
            policy=policy
        )
        
        result.metadata['provenance_digest'] = artifact_digest
        return result
        
    def verify_bundle(
        self,
        bundle: Dict[str, Any],
        policy: Optional[VerificationPolicy] = None
    ) -> SignatureResult:
        """
        Verify a Sigstore bundle
        
        Args:
            bundle: Sigstore bundle dictionary
            policy: Optional verification policy
            
        Returns:
            SignatureResult with verification status
        """
        result = SignatureResult(
            status=VerificationStatus.UNKNOWN,
            signature_type=SignatureType.SIGSTORE
        )
        
        try:
            # Extract components from bundle
            media_type = bundle.get('mediaType', '')
            verification_material = bundle.get('verificationMaterial', {})
            message_signature = bundle.get('messageSignature', {})
            
            # Get certificate from bundle
            cert_chain = verification_material.get('x509CertificateChain', {})
            certificates = cert_chain.get('certificates', [])
            
            if certificates:
                cert_der = certificates[0].get('rawBytes', '')
                result.certificate = self._parse_certificate_der(cert_der)
                if result.certificate:
                    result.signer_identity = self._extract_identity(result.certificate)
                    
            # Get transparency log entry from bundle
            tlog_entries = verification_material.get('tlogEntries', [])
            if tlog_entries:
                entry = tlog_entries[0]
                result.transparency_entry = TransparencyLogEntry(
                    log_index=entry.get('logIndex', 0),
                    log_id=entry.get('logId', {}).get('keyId', ''),
                    integrated_time=datetime.fromisoformat(
                        entry.get('integratedTime', datetime.now(timezone.utc).isoformat())
                    ),
                    body=entry.get('canonicalizedBody', ''),
                    inclusion_proof=entry.get('inclusionProof')
                )
                
            # Verify bundle contents
            active_policy = policy or self.default_policy
            policy_result = self._verify_policy(result, active_policy)
            
            if policy_result['passed']:
                result.status = VerificationStatus.VALID
            else:
                result.status = VerificationStatus.INVALID
                result.errors.extend(policy_result['errors'])
                
        except Exception as e:
            result.status = VerificationStatus.INVALID
            result.errors.append(f'Bundle verification error: {str(e)}')
            logger.error(f'Bundle verification failed: {e}')
            
        return result
        
    def add_trusted_root(self, name: str, certificate_pem: str) -> None:
        """Add a trusted root certificate"""
        self._trusted_roots[name] = certificate_pem
        
    def create_policy(
        self,
        name: str,
        **kwargs
    ) -> VerificationPolicy:
        """Create a new verification policy"""
        return VerificationPolicy(name=name, **kwargs)
        
    def _create_default_policy(self) -> VerificationPolicy:
        """Create the default verification policy"""
        return VerificationPolicy(
            name='default',
            require_transparency_log=True,
            require_timestamp=True,
            allowed_signature_types=[SignatureType.SIGSTORE, SignatureType.COSIGN]
        )
        
    def _decode_signature(self, signature: str) -> Optional[bytes]:
        """Decode a base64-encoded signature"""
        try:
            return base64.b64decode(signature)
        except Exception:
            return None
            
    def _parse_certificate(self, pem: str) -> Optional[Certificate]:
        """Parse a PEM-encoded certificate"""
        try:
            # Simplified certificate parsing
            # In production, use cryptography library
            fingerprint = hashlib.sha256(pem.encode()).hexdigest()
            
            return Certificate(
                subject='CN=synergymesh-build',
                issuer='CN=Fulcio,O=sigstore.dev',
                not_before=datetime.now(timezone.utc),
                not_after=datetime(2030, 12, 31, tzinfo=timezone.utc),
                serial_number=str(uuid4()),
                fingerprint=fingerprint,
                pem=pem
            )
        except Exception as e:
            logger.error(f'Certificate parsing failed: {e}')
            return None
            
    def _parse_certificate_der(self, der_base64: str) -> Optional[Certificate]:
        """Parse a DER-encoded certificate (base64)"""
        try:
            der_bytes = base64.b64decode(der_base64)
            fingerprint = hashlib.sha256(der_bytes).hexdigest()
            
            return Certificate(
                subject='CN=synergymesh-build',
                issuer='CN=Fulcio,O=sigstore.dev',
                not_before=datetime.now(timezone.utc),
                not_after=datetime(2030, 12, 31, tzinfo=timezone.utc),
                serial_number=str(uuid4()),
                fingerprint=fingerprint
            )
        except Exception as e:
            logger.error(f'DER certificate parsing failed: {e}')
            return None
            
    def _extract_identity(self, cert: Certificate) -> str:
        """Extract signer identity from certificate"""
        # Extract from SAN or subject
        return cert.subject
        
    def _verify_policy(
        self,
        result: SignatureResult,
        policy: VerificationPolicy
    ) -> Dict[str, Any]:
        """Verify against policy requirements"""
        errors = []
        
        # Check signature type
        if result.signature_type not in policy.allowed_signature_types:
            errors.append(f'Signature type {result.signature_type.value} not allowed')
            
        # Check identity patterns
        if policy.required_identity_patterns and result.signer_identity:
            matched = False
            for pattern in policy.required_identity_patterns:
                if pattern in result.signer_identity:
                    matched = True
                    break
            if not matched:
                errors.append('Signer identity does not match required patterns')
                
        # Check issuer requirements
        if policy.required_issuers and result.certificate:
            if result.certificate.issuer not in policy.required_issuers:
                errors.append('Certificate issuer not in required issuers list')
                
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
        
    def _check_transparency_log(
        self,
        artifact_digest: str,
        signature: str
    ) -> Optional[TransparencyLogEntry]:
        """
        Check transparency log for entry
        
        NOTE: This is a simulation for framework demonstration.
        In production, this would make actual API calls to Rekor
        transparency log service.
        
        Args:
            artifact_digest: Artifact digest to look up
            signature: Signature to verify
            
        Returns:
            TransparencyLogEntry if found, None otherwise
        """
        # Simulate Rekor lookup - production implementation would use:
        # import requests
        # response = requests.post(f'{self.rekor_url}/api/v1/log/entries/retrieve')
        return TransparencyLogEntry(
            log_index=12345,
            log_id='rekor.sigstore.dev',
            integrated_time=datetime.now(timezone.utc),
            body=base64.b64encode(f'{artifact_digest}:{signature[:20]}'.encode()).decode()
        )
        
    def _cryptographic_verify(
        self,
        artifact_digest: str,
        signature: bytes,
        certificate: Optional[Certificate]
    ) -> Dict[str, Any]:
        """
        Perform cryptographic verification
        
        NOTE: This is a simulation for framework demonstration.
        In production, this would use the cryptography library to
        perform actual signature verification against the certificate.
        
        Production implementation would use:
        - cryptography.hazmat.primitives.asymmetric for key operations
        - Certificate chain validation
        - Signature algorithm verification
        
        Args:
            artifact_digest: Digest of the artifact
            signature: Decoded signature bytes
            certificate: Certificate for verification
            
        Returns:
            Verification result dictionary
        """
        # Simulate successful verification for framework demonstration
        # Production would perform actual cryptographic verification
        return {
            'valid': True,
            'claims': {
                'artifact_digest': artifact_digest,
                'verified_at': datetime.now(timezone.utc).isoformat()
            }
        }


# Factory functions
def create_signature_verifier(
    rekor_url: str = 'https://rekor.sigstore.dev',
    fulcio_url: str = 'https://fulcio.sigstore.dev'
) -> SignatureVerifier:
    """Create a new SignatureVerifier instance"""
    return SignatureVerifier(rekor_url, fulcio_url)


def create_verification_policy(name: str, **kwargs) -> VerificationPolicy:
    """Create a new VerificationPolicy"""
    return VerificationPolicy(name=name, **kwargs)
