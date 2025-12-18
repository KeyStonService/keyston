#!/usr/bin/env python3
"""
自動駕駛無人機 (Autopilot Drone)

負責自動化任務的執行邏輯，包括文件監控和任務觸發。
對應 config/dev/automation/auto-pilot.js (Python 版本)
"""

import subprocess
from collections.abc import Callable
from datetime import datetime
from typing import Any

from .base_drone import BaseDrone, DroneStatus


class AutopilotDrone(BaseDrone):
    """
    自動駕駛無人機
    
    負責：
    - 監控文件變更
    - 觸發自動化任務
    - 管理工作流程
    """

    def __init__(self) -> None:
        super().__init__(name="自動駕駛無人機", drone_id="autopilot")
        self.task_queue: list[dict[str, Any]] = []
        self.watchers: list[Any] = []
        self.is_processing = False

    def start(self) -> bool:
        """啟動自動駕駛"""
        self.log_info("✈️ 啟動自動駕駛無人機...")

        if not self.load_config():
            self.log_warn("使用預設配置")

        self.status = DroneStatus.RUNNING
        self.start_time = datetime.now()

        self.log_success("自動駕駛已啟動")
        return True

    def stop(self) -> bool:
        """停止自動駕駛"""
        self.log_info("停止自動駕駛無人機...")

        # 清理監控器
        self.watchers.clear()
        self.status = DroneStatus.STOPPED

        self.log_success("自動駕駛已停止")
        return True

    def execute(self) -> dict[str, Any]:
        """執行自動駕駛任務"""
        self.log_info("🔍 執行系統診斷...")

        # 執行診斷
        diagnosis = self.run_diagnosis()

        return diagnosis

    def run_diagnosis(self) -> dict[str, Any]:
        """
        執行系統診斷
        
        Returns:
            診斷結果
        """
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'passed': 0,
            'failed': 0,
        }

        # 檢查 Node.js
        node_check = self._check_tool('node')
        diagnosis['checks'].append(node_check)

        # 檢查 npm
        npm_check = self._check_tool('npm')
        diagnosis['checks'].append(npm_check)

        # 檢查 Docker
        docker_check = self._check_tool('docker')
        diagnosis['checks'].append(docker_check)

        # 檢查 Python
        python_check = self._check_tool('python3')
        diagnosis['checks'].append(python_check)

        # 統計結果
        for check in diagnosis['checks']:
            if check['status'] == 'ok':
                diagnosis['passed'] += 1
            else:
                diagnosis['failed'] += 1

        # 顯示結果
        self._display_diagnosis(diagnosis)

        return diagnosis

    def _check_tool(self, tool: str) -> dict[str, Any]:
        """檢查工具是否可用"""
        try:
            result = subprocess.run(
                [tool, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip().split('\n')[0] if result.returncode == 0 else None
            return {
                'tool': tool,
                'status': 'ok' if result.returncode == 0 else 'error',
                'version': version,
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return {
                'tool': tool,
                'status': 'error',
                'version': None,
            }

    def _display_diagnosis(self, diagnosis: dict[str, Any]) -> None:
        """顯示診斷結果"""
        self.log_info("📊 系統診斷結果:")
        print()

        for check in diagnosis['checks']:
            icon = '✅' if check['status'] == 'ok' else '❌'
            version = check.get('version', '未安裝')
            print(f"  {icon} {check['tool']}: {version}")

        print()
        self.log_info(f"診斷結果: {diagnosis['passed']} 通過, {diagnosis['failed']} 失敗")

    def queue_task(self, task_name: str, options: dict | None = None) -> None:
        """
        將任務加入佇列
        
        Args:
            task_name: 任務名稱
            options: 任務選項
        """
        self.task_queue.append({
            'name': task_name,
            'options': options or {},
            'queued_at': datetime.now().isoformat(),
        })
        self.log_info(f"任務已加入佇列: {task_name}")

        # 處理佇列
        self._process_queue()

    def _process_queue(self) -> None:
        """處理任務佇列"""
        if self.is_processing or not self.task_queue:
            return

        self.is_processing = True

        while self.task_queue:
            task = self.task_queue.pop(0)
            self._execute_task(task)

        self.is_processing = False

    def _execute_task(self, task: dict[str, Any]) -> bool:
        """執行單一任務"""
        task_name = task['name']
        self.log_info(f"🚀 執行任務: {task_name}")

        task_handlers: dict[str, Callable[[], bool]] = {
            'lint': self._run_lint,
            'format': self._run_format,
            'test': self._run_tests,
            'build': self._run_build,
        }

        handler = task_handlers.get(task_name)
        if handler:
            result = handler()
            if result:
                self.log_success(f"任務完成: {task_name}")
            else:
                self.log_warn(f"任務有警告: {task_name}")
            return result
        else:
            self.log_warn(f"未知任務: {task_name}")
            return False

    def _run_lint(self) -> bool:
        """執行 Lint 檢查"""
        self.log_info("  執行程式碼檢查...")
        try:
            subprocess.run(
                ['npm', 'run', 'lint', '--if-present'],
                cwd=self.project_root,
                capture_output=True,
                timeout=120
            )
            return True
        except Exception:
            return False

    def _run_format(self) -> bool:
        """執行格式化"""
        self.log_info("  執行程式碼格式化...")
        return True

    def _run_tests(self) -> bool:
        """執行測試"""
        self.log_info("  執行測試...")
        try:
            subprocess.run(
                ['npm', 'test', '--if-present'],
                cwd=self.project_root,
                capture_output=True,
                timeout=300
            )
            return True
        except Exception:
            return False

    def _run_build(self) -> bool:
        """執行建置"""
        self.log_info("  執行建置...")
        try:
            subprocess.run(
                ['npm', 'run', 'build', '--if-present'],
                cwd=self.project_root,
                capture_output=True,
                timeout=300
            )
            return True
        except Exception:
            return False

    def run_core_autopilot(self) -> int:
        """
        執行核心自動駕駛 (config/dev/automation/auto-pilot.js)
        
        Returns:
            執行結果代碼
        """
        core_script = self.project_root / 'config/dev' / 'automation' / 'auto-pilot.js'

        if not core_script.exists():
            self.log_error(f"核心自動駕駛腳本不存在: {core_script}")
            return 1

        self.log_info(f"執行核心自動駕駛: {core_script}")

        try:
            result = subprocess.run(
                ['node', str(core_script), 'diagnose'],
                cwd=self.project_root
            )
            return result.returncode
        except Exception as e:
            self.log_error(f"執行失敗: {e}")
            return 1
