"""
Git Provider Manager

Manages Git provider integrations including:
- GitHub App / OAuth App installations
- GitLab integrations
- Token management and refresh
- Authorization state tracking
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class GitProvider(Enum):
    """Supported Git providers"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class AuthType(Enum):
    """Authentication type"""
    GITHUB_APP = "github_app"
    OAUTH_APP = "oauth_app"
    PERSONAL_TOKEN = "personal_token"
    GITLAB_INTEGRATION = "gitlab_integration"
    BITBUCKET_APP = "bitbucket_app"


@dataclass
class ProviderAuth:
    """
    Provider authentication credentials

    Handles token storage and refresh.
    """
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)  # Tenant isolation

    provider: GitProvider = GitProvider.GITHUB
    auth_type: AuthType = AuthType.GITHUB_APP

    # For GitHub App
    installation_id: str | None = None
    app_id: str | None = None

    # Tokens (encrypted in storage)
    access_token_encrypted: str | None = None
    refresh_token_encrypted: str | None = None

    # Token metadata
    token_expires_at: datetime | None = None
    token_scopes: list[str] = field(default_factory=list)

    # Status
    is_active: bool = True
    last_used_at: datetime | None = None
    last_refreshed_at: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return False
        # Add 5 minute buffer
        return datetime.utcnow() > (self.token_expires_at - timedelta(minutes=5))


@dataclass
class ProviderInstallation:
    """
    Git provider installation record

    Tracks where the app is installed and its permissions.
    """
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)  # Tenant isolation

    provider: GitProvider = GitProvider.GITHUB
    auth_id: UUID | None = None  # Link to ProviderAuth

    # Installation details
    installation_id: str = ""  # Provider's installation ID
    account_type: str = "Organization"  # Organization, User
    account_login: str = ""
    account_id: str = ""

    # Authorized repositories
    repository_selection: str = "all"  # all, selected
    authorized_repos: list[str] = field(default_factory=list)  # list of repo full names

    # Permissions granted
    permissions: dict[str, str] = field(default_factory=dict)
    # e.g., {"checks": "write", "contents": "read", "pull_requests": "write"}

    # Events subscribed
    events: list[str] = field(default_factory=list)
    # e.g., ["push", "pull_request", "check_run"]

    # Status
    is_active: bool = True
    suspended_at: datetime | None = None
    suspension_reason: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class ProviderRepository(Protocol):
    """Repository interface for provider data"""

    async def save_auth(self, auth: ProviderAuth) -> ProviderAuth:
        ...

    async def get_auth(self, org_id: UUID, auth_id: UUID) -> ProviderAuth | None:
        ...

    async def get_auth_by_installation(
        self, org_id: UUID, installation_id: str
    ) -> ProviderAuth | None:
        ...

    async def update_auth(self, auth: ProviderAuth) -> ProviderAuth:
        ...

    async def save_installation(
        self, installation: ProviderInstallation
    ) -> ProviderInstallation:
        ...

    async def get_installation(
        self, org_id: UUID, installation_id: str
    ) -> ProviderInstallation | None:
        ...

    async def list_installations(
        self, org_id: UUID
    ) -> list[ProviderInstallation]:
        ...

    async def update_installation(
        self, installation: ProviderInstallation
    ) -> ProviderInstallation:
        ...


class SecretsManager(Protocol):
    """Interface for secrets management"""

    async def encrypt(self, value: str) -> str:
        """Encrypt a value for storage"""
        ...

    async def decrypt(self, encrypted: str) -> str:
        """Decrypt a stored value"""
        ...


class HTTPClient(Protocol):
    """HTTP client interface"""

    async def get(
        self,
        url: str,
        headers: dict[str, str] = None,
    ) -> dict[str, Any]:
        ...

    async def post(
        self,
        url: str,
        data: dict[str, Any] = None,
        headers: dict[str, str] = None,
    ) -> dict[str, Any]:
        ...


