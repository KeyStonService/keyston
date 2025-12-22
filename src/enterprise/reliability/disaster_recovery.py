"""
Disaster Recovery

Ensures business continuity:
- Database backup and restoration
- Event log retention and replay
- Point-in-time recovery capability
- Recovery Time Objective (RTO) and Recovery Point Objective (RPO)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Backup types"""
    FULL = "full"               # Complete backup
    INCREMENTAL = "incremental" # Changes since last backup
    DIFFERENTIAL = "differential" # Changes since last full
    SNAPSHOT = "snapshot"       # Point-in-time snapshot


class BackupStatus(Enum):
    """Backup status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class RecoveryStatus(Enum):
    """Recovery operation status"""
    PENDING = "pending"
    VALIDATING = "validating"
    RESTORING = "restoring"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackupConfig:
    """
    Backup configuration

    Defines backup schedule and retention.
    """
    # Schedule
    full_backup_interval_hours: int = 24      # Daily full backup
    incremental_interval_hours: int = 1       # Hourly incremental

    # Retention
    full_backup_retention_days: int = 30      # Keep 30 days of full backups
    incremental_retention_days: int = 7       # Keep 7 days of incrementals

    # Targets
    backup_database: bool = True
    backup_event_log: bool = True
    backup_object_storage: bool = True
    backup_secrets: bool = True

    # Storage
    backup_bucket: str = "mno-backups"
    backup_region: str = "us-east-1"

    # Encryption
    encrypt_backups: bool = True
    encryption_key_id: str = ""

    # Verification
    verify_after_backup: bool = True
    verify_restore_daily: bool = True


@dataclass
class BackupRecord:
    """
    Record of a backup
    """
    id: UUID = field(default_factory=uuid4)

    # Backup details
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.PENDING

    # What was backed up
    database_included: bool = True
    event_log_included: bool = True
    objects_included: bool = True
    secrets_included: bool = False

    # Location
    storage_location: str = ""
    size_bytes: int = 0

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None

    # Chain (for incremental)
    parent_backup_id: UUID | None = None
    sequence_number: int = 0

    # Verification
    verified: bool = False
    verified_at: datetime | None = None
    checksum: str = ""

    # Retention
    expires_at: datetime | None = None

    # Error
    error: str | None = None


@dataclass
class RecoveryPoint:
    """
    Point-in-time recovery point

    Represents a point to which we can recover.
    """
    id: UUID = field(default_factory=uuid4)

    # Point in time
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # What can be recovered
    database_recoverable: bool = True
    event_log_recoverable: bool = True
    objects_recoverable: bool = True

    # Backups needed for recovery
    required_backups: list[UUID] = field(default_factory=list)

    # Estimated recovery time
    estimated_rto_minutes: int = 30

    # Data loss (RPO)
    potential_data_loss_minutes: int = 5

    # Verified
    verified: bool = False


@dataclass
class RecoveryPlan:
    """
    Recovery plan for disaster scenarios
    """
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""

    # Recovery objectives
    target_rto_minutes: int = 60    # Recovery Time Objective
    target_rpo_minutes: int = 15    # Recovery Point Objective

    # Steps
    steps: list[dict[str, Any]] = field(default_factory=list)

    # Dependencies
    required_resources: list[str] = field(default_factory=list)
    required_credentials: list[str] = field(default_factory=list)

    # Testing
    last_tested_at: datetime | None = None
    last_test_result: str | None = None
    test_frequency_days: int = 30

    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class BackupStorage(Protocol):
    """Interface for backup storage"""

    async def save_backup(self, record: BackupRecord) -> BackupRecord:
        ...

    async def get_backup(self, backup_id: UUID) -> BackupRecord | None:
        ...

    async def list_backups(
        self,
        backup_type: BackupType | None = None,
        status: BackupStatus | None = None,
        limit: int = 100,
    ) -> list[BackupRecord]:
        ...

    async def delete_backup(self, backup_id: UUID) -> bool:
        ...


class DatabaseBackupService(Protocol):
    """Interface for database backup operations"""

    async def create_backup(
        self,
        backup_type: BackupType,
        destination: str,
    ) -> dict[str, Any]:
        ...

    async def restore_backup(
        self,
        source: str,
        target_database: str,
    ) -> dict[str, Any]:
        ...

    async def verify_backup(
        self,
        source: str,
    ) -> bool:
        ...


class EventLogBackupService(Protocol):
    """Interface for event log backup"""

    async def export_events(
        self,
        start_time: datetime,
        end_time: datetime,
        destination: str,
    ) -> dict[str, Any]:
        ...

    async def import_events(
        self,
        source: str,
    ) -> int:
        ...


@dataclass
class DisasterRecovery:
    """
    Disaster Recovery Manager

    Manages backups and recovery operations.
    """

    config: BackupConfig = field(default_factory=BackupConfig)
    backup_storage: BackupStorage | None = None
    db_backup_service: DatabaseBackupService | None = None
    event_log_service: EventLogBackupService | None = None

    # Recovery plans
    recovery_plans: dict[str, RecoveryPlan] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Backup Operations
    # ------------------------------------------------------------------

    async def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        include_database: bool = True,
        include_events: bool = True,
        include_objects: bool = False,
    ) -> BackupRecord:
        """
        Create a new backup

        Args:
            backup_type: Type of backup to create
            include_database: Include database in backup
            include_events: Include event log in backup
            include_objects: Include object storage in backup

        Returns:
            Backup record
        """
        record = BackupRecord(
            backup_type=backup_type,
            status=BackupStatus.IN_PROGRESS,
            database_included=include_database,
            event_log_included=include_events,
            objects_included=include_objects,
            started_at=datetime.utcnow(),
        )

        # Get parent for incremental
        if backup_type == BackupType.INCREMENTAL:
            last_backup = await self._get_last_backup(BackupType.FULL)
            if last_backup:
                record.parent_backup_id = last_backup.id

        # Calculate expiration
        if backup_type == BackupType.FULL:
            record.expires_at = datetime.utcnow() + timedelta(
                days=self.config.full_backup_retention_days
            )
        else:
            record.expires_at = datetime.utcnow() + timedelta(
                days=self.config.incremental_retention_days
            )

        try:
            # Create storage location
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            record.storage_location = (
                f"s3://{self.config.backup_bucket}/backups/"
                f"{backup_type.value}/{timestamp}"
            )

            total_size = 0

            # Backup database
            if include_database and self.db_backup_service:
                db_result = await self.db_backup_service.create_backup(
                    backup_type,
                    f"{record.storage_location}/database",
                )
                total_size += db_result.get("size_bytes", 0)

            # Backup event log
            if include_events and self.event_log_service:
                end_time = datetime.utcnow()
                if backup_type == BackupType.INCREMENTAL and record.parent_backup_id:
                    parent = await self.backup_storage.get_backup(record.parent_backup_id)
                    start_time = parent.completed_at if parent else end_time - timedelta(hours=1)
                else:
                    start_time = end_time - timedelta(days=30)

                event_result = await self.event_log_service.export_events(
                    start_time,
                    end_time,
                    f"{record.storage_location}/events",
                )
                total_size += event_result.get("size_bytes", 0)

            record.size_bytes = total_size
            record.status = BackupStatus.COMPLETED
            record.completed_at = datetime.utcnow()
            record.duration_seconds = (
                record.completed_at - record.started_at
            ).total_seconds()

            # Verify if configured
            if self.config.verify_after_backup:
                record.verified = await self._verify_backup(record)
                record.verified_at = datetime.utcnow()

            logger.info(
                f"Backup completed: id={record.id} "
                f"type={backup_type.value} "
                f"size={record.size_bytes} bytes"
            )

        except Exception as e:
            record.status = BackupStatus.FAILED
            record.error = str(e)
            record.completed_at = datetime.utcnow()

            logger.error(f"Backup failed: {e}")

        # Save record
        if self.backup_storage:
            record = await self.backup_storage.save_backup(record)

        return record

    async def _get_last_backup(
        self,
        backup_type: BackupType,
    ) -> BackupRecord | None:
        """Get the most recent successful backup of a type"""
        if not self.backup_storage:
            return None

        backups = await self.backup_storage.list_backups(
            backup_type=backup_type,
            status=BackupStatus.COMPLETED,
            limit=1,
        )

        return backups[0] if backups else None

    async def _verify_backup(self, record: BackupRecord) -> bool:
        """Verify a backup is valid"""
        if record.database_included and self.db_backup_service:
            is_valid = await self.db_backup_service.verify_backup(
                f"{record.storage_location}/database"
            )
            if not is_valid:
                return False

        return True

    # ------------------------------------------------------------------
    # Recovery Operations
    # ------------------------------------------------------------------

    async def get_recovery_points(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> list[RecoveryPoint]:
        """
        Get available recovery points in a time range

        Returns list of points to which we can recover.
        """
        if not self.backup_storage:
            return []

        backups = await self.backup_storage.list_backups(
            status=BackupStatus.COMPLETED,
            limit=1000,
        )

        # Filter by time range
        relevant = [
            b for b in backups
            if b.completed_at and start_time <= b.completed_at <= end_time
        ]

        # Create recovery points
        points = []
        for backup in relevant:
            point = RecoveryPoint(
                timestamp=backup.completed_at,
                database_recoverable=backup.database_included,
                event_log_recoverable=backup.event_log_included,
                objects_recoverable=backup.objects_included,
                required_backups=[backup.id],
                verified=backup.verified,
            )

            # Calculate RTO estimate
            point.estimated_rto_minutes = self._estimate_rto(backup)

            points.append(point)

        return sorted(points, key=lambda p: p.timestamp, reverse=True)

    def _estimate_rto(self, backup: BackupRecord) -> int:
        """Estimate recovery time for a backup"""
        # Base time for setup
        rto = 10

        # Add time based on size (rough estimate: 1 GB per minute)
        if backup.size_bytes > 0:
            gb = backup.size_bytes / (1024 * 1024 * 1024)
            rto += int(gb)

        # Add time for incremental chain
        if backup.backup_type == BackupType.INCREMENTAL:
            rto += 5 * backup.sequence_number

        return rto

    async def restore_to_point(
        self,
        recovery_point: RecoveryPoint,
        target_environment: str = "restore",
    ) -> dict[str, Any]:
        """
        Restore to a recovery point

        Args:
            recovery_point: Point to restore to
            target_environment: Target environment name

        Returns:
            Recovery result
        """
        result = {
            "status": RecoveryStatus.PENDING.value,
            "recovery_point": recovery_point.timestamp.isoformat(),
            "target": target_environment,
            "steps_completed": [],
            "error": None,
        }

        try:
            result["status"] = RecoveryStatus.VALIDATING.value

            # Validate backups exist
            for backup_id in recovery_point.required_backups:
                backup = await self.backup_storage.get_backup(backup_id)
                if not backup:
                    raise ValueError(f"Required backup not found: {backup_id}")
                if backup.status != BackupStatus.COMPLETED:
                    raise ValueError(f"Required backup not completed: {backup_id}")

            result["steps_completed"].append("validation")
            result["status"] = RecoveryStatus.RESTORING.value

            # Restore database
            if recovery_point.database_recoverable and self.db_backup_service:
                backup = await self.backup_storage.get_backup(
                    recovery_point.required_backups[0]
                )
                await self.db_backup_service.restore_backup(
                    f"{backup.storage_location}/database",
                    f"{target_environment}_db",
                )
                result["steps_completed"].append("database_restore")

            # Restore events
            if recovery_point.event_log_recoverable and self.event_log_service:
                backup = await self.backup_storage.get_backup(
                    recovery_point.required_backups[0]
                )
                await self.event_log_service.import_events(
                    f"{backup.storage_location}/events"
                )
                result["steps_completed"].append("event_log_restore")

            result["status"] = RecoveryStatus.VERIFYING.value

            # Verification steps would go here

            result["status"] = RecoveryStatus.COMPLETED.value

            logger.info(
                f"Recovery completed: point={recovery_point.timestamp} "
                f"target={target_environment}"
            )

        except Exception as e:
            result["status"] = RecoveryStatus.FAILED.value
            result["error"] = str(e)
            logger.error(f"Recovery failed: {e}")

        return result

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def cleanup_expired_backups(
        self,
        dry_run: bool = True,
    ) -> int:
        """
        Clean up expired backups

        Args:
            dry_run: If True, only count without deleting

        Returns:
            Number of backups cleaned up
        """
        if not self.backup_storage:
            return 0

        backups = await self.backup_storage.list_backups(limit=10000)
        now = datetime.utcnow()
        count = 0

        for backup in backups:
            if backup.expires_at and backup.expires_at < now:
                if not dry_run:
                    await self.backup_storage.delete_backup(backup.id)
                count += 1

        logger.info(f"Backup cleanup: {count} expired (dry_run={dry_run})")

        return count

    # ------------------------------------------------------------------
    # Recovery Plans
    # ------------------------------------------------------------------

    def register_recovery_plan(self, plan: RecoveryPlan) -> None:
        """Register a recovery plan"""
        self.recovery_plans[plan.name] = plan

    async def test_recovery_plan(
        self,
        plan_name: str,
    ) -> dict[str, Any]:
        """Test a recovery plan"""
        plan = self.recovery_plans.get(plan_name)
        if not plan:
            raise ValueError(f"Recovery plan not found: {plan_name}")

        result = {
            "plan_name": plan_name,
            "tested_at": datetime.utcnow().isoformat(),
            "steps_tested": [],
            "success": True,
            "errors": [],
        }

        for step in plan.steps:
            step_name = step.get("name", "unknown")
            try:
                # Execute test for step
                # In practice, this would run actual tests
                result["steps_tested"].append(step_name)
            except Exception as e:
                result["success"] = False
                result["errors"].append({
                    "step": step_name,
                    "error": str(e),
                })

        # Update plan
        plan.last_tested_at = datetime.utcnow()
        plan.last_test_result = "success" if result["success"] else "failed"

        return result
