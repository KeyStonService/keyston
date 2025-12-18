"""
Issue Manager

Create and manage GitHub issues for CI/CD errors.
Provides structured issue templates and status tracking.

Reference: IssueOps for automating CI/CD [8]
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from .ci_error_analyzer import CIError, ErrorCategory, ErrorSeverity


class IssueStatus(Enum):
    """Status of a CI issue"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FIX_ATTEMPTED = "fix_attempted"
    FIX_PENDING_REVIEW = "fix_pending_review"
    RESOLVED = "resolved"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"


@dataclass
class IssueTemplate:
    """Template for creating CI error issues"""
    template_id: str
    name: str
    title_format: str
    body_template: str
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    
    def render(self, error: CIError, workflow_info: Dict[str, Any]) -> Dict[str, Any]:
        """Render the template with error data"""
        title = self.title_format.format(
            category=error.category.value,
            severity=error.severity.value,
            title=error.title,
            file=error.file_path or "unknown",
        )
        
        body = self.body_template.format(
            error_id=error.error_id,
            category=error.category.value,
            severity=error.severity.value,
            title=error.title,
            message=error.message,
            file_path=error.file_path or "N/A",
            line_number=error.line_number or "N/A",
            code_snippet=error.code_snippet or "No code snippet available",
            stack_trace=error.stack_trace or "No stack trace available",
            fix_suggestion=error.fix_suggestion or "No automatic fix suggestion",
            auto_fixable="Yes ✅" if error.auto_fixable else "No ❌",
            workflow_name=workflow_info.get('workflow_name', 'Unknown'),
            workflow_run_id=workflow_info.get('run_id', 'Unknown'),
            workflow_url=workflow_info.get('url', '#'),
            branch=workflow_info.get('branch', 'Unknown'),
            commit_sha=workflow_info.get('commit_sha', 'Unknown'),
            timestamp=error.timestamp.isoformat(),
        )
        
        return {
            'title': title[:256],  # GitHub title limit
            'body': body,
            'labels': self.labels,
            'assignees': self.assignees,
        }


@dataclass
class CIIssue:
    """Represents a GitHub issue for a CI error"""
    issue_id: Optional[int]
    error: CIError
    status: IssueStatus
    workflow_info: Dict[str, Any]
    github_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    fix_attempts: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'issue_id': self.issue_id,
            'error': self.error.to_dict(),
            'status': self.status.value,
            'workflow_info': self.workflow_info,
            'github_url': self.github_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'fix_attempts_count': len(self.fix_attempts),
            'labels': self.labels,
            'assignees': self.assignees,
        }


