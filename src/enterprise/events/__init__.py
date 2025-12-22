"""
Event and Job Orchestration System

This is the critical infrastructure for "strong gate + reporting":
- Event Log: Webhook events are persisted first, enabling replay and audit
- Job Queue: Separate queues for gate (high priority) and report (low priority)
- Idempotency: Same PR/commit webhook resend won't cause duplicate runs
- Retry/DLQ: Controlled retry for tool/provider failures
- State Machine: Run lifecycle tracking (queued → running → completed/failed)
"""

from enterprise.events.event_log import (
    EventFilter,
    EventLog,
    StoredEvent,
)
from enterprise.events.idempotency import (
    IdempotencyKey,
    IdempotencyManager,
)
from enterprise.events.job_queue import (
    DeadLetterQueue,
    Job,
    JobPriority,
    JobQueue,
    JobStatus,
)
from enterprise.events.state_machine import (
    Run,
    RunState,
    RunStateMachine,
    RunTransition,
)

__all__ = [
    # Event Log
    "EventLog",
    "StoredEvent",
    "EventFilter",
    # Job Queue
    "JobQueue",
    "Job",
    "JobPriority",
    "JobStatus",
    "DeadLetterQueue",
    # Idempotency
    "IdempotencyManager",
    "IdempotencyKey",
    # State Machine
    "RunStateMachine",
    "Run",
    "RunState",
    "RunTransition",
]
