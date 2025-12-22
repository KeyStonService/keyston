"""
Secrets Manager

Securely manages sensitive credentials:
- Provider tokens (GitHub, GitLab)
- Webhook secrets
- API keys
- Encryption keys

Uses KMS/Vault/Secret Manager for secure storage.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Types of secrets"""
    WEBHOOK_SECRET = "webhook_secret"
    PROVIDER_TOKEN = "provider_token"
    API_KEY = "api_key"
    ENCRYPTION_KEY = "encryption_key"
    OAUTH_CLIENT_SECRET = "oauth_client_secret"
    SIGNING_KEY = "signing_key"
    DATABASE_PASSWORD = "database_password"
    SERVICE_ACCOUNT = "service_account"
    CUSTOM = "custom"


class SecretScope(Enum):
    """Scope of secret access"""
    ORGANIZATION = "organization"    # Available to entire org
    PROJECT = "project"             # Available to specific project
    REPOSITORY = "repository"       # Available to specific repo
    SYSTEM = "system"               # System-level (not tenant-specific)


@dataclass
class Secret:
    """
    Secret metadata

    NOTE: The actual secret value is never stored in this object.
    Only the encrypted version is stored in the backend.
    """
    id: UUID = field(default_factory=uuid4)

    # Identity
    name: str = ""
    description: str = ""
    secret_type: SecretType = SecretType.CUSTOM

    # Scope
    scope: SecretScope = SecretScope.ORGANIZATION
    org_id: UUID | None = None
    project_id: UUID | None = None
    repo_id: UUID | None = None

    # Metadata
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: UUID | None = None

    # Expiration
    expires_at: datetime | None = None
    rotation_interval_days: int | None = None
    last_rotated_at: datetime | None = None

    # Audit
    last_accessed_at: datetime | None = None
    access_count: int = 0

    # Tags
    tags: dict[str, str] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if secret is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def needs_rotation(self) -> bool:
        """Check if secret needs rotation"""
        if not self.rotation_interval_days:
            return False
        if not self.last_rotated_at:
            return True
        rotation_due = self.last_rotated_at + timedelta(days=self.rotation_interval_days)
        return datetime.utcnow() > rotation_due


class KMSProvider(Protocol):
    """Interface for Key Management Service"""

    async def encrypt(
        self,
        plaintext: bytes,
        key_id: str,
        context: dict[str, str] | None = None,
    ) -> bytes:
        """Encrypt data with a KMS key"""
        ...

    async def decrypt(
        self,
        ciphertext: bytes,
        key_id: str,
        context: dict[str, str] | None = None,
    ) -> bytes:
        """Decrypt data with a KMS key"""
        ...

    async def generate_data_key(
        self,
        key_id: str,
        context: dict[str, str] | None = None,
    ) -> tuple[bytes, bytes]:
        """Generate a data key, return (plaintext, encrypted)"""
        ...


class SecretStorage(Protocol):
    """Interface for secret storage"""

    async def save(
        self,
        secret: Secret,
        encrypted_value: bytes,
    ) -> Secret:
        """Save a secret with its encrypted value"""
        ...

    async def get(
        self,
        secret_id: UUID,
    ) -> tuple[Secret, bytes] | None:
        """Get a secret and its encrypted value"""
        ...

    async def get_by_name(
        self,
        name: str,
        scope: SecretScope,
        org_id: UUID | None = None,
        project_id: UUID | None = None,
        repo_id: UUID | None = None,
    ) -> tuple[Secret, bytes] | None:
        """Get a secret by name and scope"""
        ...

    async def list(
        self,
        org_id: UUID,
        secret_type: SecretType | None = None,
    ) -> list[Secret]:
        """List secrets (metadata only)"""
        ...

    async def update(
        self,
        secret: Secret,
        encrypted_value: bytes | None = None,
    ) -> Secret:
        """Update a secret"""
        ...

    async def delete(
        self,
        secret_id: UUID,
    ) -> bool:
        """Delete a secret"""
        ...


class AuditLogger(Protocol):
    """Interface for audit logging"""

    async def log(
        self,
        org_id: UUID | None,
        action: str,
        actor_id: UUID | None,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any],
    ) -> None:
        ...


