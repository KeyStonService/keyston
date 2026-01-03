#!/usr/bin/env python3
"""
MachineNativeOps SuperAgent - Multi-Agent Orchestrator

SuperAgent is the central coordinator in the multi-agent MPC architecture.
It handles message routing, state machine management, agent orchestration,
consensus building, and complete audit trail maintenance.

Key Responsibilities:
- Message routing and distribution
- Incident lifecycle state machine management
- Agent coordination and consensus decision making
- Audit trail and provenance tracking
- Prometheus metrics exposition
- Circuit breaker and retry mechanisms
"""

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import uvicorn
from gate_handler import gate_handler

# Local imports
from config import settings
from models.messages import (
    MessageEnvelope,
    MessageType,
    MessageResponse,
    Urgency,
)
from models.incidents import IncidentState, Incident
from models.consensus import VoteType, ConsensusState
from services.state_machine import IncidentStateMachine
from services.event_store import EventStore
from services.audit_trail import AuditTrail, AuditAction
from services.consensus import ConsensusManager
from services.agent_client import AgentClient, AgentRegistry
from utils.metrics import MetricsCollector
from utils.circuit_breaker import CircuitBreakerRegistry
from utils.retry import BackpressureController
from utils.structured_logging import (
    get_logger,
    set_trace_context,
    clear_trace_context,
)

# Initialize logger
logger = get_logger(
    name="super-agent",
    level=settings.log_level,
    format_type=settings.log_format,
)


