"""
MachineNativeOps Auto Monitor
System monitoring with quantum state tracking
"""

__version__ = "2.0.0"
__author__ = "MachineNativeOps Team"
__email__ = "team@machinenativeops.io"
__description__ = "System monitoring with quantum state tracking"

from .app import MachineNativeOpsAutoMonitor
from .config import Config
from .collectors import SystemCollector, QuantumCollector

__all__ = [
    "MachineNativeOpsAutoMonitor",
    "Config", 
    "SystemCollector",
    "QuantumCollector",
]