"""
API Token Manager

Manages API tokens with:
- Usage separation (read, write, integration, worker)
- Revocation
- Rotation
- Expiration
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol
from uuid import UUID

from enterprise.iam.models import (
    APIToken,
    Permission,
    TokenScope,
)

logger = logging.getLogger(__name__)


# Token scope to permissions mapping
SCOPE_PERMISSIONS: dict[TokenScope, list[Permission]] = {
    TokenScope.READ: [
        Permission.ORG_READ,
        Permission.PROJECT_READ,
        Permission.REPO_READ,
        Permission.POLICY_READ,
        Permission.RUN_READ,
        Permission.REPORT_READ,
    ],
    TokenScope.WRITE: [
        Permission.ORG_READ,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.REPO_READ,
        Permission.REPO_UPDATE,
        Permission.POLICY_READ,
        Permission.POLICY_CREATE,
        Permission.POLICY_UPDATE,
        Permission.RUN_CREATE,
        Permission.RUN_READ,
        Permission.RUN_CANCEL,
        Permission.REPORT_READ,
        Permission.REPORT_EXPORT,
    ],
    TokenScope.INTEGRATION: [
        Permission.REPO_READ,
        Permission.REPO_MANAGE_WEBHOOKS,
        Permission.RUN_CREATE,
        Permission.RUN_READ,
        Permission.INTEGRATION_READ,
        Permission.INTEGRATION_UPDATE,
    ],
    TokenScope.WORKER: [
        Permission.REPO_READ,
        Permission.POLICY_READ,
        Permission.RUN_CREATE,
        Permission.RUN_READ,
    ],
    TokenScope.ADMIN: list(Permission),  # All permissions
}


class TokenRepository(Protocol):
    """Repository interface for token storage"""

    async def save_token(self, token: APIToken) -> APIToken:
        ...

    async def get_token_by_hash(self, token_hash: str) -> APIToken | None:
        ...

    async def get_token_by_id(
        self, org_id: UUID, token_id: UUID
    ) -> APIToken | None:
        ...

    async def list_tokens(
        self,
        org_id: UUID,
        user_id: UUID | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[APIToken]:
        ...

    async def update_token(self, token: APIToken) -> APIToken:
        ...

    async def delete_token(self, org_id: UUID, token_id: UUID) -> bool:
        ...


class AuditLogger(Protocol):
    """Interface for audit logging"""

    async def log(
        self,
        org_id: UUID,
        action: str,
        actor_id: UUID,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any],
    ) -> None:
        ...


@dataclass
class TokenValidationResult:
    """Result of token validation"""
    valid: bool
    token: APIToken | None = None
    org_id: UUID | None = None
    permissions: list[Permission] = None
    error: str | None = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []


@dataclass
class TokenManager:
    """
    API Token Manager

    Manages tokens with:
    - Scoped access (read, write, integration, worker)
    - Revocation support
    - Rotation (create new, invalidate old)
    - Expiration enforcement
    """

    repository: TokenRepository
    audit_logger: AuditLogger | None = None

    # Default token validity periods
    DEFAULT_EXPIRY_DAYS = 90
    MAX_EXPIRY_DAYS = 365

    # Token prefix for identification
    TOKEN_PREFIX = "mno_"

    # ------------------------------------------------------------------
    # Token Creation
    # ------------------------------------------------------------------

    async def create_token(
        self,
        org_id: UUID,
        name: str,
        scope: TokenScope,
        created_by: UUID,
        description: str = "",
        expires_in_days: int | None = None,
        is_personal: bool = True,
        custom_permissions: list[Permission] | None = None,
    ) -> tuple[str, APIToken]:
        """
        Create a new API token

        Args:
            org_id: Organization the token belongs to
            name: Human-readable token name
            scope: Token scope (read, write, integration, worker)
            created_by: User creating the token
            description: Optional description
            expires_in_days: Token validity period (None for non-expiring)
            is_personal: True if personal token, False if org/service token
            custom_permissions: Override default scope permissions

        Returns:
            Tuple of (raw_token, token_entity)
            raw_token is ONLY returned once - store it securely!
        """
        # Generate token
        raw_token = self._generate_raw_token()
        token_hash = self._hash_token(raw_token)
        token_prefix = raw_token[:12]  # "mno_" + 8 chars

        # Calculate expiration
        expires_at = None
        if expires_in_days is not None:
            expires_in_days = min(expires_in_days, self.MAX_EXPIRY_DAYS)
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Determine permissions
        if custom_permissions:
            permissions = [p.value for p in custom_permissions]
        else:
            permissions = [p.value for p in SCOPE_PERMISSIONS.get(scope, [])]

        token = APIToken(
            org_id=org_id,
            name=name,
            description=description,
            token_hash=token_hash,
            token_prefix=token_prefix,
            scope=scope,
            permissions=permissions,
            created_by=created_by,
            is_personal=is_personal,
            expires_at=expires_at,
        )

        token = await self.repository.save_token(token)

        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="token.created",
                actor_id=created_by,
                resource_type="api_token",
                resource_id=str(token.id),
                details={
                    "name": name,
                    "scope": scope.value,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                },
            )

        logger.info(f"Token created: {token_prefix}... org={org_id} scope={scope.value}")

        return raw_token, token

    async def create_service_token(
        self,
        org_id: UUID,
        name: str,
        scope: TokenScope,
        created_by: UUID,
        description: str = "",
    ) -> tuple[str, APIToken]:
        """
        Create a service token (non-personal, for integrations/workers)

        Service tokens:
        - Are not tied to a specific user
        - Have longer expiry (or none)
        - Used for automated systems
        """
        return await self.create_token(
            org_id=org_id,
            name=name,
            scope=scope,
            created_by=created_by,
            description=description,
            expires_in_days=None,  # No expiry for service tokens
            is_personal=False,
        )

    # ------------------------------------------------------------------
    # Token Validation
    # ------------------------------------------------------------------

    async def validate_token(self, raw_token: str) -> TokenValidationResult:
        """
        Validate a token and return its permissions

        Args:
            raw_token: The raw token string (e.g., "mno_abc123...")

        Returns:
            TokenValidationResult with validation status and permissions
        """
        if not raw_token or not raw_token.startswith(self.TOKEN_PREFIX):
            return TokenValidationResult(
                valid=False,
                error="Invalid token format"
            )

        token_hash = self._hash_token(raw_token)
        token = await self.repository.get_token_by_hash(token_hash)

        if not token:
            return TokenValidationResult(
                valid=False,
                error="Token not found"
            )

        # Check if revoked
        if token.revoked_at is not None:
            return TokenValidationResult(
                valid=False,
                error="Token has been revoked"
            )

        # Check expiration
        if token.expires_at and datetime.utcnow() > token.expires_at:
            return TokenValidationResult(
                valid=False,
                error="Token has expired"
            )

        # Update last used
        token.last_used_at = datetime.utcnow()
        await self.repository.update_token(token)

        # Parse permissions
        permissions = [Permission(p) for p in token.permissions if p in [e.value for e in Permission]]

        return TokenValidationResult(
            valid=True,
            token=token,
            org_id=token.org_id,
            permissions=permissions,
        )

    async def validate_token_permission(
        self,
        raw_token: str,
        required_permission: Permission,
    ) -> TokenValidationResult:
        """
        Validate token and check for a specific permission

        Args:
            raw_token: The raw token string
            required_permission: Permission that must be present

        Returns:
            TokenValidationResult (valid=False if permission missing)
        """
        result = await self.validate_token(raw_token)

        if not result.valid:
            return result

        if required_permission not in result.permissions:
            return TokenValidationResult(
                valid=False,
                token=result.token,
                org_id=result.org_id,
                permissions=result.permissions,
                error=f"Token lacks required permission: {required_permission.value}"
            )

        return result

    # ------------------------------------------------------------------
    # Token Management
    # ------------------------------------------------------------------

    async def revoke_token(
        self,
        org_id: UUID,
        token_id: UUID,
        revoked_by: UUID,
        reason: str = "",
    ) -> bool:
        """
        Revoke a token (make it permanently invalid)

        Args:
            org_id: Organization ID (for tenant isolation)
            token_id: Token to revoke
            revoked_by: User revoking the token
            reason: Reason for revocation

        Returns:
            True if revoked successfully
        """
        token = await self.repository.get_token_by_id(org_id, token_id)

        if not token:
            raise ValueError(f"Token not found: {token_id}")

        if token.revoked_at is not None:
            raise ValueError("Token is already revoked")

        token.revoked_at = datetime.utcnow()
        token.revoked_by = revoked_by
        token.revoke_reason = reason

        await self.repository.update_token(token)

        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="token.revoked",
                actor_id=revoked_by,
                resource_type="api_token",
                resource_id=str(token_id),
                details={"reason": reason, "token_prefix": token.token_prefix},
            )

        logger.info(f"Token revoked: {token.token_prefix}... reason={reason}")
        return True

    async def rotate_token(
        self,
        org_id: UUID,
        token_id: UUID,
        rotated_by: UUID,
    ) -> tuple[str, APIToken]:
        """
        Rotate a token (create new, revoke old)

        This is a security best practice - regularly rotate tokens.

        Args:
            org_id: Organization ID
            token_id: Token to rotate
            rotated_by: User performing rotation

        Returns:
            Tuple of (new_raw_token, new_token_entity)
        """
        old_token = await self.repository.get_token_by_id(org_id, token_id)

        if not old_token:
            raise ValueError(f"Token not found: {token_id}")

        if old_token.revoked_at is not None:
            raise ValueError("Cannot rotate a revoked token")

        # Create new token with same properties
        raw_token, new_token = await self.create_token(
            org_id=org_id,
            name=old_token.name,
            scope=old_token.scope,
            created_by=rotated_by,
            description=old_token.description,
            expires_in_days=self.DEFAULT_EXPIRY_DAYS,
            is_personal=old_token.is_personal,
            custom_permissions=[Permission(p) for p in old_token.permissions],
        )

        # Mark rotation lineage
        new_token.rotated_from = old_token.id
        new_token.rotated_at = datetime.utcnow()
        await self.repository.update_token(new_token)

        # Revoke old token
        await self.revoke_token(
            org_id=org_id,
            token_id=token_id,
            revoked_by=rotated_by,
            reason="Rotated to new token",
        )

        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="token.rotated",
                actor_id=rotated_by,
                resource_type="api_token",
                resource_id=str(new_token.id),
                details={
                    "old_token_id": str(token_id),
                    "new_token_prefix": new_token.token_prefix,
                },
            )

        logger.info(
            f"Token rotated: {old_token.token_prefix}... -> {new_token.token_prefix}..."
        )

        return raw_token, new_token

    async def list_tokens(
        self,
        org_id: UUID,
        user_id: UUID | None = None,
        include_revoked: bool = False,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        List tokens for an organization

        Args:
            org_id: Organization ID
            user_id: Filter by creator (None for all)
            include_revoked: Include revoked tokens
            offset: Pagination offset
            limit: Pagination limit

        Returns:
            List of token info (excluding sensitive data)
        """
        tokens = await self.repository.list_tokens(org_id, user_id, offset, limit)

        result = []
        for token in tokens:
            if not include_revoked and token.revoked_at is not None:
                continue

            result.append({
                "id": str(token.id),
                "name": token.name,
                "description": token.description,
                "token_prefix": token.token_prefix,
                "scope": token.scope.value,
                "is_personal": token.is_personal,
                "created_at": token.created_at.isoformat(),
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
                "is_expired": (
                    token.expires_at is not None
                    and datetime.utcnow() > token.expires_at
                ),
                "is_revoked": token.revoked_at is not None,
            })

        return result

    async def cleanup_expired_tokens(
        self,
        org_id: UUID,
        dry_run: bool = True,
    ) -> int:
        """
        Clean up expired tokens

        Args:
            org_id: Organization ID
            dry_run: If True, only count without deleting

        Returns:
            Number of tokens cleaned up (or would be)
        """
        tokens = await self.repository.list_tokens(org_id, limit=10000)

        expired_count = 0
        for token in tokens:
            if token.expires_at and datetime.utcnow() > token.expires_at:
                if not dry_run:
                    await self.repository.delete_token(org_id, token.id)
                expired_count += 1

        logger.info(
            f"Expired token cleanup: org={org_id} count={expired_count} dry_run={dry_run}"
        )

        return expired_count

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _generate_raw_token(self) -> str:
        """Generate a cryptographically secure token"""
        return f"{self.TOKEN_PREFIX}{secrets.token_urlsafe(32)}"

    def _hash_token(self, raw_token: str) -> str:
        """Hash a token for storage"""
        return hashlib.sha256(raw_token.encode()).hexdigest()
