"""
Gateway API Integration Tests
"""

import pytest
import httpx
from typing import Dict, Any


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_health_endpoint(self, gateway_client: httpx.AsyncClient):
        """Test /health endpoint returns 200."""
        response = await gateway_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_readiness_endpoint(self, gateway_client: httpx.AsyncClient):
        """Test /ready endpoint returns 200 when service is ready."""
        response = await gateway_client.get("/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, gateway_client: httpx.AsyncClient):
        """Test /metrics endpoint returns Prometheus metrics."""
        response = await gateway_client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "http_requests_total" in response.text


class TestAPIVersioning:
    """Test API versioning."""

    @pytest.mark.asyncio
    async def test_v1_api_available(self, gateway_client: httpx.AsyncClient):
        """Test v1 API is accessible."""
        response = await gateway_client.get("/api/v1/status")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_api_version_header(self, gateway_client: httpx.AsyncClient):
        """Test API returns version header."""
        response = await gateway_client.get("/api/v1/status")

        assert "X-API-Version" in response.headers


class TestAuthentication:
    """Test authentication endpoints."""

    @pytest.mark.asyncio
    async def test_unauthenticated_request_rejected(self, gateway_client: httpx.AsyncClient):
        """Test that unauthenticated requests to protected endpoints are rejected."""
        response = await gateway_client.get("/api/v1/protected")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, gateway_client: httpx.AsyncClient):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await gateway_client.get("/api/v1/protected", headers=headers)

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_valid_token_accepted(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test that valid tokens are accepted."""
        response = await gateway_client.get("/api/v1/protected", headers=auth_headers)

        # Assuming the endpoint exists and token is valid
        assert response.status_code != 401


class TestRateLimiting:
    """Test rate limiting."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_rate_limit_headers(self, gateway_client: httpx.AsyncClient):
        """Test that rate limit headers are present."""
        response = await gateway_client.get("/api/v1/status")

        # Check for standard rate limit headers
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]

        for header in rate_limit_headers:
            assert header in response.headers, f"Missing header: {header}"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, gateway_client: httpx.AsyncClient):
        """Test rate limit exceeded response."""
        # This test would need to exceed the rate limit
        # Skipping actual implementation to avoid test pollution
        pytest.skip("Rate limit test requires controlled environment")


class TestCORS:
    """Test CORS configuration."""

    @pytest.mark.asyncio
    async def test_cors_preflight(self, gateway_client: httpx.AsyncClient):
        """Test CORS preflight request."""
        headers = {
            "Origin": "https://app.chatops.example.com",
            "Access-Control-Request-Method": "POST",
        }
        response = await gateway_client.options("/api/v1/status", headers=headers)

        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    @pytest.mark.asyncio
    async def test_cors_allowed_origin(self, gateway_client: httpx.AsyncClient):
        """Test CORS for allowed origin."""
        headers = {"Origin": "https://app.chatops.example.com"}
        response = await gateway_client.get("/api/v1/status", headers=headers)

        assert "Access-Control-Allow-Origin" in response.headers


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_404_response(self, gateway_client: httpx.AsyncClient):
        """Test 404 response for non-existent endpoint."""
        response = await gateway_client.get("/api/v1/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "message" in data

    @pytest.mark.asyncio
    async def test_method_not_allowed(self, gateway_client: httpx.AsyncClient):
        """Test 405 response for wrong HTTP method."""
        response = await gateway_client.delete("/api/v1/status")

        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_invalid_json_body(self, gateway_client: httpx.AsyncClient):
        """Test 400 response for invalid JSON body."""
        response = await gateway_client.post(
            "/api/v1/messages",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400


class TestRequestValidation:
    """Test request validation."""

    @pytest.mark.asyncio
    async def test_missing_required_field(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test validation error for missing required field."""
        response = await gateway_client.post(
            "/api/v1/messages",
            json={},  # Missing required fields
            headers=auth_headers,
        )

        assert response.status_code == 400 or response.status_code == 422
        data = response.json()
        assert "error" in data or "detail" in data

    @pytest.mark.asyncio
    async def test_invalid_field_type(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str]
    ):
        """Test validation error for invalid field type."""
        response = await gateway_client.post(
            "/api/v1/messages",
            json={"content": 123},  # Should be string
            headers=auth_headers,
        )

        assert response.status_code in [400, 422]
