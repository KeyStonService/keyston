#!/usr/bin/env python3
"""
Tests for SuperAgent API Endpoints.

Tests cover:
- Health and readiness endpoints
- Message handling endpoints
- Incident management endpoints
- Consensus voting endpoints
- Metrics and audit endpoints
"""

import os
import sys

import pytest
from httpx import AsyncClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHealthEndpoints:
    """Tests for health-related endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test /health endpoint returns healthy status."""
        response = await async_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data

    @pytest.mark.asyncio
    async def test_ready_endpoint(self, async_client: AsyncClient):
        """Test /ready endpoint returns ready status."""
        response = await async_client.get("/ready")
        assert response.status_code == 200

        data = response.json()
        assert data["ready"] is True

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint returns service info."""
        response = await async_client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "SuperAgent"
        assert "version" in data


class TestMessageEndpoints:
    """Tests for message handling endpoints."""

    @pytest.mark.asyncio
    async def test_send_message_valid(
        self, async_client: AsyncClient, sample_message_payload
    ):
        """Test sending a valid message."""
        response = await async_client.post("/message", json=sample_message_payload)

        # Should be accepted (202) or OK (200)
        assert response.status_code in [200, 202]

        data = response.json()
        assert "message_id" in data or "id" in data

    @pytest.mark.asyncio
    async def test_send_message_invalid_type(self, async_client: AsyncClient):
        """Test sending a message with invalid type."""
        payload = {
            "id": "test-001",
            "type": "invalid.type",
            "source_agent": "test",
            "payload": {},
        }
        response = await async_client.post("/message", json=payload)

        # Should return validation error
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_send_message_missing_fields(self, async_client: AsyncClient):
        """Test sending a message with missing required fields."""
        payload = {
            "id": "test-001",
            # Missing type and source_agent
            "payload": {},
        }
        response = await async_client.post("/message", json=payload)

        assert response.status_code == 422


class TestIncidentEndpoints:
    """Tests for incident management endpoints."""

    @pytest.mark.asyncio
    async def test_create_incident(
        self, async_client: AsyncClient, sample_incident_payload
    ):
        """Test creating an incident."""
        response = await async_client.post("/incidents", json=sample_incident_payload)

        assert response.status_code in [200, 201]

        data = response.json()
        assert data["id"] == sample_incident_payload["id"]
        assert data["state"] == "OPEN"

    @pytest.mark.asyncio
    async def test_get_incident(
        self, async_client: AsyncClient, sample_incident_payload
    ):
        """Test retrieving an incident."""
        # First create the incident
        await async_client.post("/incidents", json=sample_incident_payload)

        # Then retrieve it
        response = await async_client.get(f"/incidents/{sample_incident_payload['id']}")

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sample_incident_payload["id"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_incident(self, async_client: AsyncClient):
        """Test retrieving a nonexistent incident returns 404."""
        response = await async_client.get("/incidents/nonexistent-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_incidents(self, async_client: AsyncClient):
        """Test listing all incidents."""
        response = await async_client.get("/incidents")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_transition_incident(
        self, async_client: AsyncClient, sample_incident_payload
    ):
        """Test transitioning an incident state."""
        # Create incident
        await async_client.post("/incidents", json=sample_incident_payload)

        # Transition to TRIAGE
        transition_payload = {
            "to_state": "TRIAGE",
            "actor": "operator-001",
            "reason": "Starting investigation",
        }
        response = await async_client.post(
            f"/incidents/{sample_incident_payload['id']}/transition",
            json=transition_payload,
        )

        assert response.status_code == 200

        data = response.json()
        assert data["state"] == "TRIAGE"


class TestConsensusEndpoints:
    """Tests for consensus voting endpoints."""

    @pytest.mark.asyncio
    async def test_create_consensus_request(self, async_client: AsyncClient):
        """Test creating a consensus request."""
        payload = {
            "request_type": "action_approval",
            "initiator": "super-agent",
            "payload": {"action": "restart_service"},
            "required_agents": ["agent-1", "agent-2"],
        }
        response = await async_client.post("/consensus", json=payload)

        assert response.status_code in [200, 201]

        data = response.json()
        assert "id" in data
        assert data["state"] == "pending"

    @pytest.mark.asyncio
    async def test_submit_vote(self, async_client: AsyncClient, sample_vote_payload):
        """Test submitting a vote."""
        # First create a consensus request
        request_payload = {
            "request_type": "test",
            "initiator": "super-agent",
            "payload": {},
            "required_agents": ["agent-001"],
        }
        create_response = await async_client.post("/consensus", json=request_payload)
        request_id = create_response.json()["id"]

        # Submit vote
        vote_payload = {
            "voter_id": "agent-001",
            "vote": "approve",
            "reason": "Approved",
        }
        response = await async_client.post(
            f"/consensus/{request_id}/vote", json=vote_payload
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_consensus_result(self, async_client: AsyncClient):
        """Test getting consensus result."""
        # Create and complete a consensus request
        request_payload = {
            "request_type": "test",
            "initiator": "super-agent",
            "payload": {},
            "required_agents": ["agent-001"],
        }
        create_response = await async_client.post("/consensus", json=request_payload)
        request_id = create_response.json()["id"]

        # Submit vote to complete
        vote_payload = {
            "voter_id": "agent-001",
            "vote": "approve",
            "reason": "Approved",
        }
        await async_client.post(f"/consensus/{request_id}/vote", json=vote_payload)

        # Get result
        response = await async_client.get(f"/consensus/{request_id}/result")

        assert response.status_code == 200
        data = response.json()
        assert "state" in data


class TestMetricsEndpoints:
    """Tests for metrics and observability endpoints."""

    @pytest.mark.asyncio
    async def test_prometheus_metrics(self, async_client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await async_client.get("/metrics")

        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("text/plain")

        text = response.text
        assert "# HELP" in text
        assert "# TYPE" in text

    @pytest.mark.asyncio
    async def test_json_metrics(self, async_client: AsyncClient):
        """Test JSON metrics endpoint."""
        response = await async_client.get("/metrics/json")

        assert response.status_code == 200

        data = response.json()
        assert "uptime_seconds" in data
        assert "metrics" in data


class TestAuditEndpoints:
    """Tests for audit trail endpoints."""

    @pytest.mark.asyncio
    async def test_get_audit_entries(self, async_client: AsyncClient):
        """Test retrieving audit entries."""
        response = await async_client.get("/audit")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_audit_with_filters(self, async_client: AsyncClient):
        """Test retrieving audit entries with filters."""
        response = await async_client.get("/audit?actor=super-agent&limit=10")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_verify_audit_integrity(self, async_client: AsyncClient):
        """Test audit integrity verification."""
        response = await async_client.get("/audit/verify")

        assert response.status_code == 200

        data = response.json()
        assert "valid" in data


class TestStatusEndpoints:
    """Tests for status and info endpoints."""

    @pytest.mark.asyncio
    async def test_status_endpoint(self, async_client: AsyncClient):
        """Test status endpoint."""
        response = await async_client.get("/status")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_agents_endpoint(self, async_client: AsyncClient):
        """Test agents registry endpoint."""
        response = await async_client.get("/agents")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, (list, dict))


class TestCircuitBreakerEndpoints:
    """Tests for circuit breaker status endpoints."""

    @pytest.mark.asyncio
    async def test_circuit_breakers_status(self, async_client: AsyncClient):
        """Test circuit breakers status endpoint."""
        response = await async_client.get("/circuit-breakers")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
