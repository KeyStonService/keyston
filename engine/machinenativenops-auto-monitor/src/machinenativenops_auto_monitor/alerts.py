"""
Alert Management Module
警報管理模組

Handles alert rules, alert generation, and alert routing for MachineNativeOps monitoring.
"""

import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class Alert:
    """Represents a monitoring alert."""
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: AlertStatus = AlertStatus.FIRING
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        return {
            'name': self.name,
            'severity': self.severity.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'labels': self.labels,
            'annotations': self.annotations,
        }


@dataclass
class AlertRule:
    """Defines an alert rule with condition and action."""
    name: str
    condition: Callable[[Dict], bool]
    severity: AlertSeverity
    message_template: str
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    
    def evaluate(self, metrics: Dict) -> Optional[Alert]:
        """Evaluate the rule against metrics and generate alert if needed."""
        if not self.enabled:
            return None
        
        try:
            if self.condition(metrics):
                message = self.message_template.format(**metrics)
                return Alert(
                    name=self.name,
                    severity=self.severity,
                    message=message,
                    labels=self.labels,
                )
        except Exception as e:
            logger.error(f"Error evaluating rule '{self.name}': {e}")
        
        return None


class AlertManager:
    """Manages alert rules and active alerts."""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.handlers: List[Callable[[Alert], None]] = []
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Remove an alert rule by name."""
        self.rules = [r for r in self.rules if r.name != rule_name]
        logger.info(f"Removed alert rule: {rule_name}")
    
    def add_handler(self, handler: Callable[[Alert], None]):
        """Add an alert handler function."""
        self.handlers.append(handler)
    
    def evaluate_rules(self, metrics: Dict):
        """Evaluate all rules against current metrics."""
        for rule in self.rules:
            alert = rule.evaluate(metrics)
            if alert:
                self._fire_alert(alert)
            elif rule.name in self.active_alerts:
                self._resolve_alert(rule.name)
    
    def _fire_alert(self, alert: Alert):
        """Fire an alert."""
        if alert.name not in self.active_alerts:
            logger.warning(f"🚨 Alert fired: {alert.name} - {alert.message}")
            self.active_alerts[alert.name] = alert
            self.alert_history.append(alert)
            
            # Call all handlers
            for handler in self.handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
    
    def _resolve_alert(self, alert_name: str):
        """Resolve an active alert."""
        if alert_name in self.active_alerts:
            alert = self.active_alerts[alert_name]
            alert.status = AlertStatus.RESOLVED
            logger.info(f"✅ Alert resolved: {alert_name}")
            del self.active_alerts[alert_name]
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history with optional limit."""
        return self.alert_history[-limit:]
    
    def silence_alert(self, alert_name: str):
        """Silence an active alert."""
        if alert_name in self.active_alerts:
            self.active_alerts[alert_name].status = AlertStatus.SILENCED
            logger.info(f"🔇 Alert silenced: {alert_name}")


# Pre-defined alert rules for common scenarios
def create_default_rules() -> List[AlertRule]:
    """Create default alert rules for MachineNativeOps monitoring."""
    return [
        AlertRule(
            name="high_cpu_usage",
            condition=lambda m: m.get('cpu_percent', 0) > 80,
            severity=AlertSeverity.WARNING,
            message_template="CPU usage is high: {cpu_percent}%",
            labels={'component': 'system', 'resource': 'cpu'},
        ),
        AlertRule(
            name="high_memory_usage",
            condition=lambda m: m.get('memory_percent', 0) > 85,
            severity=AlertSeverity.WARNING,
            message_template="Memory usage is high: {memory_percent}%",
            labels={'component': 'system', 'resource': 'memory'},
        ),
        AlertRule(
            name="disk_space_low",
            condition=lambda m: m.get('disk_percent', 0) > 90,
            severity=AlertSeverity.CRITICAL,
            message_template="Disk space is critically low: {disk_percent}%",
            labels={'component': 'system', 'resource': 'disk'},
        ),
        AlertRule(
            name="service_down",
            condition=lambda m: not m.get('service_healthy', True),
            severity=AlertSeverity.CRITICAL,
            message_template="Service is down: {service_name}",
            labels={'component': 'service', 'health': 'down'},
        ),
    ]
