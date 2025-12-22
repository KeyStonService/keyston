#!/usr/bin/env python3
"""
Message Models for SuperAgent

Defines all message-related data structures including:
- Message types and envelope structure
- Request/response models
- Validation logic
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid


class MessageType(str, Enum):
    """Supported message types in the multi-agent system."""

    # Incident Lifecycle
    INCIDENT_SIGNAL = "IncidentSignal"
    RCA_REPORT = "RCAReport"
    FIX_PROPOSAL = "FixProposal"
    VERIFICATION_REPORT = "VerificationReport"
    APPROVAL_DECISION = "ApprovalDecision"
    EXECUTION_ORDER = "ExecutionOrder"
    EXECUTION_RESULT = "ExecutionResult"

    # Evidence & Audit
    EVIDENCE_BUNDLE_REF = "EvidenceBundleRef"
    AUDIT_EVENT = "AuditEvent"

    # Knowledge Management
    KNOWLEDGE_ARTIFACT_PUBLISHED = "KnowledgeArtifactPublished"

    # Consensus
    CONSENSUS_REQUEST = "ConsensusRequest"
    CONSENSUS_VOTE = "ConsensusVote"
    CONSENSUS_RESULT = "ConsensusResult"

    # Health & Status
    HEARTBEAT = "Heartbeat"
    STATUS_UPDATE = "StatusUpdate"


class Urgency(str, Enum):
    """Priority levels for messages and incidents."""
    P1 = "P1"  # Critical - Immediate action required
    P2 = "P2"  # High - Action within hours
    P3 = "P3"  # Medium - Action within days
    P4 = "P4"  # Low - Scheduled action


class MessageMetadata(BaseModel):
    """Metadata for message envelope."""

    trace_id: str = Field(..., description="Unique trace ID for distributed tracing")
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Span ID")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Message timestamp in ISO 8601 format"
    )
    source_agent: str = Field(..., description="Name of the sending agent")
    target_agent: str = Field(..., description="Name of the receiving agent")
    message_type: MessageType = Field(..., description="Type of message")
    schema_version: str = Field(default="v1.0.0", description="Schema version")
    idempotency_key: Optional[str] = Field(default=None, description="Key for idempotent processing")
    signature: Optional[str] = Field(default=None, description="Ed25519 signature for verification")
    correlation_id: Optional[str] = Field(default=None, description="ID linking related messages")
    reply_to: Optional[str] = Field(default=None, description="Agent to reply to")

    @field_validator("trace_id")
    @classmethod
    def validate_trace_id(cls, v: str) -> str:
        """Validate trace ID format."""
        if not v or len(v) < 10:
            raise ValueError("trace_id must be at least 10 characters")
        return v

    @classmethod
    def generate_trace_id(cls) -> str:
        """Generate a new trace ID."""
        return f"axm-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4()}"


class MessageContext(BaseModel):
    """Context information for message routing and processing."""

    namespace: str = Field(..., description="Kubernetes namespace")
    cluster: str = Field(..., description="Cluster identifier")
    urgency: Optional[Urgency] = Field(default=Urgency.P3, description="Message urgency")
    constraints_ref: Optional[str] = Field(default=None, description="Reference to policy constraints")
    environment: Optional[str] = Field(default="production", description="Environment (prod/staging/dev)")
    region: Optional[str] = Field(default=None, description="Geographic region")
    tags: Optional[Dict[str, str]] = Field(default=None, description="Additional context tags")


class MessageEnvelope(BaseModel):
    """Standard message envelope for all agent communication."""

    meta: Dict[str, Any] = Field(..., description="Message metadata")
    context: Dict[str, Any] = Field(..., description="Message context")
    payload: Dict[str, Any] = Field(..., description="Message payload")

    def get_metadata(self) -> MessageMetadata:
        """Parse metadata into structured object."""
        return MessageMetadata(
            trace_id=self.meta.get("trace_id", ""),
            span_id=self.meta.get("span_id", str(uuid.uuid4())),
            timestamp=self.meta.get("timestamp", datetime.now().isoformat()),
            source_agent=self.meta.get("source_agent", ""),
            target_agent=self.meta.get("target_agent", ""),
            message_type=MessageType(self.meta.get("message_type", "")),
            schema_version=self.meta.get("schema_version", "v1.0.0"),
            idempotency_key=self.meta.get("idempotency_key"),
            signature=self.meta.get("signature"),
            correlation_id=self.meta.get("correlation_id"),
            reply_to=self.meta.get("reply_to"),
        )

    def get_context(self) -> MessageContext:
        """Parse context into structured object."""
        urgency = self.context.get("urgency")
        return MessageContext(
            namespace=self.context.get("namespace", ""),
            cluster=self.context.get("cluster", ""),
            urgency=Urgency(urgency) if urgency else Urgency.P3,
            constraints_ref=self.context.get("constraints_ref"),
            environment=self.context.get("environment", "production"),
            region=self.context.get("region"),
            tags=self.context.get("tags"),
        )

    @classmethod
    def create(
        cls,
        message_type: MessageType,
        payload: Dict[str, Any],
        source_agent: str = "super-agent",
        target_agent: str = "super-agent",
        namespace: str = "axiom-system",
        cluster: str = "default",
        urgency: Urgency = Urgency.P3,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> "MessageEnvelope":
        """Create a new message envelope with default values."""
        return cls(
            meta={
                "trace_id": trace_id or MessageMetadata.generate_trace_id(),
                "span_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source_agent": source_agent,
                "target_agent": target_agent,
                "message_type": message_type.value,
                "schema_version": "v1.0.0",
                "correlation_id": correlation_id,
            },
            context={
                "namespace": namespace,
                "cluster": cluster,
                "urgency": urgency.value,
            },
            payload=payload,
        )


class MessageResponse(BaseModel):
    """Standard response for message processing."""

    status: str = Field(..., description="Processing status (success/error)")
    trace_id: str = Field(..., description="Trace ID from request")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Response timestamp"
    )
    processing_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Processing result details"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_code: Optional[str] = Field(default=None, description="Error code for programmatic handling")
