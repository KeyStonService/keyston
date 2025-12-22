"""
Git Provider Integration Module

Provides stable integration with GitHub/GitLab including:
- Webhook Receiver with signature verification
- Anti-replay protection (timestamp/nonce)
- Rate limiting and backpressure
- Provider App/OAuth installation management
- Check Run / Status / Comment write-back
"""

from enterprise.integrations.providers import (
    GitProvider,
    GitProviderManager,
    ProviderAuth,
    ProviderInstallation,
)
from enterprise.integrations.webhook import (
    WebhookEvent,
    WebhookReceiver,
    WebhookValidationError,
)
from enterprise.integrations.writeback import (
    CheckRunConclusion,
    CheckRunStatus,
    CheckRunWriter,
    CommentWriter,
    StatusWriter,
)

__all__ = [
    # Webhook
    "WebhookReceiver",
    "WebhookEvent",
    "WebhookValidationError",
    # Providers
    "GitProviderManager",
    "GitProvider",
    "ProviderInstallation",
    "ProviderAuth",
    # Write-back
    "CheckRunWriter",
    "CheckRunStatus",
    "CheckRunConclusion",
    "StatusWriter",
    "CommentWriter",
]
