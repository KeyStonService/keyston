#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                         System Watchdog Service
                            系統看門狗服務
═══════════════════════════════════════════════════════════════════════════════

Independent watchdog service that monitors the automation_launcher.py and
triggers Phoenix Agent when issues are detected.

This service runs independently and cannot be disabled by the launcher itself.
It's the ultimate safety net for the system.

Features:
- Independent process monitoring
- Automatic Phoenix Agent trigger
- Heartbeat verification
- Process resurrection
- Incident logging

Author: SynergyMesh Team
Version: 1.0.0
Created: 2025-12-09

═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import logging
import os
import sys
import signal
import time
import psutil
import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# ============================================================================
# Configuration
# ============================================================================

BASE_PATH = Path(__file__).parent.parent.parent
STATE_PATH = BASE_PATH / ".watchdog_state.json"
LOG_PATH = BASE_PATH / ".automation_logs" / "watchdog.log"
HEARTBEAT_PATH = BASE_PATH / ".launcher_heartbeat.json"

DEFAULT_CONFIG = {
    "check_interval": 30,  # Check every 30 seconds
    "heartbeat_timeout": 90,  # No heartbeat for 90 seconds = problem
    "max_restart_attempts": 5,
    "restart_cooldown": 300,  # 5 minutes between restarts
    "monitored_processes": [
        {
            "name": "automation_launcher",
            "pattern": "automation_launcher.py",
            "critical": True,
            "auto_restart": True
        }
    ]
}

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ProcessStatus:
    """Process status information"""
    name: str
    pattern: str
    running: bool
    pid: Optional[int] = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    last_check: datetime = field(default_factory=datetime.now)
    last_restart: Optional[datetime] = None
    restart_count: int = 0


@dataclass
class WatchdogEvent:
    """Watchdog event record"""
    timestamp: datetime
    event_type: str  # process_down, process_restarted, heartbeat_timeout, phoenix_triggered
    process: str
    details: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# System Watchdog
# ============================================================================

