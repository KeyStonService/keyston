"""
Alert management system for MachineNativeOps Auto Monitor
Handles threshold-based alerts and auto-repair functionality
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .config import MonitoringConfig, AutoRepairConfig
from .storage import DatabaseManager

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(Enum):
    """Alert types"""
    CPU_HIGH = "cpu_high"
    MEMORY_HIGH = "memory_high"
    DISK_HIGH = "disk_high"
    API_RESPONSE_SLOW = "api_response_slow"
    QUANTUM_FIDELITY_LOW = "quantum_fidelity_low"
    QUANTUM_ERROR_RATE_HIGH = "quantum_error_rate_high"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DATABASE_ERROR = "database_error"

@dataclass
class Alert:
    """Alert data structure"""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    data: Dict[str, Any]
    timestamp: str
    resolved: bool = False
    resolved_at: Optional[str] = None

class AlertManager:
    """Alert management and auto-repair system"""
    
    def __init__(self, monitoring_config: MonitoringConfig, auto_repair_config: AutoRepairConfig):
        self.monitoring_config = monitoring_config
        self.auto_repair_config = auto_repair_config
        self.logger = logging.getLogger(__name__)
        
        # Database manager
        self.db_manager: Optional[DatabaseManager] = None
        
        # Active alerts tracking
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Auto-repair handlers
        self.repair_handlers: Dict[AlertType, Callable] = {}
        self._register_default_handlers()
        
        # Thread lock
        self._lock = threading.Lock()
        
        self.logger.info("Alert manager initialized")
    
    def set_database_manager(self, db_manager: DatabaseManager):
        """Set database manager for persistence"""
        self.db_manager = db_manager
        
        # Load active alerts from database
        self._load_active_alerts()
    
    def _register_default_handlers(self):
        """Register default auto-repair handlers"""
        self.repair_handlers = {
            AlertType.SERVICE_UNAVAILABLE: self._handle_service_unavailable,
            AlertType.DATABASE_ERROR: self._handle_database_error,
            # Add more handlers as needed
        }
    
    def check_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts"""
        try:
            timestamp = metrics.get('timestamp', datetime.utcnow().isoformat())
            
            # CPU usage check
            cpu_usage = metrics.get('cpu_usage_percent', 0)
            if cpu_usage > self.monitoring_config.cpu_threshold:
                self._create_alert(
                    AlertType.CPU_HIGH,
                    AlertSeverity.WARNING if cpu_usage < 95 else AlertSeverity.CRITICAL,
                    f"High CPU usage: {cpu_usage:.1f}%",
                    {'cpu_usage': cpu_usage, 'threshold': self.monitoring_config.cpu_threshold},
                    timestamp
                )
            
            # Memory usage check
            memory_usage = metrics.get('memory_usage_percent', 0)
            if memory_usage > self.monitoring_config.memory_threshold:
                self._create_alert(
                    AlertType.MEMORY_HIGH,
                    AlertSeverity.WARNING if memory_usage < 95 else AlertSeverity.CRITICAL,
                    f"High memory usage: {memory_usage:.1f}%",
                    {'memory_usage': memory_usage, 'threshold': self.monitoring_config.memory_threshold},
                    timestamp
                )
            
            # Disk usage check
            disk_usage = metrics.get('disk_usage_percent', 0)
            if disk_usage > self.monitoring_config.disk_threshold:
                self._create_alert(
                    AlertType.DISK_HIGH,
                    AlertSeverity.WARNING if disk_usage < 98 else AlertSeverity.CRITICAL,
                    f"High disk usage: {disk_usage:.1f}%",
                    {'disk_usage': disk_usage, 'threshold': self.monitoring_config.disk_threshold},
                    timestamp
                )
            
            # API response time check
            api_response_time = metrics.get('api_response_time_ms', 0)
            if api_response_time > self.monitoring_config.api_response_threshold:
                self._create_alert(
                    AlertType.API_RESPONSE_SLOW,
                    AlertSeverity.WARNING,
                    f"Slow API response: {api_response_time:.0f}ms",
                    {'response_time': api_response_time, 'threshold': self.monitoring_config.api_response_threshold},
                    timestamp
                )
            
            # Quantum metrics checks
            if 'quantum_fidelity' in metrics:
                fidelity = metrics['quantum_fidelity']
                if fidelity < self.monitoring_config.quantum_fidelity_threshold:
                    self._create_alert(
                        AlertType.QUANTUM_FIDELITY_LOW,
                        AlertSeverity.WARNING,
                        f"Low quantum fidelity: {fidelity:.3f}",
                        {'fidelity': fidelity, 'threshold': self.monitoring_config.quantum_fidelity_threshold},
                        timestamp
                    )
            
            if 'quantum_error_rate' in metrics:
                error_rate = metrics['quantum_error_rate']
                if error_rate > self.monitoring_config.quantum_error_rate_threshold:
                    self._create_alert(
                        AlertType.QUANTUM_ERROR_RATE_HIGH,
                        AlertSeverity.WARNING,
                        f"High quantum error rate: {error_rate:.4f}",
                        {'error_rate': error_rate, 'threshold': self.monitoring_config.quantum_error_rate_threshold},
                        timestamp
                    )
            
            # Service availability check
            if 'kubernetes_services_healthy' in metrics and 'kubernetes_services_total' in metrics:
                healthy = metrics['kubernetes_services_healthy']
                total = metrics['kubernetes_services_total']
                if total > 0 and healthy < total:
                    self._create_alert(
                        AlertType.SERVICE_UNAVAILABLE,
                        AlertSeverity.WARNING,
                        f"Services unavailable: {total - healthy}/{total} unhealthy",
                        {'healthy': healthy, 'total': total},
                        timestamp
                    )
            
        except Exception as e:
            self.logger.error(f"Alert check failed: {e}")
    
    def _create_alert(self, alert_type: AlertType, severity: AlertSeverity, 
                     message: str, data: Dict[str, Any], timestamp: str):
        """Create and process alert"""
        with self._lock:
            alert_key = f"{alert_type.value}_{timestamp}"
            
            # Check if similar alert already exists
            if self._similar_active_alert_exists(alert_type, data):
                return
            
            alert = Alert(
                alert_type=alert_type,
                severity=severity,
                message=message,
                data=data,
                timestamp=timestamp
            )
            
            self.active_alerts[alert_key] = alert
            self.alert_history.append(alert)
            
            # Store in database
            if self.db_manager:
                self.db_manager.store_alert(
                    alert_type.value,
                    severity.value,
                    message,
                    data
                )
            
            self.logger.warning(f"Alert created: {alert_type.value} - {message}")
            
            # Trigger auto-repair if enabled and applicable
            if self.auto_repair_config.enabled and alert_type in self.repair_handlers:
                self._trigger_auto_repair(alert)
    
    def _similar_active_alert_exists(self, alert_type: AlertType, data: Dict[str, Any]) -> bool:
        """Check if similar active alert already exists"""
        for alert in self.active_alerts.values():
            if alert.alert_type == alert_type and not alert.resolved:
                # Check if data is similar (within 5% for numerical values)
                for key, value in data.items():
                    if isinstance(value, (int, float)) and key in alert.data:
                        old_value = alert.data[key]
                        if isinstance(old_value, (int, float)):
                            diff = abs(value - old_value) / max(old_value, 1)
                            if diff < 0.05:  # Within 5%
                                return True
        return False
    
    def _trigger_auto_repair(self, alert: Alert):
        """Trigger auto-repair for alert"""
        try:
            handler = self.repair_handlers.get(alert.alert_type)
            if not handler:
                self.logger.info(f"No auto-repair handler for {alert.alert_type.value}")
                return
            
            self.logger.info(f"Triggering auto-repair for {alert.alert_type.value}")
            
            # Run repair in separate thread
            repair_thread = threading.Thread(
                target=self._execute_repair,
                args=(alert, handler),
                daemon=True
            )
            repair_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to trigger auto-repair: {e}")
    
    def _execute_repair(self, alert: Alert, handler: Callable):
        """Execute auto-repair handler"""
        try:
            success = handler(alert)
            
            if success:
                self._resolve_alert(alert.alert_type, "Auto-repair successful")
                self.logger.info(f"Auto-repair successful for {alert.alert_type.value}")
            else:
                self.logger.warning(f"Auto-repair failed for {alert.alert_type.value}")
                
        except Exception as e:
            self.logger.error(f"Auto-repair execution failed: {e}")
    
    def _resolve_alert(self, alert_type: AlertType, reason: str):
        """Resolve alerts of specific type"""
        with self._lock:
            resolved_count = 0
            current_time = datetime.utcnow().isoformat()
            
            for key, alert in list(self.active_alerts.items()):
                if alert.alert_type == alert_type and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = current_time
                    del self.active_alerts[key]
                    resolved_count += 1
            
            # Update database
            if self.db_manager and resolved_count > 0:
                # This is simplified - in practice, you'd track alert IDs
                self.logger.info(f"Resolved {resolved_count} {alert_type.value} alerts: {reason}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        with self._lock:
            alerts = []
            for alert in self.active_alerts.values():
                alert_dict = {
                    'alert_type': alert.alert_type.value,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'data': alert.data,
                    'timestamp': alert.timestamp,
                }
                alerts.append(alert_dict)
            return alerts
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        return [
            {
                'alert_type': alert.alert_type.value,
                'severity': alert.severity.value,
                'message': alert.message,
                'data': alert.data,
                'timestamp': alert.timestamp,
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at,
            }
            for alert in self.alert_history[-limit:]
        ]
    
    def _load_active_alerts(self):
        """Load active alerts from database"""
        if not self.db_manager:
            return
        
        try:
            db_alerts = self.db_manager.get_active_alerts()
            
            for db_alert in db_alerts:
                alert_type = AlertType(db_alert['alert_type'])
                severity = AlertSeverity(db_alert['severity'])
                
                alert = Alert(
                    alert_type=alert_type,
                    severity=severity,
                    message=db_alert['message'],
                    data=db_alert['data'],
                    timestamp=db_alert['timestamp'],
                )
                
                key = f"{alert_type.value}_{alert.timestamp}"
                self.active_alerts[key] = alert
            
            self.logger.info(f"Loaded {len(self.active_alerts)} active alerts from database")
            
        except Exception as e:
            self.logger.error(f"Failed to load active alerts: {e}")
    
    # Default auto-repair handlers
    def _handle_service_unavailable(self, alert: Alert) -> bool:
        """Handle service unavailability"""
        try:
            # This is a placeholder - in practice, you'd implement
            # Kubernetes service restart, scale-up, etc.
            self.logger.info("Service unavailable: would attempt restart/repair")
            return True
            
        except Exception as e:
            self.logger.error(f"Service repair failed: {e}")
            return False
    
    def _handle_database_error(self, alert: Alert) -> bool:
        """Handle database errors"""
        try:
            # This is a placeholder - in practice, you'd implement
            # database reconnection, cleanup, etc.
            self.logger.info("Database error: would attempt reconnection/repair")
            return True
            
        except Exception as e:
            self.logger.error(f"Database repair failed: {e}")
            return False