@dataclass
class SecretsManager:
    """
    Secrets Manager

    Securely manages secrets with:
    - Encryption at rest (via KMS)
    - Access auditing
    - Automatic rotation
    - Scope-based access control
    """

    storage: SecretStorage
    kms_provider: KMSProvider
    audit_logger: AuditLogger | None = None

    # KMS key IDs (different keys for different purposes)
    master_key_id: str = "alias/mno-secrets-master"
    provider_key_id: str = "alias/mno-provider-secrets"

    # Encryption context template
    _encryption_context_template: dict[str, str] = field(default_factory=lambda: {
        "service": "machinenativeops",
        "purpose": "secrets",
    })

    # ------------------------------------------------------------------
    # Secret Creation
    # ------------------------------------------------------------------

    async def create_secret(
        self,
        name: str,
        value: str,
        secret_type: SecretType,
        org_id: UUID | None = None,
        scope: SecretScope = SecretScope.ORGANIZATION,
        project_id: UUID | None = None,
        repo_id: UUID | None = None,
        created_by: UUID | None = None,
        expires_at: datetime | None = None,
        rotation_interval_days: int | None = None,
        tags: dict[str, str] | None = None,
    ) -> Secret:
        """
        Create a new secret

        The value is encrypted before storage.

        Args:
            name: Secret name (unique within scope)
            value: Secret value (will be encrypted)
            secret_type: Type of secret
            org_id: Organization ID (for tenant-scoped secrets)
            scope: Access scope
            project_id: Project ID (if project-scoped)
            repo_id: Repository ID (if repo-scoped)
            created_by: User who created the secret
            expires_at: Optional expiration time
            rotation_interval_days: Days between rotations
            tags: Optional tags

        Returns:
            Created secret (without value)
        """
        # Encrypt the value
        key_id = self._get_key_id_for_type(secret_type)
        context = self._build_encryption_context(org_id, secret_type)

        encrypted_value = await self.kms_provider.encrypt(
            value.encode("utf-8"),
            key_id,
            context,
        )

        # Create secret metadata
        secret = Secret(
            name=name,
            secret_type=secret_type,
            scope=scope,
            org_id=org_id,
            project_id=project_id,
            repo_id=repo_id,
            created_by=created_by,
            expires_at=expires_at,
            rotation_interval_days=rotation_interval_days,
            last_rotated_at=datetime.utcnow(),
            tags=tags or {},
        )

        # Store
        secret = await self.storage.save(secret, encrypted_value)

        # Audit log
        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="secret.created",
                actor_id=created_by,
                resource_type="secret",
                resource_id=str(secret.id),
                details={
                    "name": name,
                    "type": secret_type.value,
                    "scope": scope.value,
                },
            )

        logger.info(
            f"Secret created: name={name} type={secret_type.value} "
            f"scope={scope.value}"
        )

        return secret

    # ------------------------------------------------------------------
    # Secret Retrieval
    # ------------------------------------------------------------------

    async def get_secret_value(
        self,
        secret_id: UUID,
        accessed_by: UUID | None = None,
    ) -> str | None:
        """
        Retrieve a secret's value

        The value is decrypted before returning.
        Access is audited.
        """
        result = await self.storage.get(secret_id)
        if not result:
            return None

        secret, encrypted_value = result

        # Check expiration
        if secret.is_expired:
            logger.warning("Attempted access to expired secret")
            return None

        # Decrypt
        key_id = self._get_key_id_for_type(secret.secret_type)
        context = self._build_encryption_context(secret.org_id, secret.secret_type)

        try:
            plaintext = await self.kms_provider.decrypt(
                encrypted_value,
                key_id,
                context,
            )
        except Exception as e:
            secret_id_hash = hashlib.sha256(str(secret_id).encode("utf-8")).hexdigest()[:8]
            logger.error(f"Failed to decrypt secret (id_hash={secret_id_hash}): {e}")
            return None

        # Update access metadata
        secret.last_accessed_at = datetime.utcnow()
        secret.access_count += 1
        await self.storage.update(secret)

        # Audit log
        if self.audit_logger:
            await self.audit_logger.log(
                org_id=secret.org_id,
                action="secret.accessed",
                actor_id=accessed_by,
                resource_type="secret",
                resource_id=str(secret_id),
                details={"name": secret.name},
            )

        return plaintext.decode("utf-8")

    async def get_secret_by_name(
        self,
        name: str,
        org_id: UUID | None = None,
        scope: SecretScope = SecretScope.ORGANIZATION,
        project_id: UUID | None = None,
        repo_id: UUID | None = None,
        accessed_by: UUID | None = None,
    ) -> str | None:
        """Get secret value by name and scope"""
        result = await self.storage.get_by_name(
            name, scope, org_id, project_id, repo_id
        )
        if not result:
            return None

        secret, _ = result
        return await self.get_secret_value(secret.id, accessed_by)

    async def get_secret_metadata(
        self,
        secret_id: UUID,
    ) -> Secret | None:
        """Get secret metadata (without value)"""
        result = await self.storage.get(secret_id)
        return result[0] if result else None

    # ------------------------------------------------------------------
    # Secret Management
    # ------------------------------------------------------------------

    async def rotate_secret(
        self,
        secret_id: UUID,
        new_value: str,
        rotated_by: UUID | None = None,
    ) -> Secret:
        """
        Rotate a secret (update its value)

        Args:
            secret_id: Secret to rotate
            new_value: New secret value
            rotated_by: User performing rotation

        Returns:
            Updated secret
        """
        result = await self.storage.get(secret_id)
        if not result:
            raise ValueError(f"Secret not found: {secret_id}")

        secret, _ = result

        # Encrypt new value
        key_id = self._get_key_id_for_type(secret.secret_type)
        context = self._build_encryption_context(secret.org_id, secret.secret_type)

        encrypted_value = await self.kms_provider.encrypt(
            new_value.encode("utf-8"),
            key_id,
            context,
        )

        # Update secret
        secret.version += 1
        secret.updated_at = datetime.utcnow()
        secret.last_rotated_at = datetime.utcnow()

        secret = await self.storage.update(secret, encrypted_value)

        # Audit log
        if self.audit_logger:
            await self.audit_logger.log(
                org_id=secret.org_id,
                action="secret.rotated",
                actor_id=rotated_by,
                resource_type="secret",
                resource_id=str(secret_id),
                details={
                    "name": secret.name,
                    "new_version": secret.version,
                },
            )

        logger.info("Secret rotated: name=%s version=%s", secret.name, secret.version)

        return secret

    async def delete_secret(
        self,
        secret_id: UUID,
        deleted_by: UUID | None = None,
    ) -> bool:
        """Delete a secret"""
        result = await self.storage.get(secret_id)
        if not result:
            return False

        secret, _ = result

        success = await self.storage.delete(secret_id)

        if success and self.audit_logger:
            await self.audit_logger.log(
                org_id=secret.org_id,
                action="secret.deleted",
                actor_id=deleted_by,
                resource_type="secret",
                resource_id=str(secret_id),
                details={"name": secret.name},
            )

        return success

    async def list_secrets(
        self,
        org_id: UUID,
        secret_type: SecretType | None = None,
    ) -> list[Secret]:
        """List secrets (metadata only, no values)"""
        return await self.storage.list(org_id, secret_type)

    # ------------------------------------------------------------------
    # Rotation Monitoring
    # ------------------------------------------------------------------

    async def get_secrets_needing_rotation(
        self,
        org_id: UUID | None = None,
    ) -> list[Secret]:
        """Get secrets that need rotation"""
        all_secrets = await self.storage.list(org_id)
        return [s for s in all_secrets if s.needs_rotation]

    async def get_expiring_secrets(
        self,
        org_id: UUID | None = None,
        within_days: int = 7,
    ) -> list[Secret]:
        """Get secrets expiring soon"""
        all_secrets = await self.storage.list(org_id)
        cutoff = datetime.utcnow() + timedelta(days=within_days)

        return [
            s for s in all_secrets
            if s.expires_at and s.expires_at < cutoff
        ]

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _get_key_id_for_type(self, secret_type: SecretType) -> str:
        """Get KMS key ID for secret type"""
        # Use different keys for different secret types for isolation
        if secret_type in {SecretType.PROVIDER_TOKEN, SecretType.OAUTH_CLIENT_SECRET}:
            return self.provider_key_id
        return self.master_key_id

    def _build_encryption_context(
        self,
        org_id: UUID | None,
        secret_type: SecretType,
    ) -> dict[str, str]:
        """Build encryption context for KMS"""
        context = {**self._encryption_context_template}

        if org_id:
            context["org_id"] = str(org_id)

        context["secret_type"] = secret_type.value

        return context


# ------------------------------------------------------------------
# Convenience Functions
# ------------------------------------------------------------------

async def get_webhook_secret(
    secrets_manager: SecretsManager,
    org_id: UUID,
    repo_id: UUID,
) -> str | None:
    """Get webhook secret for a repository"""
    return await secrets_manager.get_secret_by_name(
        name=f"webhook-{repo_id}",
        org_id=org_id,
        scope=SecretScope.REPOSITORY,
        repo_id=repo_id,
    )


async def get_provider_token(
    secrets_manager: SecretsManager,
    org_id: UUID,
    installation_id: str,
) -> str | None:
    """Get provider installation token"""
    return await secrets_manager.get_secret_by_name(
        name=f"installation-token-{installation_id}",
        org_id=org_id,
        scope=SecretScope.ORGANIZATION,
    )
