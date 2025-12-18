"""
Fix Status Tracker

Track fix attempts and their results across CI/CD pipelines.
Provides metrics and insights on fix effectiveness.

Reference: Tracking fix status and auto-closing issues [2]
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .auto_fix_engine import FixAttempt, FixStrategy


class FixStatus(Enum):
    """Status of a fix"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PR_CREATED = "pr_created"
    PR_MERGED = "pr_merged"
    VERIFIED = "verified"
    FAILED = "failed"
    REVERTED = "reverted"


@dataclass
class FixMetrics:
    """Metrics for fix tracking"""
    total_errors: int = 0
    total_fix_attempts: int = 0
    successful_fixes: int = 0
    failed_fixes: int = 0
    auto_fixed: int = 0
    manual_fixed: int = 0
    avg_time_to_fix_minutes: float = 0.0
    fix_rate: float = 0.0
    reoccurrence_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_errors': self.total_errors,
            'total_fix_attempts': self.total_fix_attempts,
            'successful_fixes': self.successful_fixes,
            'failed_fixes': self.failed_fixes,
            'auto_fixed': self.auto_fixed,
            'manual_fixed': self.manual_fixed,
            'avg_time_to_fix_minutes': round(self.avg_time_to_fix_minutes, 2),
            'fix_rate': round(self.fix_rate * 100, 2),
            'reoccurrence_rate': round(self.reoccurrence_rate * 100, 2),
        }


@dataclass
class FixHistory:
    """History entry for a fix"""
    history_id: str
    error_id: str
    status: FixStatus
    details: str
    pr_number: Optional[int] = None
    commit_sha: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'history_id': self.history_id,
            'error_id': self.error_id,
            'status': self.status.value,
            'details': self.details,
            'pr_number': self.pr_number,
            'commit_sha': self.commit_sha,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class TrackedFix:
    """A tracked fix for an error"""
    error_id: str
    error_category: str
    status: FixStatus
    created_at: datetime
    updated_at: datetime
    attempts: List[FixAttempt] = field(default_factory=list)
    history: List[FixHistory] = field(default_factory=list)
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    issue_number: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    verification_status: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'error_id': self.error_id,
            'error_category': self.error_category,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'attempts_count': len(self.attempts),
            'history_count': len(self.history),
            'pr_number': self.pr_number,
            'pr_url': self.pr_url,
            'issue_number': self.issue_number,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'verification_status': self.verification_status,
        }


