"""
Event Log (Outbox Pattern)

Webhook events are stored first ("落盤") before processing.
This enables:
- Replay: Re-process events if needed
- Audit: Complete history of all events
- Reliability: Events are never lost

This is the CORE of event-driven architecture.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class EventStatus(Enum):
    """Event processing status"""
    RECEIVED = "received"       # Just received, not processed
    PROCESSING = "processing"   # Currently being processed
    PROCESSED = "processed"     # Successfully processed
    FAILED = "failed"          # Processing failed
    SKIPPED = "skipped"        # Skipped (e.g., duplicate, filtered)


@dataclass
class StoredEvent:
    """
    Stored event in the event log

    This is the "standardized event" that webhooks are converted to.
    It's the source of truth for all processing.
    """
    id: UUID = field(default_factory=uuid4)

    # Tenant isolation
    org_id: UUID = field(default_factory=uuid4)

    # Event identification
    event_type: str = ""         # e.g., "pull_request.opened"
    source: str = ""             # e.g., "github", "gitlab"
    source_id: str = ""          # Provider's event ID (delivery_id)

    # Correlation
    correlation_id: UUID | None = None  # Links related events
    causation_id: UUID | None = None    # Event that caused this one

    # Repository context
    repo_id: UUID | None = None
    repo_full_name: str = ""

    # Event-specific data (denormalized for querying)
    head_sha: str | None = None
    pr_number: int | None = None
    ref: str | None = None

    # Full payload
    payload: dict[str, Any] = field(default_factory=dict)

    # Processing status
    status: EventStatus = EventStatus.RECEIVED
    processed_at: datetime | None = None
    process_error: str | None = None
    retry_count: int = 0

    # Jobs spawned from this event
    job_ids: list[UUID] = field(default_factory=list)

    # Metadata
    received_at: datetime = field(default_factory=datetime.utcnow)
    schema_version: str = "1.0"

    # Audit
    processed_by: str | None = None  # Worker ID that processed

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": str(self.id),
            "org_id": str(self.org_id),
            "event_type": self.event_type,
            "source": self.source,
            "source_id": self.source_id,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "causation_id": str(self.causation_id) if self.causation_id else None,
            "repo_id": str(self.repo_id) if self.repo_id else None,
            "repo_full_name": self.repo_full_name,
            "head_sha": self.head_sha,
            "pr_number": self.pr_number,
            "ref": self.ref,
            "payload": self.payload,
            "status": self.status.value,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "process_error": self.process_error,
            "retry_count": self.retry_count,
            "job_ids": [str(j) for j in self.job_ids],
            "received_at": self.received_at.isoformat(),
            "schema_version": self.schema_version,
            "processed_by": self.processed_by,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoredEvent":
        """Create from dictionary"""
        return cls(
            id=UUID(data["id"]),
            org_id=UUID(data["org_id"]),
            event_type=data.get("event_type", ""),
            source=data.get("source", ""),
            source_id=data.get("source_id", ""),
            correlation_id=UUID(data["correlation_id"]) if data.get("correlation_id") else None,
            causation_id=UUID(data["causation_id"]) if data.get("causation_id") else None,
            repo_id=UUID(data["repo_id"]) if data.get("repo_id") else None,
            repo_full_name=data.get("repo_full_name", ""),
            head_sha=data.get("head_sha"),
            pr_number=data.get("pr_number"),
            ref=data.get("ref"),
            payload=data.get("payload", {}),
            status=EventStatus(data.get("status", "received")),
            processed_at=datetime.fromisoformat(data["processed_at"]) if data.get("processed_at") else None,
            process_error=data.get("process_error"),
            retry_count=data.get("retry_count", 0),
            job_ids=[UUID(j) for j in data.get("job_ids", [])],
            received_at=datetime.fromisoformat(data["received_at"]) if data.get("received_at") else datetime.utcnow(),
            schema_version=data.get("schema_version", "1.0"),
            processed_by=data.get("processed_by"),
        )


@dataclass
class EventFilter:
    """Filter for querying events"""
    org_id: UUID | None = None
    event_types: list[str] | None = None
    source: str | None = None
    repo_id: UUID | None = None
    head_sha: str | None = None
    pr_number: int | None = None
    status: EventStatus | None = None
    received_after: datetime | None = None
    received_before: datetime | None = None
    correlation_id: UUID | None = None


class EventStorage(Protocol):
    """Storage interface for event log"""

    async def save(self, event: StoredEvent) -> StoredEvent:
        ...

    async def get(self, event_id: UUID) -> StoredEvent | None:
        ...

    async def update(self, event: StoredEvent) -> StoredEvent:
        ...

    async def query(
        self,
        filter: EventFilter,
        offset: int = 0,
        limit: int = 100,
    ) -> list[StoredEvent]:
        ...

    async def count(self, filter: EventFilter) -> int:
        ...


class EventPublisher(Protocol):
    """Interface for publishing events to processing queue"""

    async def publish(self, event: StoredEvent) -> None:
        ...


@dataclass
class EventLog:
    """
    Event Log Manager

    Core component for event-driven architecture:
    1. Receive webhook → Store event (落盤)
    2. Publish to processing queue
    3. Track processing status
    4. Enable replay if needed
    """

    storage: EventStorage
    publisher: EventPublisher | None = None

    # Retention settings
    retention_days: int = 90
    max_retry_count: int = 3

    # ------------------------------------------------------------------
    # Event Ingestion
    # ------------------------------------------------------------------

    async def store_event(
        self,
        org_id: UUID,
        event_type: str,
        source: str,
        source_id: str,
        payload: dict[str, Any],
        repo_id: UUID | None = None,
        repo_full_name: str = "",
        head_sha: str | None = None,
        pr_number: int | None = None,
        ref: str | None = None,
        correlation_id: UUID | None = None,
    ) -> StoredEvent:
        """
        Store a new event (落盤)

        This MUST be called before any processing.
        The event is persisted first, then published for processing.

        Args:
            org_id: Organization ID (tenant isolation)
            event_type: Event type (e.g., "pull_request.opened")
            source: Event source (e.g., "github")
            source_id: Provider's event ID for deduplication
            payload: Full event payload
            repo_id: Repository ID in our system
            repo_full_name: Repository full name
            head_sha: Commit SHA (for PR/push events)
            pr_number: PR number (for PR events)
            ref: Git ref (branch/tag)
            correlation_id: Correlation ID for related events

        Returns:
            Stored event
        """
        event = StoredEvent(
            org_id=org_id,
            event_type=event_type,
            source=source,
            source_id=source_id,
            payload=payload,
            repo_id=repo_id,
            repo_full_name=repo_full_name,
            head_sha=head_sha,
            pr_number=pr_number,
            ref=ref,
            correlation_id=correlation_id or uuid4(),
            status=EventStatus.RECEIVED,
        )

        # Persist first (落盤)
        event = await self.storage.save(event)

        logger.info(
            f"Event stored: id={event.id} type={event_type} "
            f"source={source} repo={repo_full_name}"
        )

        # Publish for processing
        if self.publisher:
            await self.publisher.publish(event)

        return event

    async def get_event(self, event_id: UUID) -> StoredEvent | None:
        """Get an event by ID"""
        return await self.storage.get(event_id)

    async def query_events(
        self,
        filter: EventFilter,
        offset: int = 0,
        limit: int = 100,
    ) -> list[StoredEvent]:
        """Query events with filter"""
        return await self.storage.query(filter, offset, limit)

    # ------------------------------------------------------------------
    # Event Processing
    # ------------------------------------------------------------------

    async def mark_processing(
        self,
        event_id: UUID,
        worker_id: str = "",
    ) -> StoredEvent:
        """Mark an event as being processed"""
        event = await self.storage.get(event_id)
        if not event:
            raise ValueError(f"Event not found: {event_id}")

        event.status = EventStatus.PROCESSING
        event.processed_by = worker_id
        event = await self.storage.update(event)

        return event

    async def mark_processed(
        self,
        event_id: UUID,
        job_ids: list[UUID] | None = None,
    ) -> StoredEvent:
        """Mark an event as successfully processed"""
        event = await self.storage.get(event_id)
        if not event:
            raise ValueError(f"Event not found: {event_id}")

        event.status = EventStatus.PROCESSED
        event.processed_at = datetime.utcnow()
        if job_ids:
            event.job_ids.extend(job_ids)

        event = await self.storage.update(event)

        logger.info(f"Event processed: id={event_id} jobs={len(job_ids or [])}")

        return event

    async def mark_failed(
        self,
        event_id: UUID,
        error: str,
    ) -> StoredEvent:
        """Mark an event as failed"""
        event = await self.storage.get(event_id)
        if not event:
            raise ValueError(f"Event not found: {event_id}")

        event.status = EventStatus.FAILED
        event.process_error = error
        event.retry_count += 1

        event = await self.storage.update(event)

        logger.warning(f"Event failed: id={event_id} error={error}")

        return event

    async def mark_skipped(
        self,
        event_id: UUID,
        reason: str,
    ) -> StoredEvent:
        """Mark an event as skipped (e.g., duplicate)"""
        event = await self.storage.get(event_id)
        if not event:
            raise ValueError(f"Event not found: {event_id}")

        event.status = EventStatus.SKIPPED
        event.process_error = reason
        event.processed_at = datetime.utcnow()

        event = await self.storage.update(event)

        logger.info(f"Event skipped: id={event_id} reason={reason}")

        return event

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    async def replay_event(
        self,
        event_id: UUID,
    ) -> StoredEvent:
        """
        Replay a single event

        Resets status and publishes for reprocessing.
        """
        event = await self.storage.get(event_id)
        if not event:
            raise ValueError(f"Event not found: {event_id}")

        # Reset status
        event.status = EventStatus.RECEIVED
        event.processed_at = None
        event.process_error = None
        event.job_ids = []

        event = await self.storage.update(event)

        # Re-publish
        if self.publisher:
            await self.publisher.publish(event)

        logger.info(f"Event replayed: id={event_id}")

        return event

    async def replay_events(
        self,
        filter: EventFilter,
        limit: int = 1000,
    ) -> int:
        """
        Replay multiple events matching filter

        Use with caution - can cause load spikes.

        Returns:
            Number of events replayed
        """
        events = await self.storage.query(filter, limit=limit)
        count = 0

        for event in events:
            await self.replay_event(event.id)
            count += 1

        logger.info(f"Events replayed: count={count}")

        return count

    async def replay_failed(
        self,
        org_id: UUID,
        max_retry: int = 3,
    ) -> int:
        """Replay all failed events that haven't exceeded retry limit"""
        filter = EventFilter(
            org_id=org_id,
            status=EventStatus.FAILED,
        )

        events = await self.storage.query(filter, limit=10000)
        count = 0

        for event in events:
            if event.retry_count < max_retry:
                await self.replay_event(event.id)
                count += 1

        logger.info(f"Failed events replayed: count={count}")

        return count

    # ------------------------------------------------------------------
    # Correlation
    # ------------------------------------------------------------------

    async def get_correlated_events(
        self,
        correlation_id: UUID,
    ) -> list[StoredEvent]:
        """Get all events with the same correlation ID"""
        filter = EventFilter(correlation_id=correlation_id)
        return await self.storage.query(filter, limit=1000)

    async def get_event_chain(
        self,
        event_id: UUID,
    ) -> list[StoredEvent]:
        """Get the causation chain for an event"""
        event = await self.storage.get(event_id)
        if not event:
            return []

        chain = [event]

        # Walk back through causation
        current = event
        while current.causation_id:
            parent = await self.storage.get(current.causation_id)
            if not parent:
                break
            chain.insert(0, parent)
            current = parent

        return chain

    # ------------------------------------------------------------------
    # Audit & Retention
    # ------------------------------------------------------------------

    async def get_event_count(
        self,
        org_id: UUID,
        since: datetime | None = None,
    ) -> dict[str, int]:
        """Get event counts by status"""
        counts = {}

        for status in EventStatus:
            filter = EventFilter(
                org_id=org_id,
                status=status,
                received_after=since,
            )
            counts[status.value] = await self.storage.count(filter)

        return counts

    async def cleanup_old_events(
        self,
        org_id: UUID,
        older_than_days: int | None = None,
        dry_run: bool = True,
    ) -> int:
        """
        Clean up old events

        Only removes PROCESSED and SKIPPED events.
        FAILED events are kept for investigation.
        """
        days = older_than_days or self.retention_days
        cutoff = datetime.utcnow() - timedelta(days=days)

        filter = EventFilter(
            org_id=org_id,
            received_before=cutoff,
        )

        events = await self.storage.query(filter, limit=10000)
        count = 0

        for event in events:
            if event.status in (EventStatus.PROCESSED, EventStatus.SKIPPED):
                if not dry_run:
                    # In production, soft delete or archive
                    pass
                count += 1

        logger.info(
            f"Event cleanup: org={org_id} count={count} dry_run={dry_run}"
        )

        return count
