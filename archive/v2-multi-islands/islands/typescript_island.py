#!/usr/bin/env python3
"""
TypeScript 島嶼 - 全棧開發

負責 Web 儀表板、API 客戶端生成、實時監控等任務。
"""

from datetime import datetime
from pathlib import Path
from typing import Any
import subprocess

from .base_island import BaseIsland, IslandStatus


class TypeScriptIsland(BaseIsland):
    """
    ⚡ TypeScript 全棧開發島
    
    優勢：
    - 前後端統一語言
    - 豐富的生態系統
    - 開發效率極高
    
    能力：
    - web_dashboard: Web 儀表板
    - api_client_generator: API 客戶端生成
    - real_time_monitor: 實時監控
    - dev_tools_suite: 開發工具套件
    """
    
    def __init__(self) -> None:
        super().__init__(
            name="⚡ TypeScript 全棧開發島",
            island_id="typescript",
            language="typescript"
        )
        self.capabilities = [
            "web_dashboard",
            "api_client_generator",
            "real_time_monitor",
            "dev_tools_suite"
        ]
    
    def _get_language_check_command(self) -> tuple[str, str]:
        return ("tsc", "--version")
    
    def activate(self) -> bool:
        """啟動 TypeScript 島嶼"""
        self.log_info("啟動 TypeScript 全棧開發島...")
        
        # 檢查 TypeScript 和 Node.js
        available, version = self.check_language_tool()
        if not available:
            self.log_warn("TypeScript 未安裝，檢查 Node.js...")
            node_available = self._check_node()
            if node_available:
                self.log_info("Node.js 可用，可透過 npx 使用 TypeScript")
        else:
            self.log_info(f"TypeScript 版本: {version}")
        
        self.status = IslandStatus.ACTIVATING
        self.activated_at = datetime.now()
        
        self.status = IslandStatus.ACTIVE
        self.log_success("TypeScript 全棧開發島已啟動")
        return True
    
    def deactivate(self) -> bool:
        """停止 TypeScript 島嶼"""
        self.log_info("停止 TypeScript 全棧開發島...")
        self.status = IslandStatus.DORMANT
        self.activated_at = None
        self.log_success("TypeScript 全棧開發島已停止")
        return True
    
    def execute(self) -> dict[str, Any]:
        """執行開發環境檢查"""
        self.log_info("🔍 執行開發環境檢查...")
        
        result = {
            'island': self.island_id,
            'task': 'dev_environment_check',
            'timestamp': datetime.now().isoformat(),
            'tools': self._check_dev_tools(),
            'project_info': self._check_project(),
        }
        
        self._display_result(result)
        return result
    
    def _check_node(self) -> bool:
        """檢查 Node.js"""
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_dev_tools(self) -> dict[str, Any]:
        """檢查開發工具"""
        tools = {}
        
        tool_commands = [
            ('node', ['node', '--version']),
            ('npm', ['npm', '--version']),
            ('tsc', ['tsc', '--version']),
            ('eslint', ['eslint', '--version']),
        ]
        
        for tool_name, cmd in tool_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                tools[tool_name] = {
                    'available': result.returncode == 0,
                    'version': result.stdout.strip().split('\n')[0] if result.returncode == 0 else None,
                }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                tools[tool_name] = {'available': False, 'version': None}
        
        return tools
    
    def _check_project(self) -> dict[str, Any]:
        """檢查專案資訊"""
        package_json = self.project_root / 'package.json'
        tsconfig = self.project_root / 'tsconfig.json'
        
        return {
            'has_package_json': package_json.exists(),
            'has_tsconfig': tsconfig.exists(),
            'project_root': str(self.project_root),
        }
    
    def _display_result(self, result: dict[str, Any]) -> None:
        """顯示結果"""
        self.log_info("📊 開發環境狀態:")
        
        print("\n  工具:")
        for tool, info in result['tools'].items():
            status = '✅' if info['available'] else '❌'
            version = info.get('version', '未安裝')
            print(f"    {status} {tool}: {version}")
        
        print("\n  專案:")
        print(f"    package.json: {'✅' if result['project_info']['has_package_json'] else '❌'}")
        print(f"    tsconfig.json: {'✅' if result['project_info']['has_tsconfig'] else '❌'}")
