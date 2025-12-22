#!/usr/bin/env python3
"""
Tests for SuperAgent Models.

Tests cover:
- Message envelope models
- Incident lifecycle models
- Consensus voting models
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.messages import (
    MessageEnvelope,
    MessageType,
    MessageMetadata,
    MessageContext,
    MessageResponse,
    Urgency,
)
from models.incidents import (
    Incident,
    IncidentState,
    IncidentTransition,
    IncidentHistory,
    VALID_TRANSITIONS,
)
from models.consensus import (
    Vote,
    VoteType,
    ConsensusRequest,
    ConsensusResult,
    ConsensusState,
    AgentWeight,
    DEFAULT_AGENT_WEIGHTS,
)


class TestMessageModels:
    """Tests for message-related models."""

    def test_message_type_enum(self):
        """Test MessageType enum values."""
        assert MessageType.INCIDENT_CREATE == "incident.create"
        assert MessageType.HEARTBEAT == "system.heartbeat"
        assert MessageType.CONSENSUS_REQUEST == "consensus.request"

    def test_urgency_enum(self):
        """Test Urgency enum values."""
        assert Urgency.LOW == "low"
        assert Urgency.MEDIUM == "medium"
        assert Urgency.HIGH == "high"
        assert Urgency.CRITICAL == "critical"

    def test_message_metadata_creation(self):
        """Test MessageMetadata creation."""
        meta = MessageMetadata(
            timestamp=datetime.now(),
            trace_id="trace-123",
            span_id="span-456",
        )
        assert meta.trace_id == "trace-123"
        assert meta.span_id == "span-456"
        assert meta.version == "1.0"

    def test_message_envelope_creation(self):
        """Test MessageEnvelope creation."""
        envelope = MessageEnvelope(
            id=str(uuid4()),
            type=MessageType.INCIDENT_CREATE,
            source_agent="test-agent",
            payload={"title": "Test", "severity": "high"},
        )
        assert envelope.type == MessageType.INCIDENT_CREATE
        assert envelope.source_agent == "test-agent"
        assert envelope.urgency == Urgency.MEDIUM  # default

    def test_message_envelope_factory(self):
        """Test MessageEnvelope.create() factory method."""
        envelope = MessageEnvelope.create(
            msg_type=MessageType.CONSENSUS_REQUEST,
            source="orchestrator",
            payload={"action": "vote"},
        )
        assert envelope.type == MessageType.CONSENSUS_REQUEST
        assert envelope.source_agent == "orchestrator"
        assert envelope.id is not None
        assert envelope.metadata is not None

    def test_message_response(self):
        """Test MessageResponse creation."""
        response = MessageResponse(
            message_id="msg-001",
            status="accepted",
            details={"queue_position": 5},
        )
        assert response.message_id == "msg-001"
        assert response.status == "accepted"


class TestIncidentModels:
    """Tests for incident-related models."""

    def test_incident_state_enum(self):
        """Test IncidentState enum values."""
        assert IncidentState.OPEN == "OPEN"
        assert IncidentState.TRIAGE == "TRIAGE"
        assert IncidentState.CLOSED == "CLOSED"
        assert IncidentState.LEARN == "LEARN"

    def test_valid_transitions_defined(self):
        """Test that valid transitions are properly defined."""
        assert IncidentState.TRIAGE in VALID_TRANSITIONS[IncidentState.OPEN]
        assert IncidentState.RCA in VALID_TRANSITIONS[IncidentState.TRIAGE]
        assert len(VALID_TRANSITIONS[IncidentState.LEARN]) == 0  # terminal state

    def test_incident_creation(self):
        """Test Incident model creation."""
        incident = Incident(
            id="inc-001",
            title="Database Connection Failure",
            description="Primary DB connection pool exhausted",
            severity="critical",
            type="infrastructure",
        )
        assert incident.id == "inc-001"
        assert incident.state == IncidentState.OPEN
        assert incident.severity == "critical"

    def test_incident_can_transition_to(self):
        """Test incident transition validation."""
        incident = Incident(
            id="inc-001",
            title="Test",
            description="Test incident",
            severity="low",
            type="test",
        )
        # OPEN can transition to TRIAGE
        assert incident.can_transition_to(IncidentState.TRIAGE) is True
        # OPEN cannot transition directly to CLOSED
        assert incident.can_transition_to(IncidentState.CLOSED) is False

    def test_incident_transition_to(self):
        """Test incident state transition."""
        incident = Incident(
            id="inc-001",
            title="Test",
            description="Test incident",
            severity="low",
            type="test",
        )
        # Transition to TRIAGE
        incident.transition_to(IncidentState.TRIAGE, "operator-001", "Starting triage")
        assert incident.state == IncidentState.TRIAGE
        assert len(incident.history) == 1
        assert incident.history[0].from_state == IncidentState.OPEN
        assert incident.history[0].to_state == IncidentState.TRIAGE

    def test_incident_invalid_transition_raises(self):
        """Test that invalid transitions raise ValueError."""
        incident = Incident(
            id="inc-001",
            title="Test",
            description="Test incident",
            severity="low",
            type="test",
        )
        with pytest.raises(ValueError, match="Invalid transition"):
            incident.transition_to(IncidentState.EXECUTE, "operator-001", "Invalid")

    def test_incident_transition_model(self):
        """Test IncidentTransition model."""
        transition = IncidentTransition(
            from_state=IncidentState.OPEN,
            to_state=IncidentState.TRIAGE,
            actor="operator-001",
            reason="Starting investigation",
        )
        assert transition.from_state == IncidentState.OPEN
        assert transition.timestamp is not None


class TestConsensusModels:
    """Tests for consensus-related models."""

    def test_vote_type_enum(self):
        """Test VoteType enum values."""
        assert VoteType.APPROVE == "approve"
        assert VoteType.REJECT == "reject"
        assert VoteType.ABSTAIN == "abstain"
        assert VoteType.VETO == "veto"

    def test_consensus_state_enum(self):
        """Test ConsensusState enum values."""
        assert ConsensusState.PENDING == "pending"
        assert ConsensusState.APPROVED == "approved"
        assert ConsensusState.REJECTED == "rejected"

    def test_vote_creation(self):
        """Test Vote model creation."""
        vote = Vote(
            voter_id="agent-001",
            vote_type=VoteType.APPROVE,
            weight=1.5,
            reason="All checks passed",
        )
        assert vote.voter_id == "agent-001"
        assert vote.vote_type == VoteType.APPROVE
        assert vote.weight == 1.5

    def test_consensus_request_creation(self):
        """Test ConsensusRequest model creation."""
        request = ConsensusRequest(
            id="req-001",
            request_type="action_approval",
            initiator="super-agent",
            payload={"action": "restart_service", "target": "api-server"},
            required_agents=["monitoring-agent", "security-agent"],
        )
        assert request.id == "req-001"
        assert request.state == ConsensusState.PENDING
        assert len(request.votes) == 0
        assert request.quorum == 0.51  # default

    def test_default_agent_weights(self):
        """Test default agent weight configuration."""
        assert "super-agent" in DEFAULT_AGENT_WEIGHTS
        assert DEFAULT_AGENT_WEIGHTS["super-agent"].weight == 2.0
        assert DEFAULT_AGENT_WEIGHTS["super-agent"].has_veto is True
        assert DEFAULT_AGENT_WEIGHTS["monitoring-agent"].weight == 1.0

    def test_consensus_result(self):
        """Test ConsensusResult model."""
        result = ConsensusResult(
            request_id="req-001",
            state=ConsensusState.APPROVED,
            total_weight=5.5,
            approve_weight=4.0,
            reject_weight=1.5,
            abstain_count=0,
            veto_used=False,
        )
        assert result.state == ConsensusState.APPROVED
        assert result.approve_weight > result.reject_weight


class TestModelValidation:
    """Tests for Pydantic model validation."""

    def test_message_envelope_requires_type(self):
        """Test that MessageEnvelope requires type field."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            MessageEnvelope(
                id="msg-001",
                source_agent="test",
                payload={},
            )

    def test_incident_requires_title(self):
        """Test that Incident requires title field."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            Incident(
                id="inc-001",
                description="Test",
                severity="low",
                type="test",
            )

    def test_vote_requires_voter_id(self):
        """Test that Vote requires voter_id field."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            Vote(
                vote_type=VoteType.APPROVE,
                weight=1.0,
            )
