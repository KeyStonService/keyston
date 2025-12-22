#!/usr/bin/env python3
"""
GitHub Integration Service for Teams Orchestrator

Provides GitHub API integration for:
- Workflow triggering
- Pull request management
- Issue creation
- Status checks
- Artifact management
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import logging
import aiohttp

logger = logging.getLogger(__name__)


class GitHubEventType(str, Enum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    ISSUE_COMMENT = "issue_comment"
    WORKFLOW_DISPATCH = "workflow_dispatch"
    SCHEDULE = "schedule"
    CHECK_RUN = "check_run"
    CHECK_SUITE = "check_suite"
    DEPLOYMENT = "deployment"
    DEPLOYMENT_STATUS = "deployment_status"


class CheckStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CheckConclusion(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"


class GitHubIntegration:
    """GitHub API integration service."""

    def __init__(
        self,
        token: Optional[str] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
    ):
        self._token = token or os.getenv("GITHUB_TOKEN")
        self._owner = owner or os.getenv("GITHUB_REPOSITORY_OWNER", "")
        self._repo = repo or os.getenv("GITHUB_REPOSITORY", "").split("/")[-1]
        self._base_url = "https://api.github.com"
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            if self._token:
                headers["Authorization"] = f"Bearer {self._token}"
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make GitHub API request."""
        session = await self._get_session()
        url = f"{self._base_url}{endpoint}"

        try:
            async with session.request(method, url, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"GitHub API error: {response.status} - {error_text}")
                    return {"error": error_text, "status": response.status}
                if response.status == 204:
                    return {"success": True}
                return await response.json()
        except Exception as e:
            logger.error(f"GitHub API request failed: {e}")
            return {"error": str(e)}

    async def create_check_run(
        self,
        name: str,
        head_sha: str,
        status: CheckStatus = CheckStatus.QUEUED,
        conclusion: Optional[CheckConclusion] = None,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        details_url: Optional[str] = None,
        annotations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a check run for a commit."""
        endpoint = f"/repos/{self._owner}/{self._repo}/check-runs"
        
        data: Dict[str, Any] = {
            "name": name,
            "head_sha": head_sha,
            "status": status.value,
        }

        if conclusion:
            data["conclusion"] = conclusion.value
            data["completed_at"] = datetime.utcnow().isoformat() + "Z"

        if title or summary:
            data["output"] = {}
            if title:
                data["output"]["title"] = title
            if summary:
                data["output"]["summary"] = summary
            if annotations:
                data["output"]["annotations"] = annotations

        if details_url:
            data["details_url"] = details_url

        return await self._request("POST", endpoint, data)

    async def update_check_run(
        self,
        check_run_id: int,
        status: Optional[CheckStatus] = None,
        conclusion: Optional[CheckConclusion] = None,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        annotations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Update an existing check run."""
        endpoint = f"/repos/{self._owner}/{self._repo}/check-runs/{check_run_id}"
        
        data: Dict[str, Any] = {}
        
        if status:
            data["status"] = status.value
        
        if conclusion:
            data["conclusion"] = conclusion.value
            data["completed_at"] = datetime.utcnow().isoformat() + "Z"

        if title or summary or annotations:
            data["output"] = {}
            if title:
                data["output"]["title"] = title
            if summary:
                data["output"]["summary"] = summary
            if annotations:
                data["output"]["annotations"] = annotations

        return await self._request("PATCH", endpoint, data)

    async def create_issue_comment(
        self,
        issue_number: int,
        body: str,
    ) -> Dict[str, Any]:
        """Create a comment on an issue or pull request."""
        endpoint = f"/repos/{self._owner}/{self._repo}/issues/{issue_number}/comments"
        return await self._request("POST", endpoint, {"body": body})

    async def create_pull_request_review(
        self,
        pull_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a pull request review."""
        endpoint = f"/repos/{self._owner}/{self._repo}/pulls/{pull_number}/reviews"
        
        data: Dict[str, Any] = {
            "body": body,
            "event": event,
        }
        
        if comments:
            data["comments"] = comments

        return await self._request("POST", endpoint, data)

    async def create_deployment(
        self,
        ref: str,
        environment: str,
        description: Optional[str] = None,
        auto_merge: bool = False,
        required_contexts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a deployment."""
        endpoint = f"/repos/{self._owner}/{self._repo}/deployments"
        
        data: Dict[str, Any] = {
            "ref": ref,
            "environment": environment,
            "auto_merge": auto_merge,
        }
        
        if description:
            data["description"] = description
        if required_contexts is not None:
            data["required_contexts"] = required_contexts

        return await self._request("POST", endpoint, data)

    async def create_deployment_status(
        self,
        deployment_id: int,
        state: str,
        environment_url: Optional[str] = None,
        log_url: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a deployment status."""
        endpoint = f"/repos/{self._owner}/{self._repo}/deployments/{deployment_id}/statuses"
        
        data: Dict[str, Any] = {
            "state": state,
        }
        
        if environment_url:
            data["environment_url"] = environment_url
        if log_url:
            data["log_url"] = log_url
        if description:
            data["description"] = description

        return await self._request("POST", endpoint, data)

    async def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create an issue."""
        endpoint = f"/repos/{self._owner}/{self._repo}/issues"
        
        data: Dict[str, Any] = {
            "title": title,
            "body": body,
        }
        
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees

        return await self._request("POST", endpoint, data)

    async def get_pull_request(self, pull_number: int) -> Dict[str, Any]:
        """Get pull request details."""
        endpoint = f"/repos/{self._owner}/{self._repo}/pulls/{pull_number}"
        return await self._request("GET", endpoint)

    async def get_pull_request_files(self, pull_number: int) -> List[Dict[str, Any]]:
        """Get files changed in a pull request."""
        endpoint = f"/repos/{self._owner}/{self._repo}/pulls/{pull_number}/files"
        result = await self._request("GET", endpoint)
        return result if isinstance(result, list) else []

    async def get_commit(self, sha: str) -> Dict[str, Any]:
        """Get commit details."""
        endpoint = f"/repos/{self._owner}/{self._repo}/commits/{sha}"
        return await self._request("GET", endpoint)

    async def get_workflow_runs(
        self,
        workflow_id: Optional[str] = None,
        branch: Optional[str] = None,
        status: Optional[str] = None,
        per_page: int = 10,
    ) -> Dict[str, Any]:
        """Get workflow runs."""
        endpoint = f"/repos/{self._owner}/{self._repo}/actions/runs"
        
        params = []
        if workflow_id:
            params.append(f"workflow_id={workflow_id}")
        if branch:
            params.append(f"branch={branch}")
        if status:
            params.append(f"status={status}")
        params.append(f"per_page={per_page}")
        
        if params:
            endpoint += "?" + "&".join(params)

        return await self._request("GET", endpoint)

    async def dispatch_workflow(
        self,
        workflow_id: str,
        ref: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Trigger a workflow dispatch event."""
        endpoint = f"/repos/{self._owner}/{self._repo}/actions/workflows/{workflow_id}/dispatches"
        
        data: Dict[str, Any] = {
            "ref": ref,
        }
        
        if inputs:
            data["inputs"] = inputs

        return await self._request("POST", endpoint, data)

    async def upload_sarif(
        self,
        commit_sha: str,
        ref: str,
        sarif_content: str,
        tool_name: str = "teams-security-scanner",
    ) -> Dict[str, Any]:
        """Upload SARIF analysis results."""
        import base64
        import gzip

        compressed = gzip.compress(sarif_content.encode())
        encoded = base64.b64encode(compressed).decode()

        endpoint = f"/repos/{self._owner}/{self._repo}/code-scanning/sarifs"
        
        data = {
            "commit_sha": commit_sha,
            "ref": ref,
            "sarif": encoded,
            "tool_name": tool_name,
        }

        return await self._request("POST", endpoint, data)


class GitHubEventHandler:
    """Handle GitHub webhook events and map to team events."""

    EVENT_MAPPING = {
        "push": "CODE_CHANGE_DETECTED",
        "pull_request.opened": "PULL_REQUEST_OPENED",
        "pull_request.synchronize": "PULL_REQUEST_SYNCHRONIZED",
        "pull_request.closed": "PULL_REQUEST_CLOSED",
        "pull_request_review.submitted": "REVIEW_SUBMITTED",
        "issue_comment.created": "COMMENT_CREATED",
        "workflow_dispatch": "MANUAL_OVERRIDE",
        "schedule": "SCHEDULED_EVENT",
        "deployment": "DEPLOYMENT_REQUESTED",
    }

    @classmethod
    def map_event(cls, github_event: str, action: Optional[str] = None) -> str:
        """Map GitHub event to team event type."""
        key = f"{github_event}.{action}" if action else github_event
        return cls.EVENT_MAPPING.get(key, cls.EVENT_MAPPING.get(github_event, "UNKNOWN_EVENT"))

    @classmethod
    def parse_webhook(cls, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GitHub webhook payload into team event."""
        event_type = headers.get("X-GitHub-Event", "unknown")
        action = payload.get("action")
        
        team_event = cls.map_event(event_type, action)
        
        event_data = {
            "event_type": team_event,
            "github_event": event_type,
            "github_action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "delivery_id": headers.get("X-GitHub-Delivery"),
        }

        if event_type == "push":
            event_data.update({
                "ref": payload.get("ref"),
                "before": payload.get("before"),
                "after": payload.get("after"),
                "commits": payload.get("commits", []),
                "pusher": payload.get("pusher", {}).get("name"),
            })
        elif event_type == "pull_request":
            pr = payload.get("pull_request", {})
            event_data.update({
                "pull_number": payload.get("number"),
                "title": pr.get("title"),
                "body": pr.get("body"),
                "head_sha": pr.get("head", {}).get("sha"),
                "base_ref": pr.get("base", {}).get("ref"),
                "head_ref": pr.get("head", {}).get("ref"),
                "author": pr.get("user", {}).get("login"),
                "draft": pr.get("draft", False),
            })

        return event_data
