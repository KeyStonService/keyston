#!/usr/bin/env python3
"""
Java 島嶼 - 企業級服務

負責企業整合、消息隊列管理、批處理等企業級任務。
"""

from datetime import datetime
from typing import Any
import subprocess

from .base_island import BaseIsland, IslandStatus


class JavaIsland(BaseIsland):
    """
    ☕ Java 企業服務島
    
    優勢：
    - 企業級穩定性
    - 成熟的框架生態
    - 強大的並發處理
    
    能力：
    - enterprise_integration: 企業整合
    - message_queue_manager: 消息隊列管理
    - batch_processing: 批處理
    - legacy_system_bridge: 遺留系統橋接
    """
    
    def __init__(self) -> None:
        super().__init__(
            name="☕ Java 企業服務島",
            island_id="java",
            language="java"
        )
        self.capabilities = [
            "enterprise_integration",
            "message_queue_manager",
            "batch_processing",
            "legacy_system_bridge"
        ]
    
    def _get_language_check_command(self) -> tuple[str, str]:
        return ("java", "--version")
    
    def activate(self) -> bool:
        """啟動 Java 島嶼"""
        self.log_info("啟動 Java 企業服務島...")
        
        available, version = self.check_language_tool()
        if not available:
            self.log_warn("Java 未安裝，島嶼將以受限模式運行")
        else:
            self.log_info(f"Java 版本: {version}")
        
        self.status = IslandStatus.ACTIVATING
        self.activated_at = datetime.now()
        
        # 檢查企業級工具
        self._check_enterprise_tools()
        
        self.status = IslandStatus.ACTIVE
        self.log_success("Java 企業服務島已啟動")
        return True
    
    def deactivate(self) -> bool:
        """停止 Java 島嶼"""
        self.log_info("停止 Java 企業服務島...")
        self.status = IslandStatus.DORMANT
        self.activated_at = None
        self.log_success("Java 企業服務島已停止")
        return True
    
    def execute(self) -> dict[str, Any]:
        """執行企業環境檢查"""
        self.log_info("🔍 執行企業環境檢查...")
        
        result = {
            'island': self.island_id,
            'task': 'enterprise_environment_check',
            'timestamp': datetime.now().isoformat(),
            'tools': self._check_java_tools(),
        }
        
        self._display_result(result)
        return result
    
    def _check_enterprise_tools(self) -> None:
        """檢查企業級工具"""
        self.log_info("  檢查企業級工具...")
    
    def _check_java_tools(self) -> dict[str, Any]:
        """檢查 Java 相關工具"""
        tools = {}
        
        tool_commands = [
            ('java', ['java', '--version']),
            ('javac', ['javac', '--version']),
            ('mvn', ['mvn', '--version']),
            ('gradle', ['gradle', '--version']),
        ]
        
        for tool_name, cmd in tool_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                version = result.stdout.strip().split('\n')[0] if result.returncode == 0 else None
                tools[tool_name] = {
                    'available': result.returncode == 0,
                    'version': version,
                }
            except (FileNotFoundError, subprocess.TimeoutExpired):
                tools[tool_name] = {'available': False, 'version': None}
        
        return tools
    
    def _display_result(self, result: dict[str, Any]) -> None:
        """顯示結果"""
        self.log_info("📊 Java 企業環境狀態:")
        
        print("\n  工具:")
        for tool, info in result['tools'].items():
            status = '✅' if info['available'] else '❌'
            version = info.get('version', '未安裝')
            if version and len(version) > 50:
                version = version[:50] + '...'
            print(f"    {status} {tool}: {version}")
