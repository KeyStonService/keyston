#!/usr/bin/env python3
"""
Incident State Machine Service for SuperAgent

Manages incident lifecycle with:
- State transition validation
- Transition hooks
- History tracking
- Event emission
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
import asyncio

from ..models.incidents import (
    Incident,
    IncidentState,
    IncidentTransition,
    VALID_TRANSITIONS,
)
from .event_store import EventStore
from .audit_trail import AuditTrail, AuditAction


class TransitionError(Exception):
    """Error during state transition."""

    def __init__(self, message: str, from_state: IncidentState, to_state: IncidentState):
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state


class IncidentStateMachine:
    """
    State machine for incident lifecycle management.

    Provides:
    - State validation
    - Transition execution
    - Pre/post hooks
    - Event store integration
    """

    def __init__(
        self,
        event_store: Optional[EventStore] = None,
        audit_trail: Optional[AuditTrail] = None,
    ):
        self._event_store = event_store
        self._audit_trail = audit_trail
        self._incidents: Dict[str, Incident] = {}
        self._lock = asyncio.Lock()

        # Transition hooks
        self._pre_hooks: Dict[Tuple[IncidentState, IncidentState], List[Callable]] = {}
        self._post_hooks: Dict[Tuple[IncidentState, IncidentState], List[Callable]] = {}

        # State entry/exit hooks
        self._on_enter: Dict[IncidentState, List[Callable]] = {}
        self._on_exit: Dict[IncidentState, List[Callable]] = {}

    async def create_incident(
        self,
        trace_id: str,
        incident_type: str,
        severity: str = "medium",
        title: Optional[str] = None,
        description: Optional[str] = None,
        affected_resources: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: str = "super-agent",
    ) -> Incident:
        """Create a new incident."""
        incident = Incident(
            trace_id=trace_id,
            incident_type=incident_type,
            severity=severity,
            title=title or f"{incident_type} - {trace_id[:20]}",
            description=description,
            affected_resources=affected_resources or [],
            metadata=metadata or {},
        )

        async with self._lock:
            self._incidents[incident.incident_id] = incident

        # Store event
        if self._event_store:
            await self._event_store.append(
                event_type="IncidentCreated",
                aggregate_type="incident",
                aggregate_id=incident.incident_id,
                trace_id=trace_id,
                data=incident.to_dict(),
            )

        # Audit log
        if self._audit_trail:
            await self._audit_trail.log(
                action=AuditAction.INCIDENT_CREATED,
                actor=created_by,
                target=incident.incident_id,
                trace_id=trace_id,
                incident_id=incident.incident_id,
                new_state=incident.state.value,
                details={"incident_type": incident_type, "severity": severity},
            )

        return incident

    async def transition(
        self,
        incident_id: str,
        to_state: IncidentState,
        trigger: str,
        triggered_by: str,
        message_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Transition an incident to a new state.

        Returns (success, error_message).
        """
        async with self._lock:
            incident = self._incidents.get(incident_id)
            if not incident:
                return False, f"Incident {incident_id} not found"

            from_state = incident.state

            # Validate transition
            if not incident.can_transition_to(to_state):
                error = f"Invalid transition from {from_state.value} to {to_state.value}"
                return False, error

            # Execute pre-hooks
            try:
                await self._execute_pre_hooks(incident, from_state, to_state)
            except Exception as e:
                return False, f"Pre-hook failed: {str(e)}"

            # Execute on-exit hooks
            await self._execute_on_exit(incident, from_state)

            # Perform transition
            success = incident.transition_to(
                new_state=to_state,
                trigger=trigger,
                triggered_by=triggered_by,
                message_id=message_id,
                metadata=metadata,
            )

            if not success:
                return False, "Transition failed"

            # Execute on-enter hooks
            await self._execute_on_enter(incident, to_state)

            # Execute post-hooks
            await self._execute_post_hooks(incident, from_state, to_state)

        # Store event
        if self._event_store:
            await self._event_store.append(
                event_type="IncidentTransitioned",
                aggregate_type="incident",
                aggregate_id=incident_id,
                trace_id=incident.trace_id,
                data={
                    "from_state": from_state.value,
                    "to_state": to_state.value,
                    "trigger": trigger,
                    "triggered_by": triggered_by,
                },
            )

        # Audit log
        if self._audit_trail:
            await self._audit_trail.log_incident_transition(
                incident_id=incident_id,
                trace_id=incident.trace_id,
                actor=triggered_by,
                previous_state=from_state.value,
                new_state=to_state.value,
                trigger=trigger,
            )

        return True, None

    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get an incident by ID."""
        async with self._lock:
            return self._incidents.get(incident_id)

    async def find_by_trace_id(self, trace_id: str) -> Optional[Incident]:
        """Find incident by trace ID."""
        async with self._lock:
            for incident in self._incidents.values():
                if incident.trace_id == trace_id:
                    return incident
            return None

    async def list_incidents(
        self,
        state: Optional[IncidentState] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Incident]:
        """List incidents with optional filters."""
        async with self._lock:
            incidents = list(self._incidents.values())

        if state:
            incidents = [i for i in incidents if i.state == state]
        if severity:
            incidents = [i for i in incidents if i.severity == severity]

        # Sort by updated_at descending
        incidents.sort(key=lambda x: x.updated_at, reverse=True)

        return incidents[:limit]

    async def get_statistics(self) -> Dict[str, Any]:
        """Get incident statistics."""
        async with self._lock:
            incidents = list(self._incidents.values())

        if not incidents:
            return {
                "total": 0,
                "by_state": {},
                "by_severity": {},
            }

        by_state: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        open_count = 0
        resolved_count = 0

        for incident in incidents:
            by_state[incident.state.value] = by_state.get(incident.state.value, 0) + 1
            by_severity[incident.severity] = by_severity.get(incident.severity, 0) + 1

            if incident.state in [IncidentState.CLOSE, IncidentState.LEARN]:
                resolved_count += 1
            else:
                open_count += 1

        return {
            "total": len(incidents),
            "open": open_count,
            "resolved": resolved_count,
            "by_state": by_state,
            "by_severity": by_severity,
        }

    def register_pre_hook(
        self,
        from_state: IncidentState,
        to_state: IncidentState,
        hook: Callable,
    ) -> None:
        """Register a pre-transition hook."""
        key = (from_state, to_state)
        if key not in self._pre_hooks:
            self._pre_hooks[key] = []
        self._pre_hooks[key].append(hook)

    def register_post_hook(
        self,
        from_state: IncidentState,
        to_state: IncidentState,
        hook: Callable,
    ) -> None:
        """Register a post-transition hook."""
        key = (from_state, to_state)
        if key not in self._post_hooks:
            self._post_hooks[key] = []
        self._post_hooks[key].append(hook)

    def register_on_enter(self, state: IncidentState, hook: Callable) -> None:
        """Register a state entry hook."""
        if state not in self._on_enter:
            self._on_enter[state] = []
        self._on_enter[state].append(hook)

    def register_on_exit(self, state: IncidentState, hook: Callable) -> None:
        """Register a state exit hook."""
        if state not in self._on_exit:
            self._on_exit[state] = []
        self._on_exit[state].append(hook)

    async def _execute_pre_hooks(
        self,
        incident: Incident,
        from_state: IncidentState,
        to_state: IncidentState,
    ) -> None:
        """Execute pre-transition hooks."""
        hooks = self._pre_hooks.get((from_state, to_state), [])
        for hook in hooks:
            if asyncio.iscoroutinefunction(hook):
                await hook(incident, from_state, to_state)
            else:
                hook(incident, from_state, to_state)

    async def _execute_post_hooks(
        self,
        incident: Incident,
        from_state: IncidentState,
        to_state: IncidentState,
    ) -> None:
        """Execute post-transition hooks."""
        hooks = self._post_hooks.get((from_state, to_state), [])
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(incident, from_state, to_state)
                else:
                    hook(incident, from_state, to_state)
            except Exception:
                pass  # Don't fail on post-hook errors

    async def _execute_on_enter(
        self,
        incident: Incident,
        state: IncidentState,
    ) -> None:
        """Execute state entry hooks."""
        hooks = self._on_enter.get(state, [])
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(incident, state)
                else:
                    hook(incident, state)
            except Exception:
                pass

    async def _execute_on_exit(
        self,
        incident: Incident,
        state: IncidentState,
    ) -> None:
        """Execute state exit hooks."""
        hooks = self._on_exit.get(state, [])
        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(incident, state)
                else:
                    hook(incident, state)
            except Exception:
                pass

    def get_valid_transitions(self, state: IncidentState) -> List[IncidentState]:
        """Get valid transitions from a state."""
        return VALID_TRANSITIONS.get(state, [])

    def __len__(self) -> int:
        """Return number of incidents."""
        return len(self._incidents)