class IssueManager:
    """
    Issue Manager
    
    Create and manage GitHub issues for CI/CD errors.
    
    Features:
    - Template-based issue creation
    - Label management based on error type
    - Status tracking
    - Duplicate detection
    """
    
    # Default issue template
    DEFAULT_TEMPLATE = IssueTemplate(
        template_id="default_ci_error",
        name="Default CI Error Template",
        title_format="[CI/{severity}] {title}",
        body_template="""## 🚨 CI/CD Error Detected

### Error Information

| Field | Value |
|-------|-------|
| **Error ID** | `{error_id}` |
| **Category** | {category} |
| **Severity** | {severity} |
| **Auto-Fixable** | {auto_fixable} |
| **File** | `{file_path}` |
| **Line** | {line_number} |

### Error Message

```
{message}
```

### Code Snippet

```
{code_snippet}
```

### Stack Trace

<details>
<summary>Click to expand stack trace</summary>

```
{stack_trace}
```

</details>

### Fix Suggestion

{fix_suggestion}

### Workflow Information

| Field | Value |
|-------|-------|
| **Workflow** | {workflow_name} |
| **Run ID** | [{workflow_run_id}]({workflow_url}) |
| **Branch** | `{branch}` |
| **Commit** | `{commit_sha}` |
| **Timestamp** | {timestamp} |

---

*This issue was automatically created by SynergyMesh CI Error Handler.*
""",
        labels=["ci-error", "automated"],
    )
    
    # Category to label mapping
    CATEGORY_LABELS = {
        ErrorCategory.BUILD_ERROR: ["build", "error"],
        ErrorCategory.TEST_FAILURE: ["test", "failure"],
        ErrorCategory.LINT_ERROR: ["lint", "code-quality"],
        ErrorCategory.TYPE_ERROR: ["type-error", "typescript"],
        ErrorCategory.DEPENDENCY_ERROR: ["dependencies"],
        ErrorCategory.SECURITY_SCAN: ["security", "vulnerability"],
        ErrorCategory.DEPLOYMENT_ERROR: ["deployment"],
        ErrorCategory.TIMEOUT: ["timeout", "performance"],
        ErrorCategory.RESOURCE_LIMIT: ["resources"],
        ErrorCategory.CONFIGURATION_ERROR: ["configuration"],
        ErrorCategory.NETWORK_ERROR: ["network"],
        ErrorCategory.PERMISSION_ERROR: ["permissions"],
        ErrorCategory.UNKNOWN: ["needs-triage"],
    }
    
    # Severity to label mapping
    SEVERITY_LABELS = {
        ErrorSeverity.LOW: "priority-low",
        ErrorSeverity.MEDIUM: "priority-medium",
        ErrorSeverity.HIGH: "priority-high",
        ErrorSeverity.CRITICAL: "priority-critical",
    }
    
    def __init__(self, custom_templates: Optional[Dict[str, IssueTemplate]] = None):
        """
        Initialize the Issue Manager
        
        Args:
            custom_templates: Custom templates by category
        """
        self.templates = {'default': self.DEFAULT_TEMPLATE}
        if custom_templates:
            self.templates.update(custom_templates)
        self._issues: Dict[str, CIIssue] = {}
    
    def create_issue_content(
        self,
        error: CIError,
        workflow_info: Dict[str, Any],
        template_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Create issue content from error
        
        Args:
            error: The CI error
            workflow_info: Information about the workflow run
            template_id: Template to use
            
        Returns:
            Dictionary with issue title, body, labels, etc.
        """
        template = self.templates.get(template_id, self.DEFAULT_TEMPLATE)
        content = template.render(error, workflow_info)
        
        # Add category and severity labels
        all_labels = list(content['labels'])
        all_labels.extend(self.CATEGORY_LABELS.get(error.category, []))
        all_labels.append(self.SEVERITY_LABELS.get(error.severity, ""))
        
        # Remove empty labels and duplicates
        content['labels'] = list(set(l for l in all_labels if l))
        
        return content
    
    def register_issue(
        self,
        error: CIError,
        workflow_info: Dict[str, Any],
        issue_id: Optional[int] = None,
        github_url: Optional[str] = None
    ) -> CIIssue:
        """
        Register a new CI issue
        
        Args:
            error: The CI error
            workflow_info: Information about the workflow run
            issue_id: GitHub issue ID (if created)
            github_url: GitHub issue URL
            
        Returns:
            The registered CIIssue
        """
        ci_issue = CIIssue(
            issue_id=issue_id,
            error=error,
            status=IssueStatus.OPEN,
            workflow_info=workflow_info,
            github_url=github_url,
            labels=self.CATEGORY_LABELS.get(error.category, []) + ["ci-error"],
        )
        
        self._issues[error.error_id] = ci_issue
        return ci_issue
    
    def update_status(self, error_id: str, status: IssueStatus) -> Optional[CIIssue]:
        """Update the status of an issue"""
        if error_id in self._issues:
            issue = self._issues[error_id]
            issue.status = status
            issue.updated_at = datetime.now()
            return issue
        return None
    
    def add_fix_attempt(
        self,
        error_id: str,
        fix_info: Dict[str, Any]
    ) -> Optional[CIIssue]:
        """Add a fix attempt to an issue"""
        if error_id in self._issues:
            issue = self._issues[error_id]
            fix_info['timestamp'] = datetime.now().isoformat()
            issue.fix_attempts.append(fix_info)
            issue.status = IssueStatus.FIX_ATTEMPTED
            issue.updated_at = datetime.now()
            return issue
        return None
    
    def add_comment(
        self,
        error_id: str,
        comment: str,
        author: str = "bot"
    ) -> Optional[CIIssue]:
        """Add a comment to an issue"""
        if error_id in self._issues:
            issue = self._issues[error_id]
            issue.comments.append({
                'text': comment,
                'author': author,
                'timestamp': datetime.now().isoformat(),
            })
            issue.updated_at = datetime.now()
            return issue
        return None
    
    def get_issue(self, error_id: str) -> Optional[CIIssue]:
        """Get an issue by error ID"""
        return self._issues.get(error_id)
    
    def get_issues_by_status(self, status: IssueStatus) -> List[CIIssue]:
        """Get all issues with a specific status"""
        return [i for i in self._issues.values() if i.status == status]
    
    def get_open_issues(self) -> List[CIIssue]:
        """Get all open issues"""
        open_statuses = {IssueStatus.OPEN, IssueStatus.IN_PROGRESS, IssueStatus.FIX_ATTEMPTED}
        return [i for i in self._issues.values() if i.status in open_statuses]
    
    def check_duplicate(self, error: CIError) -> Optional[CIIssue]:
        """
        Check if a similar issue already exists
        
        Args:
            error: The new error to check
            
        Returns:
            Existing issue if duplicate found, None otherwise
        """
        for issue in self._issues.values():
            # Same category, file, and similar message
            if (issue.error.category == error.category and
                issue.error.file_path == error.file_path and
                issue.status in {IssueStatus.OPEN, IssueStatus.IN_PROGRESS}):
                # Check message similarity (simple check)
                if (error.message[:100] in issue.error.message or
                    issue.error.message[:100] in error.message):
                    return issue
        return None
    
    def generate_close_comment(self, issue: CIIssue, resolution: str) -> str:
        """Generate a comment for closing an issue"""
        return f"""## 🎉 Issue Resolved

This issue has been resolved.

**Resolution:** {resolution}

**Fix Attempts:** {len(issue.fix_attempts)}

**Time to Resolution:** {(datetime.now() - issue.created_at).total_seconds() / 60:.1f} minutes

---

*Automatically closed by SynergyMesh CI Error Handler.*
"""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about managed issues"""
        total = len(self._issues)
        if total == 0:
            return {'total': 0}
        
        by_status = {}
        by_category = {}
        by_severity = {}
        
        for issue in self._issues.values():
            status = issue.status.value
            category = issue.error.category.value
            severity = issue.error.severity.value
            
            by_status[status] = by_status.get(status, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        resolved = by_status.get('resolved', 0) + by_status.get('closed', 0)
        
        return {
            'total': total,
            'by_status': by_status,
            'by_category': by_category,
            'by_severity': by_severity,
            'resolution_rate': resolved / total if total > 0 else 0,
        }
