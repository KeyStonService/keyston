"""
SynergyMesh v1-python-drones 套件

Python 無人機系統 - 高階應用整合層
"""

__version__ = "1.1.0"
__author__ = "SynergyMesh Team"

# 使用延遲導入以避免循環依賴
def get_drones():
    """取得無人機類別"""
    from .drones import BaseDrone, CoordinatorDrone, AutopilotDrone, DeploymentDrone
    return BaseDrone, CoordinatorDrone, AutopilotDrone, DeploymentDrone

def get_config():
    """取得配置類別"""
    from .config import DroneConfig
    return DroneConfig

__all__ = [
    "__version__",
    "__author__",
    "get_drones",
    "get_config",
]
