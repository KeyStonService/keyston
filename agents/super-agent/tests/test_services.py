#!/usr/bin/env python3
"""
Tests for SuperAgent Services.

Tests cover:
- Audit trail logging and verification
- Event store persistence
- State machine transitions
- Consensus management
- Agent client communication
"""

import asyncio
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.audit_trail import AuditTrail, AuditEntry, AuditAction
from services.event_store import EventStore, StoredEvent
from services.state_machine import IncidentStateMachine
from services.consensus import ConsensusManager
from services.agent_client import AgentClient, AgentRegistry
from models.incidents import Incident, IncidentState
from models.consensus import VoteType, ConsensusState


class TestAuditTrail:
    """Tests for AuditTrail service."""

    @pytest.fixture
    def audit_trail(self):
        """Create an AuditTrail instance."""
        return AuditTrail(max_entries=100)

    @pytest.mark.asyncio
    async def test_log_creates_entry(self, audit_trail):
        """Test that log() creates an audit entry."""
        entry = await audit_trail.log(
            action=AuditAction.INCIDENT_CREATED,
            actor="test-agent",
            resource_type="incident",
            resource_id="inc-001",
            details={"title": "Test Incident"},
        )
        assert entry.action == AuditAction.INCIDENT_CREATED
        assert entry.actor == "test-agent"
        assert entry.resource_id == "inc-001"
        assert entry.checksum is not None

    @pytest.mark.asyncio
    async def test_log_entry_has_checksum(self, audit_trail):
        """Test that audit entries have checksums."""
        entry = await audit_trail.log(
            action=AuditAction.STATE_TRANSITION,
            actor="super-agent",
            resource_type="incident",
            resource_id="inc-002",
        )
        assert len(entry.checksum) == 64  # SHA256 hex

    @pytest.mark.asyncio
    async def test_query_by_action(self, audit_trail):
        """Test querying entries by action."""
        await audit_trail.log(
            action=AuditAction.INCIDENT_CREATED,
            actor="agent-1",
            resource_type="incident",
            resource_id="inc-001",
        )
        await audit_trail.log(
            action=AuditAction.STATE_TRANSITION,
            actor="agent-2",
            resource_type="incident",
            resource_id="inc-002",
        )

        results = await audit_trail.query(action=AuditAction.INCIDENT_CREATED)
        assert len(results) == 1
        assert results[0].action == AuditAction.INCIDENT_CREATED

    @pytest.mark.asyncio
    async def test_query_by_actor(self, audit_trail):
        """Test querying entries by actor."""
        await audit_trail.log(
            action=AuditAction.MESSAGE_SENT,
            actor="agent-1",
            resource_type="message",
            resource_id="msg-001",
        )
        await audit_trail.log(
            action=AuditAction.MESSAGE_SENT,
            actor="agent-2",
            resource_type="message",
            resource_id="msg-002",
        )

        results = await audit_trail.query(actor="agent-1")
        assert len(results) == 1
        assert results[0].actor == "agent-1"

    @pytest.mark.asyncio
    async def test_verify_integrity(self, audit_trail):
        """Test audit trail integrity verification."""
        await audit_trail.log(
            action=AuditAction.INCIDENT_CREATED,
            actor="agent-1",
            resource_type="incident",
            resource_id="inc-001",
        )
        await audit_trail.log(
            action=AuditAction.STATE_TRANSITION,
            actor="agent-1",
            resource_type="incident",
            resource_id="inc-001",
        )

        is_valid = await audit_trail.verify_integrity()
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_max_entries_limit(self, audit_trail):
        """Test that max_entries limit is enforced."""
        for i in range(150):
            await audit_trail.log(
                action=AuditAction.MESSAGE_SENT,
                actor="agent-1",
                resource_type="message",
                resource_id=f"msg-{i:03d}",
            )

        all_entries = await audit_trail.query()
        assert len(all_entries) <= 100


