#!/usr/bin/env python3
"""
無人機基礎類別模組

提供所有無人機類型的基礎實現。
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class DroneStatus(Enum):
    """無人機狀態枚舉"""

    INITIALIZED = "initialized"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    SCRIPT_MISSING = "script_missing"


class BaseDrone(ABC):
    """
    無人機基礎抽象類別

    所有具體無人機類型都應繼承此類別。

    Attributes:
        name: 無人機名稱
        status: 當前狀態
        priority: 優先級（數字越小優先級越高）
    """

    def __init__(self, name: str, priority: int = 99) -> None:
        """
        初始化無人機

        Args:
            name: 無人機名稱
            priority: 優先級，預設為 99
        """
        self.name = name
        self.priority = priority
        self.status = DroneStatus.INITIALIZED
        self._config: dict[str, Any] = {}

    @abstractmethod
    def start(self) -> bool:
        """
        啟動無人機

        Returns:
            是否成功啟動
        """
        pass

    @abstractmethod
    def stop(self) -> bool:
        """
        停止無人機

        Returns:
            是否成功停止
        """
        pass

    @abstractmethod
    def execute_task(self, task_name: str, **kwargs: Any) -> Any:
        """
        執行任務

        Args:
            task_name: 任務名稱
            **kwargs: 任務參數

        Returns:
            任務執行結果
        """
        pass

    def get_status(self) -> DroneStatus:
        """
        獲取當前狀態

        Returns:
            當前無人機狀態
        """
        return self.status

    def set_config(self, config: dict[str, Any]) -> None:
        """
        設定配置

        Args:
            config: 配置字典
        """
        self._config = config

    def get_config(self) -> dict[str, Any]:
        """
        獲取配置

        Returns:
            配置字典
        """
        return self._config.copy()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, status={self.status.value!r})"
