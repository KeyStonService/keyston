"""
Supply Chain Security

Ensures worker images are secure and traceable:
- Version locking: Fixed image versions
- SBOM: Software Bill of Materials
- Signatures: Image signing and verification
- Attestation: SLSA provenance

Enterprise procurement will ask about these!
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class AttestationType(Enum):
    """Types of attestations"""
    SLSA_PROVENANCE = "slsa_provenance"
    SBOM = "sbom"
    VULNERABILITY_SCAN = "vulnerability_scan"
    IMAGE_SIGNATURE = "image_signature"
    BUILD_SIGNATURE = "build_signature"


class SBOMFormat(Enum):
    """SBOM format types"""
    SPDX_JSON = "spdx-json"
    SPDX_TAG_VALUE = "spdx-tag-value"
    CYCLONEDX_JSON = "cyclonedx-json"
    CYCLONEDX_XML = "cyclonedx-xml"


class SLSALevel(Enum):
    """SLSA security levels"""
    L0 = 0  # No guarantees
    L1 = 1  # Provenance exists
    L2 = 2  # Hosted build + signed provenance
    L3 = 3  # Hardened build + non-falsifiable provenance


@dataclass
class ImageDigest:
    """Container image digest"""
    algorithm: str = "sha256"
    digest: str = ""

    def __str__(self) -> str:
        return f"{self.algorithm}:{self.digest}"

    @classmethod
    def from_string(cls, digest_str: str) -> "ImageDigest":
        if ":" in digest_str:
            algo, digest = digest_str.split(":", 1)
            return cls(algorithm=algo, digest=digest)
        return cls(digest=digest_str)


@dataclass
class ImageReference:
    """
    Container image reference

    Immutable reference to a specific image version.
    """
    registry: str = "ghcr.io"
    repository: str = "machinenativeops/worker"
    tag: str = "latest"
    digest: ImageDigest | None = None

    @property
    def full_name(self) -> str:
        """Full image name without digest"""
        return f"{self.registry}/{self.repository}:{self.tag}"

    @property
    def immutable_reference(self) -> str:
        """Immutable reference with digest"""
        if self.digest:
            return f"{self.registry}/{self.repository}@{self.digest}"
        return self.full_name


@dataclass
class SBOMPackage:
    """Package entry in SBOM"""
    name: str = ""
    version: str = ""
    supplier: str = ""
    license: str = ""
    purl: str = ""  # Package URL
    checksums: dict[str, str] = field(default_factory=dict)
    vulnerabilities: list[str] = field(default_factory=list)


@dataclass
class SBOM:
    """
    Software Bill of Materials

    Lists all components in a worker image.
    """
    id: UUID = field(default_factory=uuid4)

    # Image this SBOM describes
    image_reference: ImageReference = field(default_factory=ImageReference)

    # Format and version
    format: SBOMFormat = SBOMFormat.SPDX_JSON
    spec_version: str = "2.3"

    # Creation
    created_at: datetime = field(default_factory=datetime.utcnow)
    tool_name: str = ""
    tool_version: str = ""

    # Packages
    packages: list[SBOMPackage] = field(default_factory=list)

    # Document
    document_namespace: str = ""
    document_name: str = ""

    # Stats
    package_count: int = 0
    vulnerability_count: int = 0

    # Raw SBOM document
    raw_document: dict[str, Any] | None = None


@dataclass
class ImageSignature:
    """Container image signature"""
    id: UUID = field(default_factory=uuid4)

    # Image
    image_reference: ImageReference = field(default_factory=ImageReference)

    # Signature
    signature: str = ""
    signature_algorithm: str = "ecdsa-p256"

    # Signing identity
    signer_identity: str = ""  # e.g., "ci@machinenativeops.io"
    signer_issuer: str = ""    # e.g., "https://accounts.google.com"

    # Verification
    public_key: str | None = None
    certificate: str | None = None
    certificate_chain: list[str] = field(default_factory=list)

    # Timestamps
    signed_at: datetime = field(default_factory=datetime.utcnow)
    verified_at: datetime | None = None

    # Sigstore/Cosign specific
    rekor_log_index: int | None = None
    transparency_log_id: str | None = None


@dataclass
class SLSAProvenance:
    """
    SLSA Provenance Attestation

    Documents how an artifact was built.
    """
    id: UUID = field(default_factory=uuid4)

    # Subject (what was built)
    subject_name: str = ""
    subject_digest: ImageDigest = field(default_factory=ImageDigest)

    # Builder
    builder_id: str = ""  # e.g., "https://github.com/actions/runner"
    builder_version: str = ""

    # Build type
    build_type: str = "https://slsa.dev/container/v0.1"

    # SLSA level
    slsa_level: SLSALevel = SLSALevel.L0

    # Invocation (what triggered the build)
    invocation_id: str = ""
    invocation_config_source: str = ""  # e.g., git URL

    # Materials (inputs to the build)
    materials: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    build_started_on: datetime | None = None
    build_finished_on: datetime | None = None
    reproducible: bool = False

    # Source
    source_repository: str = ""
    source_ref: str = ""
    source_digest: str = ""

    # Signature
    signature: ImageSignature | None = None

    # Raw attestation
    raw_attestation: dict[str, Any] | None = None


@dataclass
class ImageAttestation:
    """
    Complete attestation for an image

    Bundles all attestation types together.
    """
    id: UUID = field(default_factory=uuid4)

    # Image
    image_reference: ImageReference = field(default_factory=ImageReference)

    # Attestations
    slsa_provenance: SLSAProvenance | None = None
    sbom: SBOM | None = None
    signature: ImageSignature | None = None

    # Verification status
    verified: bool = False
    verified_at: datetime | None = None
    verification_errors: list[str] = field(default_factory=list)

    # Vulnerability summary
    critical_vulns: int = 0
    high_vulns: int = 0
    medium_vulns: int = 0
    low_vulns: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)


class AttestationStorage(Protocol):
    """Interface for attestation storage"""

    async def save(self, attestation: ImageAttestation) -> ImageAttestation:
        ...

    async def get_by_digest(
        self,
        digest: ImageDigest,
    ) -> ImageAttestation | None:
        ...

    async def get_by_image(
        self,
        image_reference: ImageReference,
    ) -> ImageAttestation | None:
        ...

    async def list_attestations(
        self,
        repository: str,
        limit: int = 100,
    ) -> list[ImageAttestation]:
        ...


class SignatureVerifier(Protocol):
    """Interface for signature verification"""

    async def verify_signature(
        self,
        image_reference: ImageReference,
        signature: ImageSignature,
    ) -> bool:
        ...

    async def verify_provenance(
        self,
        image_reference: ImageReference,
        provenance: SLSAProvenance,
    ) -> bool:
        ...


class SBOMScanner(Protocol):
    """Interface for SBOM scanning"""

    async def scan_vulnerabilities(
        self,
        sbom: SBOM,
    ) -> list[dict[str, Any]]:
        ...


@dataclass
class SupplyChainValidator:
    """
    Supply Chain Validator

    Validates worker images meet security requirements:
    - Image is signed
    - SLSA provenance exists
    - SBOM exists and vulnerabilities are acceptable
    - Image version is allowed
    """

    storage: AttestationStorage | None = None
    signature_verifier: SignatureVerifier | None = None
    sbom_scanner: SBOMScanner | None = None

    # Policy settings
    require_signature: bool = True
    require_slsa_level: SLSALevel = SLSALevel.L2
    require_sbom: bool = True

    # Vulnerability thresholds
    max_critical_vulns: int = 0
    max_high_vulns: int = 5

    # Allowed images
    allowed_registries: list[str] = field(default_factory=lambda: [
        "ghcr.io/machinenativeops",
        "docker.io/machinenativeops",
    ])

    allowed_images: list[str] = field(default_factory=lambda: [
        "ghcr.io/machinenativeops/worker",
        "ghcr.io/machinenativeops/scanner",
    ])

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    async def validate_image(
        self,
        image_reference: ImageReference,
    ) -> tuple[bool, list[str]]:
        """
        Validate an image meets security requirements

        Args:
            image_reference: Image to validate

        Returns:
            Tuple of (valid, errors)
        """
        errors = []

        # Check registry is allowed
        if not self._is_registry_allowed(image_reference):
            errors.append(f"Registry not allowed: {image_reference.registry}")

        # Check image is allowed
        if not self._is_image_allowed(image_reference):
            errors.append(f"Image not allowed: {image_reference.full_name}")

        # Require digest for production
        if not image_reference.digest:
            errors.append("Image must be referenced by digest, not tag")

        # Get attestation
        attestation = None
        if self.storage and image_reference.digest:
            attestation = await self.storage.get_by_digest(image_reference.digest)

        # Check signature
        if self.require_signature:
            if not attestation or not attestation.signature:
                errors.append("Image signature required but not found")
            elif self.signature_verifier:
                is_valid = await self.signature_verifier.verify_signature(
                    image_reference,
                    attestation.signature,
                )
                if not is_valid:
                    errors.append("Image signature verification failed")

        # Check SLSA provenance
        if self.require_slsa_level.value > 0:
            if not attestation or not attestation.slsa_provenance:
                errors.append(
                    f"SLSA L{self.require_slsa_level.value} provenance required but not found"
                )
            elif attestation.slsa_provenance.slsa_level.value < self.require_slsa_level.value:
                errors.append(
                    f"SLSA L{self.require_slsa_level.value} required, "
                    f"got L{attestation.slsa_provenance.slsa_level.value}"
                )

        # Check SBOM and vulnerabilities
        if self.require_sbom:
            if not attestation or not attestation.sbom:
                errors.append("SBOM required but not found")
            else:
                # Check vulnerabilities
                if attestation.critical_vulns > self.max_critical_vulns:
                    errors.append(
                        f"Too many critical vulnerabilities: "
                        f"{attestation.critical_vulns} (max {self.max_critical_vulns})"
                    )
                if attestation.high_vulns > self.max_high_vulns:
                    errors.append(
                        f"Too many high vulnerabilities: "
                        f"{attestation.high_vulns} (max {self.max_high_vulns})"
                    )

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(f"Image validated: {image_reference.immutable_reference}")
        else:
            logger.warning(
                f"Image validation failed: {image_reference.immutable_reference} "
                f"errors={errors}"
            )

        return is_valid, errors

    # ------------------------------------------------------------------
    # Attestation Management
    # ------------------------------------------------------------------

    async def store_attestation(
        self,
        image_reference: ImageReference,
        slsa_provenance: SLSAProvenance | None = None,
        sbom: SBOM | None = None,
        signature: ImageSignature | None = None,
    ) -> ImageAttestation:
        """Store attestation for an image"""
        attestation = ImageAttestation(
            image_reference=image_reference,
            slsa_provenance=slsa_provenance,
            sbom=sbom,
            signature=signature,
        )

        # Scan SBOM for vulnerabilities
        if sbom and self.sbom_scanner:
            vulns = await self.sbom_scanner.scan_vulnerabilities(sbom)
            attestation.critical_vulns = sum(1 for v in vulns if v.get("severity") == "CRITICAL")
            attestation.high_vulns = sum(1 for v in vulns if v.get("severity") == "HIGH")
            attestation.medium_vulns = sum(1 for v in vulns if v.get("severity") == "MEDIUM")
            attestation.low_vulns = sum(1 for v in vulns if v.get("severity") == "LOW")

        if self.storage:
            attestation = await self.storage.save(attestation)

        return attestation

    async def get_attestation(
        self,
        image_reference: ImageReference,
    ) -> ImageAttestation | None:
        """Get attestation for an image"""
        if not self.storage:
            return None

        if image_reference.digest:
            return await self.storage.get_by_digest(image_reference.digest)

        return await self.storage.get_by_image(image_reference)

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _is_registry_allowed(self, image_reference: ImageReference) -> bool:
        """Check if registry is in allowlist"""
        for allowed in self.allowed_registries:
            if image_reference.full_name.startswith(allowed):
                return True
        return False

    def _is_image_allowed(self, image_reference: ImageReference) -> bool:
        """Check if image is in allowlist"""
        full_name = f"{image_reference.registry}/{image_reference.repository}"
        return full_name in self.allowed_images


# ------------------------------------------------------------------
# Image Pinning Helpers
# ------------------------------------------------------------------

@dataclass
class ImagePinConfig:
    """
    Image pinning configuration

    Pins specific image versions for stability and security.
    """
    # Pinned images
    pinned_images: dict[str, str] = field(default_factory=dict)
    # e.g., {"worker": "ghcr.io/mno/worker@sha256:abc123..."}

    # Allowed digest prefixes (for emergency updates)
    allowed_digest_prefixes: dict[str, list[str]] = field(default_factory=dict)

    # Last updated
    updated_at: datetime = field(default_factory=datetime.utcnow)
    updated_by: str | None = None

    def get_pinned_image(self, name: str) -> ImageReference | None:
        """Get pinned image reference"""
        pinned = self.pinned_images.get(name)
        if not pinned:
            return None

        if "@" in pinned:
            base, digest = pinned.rsplit("@", 1)
            if "/" in base:
                parts = base.split("/")
                registry = parts[0]
                repo = "/".join(parts[1:])
                if ":" in repo:
                    repo, tag = repo.rsplit(":", 1)
                else:
                    tag = "latest"
            else:
                registry = "docker.io"
                repo = base
                tag = "latest"

            return ImageReference(
                registry=registry,
                repository=repo,
                tag=tag,
                digest=ImageDigest.from_string(digest),
            )

        return None
