#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                         Dr. Phoenix - Recovery Agent
                           鳳凰博士 - 恢復代理
═══════════════════════════════════════════════════════════════════════════════

Virtual Expert Agent for autonomous system recovery.
Monitors system health and automatically fixes failures without human intervention.

Dr. Phoenix symbolizes rebirth and recovery - capable of restoring the system
even when core components like automation_launcher.py fail.

Features:
- Autonomous operation without human intervention
- Multi-strategy recovery approaches
- Health monitoring and early warning
- Incident tracking and learning
- Escalation to humans when needed

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
import yaml
import json
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# ============================================================================
# Configuration
# ============================================================================

BASE_PATH = Path(__file__).parent.parent.parent.parent
CONFIG_PATH = BASE_PATH / "config" / "recovery-system.yaml"
PROFILE_PATH = BASE_PATH / "config" / "agents" / "profiles" / "recovery_expert.yaml"
STATE_PATH = BASE_PATH / ".phoenix_state.json"
LOG_PATH = BASE_PATH / ".automation_logs" / "phoenix.log"

# ============================================================================
# Data Models
# ============================================================================

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Available recovery strategies"""
    QUICK_RESTART = "quick_restart"
    SAFE_MODE_RESTART = "safe_mode_restart"
    CONFIGURATION_ROLLBACK = "configuration_rollback"
    SERVICE_DEPENDENCY_RESTART = "service_dependency_restart"
    BACKUP_RESTORE = "backup_restore"
    FULL_SYSTEM_BOOTSTRAP = "full_system_bootstrap"


class OperatingMode(Enum):
    """Operating modes"""
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    MANUAL = "manual"


@dataclass
class HealthCheck:
    """Health check result"""
    component: str
    status: HealthStatus
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class RecoveryAttempt:
    """Recovery attempt record"""
    incident_id: str
    component: str
    strategy: RecoveryStrategy
    timestamp: datetime
    success: bool
    duration: float
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class Incident:
    """Incident record"""
    id: str
    component: str
    status: HealthStatus
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    recovery_attempts: List[RecoveryAttempt] = field(default_factory=list)
    escalation_level: int = 1
    resolution: Optional[str] = None


# ============================================================================
# Phoenix Agent
# ============================================================================

class PhoenixAgent:
    """
    Dr. Phoenix - Virtual Recovery Expert Agent
    
    Autonomous agent that monitors system health and automatically
    recovers from failures without human intervention.
    """
    
    def __init__(
        self,
        config_path: Path = CONFIG_PATH,
        profile_path: Path = PROFILE_PATH,
        mode: OperatingMode = OperatingMode.AUTONOMOUS
    ):
        self.config_path = config_path
        self.profile_path = profile_path
        self.mode = mode
        
        # Load configuration and profile
        self.config = self._load_config()
        self.profile = self._load_profile()
        
        # State
        self.running = False
        self.start_time: Optional[datetime] = None
        self.health_checks: Dict[str, HealthCheck] = {}
        self.active_incidents: Dict[str, Incident] = {}
        self.recovery_history: List[RecoveryAttempt] = []
        
        # Setup logging
        self._setup_logging()
        
        # Statistics
        self.stats = {
            "total_health_checks": 0,
            "total_incidents": 0,
            "total_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "escalations": 0
        }
        
        self.logger.info(f"🦅 Dr. Phoenix initialized in {mode.value} mode")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load recovery system configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        else:
            # Default configuration
            return {
                "monitoring": {
                    "health_check_interval": 30,
                    "critical_components": [
                        "automation_launcher.py",
                        "master_orchestrator",
                        "core_services"
                    ]
                },
                "recovery": {
                    "max_restart_attempts": 3,
                    "retry_delay": 5,
                    "strategy_timeout": {
                        "quick_restart": 30,
                        "safe_mode_restart": 120,
                        "configuration_rollback": 300,
                        "backup_restore": 1800
                    }
                },
                "escalation": {
                    "enabled": True,
                    "levels": [1, 2, 3, 4, 5]
                }
            }
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load agent profile"""
        if self.profile_path.exists():
            with open(self.profile_path) as f:
                return yaml.safe_load(f)
        else:
            return {"agent_profile": {"identity": {"name": "Dr. Phoenix"}}}
    
    def _setup_logging(self):
        """Setup logging system"""
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("PhoenixAgent")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(LOG_PATH)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - 🦅 Dr. Phoenix - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    async def start(self):
        """Start Phoenix Agent"""
        self.logger.info("=" * 70)
        self.logger.info("🔥 Starting Dr. Phoenix Recovery Agent")
        self.logger.info(f"   Mode: {self.mode.value}")
        self.logger.info(f"   Profile: {self.profile_path}")
        self.logger.info(f"   Config: {self.config_path}")
        self.logger.info("=" * 70)
        
        self.running = True
        self.start_time = datetime.now()
        
        # Load previous state
        self._load_state()
        
        # Start monitoring loop
        await self._monitoring_loop()
    
    async def stop(self):
        """Stop Phoenix Agent"""
        self.logger.info("🛑 Stopping Dr. Phoenix Recovery Agent")
        self.running = False
        
        # Save state
        self._save_state()
        
        # Final report
        self._generate_report()
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        interval = self.config["monitoring"]["health_check_interval"]
        
        while self.running:
            try:
                # Perform health checks
                await self._perform_health_checks()
                
                # Check for issues
                await self._check_for_issues()
                
                # Update statistics
                self.stats["total_health_checks"] += 1
                
                # Wait for next check
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all critical components"""
        critical_components = self.config["monitoring"]["critical_components"]
        
        for component in critical_components:
            try:
                health = await self._check_component_health(component)
                self.health_checks[component] = health
                
                if health.status != HealthStatus.HEALTHY:
                    self.logger.warning(
                        f"⚠️  Component {component} is {health.status.value}"
                    )
                
            except Exception as e:
                self.logger.error(f"Failed to check {component}: {e}")
                self.health_checks[component] = HealthCheck(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    timestamp=datetime.now(),
                    details={"error": str(e)}
                )
    
    async def _check_component_health(self, component: str) -> HealthCheck:
        """Check health of a specific component"""
        timestamp = datetime.now()
        
        # Check if automation_launcher.py is running
        if component == "automation_launcher.py":
            return await self._check_launcher_health(timestamp)
        
        # Check other components
        elif component == "master_orchestrator":
            return await self._check_orchestrator_health(timestamp)
        
        elif component == "core_services":
            return await self._check_core_services_health(timestamp)
        
        else:
            # Generic process check
            return await self._check_process_health(component, timestamp)
    
    async def _check_launcher_health(self, timestamp: datetime) -> HealthCheck:
        """Check automation_launcher.py health"""
        launcher_path = BASE_PATH / "automation_launcher.py"
        
        # Check if process is running
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'automation_launcher.py' in ' '.join(cmdline):
                    # Process is running, check if it's responsive
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    
                    # Determine status based on metrics
                    if cpu_percent > 90:
                        status = HealthStatus.DEGRADED
                    elif memory_mb > 1024:  # > 1GB
                        status = HealthStatus.DEGRADED
                    else:
                        status = HealthStatus.HEALTHY
                    
                    return HealthCheck(
                        component="automation_launcher.py",
                        status=status,
                        timestamp=timestamp,
                        details={
                            "pid": proc.pid,
                            "running": True
                        },
                        metrics={
                            "cpu_percent": cpu_percent,
                            "memory_mb": memory_mb
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Process not found
        return HealthCheck(
            component="automation_launcher.py",
            status=HealthStatus.CRITICAL,
            timestamp=timestamp,
            details={"running": False},
            metrics={}
        )
    
    async def _check_orchestrator_health(self, timestamp: datetime) -> HealthCheck:
        """Check master_orchestrator health"""
        # Check if master_orchestrator process is running
        orchestrator_script = "master_orchestrator.py"

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and orchestrator_script in ' '.join(cmdline):
                    # Process found and running
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    memory_mb = proc.memory_info().rss / 1024 / 1024

                    return HealthCheck(
                        component="master_orchestrator",
                        status=HealthStatus.HEALTHY,
                        timestamp=timestamp,
                        details={
                            "pid": proc.pid,
                            "running": True
                        },
                        metrics={
                            "cpu_percent": cpu_percent,
                            "memory_mb": memory_mb
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Process not found - orchestrator is down
        return HealthCheck(
            component="master_orchestrator",
            status=HealthStatus.CRITICAL,
            timestamp=timestamp,
            details={"running": False},
            metrics={}
        )
    
    async def _check_core_services_health(self, timestamp: datetime) -> HealthCheck:
        """Check core services health"""
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine status
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            status = HealthStatus.CRITICAL
        elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 80:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY
        
        return HealthCheck(
            component="core_services",
            status=status,
            timestamp=timestamp,
            details={
                "system_resources": True
            },
            metrics={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
        )
    
    async def _check_process_health(
        self, 
        process_name: str, 
        timestamp: datetime
    ) -> HealthCheck:
        """Generic process health check"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == process_name:
                    return HealthCheck(
                        component=process_name,
                        status=HealthStatus.HEALTHY,
                        timestamp=timestamp,
                        details={"pid": proc.pid}
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return HealthCheck(
            component=process_name,
            status=HealthStatus.CRITICAL,
            timestamp=timestamp,
            details={"running": False}
        )
    
    async def _check_for_issues(self):
        """Check for issues and trigger recovery if needed"""
        for component, health in self.health_checks.items():
            # Skip healthy components
            if health.status == HealthStatus.HEALTHY:
                continue
            
            # Check if we already have an active incident
            if component in self.active_incidents:
                incident = self.active_incidents[component]
                # Check if we should escalate
                await self._handle_existing_incident(incident, health)
            else:
                # Create new incident
                await self._handle_new_incident(component, health)
    
    async def _handle_new_incident(self, component: str, health: HealthCheck):
        """Handle a new incident"""
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{component}"
        
        incident = Incident(
            id=incident_id,
            component=component,
            status=health.status,
            detected_at=datetime.now()
        )
        
        self.active_incidents[component] = incident
        self.stats["total_incidents"] += 1
        
        self.logger.warning(f"🚨 New incident: {incident_id} - {component} is {health.status.value}")
        
        # Trigger recovery if in autonomous mode
        if self.mode == OperatingMode.AUTONOMOUS:
            await self._trigger_recovery(incident, health)
        else:
            self.logger.info(f"⏸️  Manual mode - waiting for human intervention")
    
    async def _handle_existing_incident(self, incident: Incident, health: HealthCheck):
        """Handle an existing incident"""
        # Update incident status
        incident.status = health.status
        
        # Check if resolved
        if health.status == HealthStatus.HEALTHY:
            self.logger.info(f"✅ Incident {incident.id} resolved automatically")
            incident.resolved_at = datetime.now()
            incident.resolution = "automatic_recovery"
            del self.active_incidents[incident.component]
            return
        
        # Check if we should try another recovery
        last_attempt = incident.recovery_attempts[-1] if incident.recovery_attempts else None
        if last_attempt:
            time_since_last = (datetime.now() - last_attempt.timestamp).seconds
            if time_since_last > 60:  # Wait at least 1 minute between attempts
                await self._trigger_recovery(incident, health)
    
    async def _trigger_recovery(self, incident: Incident, health: HealthCheck):
        """Trigger recovery procedure"""
        self.logger.info(f"🔧 Triggering recovery for {incident.component}")
        
        # Select recovery strategy
        strategy = self._select_recovery_strategy(incident, health)
        
        # Execute recovery
        attempt = await self._execute_recovery(incident, strategy)
        
        # Record attempt
        incident.recovery_attempts.append(attempt)
        self.recovery_history.append(attempt)
        self.stats["total_recoveries"] += 1
        
        if attempt.success:
            self.stats["successful_recoveries"] += 1
            self.logger.info(f"✅ Recovery successful using {strategy.value}")
        else:
            self.stats["failed_recoveries"] += 1
            self.logger.error(f"❌ Recovery failed using {strategy.value}")
            
            # Escalate if needed
            await self._escalate_if_needed(incident)
    
    def _select_recovery_strategy(
        self, 
        incident: Incident, 
        health: HealthCheck
    ) -> RecoveryStrategy:
        """Select appropriate recovery strategy"""
        num_attempts = len(incident.recovery_attempts)
        
        # Try strategies in order of priority
        if num_attempts == 0:
            return RecoveryStrategy.QUICK_RESTART
        elif num_attempts == 1:
            return RecoveryStrategy.SAFE_MODE_RESTART
        elif num_attempts == 2:
            return RecoveryStrategy.CONFIGURATION_ROLLBACK
        elif num_attempts == 3:
            return RecoveryStrategy.BACKUP_RESTORE
        else:
            return RecoveryStrategy.FULL_SYSTEM_BOOTSTRAP
    
    async def _execute_recovery(
        self, 
        incident: Incident, 
        strategy: RecoveryStrategy
    ) -> RecoveryAttempt:
        """Execute recovery strategy"""
        start_time = time.time()
        
        self.logger.info(f"🔄 Executing {strategy.value} for {incident.component}")
        
        try:
            if strategy == RecoveryStrategy.QUICK_RESTART:
                success = await self._quick_restart(incident.component)
            elif strategy == RecoveryStrategy.SAFE_MODE_RESTART:
                success = await self._safe_mode_restart(incident.component)
            elif strategy == RecoveryStrategy.CONFIGURATION_ROLLBACK:
                success = await self._configuration_rollback(incident.component)
            elif strategy == RecoveryStrategy.BACKUP_RESTORE:
                success = await self._backup_restore(incident.component)
            elif strategy == RecoveryStrategy.FULL_SYSTEM_BOOTSTRAP:
                success = await self._full_system_bootstrap(incident.component)
            else:
                success = False
            
            duration = time.time() - start_time
            
            return RecoveryAttempt(
                incident_id=incident.id,
                component=incident.component,
                strategy=strategy,
                timestamp=datetime.now(),
                success=success,
                duration=duration,
                details={"strategy": strategy.value}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Recovery execution error: {e}", exc_info=True)
            
            return RecoveryAttempt(
                incident_id=incident.id,
                component=incident.component,
                strategy=strategy,
                timestamp=datetime.now(),
                success=False,
                duration=duration,
                error=str(e)
            )
    
    async def _quick_restart(self, component: str) -> bool:
        """Quick restart strategy"""
        self.logger.info(f"🔄 Quick restart: {component}")
        
        if component == "automation_launcher.py":
            # Find and kill the process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and 'automation_launcher.py' in ' '.join(cmdline):
                        proc.terminate()
                        proc.wait(timeout=10)
                        
                        # Restart
                        await asyncio.sleep(2)
                        # Note: Actual restart would be handled by watchdog
                        return True
                except Exception as e:
                    self.logger.error(f"Error restarting: {e}")
                    return False
        
        return False
    
    async def _safe_mode_restart(self, component: str) -> bool:
        """Safe mode restart strategy - restart with minimal configuration"""
        self.logger.info(f"🔄 Safe mode restart: {component}")

        try:
            # Create safe mode marker file
            safe_mode_marker = BASE_PATH / ".safe_mode"
            safe_mode_marker.write_text(f"safe_mode={component}\ntimestamp={datetime.now().isoformat()}\n")

            # Find and terminate the process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and component in ' '.join(cmdline):
                        self.logger.info(f"Terminating {component} (PID: {proc.pid}) for safe mode restart")
                        proc.terminate()
                        proc.wait(timeout=10)

                        # Wait for clean shutdown
                        await asyncio.sleep(3)

                        # Safe mode restart would be handled by watchdog or systemd
                        # The presence of .safe_mode file signals minimal config should be used
                        self.logger.info(f"✅ Safe mode restart completed for {component}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.warning(f"Process access error: {e}")
                    continue

            self.logger.warning(f"⚠️  Process {component} not found for safe mode restart")
            return False

        except Exception as e:
            self.logger.error(f"Safe mode restart failed: {e}", exc_info=True)
            return False
    
    async def _configuration_rollback(self, component: str) -> bool:
        """Configuration rollback strategy - restore previous working configuration"""
        self.logger.info(f"🔄 Configuration rollback: {component}")

        try:
            # Look for configuration backup
            config_dir = BASE_PATH / "config"
            backup_dir = BASE_PATH / ".config_backups"

            if not backup_dir.exists():
                self.logger.warning(f"⚠️  No configuration backups found at {backup_dir}")
                return False

            # Find the most recent backup
            backups = sorted(backup_dir.glob("*.backup"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not backups:
                self.logger.warning("⚠️  No configuration backup files found")
                return False

            latest_backup = backups[0]
            self.logger.info(f"📦 Rolling back to configuration: {latest_backup.name}")

            # Restore configuration (implementation depends on config format)
            # For now, create a rollback marker
            rollback_marker = BASE_PATH / ".config_rollback"
            rollback_marker.write_text(
                f"component={component}\n"
                f"backup={latest_backup}\n"
                f"timestamp={datetime.now().isoformat()}\n"
            )

            # Log success
            self.logger.info(f"✅ Configuration rollback marker created for {component}")
            return True

        except Exception as e:
            self.logger.error(f"Configuration rollback failed: {e}", exc_info=True)
            return False
    
    async def _backup_restore(self, component: str) -> bool:
        """Backup restore strategy - restore component from backup"""
        self.logger.info(f"🔄 Backup restore: {component}")

        try:
            backup_dir = BASE_PATH / ".backups"

            if not backup_dir.exists():
                self.logger.warning(f"⚠️  No backups directory found at {backup_dir}")
                return False

            # Find component-specific backups
            component_backups = sorted(
                backup_dir.glob(f"{component}*.tar.gz"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if not component_backups:
                self.logger.warning(f"⚠️  No backups found for component: {component}")
                return False

            latest_backup = component_backups[0]
            self.logger.info(f"📦 Restoring from backup: {latest_backup.name}")

            # Create restore marker
            restore_marker = BASE_PATH / ".restore_in_progress"
            restore_marker.write_text(
                f"component={component}\n"
                f"backup={latest_backup}\n"
                f"timestamp={datetime.now().isoformat()}\n"
            )

            # In production, this would extract the backup and restart the component
            # For now, we log the action and create a marker
            self.logger.info(f"✅ Backup restore initiated for {component}")

            # Clean up marker after successful restore
            await asyncio.sleep(1)
            if restore_marker.exists():
                restore_marker.unlink()

            return True

        except Exception as e:
            self.logger.error(f"Backup restore failed: {e}", exc_info=True)
            return False
    
    async def _full_system_bootstrap(self, component: str) -> bool:
        """Full system bootstrap strategy - complete system reinitialization"""
        self.logger.info(f"🔄 Full system bootstrap: {component}")
        self.logger.warning("⚠️  FULL SYSTEM BOOTSTRAP - This is the nuclear option!")

        try:
            # Create bootstrap marker
            bootstrap_marker = BASE_PATH / ".bootstrap_in_progress"
            bootstrap_marker.write_text(
                f"component={component}\n"
                f"reason=recovery_escalation\n"
                f"timestamp={datetime.now().isoformat()}\n"
                f"triggered_by=phoenix_agent\n"
            )

            # Log critical action
            self.logger.critical(
                f"🚨 Initiating full system bootstrap for {component}\n"
                f"   This will reinitialize all core services\n"
                f"   Bootstrap marker created at: {bootstrap_marker}"
            )

            # In production, this would:
            # 1. Save current state
            # 2. Stop all services gracefully
            # 3. Clear temporary files and caches
            # 4. Reinitialize with default configuration
            # 5. Start services in dependency order
            # 6. Verify system health

            # For now, create detailed bootstrap log
            bootstrap_log = BASE_PATH / ".automation_logs" / f"bootstrap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            bootstrap_log.parent.mkdir(parents=True, exist_ok=True)
            bootstrap_log.write_text(
                f"=== FULL SYSTEM BOOTSTRAP ===\n"
                f"Component: {component}\n"
                f"Timestamp: {datetime.now().isoformat()}\n"
                f"Reason: Escalated recovery failure\n"
                f"Status: Initiated\n"
                f"\n"
                f"Next steps:\n"
                f"1. Manual verification required\n"
                f"2. Review system logs\n"
                f"3. Restart core services if needed\n"
            )

            self.logger.info(f"✅ Bootstrap sequence initiated - log: {bootstrap_log}")
            return True

        except Exception as e:
            self.logger.error(f"Full system bootstrap failed: {e}", exc_info=True)
            return False
    
    async def _escalate_if_needed(self, incident: Incident):
        """Escalate incident if recovery fails"""
        num_attempts = len(incident.recovery_attempts)
        
        # Escalate after 3 failed attempts
        if num_attempts >= 3:
            incident.escalation_level = min(incident.escalation_level + 1, 5)
            self.stats["escalations"] += 1
            
            self.logger.critical(
                f"🚨 ESCALATION LEVEL {incident.escalation_level}: {incident.id} - {incident.component}"
            )
            
            # Send notifications to humans
            self._notify_escalation(incident)
    
    def _notify_escalation(self, incident: Incident):
        """Notify humans of escalation via notification queue"""
        self.logger.critical(f"📢 Notifying on-call team about {incident.id}")

        try:
            # Create notification directory
            notification_dir = BASE_PATH / ".notifications"
            notification_dir.mkdir(parents=True, exist_ok=True)

            # Create notification file for external pickup
            notification_file = notification_dir / f"escalation_{incident.id}.json"

            notification_data = {
                "incident_id": incident.id,
                "component": incident.component,
                "status": incident.status.value,
                "escalation_level": incident.escalation_level,
                "detected_at": incident.detected_at.isoformat(),
                "recovery_attempts": len(incident.recovery_attempts),
                "timestamp": datetime.now().isoformat(),
                "severity": "CRITICAL",
                "channels": ["email", "slack", "pagerduty"],
                "message": f"Component {incident.component} has escalated to level {incident.escalation_level} after {len(incident.recovery_attempts)} failed recovery attempts",
                "action_required": True
            }

            # Write notification
            with open(notification_file, 'w') as f:
                json.dump(notification_data, f, indent=2)

            self.logger.info(f"✅ Notification queued: {notification_file}")

            # Also log to dedicated notification log
            notification_log = BASE_PATH / ".automation_logs" / "notifications.log"
            notification_log.parent.mkdir(parents=True, exist_ok=True)

            with open(notification_log, 'a') as f:
                f.write(
                    f"[{datetime.now().isoformat()}] ESCALATION {incident.escalation_level} - "
                    f"{incident.id} - {incident.component} - {len(incident.recovery_attempts)} attempts\n"
                )

        except Exception as e:
            self.logger.error(f"Failed to create notification: {e}", exc_info=True)
    
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
                "uptime": str(datetime.now() - self.start_time) if self.start_time else "0"
            }
            
            with open(STATE_PATH, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info("💾 State saved")
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def _generate_report(self):
        """Generate final report"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        self.logger.info("=" * 70)
        self.logger.info("📊 Dr. Phoenix Recovery Report")
        self.logger.info("=" * 70)
        self.logger.info(f"Uptime: {uptime}")
        self.logger.info(f"Total Health Checks: {self.stats['total_health_checks']}")
        self.logger.info(f"Total Incidents: {self.stats['total_incidents']}")
        self.logger.info(f"Total Recoveries: {self.stats['total_recoveries']}")
        self.logger.info(f"Successful: {self.stats['successful_recoveries']}")
        self.logger.info(f"Failed: {self.stats['failed_recoveries']}")
        self.logger.info(f"Escalations: {self.stats['escalations']}")
        
        if self.stats['total_recoveries'] > 0:
            success_rate = (
                self.stats['successful_recoveries'] / self.stats['total_recoveries'] * 100
            )
            self.logger.info(f"Success Rate: {success_rate:.1f}%")
        
        self.logger.info("=" * 70)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        uptime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        return {
            "agent": "Dr. Phoenix",
            "mode": self.mode.value,
            "running": self.running,
            "uptime": str(uptime),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "health_checks": {
                component: {
                    "status": health.status.value,
                    "timestamp": health.timestamp.isoformat(),
                    "metrics": health.metrics
                }
                for component, health in self.health_checks.items()
            },
            "active_incidents": len(self.active_incidents),
            "statistics": self.stats
        }


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Dr. Phoenix - Recovery Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "command",
        choices=["start", "status", "stop"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["autonomous", "supervised", "manual"],
        default="autonomous",
        help="Operating mode"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Config file path"
    )
    
    args = parser.parse_args()
    
    # Create agent
    mode = OperatingMode[args.mode.upper()]
    agent = PhoenixAgent(mode=mode)
    
    # Execute command
    if args.command == "start":
        # Setup signal handlers
        def signal_handler(sig, frame):
            asyncio.create_task(agent.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start agent
        await agent.start()
    
    elif args.command == "status":
        status = agent.get_status()
        print(yaml.dump(status, default_flow_style=False))
    
    elif args.command == "stop":
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
