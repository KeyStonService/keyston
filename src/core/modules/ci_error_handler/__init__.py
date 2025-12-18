"""
Phase 12: GitHub Issues CI Error Auto-Handler System

This module provides automatic CI error detection, analysis, and resolution
through GitHub Issues integration.

Core Components:
- CIErrorAnalyzer: Parse and analyze CI/CD error logs
- IssueManager: Create and manage GitHub issues for CI errors
- AutoFixEngine: Generate and apply AI-driven fixes
- FixStatusTracker: Track fix attempts and results
"""

from .auto_fix_engine import (
    AutoFixEngine,
    FixAttempt,
    FixResult,
    FixStrategy,
)
from .ci_error_analyzer import (
    CIError,
    CIErrorAnalyzer,
    ErrorCategory,
    ErrorPattern,
    ErrorSeverity,
)
from .fix_status_tracker import (
    FixHistory,
    FixMetrics,
    FixStatus,
    FixStatusTracker,
)
from .issue_manager import (
    CIIssue,
    IssueManager,
    IssueStatus,
    IssueTemplate,
)

__all__ = [
    # CI Error Analyzer
    'CIErrorAnalyzer',
    'ErrorCategory',
    'ErrorSeverity',
    'CIError',
    'ErrorPattern',
    # Issue Manager
    'IssueManager',
    'IssueTemplate',
    'IssueStatus',
    'CIIssue',
    # Auto Fix Engine
    'AutoFixEngine',
    'FixStrategy',
    'FixResult',
    'FixAttempt',
    # Fix Status Tracker
    'FixStatusTracker',
    'FixStatus',
    'FixMetrics',
    'FixHistory',
]
