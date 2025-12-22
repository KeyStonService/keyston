"""
Audit Logger

Records "who changed what when" for enterprise compliance:
- All configuration changes
- All access to sensitive data
- All authentication events
- All API calls

This is a HARD requirement for enterprise customers.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """Audit action categories"""
    # Authentication
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_LOGIN_FAILED = "auth.login_failed"
    AUTH_TOKEN_CREATED = "auth.token_created"
    AUTH_TOKEN_REVOKED = "auth.token_revoked"
    AUTH_SSO_LOGIN = "auth.sso_login"
    AUTH_MFA_ENABLED = "auth.mfa_enabled"
    AUTH_MFA_DISABLED = "auth.mfa_disabled"

    # Organization
    ORG_CREATED = "org.created"
    ORG_UPDATED = "org.updated"
    ORG_DELETED = "org.deleted"
    ORG_SUSPENDED = "org.suspended"
    ORG_REACTIVATED = "org.reactivated"

    # Membership
    MEMBER_ADDED = "member.added"
    MEMBER_REMOVED = "member.removed"
    MEMBER_ROLE_CHANGED = "member.role_changed"
    MEMBER_INVITED = "member.invited"

    # Project
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"

    # Repository
    REPO_ADDED = "repo.added"
    REPO_REMOVED = "repo.removed"
    REPO_SETTINGS_CHANGED = "repo.settings_changed"

    # Policy
    POLICY_CREATED = "policy.created"
    POLICY_UPDATED = "policy.updated"
    POLICY_DELETED = "policy.deleted"
    POLICY_ENABLED = "policy.enabled"
    POLICY_DISABLED = "policy.disabled"

    # Integration
    INTEGRATION_INSTALLED = "integration.installed"
    INTEGRATION_UNINSTALLED = "integration.uninstalled"
    INTEGRATION_UPDATED = "integration.updated"
    WEBHOOK_CREATED = "webhook.created"
    WEBHOOK_DELETED = "webhook.deleted"

    # Secrets
    SECRET_CREATED = "secret.created"
    SECRET_ACCESSED = "secret.accessed"
    SECRET_ROTATED = "secret.rotated"
    SECRET_DELETED = "secret.deleted"

    # API
    API_KEY_CREATED = "api.key_created"
    API_KEY_REVOKED = "api.key_revoked"
    API_CALL = "api.call"
    API_RATE_LIMITED = "api.rate_limited"

    # Runs
    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    RUN_CANCELED = "run.canceled"

    # Data Access
    DATA_EXPORTED = "data.exported"
    REPORT_GENERATED = "report.generated"
    REPORT_DOWNLOADED = "report.downloaded"

    # Settings
    SETTINGS_CHANGED = "settings.changed"
    SSO_CONFIGURED = "sso.configured"
    SSO_DISABLED = "sso.disabled"

    # Custom
    CUSTOM = "custom"


class AuditSeverity(Enum):
    """Audit entry severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """
    Audit log entry

    Immutable record of an auditable event.
    """
    id: UUID = field(default_factory=uuid4)

    # What happened
    action: AuditAction = AuditAction.CUSTOM
    severity: AuditSeverity = AuditSeverity.INFO

    # Who did it
    actor_id: UUID | None = None
    actor_type: str = "user"  # user, service, system
    actor_email: str | None = None
    actor_ip: str | None = None
    actor_user_agent: str | None = None

    # Where
    org_id: UUID | None = None
    project_id: UUID | None = None
    repo_id: UUID | None = None

    # What was affected
    resource_type: str = ""   # e.g., "policy", "member", "secret"
    resource_id: str = ""     # ID of the resource
    resource_name: str | None = None  # Human-readable name

    # Details
    description: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    # Change tracking (for updates)
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None

    # Request context
    request_id: str | None = None
    session_id: str | None = None
    correlation_id: UUID | None = None

    # Timing
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Metadata
    version: str = "1.0"
    source: str = "api"  # api, webhook, scheduled, manual

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        return {
            "id": str(self.id),
            "action": self.action.value,
            "severity": self.severity.value,
            "actor_id": str(self.actor_id) if self.actor_id else None,
            "actor_type": self.actor_type,
            "actor_email": self.actor_email,
            "actor_ip": self.actor_ip,
            "actor_user_agent": self.actor_user_agent,
            "org_id": str(self.org_id) if self.org_id else None,
            "project_id": str(self.project_id) if self.project_id else None,
            "repo_id": str(self.repo_id) if self.repo_id else None,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "description": self.description,
            "details": self.details,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "source": self.source,
        }


@dataclass
class AuditQuery:
    """Query parameters for audit log search"""
    org_id: UUID | None = None
    actor_id: UUID | None = None
    actions: list[AuditAction] | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    severity: AuditSeverity | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    search_text: str | None = None


