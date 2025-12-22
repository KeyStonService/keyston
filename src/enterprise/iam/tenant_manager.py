"""
Tenant Manager - Multi-tenant Operations

Handles tenant (Organization) lifecycle and ensures proper isolation.
Every operation MUST be scoped to org_id.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from enterprise.iam.models import (
    Organization,
    Project,
    Repository,
)

logger = logging.getLogger(__name__)


class TenantRepository(Protocol):
    """Repository interface for tenant data persistence"""

    async def save_organization(self, org: Organization) -> Organization:
        ...

    async def get_organization(self, org_id: UUID) -> Organization | None:
        ...

    async def get_organization_by_slug(self, slug: str) -> Organization | None:
        ...

    async def update_organization(self, org: Organization) -> Organization:
        ...

    async def delete_organization(self, org_id: UUID) -> bool:
        ...

    async def list_organizations(
        self,
        user_id: UUID | None = None,
        offset: int = 0,
        limit: int = 100
    ) -> list[Organization]:
        ...

    async def save_project(self, project: Project) -> Project:
        ...

    async def get_project(self, org_id: UUID, project_id: UUID) -> Project | None:
        ...

    async def list_projects(
        self,
        org_id: UUID,
        offset: int = 0,
        limit: int = 100
    ) -> list[Project]:
        ...

    async def save_repository(self, repo: Repository) -> Repository:
        ...

    async def get_repository(self, org_id: UUID, repo_id: UUID) -> Repository | None:
        ...

    async def list_repositories(
        self,
        org_id: UUID,
        project_id: UUID | None = None,
        offset: int = 0,
        limit: int = 100
    ) -> list[Repository]:
        ...


class TenantEventPublisher(Protocol):
    """Event publisher for tenant lifecycle events"""

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        ...


@dataclass
class TenantManager:
    """
    Manages multi-tenant operations

    Key principle: org_id is the isolation boundary.
    Every query, mutation, and operation must be scoped to org_id.
    """

    repository: TenantRepository
    event_publisher: TenantEventPublisher | None = None

    # Validation patterns
    SLUG_PATTERN = re.compile(r'^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$')
    RESERVED_SLUGS = frozenset([
        'admin', 'api', 'app', 'auth', 'billing', 'console',
        'dashboard', 'help', 'login', 'logout', 'register',
        'settings', 'status', 'support', 'system', 'www',
    ])

    # ------------------------------------------------------------------
    # Organization Operations
    # ------------------------------------------------------------------

    async def create_organization(
        self,
        name: str,
        slug: str,
        created_by: UUID,
        display_name: str | None = None,
        plan: str = "free",
    ) -> Organization:
        """
        Create a new organization (tenant)

        Args:
            name: Organization name
            slug: URL-friendly identifier
            created_by: User ID of the creator
            display_name: Optional display name
            plan: Subscription plan

        Returns:
            Created Organization

        Raises:
            ValueError: If slug is invalid or taken
        """
        # Validate slug
        slug = slug.lower().strip()
        if not self._validate_slug(slug):
            raise ValueError(
                f"Invalid slug '{slug}'. Must be 3-40 chars, lowercase alphanumeric with hyphens."
            )

        if slug in self.RESERVED_SLUGS:
            raise ValueError(f"Slug '{slug}' is reserved.")

        # Check uniqueness
        existing = await self.repository.get_organization_by_slug(slug)
        if existing:
            raise ValueError(f"Slug '{slug}' is already taken.")

        # Create organization
        org = Organization(
            name=name,
            slug=slug,
            display_name=display_name or name,
            plan=plan,
            created_by=created_by,
        )

        # Apply plan quotas
        self._apply_plan_quotas(org)

        # Persist
        org = await self.repository.save_organization(org)

        # Publish event
        if self.event_publisher:
            await self.event_publisher.publish(
                "organization.created",
                {
                    "org_id": str(org.id),
                    "slug": org.slug,
                    "created_by": str(created_by),
                }
            )

        logger.info(f"Organization created: {org.slug} (id={org.id})")
        return org

    async def get_organization(self, org_id: UUID) -> Organization | None:
        """Get organization by ID"""
        return await self.repository.get_organization(org_id)

    async def get_organization_by_slug(self, slug: str) -> Organization | None:
        """Get organization by slug"""
        return await self.repository.get_organization_by_slug(slug.lower())

    async def update_organization(
        self,
        org_id: UUID,
        updates: dict[str, Any],
        updated_by: UUID,
    ) -> Organization:
        """
        Update organization settings

        Allowed fields: name, display_name, billing_email
        """
        org = await self.repository.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization not found: {org_id}")

        # Apply allowed updates
        allowed_fields = {'name', 'display_name', 'billing_email'}
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(org, field, value)

        org.updated_at = datetime.utcnow()
        org = await self.repository.update_organization(org)

        if self.event_publisher:
            await self.event_publisher.publish(
                "organization.updated",
                {
                    "org_id": str(org_id),
                    "updated_by": str(updated_by),
                    "fields": list(updates.keys()),
                }
            )

        return org

    async def suspend_organization(
        self,
        org_id: UUID,
        reason: str,
        suspended_by: UUID,
    ) -> Organization:
        """Suspend an organization (e.g., for billing issues)"""
        org = await self.repository.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization not found: {org_id}")

        org.is_active = False
        org.suspended_at = datetime.utcnow()
        org.suspension_reason = reason
        org = await self.repository.update_organization(org)

        if self.event_publisher:
            await self.event_publisher.publish(
                "organization.suspended",
                {
                    "org_id": str(org_id),
                    "reason": reason,
                    "suspended_by": str(suspended_by),
                }
            )

        logger.warning(f"Organization suspended: {org.slug} - {reason}")
        return org

    # ------------------------------------------------------------------
    # Project Operations
    # ------------------------------------------------------------------

    async def create_project(
        self,
        org_id: UUID,
        name: str,
        slug: str,
        created_by: UUID,
        description: str = "",
    ) -> Project:
        """
        Create a project within an organization

        IMPORTANT: org_id is the isolation boundary.
        """
        # Verify org exists and is active
        org = await self.repository.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization not found: {org_id}")
        if not org.is_active:
            raise ValueError(f"Organization is suspended: {org_id}")

        # Check quota
        projects = await self.repository.list_projects(org_id)
        if len(projects) >= org.max_projects:
            raise ValueError(
                f"Project limit reached ({org.max_projects}). Upgrade plan for more."
            )

        # Validate slug
        slug = slug.lower().strip()
        if not self._validate_slug(slug):
            raise ValueError(f"Invalid project slug: {slug}")

        project = Project(
            org_id=org_id,  # CRITICAL: Tenant isolation
            name=name,
            slug=slug,
            description=description,
            created_by=created_by,
        )

        project = await self.repository.save_project(project)

        if self.event_publisher:
            await self.event_publisher.publish(
                "project.created",
                {
                    "org_id": str(org_id),
                    "project_id": str(project.id),
                    "created_by": str(created_by),
                }
            )

        return project

    async def get_project(self, org_id: UUID, project_id: UUID) -> Project | None:
        """
        Get project by ID

        IMPORTANT: Always pass org_id for tenant isolation.
        """
        return await self.repository.get_project(org_id, project_id)

    async def list_projects(
        self,
        org_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        """List projects for an organization"""
        return await self.repository.list_projects(org_id, offset, limit)

    # ------------------------------------------------------------------
    # Repository Operations
    # ------------------------------------------------------------------

    async def create_repository(
        self,
        org_id: UUID,
        project_id: UUID,
        name: str,
        full_name: str,
        provider: str,
        provider_repo_id: str,
        clone_url: str,
        created_by: UUID,
        provider_installation_id: str | None = None,
    ) -> Repository:
        """
        Register a repository for analysis

        IMPORTANT: org_id is the isolation boundary.
        """
        # Verify project exists
        project = await self.repository.get_project(org_id, project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")

        # Check org quota
        org = await self.repository.get_organization(org_id)
        repos = await self.repository.list_repositories(org_id, project_id)
        if len(repos) >= org.max_repos_per_project:
            raise ValueError(
                f"Repository limit reached for project ({org.max_repos_per_project})."
            )

        repo = Repository(
            org_id=org_id,  # CRITICAL: Tenant isolation
            project_id=project_id,
            name=name,
            full_name=full_name,
            provider=provider,
            provider_repo_id=provider_repo_id,
            provider_installation_id=provider_installation_id,
            clone_url=clone_url,
        )

        repo = await self.repository.save_repository(repo)

        if self.event_publisher:
            await self.event_publisher.publish(
                "repository.created",
                {
                    "org_id": str(org_id),
                    "project_id": str(project_id),
                    "repo_id": str(repo.id),
                    "provider": provider,
                    "full_name": full_name,
                }
            )

        return repo

    async def get_repository(self, org_id: UUID, repo_id: UUID) -> Repository | None:
        """Get repository by ID with tenant isolation"""
        return await self.repository.get_repository(org_id, repo_id)

    async def list_repositories(
        self,
        org_id: UUID,
        project_id: UUID | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Repository]:
        """List repositories for org/project"""
        return await self.repository.list_repositories(org_id, project_id, offset, limit)

    # ------------------------------------------------------------------
    # Tenant Isolation Utilities
    # ------------------------------------------------------------------

    def verify_tenant_access(
        self,
        requested_org_id: UUID,
        user_org_ids: list[UUID],
    ) -> bool:
        """
        Verify user has access to the requested organization

        This is a critical security check - never skip it.
        """
        return requested_org_id in user_org_ids

    async def get_tenant_context(self, org_id: UUID) -> dict[str, Any]:
        """
        Get tenant context for request processing

        Returns quotas, settings, and status for the tenant.
        """
        org = await self.repository.get_organization(org_id)
        if not org:
            raise ValueError(f"Organization not found: {org_id}")

        return {
            "org_id": str(org.id),
            "slug": org.slug,
            "plan": org.plan,
            "is_active": org.is_active,
            "quotas": {
                "max_projects": org.max_projects,
                "max_repos_per_project": org.max_repos_per_project,
                "max_members": org.max_members,
                "max_analysis_per_month": org.max_analysis_per_month,
                "max_concurrent_runs": org.max_concurrent_runs,
            },
            "features": {
                "sso_enabled": org.sso_enabled,
            },
        }

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _validate_slug(self, slug: str) -> bool:
        """Validate slug format"""
        return bool(self.SLUG_PATTERN.match(slug))

    def _apply_plan_quotas(self, org: Organization) -> None:
        """Apply quotas based on subscription plan"""
        plan_quotas = {
            "free": {
                "max_projects": 3,
                "max_repos_per_project": 10,
                "max_members": 3,
                "max_analysis_per_month": 100,
                "max_concurrent_runs": 2,
            },
            "starter": {
                "max_projects": 10,
                "max_repos_per_project": 50,
                "max_members": 10,
                "max_analysis_per_month": 1000,
                "max_concurrent_runs": 5,
            },
            "professional": {
                "max_projects": 50,
                "max_repos_per_project": 200,
                "max_members": 50,
                "max_analysis_per_month": 10000,
                "max_concurrent_runs": 20,
            },
            "enterprise": {
                "max_projects": 500,
                "max_repos_per_project": 1000,
                "max_members": 500,
                "max_analysis_per_month": 100000,
                "max_concurrent_runs": 100,
            },
        }

        quotas = plan_quotas.get(org.plan, plan_quotas["free"])
        for key, value in quotas.items():
            setattr(org, key, value)
