"""
MachineNativeOps Auto-Monitor Package
機器原生運維自動監控套件

This package provides automated monitoring capabilities for MachineNativeOps infrastructure.
"""

__version__ = "1.0.0"
__author__ = "MachineNativeOps"

# Lazy imports to avoid dependency issues
__all__ = [
    'AutoMonitorApp',
    'MetricsCollector',
    'LogCollector',
    'EventCollector',
    'AlertManager',
    'AlertRule',
    'MonitorConfig',
]

def __getattr__(name):
    """Lazy import to avoid loading dependencies at package import time."""
    if name == 'AutoMonitorApp':
        from .app import AutoMonitorApp
        return AutoMonitorApp
    elif name in ('MetricsCollector', 'LogCollector', 'EventCollector'):
        from .collectors import MetricsCollector, LogCollector, EventCollector
        return {'MetricsCollector': MetricsCollector, 
                'LogCollector': LogCollector,
                'EventCollector': EventCollector}[name]
    elif name in ('AlertManager', 'AlertRule'):
        from .alerts import AlertManager, AlertRule
        return {'AlertManager': AlertManager, 'AlertRule': AlertRule}[name]
    elif name == 'MonitorConfig':
        from .config import MonitorConfig
        return MonitorConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
