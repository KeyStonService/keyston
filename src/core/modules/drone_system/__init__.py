#!/usr/bin/env python3
"""
SynergyMesh 無人機系統模組

整合自 legacy/v1-python-drones，提供自動化無人機編隊功能。

模組包含:
- BaseDrone: 無人機基礎類別
- CoordinatorDrone: 協調器無人機
- AutopilotDrone: 自動駕駛無人機
- DeploymentDrone: 部署無人機
- DroneConfig: 配置管理
"""

from .autopilot import AutopilotDrone
from .base import BaseDrone, DroneStatus
from .config import DroneConfig
from .coordinator import CoordinatorDrone
from .deployment import DeploymentDrone
from .utils import Colors, print_error, print_info, print_success, print_warn

__all__ = [
    # 基礎類別
    "BaseDrone",
    "DroneStatus",
    # 具體無人機
    "CoordinatorDrone",
    "AutopilotDrone",
    "DeploymentDrone",
    # 配置
    "DroneConfig",
    # 工具函數
    "Colors",
    "print_info",
    "print_success",
    "print_warn",
    "print_error",
]

__version__ = "2.0.0"
