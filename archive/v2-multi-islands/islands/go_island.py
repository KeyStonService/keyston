#!/usr/bin/env python3
"""
Go 島嶼 - 雲原生服務

負責 API 網關、微服務網格、容器管理等雲原生任務。
"""

from datetime import datetime
from typing import Any
import subprocess

from .base_island import BaseIsland, IslandStatus


class GoIsland(BaseIsland):
    """
    🌊 Go 雲原生服務島
    
    優勢：
    - 雲原生生態完善
    - 並發模型優秀
    - 部署簡單快速
    
    能力：
    - api_gateway: API 網關
    - microservice_mesh: 微服務網格
    - container_manager: 容器管理
    - distributed_cache: 分散式緩存
    """
    
    def __init__(self) -> None:
        super().__init__(
            name="🌊 Go 雲原生服務島",
            island_id="go",
            language="go"
        )
        self.capabilities = [
            "api_gateway",
            "microservice_mesh",
            "container_manager",
            "distributed_cache"
        ]
    
    def _get_language_check_command(self) -> tuple[str, str]:
        return ("go", "version")
    
    def activate(self) -> bool:
        """啟動 Go 島嶼"""
        self.log_info("啟動 Go 雲原生服務島...")
        
        available, version = self.check_language_tool()
        if not available:
            self.log_warn("Go 未安裝，島嶼將以受限模式運行")
        else:
            self.log_info(f"Go 版本: {version}")
        
        self.status = IslandStatus.ACTIVATING
        self.activated_at = datetime.now()
        
        # 檢查 Docker 和 Kubernetes 工具
        self._check_cloud_native_tools()
        
        self.status = IslandStatus.ACTIVE
        self.log_success("Go 雲原生服務島已啟動")
        return True
    
    def deactivate(self) -> bool:
        """停止 Go 島嶼"""
        self.log_info("停止 Go 雲原生服務島...")
        self.status = IslandStatus.DORMANT
        self.activated_at = None
        self.log_success("Go 雲原生服務島已停止")
        return True
    
    def execute(self) -> dict[str, Any]:
        """執行雲原生服務檢查"""
        self.log_info("🔍 執行雲原生服務檢查...")
        
        result = {
            'island': self.island_id,
            'task': 'cloud_native_check',
            'timestamp': datetime.now().isoformat(),
            'services': self._check_services(),
        }
        
        self._display_services(result['services'])
        return result
    
    def _check_cloud_native_tools(self) -> dict[str, bool]:
        """檢查雲原生工具"""
        tools = {
            'docker': self._check_tool('docker', '--version'),
            'kubectl': self._check_tool('kubectl', 'version', '--client'),
            'helm': self._check_tool('helm', 'version', '--short'),
        }
        return tools
    
    def _check_tool(self, *args: str) -> bool:
        """檢查工具是否可用"""
        try:
            result = subprocess.run(
                list(args),
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_services(self) -> dict[str, Any]:
        """檢查服務狀態"""
        tools = self._check_cloud_native_tools()
        
        return {
            'docker': {
                'available': tools.get('docker', False),
                'status': 'running' if tools.get('docker') else 'not_installed',
            },
            'kubernetes': {
                'available': tools.get('kubectl', False),
                'status': 'available' if tools.get('kubectl') else 'not_installed',
            },
            'helm': {
                'available': tools.get('helm', False),
                'status': 'available' if tools.get('helm') else 'not_installed',
            },
        }
    
    def _display_services(self, services: dict[str, Any]) -> None:
        """顯示服務狀態"""
        self.log_info("📊 雲原生服務狀態:")
        for service, info in services.items():
            status = '✅' if info['available'] else '❌'
            print(f"  {status} {service}: {info['status']}")
