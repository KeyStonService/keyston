#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for governance automation system.

Tests:
1. Main launcher initialization
2. Engine coordinator discovery and initialization
3. Inter-engine communication
4. Integrated launcher functionality
"""

import asyncio
import sys
from pathlib import Path

from governance_automation_launcher import GovernanceAutomationLauncher
from coordinator import EngineCoordinator
from integrated_launcher import IntegratedGovernanceAutomationLauncher


async def test_main_launcher():
    """Test main governance automation launcher."""
    print("\n" + "=" * 80)
    print("🧪 Test 1: Main Governance Automation Launcher")
    print("=" * 80)

    launcher = GovernanceAutomationLauncher()

    # Initialize engines
    if not await launcher.initialize_engines():
        print("❌ Failed to initialize main launcher")
        return False

    print(f"✅ Main launcher initialized with {len(launcher.engines)} engines")

    # Check metrics
    metrics = launcher.get_metrics_report()
    print(f"\n📊 Metrics:")
    print(f"  Total Engines: {metrics['total_engines']}")
    print(f"  Active Engines: {metrics['active_engines']}")

    # Cleanup
    await launcher.shutdown()
    print("✅ Main launcher test passed")
    return True


async def test_coordinator():
    """Test engine coordinator."""
    print("\n" + "=" * 80)
    print("🧪 Test 2: Engine Coordinator")
    print("=" * 80)

    governance_root = Path(__file__).parent.parent
    coordinator = EngineCoordinator(governance_root)

    # Discover engines
    discovered = coordinator.discover_engines()
    print(f"✅ Discovered {len(discovered)} engines")

    # Initialize engines
    initialized_count = await coordinator.initialize_engines_in_order()
    print(f"✅ Initialized {initialized_count} engines")

    # Check status
    status = coordinator.get_coordinator_status()
    print(f"\n📊 Coordinator Status:")
    print(f"  Total Engines: {status['total_engines']}")
    print(f"  Initialized Engines: {status['initialized_engines']}")

    print("✅ Coordinator test passed")
    return True


async def test_inter_engine_communication():
    """Test inter-engine communication."""
    print("\n" + "=" * 80)
    print("🧪 Test 3: Inter-Engine Communication")
    print("=" * 80)

    governance_root = Path(__file__).parent.parent
    coordinator = EngineCoordinator(governance_root)
    coordinator.discover_engines()

    # Register message handler
    received_messages = []

    async def test_handler(message):
        received_messages.append(message)
        return {"status": "received"}

    coordinator.register_message_handler("test_message", test_handler)

    # Send test message
    await coordinator.send_message(
        source_engine="engine_1",
        target_engine="engine_2",
        message_type="test_message",
        payload={"test": "data"}
    )

    # Process messages
    await coordinator.process_messages()

    if len(received_messages) > 0:
        print("✅ Message communication test passed")
        return True
    else:
        print("❌ No messages received")
        return False


async def test_integrated_launcher():
    """Test integrated launcher."""
    print("\n" + "=" * 80)
    print("🧪 Test 4: Integrated Launcher")
    print("=" * 80)

    launcher = IntegratedGovernanceAutomationLauncher()

    if not await launcher.initialize():
        print("❌ Failed to initialize integrated launcher")
        return False

    # Check integration status
    print("\n📊 Integration Status:")
    for component, status in launcher.integration_status.items():
        status_str = "✅" if status else "❌"
        print(f"  {component}: {status_str}")

    # Get full report
    report = launcher.get_full_status_report()
    print("\n✅ Integrated launcher test passed")

    # Cleanup
    if launcher.main_launcher:
        await launcher.main_launcher.shutdown()

    return True


async def main():
    """Run all tests."""
    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║  GOVERNANCE AUTOMATION SYSTEM - COMPREHENSIVE TEST SUITE                  ║")
    print("║  治理自動化系統 - 綜合測試套件                                              ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")

    tests = [
        ("Main Launcher", test_main_launcher),
        ("Coordinator", test_coordinator),
        ("Communication", test_inter_engine_communication),
        ("Integrated Launcher", test_integrated_launcher),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:<30} {status}")

    print(f"\n  Total: {passed}/{total} tests passed")
    print("=" * 80 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
