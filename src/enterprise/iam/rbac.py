"""
RBAC (Role-Based Access Control) Manager

Enforces permission checks for all operations.
Any "setting change" MUST check permissions before proceeding.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from enterprise.iam.models import (
    ROLE_PERMISSIONS,
    Membership,
    Permission,
    Role,
)

logger = logging.getLogger(__name__)


class MembershipRepository(Protocol):
    """Repository interface for membership data"""

    async def get_membership(
        self, org_id: UUID, user_id: UUID
    ) -> Membership | None:
        ...

    async def list_memberships_for_user(
        self, user_id: UUID
    ) -> list[Membership]:
        ...

    async def list_memberships_for_org(
        self, org_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[Membership]:
        ...

    async def save_membership(self, membership: Membership) -> Membership:
        ...

    async def delete_membership(self, org_id: UUID, user_id: UUID) -> bool:
        ...

    async def count_memberships(self, org_id: UUID) -> int:
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
class PermissionDeniedError(Exception):
    """Raised when permission check fails"""
    org_id: UUID
    user_id: UUID
    required_permission: Permission
    message: str = ""

    def __post_init__(self):
        self.message = (
            f"Permission denied: user {self.user_id} lacks "
            f"{self.required_permission.value} in org {self.org_id}"
        )
        super().__init__(self.message)


@dataclass
class RBACManager:
    """
    Role-Based Access Control Manager

    Enforces permission checks for all operations.
    Key principle: ANY setting change must pass through permission check.
    """

    membership_repository: MembershipRepository
    audit_logger: AuditLogger | None = None

    # ------------------------------------------------------------------
    # Permission Checking
    # ------------------------------------------------------------------

    async def check_permission(
        self,
        org_id: UUID,
        user_id: UUID,
        permission: Permission,
        raise_on_deny: bool = True,
    ) -> bool:
        """
        Check if user has a specific permission in an organization

        Args:
            org_id: Organization ID (tenant boundary)
            user_id: User to check
            permission: Required permission
            raise_on_deny: If True, raises PermissionDeniedError on failure

        Returns:
            True if permitted, False otherwise (if raise_on_deny=False)

        Raises:
            PermissionDeniedError: If permission denied and raise_on_deny=True
        """
        membership = await self.membership_repository.get_membership(org_id, user_id)

        if not membership or not membership.is_active:
            if raise_on_deny:
                raise PermissionDeniedError(org_id, user_id, permission)
            return False

        user_permissions = ROLE_PERMISSIONS.get(membership.role, set())

        if permission not in user_permissions:
            if raise_on_deny:
                raise PermissionDeniedError(org_id, user_id, permission)
            return False

        return True

    async def check_permissions(
        self,
        org_id: UUID,
        user_id: UUID,
        permissions: list[Permission],
        require_all: bool = True,
    ) -> bool:
        """
        Check multiple permissions at once

        Args:
            org_id: Organization ID
            user_id: User to check
            permissions: List of permissions to check
            require_all: If True, all permissions must be present

        Returns:
            True if check passes
        """
        membership = await self.membership_repository.get_membership(org_id, user_id)

        if not membership or not membership.is_active:
            raise PermissionDeniedError(org_id, user_id, permissions[0])

        user_permissions = ROLE_PERMISSIONS.get(membership.role, set())

        if require_all:
            if not all(p in user_permissions for p in permissions):
                missing = [p for p in permissions if p not in user_permissions]
                raise PermissionDeniedError(org_id, user_id, missing[0])
        else:
            if not any(p in user_permissions for p in permissions):
                raise PermissionDeniedError(org_id, user_id, permissions[0])

        return True

    async def get_user_role(
        self, org_id: UUID, user_id: UUID
    ) -> Role | None:
        """Get user's role in an organization"""
        membership = await self.membership_repository.get_membership(org_id, user_id)
        return membership.role if membership and membership.is_active else None

    async def get_user_permissions(
        self, org_id: UUID, user_id: UUID
    ) -> set[Permission]:
        """Get all permissions a user has in an organization"""
        role = await self.get_user_role(org_id, user_id)
        if not role:
            return set()
        return ROLE_PERMISSIONS.get(role, set())

    async def get_user_organizations(self, user_id: UUID) -> list[dict[str, Any]]:
        """Get all organizations a user belongs to with their roles"""
        memberships = await self.membership_repository.list_memberships_for_user(user_id)
        return [
            {
                "org_id": str(m.org_id),
                "role": m.role.value,
                "is_active": m.is_active,
            }
            for m in memberships
        ]

    # ------------------------------------------------------------------
    # Membership Management
    # ------------------------------------------------------------------

    async def add_member(
        self,
        org_id: UUID,
        user_id: UUID,
        role: Role,
        invited_by: UUID,
        max_members: int = 100,
    ) -> Membership:
        """
        Add a member to an organization

        Requires: ORG_MANAGE_MEMBERS permission
        """
        # Check inviter has permission
        await self.check_permission(org_id, invited_by, Permission.ORG_MANAGE_MEMBERS)

        # Check if already a member
        existing = await self.membership_repository.get_membership(org_id, user_id)
        if existing and existing.is_active:
            raise ValueError(f"User {user_id} is already a member of org {org_id}")

        # Check member limit
        member_count = await self.membership_repository.count_memberships(org_id)
        if member_count >= max_members:
            raise ValueError(f"Member limit reached ({max_members})")

        # Cannot add someone with higher role than yourself
        inviter_role = await self.get_user_role(org_id, invited_by)
        if not self._can_assign_role(inviter_role, role):
            raise ValueError(f"Cannot assign role {role.value} - insufficient privileges")

        membership = Membership(
            org_id=org_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
            invited_at=datetime.utcnow(),
        )

        membership = await self.membership_repository.save_membership(membership)

        # Audit log
        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="member.added",
                actor_id=invited_by,
                resource_type="membership",
                resource_id=str(membership.id),
                details={
                    "user_id": str(user_id),
                    "role": role.value,
                },
            )

        logger.info(f"Member added: user={user_id} org={org_id} role={role.value}")
        return membership

    async def update_member_role(
        self,
        org_id: UUID,
        user_id: UUID,
        new_role: Role,
        updated_by: UUID,
    ) -> Membership:
        """
        Update a member's role

        Requires: ORG_MANAGE_MEMBERS permission
        Cannot demote owner unless you are also owner.
        """
        # Check permission
        await self.check_permission(org_id, updated_by, Permission.ORG_MANAGE_MEMBERS)

        membership = await self.membership_repository.get_membership(org_id, user_id)
        if not membership:
            raise ValueError(f"User {user_id} is not a member of org {org_id}")

        # Cannot change your own role
        if user_id == updated_by:
            raise ValueError("Cannot change your own role")

        # Check role assignment permissions
        updater_role = await self.get_user_role(org_id, updated_by)
        if not self._can_assign_role(updater_role, new_role):
            raise ValueError(f"Cannot assign role {new_role.value}")

        # Cannot demote owner unless you are owner
        if membership.role == Role.OWNER and updater_role != Role.OWNER:
            raise ValueError("Only owners can demote other owners")

        old_role = membership.role
        membership.role = new_role
        membership.updated_at = datetime.utcnow()

        membership = await self.membership_repository.save_membership(membership)

        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="member.role_changed",
                actor_id=updated_by,
                resource_type="membership",
                resource_id=str(membership.id),
                details={
                    "user_id": str(user_id),
                    "old_role": old_role.value,
                    "new_role": new_role.value,
                },
            )

        return membership

    async def remove_member(
        self,
        org_id: UUID,
        user_id: UUID,
        removed_by: UUID,
    ) -> bool:
        """
        Remove a member from an organization

        Requires: ORG_MANAGE_MEMBERS permission
        Cannot remove yourself (use leave_organization instead).
        Cannot remove owner unless you are owner.
        """
        # Check permission
        await self.check_permission(org_id, removed_by, Permission.ORG_MANAGE_MEMBERS)

        if user_id == removed_by:
            raise ValueError("Cannot remove yourself. Use leave_organization instead.")

        membership = await self.membership_repository.get_membership(org_id, user_id)
        if not membership:
            raise ValueError(f"User {user_id} is not a member of org {org_id}")

        # Cannot remove owner unless you are also owner
        if membership.role == Role.OWNER:
            remover_role = await self.get_user_role(org_id, removed_by)
            if remover_role != Role.OWNER:
                raise ValueError("Only owners can remove other owners")

        result = await self.membership_repository.delete_membership(org_id, user_id)

        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="member.removed",
                actor_id=removed_by,
                resource_type="membership",
                resource_id=str(membership.id),
                details={"user_id": str(user_id), "role": membership.role.value},
            )

        return result

    async def leave_organization(
        self,
        org_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Leave an organization voluntarily

        Owners cannot leave if they are the last owner.
        """
        membership = await self.membership_repository.get_membership(org_id, user_id)
        if not membership:
            raise ValueError(f"User {user_id} is not a member of org {org_id}")

        # Check if user is last owner
        if membership.role == Role.OWNER:
            all_memberships = await self.membership_repository.list_memberships_for_org(org_id)
            owner_count = sum(1 for m in all_memberships if m.role == Role.OWNER and m.is_active)
            if owner_count <= 1:
                raise ValueError(
                    "Cannot leave: you are the last owner. Transfer ownership first."
                )

        result = await self.membership_repository.delete_membership(org_id, user_id)

        if self.audit_logger:
            await self.audit_logger.log(
                org_id=org_id,
                action="member.left",
                actor_id=user_id,
                resource_type="membership",
                resource_id=str(membership.id),
                details={"role": membership.role.value},
            )

        return result

    async def list_members(
        self,
        org_id: UUID,
        requester_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        List all members of an organization

        Requires: ORG_READ permission
        """
        await self.check_permission(org_id, requester_id, Permission.ORG_READ)

        memberships = await self.membership_repository.list_memberships_for_org(
            org_id, offset, limit
        )

        return [
            {
                "user_id": str(m.user_id),
                "role": m.role.value,
                "is_active": m.is_active,
                "joined_at": m.accepted_at.isoformat() if m.accepted_at else None,
            }
            for m in memberships
        ]

    # ------------------------------------------------------------------
    # Permission Guards (Decorators)
    # ------------------------------------------------------------------

    def require_permission(self, permission: Permission):
        """
        Decorator for requiring a specific permission

        Usage:
            @rbac.require_permission(Permission.POLICY_UPDATE)
            async def update_policy(org_id, user_id, policy_data):
                ...
        """
        def decorator(func):
            async def wrapper(org_id: UUID, user_id: UUID, *args, **kwargs):
                await self.check_permission(org_id, user_id, permission)
                return await func(org_id, user_id, *args, **kwargs)
            return wrapper
        return decorator

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _can_assign_role(self, assigner_role: Role | None, target_role: Role) -> bool:
        """Check if assigner can assign the target role"""
        if not assigner_role:
            return False

        role_hierarchy = {
            Role.OWNER: 4,
            Role.ADMIN: 3,
            Role.MEMBER: 2,
            Role.READONLY: 1,
            Role.SERVICE: 0,
        }

        assigner_level = role_hierarchy.get(assigner_role, 0)
        target_level = role_hierarchy.get(target_role, 0)

        # Can only assign roles at or below your level
        # Owners can assign any role, admins can assign admin and below, etc.
        return assigner_level >= target_level


@dataclass
class PermissionContext:
    """
    Context object for permission checks

    Use this to pass permission info through the request lifecycle.
    """
    org_id: UUID
    user_id: UUID
    role: Role
    permissions: set[Permission]

    def has_permission(self, permission: Permission) -> bool:
        """Check if context has a specific permission"""
        return permission in self.permissions

    def has_any_permission(self, permissions: list[Permission]) -> bool:
        """Check if context has any of the specified permissions"""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: list[Permission]) -> bool:
        """Check if context has all of the specified permissions"""
        return all(p in self.permissions for p in permissions)

    @classmethod
    async def from_request(
        cls,
        org_id: UUID,
        user_id: UUID,
        rbac_manager: RBACManager,
    ) -> "PermissionContext":
        """Create a permission context from a request"""
        role = await rbac_manager.get_user_role(org_id, user_id)
        if not role:
            raise PermissionDeniedError(
                org_id, user_id, Permission.ORG_READ
            )

        permissions = await rbac_manager.get_user_permissions(org_id, user_id)

        return cls(
            org_id=org_id,
            user_id=user_id,
            role=role,
            permissions=permissions,
        )
