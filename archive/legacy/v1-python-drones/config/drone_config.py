#!/usr/bin/env python3
"""
SynergyMesh 無人機配置載入器

此模組負責從 drone-config.yml 載入配置並提供給無人機使用。
"""

from pathlib import Path
from typing import Any, Optional


class DroneConfig:
    """無人機配置管理器"""

    _instance: Optional['DroneConfig'] = None
    _config: dict[str, Any] = {}

    def __new__(cls) -> 'DroneConfig':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._config:
            self._load_config()

    @classmethod
    def load(cls) -> 'DroneConfig':
        """載入配置的工廠方法"""
        return cls()

    def _find_project_root(self) -> Path:
        """尋找專案根目錄"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / 'drone-config.yml').exists():
                return current
            if (current / 'package.json').exists():
                return current
            current = current.parent
        return Path.cwd()

    def _load_config(self) -> None:
        """從 drone-config.yml 載入配置"""
        project_root = self._find_project_root()
        config_path = project_root / 'drone-config.yml'

        if not config_path.exists():
            print(f"[WARN] 配置檔案不存在: {config_path}")
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
                'name': 'SynergyMesh Automation',
            },
            'drone_fleet': {
                'coordinator': {
                    'name': '主協調器',
                    'script': 'config/dev/automation/drone-coordinator.py',
                    'priority': 1,
                    'auto_start': True,
                },
                'autopilot': {
                    'name': '自動駕駛',
                    'script': 'config/dev/automation/auto-pilot.js',
                    'priority': 2,
                    'auto_start': True,
                },
            },
            'automation': {
                'code_generation': {'enabled': True},
                'deployment': {'enabled': True},
            },
            'version_control': {
                'current_version': 'v1',
                'supported_versions': ['v1', 'v2'],
            },
        }

    @property
    def meta(self) -> dict[str, Any]:
        """取得元資訊"""
        return self._config.get('meta', {})

    @property
    def drone_fleet(self) -> dict[str, Any]:
        """取得無人機編隊配置"""
        return self._config.get('drone_fleet', {})

    @property
    def automation(self) -> dict[str, Any]:
        """取得自動化配置"""
        return self._config.get('automation', {})

    @property
    def environments(self) -> dict[str, Any]:
        """取得環境配置"""
        return self._config.get('environments', {})

    @property
    def version_control(self) -> dict[str, Any]:
        """取得版本控制配置"""
        return self._config.get('version_control', {})

    @property
    def integrations(self) -> dict[str, Any]:
        """取得整合配置"""
        return self._config.get('integrations', {})

    @property
    def monitoring(self) -> dict[str, Any]:
        """取得監控配置"""
        return self._config.get('monitoring', {})

    @property
    def security(self) -> dict[str, Any]:
        """取得安全配置"""
        return self._config.get('security', {})

    def get(self, key: str, default: Any = None) -> Any:
        """取得配置值"""
        return self._config.get(key, default)

    def get_drone(self, drone_id: str) -> dict[str, Any] | None:
        """取得特定無人機的配置"""
        return self.drone_fleet.get(drone_id)

    def get_environment(self, env_name: str) -> dict[str, Any] | None:
        """取得特定環境的配置"""
        return self.environments.get(env_name)