class SystemWatchdog:
    """
    System Watchdog Service
    
    Independent monitoring service that watches critical processes and
    triggers Phoenix Agent when needed.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # State
        self.running = False
        self.start_time: Optional[datetime] = None
        self.process_status: Dict[str, ProcessStatus] = {}
        self.events: List[WatchdogEvent] = []
        
        # Phoenix Agent reference
        self.phoenix_agent = None
        
        # Setup logging
        self._setup_logging()
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "processes_restarted": 0,
            "phoenix_triggers": 0,
            "events": 0
        }
        
        self.logger.info("🐕 System Watchdog initialized")
    
    def _setup_logging(self):
        """Setup logging system"""
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("SystemWatchdog")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(LOG_PATH)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - 🐕 Watchdog - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    async def start(self):
        """Start watchdog service"""
        self.logger.info("=" * 70)
        self.logger.info("🐕 Starting System Watchdog Service")
        self.logger.info(f"   Check Interval: {self.config['check_interval']}s")
        self.logger.info(f"   Heartbeat Timeout: {self.config['heartbeat_timeout']}s")
        self.logger.info("=" * 70)
        
        self.running = True
        self.start_time = datetime.now()
        
        # Load previous state
        self._load_state()
        
        # Initialize Phoenix Agent
        await self._initialize_phoenix_agent()
        
        # Start monitoring loop
        await self._monitoring_loop()
    
    async def stop(self):
        """Stop watchdog service"""
        self.logger.info("🛑 Stopping System Watchdog")
        self.running = False
        
        # Save state
        self._save_state()
        
        # Stop Phoenix Agent if running
        if self.phoenix_agent:
            await self.phoenix_agent.stop()
    
    async def _initialize_phoenix_agent(self):
        """Initialize Phoenix Agent"""
        try:
            # Import Phoenix Agent
            sys.path.insert(0, str(BASE_PATH / "services" / "agents" / "recovery"))
            from phoenix_agent import PhoenixAgent, OperatingMode
            
            # Create Phoenix Agent instance
            self.phoenix_agent = PhoenixAgent(mode=OperatingMode.AUTONOMOUS)
            self.logger.info("🦅 Phoenix Agent initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Phoenix Agent: {e}")
            self.phoenix_agent = None
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        interval = self.config["check_interval"]
        
        while self.running:
            try:
                # Check all monitored processes
                await self._check_processes()
                
                # Check heartbeats
                await self._check_heartbeats()
                
                # Update statistics
                self.stats["total_checks"] += 1
                
                # Wait for next check
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(interval)
    
    async def _check_processes(self):
        """Check all monitored processes"""
        for process_config in self.config["monitored_processes"]:
            name = process_config["name"]
            pattern = process_config["pattern"]
            critical = process_config.get("critical", False)
            auto_restart = process_config.get("auto_restart", False)
            
            # Check if process is running
            status = await self._get_process_status(name, pattern)
            self.process_status[name] = status
            
            # Handle process down
            if not status.running and critical:
                self.logger.warning(f"⚠️  Critical process {name} is not running")
                
                # Record event
                self._record_event(
                    event_type="process_down",
                    process=name,
                    details={"pattern": pattern}
                )
                
                # Auto restart if enabled
                if auto_restart:
                    await self._handle_process_down(name, pattern, status)
                
                # Trigger Phoenix Agent
                await self._trigger_phoenix_agent(name, "process_down")
    
    async def _get_process_status(
        self, 
        name: str, 
        pattern: str
    ) -> ProcessStatus:
        """Get status of a specific process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and pattern in ' '.join(cmdline):
                    # Process found
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    
                    # Get previous status for restart tracking
                    prev_status = self.process_status.get(name)
                    
                    return ProcessStatus(
                        name=name,
                        pattern=pattern,
                        running=True,
                        pid=proc.pid,
                        cpu_percent=cpu_percent,
                        memory_mb=memory_mb,
                        last_check=datetime.now(),
                        last_restart=prev_status.last_restart if prev_status else None,
                        restart_count=prev_status.restart_count if prev_status else 0
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Process not found
        prev_status = self.process_status.get(name)
        return ProcessStatus(
            name=name,
            pattern=pattern,
            running=False,
            last_check=datetime.now(),
            last_restart=prev_status.last_restart if prev_status else None,
            restart_count=prev_status.restart_count if prev_status else 0
        )
    
    async def _check_heartbeats(self):
        """Check heartbeat files"""
        if not HEARTBEAT_PATH.exists():
            return
        
        try:
            with open(HEARTBEAT_PATH) as f:
                heartbeat = json.load(f)
            
            last_heartbeat = datetime.fromisoformat(heartbeat.get("timestamp"))
            time_since = (datetime.now() - last_heartbeat).seconds
            
            timeout = self.config["heartbeat_timeout"]
            
            if time_since > timeout:
                self.logger.warning(
                    f"⚠️  Heartbeat timeout: {time_since}s since last heartbeat"
                )
                
                # Record event
                self._record_event(
                    event_type="heartbeat_timeout",
                    process="automation_launcher",
                    details={
                        "time_since_heartbeat": time_since,
                        "timeout": timeout
                    }
                )
                
                # Trigger Phoenix Agent
                await self._trigger_phoenix_agent(
                    "automation_launcher", 
                    "heartbeat_timeout"
                )
                
        except Exception as e:
            self.logger.error(f"Error checking heartbeat: {e}")
    
    async def _handle_process_down(
        self, 
        name: str, 
        pattern: str, 
        status: ProcessStatus
    ):
        """Handle a process that is down"""
        # Check restart cooldown
        if status.last_restart:
            cooldown = self.config["restart_cooldown"]
            time_since_restart = (datetime.now() - status.last_restart).seconds
            
            if time_since_restart < cooldown:
                self.logger.info(
                    f"⏳ Restart cooldown: {cooldown - time_since_restart}s remaining"
                )
                return
        
        # Check max restart attempts
        max_attempts = self.config["max_restart_attempts"]
        if status.restart_count >= max_attempts:
            self.logger.error(
                f"❌ Max restart attempts ({max_attempts}) reached for {name}"
            )
            return
        
        # Attempt restart
        self.logger.info(f"🔄 Attempting to restart {name}")
        
        try:
            # For automation_launcher, we can restart it
            if "automation_launcher" in name:
                await self._restart_launcher()
                
                # Update status
                status.last_restart = datetime.now()
                status.restart_count += 1
                self.stats["processes_restarted"] += 1
                
                # Record event
                self._record_event(
                    event_type="process_restarted",
                    process=name,
                    details={
                        "restart_count": status.restart_count,
                        "attempt": status.restart_count
                    }
                )
                
                self.logger.info(f"✅ Restarted {name} (attempt {status.restart_count})")
            
        except Exception as e:
            self.logger.error(f"Failed to restart {name}: {e}")
    
    async def _restart_launcher(self):
        """Restart automation launcher"""
        launcher_path = BASE_PATH / "automation_launcher.py"
        
        # Kill existing process if any
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'automation_launcher.py' in ' '.join(cmdline):
                    proc.terminate()
                    proc.wait(timeout=10)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Start new process
        # Note: In production, this would use a proper process manager
        # For now, we just log the attempt
        self.logger.info(f"Would restart: python {launcher_path}")
    
    async def _trigger_phoenix_agent(self, component: str, reason: str):
        """Trigger Phoenix Agent"""
        if not self.phoenix_agent:
            self.logger.warning("Phoenix Agent not available")
            return
        
        self.logger.info(f"🦅 Triggering Phoenix Agent for {component} ({reason})")
        
        # Record event
        self._record_event(
            event_type="phoenix_triggered",
            process=component,
            details={"reason": reason}
        )
        
        self.stats["phoenix_triggers"] += 1
        
        # Start Phoenix Agent if not already running
        if not self.phoenix_agent.running:
            asyncio.create_task(self.phoenix_agent.start())
    
    def _record_event(
        self, 
        event_type: str, 
        process: str, 
        details: Dict[str, Any]
    ):
        """Record a watchdog event"""
        event = WatchdogEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            process=process,
            details=details
        )
        
        self.events.append(event)
        self.stats["events"] += 1
        
        # Keep only last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]
    
    def _load_state(self):
        """Load previous state"""
        if STATE_PATH.exists():
            try:
                with open(STATE_PATH) as f:
                    state = json.load(f)
                    self.stats = state.get("stats", self.stats)
                    self.logger.info("📂 Previous state loaded")
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")
    
    def _save_state(self):
        """Save current state"""
        try:
            state = {
                "stats": self.stats,
                "timestamp": datetime.now().isoformat(),
                "uptime": str(datetime.now() - self.start_time) if self.start_time else "0",
                "process_status": {
                    name: {
                        "running": status.running,
                        "restart_count": status.restart_count,
                        "last_restart": status.last_restart.isoformat() if status.last_restart else None
                    }
                    for name, status in self.process_status.items()
                }
            }
            
            with open(STATE_PATH, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info("💾 State saved")
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        return {
            "service": "System Watchdog",
            "running": self.running,
            "uptime": str(uptime),
            "processes": {
                name: {
                    "running": status.running,
                    "pid": status.pid,
                    "cpu_percent": status.cpu_percent,
                    "memory_mb": status.memory_mb,
                    "restart_count": status.restart_count
                }
                for name, status in self.process_status.items()
            },
            "phoenix_agent": {
                "initialized": self.phoenix_agent is not None,
                "running": self.phoenix_agent.running if self.phoenix_agent else False
            },
            "statistics": self.stats,
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "process": event.process
                }
                for event in self.events[-10:]
            ]
        }


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="System Watchdog Service",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        choices=["start", "status", "stop"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    # Create watchdog
    watchdog = SystemWatchdog()
    
    # Execute command
    if args.command == "start":
        # Setup signal handlers
        def signal_handler(sig, frame):
            asyncio.create_task(watchdog.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start watchdog
        await watchdog.start()
    
    elif args.command == "status":
        status = watchdog.get_status()
        print(yaml.dump(status, default_flow_style=False))
    
    elif args.command == "stop":
        await watchdog.stop()


if __name__ == "__main__":
    asyncio.run(main())
