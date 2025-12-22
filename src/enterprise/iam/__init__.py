"""
Enterprise IAM (Identity and Access Management) Module

This module provides multi-tenant identity management with:
- Tenant Model: Organization / Project / Repository hierarchy
- RBAC: Role-Based Access Control with Owner/Admin/Member/ReadOnly roles
- SSO/OIDC: Extension points for enterprise SSO integration
- API Token Management: Scoped tokens with rotation and revocation

All data must carry org_id as the tenant isolation root key.
"""

from enterprise.iam.models import (
    APIToken,
    Membership,
    OIDCProvider,
    Organization,
    Permission,
    Project,
    Repository,
    Role,
    SSOConfig,
    TokenScope,
    User,
)
from enterprise.iam.rbac import RBACManager
from enterprise.iam.sso import SSOManager
from enterprise.iam.tenant_manager import TenantManager
from enterprise.iam.token_manager import TokenManager

__all__ = [
    # Models
    "Organization",
    "Project",
    "Repository",
    "User",
    "Membership",
    "Role",
    "Permission",
    "APIToken",
    "TokenScope",
    "SSOConfig",
    "OIDCProvider",
    # Managers
    "TenantManager",
    "RBACManager",
    "TokenManager",
    "SSOManager",
]
