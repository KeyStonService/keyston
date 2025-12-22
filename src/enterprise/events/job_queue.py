"""
Job Queue System

Separate queues for different priorities:
- gate_queue: High priority, for blocking checks (must complete quickly)
- report_queue: Low priority, for reporting (can be delayed)

Features:
- Priority-based scheduling
- Retry with exponential backoff
- Dead Letter Queue (DLQ) for failed jobs
- Visibility timeout for crash recovery
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class JobPriority(Enum):
    """Job priority levels"""
    CRITICAL = 0    # Gate checks (blocking)
    HIGH = 1        # Time-sensitive operations
    NORMAL = 2      # Standard processing
    LOW = 3         # Background tasks
    BULK = 4        # Batch operations


class JobStatus(Enum):
    """Job status"""
    PENDING = "pending"           # Waiting in queue
    PROCESSING = "processing"     # Being executed
    COMPLETED = "completed"       # Successfully completed
    FAILED = "failed"            # Failed (will retry)
    DEAD = "dead"                # Exceeded retries, moved to DLQ
    CANCELLED = "cancelled"      # Manually cancelled


class QueueType(Enum):
    """Queue types"""
    GATE = "gate_queue"           # High priority gate checks
    REPORT = "report_queue"       # Lower priority reporting
    INTEGRATION = "integration_queue"  # Provider integrations
    NOTIFICATION = "notification_queue"  # Notifications


@dataclass
class Job:
    """
    Job in the queue

    Represents a unit of work to be processed.
    """
    id: UUID = field(default_factory=uuid4)

    # Tenant isolation
    org_id: UUID = field(default_factory=uuid4)

    # Job type and data
    job_type: str = ""         # e.g., "analyze_pr", "generate_report"
    payload: dict[str, Any] = field(default_factory=dict)

    # Queue assignment
    queue: QueueType = QueueType.GATE
    priority: JobPriority = JobPriority.NORMAL

    # Source event (for tracing)
    event_id: UUID | None = None
    correlation_id: UUID | None = None

    # Status
    status: JobStatus = JobStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: datetime | None = None  # For delayed jobs
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Retry
    attempt: int = 0
    max_attempts: int = 3
    next_retry_at: datetime | None = None

    # Visibility
    visibility_timeout: int = 300  # Seconds before job becomes visible again
    visible_at: datetime | None = None

    # Worker
    worker_id: str | None = None
    locked_until: datetime | None = None

    # Metadata
    timeout_seconds: int = 600   # Job execution timeout
    idempotency_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": str(self.id),
            "org_id": str(self.org_id),
            "job_type": self.job_type,
            "payload": self.payload,
            "queue": self.queue.value,
            "priority": self.priority.value,
            "event_id": str(self.event_id) if self.event_id else None,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None,
            "visibility_timeout": self.visibility_timeout,
            "worker_id": self.worker_id,
            "timeout_seconds": self.timeout_seconds,
            "idempotency_key": self.idempotency_key,
        }


@dataclass
class DeadLetterJob:
    """Job that has been moved to the Dead Letter Queue"""
    id: UUID = field(default_factory=uuid4)
    original_job: Job = None
    moved_at: datetime = field(default_factory=datetime.utcnow)
    reason: str = ""
    final_error: str = ""
    attempts_made: int = 0


class JobStorage(Protocol):
    """Storage interface for jobs"""

    async def save(self, job: Job) -> Job:
        ...

    async def get(self, job_id: UUID) -> Job | None:
        ...

    async def update(self, job: Job) -> Job:
        ...

    async def delete(self, job_id: UUID) -> bool:
        ...

    async def get_pending_jobs(
        self,
        queue: QueueType,
        limit: int = 10,
    ) -> list[Job]:
        """Get pending jobs ordered by priority and creation time"""
        ...

    async def get_jobs_by_status(
        self,
        org_id: UUID,
        status: JobStatus,
        limit: int = 100,
    ) -> list[Job]:
        ...

    async def count_jobs(
        self,
        org_id: UUID,
        queue: QueueType | None = None,
        status: JobStatus | None = None,
    ) -> int:
        ...


class DLQStorage(Protocol):
    """Storage interface for Dead Letter Queue"""

    async def save(self, dlq_job: DeadLetterJob) -> DeadLetterJob:
        ...

    async def get(self, job_id: UUID) -> DeadLetterJob | None:
        ...

    async def list(
        self,
        org_id: UUID,
        limit: int = 100,
    ) -> list[DeadLetterJob]:
        ...

    async def delete(self, job_id: UUID) -> bool:
        ...


JobHandler = Callable[[Job], Awaitable[dict[str, Any]]]


@dataclass
class JobQueue:
    """
    Job Queue Manager

    Manages job lifecycle with:
    - Priority-based scheduling
    - Retry with exponential backoff
    - Dead Letter Queue for failures
    - Visibility timeout for crash recovery
    """

    storage: JobStorage
    dlq_storage: DLQStorage | None = None

    # Handler registry
    handlers: dict[str, JobHandler] = field(default_factory=dict)

    # Configuration
    default_max_attempts: int = 3
    base_retry_delay: float = 30.0  # seconds
    max_retry_delay: float = 3600.0  # 1 hour

    # Visibility timeout (for crash recovery)
    default_visibility_timeout: int = 300  # 5 minutes

    # ------------------------------------------------------------------
    # Job Submission
    # ------------------------------------------------------------------

    async def enqueue(
        self,
        org_id: UUID,
        job_type: str,
        payload: dict[str, Any],
        queue: QueueType = QueueType.GATE,
        priority: JobPriority = JobPriority.NORMAL,
        event_id: UUID | None = None,
        correlation_id: UUID | None = None,
        scheduled_at: datetime | None = None,
        idempotency_key: str | None = None,
        max_attempts: int | None = None,
        timeout_seconds: int = 600,
    ) -> Job:
        """
        Enqueue a new job

        Args:
            org_id: Organization ID
            job_type: Type of job (maps to handler)
            payload: Job-specific data
            queue: Queue to use
            priority: Job priority
            event_id: Source event ID
            correlation_id: Correlation ID for tracing
            scheduled_at: Future execution time (delayed job)
            idempotency_key: Key for deduplication
            max_attempts: Max retry attempts
            timeout_seconds: Job execution timeout

        Returns:
            Created job
        """
        job = Job(
            org_id=org_id,
            job_type=job_type,
            payload=payload,
            queue=queue,
            priority=priority,
            event_id=event_id,
            correlation_id=correlation_id or uuid4(),
            scheduled_at=scheduled_at,
            idempotency_key=idempotency_key,
            max_attempts=max_attempts or self.default_max_attempts,
            timeout_seconds=timeout_seconds,
            visibility_timeout=self.default_visibility_timeout,
        )

        job = await self.storage.save(job)

        logger.info(
            f"Job enqueued: id={job.id} type={job_type} "
            f"queue={queue.value} priority={priority.value}"
        )

        return job

    async def enqueue_gate_job(
        self,
        org_id: UUID,
        job_type: str,
        payload: dict[str, Any],
        event_id: UUID | None = None,
        **kwargs,
    ) -> Job:
        """Convenience method for high-priority gate jobs"""
        return await self.enqueue(
            org_id=org_id,
            job_type=job_type,
            payload=payload,
            queue=QueueType.GATE,
            priority=JobPriority.CRITICAL,
            event_id=event_id,
            timeout_seconds=300,  # 5 minute timeout for gate
            **kwargs,
        )

    async def enqueue_report_job(
        self,
        org_id: UUID,
        job_type: str,
        payload: dict[str, Any],
        event_id: UUID | None = None,
        **kwargs,
    ) -> Job:
        """Convenience method for lower-priority report jobs"""
        return await self.enqueue(
            org_id=org_id,
            job_type=job_type,
            payload=payload,
            queue=QueueType.REPORT,
            priority=JobPriority.NORMAL,
            event_id=event_id,
            timeout_seconds=1800,  # 30 minute timeout for reports
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Job Processing
    # ------------------------------------------------------------------

    async def fetch_job(
        self,
        queue: QueueType,
        worker_id: str,
    ) -> Job | None:
        """
        Fetch the next available job from a queue

        Uses visibility timeout to prevent duplicate processing.
        """
        jobs = await self.storage.get_pending_jobs(queue, limit=1)

        if not jobs:
            return None

        job = jobs[0]

        # Check if scheduled for later
        if job.scheduled_at and datetime.utcnow() < job.scheduled_at:
            return None

        # Lock the job
        job.status = JobStatus.PROCESSING
        job.worker_id = worker_id
        job.started_at = datetime.utcnow()
        job.locked_until = datetime.utcnow() + timedelta(seconds=job.visibility_timeout)
        job.attempt += 1

        job = await self.storage.update(job)

        logger.debug(f"Job fetched: id={job.id} worker={worker_id}")

        return job

    async def complete_job(
        self,
        job_id: UUID,
        result: dict[str, Any] | None = None,
    ) -> Job:
        """Mark a job as completed"""
        job = await self.storage.get(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result = result

        job = await self.storage.update(job)

        logger.info(
            f"Job completed: id={job_id} "
            f"duration={(job.completed_at - job.started_at).total_seconds():.2f}s"
        )

        return job

    async def fail_job(
        self,
        job_id: UUID,
        error: str,
    ) -> Job:
        """
        Mark a job as failed

        Will schedule retry if attempts remain, otherwise move to DLQ.
        """
        job = await self.storage.get(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        job.error = error

        if job.attempt >= job.max_attempts:
            # Move to Dead Letter Queue
            job.status = JobStatus.DEAD
            job = await self.storage.update(job)

            if self.dlq_storage:
                dlq_job = DeadLetterJob(
                    original_job=job,
                    reason="max_attempts_exceeded",
                    final_error=error,
                    attempts_made=job.attempt,
                )
                await self.dlq_storage.save(dlq_job)

            logger.warning(
                f"Job moved to DLQ: id={job_id} attempts={job.attempt} error={error}"
            )
        else:
            # Schedule retry with exponential backoff
            delay = min(
                self.base_retry_delay * (2 ** (job.attempt - 1)),
                self.max_retry_delay,
            )
            job.status = JobStatus.PENDING
            job.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
            job.scheduled_at = job.next_retry_at
            job.worker_id = None
            job.locked_until = None

            job = await self.storage.update(job)

            logger.info(
                f"Job scheduled for retry: id={job_id} "
                f"attempt={job.attempt}/{job.max_attempts} "
                f"next_retry_at={job.next_retry_at}"
            )

        return job

    async def cancel_job(
        self,
        job_id: UUID,
        reason: str = "",
    ) -> Job:
        """Cancel a pending or processing job"""
        job = await self.storage.get(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        if job.status not in (JobStatus.PENDING, JobStatus.PROCESSING):
            raise ValueError(f"Cannot cancel job in status: {job.status.value}")

        job.status = JobStatus.CANCELLED
        job.error = reason
        job.completed_at = datetime.utcnow()

        job = await self.storage.update(job)

        logger.info(f"Job cancelled: id={job_id} reason={reason}")

        return job

    # ------------------------------------------------------------------
    # Handler Registration
    # ------------------------------------------------------------------

    def register_handler(
        self,
        job_type: str,
        handler: JobHandler,
    ) -> None:
        """Register a handler for a job type"""
        self.handlers[job_type] = handler
        logger.info(f"Handler registered: {job_type}")

    async def process_job(self, job: Job) -> Job:
        """
        Process a job using the registered handler

        This is called by workers after fetching a job.
        """
        handler = self.handlers.get(job.job_type)

        if not handler:
            return await self.fail_job(job.id, f"No handler for job type: {job.job_type}")

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(job),
                timeout=job.timeout_seconds,
            )
            return await self.complete_job(job.id, result)

        except TimeoutError:
            return await self.fail_job(job.id, f"Job timed out after {job.timeout_seconds}s")

        except Exception as e:
            logger.exception(f"Job failed: id={job.id} error={e}")
            return await self.fail_job(job.id, str(e))

    # ------------------------------------------------------------------
    # Visibility Timeout Recovery
    # ------------------------------------------------------------------

    async def recover_stale_jobs(
        self,
        queue: QueueType,
    ) -> int:
        """
        Recover jobs that exceeded visibility timeout

        These are jobs where the worker crashed or timed out.
        """
        # This would query for jobs where:
        # - status = PROCESSING
        # - locked_until < now
        # And reset them to PENDING

        # Implementation depends on storage backend
        logger.info(f"Recovering stale jobs for queue: {queue.value}")
        return 0

    # ------------------------------------------------------------------
    # DLQ Operations
    # ------------------------------------------------------------------

    async def retry_dlq_job(
        self,
        dlq_job_id: UUID,
    ) -> Job | None:
        """Retry a job from the Dead Letter Queue"""
        if not self.dlq_storage:
            raise ValueError("DLQ storage not configured")

        dlq_job = await self.dlq_storage.get(dlq_job_id)
        if not dlq_job:
            raise ValueError(f"DLQ job not found: {dlq_job_id}")

        # Create a new job from the DLQ job
        original = dlq_job.original_job
        new_job = await self.enqueue(
            org_id=original.org_id,
            job_type=original.job_type,
            payload=original.payload,
            queue=original.queue,
            priority=original.priority,
            event_id=original.event_id,
            correlation_id=original.correlation_id,
            max_attempts=3,  # Reset attempts
        )

        # Remove from DLQ
        await self.dlq_storage.delete(dlq_job_id)

        logger.info(f"DLQ job retried: {dlq_job_id} -> {new_job.id}")

        return new_job

    async def list_dlq_jobs(
        self,
        org_id: UUID,
        limit: int = 100,
    ) -> list[DeadLetterJob]:
        """List jobs in the Dead Letter Queue"""
        if not self.dlq_storage:
            return []
        return await self.dlq_storage.list(org_id, limit)

    # ------------------------------------------------------------------
    # Queue Stats
    # ------------------------------------------------------------------

    async def get_queue_stats(
        self,
        org_id: UUID,
    ) -> dict[str, Any]:
        """Get queue statistics"""
        stats = {}

        for queue in QueueType:
            pending = await self.storage.count_jobs(org_id, queue, JobStatus.PENDING)
            processing = await self.storage.count_jobs(org_id, queue, JobStatus.PROCESSING)

            stats[queue.value] = {
                "pending": pending,
                "processing": processing,
            }

        return stats


@dataclass
class DeadLetterQueue:
    """
    Dead Letter Queue (DLQ) Manager

    Stores jobs that have failed too many times for investigation.
    """

    storage: DLQStorage

    async def add(
        self,
        job: Job,
        reason: str,
        final_error: str,
    ) -> DeadLetterJob:
        """Add a job to the DLQ"""
        dlq_job = DeadLetterJob(
            original_job=job,
            reason=reason,
            final_error=final_error,
            attempts_made=job.attempt,
        )

        return await self.storage.save(dlq_job)

    async def list(
        self,
        org_id: UUID,
        limit: int = 100,
    ) -> list[DeadLetterJob]:
        """List DLQ jobs"""
        return await self.storage.list(org_id, limit)

    async def remove(self, job_id: UUID) -> bool:
        """Remove a job from the DLQ"""
        return await self.storage.delete(job_id)

    async def clear(self, org_id: UUID) -> int:
        """Clear all DLQ jobs for an org"""
        jobs = await self.storage.list(org_id, limit=10000)
        count = 0
        for job in jobs:
            await self.storage.delete(job.id)
            count += 1
        return count
