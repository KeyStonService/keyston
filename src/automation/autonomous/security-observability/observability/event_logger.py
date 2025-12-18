"""
autonomous-system/security-observability/observability/event_logger.py

Event logging and safety monitoring for autonomous systems.
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from threading import RLock


class EventCategory(str, Enum):
    """事件分類 Event Categories"""
    SENSOR_ERROR = "sensor_error"
    CONTROL_ERROR = "control_error"
    SAFETY_VIOLATION = "safety_violation"
    SYSTEM_ERROR = "system_error"
    AUDIT = "audit"


@dataclass
class Event:
    """事件結構 Event Structure"""
    timestamp: datetime
    category: EventCategory
    module: str
    severity: str  # "INFO", "WARN", "ERROR", "CRITICAL"
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    parent_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['category'] = self.category.value
        return data


class EventLogger:
    """事件日誌記錄器 Event Logger"""

    def __init__(self, buffer_size: int = 100):
        """
        創建新的事件日誌記錄器
        Create new event logger

        Args:
            buffer_size: Buffer size for events (unused in Python, kept for API compatibility)
        """
        self.store: List[Event] = []
        self._lock = RLock()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup standard logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def log_event(
        self,
        category: EventCategory,
        module: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        記錄事件 Log an event

        Args:
            category: Event category
            module: Module name
            severity: Severity level
            message: Event message
            metadata: Additional metadata
        """
        event = Event(
            timestamp=datetime.now(),
            category=category,
            module=module,
            severity=severity,
            message=message,
            metadata=metadata or {},
            trace_id=self._generate_trace_id()
        )

        with self._lock:
            self.store.append(event)

        # Output to standard logging
        log_icons = {
            "INFO": "ℹ️",
            "WARN": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨",
        }

        icon = log_icons.get(severity, "•")
        log_message = (
            f"{icon} [{category.value}] {module}/{severity}: {message} "
            f"(TraceID: {event.trace_id})"
        )

        # Map to appropriate log level
        if severity == "INFO":
            self.logger.info(log_message)
        elif severity == "WARN":
            self.logger.warning(log_message)
        elif severity == "ERROR":
            self.logger.error(log_message)
        elif severity == "CRITICAL":
            self.logger.critical(log_message)

    def get_events_by_category(self, category: EventCategory) -> List[Event]:
        """
        按分類查詢事件 Get events by category

        Args:
            category: Event category to filter by

        Returns:
            List of events matching the category
        """
        with self._lock:
            return [event for event in self.store if event.category == category]

    def get_events_by_severity(self, severity: str) -> List[Event]:
        """
        按嚴重性查詢事件 Get events by severity

        Args:
            severity: Severity level to filter by

        Returns:
            List of events matching the severity
        """
        with self._lock:
            return [event for event in self.store if event.severity == severity]

    def export_json(self) -> str:
        """
        導出 JSON 格式日誌 Export logs as JSON

        Returns:
            JSON string of all events
        """
        with self._lock:
            events_data = [event.to_dict() for event in self.store]
            return json.dumps(events_data, indent=2, ensure_ascii=False)

    @staticmethod
    def _generate_trace_id() -> str:
        """
        生成追蹤 ID Generate trace ID

        Returns:
            Unique trace ID
        """
        return f"trace_{int(time.time() * 1e9)}"


class SafetyMonitor:
    """安全監控器 Safety Monitor"""

    def __init__(self, logger: EventLogger):
        """
        創建安全監控器 Create safety monitor

        Args:
            logger: Event logger instance
        """
        self.logger = logger
        self._lock = RLock()

    def check_altitude_limit(self, altitude: float, max_altitude: float) -> bool:
        """
        檢查高度限制 Check altitude limit

        Args:
            altitude: Current altitude
            max_altitude: Maximum allowed altitude

        Returns:
            True if within limit, False otherwise
        """
        if altitude > max_altitude:
            self.logger.log_event(
                EventCategory.SAFETY_VIOLATION,
                "safety_monitor",
                "CRITICAL",
                f"Altitude exceeded: {altitude:.2f} > {max_altitude:.2f}",
                {
                    "current_altitude": altitude,
                    "max_altitude": max_altitude,
                }
            )
            return False
        return True

    def check_velocity_limit(self, velocity: float, max_velocity: float) -> bool:
        """
        檢查速度限制 Check velocity limit

        Args:
            velocity: Current velocity
            max_velocity: Maximum allowed velocity

        Returns:
            True if within limit, False otherwise
        """
        if velocity > max_velocity:
            self.logger.log_event(
                EventCategory.SAFETY_VIOLATION,
                "safety_monitor",
                "CRITICAL",
                f"Velocity exceeded: {velocity:.2f} > {max_velocity:.2f}",
                {
                    "current_velocity": velocity,
                    "max_velocity": max_velocity,
                }
            )
            return False
        return True

    def generate_safety_report(self) -> str:
        """
        生成安全報告 Generate safety report

        Returns:
            Safety report as formatted string
        """
        violations = self.logger.get_events_by_category(EventCategory.SAFETY_VIOLATION)
        errors = self.logger.get_events_by_category(EventCategory.SENSOR_ERROR)

        report = f"""
╔════════════════════════════════════════╗
║          安全監控報告                    ║
╚════════════════════════════════════════╝

安全違規事件：{len(violations)}
感測器錯誤：{len(errors)}
總事件數：{len(self.logger.store)}

最近的安全違規：
"""

        # Show last 5 violations
        for i, violation in enumerate(violations[-5:]):
            timestamp_str = violation.timestamp.strftime("%H:%M:%S")
            report += f"  • {timestamp_str}: {violation.message}\n"

        return report
