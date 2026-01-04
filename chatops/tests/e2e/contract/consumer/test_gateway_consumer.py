"""
Pact Consumer Tests - Gateway as Consumer of Engine API

These tests define the contract that Gateway expects from Engine.
"""

import pytest
from pact import Consumer, Provider, Like, EachLike, Term


class TestGatewayConsumesEngine:
    """Gateway consuming Engine API contracts."""

    @pytest.fixture
    def pact(self):
        """Set up Pact mock provider."""
        pact = Consumer("ChatOpsGateway").has_pact_with(
            Provider("ChatOpsEngine"),
            host_name="localhost",
            port=1234,
            pact_dir="./pacts",
            log_dir="./logs",
        )
        pact.start_service()
        yield pact
        pact.stop_service()

    def test_process_message(self, pact):
        """Contract: Gateway sends message to Engine for processing."""
        expected_response = {
            "status": "processed",
            "result": {
                "message_id": Like("msg-123"),
                "processed_at": Like("2024-01-15T10:00:00Z"),
                "output": Like("Processed output"),
            },
        }

        (pact
         .given("Engine is available")
         .upon_receiving("a request to process a message")
         .with_request(
             method="POST",
             path="/api/v1/process",
             headers={"Content-Type": "application/json"},
             body={
                 "message_id": Like("msg-123"),
                 "content": Like("Hello, world!"),
                 "metadata": Like({"source": "gateway"}),
             },
         )
         .will_respond_with(200, body=expected_response))

        with pact:
            # Actual HTTP call would go here
            # result = gateway_client.process_message(...)
            pass

    def test_get_processing_status(self, pact):
        """Contract: Gateway checks processing status from Engine."""
        expected_response = {
            "execution_id": Like("exec-123"),
            "status": Term(
                consumer=r"pending|processing|completed|failed",
                generate="completed",
            ),
            "progress": Like(100),
            "result": Like({"data": "result"}),
        }

        (pact
         .given("A processing job exists")
         .upon_receiving("a request for processing status")
         .with_request(
             method="GET",
             path="/api/v1/process/status/exec-123",
             headers={"Accept": "application/json"},
         )
         .will_respond_with(200, body=expected_response))

        with pact:
            pass

    def test_batch_process_messages(self, pact):
        """Contract: Gateway sends batch of messages to Engine."""
        expected_response = {
            "batch_id": Like("batch-123"),
            "results": EachLike({
                "message_id": Like("msg-1"),
                "status": Like("processed"),
            }),
            "total": Like(3),
            "succeeded": Like(3),
            "failed": Like(0),
        }

        (pact
         .given("Engine is available for batch processing")
         .upon_receiving("a batch processing request")
         .with_request(
             method="POST",
             path="/api/v1/process/batch",
             headers={"Content-Type": "application/json"},
             body={
                 "messages": EachLike({
                     "id": Like("msg-1"),
                     "content": Like("Message content"),
                 }),
             },
         )
         .will_respond_with(200, body=expected_response))

        with pact:
            pass

    def test_engine_health_check(self, pact):
        """Contract: Gateway checks Engine health."""
        expected_response = {
            "status": Term(
                consumer=r"healthy|unhealthy|degraded",
                generate="healthy",
            ),
            "checks": Like({
                "database": "healthy",
                "redis": "healthy",
            }),
            "version": Like("1.0.0"),
        }

        (pact
         .given("Engine is running")
         .upon_receiving("a health check request")
         .with_request(
             method="GET",
             path="/health",
         )
         .will_respond_with(200, body=expected_response))

        with pact:
            pass

    def test_engine_error_response(self, pact):
        """Contract: Engine returns error for invalid request."""
        expected_response = {
            "error": {
                "code": Like("VALIDATION_ERROR"),
                "message": Like("Invalid message format"),
                "details": Like([{"field": "content", "error": "required"}]),
            },
        }

        (pact
         .given("Engine validates input")
         .upon_receiving("an invalid message request")
         .with_request(
             method="POST",
             path="/api/v1/process",
             headers={"Content-Type": "application/json"},
             body={},  # Invalid: missing required fields
         )
         .will_respond_with(400, body=expected_response))

        with pact:
            pass


class TestGatewayConsumesNotificationService:
    """Gateway consuming Notification Service contracts."""

    @pytest.fixture
    def pact(self):
        """Set up Pact mock provider for Notification Service."""
        pact = Consumer("ChatOpsGateway").has_pact_with(
            Provider("NotificationService"),
            host_name="localhost",
            port=1235,
            pact_dir="./pacts",
            log_dir="./logs",
        )
        pact.start_service()
        yield pact
        pact.stop_service()

    def test_send_notification(self, pact):
        """Contract: Gateway sends notification request."""
        expected_response = {
            "notification_id": Like("notif-123"),
            "status": Like("queued"),
            "estimated_delivery": Like("2024-01-15T10:00:00Z"),
        }

        (pact
         .given("Notification service is available")
         .upon_receiving("a notification send request")
         .with_request(
             method="POST",
             path="/api/v1/notifications/send",
             headers={"Content-Type": "application/json"},
             body={
                 "recipient": Like("user-123"),
                 "channel": Term(
                     consumer=r"email|sms|push|slack",
                     generate="email",
                 ),
                 "template": Like("welcome"),
                 "data": Like({"name": "John"}),
             },
         )
         .will_respond_with(202, body=expected_response))

        with pact:
            pass
