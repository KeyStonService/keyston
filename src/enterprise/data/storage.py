"""
Object Storage

Stores reports, artifacts, and raw results:
- Analysis reports
- Raw tool output
- Generated artifacts
- Exported data

Uses S3/MinIO/GCS compatible storage.
"""

import hashlib
import logging
import mimetypes
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class StorageClass(Enum):
    """Storage class for cost optimization"""
    STANDARD = "standard"              # Frequently accessed
    INFREQUENT = "infrequent"         # Less frequently accessed
    ARCHIVE = "archive"               # Rarely accessed, archival
    GLACIER = "glacier"               # Long-term archival


class ContentType(Enum):
    """Common content types"""
    JSON = "application/json"
    HTML = "text/html"
    PDF = "application/pdf"
    TEXT = "text/plain"
    GZIP = "application/gzip"
    TAR_GZ = "application/x-tar+gzip"
    ZIP = "application/zip"
    BINARY = "application/octet-stream"


@dataclass
class StorageLocation:
    """
    Storage location reference

    Defines where an object is stored.
    """
    bucket: str = ""
    key: str = ""
    region: str | None = None

    @property
    def uri(self) -> str:
        """S3-style URI"""
        return f"s3://{self.bucket}/{self.key}"

    @property
    def path(self) -> str:
        """Full path"""
        return f"{self.bucket}/{self.key}"


@dataclass
class StorageObject:
    """
    Stored object metadata

    Represents an object in storage without the actual content.
    """
    id: UUID = field(default_factory=uuid4)

    # Location
    location: StorageLocation = field(default_factory=StorageLocation)

    # Tenant isolation
    org_id: UUID = field(default_factory=uuid4)

    # Object metadata
    filename: str = ""
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    checksum: str = ""  # MD5 or SHA256
    checksum_algorithm: str = "sha256"

    # Classification
    object_type: str = ""  # report, artifact, log, export
    run_id: UUID | None = None
    repo_id: UUID | None = None

    # Storage settings
    storage_class: StorageClass = StorageClass.STANDARD

    # Versioning
    version_id: str | None = None
    is_latest: bool = True

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    last_accessed_at: datetime | None = None

    # Tags
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "bucket": self.location.bucket,
            "key": self.location.key,
            "org_id": str(self.org_id),
            "filename": self.filename,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "object_type": self.object_type,
            "run_id": str(self.run_id) if self.run_id else None,
            "repo_id": str(self.repo_id) if self.repo_id else None,
            "storage_class": self.storage_class.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "tags": self.tags,
        }


