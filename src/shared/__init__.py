"""
SynergyMesh 共享資源套件

提供 v1-python-drones 和 v2-multi-islands 之間共享的配置、工具和常數。
"""

__version__ = "1.0.0"
__author__ = "SynergyMesh Team"

from .config import BaseConfig
from .utils import Colors, print_banner, print_info, print_success, print_warn, print_error, get_project_root
from .constants import VERSION, SYSTEM_NAME, SUPPORTED_MODES, ISLAND_TYPES, BRIDGE_PROTOCOLS

__all__ = [
    "__version__",
    "__author__",
    # Config
    "BaseConfig",
    # Utils
    "Colors",
    "print_banner",
    "print_info",
    "print_success",
    "print_warn",
    "print_error",
    "get_project_root",
    # Constants
    "VERSION",
    "SYSTEM_NAME",
    "SUPPORTED_MODES",
    "ISLAND_TYPES",
    "BRIDGE_PROTOCOLS",
]
