"""
Idempotency Manager

Ensures that the same PR/commit webhook resend:
- Does NOT cause duplicate runs
- Does NOT cause duplicate write-backs
- Does NOT cause data explosion

Key principle: Same input → Same output, no side effects on retry.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Generic, Protocol, TypeVar
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

T = TypeVar('T')


class IdempotencyStatus(Enum):
    """Status of an idempotency record"""
    IN_PROGRESS = "in_progress"   # Operation is currently running
    COMPLETED = "completed"       # Operation completed successfully
    FAILED = "failed"            # Operation failed


@dataclass
class IdempotencyKey:
    """
    Idempotency key components

    Used to uniquely identify an operation for deduplication.
    """
    # Primary components
    org_id: UUID
    operation_type: str   # e.g., "pr_analysis", "check_run_create"

    # Context-specific components
    repo_full_name: str = ""
    head_sha: str = ""
    pr_number: int | None = None

    # Additional discriminators
    discriminator: str = ""  # Additional unique component

    def __str__(self) -> str:
        """Generate string key"""
        parts = [
            str(self.org_id),
            self.operation_type,
            self.repo_full_name,
            self.head_sha,
        ]

        if self.pr_number is not None:
            parts.append(f"pr:{self.pr_number}")

        if self.discriminator:
            parts.append(self.discriminator)

        return ":".join(parts)

    @property
    def hash(self) -> str:
        """Generate hash of the key for storage"""
        return hashlib.sha256(str(self).encode()).hexdigest()


@dataclass
class IdempotencyRecord:
    """
    Stored idempotency record

    Tracks the state of an idempotent operation.
    """
    id: UUID = field(default_factory=uuid4)

    # Key
    key_hash: str = ""
    key_string: str = ""

    # Tenant
    org_id: UUID = field(default_factory=uuid4)

    # Status
    status: IdempotencyStatus = IdempotencyStatus.IN_PROGRESS

    # Result (stored for returning on duplicate requests)
    result: dict[str, Any] | None = None
    error: str | None = None

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    expires_at: datetime | None = None

    # Metadata
    operation_type: str = ""
    request_id: str | None = None


class IdempotencyStorage(Protocol):
    """Storage interface for idempotency records"""

    async def get_by_key(self, key_hash: str) -> IdempotencyRecord | None:
        ...

    async def save(self, record: IdempotencyRecord) -> IdempotencyRecord:
        ...

    async def update(self, record: IdempotencyRecord) -> IdempotencyRecord:
        ...

    async def delete(self, key_hash: str) -> bool:
        ...

    async def cleanup_expired(self) -> int:
        ...


@dataclass
class IdempotencyResult(Generic[T]):
    """Result of an idempotency check"""
    is_duplicate: bool
    record: IdempotencyRecord
    cached_result: T | None = None


@dataclass
class IdempotencyManager:
    """
    Idempotency Manager

    Ensures operations are executed exactly once:
    - First request: Execute and store result
    - Duplicate request: Return cached result
    - In-flight duplicate: Wait for original or fail

    Usage:
        async with idempotency.guard(key) as result:
            if result.is_duplicate:
                return result.cached_result

            # Do the actual work
            response = await do_work()

            # Store result for future duplicates
            await result.complete(response)
            return response
    """

    storage: IdempotencyStorage

    # TTL for records
    default_ttl_seconds: int = 86400  # 24 hours

    # In-memory cache for hot path (optional)
    _cache: dict[str, IdempotencyRecord] = field(default_factory=dict)
    _cache_enabled: bool = False

    # ------------------------------------------------------------------
    # Idempotency Checking
    # ------------------------------------------------------------------

    async def check(
        self,
        key: IdempotencyKey,
        ttl_seconds: int | None = None,
    ) -> IdempotencyResult:
        """
        Check if an operation is a duplicate

        Args:
            key: Idempotency key
            ttl_seconds: Custom TTL for this operation

        Returns:
            IdempotencyResult with duplicate status and cached result if available
        """
        key_hash = key.hash

        # Check cache first
        if self._cache_enabled and key_hash in self._cache:
            record = self._cache[key_hash]
            if record.status == IdempotencyStatus.COMPLETED:
                return IdempotencyResult(
                    is_duplicate=True,
                    record=record,
                    cached_result=record.result,
                )

        # Check storage
        record = await self.storage.get_by_key(key_hash)

        if record:
            # Check if expired
            if record.expires_at and datetime.utcnow() > record.expires_at:
                await self.storage.delete(key_hash)
                record = None

        if record:
            if record.status == IdempotencyStatus.COMPLETED:
                logger.debug(f"Idempotency hit (completed): {key}")
                return IdempotencyResult(
                    is_duplicate=True,
                    record=record,
                    cached_result=record.result,
                )

            elif record.status == IdempotencyStatus.IN_PROGRESS:
                # Operation is in flight - this is a race condition
                logger.warning(f"Idempotency hit (in progress): {key}")
                return IdempotencyResult(
                    is_duplicate=True,
                    record=record,
                    cached_result=None,  # No result yet
                )

            elif record.status == IdempotencyStatus.FAILED:
                # Previous attempt failed - allow retry
                logger.debug(f"Idempotency hit (failed, allowing retry): {key}")
                await self.storage.delete(key_hash)
                record = None

        # New operation - create record
        ttl = ttl_seconds or self.default_ttl_seconds
        record = IdempotencyRecord(
            key_hash=key_hash,
            key_string=str(key),
            org_id=key.org_id,
            operation_type=key.operation_type,
            status=IdempotencyStatus.IN_PROGRESS,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl),
        )

        record = await self.storage.save(record)

        if self._cache_enabled:
            self._cache[key_hash] = record

        logger.debug(f"Idempotency miss, new record: {key}")

        return IdempotencyResult(
            is_duplicate=False,
            record=record,
        )

    async def complete(
        self,
        key: IdempotencyKey,
        result: dict[str, Any],
    ) -> IdempotencyRecord:
        """
        Mark an operation as completed with result

        The result will be returned for future duplicate requests.
        """
        key_hash = key.hash

        record = await self.storage.get_by_key(key_hash)
        if not record:
            raise ValueError(f"No idempotency record found for key: {key}")

        record.status = IdempotencyStatus.COMPLETED
        record.result = result
        record.completed_at = datetime.utcnow()

        record = await self.storage.update(record)

        if self._cache_enabled:
            self._cache[key_hash] = record

        logger.debug(f"Idempotency completed: {key}")

        return record

    async def fail(
        self,
        key: IdempotencyKey,
        error: str,
    ) -> IdempotencyRecord:
        """
        Mark an operation as failed

        Failed operations can be retried.
        """
        key_hash = key.hash

        record = await self.storage.get_by_key(key_hash)
        if not record:
            raise ValueError(f"No idempotency record found for key: {key}")

        record.status = IdempotencyStatus.FAILED
        record.error = error
        record.completed_at = datetime.utcnow()

        record = await self.storage.update(record)

        if self._cache_enabled:
            self._cache[key_hash] = record

        logger.debug(f"Idempotency failed: {key} error={error}")

        return record

    async def release(
        self,
        key: IdempotencyKey,
    ) -> bool:
        """
        Release an idempotency lock without storing result

        Used when operation is cancelled or needs to be retried.
        """
        key_hash = key.hash

        result = await self.storage.delete(key_hash)

        if self._cache_enabled and key_hash in self._cache:
            del self._cache[key_hash]

        logger.debug(f"Idempotency released: {key}")

        return result

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------

    def guard(
        self,
        key: IdempotencyKey,
        ttl_seconds: int | None = None,
    ) -> "IdempotencyGuard":
        """
        Create an idempotency guard context manager

        Usage:
            async with manager.guard(key) as guard:
                if guard.is_duplicate:
                    return guard.cached_result

                result = await do_work()
                await guard.complete(result)
                return result
        """
        return IdempotencyGuard(self, key, ttl_seconds)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def cleanup(self) -> int:
        """Clean up expired idempotency records"""
        count = await self.storage.cleanup_expired()
        logger.info(f"Cleaned up {count} expired idempotency records")
        return count


@dataclass
class IdempotencyGuard:
    """
    Context manager for idempotent operations

    Usage:
        async with IdempotencyGuard(manager, key) as guard:
            if guard.is_duplicate:
                return guard.cached_result
            result = await do_work()
            await guard.complete(result)
    """
    manager: IdempotencyManager
    key: IdempotencyKey
    ttl_seconds: int | None = None

    _result: IdempotencyResult | None = None
    _completed: bool = False

    @property
    def is_duplicate(self) -> bool:
        """Check if this is a duplicate request"""
        return self._result.is_duplicate if self._result else False

    @property
    def cached_result(self) -> dict[str, Any] | None:
        """Get cached result for duplicates"""
        return self._result.cached_result if self._result else None

    async def __aenter__(self) -> "IdempotencyGuard":
        """Enter the context - check idempotency"""
        self._result = await self.manager.check(self.key, self.ttl_seconds)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context - handle completion or failure"""
        if self._completed or self.is_duplicate:
            return

        if exc_type:
            # Operation failed
            await self.manager.fail(self.key, str(exc_val))
        else:
            # Operation succeeded but no result stored - release lock
            await self.manager.release(self.key)

    async def complete(self, result: dict[str, Any]) -> None:
        """Mark operation as completed with result"""
        await self.manager.complete(self.key, result)
        self._completed = True


# ------------------------------------------------------------------
# Convenience Functions for Common Patterns
# ------------------------------------------------------------------

def make_pr_analysis_key(
    org_id: UUID,
    repo_full_name: str,
    pr_number: int,
    head_sha: str,
) -> IdempotencyKey:
    """Create idempotency key for PR analysis"""
    return IdempotencyKey(
        org_id=org_id,
        operation_type="pr_analysis",
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        head_sha=head_sha,
    )


def make_check_run_key(
    org_id: UUID,
    repo_full_name: str,
    head_sha: str,
    check_name: str,
) -> IdempotencyKey:
    """Create idempotency key for creating a check run"""
    return IdempotencyKey(
        org_id=org_id,
        operation_type="check_run_create",
        repo_full_name=repo_full_name,
        head_sha=head_sha,
        discriminator=check_name,
    )


def make_report_generation_key(
    org_id: UUID,
    repo_full_name: str,
    head_sha: str,
    report_type: str,
) -> IdempotencyKey:
    """Create idempotency key for report generation"""
    return IdempotencyKey(
        org_id=org_id,
        operation_type="report_generation",
        repo_full_name=repo_full_name,
        head_sha=head_sha,
        discriminator=report_type,
    )