class TestEventStore:
    """Tests for EventStore service."""

    @pytest.fixture
    def event_store(self):
        """Create an EventStore instance."""
        return EventStore(backend="memory")

    @pytest.mark.asyncio
    async def test_append_event(self, event_store):
        """Test appending an event."""
        await event_store.initialize()

        event = await event_store.append(
            aggregate_id="inc-001",
            event_type="IncidentCreated",
            data={"title": "Test", "severity": "high"},
            metadata={"actor": "test-agent"},
        )
        assert event.aggregate_id == "inc-001"
        assert event.event_type == "IncidentCreated"
        assert event.sequence == 0

    @pytest.mark.asyncio
    async def test_get_events_for_aggregate(self, event_store):
        """Test getting events for an aggregate."""
        await event_store.initialize()

        await event_store.append("inc-001", "Created", {"a": 1})
        await event_store.append("inc-001", "Updated", {"b": 2})
        await event_store.append("inc-002", "Created", {"c": 3})

        events = await event_store.get_events("inc-001")
        assert len(events) == 2
        assert events[0].event_type == "Created"
        assert events[1].event_type == "Updated"

    @pytest.mark.asyncio
    async def test_event_sequence_increments(self, event_store):
        """Test that event sequence increments correctly."""
        await event_store.initialize()

        e1 = await event_store.append("inc-001", "Event1", {})
        e2 = await event_store.append("inc-001", "Event2", {})
        e3 = await event_store.append("inc-001", "Event3", {})

        assert e1.sequence == 0
        assert e2.sequence == 1
        assert e3.sequence == 2

    @pytest.mark.asyncio
    async def test_subscribe_and_notify(self, event_store):
        """Test event subscription and notification."""
        await event_store.initialize()

        received_events = []

        async def handler(event):
            received_events.append(event)

        event_store.subscribe("IncidentCreated", handler)

        await event_store.append("inc-001", "IncidentCreated", {"title": "Test"})
        await event_store.append("inc-001", "IncidentUpdated", {"title": "Updated"})

        # Allow time for async handler
        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        assert received_events[0].event_type == "IncidentCreated"


class TestIncidentStateMachine:
    """Tests for IncidentStateMachine service."""

    @pytest.fixture
    def state_machine(self):
        """Create an IncidentStateMachine instance."""
        event_store = EventStore(backend="memory")
        audit_trail = AuditTrail()
        return IncidentStateMachine(event_store, audit_trail)

    @pytest.mark.asyncio
    async def test_create_incident(self, state_machine):
        """Test creating an incident."""
        await state_machine.event_store.initialize()

        incident = await state_machine.create_incident(
            id="inc-001",
            title="Test Incident",
            description="A test incident",
            severity="high",
            incident_type="infrastructure",
            source_agent="test-agent",
        )
        assert incident.id == "inc-001"
        assert incident.state == IncidentState.OPEN
        assert incident.title == "Test Incident"

    @pytest.mark.asyncio
    async def test_transition_incident(self, state_machine):
        """Test transitioning an incident."""
        await state_machine.event_store.initialize()

        incident = await state_machine.create_incident(
            id="inc-002",
            title="Test",
            description="Test",
            severity="medium",
            incident_type="application",
            source_agent="test-agent",
        )

        transitioned = await state_machine.transition(
            incident_id="inc-002",
            to_state=IncidentState.TRIAGE,
            actor="operator-001",
            reason="Starting investigation",
        )
        assert transitioned.state == IncidentState.TRIAGE

    @pytest.mark.asyncio
    async def test_get_incident(self, state_machine):
        """Test retrieving an incident."""
        await state_machine.event_store.initialize()

        await state_machine.create_incident(
            id="inc-003",
            title="Retrieval Test",
            description="Test",
            severity="low",
            incident_type="test",
            source_agent="test-agent",
        )

        incident = await state_machine.get_incident("inc-003")
        assert incident is not None
        assert incident.title == "Retrieval Test"

    @pytest.mark.asyncio
    async def test_get_incidents_by_state(self, state_machine):
        """Test getting incidents by state."""
        await state_machine.event_store.initialize()

        await state_machine.create_incident(
            id="inc-004",
            title="Open 1",
            description="Test",
            severity="low",
            incident_type="test",
            source_agent="test",
        )
        await state_machine.create_incident(
            id="inc-005",
            title="Open 2",
            description="Test",
            severity="low",
            incident_type="test",
            source_agent="test",
        )

        open_incidents = await state_machine.get_incidents_by_state(IncidentState.OPEN)
        assert len(open_incidents) == 2


