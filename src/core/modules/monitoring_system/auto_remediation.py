"""
Auto Remediation Engine (自動修復引擎)

Self-healing capabilities with predefined playbooks

Reference: Self-healing infrastructure - Detect → Auto Diagnose → Execute Fix → Verify → Log [9]
"""

import asyncio
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class RemediationStatus(Enum):
    """Status of a remediation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class RemediationType(Enum):
    """Types of remediation actions"""
    RESTART = "restart"           # Restart service/component
    SCALE = "scale"               # Scale up/down
    FAILOVER = "failover"         # Failover to backup
    ROLLBACK = "rollback"         # Rollback changes
    CLEAR_CACHE = "clear_cache"   # Clear caches
    RECONFIGURE = "reconfigure"   # Reconfigure settings
    NOTIFY = "notify"             # Send notifications
    CUSTOM = "custom"             # Custom remediation


@dataclass
class RemediationAction:
    """A remediation action to execute"""
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    action_type: RemediationType = RemediationType.CUSTOM
    target: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    rollback_action: Optional['RemediationAction'] = None
    pre_conditions: list[Callable[[], bool]] = field(default_factory=list)
    post_conditions: list[Callable[[], bool]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'action_id': self.action_id,
            'name': self.name,
            'type': self.action_type.value,
            'target': self.target,
            'parameters': self.parameters,
            'timeout_seconds': self.timeout_seconds,
            'has_rollback': self.rollback_action is not None
        }


@dataclass
class RemediationPlaybook:
    """A playbook defining remediation steps"""
    playbook_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    trigger_conditions: list[str] = field(default_factory=list)
    actions: list[RemediationAction] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    max_retries: int = 3
    cooldown_seconds: int = 300
    last_executed: datetime | None = None

    def is_in_cooldown(self) -> bool:
        """Check if playbook is in cooldown period"""
        if not self.last_executed:
            return False
        elapsed = (datetime.now() - self.last_executed).total_seconds()
        return elapsed < self.cooldown_seconds


@dataclass
class RemediationResult:
    """Result of a remediation execution"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    playbook_id: str = ""
    anomaly_id: str = ""
    status: RemediationStatus = RemediationStatus.PENDING
    actions_executed: list[str] = field(default_factory=list)
    actions_failed: list[str] = field(default_factory=list)
    verification_passed: bool = False
    execution_time_ms: int = 0
    error_message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            'result_id': self.result_id,
            'playbook_id': self.playbook_id,
            'anomaly_id': self.anomaly_id,
            'status': self.status.value,
            'actions_executed': self.actions_executed,
            'actions_failed': self.actions_failed,
            'verification_passed': self.verification_passed,
            'execution_time_ms': self.execution_time_ms,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat()
        }


