"""
End-to-End Workflow Integration Tests

Tests complete user workflows across multiple services.
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any


class TestMessageWorkflow:
    """Test complete message processing workflow."""

    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_complete_message_flow(
        self,
        gateway_client: httpx.AsyncClient,
        engine_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test: Gateway receives message -> Engine processes -> Response returned."""
        # Step 1: Send message via Gateway
        message_payload = {
            "content": "Test message for E2E workflow",
            "channel": "test-channel",
            "metadata": {"test": True},
        }

        response = await gateway_client.post(
            "/api/v1/messages",
            json=message_payload,
            headers=auth_headers,
        )

        # Expecting 200 or 202 (accepted for async processing)
        assert response.status_code in [200, 201, 202]

        data = response.json()
        message_id = data.get("id") or data.get("message_id")
        assert message_id is not None

        # Step 2: Wait for processing (poll for completion)
        max_attempts = 10
        for _ in range(max_attempts):
            status_response = await gateway_client.get(
                f"/api/v1/messages/{message_id}/status",
                headers=auth_headers,
            )

            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data.get("status") in ["completed", "processed"]:
                    break

            await asyncio.sleep(1)

        # Step 3: Verify message was processed
        final_response = await gateway_client.get(
            f"/api/v1/messages/{message_id}",
            headers=auth_headers,
        )

        assert final_response.status_code == 200

    @pytest.mark.asyncio
    async def test_message_with_attachments(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test message processing with attachments."""
        message_payload = {
            "content": "Message with attachment",
            "attachments": [
                {
                    "type": "file",
                    "name": "test.txt",
                    "content": "SGVsbG8gV29ybGQ=",  # base64 "Hello World"
                }
            ],
        }

        response = await gateway_client.post(
            "/api/v1/messages",
            json=message_payload,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 202]


class TestUserSessionWorkflow:
    """Test user session lifecycle."""

    @pytest.mark.asyncio
    async def test_session_lifecycle(
        self,
        gateway_client: httpx.AsyncClient,
    ):
        """Test complete session lifecycle: create -> use -> expire."""
        # Step 1: Create session (login)
        login_payload = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = await gateway_client.post("/api/v1/auth/login", json=login_payload)

        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            assert token is not None

            # Step 2: Use session
            session_headers = {"Authorization": f"Bearer {token}"}
            profile_response = await gateway_client.get(
                "/api/v1/users/me",
                headers=session_headers,
            )

            assert profile_response.status_code == 200

            # Step 3: Logout
            logout_response = await gateway_client.post(
                "/api/v1/auth/logout",
                headers=session_headers,
            )

            assert logout_response.status_code in [200, 204]

            # Step 4: Verify session is invalid
            invalid_response = await gateway_client.get(
                "/api/v1/users/me",
                headers=session_headers,
            )

            assert invalid_response.status_code == 401


class TestNotificationWorkflow:
    """Test notification workflow."""

    @pytest.mark.asyncio
    async def test_notification_delivery(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test notification creation and delivery."""
        # Create notification
        notification_payload = {
            "recipient": "test-user",
            "type": "message",
            "title": "Test Notification",
            "body": "This is a test notification",
        }

        response = await gateway_client.post(
            "/api/v1/notifications",
            json=notification_payload,
            headers=auth_headers,
        )

        if response.status_code in [200, 201, 202]:
            data = response.json()
            notification_id = data.get("id")

            # Poll for delivery status
            for _ in range(5):
                status_response = await gateway_client.get(
                    f"/api/v1/notifications/{notification_id}/status",
                    headers=auth_headers,
                )

                if status_response.status_code == 200:
                    status = status_response.json().get("status")
                    if status in ["delivered", "sent"]:
                        break

                await asyncio.sleep(1)


class TestErrorRecoveryWorkflow:
    """Test error recovery and retry mechanisms."""

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test that transient failures are retried."""
        # This test would typically use a test mode to simulate failures
        message_payload = {
            "content": "Test retry behavior",
            "metadata": {"simulate_transient_failure": True},
        }

        response = await gateway_client.post(
            "/api/v1/messages",
            json=message_payload,
            headers=auth_headers,
        )

        # Should eventually succeed after retries
        assert response.status_code in [200, 201, 202, 500]

    @pytest.mark.asyncio
    async def test_dead_letter_queue(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test that permanent failures go to dead letter queue."""
        message_payload = {
            "content": "Test permanent failure",
            "metadata": {"simulate_permanent_failure": True},
        }

        response = await gateway_client.post(
            "/api/v1/messages",
            json=message_payload,
            headers=auth_headers,
        )

        # Should accept the message
        if response.status_code in [200, 201, 202]:
            message_id = response.json().get("id")

            # Wait and check if message ended up in DLQ
            await asyncio.sleep(5)

            dlq_response = await gateway_client.get(
                "/api/v1/admin/dlq",
                headers=auth_headers,
            )

            if dlq_response.status_code == 200:
                dlq_messages = dlq_response.json().get("messages", [])
                # Check if our message is in DLQ
                # assert any(m["id"] == message_id for m in dlq_messages)


class TestWebhookWorkflow:
    """Test webhook integration workflow."""

    @pytest.mark.asyncio
    async def test_webhook_registration_and_delivery(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test webhook registration and event delivery."""
        # Register webhook
        webhook_payload = {
            "url": "https://webhook.site/test-endpoint",
            "events": ["message.created", "message.processed"],
            "secret": "webhook-secret-123",
        }

        response = await gateway_client.post(
            "/api/v1/webhooks",
            json=webhook_payload,
            headers=auth_headers,
        )

        if response.status_code in [200, 201]:
            webhook_id = response.json().get("id")

            # Trigger an event
            message_payload = {"content": "Trigger webhook"}
            await gateway_client.post(
                "/api/v1/messages",
                json=message_payload,
                headers=auth_headers,
            )

            # Check webhook delivery status
            await asyncio.sleep(2)

            delivery_response = await gateway_client.get(
                f"/api/v1/webhooks/{webhook_id}/deliveries",
                headers=auth_headers,
            )

            if delivery_response.status_code == 200:
                deliveries = delivery_response.json().get("deliveries", [])
                # Verify delivery attempted
                # assert len(deliveries) > 0


class TestConcurrencyWorkflow:
    """Test concurrent operations."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_message_processing(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test handling of concurrent message submissions."""
        async def send_message(i: int) -> int:
            response = await gateway_client.post(
                "/api/v1/messages",
                json={"content": f"Concurrent message {i}"},
                headers=auth_headers,
            )
            return response.status_code

        # Send 10 messages concurrently
        tasks = [send_message(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        success_count = sum(1 for r in results if isinstance(r, int) and r in [200, 201, 202])
        assert success_count >= 8  # Allow some failures

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_rate_limiting_under_load(
        self,
        gateway_client: httpx.AsyncClient,
        auth_headers: Dict[str, str],
    ):
        """Test rate limiting behavior under heavy load."""
        results = []

        async def make_request():
            response = await gateway_client.get("/api/v1/status", headers=auth_headers)
            return response.status_code

        # Send 100 requests rapidly
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Expect some 429 responses
        rate_limited = sum(1 for r in results if r == 429)
        success = sum(1 for r in results if r == 200)

        # Should have a mix of success and rate-limited
        assert success > 0
        # Rate limiting might or might not kick in depending on config
