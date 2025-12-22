"""
MachineNativeOps Auto-Monitor - Alert Management
=================================================

Manages alert rules, evaluation, and notification delivery.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class AlertState(Enum):
    """Alert states."""
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"


@dataclass
class Alert:
    """Represents an alert instance."""
    id: str
    name: str
    severity: AlertSeverity
    state: AlertState
    message: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'severity': self.severity.value,
            'state': self.state.value,
            'message': self.message,
            'labels': self.labels,
            'annotations': self.annotations,
            'started_at': self.started_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


@dataclass
class AlertRule:
    """Defines an alert rule."""
    name: str
    description: str
    severity: AlertSeverity
    condition: str
    threshold: float
    duration: int = 60  # seconds
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    
    def evaluate(self, value: float) -> bool:
        """
        Evaluate the alert rule against a value.
        
        Args:
            value: The metric value to evaluate
            
        Returns:
            True if the alert condition is met, False otherwise
        """
        # Simple threshold comparison
        # In production, this would support complex expressions
        if '>' in self.condition:
            return value > self.threshold
        elif '<' in self.condition:
            return value < self.threshold
        elif '=' in self.condition:
            return value == self.threshold
        elif '!=' in self.condition:
            return value != self.threshold
        else:
            return False


class AlertManager:
    """
    Manages alert rules and active alerts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert manager.
        
        Args:
            config: Alert manager configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        self._load_rules()
    
    def _load_rules(self):
        """Load alert rules from configuration."""
        rules_config = self.config.get('rules', [])
        
        for rule_config in rules_config:
            rule = AlertRule(
                name=rule_config['name'],
                description=rule_config.get('description', ''),
                severity=AlertSeverity(rule_config.get('severity', 'warning')),
                condition=rule_config['condition'],
                threshold=rule_config['threshold'],
                duration=rule_config.get('duration', 60),
                labels=rule_config.get('labels', {}),
                annotations=rule_config.get('annotations', {}),
                enabled=rule_config.get('enabled', True)
            )
            
            self.rules[rule.name] = rule
            self.logger.info(f"Loaded alert rule: {rule.name}")
    
    def evaluate_metrics(self, metrics: Dict[str, float]):
        """
        Evaluate metrics against all alert rules.
        
        Args:
            metrics: Dictionary of metric name to value
        """
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Find matching metric
            metric_value = metrics.get(rule_name)
            if metric_value is None:
                continue
            
            # Evaluate rule
            if rule.evaluate(metric_value):
                self._fire_alert(rule, metric_value)
            else:
                self._resolve_alert(rule_name)
    
    def _fire_alert(self, rule: AlertRule, value: float):
        """
        Fire an alert based on a rule.
        
        Args:
            rule: The alert rule that triggered
            value: The metric value that triggered the alert
        """
        alert_id = f"{rule.name}_{datetime.now().timestamp()}"
        
        # Check if alert already exists
        if rule.name in self.active_alerts:
            self.logger.debug(f"Alert already active: {rule.name}")
            return
        
        # Create new alert
        alert = Alert(
            id=alert_id,
            name=rule.name,
            severity=rule.severity,
            state=AlertState.FIRING,
            message=f"{rule.description} (current value: {value}, threshold: {rule.threshold})",
            labels=rule.labels.copy(),
            annotations=rule.annotations.copy()
        )
        
        self.active_alerts[rule.name] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(
            f"ALERT FIRED: {alert.name} [{alert.severity.value}] - {alert.message}"
        )
        
        # Send notification (would integrate with actual notification system)
        self._send_notification(alert)
    
    def _resolve_alert(self, rule_name: str):
        """
        Resolve an active alert.
        
        Args:
            rule_name: Name of the alert rule
        """
        if rule_name not in self.active_alerts:
            return
        
        alert = self.active_alerts[rule_name]
        alert.state = AlertState.RESOLVED
        alert.resolved_at = datetime.now()
        
        self.logger.info(f"ALERT RESOLVED: {alert.name}")
        
        # Send resolution notification
        self._send_notification(alert)
        
        # Remove from active alerts
        del self.active_alerts[rule_name]
    
    def _send_notification(self, alert: Alert):
        """
        Send alert notification.
        
        Args:
            alert: The alert to notify about
        """
        # In production, this would integrate with notification channels
        # (email, Slack, PagerDuty, etc.)
        self.logger.info(f"Notification sent for alert: {alert.name} ({alert.state.value})")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get list of active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """
        Get alert history.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alert_history[-limit:]
    
    def add_rule(self, rule: AlertRule):
        """
        Add a new alert rule.
        
        Args:
            rule: The alert rule to add
        """
        self.rules[rule.name] = rule
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """
        Remove an alert rule.
        
        Args:
            rule_name: Name of the rule to remove
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"Removed alert rule: {rule_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alert manager statistics."""
        return {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules.values() if r.enabled),
            'active_alerts': len(self.active_alerts),
            'total_alerts_fired': len(self.alert_history),
            'alerts_by_severity': {
                severity.value: sum(
                    1 for a in self.active_alerts.values()
                    if a.severity == severity
                )
                for severity in AlertSeverity
            }
        }
