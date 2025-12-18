#!/usr/bin/env python3
"""
Python 島嶼 - AI 與數據科學

負責 AI 代碼助手、數據分析、機器學習管道等任務。
"""

import subprocess
import sys
from datetime import datetime
from typing import Any

from .base_island import BaseIsland, IslandStatus


class PythonIsland(BaseIsland):
    """
    🐍 Python AI 數據島
    
    優勢：
    - AI/ML 生態最完善
    - 腳本自動化能力強
    - 數據處理優勢明顯
    
    能力：
    - ai_code_assistant: AI 代碼助手
    - data_analysis: 數據分析
    - ml_pipeline: 機器學習管道
    - automation_scripts: 自動化腳本
    """

    def __init__(self) -> None:
        super().__init__(
            name="🐍 Python AI 數據島",
            island_id="python",
            language="python"
        )
        self.capabilities = [
            "ai_code_assistant",
            "data_analysis",
            "ml_pipeline",
            "automation_scripts"
        ]

    def _get_language_check_command(self) -> tuple[str, str]:
        return ("python3", "--version")

    def activate(self) -> bool:
        """啟動 Python 島嶼"""
        self.log_info("啟動 Python AI 數據島...")

        available, version = self.check_language_tool()
        if available:
            self.log_info(f"Python 版本: {version}")
        else:
            self.log_error("Python 未安裝")
            return False

        self.status = IslandStatus.ACTIVATING
        self.activated_at = datetime.now()

        # 檢查 AI/ML 套件
        self._check_ml_packages()

        self.status = IslandStatus.ACTIVE
        self.log_success("Python AI 數據島已啟動")
        return True

    def deactivate(self) -> bool:
        """停止 Python 島嶼"""
        self.log_info("停止 Python AI 數據島...")
        self.status = IslandStatus.DORMANT
        self.activated_at = None
        self.log_success("Python AI 數據島已停止")
        return True

    def execute(self) -> dict[str, Any]:
        """執行 Python 環境檢查"""
        self.log_info("🔍 執行 Python 環境檢查...")

        result = {
            'island': self.island_id,
            'task': 'python_environment_check',
            'timestamp': datetime.now().isoformat(),
            'python_info': self._get_python_info(),
            'packages': self._check_packages(),
        }

        self._display_result(result)
        return result

    def _check_ml_packages(self) -> None:
        """檢查 ML 套件"""
        self.log_info("  檢查 AI/ML 套件...")

    def _get_python_info(self) -> dict[str, Any]:
        """取得 Python 資訊"""
        return {
            'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'implementation': sys.implementation.name,
            'platform': sys.platform,
        }

    def _check_packages(self) -> dict[str, bool]:
        """檢查重要套件"""
        packages = {}

        check_list = [
            'numpy',
            'pandas',
            'requests',
            'pyyaml',
            'pytest',
        ]

        for pkg in check_list:
            try:
                __import__(pkg)
                packages[pkg] = True
            except ImportError:
                packages[pkg] = False

        return packages

    def _display_result(self, result: dict[str, Any]) -> None:
        """顯示結果"""
        self.log_info("📊 Python 環境狀態:")

        info = result['python_info']
        print(f"\n  Python 版本: {info['version']}")
        print(f"  實作: {info['implementation']}")
        print(f"  平台: {info['platform']}")

        print("\n  套件:")
        for pkg, available in result['packages'].items():
            status = '✅' if available else '❌'
            print(f"    {status} {pkg}")

    def run_v1_drones(self) -> int:
        """
        執行 v1-python-drones 系統
        
        Returns:
            執行結果代碼
        """
        v1_main = self.project_root / 'v1-python-drones' / 'main.py'

        if not v1_main.exists():
            self.log_error(f"v1-python-drones 不存在: {v1_main}")
            return 1

        self.log_info("執行 v1-python-drones 系統...")

        try:
            result = subprocess.run(
                ['python3', str(v1_main), '--mode=auto'],
                cwd=self.project_root
            )
            return result.returncode
        except Exception as e:
            self.log_error(f"執行失敗: {e}")
            return 1