class AuditStorage(Protocol):
    """Storage interface for audit logs"""

    async def store(self, entry: AuditEntry) -> AuditEntry:
        """Store an audit entry (append-only)"""
        ...

    async def query(
        self,
        query: AuditQuery,
        offset: int = 0,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit entries"""
        ...

    async def count(self, query: AuditQuery) -> int:
        """Count matching entries"""
        ...

    async def get_by_id(self, entry_id: UUID) -> AuditEntry | None:
        """Get a specific entry"""
        ...


class AuditExporter(Protocol):
    """Interface for exporting audit logs"""

    async def export(
        self,
        query: AuditQuery,
        format: str = "json",
    ) -> bytes:
        """Export audit logs in specified format"""
        ...


@dataclass
class AuditLogger:
    """
    Audit Logger

    Provides structured audit logging with:
    - Immutable records
    - Structured data
    - Query capability
    - Export for compliance
    """

    storage: AuditStorage
    exporter: AuditExporter | None = None

    # Configuration
    enabled: bool = True
    include_details: bool = True
    mask_sensitive_fields: bool = True

    # Sensitive field patterns to mask
    sensitive_fields: list[str] = field(default_factory=lambda: [
        "password", "secret", "token", "api_key", "private_key",
        "access_token", "refresh_token", "credential",
    ])

    # Retention
    retention_days: int = 365

    # ------------------------------------------------------------------
    # Logging Methods
    # ------------------------------------------------------------------

    async def log(
        self,
        action: AuditAction,
        actor_id: UUID | None = None,
        org_id: UUID | None = None,
        resource_type: str = "",
        resource_id: str = "",
        description: str = "",
        details: dict[str, Any] | None = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        actor_email: str | None = None,
        actor_ip: str | None = None,
        request_id: str | None = None,
        correlation_id: UUID | None = None,
    ) -> AuditEntry:
        """
        Log an audit event

        Args:
            action: What action was performed
            actor_id: Who performed the action
            org_id: Organization context
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            description: Human-readable description
            details: Additional details
            severity: Event severity
            old_value: Previous value (for updates)
            new_value: New value (for updates)
            actor_email: Actor's email
            actor_ip: Actor's IP address
            request_id: Request ID for correlation
            correlation_id: Correlation ID for tracing

        Returns:
            Created audit entry
        """
        if not self.enabled:
            return None

        # Mask sensitive fields
        safe_details = self._mask_sensitive(details) if details else {}
        safe_old = self._mask_sensitive(old_value) if old_value else None
        safe_new = self._mask_sensitive(new_value) if new_value else None

        entry = AuditEntry(
            action=action,
            severity=severity,
            actor_id=actor_id,
            actor_email=actor_email,
            actor_ip=actor_ip,
            org_id=org_id,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            details=safe_details if self.include_details else {},
            old_value=safe_old,
            new_value=safe_new,
            request_id=request_id,
            correlation_id=correlation_id,
        )

        entry = await self.storage.store(entry)

        # Also log to standard logger for debugging
        logger.info(
            f"AUDIT: action={action.value} actor={actor_id} "
            f"resource={resource_type}/{resource_id} org={org_id}"
        )

        return entry

    async def log_auth_success(
        self,
        user_id: UUID,
        email: str,
        ip_address: str,
        method: str = "password",
    ) -> AuditEntry:
        """Log successful authentication"""
        return await self.log(
            action=AuditAction.AUTH_LOGIN,
            actor_id=user_id,
            actor_email=email,
            actor_ip=ip_address,
            resource_type="user",
            resource_id=str(user_id),
            description=f"User logged in via {method}",
            details={"method": method},
        )

    async def log_auth_failure(
        self,
        email: str,
        ip_address: str,
        reason: str,
    ) -> AuditEntry:
        """Log failed authentication"""
        return await self.log(
            action=AuditAction.AUTH_LOGIN_FAILED,
            actor_email=email,
            actor_ip=ip_address,
            resource_type="auth",
            resource_id="login",
            description=f"Login failed: {reason}",
            severity=AuditSeverity.WARNING,
            details={"reason": reason},
        )

    async def log_setting_change(
        self,
        actor_id: UUID,
        org_id: UUID,
        setting_name: str,
        old_value: Any,
        new_value: Any,
    ) -> AuditEntry:
        """Log a setting change"""
        return await self.log(
            action=AuditAction.SETTINGS_CHANGED,
            actor_id=actor_id,
            org_id=org_id,
            resource_type="setting",
            resource_id=setting_name,
            description=f"Setting '{setting_name}' changed",
            old_value={"value": old_value},
            new_value={"value": new_value},
        )

    async def log_member_change(
        self,
        actor_id: UUID,
        org_id: UUID,
        member_id: UUID,
        action_type: str,  # added, removed, role_changed
        details: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Log a membership change"""
        action_map = {
            "added": AuditAction.MEMBER_ADDED,
            "removed": AuditAction.MEMBER_REMOVED,
            "role_changed": AuditAction.MEMBER_ROLE_CHANGED,
        }

        return await self.log(
            action=action_map.get(action_type, AuditAction.CUSTOM),
            actor_id=actor_id,
            org_id=org_id,
            resource_type="member",
            resource_id=str(member_id),
            description=f"Member {action_type}",
            details=details,
        )

    async def log_api_call(
        self,
        actor_id: UUID | None,
        org_id: UUID | None,
        method: str,
        path: str,
        status_code: int,
        ip_address: str,
        request_id: str,
    ) -> AuditEntry:
        """Log an API call"""
        severity = (
            AuditSeverity.INFO
            if status_code < 400
            else AuditSeverity.WARNING
        )

        return await self.log(
            action=AuditAction.API_CALL,
            actor_id=actor_id,
            org_id=org_id,
            actor_ip=ip_address,
            resource_type="api",
            resource_id=path,
            description=f"{method} {path} -> {status_code}",
            severity=severity,
            details={
                "method": method,
                "path": path,
                "status_code": status_code,
            },
            request_id=request_id,
        )

    # ------------------------------------------------------------------
    # Query Methods
    # ------------------------------------------------------------------

    async def query(
        self,
        query: AuditQuery,
        offset: int = 0,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Query audit logs"""
        return await self.storage.query(query, offset, limit)

    async def get_org_audit_log(
        self,
        org_id: UUID,
        days: int = 30,
        offset: int = 0,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Get audit log for an organization"""
        query = AuditQuery(
            org_id=org_id,
            start_time=datetime.utcnow() - timedelta(days=days),
        )
        return await self.storage.query(query, offset, limit)

    async def get_user_activity(
        self,
        user_id: UUID,
        days: int = 30,
    ) -> list[AuditEntry]:
        """Get activity for a specific user"""
        query = AuditQuery(
            actor_id=user_id,
            start_time=datetime.utcnow() - timedelta(days=days),
        )
        return await self.storage.query(query, limit=1000)

    async def get_security_events(
        self,
        org_id: UUID,
        days: int = 7,
    ) -> list[AuditEntry]:
        """Get security-relevant events"""
        security_actions = [
            AuditAction.AUTH_LOGIN_FAILED,
            AuditAction.AUTH_TOKEN_REVOKED,
            AuditAction.SECRET_ACCESSED,
            AuditAction.MEMBER_ROLE_CHANGED,
            AuditAction.SSO_CONFIGURED,
            AuditAction.API_RATE_LIMITED,
        ]

        query = AuditQuery(
            org_id=org_id,
            actions=security_actions,
            start_time=datetime.utcnow() - timedelta(days=days),
        )
        return await self.storage.query(query, limit=1000)

    # ------------------------------------------------------------------
    # Export Methods
    # ------------------------------------------------------------------

    async def export_audit_log(
        self,
        org_id: UUID,
        start_time: datetime,
        end_time: datetime,
        format: str = "json",
    ) -> bytes:
        """
        Export audit log for compliance

        Args:
            org_id: Organization to export
            start_time: Start of period
            end_time: End of period
            format: Export format (json, csv)

        Returns:
            Exported data as bytes
        """
        if not self.exporter:
            # Fallback to simple JSON export
            query = AuditQuery(
                org_id=org_id,
                start_time=start_time,
                end_time=end_time,
            )
            entries = await self.storage.query(query, limit=100000)

            data = [e.to_dict() for e in entries]
            return json.dumps(data, indent=2).encode("utf-8")

        query = AuditQuery(
            org_id=org_id,
            start_time=start_time,
            end_time=end_time,
        )
        return await self.exporter.export(query, format)

    # ------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------

    def _mask_sensitive(self, data: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive fields in data"""
        if not data or not self.mask_sensitive_fields:
            return data

        masked = {}
        for key, value in data.items():
            key_lower = key.lower()

            # Check if field is sensitive
            is_sensitive = any(
                pattern in key_lower
                for pattern in self.sensitive_fields
            )

            if is_sensitive:
                if isinstance(value, str):
                    # Show first/last 4 chars
                    if len(value) > 8:
                        masked[key] = f"{value[:4]}...{value[-4:]}"
                    else:
                        masked[key] = "***MASKED***"
                else:
                    masked[key] = "***MASKED***"
            elif isinstance(value, dict):
                # Recursively mask nested dicts
                masked[key] = self._mask_sensitive(value)
            else:
                masked[key] = value

        return masked
