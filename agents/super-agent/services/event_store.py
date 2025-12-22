#!/usr/bin/env python3
"""
Event Store Service for SuperAgent

Provides persistent storage for events with:
- Append-only event log
- Event sourcing support
- Snapshot capabilities
- Query and replay
"""

import json
import sqlite3
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
import uuid
from pathlib import Path


class StoredEvent(BaseModel):
    """Event stored in the event store."""

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event ID"
    )
    event_type: str = Field(..., description="Type of event")
    aggregate_type: str = Field(..., description="Aggregate type (e.g., 'incident')")
    aggregate_id: str = Field(..., description="Aggregate ID")
    sequence_number: int = Field(..., description="Sequence number within aggregate")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Event timestamp"
    )
    trace_id: Optional[str] = Field(default=None, description="Trace ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp,
            "trace_id": self.trace_id,
            "data": self.data,
            "metadata": self.metadata,
        }


class EventStore:
    """
    Event store with support for memory and SQLite backends.

    Provides:
    - Append events
    - Query by aggregate
    - Event replay
    - Snapshot creation
    """

    def __init__(
        self,
        store_type: str = "memory",
        db_path: Optional[str] = None,
        max_events: int = 100000,
    ):
        self._store_type = store_type
        self._db_path = db_path
        self._max_events = max_events
        self._lock = asyncio.Lock()

        # In-memory storage
        self._events: List[StoredEvent] = []
        self._sequence_numbers: Dict[str, int] = {}  # aggregate_id -> last sequence

        # SQLite connection (lazy init)
        self._connection: Optional[sqlite3.Connection] = None

        # Event handlers
        self._handlers: Dict[str, List[Callable]] = {}

    async def initialize(self) -> None:
        """Initialize the event store."""
        if self._store_type == "sqlite" and self._db_path:
            await self._init_sqlite()

    async def _init_sqlite(self) -> None:
        """Initialize SQLite database."""
        path = Path(self._db_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(str(path), check_same_thread=False)
        cursor = self._connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                aggregate_type TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                trace_id TEXT,
                data TEXT NOT NULL,
                metadata TEXT NOT NULL,
                UNIQUE(aggregate_id, sequence_number)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_aggregate
            ON events(aggregate_type, aggregate_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON events(timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trace
            ON events(trace_id)
        """)

        self._connection.commit()

    async def append(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        data: Dict[str, Any],
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoredEvent:
        """Append an event to the store."""
        async with self._lock:
            # Get next sequence number
            key = f"{aggregate_type}:{aggregate_id}"
            sequence = self._sequence_numbers.get(key, 0) + 1
            self._sequence_numbers[key] = sequence

            event = StoredEvent(
                event_type=event_type,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                sequence_number=sequence,
                trace_id=trace_id,
                data=data,
                metadata=metadata or {},
            )

            if self._store_type == "sqlite" and self._connection:
                await self._append_sqlite(event)
            else:
                self._events.append(event)
                # Enforce max events for memory store
                if len(self._events) > self._max_events:
                    self._events = self._events[-self._max_events:]

        # Trigger handlers
        await self._trigger_handlers(event)

        return event

    async def _append_sqlite(self, event: StoredEvent) -> None:
        """Append event to SQLite."""
        if not self._connection:
            return

        cursor = self._connection.cursor()
        cursor.execute(
            """
            INSERT INTO events (
                event_id, event_type, aggregate_type, aggregate_id,
                sequence_number, timestamp, trace_id, data, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_type,
                event.aggregate_type,
                event.aggregate_id,
                event.sequence_number,
                event.timestamp,
                event.trace_id,
                json.dumps(event.data),
                json.dumps(event.metadata),
            ),
        )
        self._connection.commit()

    async def get_events(
        self,
        aggregate_type: Optional[str] = None,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        trace_id: Optional[str] = None,
        from_sequence: Optional[int] = None,
        to_sequence: Optional[int] = None,
        from_timestamp: Optional[str] = None,
        to_timestamp: Optional[str] = None,
        limit: int = 1000,
    ) -> List[StoredEvent]:
        """Query events with filters."""
        if self._store_type == "sqlite" and self._connection:
            return await self._query_sqlite(
                aggregate_type, aggregate_id, event_type, trace_id,
                from_sequence, to_sequence, from_timestamp, to_timestamp, limit
            )

        # In-memory query
        async with self._lock:
            result = list(self._events)

        if aggregate_type:
            result = [e for e in result if e.aggregate_type == aggregate_type]
        if aggregate_id:
            result = [e for e in result if e.aggregate_id == aggregate_id]
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        if trace_id:
            result = [e for e in result if e.trace_id == trace_id]
        if from_sequence:
            result = [e for e in result if e.sequence_number >= from_sequence]
        if to_sequence:
            result = [e for e in result if e.sequence_number <= to_sequence]
        if from_timestamp:
            result = [e for e in result if e.timestamp >= from_timestamp]
        if to_timestamp:
            result = [e for e in result if e.timestamp <= to_timestamp]

        return result[:limit]

    async def _query_sqlite(
        self,
        aggregate_type: Optional[str],
        aggregate_id: Optional[str],
        event_type: Optional[str],
        trace_id: Optional[str],
        from_sequence: Optional[int],
        to_sequence: Optional[int],
        from_timestamp: Optional[str],
        to_timestamp: Optional[str],
        limit: int,
    ) -> List[StoredEvent]:
        """Query SQLite database."""
        if not self._connection:
            return []

        query = "SELECT * FROM events WHERE 1=1"
        params: List[Any] = []

        if aggregate_type:
            query += " AND aggregate_type = ?"
            params.append(aggregate_type)
        if aggregate_id:
            query += " AND aggregate_id = ?"
            params.append(aggregate_id)
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if trace_id:
            query += " AND trace_id = ?"
            params.append(trace_id)
        if from_sequence:
            query += " AND sequence_number >= ?"
            params.append(from_sequence)
        if to_sequence:
            query += " AND sequence_number <= ?"
            params.append(to_sequence)
        if from_timestamp:
            query += " AND timestamp >= ?"
            params.append(from_timestamp)
        if to_timestamp:
            query += " AND timestamp <= ?"
            params.append(to_timestamp)

        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)

        cursor = self._connection.cursor()
        cursor.execute(query, params)

        events = []
        for row in cursor.fetchall():
            events.append(StoredEvent(
                event_id=row[0],
                event_type=row[1],
                aggregate_type=row[2],
                aggregate_id=row[3],
                sequence_number=row[4],
                timestamp=row[5],
                trace_id=row[6],
                data=json.loads(row[7]),
                metadata=json.loads(row[8]),
            ))

        return events

    async def get_aggregate_events(
        self,
        aggregate_type: str,
        aggregate_id: str,
    ) -> List[StoredEvent]:
        """Get all events for an aggregate."""
        return await self.get_events(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            limit=10000,
        )

    async def replay(
        self,
        aggregate_type: str,
        aggregate_id: str,
        handler: Callable[[StoredEvent], None],
    ) -> int:
        """Replay events for an aggregate through a handler."""
        events = await self.get_aggregate_events(aggregate_type, aggregate_id)
        for event in events:
            handler(event)
        return len(events)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def _trigger_handlers(self, event: StoredEvent) -> None:
        """Trigger handlers for an event."""
        handlers = self._handlers.get(event.event_type, [])
        handlers.extend(self._handlers.get("*", []))  # Wildcard handlers

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                pass  # Don't fail on handler errors

    async def get_statistics(self) -> Dict[str, Any]:
        """Get event store statistics."""
        if self._store_type == "sqlite" and self._connection:
            cursor = self._connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT event_type, COUNT(*) FROM events GROUP BY event_type"
            )
            by_type = dict(cursor.fetchall())

            cursor.execute(
                "SELECT aggregate_type, COUNT(*) FROM events GROUP BY aggregate_type"
            )
            by_aggregate = dict(cursor.fetchall())
        else:
            async with self._lock:
                total = len(self._events)
                by_type: Dict[str, int] = {}
                by_aggregate: Dict[str, int] = {}
                for e in self._events:
                    by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
                    by_aggregate[e.aggregate_type] = by_aggregate.get(e.aggregate_type, 0) + 1

        return {
            "total_events": total,
            "store_type": self._store_type,
            "events_by_type": by_type,
            "events_by_aggregate": by_aggregate,
            "aggregates_tracked": len(self._sequence_numbers),
        }

    async def close(self) -> None:
        """Close the event store."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __len__(self) -> int:
        """Return total event count."""
        if self._store_type == "sqlite" and self._connection:
            cursor = self._connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            return cursor.fetchone()[0]
        return len(self._events)
