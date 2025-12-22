#!/usr/bin/env python3
"""
Structured Logging for SuperAgent

Provides JSON-formatted logging with:
- Trace ID propagation
- Request context
- Performance metrics
- Error details
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variables for request tracking
current_trace_id: ContextVar[Optional[str]] = ContextVar("current_trace_id", default=None)
current_span_id: ContextVar[Optional[str]] = ContextVar("current_span_id", default=None)
current_request_id: ContextVar[Optional[str]] = ContextVar("current_request_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(
        self,
        service_name: str = "super-agent",
        include_timestamp: bool = True,
        include_location: bool = True,
    ):
        super().__init__()
        self.service_name = service_name
        self.include_timestamp = include_timestamp
        self.include_location = include_location

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "service": self.service_name,
        }

        if self.include_timestamp:
            log_data["timestamp"] = datetime.now().isoformat()

        if self.include_location:
            log_data["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add context from context vars
        trace_id = current_trace_id.get()
        span_id = current_span_id.get()
        request_id = current_request_id.get()

        if trace_id:
            log_data["trace_id"] = trace_id
        if span_id:
            log_data["span_id"] = span_id
        if request_id:
            log_data["request_id"] = request_id

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info[2] else None,
            }

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as colored text."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level = record.levelname

        if self.use_colors:
            color = self.COLORS.get(level, "")
            level = f"{color}{level:8}{self.RESET}"
        else:
            level = f"{level:8}"

        # Add trace context if available
        trace_id = current_trace_id.get()
        trace_part = f" [{trace_id[:12]}]" if trace_id else ""

        message = record.getMessage()
        location = f"{record.filename}:{record.lineno}"

        formatted = f"{timestamp} {level} {location:30}{trace_part} {message}"

        # Add extra fields if present
        if hasattr(record, "extra_fields") and record.extra_fields:
            extra = " ".join(f"{k}={v}" for k, v in record.extra_fields.items())
            formatted += f" | {extra}"

        # Add exception if present
        if record.exc_info:
            formatted += "\n" + "".join(traceback.format_exception(*record.exc_info))

        return formatted


class StructuredLogger:
    """
    Structured logger with context support.

    Provides:
    - JSON and text formatting
    - Automatic context propagation
    - Extra field support
    - Performance timing
    """

    def __init__(
        self,
        name: str,
        level: str = "INFO",
        format_type: str = "json",  # "json" or "text"
        service_name: str = "super-agent",
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.service_name = service_name

        # Remove existing handlers
        self.logger.handlers = []

        # Add handler with appropriate formatter
        handler = logging.StreamHandler(sys.stdout)

        if format_type == "json":
            handler.setFormatter(JSONFormatter(service_name=service_name))
        else:
            handler.setFormatter(TextFormatter())

        self.logger.addHandler(handler)

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Internal log method with extra fields support."""
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            None if not exc_info else sys.exc_info(),
        )

        if extra:
            record.extra_fields = extra

        self.logger.handle(record)

    def debug(self, message: str, **extra) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, extra if extra else None)

    def info(self, message: str, **extra) -> None:
        """Log info message."""
        self._log(logging.INFO, message, extra if extra else None)

    def warning(self, message: str, **extra) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, extra if extra else None)

    def error(self, message: str, exc_info: bool = False, **extra) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, extra if extra else None, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False, **extra) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, extra if extra else None, exc_info=exc_info)

    def exception(self, message: str, **extra) -> None:
        """Log exception with traceback."""
        self._log(logging.ERROR, message, extra if extra else None, exc_info=True)

    # Convenience methods for common log patterns
    def request_received(
        self,
        method: str,
        path: str,
        trace_id: Optional[str] = None,
    ) -> None:
        """Log incoming request."""
        self.info(
            f"Request received: {method} {path}",
            method=method,
            path=path,
            trace_id=trace_id,
            event="request_received",
        )

    def request_completed(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Log completed request."""
        self.info(
            f"Request completed: {method} {path} -> {status_code} in {duration_ms:.2f}ms",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            event="request_completed",
        )

    def message_received(
        self,
        message_type: str,
        source_agent: str,
        trace_id: str,
    ) -> None:
        """Log message received."""
        self.info(
            f"Message received: {message_type} from {source_agent}",
            message_type=message_type,
            source_agent=source_agent,
            trace_id=trace_id,
            event="message_received",
        )

    def incident_transition(
        self,
        incident_id: str,
        from_state: str,
        to_state: str,
        trigger: str,
    ) -> None:
        """Log incident state transition."""
        self.info(
            f"Incident {incident_id} transitioned: {from_state} -> {to_state}",
            incident_id=incident_id,
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
            event="incident_transition",
        )


# Global logger instance
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(
    name: str = "super-agent",
    level: str = "INFO",
    format_type: str = "json",
) -> StructuredLogger:
    """Get or create a structured logger."""
    key = f"{name}:{level}:{format_type}"
    if key not in _loggers:
        _loggers[key] = StructuredLogger(name, level, format_type)
    return _loggers[key]


def set_trace_context(
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Set trace context for current request."""
    if trace_id:
        current_trace_id.set(trace_id)
    if span_id:
        current_span_id.set(span_id)
    if request_id:
        current_request_id.set(request_id)


def clear_trace_context() -> None:
    """Clear trace context."""
    current_trace_id.set(None)
    current_span_id.set(None)
    current_request_id.set(None)
