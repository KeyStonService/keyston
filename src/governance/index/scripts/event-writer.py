#!/usr/bin/env python3
"""
Event Writer for Governance Index
=================================

Handles event persistence, compression, and vectorization.
Solves the "agent amnesia" problem by ensuring all events are persisted
and available for future agents to read.

Usage:
    python event-writer.py write --type policy.created --data '{"policy": "security"}'
    python event-writer.py compress --threshold 100
    python event-writer.py query "security policy"
    python event-writer.py bootstrap  # Initialize context for new agent

This is a PRODUCTION tool, not a future feature.
"""

import json
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid
import sys


class EventWriter:
    """Handles event persistence and management."""

    def __init__(self, index_path: Optional[Path] = None):
        if index_path is None:
            index_path = Path(__file__).parent.parent

        self.index_path = index_path
        self.events_path = index_path / "events"
        self.registry_path = self.events_path / "registry.json"
        self.session_path = self.events_path / "current-session.json"
        self.vector_path = self.events_path / "vector-index.json"
        self.logs_path = self.events_path / "logs"
        self.compressed_path = self.events_path / "compressed"

        # Ensure directories exist
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.compressed_path.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> Dict:
        """Load JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_json(self, path: Path, data: Dict):
        """Save JSON file with proper formatting."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique = uuid.uuid4().hex[:8]
        return f"evt-{timestamp}-{unique}"

    def generate_embedding(self, text: str, dimension: int = 384) -> List[float]:
        """Generate deterministic embedding for event."""
        text_bytes = text.encode('utf-8')
        embeddings = []
        for i in range(dimension):
            hash_input = text_bytes + i.to_bytes(2, 'big')
            hash_value = hashlib.sha256(hash_input).digest()
            int_value = int.from_bytes(hash_value[:4], 'big')
            float_value = (int_value / (2**32)) * 2 - 1
            embeddings.append(round(float_value, 6))
        norm = sum(x**2 for x in embeddings) ** 0.5
        return [round(x / norm, 6) for x in embeddings]

    def write_event(self, event_type: str, data: Dict,
                    causal_parent: Optional[str] = None,
                    source: str = "agent") -> str:
        """
        Write a new event to the current session.

        Args:
            event_type: Type of event (e.g., "policy.created")
            data: Event data
            causal_parent: ID of the parent event in causal chain
            source: Source of the event

        Returns:
            Event ID
        """
        event_id = self.generate_event_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        event = {
            "id": event_id,
            "type": event_type,
            "timestamp": timestamp,
            "source": source,
            "data": data,
            "causal_parent": causal_parent,
            "status": "completed"
        }

        # Load current session
        session = self._load_json(self.session_path)

        # Add event to session
        if "events" not in session:
            session["events"] = []
        session["events"].append(event)
        session["event_count"] = len(session["events"])
        session["last_event_id"] = event_id

        # Update causal chain
        if "context" not in session:
            session["context"] = {"causal_chain": []}
        if causal_parent:
            session["context"]["causal_chain"].append({
                "parent": causal_parent,
                "child": event_id,
                "type": event_type
            })

        # Save session
        self._save_json(self.session_path, session)

        # Update registry
        registry = self._load_json(self.registry_path)
        registry["statistics"]["total_events"] = registry.get("statistics", {}).get("total_events", 0) + 1
        registry["statistics"]["last_event_id"] = event_id
        registry["statistics"]["last_update"] = timestamp
        self._save_json(self.registry_path, registry)

        # Add to vector index
        self._add_event_vector(event)

        print(f"✓ Event written: {event_id} ({event_type})")
        return event_id

    def _add_event_vector(self, event: Dict):
        """Add event to vector index."""
        vector_data = self._load_json(self.vector_path)

        # Create text representation for embedding
        text = f"{event['type']} {json.dumps(event['data'])}"
        embedding = self.generate_embedding(text)

        vector_entry = {
            "event_id": event["id"],
            "type": event["type"],
            "timestamp": event["timestamp"],
            "embedding": embedding
        }

        if "active_vectors" not in vector_data:
            vector_data["active_vectors"] = []
        vector_data["active_vectors"].append(vector_entry)
        vector_data["statistics"]["total_vectors"] = len(vector_data["active_vectors"])

        self._save_json(self.vector_path, vector_data)

    def compress_events(self, threshold: int = 100) -> int:
        """
        Compress old events into summaries.

        Args:
            threshold: Number of events before compression

        Returns:
            Number of compressed events
        """
        session = self._load_json(self.session_path)
        events = session.get("events", [])

        if len(events) < threshold:
            print(f"Only {len(events)} events, threshold is {threshold}. No compression needed.")
            return 0

        # Keep recent events, compress older ones
        keep_count = threshold // 2
        to_compress = events[:-keep_count]
        to_keep = events[-keep_count:]

        # Create compressed summary
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        compressed_file = f"compressed-{timestamp}.json"

        # Group events by type
        event_summary = {}
        for event in to_compress:
            event_type = event["type"]
            if event_type not in event_summary:
                event_summary[event_type] = {"count": 0, "last_timestamp": None}
            event_summary[event_type]["count"] += 1
            event_summary[event_type]["last_timestamp"] = event["timestamp"]

        compressed_data = {
            "compressed_at": datetime.utcnow().isoformat() + "Z",
            "event_count": len(to_compress),
            "date_range": {
                "start": to_compress[0]["timestamp"] if to_compress else None,
                "end": to_compress[-1]["timestamp"] if to_compress else None
            },
            "summary": event_summary,
            "events": to_compress
        }

        # Save compressed file
        compressed_path = self.compressed_path / compressed_file
        self._save_json(compressed_path, compressed_data)

        # Update session with only kept events
        session["events"] = to_keep
        session["event_count"] = len(to_keep)
        session["context"]["compressed_files"] = session.get("context", {}).get("compressed_files", [])
        session["context"]["compressed_files"].append(compressed_file)
        self._save_json(self.session_path, session)

        # Update registry
        registry = self._load_json(self.registry_path)
        if "files" not in registry:
            registry["files"] = []
        registry["files"].append({
            "file": compressed_file,
            "count": len(to_compress),
            "compressed_at": datetime.utcnow().isoformat() + "Z"
        })
        registry["statistics"]["total_files"] = len(registry["files"])
        self._save_json(self.registry_path, registry)

        # Update vector index
        vector_data = self._load_json(self.vector_path)
        compressed_event_ids = {e["id"] for e in to_compress}
        vector_data["active_vectors"] = [
            v for v in vector_data.get("active_vectors", [])
            if v["event_id"] not in compressed_event_ids
        ]

        # Create compressed vector
        summary_text = " ".join(f"{k}:{v['count']}" for k, v in event_summary.items())
        compressed_vector = {
            "file": compressed_file,
            "event_count": len(to_compress),
            "embedding": self.generate_embedding(summary_text)
        }
        if "compressed_events" not in vector_data:
            vector_data["compressed_events"] = []
        vector_data["compressed_events"].append(compressed_vector)
        vector_data["statistics"]["compressed_count"] = len(vector_data["compressed_events"])
        vector_data["statistics"]["last_compression"] = datetime.utcnow().isoformat() + "Z"
        self._save_json(self.vector_path, vector_data)

        print(f"✓ Compressed {len(to_compress)} events to {compressed_file}")
        return len(to_compress)

    def query_events(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Query events using vector similarity.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of matching events
        """
        query_embedding = self.generate_embedding(query)
        vector_data = self._load_json(self.vector_path)
        session = self._load_json(self.session_path)

        # Calculate similarities
        results = []
        for vector in vector_data.get("active_vectors", []):
            similarity = self._cosine_similarity(query_embedding, vector["embedding"])
            results.append({
                "event_id": vector["event_id"],
                "type": vector["type"],
                "timestamp": vector["timestamp"],
                "similarity": similarity
            })

        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)

        # Get full event data
        events_map = {e["id"]: e for e in session.get("events", [])}
        enriched_results = []
        for r in results[:top_k]:
            if r["event_id"] in events_map:
                enriched_results.append({
                    **r,
                    "data": events_map[r["event_id"]].get("data", {})
                })
            else:
                enriched_results.append(r)

        return enriched_results

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x**2 for x in a) ** 0.5
        norm_b = sum(x**2 for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0

    def bootstrap(self) -> Dict:
        """
        Bootstrap context for a new agent.

        Returns:
            Context dict containing events and related data
        """
        print("=" * 60)
        print("Agent Bootstrap - Loading Event Context")
        print("=" * 60)

        # Load all required resources
        registry = self._load_json(self.registry_path)
        session = self._load_json(self.session_path)
        vectors = self._load_json(self.vector_path)

        # Validate bootstrap contract
        contract_path = self.events_path / "bootstrap-contract.json"
        contract = self._load_json(contract_path)

        validation_passed = True
        for req in contract.get("entry_requirements", {}).get("must_read", []):
            resource = req["resource"]
            if not (self.index_path / resource).exists():
                print(f"✗ Missing required resource: {resource}")
                validation_passed = False
            else:
                print(f"✓ Loaded: {resource}")

        if not validation_passed:
            print("\n✗ Bootstrap validation failed!")
            sys.exit(1)

        # Build context
        context = {
            "session_id": session.get("session_id"),
            "recent_events": session.get("events", [])[-50:],
            "causal_chain": session.get("context", {}).get("causal_chain", []),
            "event_count": session.get("event_count", 0),
            "registry_status": registry.get("metadata", {}).get("status"),
            "vector_count": vectors.get("statistics", {}).get("total_vectors", 0)
        }

        print(f"\n✓ Bootstrap complete!")
        print(f"  Session: {context['session_id']}")
        print(f"  Events loaded: {len(context['recent_events'])}")
        print(f"  Causal chain: {len(context['causal_chain'])} links")
        print(f"  Vectors available: {context['vector_count']}")

        return context

    def close_loop(self, start_event_id: str, end_event_id: str, loop_type: str) -> Dict:
        """
        Close an event loop.

        Args:
            start_event_id: ID of the starting event
            end_event_id: ID of the ending event
            loop_type: Type of loop (e.g., "policy-flow")

        Returns:
            Closed loop record
        """
        session = self._load_json(self.session_path)

        loop_record = {
            "id": f"loop-{self.generate_event_id()}",
            "type": loop_type,
            "start_event": start_event_id,
            "end_event": end_event_id,
            "closed_at": datetime.utcnow().isoformat() + "Z"
        }

        if "closed_loops" not in session:
            session["closed_loops"] = []
        session["closed_loops"].append(loop_record)
        self._save_json(self.session_path, session)

        print(f"✓ Loop closed: {loop_type} ({start_event_id} -> {end_event_id})")
        return loop_record


def main():
    parser = argparse.ArgumentParser(
        description="Event Writer for Governance Index",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Write command
    write_parser = subparsers.add_parser("write", help="Write a new event")
    write_parser.add_argument("--type", "-t", required=True, help="Event type")
    write_parser.add_argument("--data", "-d", default="{}", help="Event data (JSON)")
    write_parser.add_argument("--parent", "-p", help="Causal parent event ID")
    write_parser.add_argument("--source", "-s", default="agent", help="Event source")

    # Compress command
    compress_parser = subparsers.add_parser("compress", help="Compress old events")
    compress_parser.add_argument("--threshold", "-t", type=int, default=100,
                                  help="Compression threshold")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query events")
    query_parser.add_argument("query", help="Search query")
    query_parser.add_argument("--top-k", "-k", type=int, default=10, help="Number of results")

    # Bootstrap command
    subparsers.add_parser("bootstrap", help="Bootstrap agent context")

    # Close loop command
    close_parser = subparsers.add_parser("close-loop", help="Close an event loop")
    close_parser.add_argument("--start", required=True, help="Start event ID")
    close_parser.add_argument("--end", required=True, help="End event ID")
    close_parser.add_argument("--type", required=True, help="Loop type")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    writer = EventWriter()

    if args.command == "write":
        data = json.loads(args.data)
        writer.write_event(args.type, data, args.parent, args.source)

    elif args.command == "compress":
        writer.compress_events(args.threshold)

    elif args.command == "query":
        results = writer.query_events(args.query, args.top_k)
        print(f"\nFound {len(results)} matching events:\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r['type']}] {r['event_id']}")
            print(f"   Similarity: {r['similarity']:.4f}")
            print(f"   Timestamp: {r['timestamp']}")
            if "data" in r:
                print(f"   Data: {json.dumps(r['data'])[:100]}")
            print()

    elif args.command == "bootstrap":
        context = writer.bootstrap()
        print("\nContext injected. Agent ready to execute.")

    elif args.command == "close-loop":
        writer.close_loop(args.start, args.end, args.type)


if __name__ == "__main__":
    main()