class SuperAgentCore:
    """
    Core SuperAgent implementation with full feature set.

    Integrates:
    - State machine for incident lifecycle
    - Event store for persistence
    - Audit trail for compliance
    - Consensus for multi-agent decisions
    - Agent client for communication
    - Metrics for observability
    - Circuit breakers for fault tolerance
    """

    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.startup_time = datetime.now()
        self._start_time = datetime.now()
        
        # Initialize core services
        self.metrics = MetricsCollector()
        self.circuit_breakers = CircuitBreakerRegistry()
        self.backpressure = BackpressureController()
        self.event_store = EventStore()
        self.audit_trail = AuditTrail()
        self.agent_registry = AgentRegistry()
        self.agent_client = AgentClient(registry=self.agent_registry)
        self.consensus = ConsensusManager()
        self.state_machine = IncidentStateMachine(event_store=self.event_store)
        
        self.message_handlers = {
            MessageType.INCIDENT_SIGNAL: self.handle_incident_signal,
            MessageType.RCA_REPORT: self.handle_rca_report,
            MessageType.FIX_PROPOSAL: self.handle_fix_proposal,
            MessageType.VERIFICATION_REPORT: self.handle_verification_report,
            MessageType.EXECUTION_RESULT: self.handle_execution_result,
        }
    
    async def initialize(self) -> None:
        """Initialize all services."""
        logger.info("Initializing SuperAgent services...")
        if hasattr(self.event_store, 'initialize'):
            await self.event_store.initialize()
        if hasattr(self.audit_trail, 'initialize'):
            await self.audit_trail.initialize()
        if hasattr(self.metrics, 'initialize'):
            await self.metrics.initialize()
        if hasattr(self.agent_registry, 'initialize'):
            await self.agent_registry.initialize()
        logger.info("SuperAgent services initialized")
    
    async def shutdown(self) -> None:
        """Shutdown all services gracefully."""
        logger.info("Shutting down SuperAgent services...")
        await self.agent_client.close()
        await self.circuit_breakers.reset_all()
        logger.info("SuperAgent services shut down")
        
    def generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return f"mno-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4()}"
    
    def generate_span_id(self) -> str:
        """Generate unique span ID"""
        return str(uuid.uuid4())
    
    def get_uptime(self) -> str:
        """Calculate uptime since startup"""
        uptime_delta = datetime.now() - self.startup_time
        total_seconds = int(uptime_delta.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def validate_message_envelope(self, envelope: MessageEnvelope) -> Tuple[bool, Optional[str]]:
        """Validate message envelope structure and required fields"""
        try:
            meta = envelope.meta
            context = envelope.context

            # Required meta fields
            required_meta = ["trace_id", "source_agent", "target_agent", "message_type"]
            for field in required_meta:
                if field not in meta or not meta[field]:
                    return False, f"Missing required meta field: {field}"

            # Required context fields
            required_context = ["namespace", "cluster"]
            for field in required_context:
                if field not in context or not context[field]:
                    return False, f"Missing required context field: {field}"

            # Validate message type
            try:
                MessageType(meta["message_type"])
            except ValueError:
                return False, f"Invalid message type: {meta['message_type']}"

            # Validate source agent is allowed
            source_agent = meta["source_agent"]
            if source_agent not in settings.allowed_agents:
                return False, f"Unknown source agent: {source_agent}"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def route_message(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Route message to appropriate handler."""
        message_type_str = envelope.meta["message_type"]
        start_time = time.time()

        try:
            message_type = MessageType(message_type_str)

            if message_type not in self.message_handlers:
                logger.warning(f"No handler for message type: {message_type}")
                return {"status": "no_handler", "message_type": message_type_str}

            result = await self.message_handlers[message_type](envelope)

            # Record metrics
            duration = time.time() - start_time
            await self.metrics.record_message(
                message_type=message_type_str,
                source_agent=envelope.meta["source_agent"],
                status="success",
                duration=duration,
            )

            return result

        except Exception as e:
            logger.exception("Message routing failed")

            # Record failure metrics
            duration = time.time() - start_time
            await self.metrics.record_message(
                message_type=message_type_str,
                source_agent=envelope.meta.get("source_agent", "unknown"),
                status="error",
                duration=duration,
            )

            return {"status": "error", "error": "Message routing failed"}

    async def handle_incident_signal(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle incoming incident signal."""
        trace_id = envelope.meta["trace_id"]
        source_agent = envelope.meta["source_agent"]
        payload = envelope.payload

        # Create incident
        incident = await self.state_machine.create_incident(
            trace_id=trace_id,
            incident_type=payload.get("incident_type", "unknown"),
            severity=payload.get("severity", "medium"),
            title=payload.get("title"),
            description=payload.get("description"),
            affected_resources=payload.get("affected_resources", []),
            metadata=payload.get("metadata", {}),
            created_by=source_agent,
        )

        # Transition to TRIAGE
        success, error = await self.state_machine.transition(
            incident_id=incident.incident_id,
            to_state=IncidentState.TRIAGE,
            trigger="incident_signal_received",
            triggered_by=source_agent,
            message_id=envelope.meta.get("idempotency_key"),
        )

        # Record metrics
        await self.metrics.record_incident_created(
            severity=incident.severity,
            incident_type=incident.incident_type,
        )

        logger.info(
            f"Incident created: {incident.incident_id}",
            incident_id=incident.incident_id,
            trace_id=trace_id,
            severity=incident.severity,
        )

        return {
            "status": "created",
            "incident_id": incident.incident_id,
            "trace_id": trace_id,
            "state": incident.state.value,
            "next_action": "severity_assessment",
        }

    async def handle_rca_report(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle RCA report from ProblemSolverAgent."""
        trace_id = envelope.meta["trace_id"]
        source_agent = envelope.meta["source_agent"]
        payload = envelope.payload

        incident = await self.state_machine.find_by_trace_id(trace_id)
        if not incident:
            return {"status": "error", "error": "Incident not found"}

        # Store RCA in event store
        await self.event_store.append(
            event_type="RCAReceived",
            aggregate_type="incident",
            aggregate_id=incident.incident_id,
            trace_id=trace_id,
            data={
                "root_cause": payload.get("root_cause"),
                "analysis": payload.get("analysis"),
                "recommendations": payload.get("recommendations", []),
            },
        )

        # Transition to PROPOSE
        success, error = await self.state_machine.transition(
            incident_id=incident.incident_id,
            to_state=IncidentState.PROPOSE,
            trigger="rca_completed",
            triggered_by=source_agent,
        )

        if not success:
            return {"status": "error", "error": error}

        await self.metrics.record_transition("RCA", "PROPOSE")

        return {
            "status": "processed",
            "incident_id": incident.incident_id,
            "trace_id": trace_id,
            "state": incident.state.value,
            "next_action": "generate_fix_proposals",
        }

    async def handle_fix_proposal(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle fix proposal from ProblemSolverAgent."""
        trace_id = envelope.meta["trace_id"]
        source_agent = envelope.meta["source_agent"]
        payload = envelope.payload

        incident = await self.state_machine.find_by_trace_id(trace_id)
        if not incident:
            return {"status": "error", "error": "Incident not found"}

        proposal_id = payload.get("proposal_id", str(uuid.uuid4()))

        # Store proposal
        await self.event_store.append(
            event_type="FixProposalReceived",
            aggregate_type="incident",
            aggregate_id=incident.incident_id,
            trace_id=trace_id,
            data={
                "proposal_id": proposal_id,
                "proposal": payload.get("proposal"),
                "estimated_risk": payload.get("estimated_risk"),
                "rollback_plan": payload.get("rollback_plan"),
            },
        )

        # Transition to VERIFY
        success, error = await self.state_machine.transition(
            incident_id=incident.incident_id,
            to_state=IncidentState.VERIFY,
            trigger="fix_proposal_received",
            triggered_by=source_agent,
        )

        if not success:
            return {"status": "error", "error": error}

        await self.metrics.record_transition("PROPOSE", "VERIFY")

        return {
            "status": "processed",
            "incident_id": incident.incident_id,
            "trace_id": trace_id,
            "state": incident.state.value,
            "next_action": "verification",
            "proposal_id": proposal_id,
        }

    async def handle_verification_report(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle verification report from QualityAssuranceAgent."""
        trace_id = envelope.meta["trace_id"]
        source_agent = envelope.meta["source_agent"]
        payload = envelope.payload

        incident = await self.state_machine.find_by_trace_id(trace_id)
        if not incident:
            return {"status": "error", "error": "Incident not found"}

        overall_status = payload.get("overall_status", "rejected")

        # Store verification result
        await self.event_store.append(
            event_type="VerificationCompleted",
            aggregate_type="incident",
            aggregate_id=incident.incident_id,
            trace_id=trace_id,
            data={
                "overall_status": overall_status,
                "checks": payload.get("checks", []),
                "issues": payload.get("issues", []),
            },
        )

        if overall_status == "approved":
            # Create consensus request for approval
            consensus_req = await self.consensus.create_request(
                trace_id=trace_id,
                request_type="fix_approval",
                title=f"Approve fix for incident {incident.incident_id}",
                incident_id=incident.incident_id,
                proposal_id=payload.get("proposal_id"),
                requested_by=source_agent,
                timeout_seconds=settings.consensus_timeout,
                payload={"incident": incident.to_dict()},
            )

            # Transition to APPROVE
            success, error = await self.state_machine.transition(
                incident_id=incident.incident_id,
                to_state=IncidentState.APPROVE,
                trigger="verification_passed",
                triggered_by=source_agent,
            )
            next_action = "await_consensus"
            await self.metrics.record_transition("VERIFY", "APPROVE")
        else:
            # Transition back to PROPOSE for refinement
            success, error = await self.state_machine.transition(
                incident_id=incident.incident_id,
                to_state=IncidentState.PROPOSE,
                trigger="verification_failed",
                triggered_by=source_agent,
            )
            next_action = "refine_proposals"
            await self.metrics.record_transition("VERIFY", "PROPOSE")

        return {
            "status": "processed",
            "incident_id": incident.incident_id,
            "trace_id": trace_id,
            "state": incident.state.value,
            "verification_status": overall_status,
            "next_action": next_action,
        }

    async def handle_execution_result(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle execution result from MaintenanceAgent."""
        trace_id = envelope.meta["trace_id"]
        source_agent = envelope.meta["source_agent"]
        payload = envelope.payload

        incident = await self.state_machine.find_by_trace_id(trace_id)
        if not incident:
            return {"status": "error", "error": "Incident not found"}

        execution_status = payload.get("status", "failure")

        # Store execution result
        await self.event_store.append(
            event_type="ExecutionCompleted",
            aggregate_type="incident",
            aggregate_id=incident.incident_id,
            trace_id=trace_id,
            data={
                "status": execution_status,
                "details": payload.get("details"),
                "duration_seconds": payload.get("duration_seconds"),
            },
        )

        if execution_status == "success":
            success, error = await self.state_machine.transition(
                incident_id=incident.incident_id,
                to_state=IncidentState.VALIDATE,
                trigger="execution_succeeded",
                triggered_by=source_agent,
            )
            next_action = "validation"
            await self.metrics.record_transition("EXECUTE", "VALIDATE")
        else:
            success, error = await self.state_machine.transition(
                incident_id=incident.incident_id,
                to_state=IncidentState.ROLLBACK,
                trigger="execution_failed",
                triggered_by=source_agent,
            )
            next_action = "rollback"
            await self.metrics.record_transition("EXECUTE", "ROLLBACK")

        return {
            "status": "processed",
            "incident_id": incident.incident_id,
            "trace_id": trace_id,
            "state": incident.state.value,
            "execution_status": execution_status,
            "next_action": next_action,
        }

    async def handle_consensus_vote(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle consensus vote from agents."""
        trace_id = envelope.meta["trace_id"]
        source_agent = envelope.meta["source_agent"]
        payload = envelope.payload

        consensus_id = payload.get("consensus_id")
        vote_type_str = payload.get("vote_type", "abstain")

        try:
            vote_type = VoteType(vote_type_str)
        except ValueError:
            return {"status": "error", "error": f"Invalid vote type: {vote_type_str}"}

        vote = await self.consensus.submit_vote(
            consensus_id=consensus_id,
            agent_id=source_agent,
            vote_type=vote_type,
            reasoning=payload.get("reasoning"),
            evidence_refs=payload.get("evidence_refs"),
            conditions=payload.get("conditions"),
        )

        if not vote:
            return {"status": "error", "error": "Vote submission failed"}

        # Check if consensus reached
        result = await self.consensus.get_result(consensus_id)
        if result:
            # Handle consensus result
            request = await self.consensus.get_request(consensus_id)
            if request and request.incident_id:
                if result.state == ConsensusState.APPROVED:
                    # Transition to EXECUTE
                    await self.state_machine.transition(
                        incident_id=request.incident_id,
                        to_state=IncidentState.EXECUTE,
                        trigger="consensus_approved",
                        triggered_by="consensus-manager",
                    )
                elif result.state in [ConsensusState.REJECTED, ConsensusState.VETOED]:
                    # Transition back to PROPOSE
                    await self.state_machine.transition(
                        incident_id=request.incident_id,
                        to_state=IncidentState.PROPOSE,
                        trigger="consensus_rejected",
                        triggered_by="consensus-manager",
                    )

        return {
            "status": "accepted",
            "vote_id": vote.vote_id,
            "consensus_id": consensus_id,
            "consensus_state": result.state.value if result else "pending",
        }

    async def handle_heartbeat(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle heartbeat from agents."""
        source_agent = envelope.meta["source_agent"]

        await self.agent_registry.update_status(source_agent, "healthy")

        return {
            "status": "acknowledged",
            "agent": source_agent,
            "timestamp": datetime.now().isoformat(),
        }

    def get_status_summary(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "status": "healthy",
            "version": settings.service_version,
            "namespace": settings.namespace,
            "uptime_seconds": self.metrics.get_uptime(),
            "start_time": self._start_time.isoformat(),
        }


# Global SuperAgent instance
super_agent: Optional[SuperAgentCore] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global super_agent
    super_agent = SuperAgentCore()
    await super_agent.initialize()
    yield
    await super_agent.shutdown()


# FastAPI Application
app = FastAPI(
    title="MachineNativeOps SuperAgent",
    description="Multi-Agent Orchestrator for MachineNativeOps Platform with full feature set",
    version=settings.service_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Middleware for request tracking and metrics."""
    start_time = time.time()
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))

    # Set trace context
    set_trace_context(trace_id=trace_id, request_id=str(uuid.uuid4()))

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Record metrics
        if super_agent:
            await super_agent.metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status=str(response.status_code),
                duration=duration,
            )

        # Add trace ID to response
        response.headers["X-Trace-Id"] = trace_id

        return response
    finally:
        clear_trace_context()


# ==================== API Endpoints ====================

@app.post("/message", response_model=MessageResponse)
async def receive_message(message: MessageEnvelope):
    """Receive and route messages from other agents."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    # Apply backpressure
    await super_agent.backpressure.acquire()

    # Validate message envelope
    is_valid, error = super_agent.validate_message_envelope(message)
    if not is_valid:
        # Log invalid message
        await super_agent.audit_trail.log(
            action=AuditAction.MESSAGE_REJECTED,
            actor=message.meta.get("source_agent", "unknown"),
            trace_id=message.meta.get("trace_id"),
            success=False,
            error_message=error,
        )
        raise HTTPException(status_code=400, detail=error)

    trace_id = message.meta["trace_id"]
    set_trace_context(trace_id=trace_id)

    # Log message received
    await super_agent.audit_trail.log_message_received(
        trace_id=trace_id,
        source_agent=message.meta["source_agent"],
        message_type=message.meta["message_type"],
    )

    # Route message
    result = await super_agent.route_message(message)

    return MessageResponse(
        status="success" if result.get("status") != "error" else "error",
        trace_id=trace_id,
        processing_result=result,
        error=result.get("error"),
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not super_agent:
        return {"status": "starting", "timestamp": datetime.now().isoformat()}

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.service_version,
        "incidents_count": len(super_agent.state_machine),
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Not ready")

    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "message_handlers": [mt.value for mt in super_agent.message_handlers.keys()],
        "event_store": await super_agent.event_store.get_statistics(),
    }


@app.get("/incidents")
async def list_incidents(
    state: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
):
    """List all incidents with optional filters."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    state_filter = IncidentState(state) if state else None
    incidents = await super_agent.state_machine.list_incidents(
        state=state_filter,
        severity=severity,
        limit=limit,
    )

    return {
        "incidents": [i.get_status_summary() for i in incidents],
        "count": len(incidents),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get specific incident details."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    incident = await super_agent.state_machine.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident.to_dict()


@app.get("/incidents/{incident_id}/history")
async def get_incident_history(incident_id: str):
    """Get incident state transition history."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    incident = await super_agent.state_machine.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {
        "incident_id": incident_id,
        "transitions": [t.to_dict() for t in incident.history.transitions],
        "total_transitions": len(incident.history.transitions),
        "duration_seconds": incident.history.get_duration(),
    }


@app.get("/incidents/{incident_id}/audit")
async def get_incident_audit(incident_id: str):
    """Get audit trail for an incident."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    entries = await super_agent.audit_trail.get_incident_audit(incident_id)
    return {
        "incident_id": incident_id,
        "entries": [e.to_dict() for e in entries],
        "count": len(entries),
    }


@app.get("/consensus")
async def list_consensus():
    """List pending consensus requests."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    pending = await super_agent.consensus.get_pending_requests()
    return {
        "pending_requests": [
            {
                "consensus_id": r.consensus_id,
                "request_type": r.request_type,
                "title": r.title,
                "created_at": r.created_at,
                "expires_at": r.expires_at,
            }
            for r in pending
        ],
        "count": len(pending),
    }


@app.get("/consensus/{consensus_id}")
async def get_consensus(consensus_id: str):
    """Get consensus request details."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    request = await super_agent.consensus.get_request(consensus_id)
    if not request:
        raise HTTPException(status_code=404, detail="Consensus request not found")

    result = await super_agent.consensus.get_result(consensus_id)
    votes = await super_agent.consensus.get_votes(consensus_id)

    return {
        "request": request.model_dump(),
        "votes": [v.to_dict() for v in votes],
        "result": result.to_dict() if result else None,
    }


@app.get("/agents")
async def list_agents():
    """List registered agents."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    agents = await super_agent.agent_registry.list_agents()
    return {
        "agents": [
            {
                "agent_id": a.agent_id,
                "url": a.url,
                "status": a.status,
                "last_seen": a.last_seen,
                "capabilities": a.capabilities,
            }
            for a in agents
        ],
        "count": len(agents),
    }


@app.get("/agents/health")
async def check_agents_health():
    """Check health of all registered agents."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    health = await super_agent.agent_client.check_all_health()
    return {
        "agents": health,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/metrics")
async def get_metrics():
    """Get metrics in JSON format."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    await super_agent.metrics.update_uptime()

    # Update incident counts
    stats = await super_agent.state_machine.get_statistics()
    await super_agent.metrics.update_incidents_by_state(stats.get("by_state", {}))

    return {
        "total_incidents": len(super_agent.incidents),
        "incidents_by_state": {
            state.value: sum(1 for inc in super_agent.incidents.values() if inc.state == state)
            for state in IncidentState
        },
        "message_types_supported": [mt.value for mt in MessageType],
        "uptime": super_agent.get_uptime(),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """Get metrics in Prometheus exposition format."""
    if not super_agent:
        return PlainTextResponse("# Service not ready\n", status_code=503)

    await super_agent.metrics.update_uptime()
    return PlainTextResponse(
        super_agent.metrics.prometheus_format(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.get("/audit")
async def get_audit_entries(
    limit: int = 100,
    offset: int = 0,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    trace_id: Optional[str] = None,
):
    """Get audit trail entries."""
    if not super_agent:
        raise HTTPException(status_code=503, detail="Service not ready")

    action_filter = AuditAction(action) if action else None
    entries = await super_agent.audit_trail.get_entries(
        limit=limit,
        offset=offset,
        action=action_filter,
        actor=actor,
        trace_id=trace_id,
    )

    return {
        "entries": [e.to_dict() for e in entries],
        "count": len(entries),
        "offset": offset,
        "limit": limit,
    }

    def handle_gate_validation_request(self, envelope: MessageEnvelope) -> Dict[str, Any]:
        """Handle gate validation requests"""
        try:
            request_data = envelope.payload
            return asyncio.run(gate_handler.handle_gate_validation_request(request_data))
        except Exception as e:
            logger.error(f"Gate validation request failed: {e}")
            return {
                "status": "FAILED",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8082,  # Updated to match unified gates workflow
        reload=True,
        log_level=settings.log_level.lower(),
    )
