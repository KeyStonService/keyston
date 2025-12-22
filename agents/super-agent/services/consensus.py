#!/usr/bin/env python3
"""
Consensus Service for SuperAgent

Implements multi-agent consensus mechanism with:
- Weighted voting
- Quorum requirements
- Veto power
- Timeout handling
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional
import uuid

from ..models.consensus import (
    Vote,
    VoteType,
    ConsensusRequest,
    ConsensusResult,
    ConsensusState,
    AgentWeight,
    DEFAULT_AGENT_WEIGHTS,
)
from .event_store import EventStore
from .audit_trail import AuditTrail, AuditAction


class ConsensusManager:
    """
    Manager for multi-agent consensus decisions.

    Provides:
    - Create consensus requests
    - Collect votes
    - Calculate results
    - Handle timeouts
    """

    def __init__(
        self,
        event_store: Optional[EventStore] = None,
        audit_trail: Optional[AuditTrail] = None,
        agent_weights: Optional[Dict[str, AgentWeight]] = None,
    ):
        self._event_store = event_store
        self._audit_trail = audit_trail
        self._agent_weights = agent_weights or DEFAULT_AGENT_WEIGHTS
        self._lock = asyncio.Lock()

        self._requests: Dict[str, ConsensusRequest] = {}
        self._votes: Dict[str, List[Vote]] = {}  # consensus_id -> votes
        self._results: Dict[str, ConsensusResult] = {}

        # Callbacks
        self._on_consensus: List[Callable] = []

    async def create_request(
        self,
        trace_id: str,
        request_type: str,
        title: str,
        description: Optional[str] = None,
        incident_id: Optional[str] = None,
        proposal_id: Optional[str] = None,
        requested_by: str = "super-agent",
        required_voters: Optional[List[str]] = None,
        optional_voters: Optional[List[str]] = None,
        quorum_percentage: float = 0.5,
        approval_threshold: float = 0.6,
        timeout_seconds: float = 300.0,
        payload: Optional[Dict[str, Any]] = None,
    ) -> ConsensusRequest:
        """Create a new consensus request."""
        # Determine voters from agent weights if not specified
        if required_voters is None:
            required_voters = [
                agent_id for agent_id, weight in self._agent_weights.items()
                if weight.required
            ]

        if optional_voters is None:
            optional_voters = [
                agent_id for agent_id, weight in self._agent_weights.items()
                if not weight.required and agent_id not in required_voters
            ]

        # Determine veto agents
        veto_agents = [
            agent_id for agent_id, weight in self._agent_weights.items()
            if weight.has_veto
        ]

        request = ConsensusRequest(
            trace_id=trace_id,
            request_type=request_type,
            title=title,
            description=description,
            incident_id=incident_id,
            proposal_id=proposal_id,
            requested_by=requested_by,
            required_voters=required_voters,
            optional_voters=optional_voters,
            quorum_percentage=quorum_percentage,
            approval_threshold=approval_threshold,
            veto_agents=veto_agents,
            timeout_seconds=timeout_seconds,
            payload=payload or {},
        )

        async with self._lock:
            self._requests[request.consensus_id] = request
            self._votes[request.consensus_id] = []

        # Store event
        if self._event_store:
            await self._event_store.append(
                event_type="ConsensusRequested",
                aggregate_type="consensus",
                aggregate_id=request.consensus_id,
                trace_id=trace_id,
                data={
                    "request_type": request_type,
                    "title": title,
                    "required_voters": required_voters,
                    "timeout_seconds": timeout_seconds,
                },
            )

        # Audit log
        if self._audit_trail:
            await self._audit_trail.log(
                action=AuditAction.CONSENSUS_REQUESTED,
                actor=requested_by,
                target=request.consensus_id,
                trace_id=trace_id,
                details={
                    "request_type": request_type,
                    "required_voters": required_voters,
                    "quorum_percentage": quorum_percentage,
                    "approval_threshold": approval_threshold,
                },
            )

        # Schedule timeout check
        asyncio.create_task(self._schedule_timeout(request))

        return request

    async def submit_vote(
        self,
        consensus_id: str,
        agent_id: str,
        vote_type: VoteType,
        reasoning: Optional[str] = None,
        evidence_refs: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
    ) -> Optional[Vote]:
        """Submit a vote for a consensus request."""
        async with self._lock:
            request = self._requests.get(consensus_id)
            if not request:
                return None

            # Check if already decided
            if consensus_id in self._results:
                return None

            # Check if expired
            if datetime.now() > datetime.fromisoformat(request.expires_at):
                return None

            # Check if agent already voted
            existing_votes = self._votes.get(consensus_id, [])
            if any(v.agent_id == agent_id for v in existing_votes):
                return None

            # Get agent weight
            agent_weight = self._agent_weights.get(
                agent_id,
                AgentWeight(agent_id=agent_id, weight=1.0)
            )

            vote = Vote(
                consensus_id=consensus_id,
                agent_id=agent_id,
                vote_type=vote_type,
                weight=agent_weight.weight,
                reasoning=reasoning,
                evidence_refs=evidence_refs or [],
                conditions=conditions,
            )

            self._votes[consensus_id].append(vote)

        # Store event
        if self._event_store:
            await self._event_store.append(
                event_type="ConsensusVoteReceived",
                aggregate_type="consensus",
                aggregate_id=consensus_id,
                trace_id=request.trace_id,
                data={
                    "agent_id": agent_id,
                    "vote_type": vote_type.value,
                    "weight": agent_weight.weight,
                },
            )

        # Audit log
        if self._audit_trail:
            await self._audit_trail.log(
                action=AuditAction.CONSENSUS_VOTE_RECEIVED,
                actor=agent_id,
                target=consensus_id,
                trace_id=request.trace_id,
                details={
                    "vote_type": vote_type.value,
                    "weight": agent_weight.weight,
                    "reasoning": reasoning,
                },
            )

        # Check if consensus reached
        await self._check_consensus(consensus_id)

        return vote

    async def _check_consensus(self, consensus_id: str) -> Optional[ConsensusResult]:
        """Check if consensus has been reached."""
        async with self._lock:
            request = self._requests.get(consensus_id)
            if not request or consensus_id in self._results:
                return None

            votes = self._votes.get(consensus_id, [])

            # Check for veto
            for vote in votes:
                if vote.vote_type == VoteType.VETO and vote.agent_id in request.veto_agents:
                    result = await self._finalize_consensus(
                        request, votes, ConsensusState.VETOED, f"Vetoed by {vote.agent_id}"
                    )
                    return result

            # Calculate participation
            all_voters = set(request.required_voters + request.optional_voters)
            voted_agents = {v.agent_id for v in votes}
            required_voted = set(request.required_voters) & voted_agents

            # Check if all required voters have voted
            if len(required_voted) < len(request.required_voters):
                return None

            # Calculate quorum
            participation = len(voted_agents) / len(all_voters) if all_voters else 0
            if participation < request.quorum_percentage:
                return None

            # Calculate weighted votes
            total_weight = sum(v.weight for v in votes if v.vote_type != VoteType.ABSTAIN)
            approve_weight = sum(v.weight for v in votes if v.vote_type == VoteType.APPROVE)
            reject_weight = sum(v.weight for v in votes if v.vote_type == VoteType.REJECT)

            if total_weight == 0:
                return None

            approval_percentage = approve_weight / total_weight

            # Determine outcome
            if approval_percentage >= request.approval_threshold:
                state = ConsensusState.APPROVED
                deciding_factor = f"Approval threshold met: {approval_percentage:.1%}"
            else:
                state = ConsensusState.REJECTED
                deciding_factor = f"Approval threshold not met: {approval_percentage:.1%}"

            result = await self._finalize_consensus(request, votes, state, deciding_factor)
            return result

    async def _finalize_consensus(
        self,
        request: ConsensusRequest,
        votes: List[Vote],
        state: ConsensusState,
        deciding_factor: str,
    ) -> ConsensusResult:
        """Finalize a consensus decision."""
        # Count votes
        approve_count = sum(1 for v in votes if v.vote_type == VoteType.APPROVE)
        reject_count = sum(1 for v in votes if v.vote_type == VoteType.REJECT)
        abstain_count = sum(1 for v in votes if v.vote_type == VoteType.ABSTAIN)
        veto_count = sum(1 for v in votes if v.vote_type == VoteType.VETO)

        # Calculate weighted approval
        total_weight = sum(v.weight for v in votes if v.vote_type != VoteType.ABSTAIN)
        approve_weight = sum(v.weight for v in votes if v.vote_type == VoteType.APPROVE)
        weighted_approval = approve_weight / total_weight if total_weight > 0 else 0

        # Collect conditions
        conditions = [v.conditions for v in votes if v.conditions and v.vote_type == VoteType.APPROVE]

        result = ConsensusResult(
            consensus_id=request.consensus_id,
            state=state,
            total_votes=len(votes),
            approve_votes=approve_count,
            reject_votes=reject_count,
            abstain_votes=abstain_count,
            veto_votes=veto_count,
            weighted_approval=weighted_approval,
            quorum_met=True,
            threshold_met=state == ConsensusState.APPROVED,
            votes=votes,
            deciding_factor=deciding_factor,
            conditions=conditions,
        )

        self._results[request.consensus_id] = result

        # Store event
        if self._event_store:
            await self._event_store.append(
                event_type="ConsensusReached",
                aggregate_type="consensus",
                aggregate_id=request.consensus_id,
                trace_id=request.trace_id,
                data=result.to_dict(),
            )

        # Audit log
        if self._audit_trail:
            await self._audit_trail.log_consensus_result(
                consensus_id=request.consensus_id,
                trace_id=request.trace_id,
                result=state.value,
                votes={v.agent_id: v.vote_type.value for v in votes},
            )

        # Trigger callbacks
        await self._trigger_callbacks(request, result)

        return result

    async def _schedule_timeout(self, request: ConsensusRequest) -> None:
        """Schedule timeout check for a consensus request."""
        await asyncio.sleep(request.timeout_seconds)

        async with self._lock:
            if request.consensus_id in self._results:
                return  # Already decided

            votes = self._votes.get(request.consensus_id, [])
            result = await self._finalize_consensus(
                request, votes, ConsensusState.EXPIRED, "Timeout reached"
            )

    async def _trigger_callbacks(
        self,
        request: ConsensusRequest,
        result: ConsensusResult,
    ) -> None:
        """Trigger consensus callbacks."""
        for callback in self._on_consensus:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(request, result)
                else:
                    callback(request, result)
            except Exception:
                pass

    def on_consensus(self, callback: Callable) -> None:
        """Register a callback for when consensus is reached."""
        self._on_consensus.append(callback)

    async def get_request(self, consensus_id: str) -> Optional[ConsensusRequest]:
        """Get a consensus request."""
        async with self._lock:
            return self._requests.get(consensus_id)

    async def get_result(self, consensus_id: str) -> Optional[ConsensusResult]:
        """Get a consensus result."""
        async with self._lock:
            return self._results.get(consensus_id)

    async def get_votes(self, consensus_id: str) -> List[Vote]:
        """Get votes for a consensus request."""
        async with self._lock:
            return self._votes.get(consensus_id, [])

    async def get_pending_requests(self) -> List[ConsensusRequest]:
        """Get all pending consensus requests."""
        async with self._lock:
            return [
                r for r in self._requests.values()
                if r.consensus_id not in self._results
            ]

    async def get_statistics(self) -> Dict[str, Any]:
        """Get consensus statistics."""
        async with self._lock:
            total_requests = len(self._requests)
            pending = sum(1 for cid in self._requests if cid not in self._results)
            approved = sum(1 for r in self._results.values() if r.state == ConsensusState.APPROVED)
            rejected = sum(1 for r in self._results.values() if r.state == ConsensusState.REJECTED)
            vetoed = sum(1 for r in self._results.values() if r.state == ConsensusState.VETOED)
            expired = sum(1 for r in self._results.values() if r.state == ConsensusState.EXPIRED)

        return {
            "total_requests": total_requests,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "vetoed": vetoed,
            "expired": expired,
            "approval_rate": approved / (approved + rejected) * 100 if (approved + rejected) > 0 else 0,
        }

    def __len__(self) -> int:
        """Return number of consensus requests."""
        return len(self._requests)