class RemediationExecutor:
    """
    Remediation Executor
    
    Executes remediation actions safely
    """

    def __init__(self):
        self._action_handlers: dict[RemediationType, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default action handlers"""
        self._action_handlers[RemediationType.RESTART] = self._handle_restart
        self._action_handlers[RemediationType.SCALE] = self._handle_scale
        self._action_handlers[RemediationType.CLEAR_CACHE] = self._handle_clear_cache
        self._action_handlers[RemediationType.NOTIFY] = self._handle_notify
        self._action_handlers[RemediationType.CUSTOM] = self._handle_custom

    def register_handler(
        self,
        action_type: RemediationType,
        handler: Callable[[RemediationAction], bool]
    ) -> None:
        """Register a custom action handler"""
        self._action_handlers[action_type] = handler

    async def _handle_restart(self, action: RemediationAction) -> bool:
        """Handle restart action"""
        # Simulate restart
        await asyncio.sleep(0.1)
        return True

    async def _handle_scale(self, action: RemediationAction) -> bool:
        """Handle scale action"""
        # Simulate scaling
        await asyncio.sleep(0.1)
        return True

    async def _handle_clear_cache(self, action: RemediationAction) -> bool:
        """Handle cache clearing"""
        # Simulate cache clearing
        await asyncio.sleep(0.05)
        return True

    async def _handle_notify(self, action: RemediationAction) -> bool:
        """Handle notification"""
        # Simulate notification
        return True

    async def _handle_custom(self, action: RemediationAction) -> bool:
        """Handle custom action"""
        # Custom actions need specific handlers
        return True

    async def execute(self, action: RemediationAction) -> bool:
        """Execute a remediation action"""
        # Check pre-conditions
        for condition in action.pre_conditions:
            if not condition():
                return False

        # Get handler
        handler = self._action_handlers.get(action.action_type, self._handle_custom)

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(action),
                timeout=action.timeout_seconds
            )

            if result:
                # Check post-conditions
                for condition in action.post_conditions:
                    if not condition():
                        return False

            return result
        except TimeoutError:
            return False
        except Exception:
            return False


class AutoRemediationEngine:
    """
    Auto Remediation Engine (自動修復引擎)
    
    Self-healing capabilities with predefined playbooks
    Zero human intervention
    
    Reference: 4 minutes, zero human involvement - Detect → Diagnose → Fix → Verify → Log [9]
    """

    def __init__(self):
        self._playbooks: dict[str, RemediationPlaybook] = {}
        self._executor = RemediationExecutor()
        self._history: list[RemediationResult] = []
        self._dry_run = False

    def set_dry_run(self, enabled: bool) -> None:
        """Enable/disable dry run mode"""
        self._dry_run = enabled

    def register_playbook(self, playbook: RemediationPlaybook) -> None:
        """Register a remediation playbook"""
        self._playbooks[playbook.playbook_id] = playbook

    def get_playbook(self, playbook_id: str) -> RemediationPlaybook | None:
        """Get a playbook by ID"""
        return self._playbooks.get(playbook_id)

    def find_matching_playbooks(self, trigger: str) -> list[RemediationPlaybook]:
        """Find playbooks matching a trigger condition"""
        matching = []
        for playbook in self._playbooks.values():
            if not playbook.enabled:
                continue
            if playbook.is_in_cooldown():
                continue
            for condition in playbook.trigger_conditions:
                if condition.lower() in trigger.lower() or trigger.lower() in condition.lower():
                    matching.append(playbook)
                    break

        # Sort by priority
        matching.sort(key=lambda p: p.priority, reverse=True)
        return matching

    async def execute_playbook(
        self,
        playbook: RemediationPlaybook,
        anomaly_id: str = ""
    ) -> RemediationResult:
        """
        Execute a remediation playbook
        
        Reference: Self-healing infrastructure [9]
        """
        import time
        start_time = time.time()

        result = RemediationResult(
            playbook_id=playbook.playbook_id,
            anomaly_id=anomaly_id,
            status=RemediationStatus.IN_PROGRESS
        )

        if self._dry_run:
            result.status = RemediationStatus.COMPLETED
            result.verification_passed = True
            result.actions_executed = [a.name for a in playbook.actions]
            return result

        try:
            # Execute each action in sequence
            for action in playbook.actions:
                success = await self._executor.execute(action)

                if success:
                    result.actions_executed.append(action.name)
                else:
                    result.actions_failed.append(action.name)

                    # Try rollback if available
                    if action.rollback_action:
                        await self._executor.execute(action.rollback_action)

                    result.status = RemediationStatus.FAILED
                    result.error_message = f"Action {action.name} failed"
                    break

            if result.status != RemediationStatus.FAILED:
                # Verification phase
                result.status = RemediationStatus.VERIFYING

                # Simple verification - check if all actions completed
                if len(result.actions_failed) == 0:
                    result.verification_passed = True
                    result.status = RemediationStatus.COMPLETED
                else:
                    result.status = RemediationStatus.FAILED

            # Update playbook last executed
            playbook.last_executed = datetime.now()

        except Exception as e:
            result.status = RemediationStatus.FAILED
            result.error_message = str(e)

        result.execution_time_ms = int((time.time() - start_time) * 1000)
        self._history.append(result)

        return result

    async def auto_remediate(
        self,
        trigger: str,
        anomaly_id: str = ""
    ) -> RemediationResult | None:
        """
        Automatically find and execute matching playbook
        
        The core of self-healing - zero human intervention
        """
        playbooks = self.find_matching_playbooks(trigger)

        if not playbooks:
            return None

        # Execute first matching playbook
        return await self.execute_playbook(playbooks[0], anomaly_id)

    def get_history(self) -> list[RemediationResult]:
        """Get remediation history"""
        return self._history.copy()

    def create_restart_playbook(
        self,
        name: str,
        target: str,
        triggers: list[str]
    ) -> RemediationPlaybook:
        """Create a simple restart playbook"""
        playbook = RemediationPlaybook(
            name=name,
            description=f"Restart {target} when triggered",
            trigger_conditions=triggers,
            actions=[
                RemediationAction(
                    name=f"restart_{target}",
                    action_type=RemediationType.RESTART,
                    target=target,
                    timeout_seconds=60
                )
            ]
        )
        self.register_playbook(playbook)
        return playbook

    def create_scale_playbook(
        self,
        name: str,
        target: str,
        scale_factor: int,
        triggers: list[str]
    ) -> RemediationPlaybook:
        """Create a scaling playbook"""
        playbook = RemediationPlaybook(
            name=name,
            description=f"Scale {target} by factor {scale_factor}",
            trigger_conditions=triggers,
            actions=[
                RemediationAction(
                    name=f"scale_{target}",
                    action_type=RemediationType.SCALE,
                    target=target,
                    parameters={'scale_factor': scale_factor},
                    timeout_seconds=120
                )
            ]
        )
        self.register_playbook(playbook)
        return playbook
