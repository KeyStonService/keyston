"""
Enterprise IAM Data Models

Multi-tenant data models with org_id as the root isolation key.
Every piece of data MUST carry org_id for proper tenant isolation.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class Role(Enum):
    """
    Enterprise RBAC Roles (minimum required set)

    Hierarchy: OWNER > ADMIN > MEMBER > READONLY
    """
    OWNER = "owner"           # Full control, can delete org, manage billing
    ADMIN = "admin"           # Can manage settings, members, but not billing
    MEMBER = "member"         # Can create/modify resources, run analyses
    READONLY = "readonly"     # View-only access
    SERVICE = "service"       # For worker/integration tokens (limited scope)


class Permission(Enum):
    """
    Fine-grained permissions for RBAC enforcement

    Format: RESOURCE_ACTION
    """
    # Organization permissions
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE_MEMBERS = "org:manage_members"
    ORG_MANAGE_BILLING = "org:manage_billing"
    ORG_MANAGE_SSO = "org:manage_sso"

    # Project permissions
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    # Repository permissions
    REPO_CREATE = "repo:create"
    REPO_READ = "repo:read"
    REPO_UPDATE = "repo:update"
    REPO_DELETE = "repo:delete"
    REPO_MANAGE_WEBHOOKS = "repo:manage_webhooks"

    # Policy permissions
    POLICY_CREATE = "policy:create"
    POLICY_READ = "policy:read"
    POLICY_UPDATE = "policy:update"
    POLICY_DELETE = "policy:delete"

    # Analysis/Run permissions
    RUN_CREATE = "run:create"
    RUN_READ = "run:read"
    RUN_CANCEL = "run:cancel"
    RUN_RETRY = "run:retry"

    # Report permissions
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"

    # Integration permissions
    INTEGRATION_CREATE = "integration:create"
    INTEGRATION_READ = "integration:read"
    INTEGRATION_UPDATE = "integration:update"
    INTEGRATION_DELETE = "integration:delete"

    # Token permissions
    TOKEN_CREATE = "token:create"
    TOKEN_READ = "token:read"
    TOKEN_REVOKE = "token:revoke"

    # Audit permissions
    AUDIT_READ = "audit:read"


# Role to Permission mapping
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.OWNER: set(Permission),  # All permissions

    Role.ADMIN: {
        Permission.ORG_READ,
        Permission.ORG_UPDATE,
        Permission.ORG_MANAGE_MEMBERS,
        Permission.ORG_MANAGE_SSO,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.REPO_CREATE,
        Permission.REPO_READ,
        Permission.REPO_UPDATE,
        Permission.REPO_DELETE,
        Permission.REPO_MANAGE_WEBHOOKS,
        Permission.POLICY_CREATE,
        Permission.POLICY_READ,
        Permission.POLICY_UPDATE,
        Permission.POLICY_DELETE,
        Permission.RUN_CREATE,
        Permission.RUN_READ,
        Permission.RUN_CANCEL,
        Permission.RUN_RETRY,
        Permission.REPORT_READ,
        Permission.REPORT_EXPORT,
        Permission.INTEGRATION_CREATE,
        Permission.INTEGRATION_READ,
        Permission.INTEGRATION_UPDATE,
        Permission.INTEGRATION_DELETE,
        Permission.TOKEN_CREATE,
        Permission.TOKEN_READ,
        Permission.TOKEN_REVOKE,
        Permission.AUDIT_READ,
    },

    Role.MEMBER: {
        Permission.ORG_READ,
        Permission.PROJECT_READ,
        Permission.PROJECT_UPDATE,
        Permission.REPO_READ,
        Permission.REPO_UPDATE,
        Permission.POLICY_READ,
        Permission.RUN_CREATE,
        Permission.RUN_READ,
        Permission.RUN_CANCEL,
        Permission.REPORT_READ,
        Permission.REPORT_EXPORT,
        Permission.INTEGRATION_READ,
        Permission.TOKEN_CREATE,
        Permission.TOKEN_READ,
    },

    Role.READONLY: {
        Permission.ORG_READ,
        Permission.PROJECT_READ,
        Permission.REPO_READ,
        Permission.POLICY_READ,
        Permission.RUN_READ,
        Permission.REPORT_READ,
    },

    Role.SERVICE: {
        Permission.REPO_READ,
        Permission.POLICY_READ,
        Permission.RUN_CREATE,
        Permission.RUN_READ,
        Permission.REPORT_READ,
    },
}


class TokenScope(Enum):
    """
    API Token scopes for separation of concerns

    Different token types for different use cases:
    - READ: Read-only access to resources
    - WRITE: Full CRUD on resources
    - INTEGRATION: For external integrations (GitHub App, etc.)
    - WORKER: For background job workers
    """
    READ = "read"
    WRITE = "write"
    INTEGRATION = "integration"
    WORKER = "worker"
    ADMIN = "admin"


@dataclass
class Organization:
    """
    Top-level tenant entity

    org_id is the ROOT isolation key - every piece of data must reference this.
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: str = ""  # URL-friendly identifier
    display_name: str = ""

    # Billing & Plan
    plan: str = "free"  # free, starter, professional, enterprise
    billing_email: str | None = None

    # SSO Configuration
    sso_enabled: bool = False
    sso_provider: str | None = None  # oidc, saml
    sso_config_id: UUID | None = None

    # Quotas
    max_projects: int = 10
    max_repos_per_project: int = 50
    max_members: int = 5
    max_analysis_per_month: int = 1000
    max_concurrent_runs: int = 5

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: UUID | None = None

    # Status
    is_active: bool = True
    suspended_at: datetime | None = None
    suspension_reason: str | None = None

    @property
    def org_id(self) -> UUID:
        """Alias for id - used as tenant isolation root key"""
        return self.id


