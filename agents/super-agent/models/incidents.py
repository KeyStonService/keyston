#!/usr/bin/env python3
"""
Incident Models for SuperAgent

Defines incident lifecycle data structures including:
- Incident states and transitions
- Incident history and audit
- State machine validation
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class IncidentState(str, Enum):
    """States in the incident lifecycle state machine."""

    OPEN = "OPEN"          # Initial state when incident is created
    TRIAGE = "TRIAGE"      # Severity assessment and categorization
    RCA = "RCA"            # Root cause analysis in progress
    PROPOSE = "PROPOSE"    # Fix proposals being generated
    VERIFY = "VERIFY"      # Proposals under verification
    APPROVE = "APPROVE"    # Waiting for approval
    EXECUTE = "EXECUTE"    # Fix being executed
    VALIDATE = "VALIDATE"  # Validating the fix
    ROLLBACK = "ROLLBACK"  # Rolling back failed fix
    CLOSE = "CLOSE"        # Incident resolved and closed
    LEARN = "LEARN"        # Post-incident learning


# Valid state transitions
VALID_TRANSITIONS: Dict[IncidentState, List[IncidentState]] = {
    IncidentState.OPEN: [IncidentState.TRIAGE],
    IncidentState.TRIAGE: [IncidentState.RCA, IncidentState.CLOSE],
    IncidentState.RCA: [IncidentState.PROPOSE, IncidentState.CLOSE],
    IncidentState.PROPOSE: [IncidentState.VERIFY, IncidentState.RCA],
    IncidentState.VERIFY: [IncidentState.APPROVE, IncidentState.PROPOSE],
    IncidentState.APPROVE: [IncidentState.EXECUTE, IncidentState.PROPOSE],
    IncidentState.EXECUTE: [IncidentState.VALIDATE, IncidentState.ROLLBACK],
    IncidentState.VALIDATE: [IncidentState.CLOSE, IncidentState.ROLLBACK, IncidentState.EXECUTE],
    IncidentState.ROLLBACK: [IncidentState.PROPOSE, IncidentState.CLOSE],
    IncidentState.CLOSE: [IncidentState.LEARN],
    IncidentState.LEARN: [],  # Terminal state
}


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    CRITICAL = "critical"  # Service down, immediate action required
    HIGH = "high"          # Major functionality impaired
    MEDIUM = "medium"      # Degraded performance
    LOW = "low"            # Minor issue


class IncidentTransition(BaseModel):
    """Record of a state transition."""

    from_state: IncidentState = Field(..., description="Previous state")
    to_state: IncidentState = Field(..., description="New state")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Transition timestamp"
    )
    trigger: str = Field(..., description="What triggered the transition")
    triggered_by: str = Field(..., description="Agent or user that triggered transition")
    message_id: Optional[str] = Field(default=None, description="Related message ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional transition data")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "timestamp": self.timestamp,
            "trigger": self.trigger,
            "triggered_by": self.triggered_by,
            "message_id": self.message_id,
            "metadata": self.metadata,
        }


class IncidentHistory(BaseModel):
    """Complete history of an incident."""

    incident_id: str = Field(..., description="Incident identifier")
    transitions: List[IncidentTransition] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list, description="Related message IDs")
    proposals: List[Dict[str, Any]] = Field(default_factory=list, description="Fix proposals")
    evidence: List[str] = Field(default_factory=list, description="Evidence bundle references")

    def add_transition(self, transition: IncidentTransition) -> None:
        """Add a transition to history."""
        self.transitions.append(transition)

    def get_duration(self) -> Optional[float]:
        """Get total duration in seconds from first to last transition."""
        if len(self.transitions) < 2:
            return None
        first = datetime.fromisoformat(self.transitions[0].timestamp)
        last = datetime.fromisoformat(self.transitions[-1].timestamp)
        return (last - first).total_seconds()


class Incident(BaseModel):
    """Core incident model with full lifecycle support."""

    incident_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique incident identifier"
    )
    trace_id: str = Field(..., description="Distributed tracing ID")
    state: IncidentState = Field(default=IncidentState.OPEN, description="Current state")
    incident_type: str = Field(..., description="Type/category of incident")
    severity: str = Field(default="medium", description="Incident severity")
    title: Optional[str] = Field(default=None, description="Short incident title")
    description: Optional[str] = Field(default=None, description="Detailed description")
    affected_resources: List[str] = Field(default_factory=list, description="Affected resources")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp"
    )
    resolved_at: Optional[str] = Field(default=None, description="Resolution timestamp")
    assigned_to: Optional[str] = Field(default=None, description="Assigned agent/user")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    history: IncidentHistory = Field(default=None, description="State transition history")

    def __init__(self, **data):
        super().__init__(**data)
        if self.history is None:
            self.history = IncidentHistory(incident_id=self.incident_id)

    def can_transition_to(self, new_state: IncidentState) -> bool:
        """Check if transition to new state is valid."""
        return new_state in VALID_TRANSITIONS.get(self.state, [])

    def transition_to(
        self,
        new_state: IncidentState,
        trigger: str,
        triggered_by: str,
        message_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Transition to a new state if valid.

        Returns True if transition successful, False otherwise.
        """
        if not self.can_transition_to(new_state):
            return False

        transition = IncidentTransition(
            from_state=self.state,
            to_state=new_state,
            trigger=trigger,
            triggered_by=triggered_by,
            message_id=message_id,
            metadata=metadata or {},
        )

        self.history.add_transition(transition)
        self.state = new_state
        self.updated_at = datetime.now().isoformat()

        if new_state == IncidentState.CLOSE:
            self.resolved_at = datetime.now().isoformat()

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "incident_id": self.incident_id,
            "trace_id": self.trace_id,
            "state": self.state.value,
            "incident_type": self.incident_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "affected_resources": self.affected_resources,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "assigned_to": self.assigned_to,
            "metadata": self.metadata,
            "transition_count": len(self.history.transitions) if self.history else 0,
        }

    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary suitable for API response."""
        return {
            "incident_id": self.incident_id,
            "trace_id": self.trace_id,
            "state": self.state.value,
            "incident_type": self.incident_type,
            "severity": self.severity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "affected_resources": self.affected_resources,
        }
