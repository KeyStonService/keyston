#!/usr/bin/env python3
"""
Consensus Models for SuperAgent

Defines multi-agent consensus and voting data structures including:
- Vote types and results
- Consensus requests and state
- Weighted voting support
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class VoteType(str, Enum):
    """Types of votes in consensus."""
    APPROVE = "approve"       # Vote in favor
    REJECT = "reject"         # Vote against
    ABSTAIN = "abstain"       # No opinion
    VETO = "veto"             # Strong rejection (blocks consensus)


class ConsensusState(str, Enum):
    """States of a consensus request."""
    PENDING = "pending"           # Waiting for votes
    COLLECTING = "collecting"     # Actively collecting votes
    APPROVED = "approved"         # Consensus reached - approved
    REJECTED = "rejected"         # Consensus reached - rejected
    VETOED = "vetoed"             # Vetoed by authorized agent
    EXPIRED = "expired"           # Timeout without consensus
    CANCELLED = "cancelled"       # Manually cancelled


class Vote(BaseModel):
    """Individual vote from an agent."""

    vote_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique vote identifier"
    )
    consensus_id: str = Field(..., description="ID of the consensus request")
    agent_id: str = Field(..., description="Voting agent identifier")
    vote_type: VoteType = Field(..., description="Type of vote cast")
    weight: float = Field(default=1.0, description="Vote weight (for weighted voting)")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Vote timestamp"
    )
    reasoning: Optional[str] = Field(default=None, description="Explanation for vote")
    evidence_refs: List[str] = Field(default_factory=list, description="Supporting evidence")
    conditions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Conditions attached to approval"
    )
    signature: Optional[str] = Field(default=None, description="Vote signature")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vote_id": self.vote_id,
            "consensus_id": self.consensus_id,
            "agent_id": self.agent_id,
            "vote_type": self.vote_type.value,
            "weight": self.weight,
            "timestamp": self.timestamp,
            "reasoning": self.reasoning,
            "evidence_refs": self.evidence_refs,
            "conditions": self.conditions,
        }


class ConsensusRequest(BaseModel):
    """Request for multi-agent consensus."""

    consensus_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique consensus request identifier"
    )
    trace_id: str = Field(..., description="Trace ID for distributed tracing")
    request_type: str = Field(..., description="Type of decision being requested")
    title: str = Field(..., description="Short description of what's being decided")
    description: Optional[str] = Field(default=None, description="Detailed description")
    incident_id: Optional[str] = Field(default=None, description="Related incident ID")
    proposal_id: Optional[str] = Field(default=None, description="Proposal being voted on")
    requested_by: str = Field(..., description="Agent requesting consensus")
    required_voters: List[str] = Field(..., description="Agents required to vote")
    optional_voters: List[str] = Field(default_factory=list, description="Optional voters")
    quorum_percentage: float = Field(default=0.5, description="Minimum participation required")
    approval_threshold: float = Field(default=0.6, description="Approval percentage needed")
    veto_enabled: bool = Field(default=True, description="Whether veto votes are allowed")
    veto_agents: List[str] = Field(default_factory=list, description="Agents with veto power")
    timeout_seconds: float = Field(default=300.0, description="Timeout for consensus")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp"
    )
    expires_at: Optional[str] = Field(default=None, description="Expiration timestamp")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Data for voters to consider")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def __init__(self, **data):
        super().__init__(**data)
        if self.expires_at is None:
            from datetime import timedelta
            created = datetime.fromisoformat(self.created_at)
            self.expires_at = (created + timedelta(seconds=self.timeout_seconds)).isoformat()


class ConsensusResult(BaseModel):
    """Result of a consensus decision."""

    consensus_id: str = Field(..., description="Consensus request identifier")
    state: ConsensusState = Field(..., description="Final consensus state")
    total_votes: int = Field(..., description="Total votes received")
    approve_votes: int = Field(default=0, description="Number of approve votes")
    reject_votes: int = Field(default=0, description="Number of reject votes")
    abstain_votes: int = Field(default=0, description="Number of abstain votes")
    veto_votes: int = Field(default=0, description="Number of veto votes")
    weighted_approval: float = Field(default=0.0, description="Weighted approval percentage")
    quorum_met: bool = Field(default=False, description="Whether quorum was reached")
    threshold_met: bool = Field(default=False, description="Whether approval threshold met")
    votes: List[Vote] = Field(default_factory=list, description="All votes cast")
    decided_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Decision timestamp"
    )
    deciding_factor: Optional[str] = Field(default=None, description="What determined the outcome")
    conditions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Conditions from conditional approvals"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "consensus_id": self.consensus_id,
            "state": self.state.value,
            "total_votes": self.total_votes,
            "approve_votes": self.approve_votes,
            "reject_votes": self.reject_votes,
            "abstain_votes": self.abstain_votes,
            "veto_votes": self.veto_votes,
            "weighted_approval": self.weighted_approval,
            "quorum_met": self.quorum_met,
            "threshold_met": self.threshold_met,
            "decided_at": self.decided_at,
            "deciding_factor": self.deciding_factor,
            "conditions": self.conditions,
        }


class AgentWeight(BaseModel):
    """Weight configuration for an agent in consensus."""

    agent_id: str = Field(..., description="Agent identifier")
    weight: float = Field(default=1.0, description="Voting weight")
    has_veto: bool = Field(default=False, description="Whether agent has veto power")
    required: bool = Field(default=False, description="Whether vote is required")
    expertise_areas: List[str] = Field(
        default_factory=list,
        description="Areas where agent has expertise"
    )


# Default agent weights
DEFAULT_AGENT_WEIGHTS: Dict[str, AgentWeight] = {
    "super-agent": AgentWeight(
        agent_id="super-agent",
        weight=1.0,
        has_veto=True,
        required=False,
    ),
    "qa-agent": AgentWeight(
        agent_id="qa-agent",
        weight=1.5,
        has_veto=True,
        required=True,
        expertise_areas=["security", "compliance", "testing"],
    ),
    "problem-solver-agent": AgentWeight(
        agent_id="problem-solver-agent",
        weight=1.0,
        has_veto=False,
        required=True,
        expertise_areas=["diagnosis", "solutions"],
    ),
    "maintenance-agent": AgentWeight(
        agent_id="maintenance-agent",
        weight=1.0,
        has_veto=False,
        required=False,
        expertise_areas=["execution", "rollback"],
    ),
    "learning-agent": AgentWeight(
        agent_id="learning-agent",
        weight=0.5,
        has_veto=False,
        required=False,
        expertise_areas=["patterns", "history"],
    ),
}
