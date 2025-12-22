"""
SSO/OIDC Manager

Extension point for enterprise SSO integration.
MVP can use email/password + magic link, but this module provides
the backend interfaces for OIDC/SAML integration.
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol
from urllib.parse import urlencode, urlparse
from uuid import UUID

import jwt as pyjwt
from jwt import PyJWKClient

from enterprise.iam.models import (
    Membership,
    Role,
    SSOConfig,
    User,
)

logger = logging.getLogger(__name__)


class SSORepository(Protocol):
    """Repository interface for SSO configuration"""

    async def save_sso_config(self, config: SSOConfig) -> SSOConfig:
        ...

    async def get_sso_config(self, org_id: UUID) -> SSOConfig | None:
        ...

    async def update_sso_config(self, config: SSOConfig) -> SSOConfig:
        ...

    async def delete_sso_config(self, org_id: UUID) -> bool:
        ...


class UserRepository(Protocol):
    """Repository interface for user operations"""

    async def get_user_by_email(self, email: str) -> User | None:
        ...

    async def get_user_by_sso(
        self, sso_provider: str, sso_subject: str
    ) -> User | None:
        ...

    async def save_user(self, user: User) -> User:
        ...

    async def update_user(self, user: User) -> User:
        ...


class MembershipRepository(Protocol):
    """Repository interface for membership operations"""

    async def get_membership(
        self, org_id: UUID, user_id: UUID
    ) -> Membership | None:
        ...

    async def save_membership(self, membership: Membership) -> Membership:
        ...


class HTTPClient(Protocol):
    """HTTP client interface for OIDC operations"""

    async def get(self, url: str, headers: dict[str, str] = None) -> dict[str, Any]:
        ...

    async def post(
        self,
        url: str,
        data: dict[str, Any] = None,
        headers: dict[str, str] = None
    ) -> dict[str, Any]:
        ...


@dataclass
class OIDCAuthorizationRequest:
    """OIDC Authorization Request data"""
    authorization_url: str
    state: str
    nonce: str
    code_verifier: str  # For PKCE


@dataclass
class OIDCTokens:
    """OIDC Token response"""
    access_token: str
    id_token: str
    refresh_token: str | None = None
    expires_in: int = 3600
    token_type: str = "Bearer"


@dataclass
class OIDCUserInfo:
    """User information from OIDC provider"""
    subject: str  # 'sub' claim
    email: str
    email_verified: bool = False
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None
    raw_claims: dict[str, Any] = None

    def __post_init__(self):
        if self.raw_claims is None:
            self.raw_claims = {}


@dataclass
class SSOManager:
    """
    SSO/OIDC Manager

    Provides enterprise SSO integration with:
    - OIDC support (OpenID Connect)
    - SAML support (planned)
    - JIT (Just-In-Time) provisioning
    - Attribute mapping
    """

    sso_repository: SSORepository
    user_repository: UserRepository
    membership_repository: MembershipRepository
    http_client: HTTPClient

    # State management (in production, use Redis/DB)
    _pending_auth: dict[str, dict[str, Any]] = None

    def __post_init__(self):
        if self._pending_auth is None:
            self._pending_auth = {}

    # ------------------------------------------------------------------
    # SSO Configuration
    # ------------------------------------------------------------------

    async def configure_oidc(
        self,
        org_id: UUID,
        issuer_url: str,
        client_id: str,
        client_secret: str,
        configured_by: UUID,
        attribute_mapping: dict[str, str] | None = None,
        jit_enabled: bool = True,
        default_role: Role = Role.MEMBER,
    ) -> SSOConfig:
        """
        Configure OIDC SSO for an organization

        Args:
            org_id: Organization ID
            issuer_url: OIDC issuer URL (e.g., https://accounts.google.com)
            client_id: OAuth client ID
            client_secret: OAuth client secret
            configured_by: User configuring SSO
            attribute_mapping: Custom claim to attribute mapping
            jit_enabled: Enable Just-In-Time provisioning
            default_role: Default role for new SSO users

        Returns:
            Saved SSOConfig
        """
        # Validate issuer URL
        parsed = urlparse(issuer_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid issuer URL: {issuer_url}")

        # Discover OIDC endpoints
        discovery_url = f"{issuer_url.rstrip('/')}/.well-known/openid-configuration"
        try:
            discovery_response = await self.http_client.get(discovery_url)
        except Exception as e:
            raise ValueError(f"Failed to discover OIDC configuration: {e}")

        if not discovery_response:
            raise ValueError("Failed to discover OIDC configuration: empty response")

        # Hash client secret for storage
        secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()

        # Default attribute mapping
        if attribute_mapping is None:
            attribute_mapping = {
                "email": "email",
                "name": "display_name",
                "picture": "avatar_url",
            }

        config = SSOConfig(
            org_id=org_id,
            provider_type="oidc",
            issuer_url=issuer_url,
            client_id=client_id,
            client_secret_hash=secret_hash,
            attribute_mapping=attribute_mapping,
            default_role=default_role,
            jit_enabled=jit_enabled,
        )

        config = await self.sso_repository.save_sso_config(config)

        logger.info(f"OIDC configured for org={org_id} issuer={issuer_url}")

        return config

    async def get_sso_config(self, org_id: UUID) -> SSOConfig | None:
        """Get SSO configuration for an organization"""
        return await self.sso_repository.get_sso_config(org_id)

    async def disable_sso(self, org_id: UUID, disabled_by: UUID) -> bool:
        """Disable SSO for an organization"""
        config = await self.sso_repository.get_sso_config(org_id)
        if not config:
            return False

        config.is_active = False
        config.updated_at = datetime.utcnow()
        await self.sso_repository.update_sso_config(config)

        logger.info(f"SSO disabled for org={org_id} by={disabled_by}")
        return True

    # ------------------------------------------------------------------
    # OIDC Authentication Flow
    # ------------------------------------------------------------------

    async def initiate_oidc_login(
        self,
        org_id: UUID,
        redirect_uri: str,
    ) -> OIDCAuthorizationRequest:
        """
        Initiate OIDC login flow

        Returns the authorization URL to redirect the user to.

        Args:
            org_id: Organization ID
            redirect_uri: URI to redirect back to after auth

        Returns:
            OIDCAuthorizationRequest with URL and state/nonce
        """
        config = await self.sso_repository.get_sso_config(org_id)
        if not config or not config.is_active:
            raise ValueError("SSO is not configured for this organization")

        # Discover endpoints
        discovery_url = f"{config.issuer_url.rstrip('/')}/.well-known/openid-configuration"
        discovery = await self.http_client.get(discovery_url)

        authorization_endpoint = discovery.get("authorization_endpoint")
        if not authorization_endpoint:
            raise ValueError("Authorization endpoint not found in OIDC discovery")

        # Generate state, nonce, and PKCE code verifier
        state = secrets.token_urlsafe(32)
        nonce = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(64)

        # Generate code challenge (PKCE)
        code_challenge = hashlib.sha256(code_verifier.encode()).digest()
        import base64
        code_challenge_b64 = base64.urlsafe_b64encode(code_challenge).decode().rstrip('=')

        # Store pending auth for validation
        self._pending_auth[state] = {
            "org_id": str(org_id),
            "nonce": nonce,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Build authorization URL
        params = {
            "client_id": config.client_id,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": redirect_uri,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge_b64,
            "code_challenge_method": "S256",
        }

        authorization_url = f"{authorization_endpoint}?{urlencode(params)}"

        return OIDCAuthorizationRequest(
            authorization_url=authorization_url,
            state=state,
            nonce=nonce,
            code_verifier=code_verifier,
        )

    async def complete_oidc_login(
        self,
        state: str,
        code: str,
        client_secret: str,
    ) -> tuple[User, Membership]:
        """
        Complete OIDC login flow after callback

        Args:
            state: State parameter from callback
            code: Authorization code from callback
            client_secret: OAuth client secret (from secure storage)

        Returns:
            Tuple of (User, Membership) - created or updated
        """
        # Validate state
        pending = self._pending_auth.get(state)
        if not pending:
            raise ValueError("Invalid or expired state parameter")

        org_id = UUID(pending["org_id"])
        code_verifier = pending["code_verifier"]
        redirect_uri = pending["redirect_uri"]
        nonce = pending["nonce"]

        # Clean up pending auth
        del self._pending_auth[state]

        # Get SSO config
        config = await self.sso_repository.get_sso_config(org_id)
        if not config:
            raise ValueError("SSO configuration not found")

        # Discover token endpoint
        discovery_url = f"{config.issuer_url.rstrip('/')}/.well-known/openid-configuration"
        discovery = await self.http_client.get(discovery_url)
        token_endpoint = discovery.get("token_endpoint")

        # Exchange code for tokens
        token_response = await self.http_client.post(
            token_endpoint,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": config.client_id,
                "client_secret": client_secret,
                "code_verifier": code_verifier,
            },
        )

        tokens = OIDCTokens(
            access_token=token_response["access_token"],
            id_token=token_response["id_token"],
            refresh_token=token_response.get("refresh_token"),
            expires_in=token_response.get("expires_in", 3600),
        )

        # Validate ID token with proper JWT signature verification using JWKS
        try:
            # Get JWKS URI from discovery document
            jwks_uri = discovery.get("jwks_uri")
            if not jwks_uri:
                raise ValueError("JWKS URI not found in discovery document")
            
            # Create JWKS client to fetch and cache signing keys
            jwks_client = PyJWKClient(jwks_uri)
            
            # Get the signing key from the JWT header
            signing_key = jwks_client.get_signing_key_from_jwt(tokens.id_token)
            
            # Verify and decode the ID token with full signature verification
            id_token_claims = pyjwt.decode(
                tokens.id_token,
                key=signing_key.key,
                algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
                audience=config.client_id,
                issuer=discovery.get("issuer"),
            )
            
            # Validate nonce to prevent replay attacks
            token_nonce = id_token_claims.get("nonce")
            if token_nonce != nonce:
                raise ValueError("ID token nonce does not match expected nonce")
        except pyjwt.InvalidTokenError as e:
            raise ValueError(f"Invalid ID token: {e}")

        # Get user info
        userinfo_endpoint = discovery.get("userinfo_endpoint")
        userinfo_response = await self.http_client.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {tokens.access_token}"},
        )

        user_info = OIDCUserInfo(
            subject=userinfo_response["sub"],
            email=userinfo_response["email"],
            email_verified=userinfo_response.get("email_verified", False),
            name=userinfo_response.get("name"),
            given_name=userinfo_response.get("given_name"),
            family_name=userinfo_response.get("family_name"),
            picture=userinfo_response.get("picture"),
            raw_claims=userinfo_response,
        )

        # Find or create user (JIT provisioning)
        user, membership = await self._provision_sso_user(
            org_id=org_id,
            config=config,
            user_info=user_info,
        )

        logger.info(
            f"OIDC login completed: org={org_id} user={user.id} email={user.email}"
        )

        return user, membership

    # ------------------------------------------------------------------
    # JIT (Just-In-Time) Provisioning
    # ------------------------------------------------------------------

    async def _provision_sso_user(
        self,
        org_id: UUID,
        config: SSOConfig,
        user_info: OIDCUserInfo,
    ) -> tuple[User, Membership]:
        """
        Provision or update SSO user

        Implements JIT (Just-In-Time) provisioning.
        """
        # Check if user exists by SSO subject
        user = await self.user_repository.get_user_by_sso(
            sso_provider=config.issuer_url,
            sso_subject=user_info.subject,
        )

        if not user:
            # Check if user exists by email
            user = await self.user_repository.get_user_by_email(user_info.email)

        if user:
            # Update existing user
            user.sso_provider = config.issuer_url
            user.sso_subject = user_info.subject
            user.email_verified = user_info.email_verified
            user.last_login_at = datetime.utcnow()

            # Update mapped attributes
            self._apply_attribute_mapping(user, user_info, config.attribute_mapping)

            user = await self.user_repository.update_user(user)
        else:
            # JIT provisioning - create new user
            if not config.jit_enabled:
                raise ValueError(
                    "User not found and JIT provisioning is disabled"
                )

            # Check allowed domains
            if config.jit_allowed_domains:
                email_domain = user_info.email.split("@")[-1]
                if email_domain not in config.jit_allowed_domains:
                    raise ValueError(
                        f"Email domain '{email_domain}' is not allowed for JIT provisioning"
                    )

            user = User(
                email=user_info.email,
                username=user_info.email.split("@")[0],
                display_name=user_info.name or user_info.email,
                avatar_url=user_info.picture,
                email_verified=user_info.email_verified,
                sso_provider=config.issuer_url,
                sso_subject=user_info.subject,
                last_login_at=datetime.utcnow(),
            )

            user = await self.user_repository.save_user(user)
            logger.info(f"JIT provisioned user: {user.email}")

        # Ensure membership exists
        membership = await self.membership_repository.get_membership(org_id, user.id)

        if not membership:
            membership = Membership(
                org_id=org_id,
                user_id=user.id,
                role=config.default_role,
                accepted_at=datetime.utcnow(),
            )
            membership = await self.membership_repository.save_membership(membership)
            logger.info(
                f"Created SSO membership: user={user.id} org={org_id} role={config.default_role.value}"
            )

        return user, membership

    def _apply_attribute_mapping(
        self,
        user: User,
        user_info: OIDCUserInfo,
        mapping: dict[str, str],
    ) -> None:
        """Apply attribute mapping from OIDC claims to user fields"""
        claim_values = {
            "email": user_info.email,
            "name": user_info.name,
            "given_name": user_info.given_name,
            "family_name": user_info.family_name,
            "picture": user_info.picture,
            **user_info.raw_claims,
        }

        for claim_name, user_field in mapping.items():
            if claim_name in claim_values and hasattr(user, user_field):
                value = claim_values[claim_name]
                if value is not None:
                    setattr(user, user_field, value)

    # ------------------------------------------------------------------
    # Magic Link Authentication (MVP fallback)
    # ------------------------------------------------------------------

    async def send_magic_link(
        self,
        email: str,
        org_id: UUID | None = None,
    ) -> str:
        """
        Send a magic link for passwordless authentication

        This is the MVP authentication method before full SSO.

        Args:
            email: User's email address
            org_id: Optional org context

        Returns:
            Magic link token (for testing; in production, email it)
        """
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Store for validation (in production, use Redis with TTL)
        self._pending_auth[f"magic_{token_hash}"] = {
            "email": email,
            "org_id": str(org_id) if org_id else None,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=15)).isoformat(),
        }

        logger.info(f"Magic link generated for {email}")

        # In production, send email here
        return token

    async def verify_magic_link(
        self,
        token: str,
    ) -> User | None:
        """
        Verify a magic link token

        Args:
            token: Magic link token from email

        Returns:
            User if valid, None if invalid/expired
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        pending = self._pending_auth.get(f"magic_{token_hash}")

        if not pending:
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(pending["expires_at"])
        if datetime.utcnow() > expires_at:
            del self._pending_auth[f"magic_{token_hash}"]
            return None

        email = pending["email"]

        # Clean up
        del self._pending_auth[f"magic_{token_hash}"]

        # Find or create user
        user = await self.user_repository.get_user_by_email(email)

        if not user:
            user = User(
                email=email,
                username=email.split("@")[0],
                display_name=email.split("@")[0],
                email_verified=True,
                last_login_at=datetime.utcnow(),
            )
            user = await self.user_repository.save_user(user)
        else:
            user.last_login_at = datetime.utcnow()
            user.email_verified = True
            user = await self.user_repository.update_user(user)

        return user