class StorageBackend(Protocol):
    """Interface for object storage backend"""

    async def put_object(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
        storage_class: str = "STANDARD",
    ) -> dict[str, Any]:
        """Upload an object"""
        ...

    async def get_object(
        self,
        bucket: str,
        key: str,
    ) -> bytes:
        """Download an object"""
        ...

    async def delete_object(
        self,
        bucket: str,
        key: str,
    ) -> bool:
        """Delete an object"""
        ...

    async def head_object(
        self,
        bucket: str,
        key: str,
    ) -> dict[str, Any] | None:
        """Get object metadata"""
        ...

    async def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[dict[str, Any]]:
        """List objects with prefix"""
        ...

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for temporary access"""
        ...

    async def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
    ) -> dict[str, Any]:
        """Copy an object"""
        ...


class ObjectMetadataStore(Protocol):
    """Interface for storing object metadata"""

    async def save(self, obj: StorageObject) -> StorageObject:
        ...

    async def get(self, obj_id: UUID) -> StorageObject | None:
        ...

    async def get_by_location(
        self, bucket: str, key: str
    ) -> StorageObject | None:
        ...

    async def list_by_org(
        self,
        org_id: UUID,
        object_type: str | None = None,
        limit: int = 100,
    ) -> list[StorageObject]:
        ...

    async def list_by_run(
        self,
        run_id: UUID,
    ) -> list[StorageObject]:
        ...

    async def delete(self, obj_id: UUID) -> bool:
        ...


@dataclass
class ObjectStorage:
    """
    Object Storage Manager

    Manages object storage with:
    - Tenant isolation (org_id in path)
    - Metadata tracking
    - Presigned URLs for secure access
    - Lifecycle management
    """

    backend: StorageBackend
    metadata_store: ObjectMetadataStore | None = None

    # Configuration
    default_bucket: str = "mno-artifacts"
    report_bucket: str = "mno-reports"

    # Path templates
    artifact_path_template: str = "orgs/{org_id}/runs/{run_id}/artifacts/{filename}"
    report_path_template: str = "orgs/{org_id}/reports/{year}/{month}/{filename}"
    export_path_template: str = "orgs/{org_id}/exports/{filename}"

    # Lifecycle
    default_retention_days: int = 90
    report_retention_days: int = 365

    # ------------------------------------------------------------------
    # Upload Operations
    # ------------------------------------------------------------------

    async def store_artifact(
        self,
        org_id: UUID,
        run_id: UUID,
        filename: str,
        data: bytes,
        content_type: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> StorageObject:
        """
        Store a run artifact

        Args:
            org_id: Organization ID
            run_id: Run ID
            filename: Filename for the artifact
            data: Artifact data
            content_type: MIME type (auto-detected if not provided)
            tags: Optional tags

        Returns:
            Stored object metadata
        """
        # Auto-detect content type
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        # Build key
        key = self.artifact_path_template.format(
            org_id=org_id,
            run_id=run_id,
            filename=filename,
        )

        # Calculate checksum
        checksum = hashlib.sha256(data).hexdigest()

        # Upload to backend
        result = await self.backend.put_object(
            bucket=self.default_bucket,
            key=key,
            data=data,
            content_type=content_type,
            metadata={
                "org-id": str(org_id),
                "run-id": str(run_id),
                "checksum": checksum,
            },
        )

        # Create metadata object
        obj = StorageObject(
            location=StorageLocation(bucket=self.default_bucket, key=key),
            org_id=org_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            checksum=checksum,
            object_type="artifact",
            run_id=run_id,
            version_id=result.get("VersionId"),
            expires_at=datetime.utcnow() + timedelta(days=self.default_retention_days),
            tags=tags or {},
        )

        # Store metadata
        if self.metadata_store:
            obj = await self.metadata_store.save(obj)

        logger.info(f"Artifact stored: {key} ({len(data)} bytes)")

        return obj

    async def store_report(
        self,
        org_id: UUID,
        filename: str,
        data: bytes,
        run_id: UUID | None = None,
        repo_id: UUID | None = None,
        content_type: str = "application/json",
        tags: dict[str, str] | None = None,
    ) -> StorageObject:
        """
        Store a report

        Reports are stored in a separate bucket with longer retention.
        """
        now = datetime.utcnow()

        key = self.report_path_template.format(
            org_id=org_id,
            year=now.year,
            month=f"{now.month:02d}",
            filename=filename,
        )

        checksum = hashlib.sha256(data).hexdigest()

        await self.backend.put_object(
            bucket=self.report_bucket,
            key=key,
            data=data,
            content_type=content_type,
            metadata={
                "org-id": str(org_id),
                "run-id": str(run_id) if run_id else "",
                "repo-id": str(repo_id) if repo_id else "",
            },
        )

        obj = StorageObject(
            location=StorageLocation(bucket=self.report_bucket, key=key),
            org_id=org_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            checksum=checksum,
            object_type="report",
            run_id=run_id,
            repo_id=repo_id,
            storage_class=StorageClass.STANDARD,
            expires_at=datetime.utcnow() + timedelta(days=self.report_retention_days),
            tags=tags or {},
        )

        if self.metadata_store:
            obj = await self.metadata_store.save(obj)

        logger.info(f"Report stored: {key}")

        return obj

    async def store_export(
        self,
        org_id: UUID,
        filename: str,
        data: bytes,
        content_type: str = "application/json",
        expires_in_days: int = 7,
    ) -> StorageObject:
        """
        Store an export file

        Exports have shorter retention and presigned URL access.
        """
        key = self.export_path_template.format(
            org_id=org_id,
            filename=filename,
        )

        checksum = hashlib.sha256(data).hexdigest()

        await self.backend.put_object(
            bucket=self.default_bucket,
            key=key,
            data=data,
            content_type=content_type,
        )

        obj = StorageObject(
            location=StorageLocation(bucket=self.default_bucket, key=key),
            org_id=org_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            checksum=checksum,
            object_type="export",
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
        )

        if self.metadata_store:
            obj = await self.metadata_store.save(obj)

        return obj

    # ------------------------------------------------------------------
    # Retrieval Operations
    # ------------------------------------------------------------------

    async def get_object(
        self,
        location: StorageLocation,
    ) -> bytes | None:
        """Get object content by location"""
        try:
            return await self.backend.get_object(location.bucket, location.key)
        except Exception as e:
            logger.error(f"Failed to get object {location.uri}: {e}")
            return None

    async def get_object_by_id(
        self,
        obj_id: UUID,
    ) -> tuple[StorageObject, bytes] | None:
        """Get object by ID (metadata + content)"""
        if not self.metadata_store:
            raise ValueError("Metadata store not configured")

        obj = await self.metadata_store.get(obj_id)
        if not obj:
            return None

        data = await self.get_object(obj.location)
        if not data:
            return None

        # Update last accessed
        obj.last_accessed_at = datetime.utcnow()
        await self.metadata_store.save(obj)

        return obj, data

    async def get_presigned_url(
        self,
        location: StorageLocation,
        expires_in: int = 3600,
    ) -> str:
        """
        Get a presigned URL for temporary access

        Use this to provide secure, time-limited download links.
        """
        return await self.backend.generate_presigned_url(
            location.bucket,
            location.key,
            expires_in,
        )

    async def get_download_url(
        self,
        obj_id: UUID,
        expires_in: int = 3600,
    ) -> str | None:
        """Get download URL for an object by ID"""
        if not self.metadata_store:
            raise ValueError("Metadata store not configured")

        obj = await self.metadata_store.get(obj_id)
        if not obj:
            return None

        return await self.get_presigned_url(obj.location, expires_in)

    # ------------------------------------------------------------------
    # Listing Operations
    # ------------------------------------------------------------------

    async def list_artifacts(
        self,
        org_id: UUID,
        run_id: UUID,
    ) -> list[StorageObject]:
        """List artifacts for a run"""
        if self.metadata_store:
            return await self.metadata_store.list_by_run(run_id)

        # Fallback to backend listing
        prefix = f"orgs/{org_id}/runs/{run_id}/artifacts/"
        items = await self.backend.list_objects(self.default_bucket, prefix)

        return [
            StorageObject(
                location=StorageLocation(bucket=self.default_bucket, key=item["Key"]),
                org_id=org_id,
                filename=item["Key"].split("/")[-1],
                size_bytes=item.get("Size", 0),
            )
            for item in items
        ]

    async def list_reports(
        self,
        org_id: UUID,
        limit: int = 100,
    ) -> list[StorageObject]:
        """List reports for an organization"""
        if self.metadata_store:
            return await self.metadata_store.list_by_org(org_id, "report", limit)

        prefix = f"orgs/{org_id}/reports/"
        items = await self.backend.list_objects(self.report_bucket, prefix, limit)

        return [
            StorageObject(
                location=StorageLocation(bucket=self.report_bucket, key=item["Key"]),
                org_id=org_id,
                filename=item["Key"].split("/")[-1],
                size_bytes=item.get("Size", 0),
            )
            for item in items
        ]

    # ------------------------------------------------------------------
    # Deletion Operations
    # ------------------------------------------------------------------

    async def delete_object(
        self,
        obj_id: UUID,
    ) -> bool:
        """Delete an object by ID"""
        if not self.metadata_store:
            raise ValueError("Metadata store not configured")

        obj = await self.metadata_store.get(obj_id)
        if not obj:
            return False

        # Delete from backend
        await self.backend.delete_object(obj.location.bucket, obj.location.key)

        # Delete metadata
        await self.metadata_store.delete(obj_id)

        logger.info(f"Object deleted: {obj.location.uri}")

        return True

    async def delete_run_artifacts(
        self,
        org_id: UUID,
        run_id: UUID,
    ) -> int:
        """Delete all artifacts for a run"""
        artifacts = await self.list_artifacts(org_id, run_id)
        count = 0

        for artifact in artifacts:
            await self.backend.delete_object(
                artifact.location.bucket,
                artifact.location.key,
            )
            if self.metadata_store:
                await self.metadata_store.delete(artifact.id)
            count += 1

        logger.info(f"Deleted {count} artifacts for run {run_id}")

        return count

    # ------------------------------------------------------------------
    # Lifecycle Management
    # ------------------------------------------------------------------

    async def cleanup_expired(
        self,
        org_id: UUID | None = None,
        dry_run: bool = True,
    ) -> int:
        """
        Clean up expired objects

        Args:
            org_id: Optional org to limit cleanup
            dry_run: If True, only count without deleting

        Returns:
            Number of objects cleaned up
        """
        if not self.metadata_store:
            logger.warning("Cannot cleanup without metadata store")
            return 0

        # Get all objects for org (or all)
        if org_id:
            objects = await self.metadata_store.list_by_org(org_id, limit=10000)
        else:
            objects = []  # Would need different query

        now = datetime.utcnow()
        count = 0

        for obj in objects:
            if obj.expires_at and obj.expires_at < now:
                if not dry_run:
                    await self.delete_object(obj.id)
                count += 1

        logger.info(f"Expired object cleanup: {count} objects (dry_run={dry_run})")

        return count