@dataclass
class GitProviderManager:
    """
    Git Provider Manager

    Manages provider integrations including:
    - Installation lifecycle
    - Token management and refresh
    - Rate limit handling
    """

    repository: ProviderRepository
    secrets_manager: SecretsManager
    http_client: HTTPClient

    # GitHub App configuration
    github_app_id: str | None = None
    github_app_private_key: str | None = None

    # Rate limit tracking
    _rate_limits: dict[str, dict[str, Any]] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Installation Management
    # ------------------------------------------------------------------

    async def register_github_installation(
        self,
        org_id: UUID,
        installation_id: str,
        account_login: str,
        account_id: str,
        account_type: str = "Organization",
        repository_selection: str = "all",
        repositories: list[str] | None = None,
        permissions: dict[str, str] | None = None,
        events: list[str] | None = None,
    ) -> ProviderInstallation:
        """
        Register a new GitHub App installation

        Called when a user installs our GitHub App.
        """
        # Create auth record
        auth = ProviderAuth(
            org_id=org_id,
            provider=GitProvider.GITHUB,
            auth_type=AuthType.GITHUB_APP,
            installation_id=installation_id,
            app_id=self.github_app_id,
        )
        auth = await self.repository.save_auth(auth)

        # Create installation record
        installation = ProviderInstallation(
            org_id=org_id,
            provider=GitProvider.GITHUB,
            auth_id=auth.id,
            installation_id=installation_id,
            account_type=account_type,
            account_login=account_login,
            account_id=account_id,
            repository_selection=repository_selection,
            authorized_repos=repositories or [],
            permissions=permissions or {},
            events=events or [],
        )
        installation = await self.repository.save_installation(installation)

        logger.info(
            f"GitHub installation registered: org={org_id} "
            f"installation={installation_id} account={account_login}"
        )

        return installation

    async def update_installation_repos(
        self,
        org_id: UUID,
        installation_id: str,
        repositories_added: list[str],
        repositories_removed: list[str],
    ) -> ProviderInstallation:
        """
        Update installation's authorized repositories

        Called when repositories are added/removed from the installation.
        """
        installation = await self.repository.get_installation(org_id, installation_id)
        if not installation:
            raise ValueError(f"Installation not found: {installation_id}")

        # Update repo list
        current_repos = set(installation.authorized_repos)
        current_repos.update(repositories_added)
        current_repos.difference_update(repositories_removed)
        installation.authorized_repos = list(current_repos)
        installation.updated_at = datetime.utcnow()

        installation = await self.repository.update_installation(installation)

        logger.info(
            f"Installation repos updated: installation={installation_id} "
            f"added={len(repositories_added)} removed={len(repositories_removed)}"
        )

        return installation

    async def suspend_installation(
        self,
        org_id: UUID,
        installation_id: str,
        reason: str = "",
    ) -> ProviderInstallation:
        """
        Mark an installation as suspended

        Called when user suspends the app or it's suspended by GitHub.
        """
        installation = await self.repository.get_installation(org_id, installation_id)
        if not installation:
            raise ValueError(f"Installation not found: {installation_id}")

        installation.is_active = False
        installation.suspended_at = datetime.utcnow()
        installation.suspension_reason = reason
        installation.updated_at = datetime.utcnow()

        installation = await self.repository.update_installation(installation)

        logger.warning(
            f"Installation suspended: installation={installation_id} reason={reason}"
        )

        return installation

    async def delete_installation(
        self,
        org_id: UUID,
        installation_id: str,
    ) -> bool:
        """
        Handle installation deletion

        Called when user uninstalls the app.
        """
        installation = await self.repository.get_installation(org_id, installation_id)
        if not installation:
            return False

        # Soft delete - mark as inactive
        installation.is_active = False
        installation.suspended_at = datetime.utcnow()
        installation.suspension_reason = "uninstalled"
        await self.repository.update_installation(installation)

        logger.info(f"Installation deleted: installation={installation_id}")
        return True

    # ------------------------------------------------------------------
    # Token Management
    # ------------------------------------------------------------------

    async def get_installation_token(
        self,
        org_id: UUID,
        installation_id: str,
    ) -> str:
        """
        Get a valid installation access token

        Handles token refresh if expired.
        """
        auth = await self.repository.get_auth_by_installation(org_id, installation_id)
        if not auth:
            raise ValueError(f"No auth found for installation: {installation_id}")

        if not auth.is_active:
            raise ValueError(f"Installation is not active: {installation_id}")

        # Check if token needs refresh
        if auth.is_token_expired or not auth.access_token_encrypted:
            auth = await self._refresh_github_token(auth)

        # Decrypt and return
        return await self.secrets_manager.decrypt(auth.access_token_encrypted)

    async def _refresh_github_token(self, auth: ProviderAuth) -> ProviderAuth:
        """
        Refresh GitHub App installation token

        GitHub App tokens are short-lived (1 hour) and need regular refresh.
        """
        if not self.github_app_id or not self.github_app_private_key:
            raise ValueError("GitHub App credentials not configured")

        # Generate JWT for API authentication
        jwt = self._generate_github_jwt()

        # Request new installation token
        url = f"https://api.github.com/app/installations/{auth.installation_id}/access_tokens"

        try:
            response = await self.http_client.post(
                url,
                headers={
                    "Authorization": f"Bearer {jwt}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
        except Exception as e:
            logger.error(f"Failed to refresh GitHub token: {e}")
            raise

        # Store new token
        token = response.get("token")
        expires_at = response.get("expires_at")

        auth.access_token_encrypted = await self.secrets_manager.encrypt(token)
        auth.token_expires_at = datetime.fromisoformat(
            expires_at.replace("Z", "+00:00")
        ) if expires_at else datetime.utcnow() + timedelta(hours=1)
        auth.last_refreshed_at = datetime.utcnow()
        auth.updated_at = datetime.utcnow()

        auth = await self.repository.update_auth(auth)

        logger.debug(f"GitHub token refreshed for installation: {auth.installation_id}")

        return auth

    def _generate_github_jwt(self) -> str:
        """Generate a JWT for GitHub App API authentication"""
        import jwt as pyjwt

        now = int(time.time())

        payload = {
            "iat": now - 60,  # Issued 1 minute ago (clock skew)
            "exp": now + 600,  # Valid for 10 minutes
            "iss": self.github_app_id,
        }

        return pyjwt.encode(
            payload,
            self.github_app_private_key,
            algorithm="RS256",
        )

    # ------------------------------------------------------------------
    # Rate Limit Handling
    # ------------------------------------------------------------------

    async def check_rate_limit(
        self,
        org_id: UUID,
        installation_id: str,
    ) -> dict[str, Any]:
        """
        Check current rate limit status for an installation

        Returns rate limit info and whether we should proceed.
        """
        token = await self.get_installation_token(org_id, installation_id)

        response = await self.http_client.get(
            "https://api.github.com/rate_limit",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        core = response.get("resources", {}).get("core", {})
        limit = core.get("limit", 5000)
        remaining = core.get("remaining", 0)
        reset = core.get("reset", 0)

        result = {
            "limit": limit,
            "remaining": remaining,
            "reset_at": datetime.fromtimestamp(reset) if reset else None,
            "should_proceed": remaining > 100,  # Buffer of 100 requests
        }

        # Store for tracking
        self._rate_limits[installation_id] = result

        return result

    async def wait_for_rate_limit(
        self,
        org_id: UUID,
        installation_id: str,
        required_requests: int = 1,
    ) -> bool:
        """
        Wait for rate limit to reset if necessary

        Returns True if we can proceed, False if we should abort.
        """
        status = await self.check_rate_limit(org_id, installation_id)

        if status["remaining"] >= required_requests:
            return True

        reset_at = status.get("reset_at")
        if not reset_at:
            return False

        wait_seconds = (reset_at - datetime.utcnow()).total_seconds()

        if wait_seconds > 300:  # Don't wait more than 5 minutes
            logger.warning(
                f"Rate limit reset too far: {wait_seconds}s for {installation_id}"
            )
            return False

        if wait_seconds > 0:
            logger.info(
                f"Waiting {wait_seconds}s for rate limit reset: {installation_id}"
            )
            import asyncio
            await asyncio.sleep(wait_seconds)

        return True

    # ------------------------------------------------------------------
    # Provider API Helpers
    # ------------------------------------------------------------------

    async def get_repository_info(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
    ) -> dict[str, Any]:
        """Get repository information from GitHub"""
        token = await self.get_installation_token(org_id, installation_id)

        response = await self.http_client.get(
            f"https://api.github.com/repos/{repo_full_name}",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        return response

    async def list_installation_repos(
        self,
        org_id: UUID,
        installation_id: str,
        page: int = 1,
        per_page: int = 100,
    ) -> list[dict[str, Any]]:
        """List repositories accessible by the installation"""
        token = await self.get_installation_token(org_id, installation_id)

        response = await self.http_client.get(
            f"https://api.github.com/installation/repositories"
            f"?page={page}&per_page={per_page}",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        return response.get("repositories", [])
