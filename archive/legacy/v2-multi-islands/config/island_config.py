#!/usr/bin/env python3
"""
SynergyMesh 島嶼配置載入器

此模組負責從 island-control.yml 或 drone-config.yml 載入配置。
"""

from pathlib import Path
from typing import Any, Optional


class IslandConfig:
    """島嶼配置管理器"""

    _instance: Optional['IslandConfig'] = None
    _config: dict[str, Any] = {}

    def __new__(cls) -> 'IslandConfig':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._config:
            self._load_config()

    @classmethod
    def load(cls) -> 'IslandConfig':
        """載入配置的工廠方法"""
        return cls()

    def _find_project_root(self) -> Path:
        """尋找專案根目錄"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / 'island-control.yml').exists():
                return current
            if (current / 'drone-config.yml').exists():
                return current
            if (current / 'package.json').exists():
                return current
            current = current.parent
        return Path.cwd()

    def _load_config(self) -> None:
        """從配置檔案載入配置"""
        project_root = self._find_project_root()

        # 優先嘗試 island-control.yml
        config_path = project_root / 'island-control.yml'
        if not config_path.exists():
            # 回退到 drone-config.yml
            config_path = project_root / 'drone-config.yml'

        if not config_path.exists():
            print("[WARN] 配置檔案不存在，使用預設配置")
            self._config = self._get_default_config()
            return

        try:
            import yaml
            with open(config_path, encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            print(f"[INFO] 配置已載入: {config_path}")
        except ImportError:
            print("[WARN] PyYAML 未安裝，使用預設配置")
            self._config = self._get_default_config()
        except Exception as e:
            print(f"[ERROR] 載入配置失敗: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """取得預設配置"""
        return {
            'meta': {
                'version': '2.0.0',
                'name': 'SynergyMesh Multi-Islands',
            },
            'islands': {
                'rust': {
                    'name': 'Rust 性能核心島',
                    'enabled': True,
                    'priority': 1,
                    'capabilities': ['performance_monitor', 'security_guardian', 'data_pipeline'],
                },
                'go': {
                    'name': 'Go 雲原生服務島',
                    'enabled': True,
                    'priority': 2,
                    'capabilities': ['api_gateway', 'microservice_mesh', 'container_manager'],
                },
                'typescript': {
                    'name': 'TypeScript 全棧開發島',
                    'enabled': True,
                    'priority': 3,
                    'capabilities': ['web_dashboard', 'api_client_generator', 'real_time_monitor'],
                },
                'python': {
                    'name': 'Python AI 數據島',
                    'enabled': True,
                    'priority': 4,
                    'capabilities': ['ai_code_assistant', 'data_analysis', 'ml_pipeline'],
                },
                'java': {
                    'name': 'Java 企業服務島',
                    'enabled': True,
                    'priority': 5,
                    'capabilities': ['enterprise_integration', 'message_queue_manager', 'batch_processing'],
                },
            },
            'orchestrator': {
                'auto_start': True,
                'health_check_interval': 30,
                'max_concurrent_islands': 5,
            },
            'bridges': {
                'enabled': True,
                'protocols': ['grpc', 'rest', 'websocket'],
            },
        }

    @property
    def meta(self) -> dict[str, Any]:
        """取得元資訊"""
        return self._config.get('meta', {})

    @property
    def islands(self) -> dict[str, Any]:
        """取得島嶼配置"""
        return self._config.get('islands', self._get_default_config()['islands'])

    @property
    def orchestrator(self) -> dict[str, Any]:
        """取得協調器配置"""
        return self._config.get('orchestrator', {})

    @property
    def bridges(self) -> dict[str, Any]:
        """取得橋接配置"""
        return self._config.get('bridges', {})

    @property
    def v2_multi_islands(self) -> dict[str, Any]:
        """取得 v2-multi-islands 專用配置"""
        return self._config.get('v2_multi_islands', {})

    def get(self, key: str, default: Any = None) -> Any:
        """取得配置值"""
        return self._config.get(key, default)

    def get_island(self, island_id: str) -> dict[str, Any] | None:
        """取得特定島嶼的配置"""
        return self.islands.get(island_id)

    def get_enabled_islands(self) -> list[str]:
        """取得所有啟用的島嶼"""
        return [
            island_id
            for island_id, config in self.islands.items()
            if config.get('enabled', True)
        ]
