"""
Write-back Channel

Writes gate results back to Git providers:
- Check Run (GitHub)
- Status (GitHub/GitLab/Bitbucket)
- Comments (PR comments)

Handles:
- Provider API rate limits
- Retries with exponential backoff
- Idempotent writes
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol
from uuid import UUID

logger = logging.getLogger(__name__)


class CheckRunStatus(Enum):
    """Check run status values"""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CheckRunConclusion(Enum):
    """Check run conclusion values (when completed)"""
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"


class CommitStatus(Enum):
    """Commit status values"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


@dataclass
class CheckRunOutput:
    """Check run output annotation"""
    title: str = ""
    summary: str = ""
    text: str = ""
    annotations: list[dict[str, Any]] = field(default_factory=list)
    # Each annotation: {path, start_line, end_line, annotation_level, message, title}


@dataclass
class CheckRunResult:
    """Result of creating/updating a check run"""
    check_run_id: int = 0
    url: str = ""
    status: CheckRunStatus = CheckRunStatus.QUEUED
    conclusion: CheckRunConclusion | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class StatusResult:
    """Result of creating a commit status"""
    status_id: int = 0
    url: str = ""
    state: CommitStatus = CommitStatus.PENDING


@dataclass
class CommentResult:
    """Result of creating a comment"""
    comment_id: int = 0
    url: str = ""


class HTTPClient(Protocol):
    """HTTP client interface with retry support"""

    async def post(
        self,
        url: str,
        data: dict[str, Any] = None,
        headers: dict[str, str] = None,
    ) -> dict[str, Any]:
        ...

    async def patch(
        self,
        url: str,
        data: dict[str, Any] = None,
        headers: dict[str, str] = None,
    ) -> dict[str, Any]:
        ...


class TokenProvider(Protocol):
    """Interface for getting installation tokens"""

    async def get_token(self, org_id: UUID, installation_id: str) -> str:
        ...


