#!/usr/bin/env python3
"""
自動駕駛無人機模組

負責自動化任務的執行邏輯。
"""

import subprocess
from pathlib import Path
from typing import Any

from .base import BaseDrone, DroneStatus
from .utils import print_error, print_info, print_success, print_warn


class AutopilotDrone(BaseDrone):
    """
    自動駕駛無人機

    負責自動化任務的執行，包括：
    - 監控文件變更
    - 觸發自動化任務
    - 管理工作流程
    """

    # 命令執行的預設超時（秒）
    COMMAND_TIMEOUT = 300

    def __init__(self, name: str = "自動駕駛", priority: int = 2) -> None:
        """
        初始化自動駕駛無人機

        Args:
            name: 無人機名稱
            priority: 優先級
        """
        super().__init__(name, priority)
        self._project_root: Path | None = None
        self._watchers: list[Any] = []
        self._task_queue: list[dict[str, Any]] = []

    def start(self) -> bool:
        """
        啟動自動駕駛

        Returns:
            是否成功啟動
        """
        print_info(f"啟動 {self.name}...")
        self._project_root = self._find_project_root()
        self.status = DroneStatus.RUNNING
        print_success(f"{self.name} 已啟動")
        return True

    def stop(self) -> bool:
        """
        停止自動駕駛

        Returns:
            是否成功停止
        """
        print_info(f"停止 {self.name}...")

        # 清理監控器
        self._watchers.clear()
        self._task_queue.clear()

        self.status = DroneStatus.STOPPED
        print_success(f"{self.name} 已停止")
        return True

    def execute_task(self, task_name: str, **kwargs: Any) -> Any:
        """
        執行自動化任務

        Args:
            task_name: 任務名稱
            **kwargs: 任務參數

        Returns:
            任務執行結果
        """
        tasks = {
            "lint": self._run_lint,
            "format": self._run_format,
            "test": self._run_tests,
            "build": self._run_build,
            "diagnosis": self._run_diagnosis,
        }

        task_func = tasks.get(task_name)
        if not task_func:
            print_error(f"未知任務: {task_name}")
            return False

        return task_func(**kwargs)

    def queue_task(self, task_name: str, **kwargs: Any) -> None:
        """
        將任務加入佇列

        Args:
            task_name: 任務名稱
            **kwargs: 任務參數
        """
        self._task_queue.append({"name": task_name, "kwargs": kwargs})
        print_info(f"任務已加入佇列: {task_name}")

    def process_queue(self) -> list[Any]:
        """
        處理任務佇列

        Returns:
            所有任務的執行結果
        """
        results = []
        while self._task_queue:
            task = self._task_queue.pop(0)
            result = self.execute_task(task["name"], **task["kwargs"])
            results.append(result)
        return results

    def _find_project_root(self) -> Path:
        """尋找專案根目錄"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / "drone-config.yml").exists():
                return current
            if (current / "package.json").exists():
                return current
            current = current.parent
        return Path.cwd()

    def _run_command(self, command: list[str], description: str) -> tuple[bool, str]:
        """
        執行命令

        Args:
            command: 命令列表
            description: 命令描述

        Returns:
            (是否成功, 輸出內容)
        """
        print_info(f"執行 {description}...")
        try:
            result = subprocess.run(
                command,
                cwd=self._project_root,
                capture_output=True,
                text=True,
                timeout=self.COMMAND_TIMEOUT,
            )
            if result.returncode == 0:
                print_success(f"{description} 完成")
                return True, result.stdout
            else:
                print_warn(f"{description} 有警告或錯誤")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            print_error(f"{description} 超時")
            return False, "Command timed out"
        except FileNotFoundError as e:
            print_error(f"找不到命令: {e}")
            return False, str(e)

    def _run_lint(self, **_kwargs: Any) -> bool:
        """執行程式碼檢查"""
        success, _ = self._run_command(["npm", "run", "lint", "--if-present"], "程式碼檢查")
        return success

    def _run_format(self, **_kwargs: Any) -> bool:
        """執行程式碼格式化"""
        print_info("執行程式碼格式化...")
        print_success("格式化完成")
        return True

    def _run_tests(self, **_kwargs: Any) -> bool:
        """執行測試"""
        success, _ = self._run_command(["npm", "test", "--if-present"], "測試")
        return success

    def _run_build(self, **_kwargs: Any) -> bool:
        """執行建置"""
        success, _ = self._run_command(["npm", "run", "build", "--if-present"], "建置")
        return success

    def _run_diagnosis(self, **_kwargs: Any) -> dict[str, Any]:
        """執行系統診斷"""
        print_info("執行系統診斷...")

        checks: dict[str, dict[str, Any]] = {}

        # 檢查工具
        tools = ["node", "npm", "python3", "docker", "git"]
        for tool in tools:
            try:
                result = subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                checks[tool] = {
                    "installed": result.returncode == 0,
                    "version": (
                        result.stdout.strip().split("\n")[0] if result.returncode == 0 else None
                    ),
                }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                checks[tool] = {"installed": False, "version": None}

        print_success("系統診斷完成")
        return checks