class FixStatusTracker:
    """
    Fix Status Tracker
    
    Track fix attempts and their results for CI/CD errors.
    
    Features:
    - Track fix lifecycle (pending → in_progress → resolved)
    - Link fixes to PRs and issues
    - Calculate fix metrics and effectiveness
    - Detect reoccurring errors
    """
    
    def __init__(self):
        """Initialize the Fix Status Tracker"""
        self._tracked_fixes: Dict[str, TrackedFix] = {}
        self._history_counter = 0
    
    def _generate_history_id(self) -> str:
        """Generate unique history ID"""
        self._history_counter += 1
        return f"HIST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._history_counter:04d}"
    
    def start_tracking(
        self,
        error_id: str,
        error_category: str,
        issue_number: Optional[int] = None
    ) -> TrackedFix:
        """
        Start tracking a fix for an error
        
        Args:
            error_id: The error ID
            error_category: Category of the error
            issue_number: Associated GitHub issue number
            
        Returns:
            The tracked fix record
        """
        now = datetime.now()
        
        tracked = TrackedFix(
            error_id=error_id,
            error_category=error_category,
            status=FixStatus.PENDING,
            created_at=now,
            updated_at=now,
            issue_number=issue_number,
        )
        
        # Add initial history entry
        tracked.history.append(FixHistory(
            history_id=self._generate_history_id(),
            error_id=error_id,
            status=FixStatus.PENDING,
            details="Fix tracking started",
        ))
        
        self._tracked_fixes[error_id] = tracked
        return tracked
    
    def update_status(
        self,
        error_id: str,
        status: FixStatus,
        details: str = "",
        pr_number: Optional[int] = None,
        commit_sha: Optional[str] = None
    ) -> Optional[TrackedFix]:
        """
        Update the status of a tracked fix
        
        Args:
            error_id: The error ID
            status: New status
            details: Details about the status change
            pr_number: Associated PR number (if applicable)
            commit_sha: Commit SHA (if applicable)
            
        Returns:
            Updated TrackedFix or None if not found
        """
        if error_id not in self._tracked_fixes:
            return None
        
        tracked = self._tracked_fixes[error_id]
        tracked.status = status
        tracked.updated_at = datetime.now()
        
        if pr_number:
            tracked.pr_number = pr_number
        
        # Add history entry
        tracked.history.append(FixHistory(
            history_id=self._generate_history_id(),
            error_id=error_id,
            status=status,
            details=details,
            pr_number=pr_number,
            commit_sha=commit_sha,
        ))
        
        # Mark as resolved if appropriate
        if status in {FixStatus.VERIFIED, FixStatus.PR_MERGED}:
            tracked.resolved_at = datetime.now()
        
        return tracked
    
    def add_attempt(
        self,
        error_id: str,
        attempt: FixAttempt
    ) -> Optional[TrackedFix]:
        """
        Add a fix attempt to tracking
        
        Args:
            error_id: The error ID
            attempt: The fix attempt
            
        Returns:
            Updated TrackedFix or None if not found
        """
        if error_id not in self._tracked_fixes:
            return None
        
        tracked = self._tracked_fixes[error_id]
        tracked.attempts.append(attempt)
        tracked.updated_at = datetime.now()
        tracked.status = FixStatus.IN_PROGRESS
        
        # Add history entry
        tracked.history.append(FixHistory(
            history_id=self._generate_history_id(),
            error_id=error_id,
            status=FixStatus.IN_PROGRESS,
            details=f"Fix attempt: {attempt.fix_description}",
        ))
        
        return tracked
    
    def link_pr(
        self,
        error_id: str,
        pr_number: int,
        pr_url: str
    ) -> Optional[TrackedFix]:
        """
        Link a PR to a tracked fix
        
        Args:
            error_id: The error ID
            pr_number: PR number
            pr_url: PR URL
            
        Returns:
            Updated TrackedFix or None if not found
        """
        if error_id not in self._tracked_fixes:
            return None
        
        tracked = self._tracked_fixes[error_id]
        tracked.pr_number = pr_number
        tracked.pr_url = pr_url
        tracked.status = FixStatus.PR_CREATED
        tracked.updated_at = datetime.now()
        
        # Add history entry
        tracked.history.append(FixHistory(
            history_id=self._generate_history_id(),
            error_id=error_id,
            status=FixStatus.PR_CREATED,
            details=f"Fix PR created: #{pr_number}",
            pr_number=pr_number,
        ))
        
        return tracked
    
    def mark_pr_merged(
        self,
        error_id: str,
        commit_sha: str,
        merged_by: Optional[str] = None
    ) -> Optional[TrackedFix]:
        """
        Mark a fix PR as merged
        
        Args:
            error_id: The error ID
            commit_sha: Merge commit SHA
            merged_by: User who merged
            
        Returns:
            Updated TrackedFix or None if not found
        """
        if error_id not in self._tracked_fixes:
            return None
        
        tracked = self._tracked_fixes[error_id]
        tracked.status = FixStatus.PR_MERGED
        tracked.resolved_at = datetime.now()
        tracked.resolved_by = merged_by
        tracked.updated_at = datetime.now()
        
        # Add history entry
        tracked.history.append(FixHistory(
            history_id=self._generate_history_id(),
            error_id=error_id,
            status=FixStatus.PR_MERGED,
            details=f"Fix PR merged by {merged_by or 'unknown'}",
            pr_number=tracked.pr_number,
            commit_sha=commit_sha,
        ))
        
        return tracked
    
    def mark_verified(
        self,
        error_id: str,
        verification_details: str = "CI passed after fix"
    ) -> Optional[TrackedFix]:
        """
        Mark a fix as verified (CI passed after fix)
        
        Args:
            error_id: The error ID
            verification_details: Details about verification
            
        Returns:
            Updated TrackedFix or None if not found
        """
        if error_id not in self._tracked_fixes:
            return None
        
        tracked = self._tracked_fixes[error_id]
        tracked.status = FixStatus.VERIFIED
        tracked.verification_status = "verified"
        tracked.updated_at = datetime.now()
        
        if not tracked.resolved_at:
            tracked.resolved_at = datetime.now()
        
        # Add history entry
        tracked.history.append(FixHistory(
            history_id=self._generate_history_id(),
            error_id=error_id,
            status=FixStatus.VERIFIED,
            details=verification_details,
        ))
        
        return tracked
    
    def mark_failed(
        self,
        error_id: str,
        failure_reason: str
    ) -> Optional[TrackedFix]:
        """
        Mark a fix as failed
        
        Args:
            error_id: The error ID
            failure_reason: Reason for failure
            
        Returns:
            Updated TrackedFix or None if not found
        """
        if error_id not in self._tracked_fixes:
            return None
        
        tracked = self._tracked_fixes[error_id]
        tracked.status = FixStatus.FAILED
        tracked.verification_status = "failed"
        tracked.updated_at = datetime.now()
        
        # Add history entry
        tracked.history.append(FixHistory(
            history_id=self._generate_history_id(),
            error_id=error_id,
            status=FixStatus.FAILED,
            details=f"Fix failed: {failure_reason}",
        ))
        
        return tracked
    
    def get_tracked_fix(self, error_id: str) -> Optional[TrackedFix]:
        """Get a tracked fix by error ID"""
        return self._tracked_fixes.get(error_id)
    
    def get_fixes_by_status(self, status: FixStatus) -> List[TrackedFix]:
        """Get all fixes with a specific status"""
        return [f for f in self._tracked_fixes.values() if f.status == status]
    
    def get_pending_fixes(self) -> List[TrackedFix]:
        """Get all pending fixes"""
        pending_statuses = {FixStatus.PENDING, FixStatus.IN_PROGRESS, FixStatus.PR_CREATED}
        return [f for f in self._tracked_fixes.values() if f.status in pending_statuses]
    
    def get_resolved_fixes(self) -> List[TrackedFix]:
        """Get all resolved fixes"""
        resolved_statuses = {FixStatus.VERIFIED, FixStatus.PR_MERGED}
        return [f for f in self._tracked_fixes.values() if f.status in resolved_statuses]
    
    def calculate_metrics(self, since: Optional[datetime] = None) -> FixMetrics:
        """
        Calculate fix metrics
        
        Args:
            since: Only include fixes since this time
            
        Returns:
            FixMetrics with calculated values
        """
        fixes = list(self._tracked_fixes.values())
        
        if since:
            fixes = [f for f in fixes if f.created_at >= since]
        
        if not fixes:
            return FixMetrics()
        
        total = len(fixes)
        successful = len([f for f in fixes if f.status in {FixStatus.VERIFIED, FixStatus.PR_MERGED}])
        failed = len([f for f in fixes if f.status == FixStatus.FAILED])
        
        # Calculate auto vs manual
        auto_fixed = 0
        manual_fixed = 0
        for fix in fixes:
            if fix.status in {FixStatus.VERIFIED, FixStatus.PR_MERGED}:
                if any(a.strategy == FixStrategy.AUTO_FIX for a in fix.attempts):
                    auto_fixed += 1
                else:
                    manual_fixed += 1
        
        # Calculate average time to fix
        fix_times = []
        for fix in fixes:
            if fix.resolved_at:
                fix_time = (fix.resolved_at - fix.created_at).total_seconds() / 60
                fix_times.append(fix_time)
        
        avg_time = sum(fix_times) / len(fix_times) if fix_times else 0
        
        # Calculate total attempts
        total_attempts = sum(len(f.attempts) for f in fixes)
        
        return FixMetrics(
            total_errors=total,
            total_fix_attempts=total_attempts,
            successful_fixes=successful,
            failed_fixes=failed,
            auto_fixed=auto_fixed,
            manual_fixed=manual_fixed,
            avg_time_to_fix_minutes=avg_time,
            fix_rate=successful / total if total > 0 else 0,
            reoccurrence_rate=0,  # Would need more data to calculate
        )
    
    def get_fix_history(self, error_id: str) -> List[FixHistory]:
        """Get the full history of a fix"""
        tracked = self._tracked_fixes.get(error_id)
        return tracked.history if tracked else []
    
    def generate_summary_report(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a summary report of fix tracking
        
        Args:
            since: Only include fixes since this time
            
        Returns:
            Dictionary with summary report
        """
        metrics = self.calculate_metrics(since)
        pending = self.get_pending_fixes()
        resolved = self.get_resolved_fixes()
        
        return {
            'generated_at': datetime.now().isoformat(),
            'period_start': since.isoformat() if since else None,
            'metrics': metrics.to_dict(),
            'pending_count': len(pending),
            'resolved_count': len(resolved),
            'pending_errors': [f.error_id for f in pending],
            'recent_resolutions': [
                {
                    'error_id': f.error_id,
                    'resolved_at': f.resolved_at.isoformat() if f.resolved_at else None,
                    'pr_number': f.pr_number,
                }
                for f in resolved[-5:]
            ],
        }
