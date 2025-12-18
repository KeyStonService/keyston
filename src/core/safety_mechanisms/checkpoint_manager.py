"""
Checkpoint Manager for HLP Executor Core

Implements checkpoint creation, compression, restoration, and cleanup
functionality with copy-on-write strategy and retention policies.

This module provides checkpoint management for safe state restoration
in case of failures during execution.
"""

import gzip
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CheckpointStatus(Enum):
    """Status of a checkpoint."""
    CREATED = "created"
    COMPRESSED = "compressed"
    RESTORED = "restored"
    EXPIRED = "expired"
    DELETED = "deleted"


@dataclass
class Checkpoint:
    """Represents a checkpoint for state restoration."""
    checkpoint_id: str
    execution_id: str
    phase_id: str
    timestamp: datetime
    state: dict[str, Any]
    status: CheckpointStatus = CheckpointStatus.CREATED
    compressed: bool = False
    compressed_size: int | None = None
    original_size: int = 0
    checksum: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate checksum after initialization."""
        if not self.checksum:
            state_str = json.dumps(self.state, sort_keys=True)
            self.checksum = hashlib.sha256(state_str.encode()).hexdigest()
            self.original_size = len(state_str.encode())


class CheckpointManager:
    """
    Manages checkpoint lifecycle including creation, compression, restoration,
    and cleanup with configurable retention policies.
    
    Features:
    - Copy-on-Write strategy for efficient storage
    - Automatic compression with gzip
    - Retention policy (keep last N checkpoints)
    - Checksum verification
    - Automatic cleanup of old checkpoints
    """
    
    def __init__(
        self,
        storage_path: Path | None = None,
        retention_count: int = 5,
        compression_enabled: bool = True,
        auto_cleanup: bool = True
    ):
        """
        Initialize the CheckpointManager.
        
        Args:
            storage_path: Path to store checkpoints (optional, uses in-memory if None)
            retention_count: Number of recent checkpoints to retain per execution
            compression_enabled: Whether to compress checkpoints automatically
            auto_cleanup: Whether to automatically clean up old checkpoints
        """
        self.storage_path = storage_path
        self.retention_count = retention_count
        self.compression_enabled = compression_enabled
        self.auto_cleanup = auto_cleanup
        
        # In-memory storage
        self._checkpoints: dict[str, list[Checkpoint]] = {}
        
        logger.info(
            "CheckpointManager initialized: storage_path=%s, retention=%d, compression=%s",
            storage_path,
            retention_count,
            compression_enabled
        )
    
    def create_checkpoint(
        self,
        execution_id: str,
        phase_id: str,
        state: dict[str, Any]
    ) -> str:
        """
        Create a checkpoint for the current state.
        
        Uses copy-on-write strategy to avoid unnecessary data duplication.
        Automatically compresses if enabled.
        
        Args:
            execution_id: Unique execution identifier
            phase_id: Phase identifier
            state: Current state to checkpoint (will be deep copied)
        
        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id(execution_id, phase_id)
        
        # Deep copy state using copy-on-write strategy
        state_copy = self._copy_on_write(state)
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            execution_id=execution_id,
            phase_id=phase_id,
            timestamp=datetime.utcnow(),
            state=state_copy,
            status=CheckpointStatus.CREATED
        )
        
        # Store checkpoint
        if execution_id not in self._checkpoints:
            self._checkpoints[execution_id] = []
        
        self._checkpoints[execution_id].append(checkpoint)
        
        # Compress if enabled
        if self.compression_enabled:
            self.compress_checkpoint(checkpoint_id)
        
        # Auto cleanup if enabled
        if self.auto_cleanup:
            self.cleanup_old_checkpoints(execution_id, self.retention_count)
        
        logger.info(
            "Created checkpoint: %s for execution=%s, phase=%s (size=%d bytes)",
            checkpoint_id,
            execution_id,
            phase_id,
            checkpoint.original_size
        )
        
        return checkpoint_id
    
    def list_checkpoints(self, execution_id: str) -> list[Checkpoint]:
        """
        List all checkpoints for an execution.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            List of checkpoints, sorted by timestamp (newest first)
        """
        checkpoints = self._checkpoints.get(execution_id, [])
        return sorted(checkpoints, key=lambda cp: cp.timestamp, reverse=True)
    
    def restore_checkpoint(self, checkpoint_id: str) -> dict[str, Any]:
        """
        Restore state from a checkpoint.
        
        Verifies checksum before restoration.
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            Restored state
        
        Raises:
            ValueError: If checkpoint not found or checksum verification fails
        """
        checkpoint = self._find_checkpoint_by_id(checkpoint_id)
        
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        # Decompress if compressed
        if checkpoint.compressed:
            self._decompress_checkpoint(checkpoint)
        
        # Verify checksum
        if not self._verify_checksum(checkpoint):
            raise ValueError(f"Checksum verification failed for checkpoint: {checkpoint_id}")
        
        # Update status
        checkpoint.status = CheckpointStatus.RESTORED
        
        logger.info(
            "Restored checkpoint: %s (execution=%s, phase=%s)",
            checkpoint_id,
            checkpoint.execution_id,
            checkpoint.phase_id
        )
        
        # Return deep copy to prevent modification
        return self._copy_on_write(checkpoint.state)
    
    def cleanup_old_checkpoints(
        self,
        execution_id: str,
        keep_count: int = 5
    ) -> int:
        """
        Clean up old checkpoints beyond the retention limit.
        
        Keeps the most recent checkpoints and removes older ones.
        
        Args:
            execution_id: Execution identifier
            keep_count: Number of recent checkpoints to keep
        
        Returns:
            Number of checkpoints removed
        """
        if execution_id not in self._checkpoints:
            return 0
        
        checkpoints = self._checkpoints[execution_id]
        if len(checkpoints) <= keep_count:
            return 0
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda cp: cp.timestamp, reverse=True)
        
        # Keep only the most recent
        to_keep = checkpoints[:keep_count]
        to_remove = checkpoints[keep_count:]
        
        # Update storage
        self._checkpoints[execution_id] = to_keep
        
        # Mark removed checkpoints as deleted
        for checkpoint in to_remove:
            checkpoint.status = CheckpointStatus.DELETED
        
        removed_count = len(to_remove)
        
        logger.info(
            "Cleaned up %d old checkpoints for execution=%s (kept %d)",
            removed_count,
            execution_id,
            keep_count
        )
        
        return removed_count
    
    def compress_checkpoint(self, checkpoint_id: str) -> int:
        """
        Compress a checkpoint using gzip.
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            Compressed size in bytes
        
        Raises:
            ValueError: If checkpoint not found
        """
        checkpoint = self._find_checkpoint_by_id(checkpoint_id)
        
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        if checkpoint.compressed:
            logger.debug("Checkpoint already compressed: %s", checkpoint_id)
            return checkpoint.compressed_size or 0
        
        # Serialize state
        state_json = json.dumps(checkpoint.state, sort_keys=True)
        state_bytes = state_json.encode('utf-8')
        
        # Compress
        compressed_data = gzip.compress(state_bytes, compresslevel=6)
        compressed_size = len(compressed_data)
        
        # Update checkpoint
        checkpoint.compressed = True
        checkpoint.compressed_size = compressed_size
        checkpoint.status = CheckpointStatus.COMPRESSED
        
        compression_ratio = (1 - compressed_size / checkpoint.original_size) * 100
        
        logger.info(
            "Compressed checkpoint: %s (original=%d bytes, compressed=%d bytes, ratio=%.1f%%)",
            checkpoint_id,
            checkpoint.original_size,
            compressed_size,
            compression_ratio
        )
        
        return compressed_size
    
    def get_checkpoint_stats(self, execution_id: str) -> dict[str, Any]:
        """
        Get statistics about checkpoints for an execution.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            Dictionary with checkpoint statistics
        """
        checkpoints = self._checkpoints.get(execution_id, [])
        
        if not checkpoints:
            return {
                "execution_id": execution_id,
                "total_checkpoints": 0,
                "total_size": 0,
                "compressed_size": 0
            }
        
        total_size = sum(cp.original_size for cp in checkpoints)
        compressed_size = sum(cp.compressed_size or 0 for cp in checkpoints if cp.compressed)
        compressed_count = sum(1 for cp in checkpoints if cp.compressed)
        
        return {
            "execution_id": execution_id,
            "total_checkpoints": len(checkpoints),
            "compressed_checkpoints": compressed_count,
            "total_size": total_size,
            "compressed_size": compressed_size,
            "compression_ratio": (1 - compressed_size / total_size) * 100 if total_size > 0 else 0,
            "oldest_checkpoint": min(cp.timestamp for cp in checkpoints),
            "newest_checkpoint": max(cp.timestamp for cp in checkpoints)
        }
    
    def _generate_checkpoint_id(self, execution_id: str, phase_id: str) -> str:
        """Generate a unique checkpoint ID."""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"cp_{execution_id}_{phase_id}_{timestamp}"
    
    def _copy_on_write(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Implement copy-on-write strategy for state.
        
        Creates a deep copy of the state to prevent shared references.
        """
        return json.loads(json.dumps(state))
    
    def _find_checkpoint_by_id(self, checkpoint_id: str) -> Checkpoint | None:
        """Find a checkpoint by its ID across all executions."""
        for checkpoints in self._checkpoints.values():
            for checkpoint in checkpoints:
                if checkpoint.checkpoint_id == checkpoint_id:
                    return checkpoint
        return None
    
    def _verify_checksum(self, checkpoint: Checkpoint) -> bool:
        """Verify the checksum of a checkpoint."""
        state_str = json.dumps(checkpoint.state, sort_keys=True)
        calculated_checksum = hashlib.sha256(state_str.encode()).hexdigest()
        return calculated_checksum == checkpoint.checksum
    
    def _decompress_checkpoint(self, checkpoint: Checkpoint) -> None:
        """
        Decompress a checkpoint state.
        
        In a production implementation with persistent storage, this would:
        1. Read compressed data from storage
        2. Decompress using gzip.decompress()
        3. Deserialize JSON back to state dict
        
        For in-memory storage, state is already decompressed.
        """
        # For in-memory storage, state is already available
        # In production with file storage, implement:
        # 1. Read compressed file from self.storage_path
        # 2. compressed_data = read_file(checkpoint_file)
        # 3. decompressed = gzip.decompress(compressed_data)
        # 4. checkpoint.state = json.loads(decompressed)
        logger.debug("Decompressing checkpoint: %s", checkpoint.checkpoint_id)
        checkpoint.compressed = False
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            True if deleted, False if not found
        """
        for execution_id, checkpoints in self._checkpoints.items():
            for i, checkpoint in enumerate(checkpoints):
                if checkpoint.checkpoint_id == checkpoint_id:
                    checkpoint.status = CheckpointStatus.DELETED
                    checkpoints.pop(i)
                    logger.info("Deleted checkpoint: %s", checkpoint_id)
                    return True
        return False
    
    def cleanup_expired_checkpoints(self, max_age_days: int = 7) -> int:
        """
        Clean up checkpoints older than the specified age.
        
        Args:
            max_age_days: Maximum age in days
        
        Returns:
            Number of checkpoints removed
        """
        cutoff_time = datetime.utcnow() - timedelta(days=max_age_days)
        removed_count = 0
        
        for execution_id, checkpoints in list(self._checkpoints.items()):
            expired = [cp for cp in checkpoints if cp.timestamp < cutoff_time]
            
            for checkpoint in expired:
                checkpoint.status = CheckpointStatus.EXPIRED
                checkpoints.remove(checkpoint)
                removed_count += 1
            
            # Remove empty execution entries
            if not checkpoints:
                del self._checkpoints[execution_id]
        
        logger.info(
            "Cleaned up %d expired checkpoints (older than %d days)",
            removed_count,
            max_age_days
        )
        
        return removed_count
