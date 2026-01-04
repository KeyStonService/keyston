"""
E2E Integration Tests - Pytest Configuration
"""

import os
import pytest
import httpx
import asyncio
from typing import AsyncGenerator, Generator
from dataclasses import dataclass


@dataclass
class TestConfig:
    """Test environment configuration."""
    gateway_url: str
    engine_url: str
    database_url: str
    redis_url: str
    timeout: float = 30.0


@pytest.fixture(scope="session")
def config() -> TestConfig:
    """Load test configuration from environment."""
    return TestConfig(
        gateway_url=os.getenv("CHATOPS_API_URL", "http://localhost:8080"),
        engine_url=os.getenv("CHATOPS_ENGINE_URL", "http://localhost:8000"),
        database_url=os.getenv("DATABASE_URL", "postgresql://chatops:chatops@localhost:5432/chatops_test"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        timeout=float(os.getenv("TEST_TIMEOUT", "30")),
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def gateway_client(config: TestConfig) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async HTTP client for Gateway API."""
    async with httpx.AsyncClient(
        base_url=config.gateway_url,
        timeout=config.timeout,
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def engine_client(config: TestConfig) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async HTTP client for Engine API."""
    async with httpx.AsyncClient(
        base_url=config.engine_url,
        timeout=config.timeout,
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def auth_headers(gateway_client: httpx.AsyncClient) -> dict:
    """Get authentication headers for API requests."""
    # In real tests, this would authenticate and return valid headers
    return {
        "Authorization": "Bearer test-token",
        "X-Request-ID": "test-request-id",
    }


@pytest.fixture(scope="session")
def db_connection(config: TestConfig):
    """Create database connection for direct DB testing."""
    import psycopg2

    conn = psycopg2.connect(config.database_url)
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def redis_client(config: TestConfig):
    """Create Redis client for cache testing."""
    import redis

    client = redis.from_url(config.redis_url)
    yield client
    client.close()


@pytest.fixture(autouse=True)
async def cleanup_test_data(db_connection):
    """Clean up test data after each test."""
    yield
    # Cleanup logic here if needed


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "smoke: marks tests as smoke tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    if config.getoption("--smoke"):
        skip_non_smoke = pytest.mark.skip(reason="Only running smoke tests")
        for item in items:
            if "smoke" not in item.keywords:
                item.add_marker(skip_non_smoke)