@dataclass
class CheckRunWriter:
    """
    GitHub Check Run Writer

    Creates and updates check runs for gate results.
    This is the primary write-back mechanism for GitHub.
    """

    http_client: HTTPClient
    token_provider: TokenProvider

    # Retry configuration
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0

    # Idempotency tracking (in production, use Redis/DB)
    _created_checks: dict[str, int] = field(default_factory=dict)

    async def create_check_run(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        name: str,
        head_sha: str,
        status: CheckRunStatus = CheckRunStatus.QUEUED,
        external_id: str | None = None,
        details_url: str | None = None,
        output: CheckRunOutput | None = None,
    ) -> CheckRunResult:
        """
        Create a new check run

        Args:
            org_id: Organization ID (for token lookup)
            installation_id: GitHub App installation ID
            repo_full_name: Repository full name (owner/repo)
            name: Check run name (displayed in GitHub)
            head_sha: Commit SHA to attach the check to
            status: Initial status
            external_id: Our internal run ID (for idempotency)
            details_url: URL to detailed results
            output: Optional output (title, summary, annotations)

        Returns:
            CheckRunResult with created check info
        """
        # Idempotency check
        idempotency_key = f"{repo_full_name}:{head_sha}:{name}:{external_id or ''}"
        if idempotency_key in self._created_checks:
            logger.debug(f"Check run already exists: {idempotency_key}")
            return CheckRunResult(
                check_run_id=self._created_checks[idempotency_key],
                status=status,
            )

        token = await self.token_provider.get_token(org_id, installation_id)

        payload = {
            "name": name,
            "head_sha": head_sha,
            "status": status.value,
        }

        if external_id:
            payload["external_id"] = external_id

        if details_url:
            payload["details_url"] = details_url

        if status == CheckRunStatus.IN_PROGRESS:
            payload["started_at"] = datetime.utcnow().isoformat() + "Z"

        if output:
            payload["output"] = {
                "title": output.title,
                "summary": output.summary,
            }
            if output.text:
                payload["output"]["text"] = output.text
            if output.annotations:
                payload["output"]["annotations"] = output.annotations[:50]  # Max 50 per request

        # Create check run with retries
        response = await self._request_with_retry(
            method="post",
            url=f"https://api.github.com/repos/{repo_full_name}/check-runs",
            token=token,
            payload=payload,
        )

        check_run_id = response.get("id", 0)
        self._created_checks[idempotency_key] = check_run_id

        logger.info(
            f"Check run created: repo={repo_full_name} sha={head_sha[:8]} "
            f"name={name} id={check_run_id}"
        )

        return CheckRunResult(
            check_run_id=check_run_id,
            url=response.get("html_url", ""),
            status=status,
            started_at=datetime.utcnow() if status == CheckRunStatus.IN_PROGRESS else None,
        )

    async def update_check_run(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        check_run_id: int,
        status: CheckRunStatus | None = None,
        conclusion: CheckRunConclusion | None = None,
        output: CheckRunOutput | None = None,
        details_url: str | None = None,
    ) -> CheckRunResult:
        """
        Update an existing check run

        Args:
            org_id: Organization ID
            installation_id: GitHub App installation ID
            repo_full_name: Repository full name
            check_run_id: ID of check run to update
            status: New status (required if not completing)
            conclusion: Conclusion (required when completing)
            output: Updated output
            details_url: Updated details URL

        Returns:
            Updated CheckRunResult
        """
        token = await self.token_provider.get_token(org_id, installation_id)

        payload = {}

        if status:
            payload["status"] = status.value

        if conclusion:
            payload["status"] = CheckRunStatus.COMPLETED.value
            payload["conclusion"] = conclusion.value
            payload["completed_at"] = datetime.utcnow().isoformat() + "Z"

        if details_url:
            payload["details_url"] = details_url

        if output:
            payload["output"] = {
                "title": output.title,
                "summary": output.summary,
            }
            if output.text:
                payload["output"]["text"] = output.text
            if output.annotations:
                payload["output"]["annotations"] = output.annotations[:50]

        response = await self._request_with_retry(
            method="patch",
            url=f"https://api.github.com/repos/{repo_full_name}/check-runs/{check_run_id}",
            token=token,
            payload=payload,
        )

        logger.info(
            f"Check run updated: repo={repo_full_name} id={check_run_id} "
            f"status={status} conclusion={conclusion}"
        )

        return CheckRunResult(
            check_run_id=check_run_id,
            url=response.get("html_url", ""),
            status=status or CheckRunStatus.COMPLETED,
            conclusion=conclusion,
            completed_at=datetime.utcnow() if conclusion else None,
        )

    async def complete_check_run(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        check_run_id: int,
        conclusion: CheckRunConclusion,
        output: CheckRunOutput | None = None,
    ) -> CheckRunResult:
        """
        Complete a check run with a conclusion

        Convenience method for the common case of completing a run.
        """
        return await self.update_check_run(
            org_id=org_id,
            installation_id=installation_id,
            repo_full_name=repo_full_name,
            check_run_id=check_run_id,
            conclusion=conclusion,
            output=output,
        )

    async def add_annotations(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        check_run_id: int,
        annotations: list[dict[str, Any]],
        output_title: str = "Analysis Results",
        output_summary: str = "",
    ) -> None:
        """
        Add annotations to a check run

        GitHub limits to 50 annotations per request, so we batch.
        """
        batch_size = 50

        for i in range(0, len(annotations), batch_size):
            batch = annotations[i:i + batch_size]

            output = CheckRunOutput(
                title=output_title,
                summary=output_summary or f"Added {len(batch)} annotations",
                annotations=batch,
            )

            await self.update_check_run(
                org_id=org_id,
                installation_id=installation_id,
                repo_full_name=repo_full_name,
                check_run_id=check_run_id,
                output=output,
            )

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        token: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Make HTTP request with exponential backoff retry"""
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        last_error = None

        for attempt in range(self.max_retries):
            try:
                if method == "post":
                    return await self.http_client.post(url, data=payload, headers=headers)
                elif method == "patch":
                    return await self.http_client.patch(url, data=payload, headers=headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")

            except Exception as e:
                last_error = e
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)

                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}): "
                    f"{e}. Retrying in {delay}s"
                )

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(delay)

        if last_error is not None:
            raise last_error
        raise RuntimeError(
            f"Request failed without a captured exception after {self.max_retries} retries"
        )


@dataclass
class StatusWriter:
    """
    Commit Status Writer

    Creates commit statuses (older API, works on all providers).
    Use CheckRunWriter for GitHub when possible.
    """

    http_client: HTTPClient
    token_provider: TokenProvider
    max_retries: int = 3
    base_delay: float = 1.0

    async def create_status(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        sha: str,
        state: CommitStatus,
        context: str = "MachineNativeOps",
        description: str = "",
        target_url: str | None = None,
    ) -> StatusResult:
        """
        Create a commit status

        Args:
            org_id: Organization ID
            installation_id: Provider installation ID
            repo_full_name: Repository full name
            sha: Commit SHA
            state: Status state (pending, success, failure, error)
            context: Status context (shown as check name)
            description: Short description
            target_url: URL to detailed results

        Returns:
            StatusResult with created status info
        """
        token = await self.token_provider.get_token(org_id, installation_id)

        payload = {
            "state": state.value,
            "context": context,
            "description": description[:140],  # GitHub limit
        }

        if target_url:
            payload["target_url"] = target_url

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = await self.http_client.post(
            f"https://api.github.com/repos/{repo_full_name}/statuses/{sha}",
            data=payload,
            headers=headers,
        )

        logger.info(
            f"Status created: repo={repo_full_name} sha={sha[:8]} "
            f"context={context} state={state.value}"
        )

        return StatusResult(
            status_id=response.get("id", 0),
            url=response.get("url", ""),
            state=state,
        )


@dataclass
class CommentWriter:
    """
    PR Comment Writer

    Creates and updates comments on pull requests.
    """

    http_client: HTTPClient
    token_provider: TokenProvider
    max_retries: int = 3

    # Track created comments for updates
    _created_comments: dict[str, int] = field(default_factory=dict)

    async def create_or_update_comment(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        pr_number: int,
        body: str,
        comment_key: str = "",
    ) -> CommentResult:
        """
        Create or update a PR comment

        Uses a hidden marker in the comment to identify our comments.

        Args:
            org_id: Organization ID
            installation_id: Provider installation ID
            repo_full_name: Repository full name
            pr_number: Pull request number
            body: Comment body (markdown)
            comment_key: Unique key to identify this comment type

        Returns:
            CommentResult with comment info
        """
        token = await self.token_provider.get_token(org_id, installation_id)
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Add hidden marker for identification
        marker = f"<!-- mno-comment-{comment_key} -->"
        full_body = f"{marker}\n{body}"

        # Check for existing comment
        cache_key = f"{repo_full_name}:{pr_number}:{comment_key}"
        existing_id = self._created_comments.get(cache_key)

        if existing_id:
            # Update existing comment
            response = await self.http_client.patch(
                f"https://api.github.com/repos/{repo_full_name}/issues/comments/{existing_id}",
                data={"body": full_body},
                headers=headers,
            )

            logger.info(f"Comment updated: repo={repo_full_name} pr={pr_number} id={existing_id}")

            return CommentResult(
                comment_id=existing_id,
                url=response.get("html_url", ""),
            )

        # Create new comment
        response = await self.http_client.post(
            f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments",
            data={"body": full_body},
            headers=headers,
        )

        comment_id = response.get("id", 0)
        self._created_comments[cache_key] = comment_id

        logger.info(
            f"Comment created: repo={repo_full_name} pr={pr_number} id={comment_id}"
        )

        return CommentResult(
            comment_id=comment_id,
            url=response.get("html_url", ""),
        )

    async def delete_comment(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        comment_id: int,
    ) -> bool:
        """Delete a comment"""
        token = await self.token_provider.get_token(org_id, installation_id)
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            # Note: DELETE returns 204 No Content
            await self.http_client.post(
                f"https://api.github.com/repos/{repo_full_name}/issues/comments/{comment_id}",
                headers={**headers, "X-HTTP-Method-Override": "DELETE"},
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete comment: {e}")
            return False


# ------------------------------------------------------------------
# Gate Result Write-back Helper
# ------------------------------------------------------------------

@dataclass
class GateWriteback:
    """
    Convenience class for gate result write-back

    Combines CheckRunWriter and StatusWriter for gate operations.
    """

    check_run_writer: CheckRunWriter
    status_writer: StatusWriter
    comment_writer: CommentWriter

    async def report_gate_started(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        head_sha: str,
        run_id: str,
        details_url: str = "",
    ) -> CheckRunResult:
        """Report that gate analysis has started"""
        return await self.check_run_writer.create_check_run(
            org_id=org_id,
            installation_id=installation_id,
            repo_full_name=repo_full_name,
            name="MachineNativeOps Gate",
            head_sha=head_sha,
            status=CheckRunStatus.IN_PROGRESS,
            external_id=run_id,
            details_url=details_url,
            output=CheckRunOutput(
                title="Analysis in Progress",
                summary="Running security and quality checks...",
            ),
        )

    async def report_gate_success(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        check_run_id: int,
        summary: str = "",
        annotations: list[dict[str, Any]] | None = None,
    ) -> CheckRunResult:
        """Report gate passed"""
        output = CheckRunOutput(
            title="All Checks Passed",
            summary=summary or "No issues found.",
            annotations=annotations or [],
        )

        return await self.check_run_writer.complete_check_run(
            org_id=org_id,
            installation_id=installation_id,
            repo_full_name=repo_full_name,
            check_run_id=check_run_id,
            conclusion=CheckRunConclusion.SUCCESS,
            output=output,
        )

    async def report_gate_failure(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        check_run_id: int,
        summary: str = "",
        annotations: list[dict[str, Any]] | None = None,
    ) -> CheckRunResult:
        """Report gate failed"""
        output = CheckRunOutput(
            title="Checks Failed",
            summary=summary or "Issues were found that must be addressed.",
            annotations=annotations or [],
        )

        return await self.check_run_writer.complete_check_run(
            org_id=org_id,
            installation_id=installation_id,
            repo_full_name=repo_full_name,
            check_run_id=check_run_id,
            conclusion=CheckRunConclusion.FAILURE,
            output=output,
        )

    async def report_gate_neutral(
        self,
        org_id: UUID,
        installation_id: str,
        repo_full_name: str,
        check_run_id: int,
        summary: str = "",
    ) -> CheckRunResult:
        """Report gate neutral (warnings only, or degraded mode)"""
        output = CheckRunOutput(
            title="Checks Completed with Warnings",
            summary=summary or "Some warnings were found but no blocking issues.",
        )

        return await self.check_run_writer.complete_check_run(
            org_id=org_id,
            installation_id=installation_id,
            repo_full_name=repo_full_name,
            check_run_id=check_run_id,
            conclusion=CheckRunConclusion.NEUTRAL,
            output=output,
        )
