"""
Webhook Receiver

Handles incoming webhooks from Git providers with:
- Signature verification (HMAC or App public key)
- Anti-replay protection (timestamp/nonce)
- Rate limiting and backpressure
"""

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class WebhookEventType(Enum):
    """Standard webhook event types across providers"""
    # Pull Request events
    PULL_REQUEST_OPENED = "pull_request.opened"
    PULL_REQUEST_SYNCHRONIZE = "pull_request.synchronize"
    PULL_REQUEST_CLOSED = "pull_request.closed"
    PULL_REQUEST_REOPENED = "pull_request.reopened"
    PULL_REQUEST_MERGED = "pull_request.merged"

    # Push events
    PUSH = "push"

    # Check events
    CHECK_SUITE_REQUESTED = "check_suite.requested"
    CHECK_RUN_REQUESTED = "check_run.requested"
    CHECK_RUN_REREQUESTED = "check_run.rerequested"

    # Review events
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"

    # Issue events
    ISSUE_COMMENT = "issue_comment"

    # Installation events
    INSTALLATION_CREATED = "installation.created"
    INSTALLATION_DELETED = "installation.deleted"

    # Unknown
    UNKNOWN = "unknown"


class WebhookValidationError(Exception):
    """Raised when webhook validation fails"""
    pass


@dataclass
class WebhookEvent:
    """
    Standardized webhook event

    Normalized representation across different Git providers.
    """
    id: UUID = field(default_factory=uuid4)

    # Event metadata
    event_type: WebhookEventType = WebhookEventType.UNKNOWN
    provider: str = "github"  # github, gitlab, bitbucket
    delivery_id: str = ""  # Provider's delivery ID
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Tenant isolation
    org_id: UUID | None = None
    repo_id: UUID | None = None
    installation_id: str | None = None

    # Repository info
    repo_full_name: str = ""
    repo_provider_id: str = ""

    # Event-specific data
    action: str = ""  # opened, synchronize, closed, etc.

    # Pull Request / Push specific
    head_sha: str | None = None
    base_sha: str | None = None
    head_ref: str | None = None  # Branch name
    base_ref: str | None = None
    pr_number: int | None = None
    pr_title: str | None = None
    pr_url: str | None = None

    # Sender
    sender_login: str | None = None
    sender_id: str | None = None

    # Raw payload (for debugging/audit)
    raw_payload: dict[str, Any] = field(default_factory=dict)

    # Validation
    is_verified: bool = False
    verification_method: str | None = None  # hmac, app_signature


class NonceStore(Protocol):
    """Interface for nonce storage (anti-replay)"""

    async def check_and_store(self, nonce: str, ttl_seconds: int = 300) -> bool:
        """
        Check if nonce exists, if not store it.

        Returns True if nonce is new (valid), False if replay (duplicate).
        """
        ...

    async def cleanup_expired(self) -> int:
        """Clean up expired nonces, return count removed"""
        ...


