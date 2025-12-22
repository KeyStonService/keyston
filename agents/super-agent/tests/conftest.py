#!/usr/bin/env python3
"""
Pytest Configuration and Fixtures for SuperAgent Tests.
"""

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, superagent_core


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing the API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def initialized_core():
    """Get the SuperAgent core after initialization."""
    # Core is initialized via lifespan, but we need to ensure it's ready
    if superagent_core is None:
        pytest.skip("SuperAgent core not initialized")
    return superagent_core


@pytest.fixture
def sample_message_payload():
    """Sample message payload for testing."""
    return {
        "id": "test-msg-001",
        "type": "INCIDENT_CREATE",
        "source_agent": "test-agent",
        "payload": {
            "title": "Test Incident",
            "description": "Test incident for unit testing",
            "severity": "medium",
        },
        "metadata": {
            "timestamp": "2024-01-15T10:00:00Z",
            "trace_id": "trace-001",
            "span_id": "span-001",
        },
    }


@pytest.fixture
def sample_incident_payload():
    """Sample incident creation payload."""
    return {
        "id": "inc-test-001",
        "title": "Test Incident",
        "description": "A test incident for validation",
        "severity": "high",
        "type": "infrastructure",
        "source_agent": "test-agent",
    }


@pytest.fixture
def sample_vote_payload():
    """Sample consensus vote payload."""
    return {
        "request_id": "req-001",
        "voter_id": "agent-001",
        "vote": "approve",
        "reason": "Looks good to proceed",
    }