@dataclass
class Project:
    """
    Project within an Organization

    Groups related repositories together.
    """
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)  # REQUIRED: Tenant isolation key

    name: str = ""
    slug: str = ""
    description: str = ""

    # Settings
    default_branch: str = "main"
    auto_scan_enabled: bool = True

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: UUID | None = None

    is_active: bool = True


@dataclass
class Repository:
    """
    Repository entity linked to a Git provider

    Represents a connection between the platform and an external Git repository.
    """
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)  # REQUIRED: Tenant isolation key
    project_id: UUID = field(default_factory=uuid4)

    name: str = ""
    full_name: str = ""  # e.g., "owner/repo"

    # Git Provider Info
    provider: str = "github"  # github, gitlab, bitbucket
    provider_repo_id: str = ""  # Provider's internal repo ID
    provider_installation_id: str | None = None  # GitHub App installation ID

    clone_url: str = ""
    default_branch: str = "main"

    # Webhook
    webhook_id: str | None = None
    webhook_secret_hash: str | None = None  # Hashed for storage
    webhook_active: bool = False

    # Settings
    gate_enabled: bool = True
    report_enabled: bool = True
    auto_fix_enabled: bool = False

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_sync_at: datetime | None = None

    is_active: bool = True


@dataclass
class User:
    """
    User entity

    Users can belong to multiple organizations with different roles.
    """
    id: UUID = field(default_factory=uuid4)

    email: str = ""
    username: str = ""
    display_name: str = ""
    avatar_url: str | None = None

    # Authentication
    password_hash: str | None = None  # For email/password auth
    email_verified: bool = False

    # SSO/OIDC fields
    sso_provider: str | None = None
    sso_subject: str | None = None  # OIDC 'sub' claim

    # 2FA
    mfa_enabled: bool = False
    mfa_secret_hash: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: datetime | None = None

    is_active: bool = True


@dataclass
class Membership:
    """
    Organization membership - links Users to Organizations with Roles
    """
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)  # REQUIRED: Tenant isolation key
    user_id: UUID = field(default_factory=uuid4)

    role: Role = Role.MEMBER

    # Invitation
    invited_by: UUID | None = None
    invited_at: datetime | None = None
    accepted_at: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    is_active: bool = True


@dataclass
class APIToken:
    """
    API Token for programmatic access

    Tokens are scoped, can be revoked, rotated, and have expiration.
    """
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)  # REQUIRED: Tenant isolation key

    name: str = ""
    description: str = ""

    # Token value (only shown once at creation)
    token_hash: str = ""  # SHA-256 hash of the actual token
    token_prefix: str = ""  # First 8 chars for identification (e.g., "mno_abc1")

    # Scope
    scope: TokenScope = TokenScope.READ
    permissions: list[str] = field(default_factory=list)  # Fine-grained permissions

    # Ownership
    created_by: UUID | None = None
    is_personal: bool = True  # True if user token, False if org/service token

    # Validity
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    last_used_ip: str | None = None

    # Rotation
    rotated_from: UUID | None = None  # Previous token if rotated
    rotated_at: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    revoked_at: datetime | None = None
    revoked_by: UUID | None = None
    revoke_reason: str | None = None

    @property
    def is_valid(self) -> bool:
        """Check if token is currently valid"""
        if self.revoked_at is not None:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    @staticmethod
    def generate_token() -> tuple[str, str, str]:
        """
        Generate a new API token

        Returns: (raw_token, token_hash, token_prefix)
        """
        raw_token = f"mno_{secrets.token_urlsafe(32)}"
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_prefix = raw_token[:12]
        return raw_token, token_hash, token_prefix


@dataclass
class SSOConfig:
    """
    SSO/OIDC Configuration for an Organization

    Stores the configuration needed for enterprise SSO integration.
    """
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)  # REQUIRED: Tenant isolation key

    provider_type: str = "oidc"  # oidc, saml

    # OIDC Settings
    issuer_url: str | None = None
    client_id: str | None = None
    client_secret_hash: str | None = None  # Encrypted in DB

    # SAML Settings
    idp_entity_id: str | None = None
    idp_sso_url: str | None = None
    idp_certificate_hash: str | None = None

    # Mapping
    attribute_mapping: dict[str, str] = field(default_factory=dict)
    # e.g., {"email": "preferred_email", "name": "displayName"}

    # Default role for new SSO users
    default_role: Role = Role.MEMBER

    # JIT (Just-In-Time) Provisioning
    jit_enabled: bool = True
    jit_allowed_domains: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    is_active: bool = True


@dataclass
class OIDCProvider:
    """
    OIDC Provider configuration (for SSO extension point)

    This is the extension point mentioned in the requirements -
    MVP can use email/password + magic link, but backend must support OIDC/SAML.
    """
    id: UUID = field(default_factory=uuid4)

    name: str = ""  # e.g., "Okta", "Azure AD", "Google Workspace"
    provider_type: str = "oidc"  # oidc, saml, oauth2

    # Discovery
    discovery_url: str | None = None  # .well-known/openid-configuration

    # Endpoints (if not using discovery)
    authorization_endpoint: str | None = None
    token_endpoint: str | None = None
    userinfo_endpoint: str | None = None
    jwks_uri: str | None = None

    # Scopes
    default_scopes: list[str] = field(default_factory=lambda: ["openid", "email", "profile"])

    # Claim mapping
    claim_mapping: dict[str, str] = field(default_factory=lambda: {
        "sub": "sso_subject",
        "email": "email",
        "name": "display_name",
    })

    # Status
    is_verified: bool = False
    is_active: bool = True

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