class TestConsensusManager:
    """Tests for ConsensusManager service."""

    @pytest.fixture
    def consensus_manager(self):
        """Create a ConsensusManager instance."""
        return ConsensusManager()

    @pytest.mark.asyncio
    async def test_create_request(self, consensus_manager):
        """Test creating a consensus request."""
        request = await consensus_manager.create_request(
            request_type="action_approval",
            initiator="super-agent",
            payload={"action": "restart"},
            required_agents=["agent-1", "agent-2"],
            timeout=60.0,
        )
        assert request.request_type == "action_approval"
        assert request.state == ConsensusState.PENDING
        assert len(request.required_agents) == 2

    @pytest.mark.asyncio
    async def test_submit_vote(self, consensus_manager):
        """Test submitting a vote."""
        request = await consensus_manager.create_request(
            request_type="test",
            initiator="super-agent",
            payload={},
            required_agents=["agent-1"],
        )

        await consensus_manager.submit_vote(
            request_id=request.id,
            voter_id="agent-1",
            vote_type=VoteType.APPROVE,
            reason="Approved",
        )

        updated = await consensus_manager.get_request(request.id)
        assert len(updated.votes) == 1
        assert updated.votes[0].vote_type == VoteType.APPROVE

    @pytest.mark.asyncio
    async def test_consensus_reached_on_approval(self, consensus_manager):
        """Test that consensus is reached when quorum approves."""
        request = await consensus_manager.create_request(
            request_type="test",
            initiator="super-agent",
            payload={},
            required_agents=["agent-1", "agent-2"],
            quorum=0.51,
        )

        # Both agents approve
        await consensus_manager.submit_vote(request.id, "agent-1", VoteType.APPROVE)
        await consensus_manager.submit_vote(request.id, "agent-2", VoteType.APPROVE)

        result = await consensus_manager.get_result(request.id)
        assert result.state == ConsensusState.APPROVED

    @pytest.mark.asyncio
    async def test_veto_blocks_approval(self, consensus_manager):
        """Test that a veto blocks approval."""
        request = await consensus_manager.create_request(
            request_type="test",
            initiator="super-agent",
            payload={},
            required_agents=["super-agent", "agent-1"],
        )

        # super-agent has veto power by default
        await consensus_manager.submit_vote(request.id, "agent-1", VoteType.APPROVE)
        await consensus_manager.submit_vote(request.id, "super-agent", VoteType.VETO)

        result = await consensus_manager.get_result(request.id)
        assert result.state == ConsensusState.VETOED
        assert result.veto_used is True


class TestAgentClient:
    """Tests for AgentClient service."""

    @pytest.fixture
    def agent_registry(self):
        """Create an AgentRegistry instance."""
        return AgentRegistry()

    @pytest.fixture
    def agent_client(self, agent_registry):
        """Create an AgentClient instance."""
        return AgentClient(agent_registry)

    def test_register_agent(self, agent_registry):
        """Test registering an agent."""
        agent_registry.register(
            agent_id="monitoring-agent",
            url="http://monitoring:8080",
            capabilities=["monitor", "alert"],
        )
        assert "monitoring-agent" in agent_registry._agents
        assert agent_registry._agents["monitoring-agent"]["url"] == "http://monitoring:8080"

    def test_get_agent_url(self, agent_registry):
        """Test getting an agent URL."""
        agent_registry.register("test-agent", "http://test:8080")
        url = agent_registry.get_url("test-agent")
        assert url == "http://test:8080"

    def test_get_nonexistent_agent_returns_none(self, agent_registry):
        """Test that getting a nonexistent agent returns None."""
        url = agent_registry.get_url("nonexistent")
        assert url is None

    def test_list_agents(self, agent_registry):
        """Test listing all agents."""
        agent_registry.register("agent-1", "http://a1:8080")
        agent_registry.register("agent-2", "http://a2:8080")

        agents = agent_registry.list_agents()
        assert len(agents) == 2
        assert "agent-1" in agents
        assert "agent-2" in agents

    @pytest.mark.asyncio
    async def test_send_message_to_unknown_agent(self, agent_client):
        """Test sending a message to an unknown agent raises error."""
        from models.messages import MessageEnvelope, MessageType

        envelope = MessageEnvelope.create(
            msg_type=MessageType.HEARTBEAT,
            source="test",
            payload={},
        )

        with pytest.raises(ValueError, match="Unknown agent"):
            await agent_client.send_message("unknown-agent", envelope)
