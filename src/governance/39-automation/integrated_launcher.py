#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integrated Governance Automation Launcher

This launcher integrates:
1. Main governance automation launcher (orchestrates all engines)
2. Engine coordinator (manages 14 dimension engines)
3. Existing system launchers (mind_matrix, etc.)

Provides unified startup and coordination of the entire governance
automation ecosystem.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

from governance_automation_launcher import (
    GovernanceAutomationLauncher,
    GovernanceAutomationEngine,
)
from coordinator import EngineCoordinator


class IntegratedGovernanceAutomationLauncher:
    """
    Integrated launcher combining all governance automation components.

    Architecture:
    ```
    IntegratedLauncher
    ├── GovernanceAutomationLauncher (main orchestrator)
    │   └── 14 GovernanceAutomationEngines (dimension engines)
    ├── EngineCoordinator (14 dimension-specific engines)
    │   └── Dimension automation engines
    └── ExistingSystemLaunchers (mind_matrix, etc.)
    ```
    """

    def __init__(self, governance_root: Optional[Path] = None):
        """Initialize integrated launcher."""
        self.governance_root = governance_root or Path(__file__).parent.parent
        self.logger = self._setup_logger()

        # Main launcher
        self.main_launcher: Optional[GovernanceAutomationLauncher] = None

        # Engine coordinator
        self.coordinator: Optional[EngineCoordinator] = None

        # Existing system launchers (to be integrated)
        self.existing_launchers: Dict[str, Any] = {}

        self.is_running = False
        self.integration_status = {
            "main_launcher": False,
            "coordinator": False,
            "existing_launchers": False,
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger("IntegratedGovernanceLauncher")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - [INTEGRATED] %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    async def initialize(self) -> bool:
        """Initialize all components in correct order."""
        self.logger.info("=" * 80)
        self.logger.info("🚀 Initializing Integrated Governance Automation Launcher")
        self.logger.info("=" * 80)

        # Step 1: Initialize main launcher
        self.logger.info("\n📍 Step 1: Initializing Main Governance Automation Launcher...")
        self.main_launcher = GovernanceAutomationLauncher(self.governance_root)
        if not await self.main_launcher.initialize_engines():
            self.logger.error("Failed to initialize main launcher")
            return False
        self.integration_status["main_launcher"] = True
        self.logger.info("✅ Main launcher initialized")

        # Step 2: Initialize engine coordinator
        self.logger.info("\n📍 Step 2: Initializing Engine Coordinator...")
        self.coordinator = EngineCoordinator(self.governance_root, self.logger)
        discovered = self.coordinator.discover_engines()
        initialized = await self.coordinator.initialize_engines_in_order()
        if initialized > 0:
            self.integration_status["coordinator"] = True
            self.logger.info(f"✅ Coordinator initialized with {initialized} engines")
        else:
            self.logger.warning("Coordinator initialized with 0 engines")

        # Step 3: Setup inter-component communication
        self.logger.info("\n📍 Step 3: Setting up inter-component communication...")
        self._setup_communication()
        self.logger.info("✅ Communication channels established")

        # Step 4: Integrate existing launchers
        self.logger.info("\n📍 Step 4: Integrating existing system launchers...")
        self._integrate_existing_launchers()
        self.logger.info("✅ Existing launchers integrated")

        self.logger.info("\n" + "=" * 80)
        self.logger.info("✅ Integrated Launcher Initialization Complete")
        self.logger.info("=" * 80 + "\n")

        return True

    def _setup_communication(self) -> None:
        """Setup communication between main launcher and coordinator."""
        if not self.coordinator:
            return

        # Register handlers for coordinator messages
        async def handle_metrics_request(message):
            """Handle metrics request from engines."""
            metrics = self.main_launcher.get_metrics_report() if self.main_launcher else {}
            return metrics

        async def handle_task_submission(message):
            """Handle task submission from engines."""
            self.logger.info(f"Task submitted: {message.payload}")
            return {"status": "accepted"}

        self.coordinator.register_message_handler("metrics_request", handle_metrics_request)
        self.coordinator.register_message_handler("task_submission", handle_task_submission)

        self.logger.info("Communication channels configured")

    def _integrate_existing_launchers(self) -> None:
        """Integrate existing system launchers."""
        # Check for mind_matrix launcher
        mind_matrix_path = (
            Path(__file__).parent.parent.parent / "runtime" / "mind_matrix" / "main.py"
        )

        if mind_matrix_path.exists():
            self.existing_launchers["mind_matrix"] = {
                "path": str(mind_matrix_path),
                "status": "discovered",
            }
            self.logger.info(f"✅ Found mind_matrix launcher: {mind_matrix_path}")
            self.integration_status["existing_launchers"] = True
        else:
            self.logger.info("mind_matrix launcher not found (optional)")

        # Check for other launchers
        # ...add more as needed

    async def run(self, duration_seconds: Optional[int] = None) -> None:
        """Run all integrated components."""
        if not await self.initialize():
            self.logger.error("Failed to initialize integrated launcher")
            return

        self.is_running = True
        self.logger.info("🎯 Starting Integrated Automation System")

        import time
        start_time = time.time()
        iteration = 0

        try:
            while self.is_running:
                iteration += 1
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"Iteration {iteration}")
                self.logger.info(f"{'='*80}")

                # Process coordinator messages
                if self.coordinator:
                    await self.coordinator.process_messages()
                    if iteration % 5 == 0:
                        await self.coordinator.perform_health_check()

                # Run main launcher cycle
                if self.main_launcher:
                    for engine in self.main_launcher.engines.values():
                        if engine.status.value == "running":
                            await engine.process_tasks()

                # Periodic status reporting
                if iteration % 10 == 0:
                    self._print_integrated_status()

                # Check duration
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    break

                await asyncio.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            await self.shutdown()

    def _print_integrated_status(self) -> None:
        """Print integrated system status."""
        print("\n" + "=" * 100)
        print("🎛️  INTEGRATED GOVERNANCE AUTOMATION SYSTEM STATUS")
        print("=" * 100)

        print("\n📊 Integration Status:")
        print(f"  Main Launcher:       {'✅ Ready' if self.integration_status['main_launcher'] else '❌ Not Ready'}")
        print(f"  Coordinator:         {'✅ Ready' if self.integration_status['coordinator'] else '❌ Not Ready'}")
        print(f"  Existing Launchers:  {'✅ Integrated' if self.integration_status['existing_launchers'] else '⚠️  Optional'}")

        if self.main_launcher:
            main_report = self.main_launcher.get_metrics_report()
            print(f"\n📈 Main Launcher:")
            print(f"  Total Engines:   {main_report['total_engines']}")
            print(f"  Active Engines:  {main_report['active_engines']}")

        if self.coordinator:
            coord_status = self.coordinator.get_coordinator_status()
            print(f"\n🔗 Coordinator:")
            print(f"  Total Engines:       {coord_status['total_engines']}")
            print(f"  Initialized Engines: {coord_status['initialized_engines']}")
            print(f"  Messages Processed:  {coord_status['messages_processed']}")

        print("\n" + "=" * 100 + "\n")

    async def shutdown(self) -> None:
        """Shutdown all components gracefully."""
        self.logger.info("🛑 Initiating integrated shutdown...")
        self.is_running = False

        if self.main_launcher:
            await self.main_launcher.shutdown()

        self._print_integrated_status()
        self.logger.info("✅ Integrated shutdown complete")

    def get_full_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report of all components."""
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "integration_status": self.integration_status,
            "main_launcher": (
                self.main_launcher.get_metrics_report()
                if self.main_launcher else None
            ),
            "coordinator": (
                self.coordinator.get_coordinator_status()
                if self.coordinator else None
            ),
            "existing_launchers": self.existing_launchers,
        }


# ════════════════════════════════════════════════════════════════════════════
# 🚀 Main Entry Point
# ════════════════════════════════════════════════════════════════════════════


async def main():
    """Main entry point for integrated launcher."""
    launcher = IntegratedGovernanceAutomationLauncher()

    try:
        await launcher.run(duration_seconds=45)  # Run for 45 seconds
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