class RateLimiter(Protocol):
    """Interface for rate limiting"""

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check rate limit for a key.

        Returns (allowed, remaining_count).
        """
        ...


class EventPublisher(Protocol):
    """Interface for publishing validated events"""

    async def publish(self, event: WebhookEvent) -> None:
        """Publish event to the event log/queue"""
        ...


@dataclass
class WebhookReceiver:
    """
    Webhook Receiver

    Handles incoming webhooks with:
    - Signature verification
    - Anti-replay protection
    - Rate limiting
    - Event normalization
    """

    nonce_store: NonceStore | None = None
    rate_limiter: RateLimiter | None = None
    event_publisher: EventPublisher | None = None

    # Configuration
    replay_window_seconds: int = 300  # 5 minutes
    rate_limit_per_minute: int = 1000
    max_payload_size: int = 10 * 1024 * 1024  # 10 MB

    # In-memory nonce cache (for MVP, use Redis in production)
    _nonces: set[str] = field(default_factory=set)
    _nonce_timestamps: dict[str, float] = field(default_factory=dict)

    # Secrets (should come from secrets manager)
    webhook_secrets: dict[str, str] = field(default_factory=dict)  # repo_id -> secret

    # ------------------------------------------------------------------
    # Webhook Reception
    # ------------------------------------------------------------------

    async def receive(
        self,
        provider: str,
        headers: dict[str, str],
        body: bytes,
        secret: str | None = None,
    ) -> WebhookEvent:
        """
        Receive and validate a webhook

        Args:
            provider: Git provider (github, gitlab, bitbucket)
            headers: HTTP headers
            body: Raw request body
            secret: Webhook secret for verification

        Returns:
            Validated and normalized WebhookEvent

        Raises:
            WebhookValidationError: If validation fails
        """
        # Size check
        if len(body) > self.max_payload_size:
            raise WebhookValidationError(
                f"Payload too large: {len(body)} bytes"
            )

        # Verify signature
        if provider == "github":
            await self._verify_github_signature(headers, body, secret)
        elif provider == "gitlab":
            await self._verify_gitlab_signature(headers, body, secret)
        elif provider == "bitbucket":
            await self._verify_bitbucket_signature(headers, body, secret)
        else:
            raise WebhookValidationError(f"Unknown provider: {provider}")

        # Anti-replay check
        delivery_id = self._get_delivery_id(provider, headers)
        if delivery_id:
            if not await self._check_nonce(delivery_id):
                raise WebhookValidationError(
                    f"Replay detected: delivery_id={delivery_id}"
                )

        # Rate limit check
        rate_key = self._get_rate_limit_key(provider, headers, body)
        if self.rate_limiter:
            allowed, remaining = await self.rate_limiter.check_rate_limit(
                rate_key,
                self.rate_limit_per_minute,
                60,
            )
            if not allowed:
                raise WebhookValidationError(
                    f"Rate limit exceeded for {rate_key}"
                )

        # Parse and normalize
        event = await self._parse_event(provider, headers, body)
        event.is_verified = True
        event.delivery_id = delivery_id or ""

        # Publish to event log
        if self.event_publisher:
            await self.event_publisher.publish(event)

        logger.info(
            f"Webhook received: provider={provider} "
            f"type={event.event_type.value} "
            f"repo={event.repo_full_name} "
            f"delivery_id={delivery_id}"
        )

        return event

    # ------------------------------------------------------------------
    # Signature Verification
    # ------------------------------------------------------------------

    async def _verify_github_signature(
        self,
        headers: dict[str, str],
        body: bytes,
        secret: str | None,
    ) -> None:
        """
        Verify GitHub webhook signature

        GitHub uses HMAC-SHA256 with the format:
        X-Hub-Signature-256: sha256=<signature>
        """
        signature_header = headers.get("X-Hub-Signature-256") or headers.get("x-hub-signature-256")

        if not signature_header:
            # Also check old SHA1 signature
            signature_header = headers.get("X-Hub-Signature") or headers.get("x-hub-signature")
            if signature_header:
                await self._verify_hmac(body, secret, signature_header, "sha1")
                return

            raise WebhookValidationError("Missing signature header")

        await self._verify_hmac(body, secret, signature_header, "sha256")

    async def _verify_gitlab_signature(
        self,
        headers: dict[str, str],
        body: bytes,
        secret: str | None,
    ) -> None:
        """
        Verify GitLab webhook signature

        GitLab uses X-Gitlab-Token header with the raw secret.
        """
        token_header = headers.get("X-Gitlab-Token") or headers.get("x-gitlab-token")

        if not token_header:
            raise WebhookValidationError("Missing GitLab token header")

        if not secret:
            raise WebhookValidationError("No webhook secret configured")

        if not hmac.compare_digest(token_header, secret):
            raise WebhookValidationError("Invalid GitLab token")

    async def _verify_bitbucket_signature(
        self,
        headers: dict[str, str],
        body: bytes,
        secret: str | None,
    ) -> None:
        """
        Verify Bitbucket webhook signature

        Bitbucket uses HMAC-SHA256 with X-Hub-Signature header.
        """
        signature_header = headers.get("X-Hub-Signature") or headers.get("x-hub-signature")

        if not signature_header:
            raise WebhookValidationError("Missing Bitbucket signature header")

        await self._verify_hmac(body, secret, signature_header, "sha256")

    async def _verify_hmac(
        self,
        body: bytes,
        secret: str | None,
        signature_header: str,
        algorithm: str,
    ) -> None:
        """Verify HMAC signature"""
        if not secret:
            raise WebhookValidationError("No webhook secret configured")

        # Parse signature header
        if "=" in signature_header:
            algo, signature = signature_header.split("=", 1)
        else:
            signature = signature_header

        # Compute expected signature
        if algorithm == "sha256":
            expected = hmac.new(
                secret.encode(),
                body,
                hashlib.sha256,
            ).hexdigest()
        elif algorithm == "sha1":
            expected = hmac.new(
                secret.encode(),
                body,
                hashlib.sha1,
            ).hexdigest()
        else:
            raise WebhookValidationError(f"Unsupported algorithm: {algorithm}")

        # Constant-time comparison
        if not hmac.compare_digest(expected, signature):
            raise WebhookValidationError("Invalid webhook signature")

    # ------------------------------------------------------------------
    # Anti-Replay Protection
    # ------------------------------------------------------------------

    async def _check_nonce(self, nonce: str) -> bool:
        """
        Check if nonce is new (anti-replay)

        Returns True if nonce is new, False if it's a replay.
        """
        if self.nonce_store:
            return await self.nonce_store.check_and_store(
                nonce,
                self.replay_window_seconds,
            )

        # In-memory fallback (for MVP)
        now = time.time()

        # Clean old nonces
        expired = [
            n for n, ts in self._nonce_timestamps.items()
            if now - ts > self.replay_window_seconds
        ]
        for n in expired:
            self._nonces.discard(n)
            del self._nonce_timestamps[n]

        # Check and store
        if nonce in self._nonces:
            return False

        self._nonces.add(nonce)
        self._nonce_timestamps[nonce] = now
        return True

    def _get_delivery_id(self, provider: str, headers: dict[str, str]) -> str | None:
        """Get delivery ID from headers based on provider"""
        if provider == "github":
            return headers.get("X-GitHub-Delivery") or headers.get("x-github-delivery")
        elif provider == "gitlab":
            return headers.get("X-Gitlab-Event-UUID") or headers.get("x-gitlab-event-uuid")
        elif provider == "bitbucket":
            return headers.get("X-Request-UUID") or headers.get("x-request-uuid")
        return None

    def _get_rate_limit_key(
        self,
        provider: str,
        headers: dict[str, str],
        body: bytes,
    ) -> str:
        """Generate rate limit key"""
        # Use installation ID or IP as rate limit key
        if provider == "github":
            # Try to extract installation from headers or body
            return f"github:{headers.get('X-GitHub-Hook-Installation-Target-ID', 'unknown')}"
        return f"{provider}:global"

    # ------------------------------------------------------------------
    # Event Parsing
    # ------------------------------------------------------------------

    async def _parse_event(
        self,
        provider: str,
        headers: dict[str, str],
        body: bytes,
    ) -> WebhookEvent:
        """Parse and normalize webhook payload"""
        import json

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            raise WebhookValidationError(f"Invalid JSON payload: {e}")

        if provider == "github":
            return self._parse_github_event(headers, payload)
        elif provider == "gitlab":
            return self._parse_gitlab_event(headers, payload)
        elif provider == "bitbucket":
            return self._parse_bitbucket_event(headers, payload)

        return WebhookEvent(
            provider=provider,
            raw_payload=payload,
        )

    def _parse_github_event(
        self,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> WebhookEvent:
        """Parse GitHub webhook payload"""
        event_name = headers.get("X-GitHub-Event") or headers.get("x-github-event", "")
        action = payload.get("action", "")

        # Map to standard event type
        event_type = self._map_github_event_type(event_name, action)

        # Extract repository info
        repo = payload.get("repository", {})
        sender = payload.get("sender", {})
        installation = payload.get("installation", {})

        event = WebhookEvent(
            event_type=event_type,
            provider="github",
            action=action,
            repo_full_name=repo.get("full_name", ""),
            repo_provider_id=str(repo.get("id", "")),
            installation_id=str(installation.get("id", "")) if installation else None,
            sender_login=sender.get("login"),
            sender_id=str(sender.get("id", "")),
            raw_payload=payload,
        )

        # Pull request specific
        pr = payload.get("pull_request", {})
        if pr:
            head = pr.get("head", {})
            base = pr.get("base", {})

            event.pr_number = pr.get("number")
            event.pr_title = pr.get("title")
            event.pr_url = pr.get("html_url")
            event.head_sha = head.get("sha")
            event.base_sha = base.get("sha")
            event.head_ref = head.get("ref")
            event.base_ref = base.get("ref")

        # Push specific
        if event_name == "push":
            event.head_sha = payload.get("after")
            event.base_sha = payload.get("before")
            event.head_ref = payload.get("ref", "").replace("refs/heads/", "")

        # Check suite/run
        check_suite = payload.get("check_suite", {})
        check_run = payload.get("check_run", {})
        if check_suite:
            event.head_sha = check_suite.get("head_sha")
        if check_run:
            event.head_sha = check_run.get("head_sha")

        return event

    def _map_github_event_type(self, event_name: str, action: str) -> WebhookEventType:
        """Map GitHub event to standard event type"""
        mapping = {
            ("pull_request", "opened"): WebhookEventType.PULL_REQUEST_OPENED,
            ("pull_request", "synchronize"): WebhookEventType.PULL_REQUEST_SYNCHRONIZE,
            ("pull_request", "closed"): WebhookEventType.PULL_REQUEST_CLOSED,
            ("pull_request", "reopened"): WebhookEventType.PULL_REQUEST_REOPENED,
            ("push", ""): WebhookEventType.PUSH,
            ("check_suite", "requested"): WebhookEventType.CHECK_SUITE_REQUESTED,
            ("check_run", "requested_action"): WebhookEventType.CHECK_RUN_REQUESTED,
            ("check_run", "rerequested"): WebhookEventType.CHECK_RUN_REREQUESTED,
            ("installation", "created"): WebhookEventType.INSTALLATION_CREATED,
            ("installation", "deleted"): WebhookEventType.INSTALLATION_DELETED,
        }

        return mapping.get((event_name, action), WebhookEventType.UNKNOWN)

    def _parse_gitlab_event(
        self,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> WebhookEvent:
        """Parse GitLab webhook payload"""
        object_kind = payload.get("object_kind", "")

        event = WebhookEvent(
            provider="gitlab",
            raw_payload=payload,
        )

        project = payload.get("project", {})
        event.repo_full_name = project.get("path_with_namespace", "")
        event.repo_provider_id = str(project.get("id", ""))

        user = payload.get("user", {})
        event.sender_login = user.get("username")
        event.sender_id = str(user.get("id", ""))

        # Merge request
        if object_kind == "merge_request":
            mr = payload.get("object_attributes", {})
            action = mr.get("action", "")

            if action == "open":
                event.event_type = WebhookEventType.PULL_REQUEST_OPENED
            elif action == "update":
                event.event_type = WebhookEventType.PULL_REQUEST_SYNCHRONIZE
            elif action == "close":
                event.event_type = WebhookEventType.PULL_REQUEST_CLOSED
            elif action == "merge":
                event.event_type = WebhookEventType.PULL_REQUEST_MERGED

            event.action = action
            event.pr_number = mr.get("iid")
            event.pr_title = mr.get("title")
            event.pr_url = mr.get("url")
            event.head_sha = mr.get("last_commit", {}).get("id")
            event.head_ref = mr.get("source_branch")
            event.base_ref = mr.get("target_branch")

        # Push
        elif object_kind == "push":
            event.event_type = WebhookEventType.PUSH
            event.head_sha = payload.get("after")
            event.base_sha = payload.get("before")
            event.head_ref = payload.get("ref", "").replace("refs/heads/", "")

        return event

    def _parse_bitbucket_event(
        self,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> WebhookEvent:
        """Parse Bitbucket webhook payload"""
        event_key = headers.get("X-Event-Key") or headers.get("x-event-key", "")

        event = WebhookEvent(
            provider="bitbucket",
            raw_payload=payload,
        )

        repo = payload.get("repository", {})
        event.repo_full_name = repo.get("full_name", "")
        event.repo_provider_id = repo.get("uuid", "")

        actor = payload.get("actor", {})
        event.sender_login = actor.get("username") or actor.get("nickname")
        event.sender_id = actor.get("uuid", "")

        # Pull request events
        if event_key.startswith("pullrequest:"):
            pr = payload.get("pullrequest", {})
            action = event_key.split(":")[-1]

            if action == "created":
                event.event_type = WebhookEventType.PULL_REQUEST_OPENED
            elif action == "updated":
                event.event_type = WebhookEventType.PULL_REQUEST_SYNCHRONIZE
            elif action in ("fulfilled", "rejected"):
                event.event_type = WebhookEventType.PULL_REQUEST_CLOSED

            event.action = action
            event.pr_number = pr.get("id")
            event.pr_title = pr.get("title")

            source = pr.get("source", {})
            destination = pr.get("destination", {})
            event.head_sha = source.get("commit", {}).get("hash")
            event.head_ref = source.get("branch", {}).get("name")
            event.base_ref = destination.get("branch", {}).get("name")

        # Push
        elif event_key == "repo:push":
            event.event_type = WebhookEventType.PUSH
            push = payload.get("push", {})
            changes = push.get("changes", [{}])[0]
            new = changes.get("new", {})
            old = changes.get("old", {})
            event.head_sha = new.get("target", {}).get("hash")
            event.base_sha = old.get("target", {}).get("hash") if old else None
            event.head_ref = new.get("name")

        return event
