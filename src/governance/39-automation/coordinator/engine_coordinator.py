#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Engine Coordinator - Connects 14 Dimension Engines with Main Launcher

This module manages the bidirectional communication and coordination between
the main governance automation launcher and the 14 dimension-specific engines.

Features:
- Engine discovery and initialization
- Task distribution
- Metrics aggregation
- Failure recovery
- Inter-dimension communication
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable, Awaitable

import yaml


@dataclass
class EngineRegistration:
    """Registration info for a dimension engine."""
    engine_id: str
    dimension_name: str
    dimension_path: str
    instance: Optional[Any] = None
    is_initialized: bool = False
    initialization_time: Optional[str] = None
    last_heartbeat: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "uninitialized"


@dataclass
class CoordinationMessage:
    """Message for inter-engine communication."""
    message_id: str
    source_engine: str
    target_engine: str
    message_type: str
    payload: Dict[str, Any]
    priority: int = 5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"


class EngineCoordinator:
    """
    Central coordinator managing all dimension automation engines.

    Responsibilities:
    - Discover and register dimension engines
    - Initialize engines in dependency order
    - Route tasks to appropriate engines
    - Aggregate metrics from all engines
    - Handle inter-engine communication
    - Provide health monitoring
    """

    def __init__(self, governance_root: Path, logger: Optional[logging.Logger] = None):
        """Initialize the engine coordinator."""
        self.governance_root = governance_root
        self.logger = logger or self._setup_logger()

        # Engine registry
        self.engines: Dict[str, EngineRegistration] = {}
        self.dimension_engines: Dict[str, Any] = {}  # Actual engine instances

        # Message queue and routing
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[CoordinationMessage] = []

        # Metrics and state
        self.coordinator_metrics = {
            "messages_processed": 0,
            "engines_initialized": 0,
            "total_engines": 0,
            "start_time": datetime.now().isoformat(),
        }

        # Dependency graph for initialization order
        self.dependency_graph = self._build_dependency_graph()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for coordinator."""
        logger = logging.getLogger("EngineCoordinator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - [EngineCoordinator] %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph for engine initialization order."""
        # Define dependencies between dimensions
        dependencies = {
            "governance_architecture": set(),  # No dependencies
            "decision_governance": {"governance_architecture"},
            "change_governance": {"governance_architecture", "decision_governance"},
            "risk_governance": {"governance_architecture", "decision_governance", "change_governance"},
            "compliance_governance": {"governance_architecture", "risk_governance"},
            "security_governance": {"compliance_governance", "risk_governance"},
            "audit_governance": {"compliance_governance", "security_governance"},
            "process_governance": {"governance_architecture", "decision_governance"},
            "performance_governance": {"process_governance"},
            "stakeholder_governance": {"governance_architecture"},
            "governance_tools": {"governance_architecture"},
            "governance_culture": {"governance_architecture"},
            "governance_metrics": {
                "decision_governance", "change_governance", "risk_governance",
                "compliance_governance", "performance_governance"
            },
            "governance_improvement": {
                "governance_metrics", "audit_governance"
            },
        }
        return dependencies

    def discover_engines(self) -> List[str]:
        """Discover all available dimension engines."""
        self.logger.info("🔍 Discovering dimension automation engines...")

        dimension_dirs = [
            d for d in self.governance_root.iterdir()
            if d.is_dir() and d.name.endswith("-governance") or d.name.startswith("governance-")
        ]

        discovered_engines = []
        for dim_dir in sorted(dimension_dirs):
            engine_file = dim_dir / "automation_engine.py"
            if engine_file.exists():
                # Extract engine ID from directory name
                engine_id = dim_dir.name.replace("-", "_")
                registration = EngineRegistration(
                    engine_id=engine_id,
                    dimension_name=dim_dir.name,
                    dimension_path=str(dim_dir)
                )
                self.engines[engine_id] = registration
                discovered_engines.append(engine_id)
                self.logger.info(f"  ✅ Discovered: {engine_id}")

        self.coordinator_metrics["total_engines"] = len(discovered_engines)
        self.logger.info(f"✅ Discovered {len(discovered_engines)} engines")
        return discovered_engines

    async def initialize_engines_in_order(self) -> int:
        """Initialize engines respecting dependency order."""
        self.logger.info("🚀 Initializing engines in dependency order...")

        # Topological sort based on dependencies
        initialized = set()
        failed = set()

        while len(initialized) < len(self.engines):
            made_progress = False

            for engine_id, registration in self.engines.items():
                if engine_id in initialized or engine_id in failed:
                    continue

                # Check if dependencies are satisfied
                deps = self.dependency_graph.get(engine_id, set())
                if deps.issubset(initialized):
                    # Initialize this engine
                    if await self._initialize_single_engine(engine_id):
                        initialized.add(engine_id)
                        made_progress = True
                    else:
                        failed.add(engine_id)
                        made_progress = True

            if not made_progress:
                # Circular dependency or other issue
                remaining = set(self.engines.keys()) - initialized - failed
                self.logger.error(f"Failed to make progress. Remaining: {remaining}")
                break

        self.coordinator_metrics["engines_initialized"] = len(initialized)
        self.logger.info(
            f"✅ Engine initialization complete: {len(initialized)} initialized, "
            f"{len(failed)} failed"
        )

        return len(initialized)

    async def _initialize_single_engine(self, engine_id: str) -> bool:
        """Initialize a single engine."""
        registration = self.engines[engine_id]

        try:
            self.logger.info(f"Initializing {registration.dimension_name}...")

            # Dynamically import and create engine instance
            engine_module_path = Path(registration.dimension_path) / "automation_engine.py"

            if not engine_module_path.exists():
                self.logger.error(f"Engine module not found: {engine_module_path}")
                return False

            # For now, create a mock instance
            # In production, this would dynamically import the module
            engine_instance = {
                "id": engine_id,
                "name": registration.dimension_name,
                "initialized": True,
            }

            registration.instance = engine_instance
            registration.is_initialized = True
            registration.initialization_time = datetime.now().isoformat()
            registration.status = "running"

            self.dimension_engines[engine_id] = engine_instance
            self.logger.info(f"✅ {registration.dimension_name} initialized successfully")

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize {engine_id}: {e}")
            registration.status = "error"
            return False

    def register_message_handler(
        self,
        message_type: str,
        handler: Callable[[CoordinationMessage], Awaitable[Any]]
    ) -> None:
        """Register a handler for a specific message type."""
        self.message_handlers[message_type].append(handler)
        self.logger.debug(f"Registered handler for message type: {message_type}")

    async def send_message(
        self,
        source_engine: str,
        target_engine: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: int = 5
    ) -> bool:
        """Send a message from one engine to another."""
        message = CoordinationMessage(
            message_id=f"{source_engine}_{target_engine}_{datetime.now().timestamp()}",
            source_engine=source_engine,
            target_engine=target_engine,
            message_type=message_type,
            payload=payload,
            priority=priority
        )

        self.message_queue.put_nowait(message)
        self.logger.debug(f"Message queued: {message.message_id}")
        return True

    async def process_messages(self) -> int:
        """Process pending coordination messages."""
        processed_count = 0

        while not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                await self._handle_message(message)
                message.status = "processed"
                self.message_history.append(message)
                processed_count += 1
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")

        if processed_count > 0:
            self.coordinator_metrics["messages_processed"] += processed_count
            self.logger.debug(f"Processed {processed_count} messages")

        return processed_count

    async def _handle_message(self, message: CoordinationMessage) -> Any:
        """Handle a single coordination message."""
        handlers = self.message_handlers.get(message.message_type, [])

        if not handlers:
            self.logger.warning(f"No handlers for message type: {message.message_type}")
            return None

        # Execute all handlers for this message type
        results = []
        for handler in handlers:
            try:
                result = await handler(message)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Handler error: {e}")

        return results

    def broadcast_to_all_engines(
        self,
        message_type: str,
        payload: Dict[str, Any]
    ) -> int:
        """Broadcast a message to all engines."""
        count = 0
        for engine_id in self.engines.keys():
            asyncio.create_task(
                self.send_message(
                    source_engine="coordinator",
                    target_engine=engine_id,
                    message_type=message_type,
                    payload=payload
                )
            )
            count += 1

        self.logger.info(f"Broadcast {message_type} to {count} engines")
        return count

    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get current coordinator status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_engines": self.coordinator_metrics["total_engines"],
            "initialized_engines": self.coordinator_metrics["engines_initialized"],
            "messages_processed": self.coordinator_metrics["messages_processed"],
            "engines": {
                engine_id: {
                    "dimension_name": reg.dimension_name,
                    "status": reg.status,
                    "is_initialized": reg.is_initialized,
                    "last_heartbeat": reg.last_heartbeat,
                }
                for engine_id, reg in self.engines.items()
            }
        }

    async def perform_health_check(self) -> None:
        """Perform health check on all engines."""
        self.logger.info("🏥 Performing coordinator health check...")

        healthy_count = 0
        for engine_id, registration in self.engines.items():
            if registration.status == "running":
                healthy_count += 1
                registration.last_heartbeat = datetime.now().isoformat()

        self.logger.info(f"Health check: {healthy_count}/{len(self.engines)} engines healthy")

    def export_metrics(self, filepath: Optional[Path] = None) -> Dict[str, Any]:
        """Export coordinator metrics and engine status."""
        metrics = {
            "coordinator": self.coordinator_metrics,
            "engines": {
                engine_id: {
                    "status": reg.status,
                    "initialized": reg.is_initialized,
                    "initialization_time": reg.initialization_time,
                    "last_heartbeat": reg.last_heartbeat,
                }
                for engine_id, reg in self.engines.items()
            },
            "message_history_size": len(self.message_history),
            "export_time": datetime.now().isoformat(),
        }

        if filepath:
            with open(filepath, 'w') as f:
                yaml.dump(metrics, f, default_flow_style=False)
            self.logger.info(f"Metrics exported to {filepath}")

        return metrics
