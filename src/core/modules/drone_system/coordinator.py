#!/usr/bin/env python3
"""
協調器無人機模組

負責協調所有無人機系統的運作。
"""

from typing import Any

from .base import BaseDrone, DroneStatus
from .utils import print_error, print_info, print_success, print_warn


class CoordinatorDrone(BaseDrone):
    """
    協調器無人機

    負責管理和協調其他無人機的運作，包括：
    - 任務調度
    - 資源管理
    - 健康監控
    """

    def __init__(self, name: str = "主協調器", priority: int = 1) -> None:
        """
        初始化協調器無人機

        Args:
            name: 無人機名稱
            priority: 優先級
        """
        super().__init__(name, priority)
        self._drones: dict[str, BaseDrone] = {}
        self._task_queue: list[dict[str, Any]] = []

    def start(self) -> bool:
        """
        啟動協調器

        Returns:
            是否成功啟動
        """
        print_info(f"啟動 {self.name}...")
        self.status = DroneStatus.RUNNING
        print_success(f"{self.name} 已啟動")
        return True

    def stop(self) -> bool:
        """
        停止協調器

        Returns:
            是否成功停止
        """
        print_info(f"停止 {self.name}...")

        # 停止所有管理的無人機
        for drone_id, drone in self._drones.items():
            try:
                drone.stop()
            except Exception as e:
                print_warn(f"停止無人機 {drone_id} 時發生錯誤: {e}")

        self.status = DroneStatus.STOPPED
        print_success(f"{self.name} 已停止")
        return True

    def execute_task(self, task_name: str, **kwargs: Any) -> Any:
        """
        執行協調任務

        Args:
            task_name: 任務名稱
            **kwargs: 任務參數

        Returns:
            任務執行結果
        """
        tasks: dict[str, Any] = {
            "analyze_environment": self._analyze_environment,
            "health_check": self._health_check,
            "dispatch_task": self._dispatch_task,
        }

        task_func = tasks.get(task_name)
        if not task_func:
            print_error(f"未知任務: {task_name}")
            return None

        if callable(task_func):
            return task_func(**kwargs)
        return None

    def register_drone(self, drone_id: str, drone: BaseDrone) -> None:
        """
        註冊無人機

        Args:
            drone_id: 無人機 ID
            drone: 無人機實例
        """
        self._drones[drone_id] = drone
        print_info(f"已註冊無人機: {drone_id} ({drone.name})")

    def unregister_drone(self, drone_id: str) -> bool:
        """
        取消註冊無人機

        Args:
            drone_id: 無人機 ID

        Returns:
            是否成功取消
        """
        if drone_id in self._drones:
            del self._drones[drone_id]
            print_info(f"已取消註冊無人機: {drone_id}")
            return True
        return False

    def get_drone(self, drone_id: str) -> BaseDrone | None:
        """
        獲取無人機實例

        Args:
            drone_id: 無人機 ID

        Returns:
            無人機實例或 None
        """
        return self._drones.get(drone_id)

    def list_drones(self) -> list[str]:
        """
        列出所有註冊的無人機

        Returns:
            無人機 ID 列表
        """
        return list(self._drones.keys())

    def _analyze_environment(self) -> dict[str, Any]:
        """分析環境"""
        print_info("分析環境中...")
        return {
            "drones_count": len(self._drones),
            "coordinator_status": self.status.value,
        }

    def _health_check(self) -> dict[str, Any]:
        """執行健康檢查"""
        print_info("執行健康檢查...")
        results: dict[str, Any] = {}

        for drone_id, drone in self._drones.items():
            results[drone_id] = {
                "name": drone.name,
                "status": drone.get_status().value,
            }

        return results

    def _dispatch_task(self, target_drone: str, task_name: str, **kwargs: Any) -> Any:
        """
        分發任務到指定無人機

        Args:
            target_drone: 目標無人機 ID
            task_name: 任務名稱
            **kwargs: 任務參數

        Returns:
            任務執行結果
        """
        drone = self._drones.get(target_drone)
        if not drone:
            print_error(f"無人機 {target_drone} 不存在")
            return None

        return drone.execute_task(task_name, **kwargs)
