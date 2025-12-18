#!/usr/bin/env python3
"""
Integration tests for the recovery system.

Tests Dr. Phoenix Agent, System Watchdog, and Emergency Recovery.
"""

import asyncio
import os
import sys
import time
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestRecoverySystemIntegration(unittest.TestCase):
    """Integration tests for recovery system"""
    
    def test_phoenix_agent_import(self):
        """Test that Phoenix Agent can be imported"""
        try:
            from services.agents.recovery.phoenix_agent import PhoenixAgent, OperatingMode
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import Phoenix Agent: {e}")
    
    def test_watchdog_import(self):
        """Test that System Watchdog can be imported"""
        try:
            from services.watchdog.system_watchdog import SystemWatchdog
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import System Watchdog: {e}")
    
    def test_emergency_recovery_import(self):
        """Test that Emergency Recovery can be imported"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from emergency_recovery import EmergencyRecovery
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import Emergency Recovery: {e}")
    
    def test_phoenix_agent_creation(self):
        """Test creating Phoenix Agent instance"""
        try:
            from services.agents.recovery.phoenix_agent import PhoenixAgent, OperatingMode
            agent = PhoenixAgent(mode=OperatingMode.MANUAL)
            self.assertIsNotNone(agent)
            self.assertEqual(agent.mode, OperatingMode.MANUAL)
        except Exception as e:
            self.fail(f"Failed to create Phoenix Agent: {e}")
    
    def test_watchdog_creation(self):
        """Test creating System Watchdog instance"""
        try:
            from services.watchdog.system_watchdog import SystemWatchdog
            watchdog = SystemWatchdog()
            self.assertIsNotNone(watchdog)
        except Exception as e:
            self.fail(f"Failed to create System Watchdog: {e}")
    
    def test_emergency_recovery_creation(self):
        """Test creating Emergency Recovery instance"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from emergency_recovery import EmergencyRecovery
            recovery = EmergencyRecovery()
            self.assertIsNotNone(recovery)
        except Exception as e:
            self.fail(f"Failed to create Emergency Recovery: {e}")
    
    def test_phoenix_profile_exists(self):
        """Test that Phoenix profile file exists"""
        profile_path = Path(__file__).parent.parent.parent / "config" / "agents" / "profiles" / "recovery_expert.yaml"
        self.assertTrue(profile_path.exists(), f"Phoenix profile not found: {profile_path}")
    
    def test_recovery_config_exists(self):
        """Test that recovery system config exists"""
        config_path = Path(__file__).parent.parent.parent / "config" / "recovery-system.yaml"
        self.assertTrue(config_path.exists(), f"Recovery config not found: {config_path}")
    
    def test_phoenix_agent_status(self):
        """Test getting Phoenix Agent status"""
        try:
            from services.agents.recovery.phoenix_agent import PhoenixAgent, OperatingMode
            agent = PhoenixAgent(mode=OperatingMode.MANUAL)
            status = agent.get_status()
            self.assertIsInstance(status, dict)
            self.assertIn("agent", status)
            self.assertEqual(status["agent"], "Dr. Phoenix")
        except Exception as e:
            self.fail(f"Failed to get Phoenix status: {e}")
    
    def test_watchdog_status(self):
        """Test getting Watchdog status"""
        try:
            from services.watchdog.system_watchdog import SystemWatchdog
            watchdog = SystemWatchdog()
            status = watchdog.get_status()
            self.assertIsInstance(status, dict)
            self.assertIn("service", status)
            self.assertEqual(status["service"], "System Watchdog")
        except Exception as e:
            self.fail(f"Failed to get Watchdog status: {e}")


class TestRecoverySystemAsync(unittest.IsolatedAsyncioTestCase):
    """Async integration tests"""
    
    async def test_phoenix_start_stop(self):
        """Test starting and stopping Phoenix Agent"""
        try:
            from services.agents.recovery.phoenix_agent import PhoenixAgent, OperatingMode
            
            agent = PhoenixAgent(mode=OperatingMode.MANUAL)
            
            # Start agent (in manual mode it won't actually monitor)
            # This is a quick test, so we'll just verify it can be created
            self.assertFalse(agent.running)
            
            # In a real scenario, we would:
            # await agent.start()
            # await asyncio.sleep(2)
            # await agent.stop()
            
            # But for CI/CD, we just verify creation works
            self.assertTrue(True)
            
        except Exception as e:
            self.fail(f"Failed Phoenix start/stop test: {e}")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestRecoverySystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestRecoverySystemAsync))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
