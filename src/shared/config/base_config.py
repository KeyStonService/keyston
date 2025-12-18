#!/usr/bin/env python3
"""
基礎配置類別

提供 v1-python-drones 和 v2-multi-islands 共用的配置基礎設施。
"""

from pathlib import Path
from typing import Any, Optional


class BaseConfig:
    """
    基礎配置類別
    
    此類別提供配置載入和管理的基礎功能，供 v1 和 v2 版本繼承使用。
    """
    
    _instance: Optional['BaseConfig'] = None
    _config: dict[str, Any] = {}
    _config_path: Optional[Path] = None
    
    def __new__(cls) -> 'BaseConfig':
        """單例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not self._config:
            self._project_root = self._find_project_root()
    
    @classmethod
    def load(cls) -> 'BaseConfig':
        """載入配置的工廠方法"""
        return cls()
    
    def _find_project_root(self) -> Path:
        """尋找專案根目錄"""
        current = Path(__file__).resolve().parent
        
        # 根目錄標識文件
        root_markers = [
            'drone-config.yml',
            'island-control.yml',
            'package.json',
            'automation-entry.sh',
        ]
        
        while current != current.parent:
            for marker in root_markers:
                if (current / marker).exists():
                    return current
            current = current.parent
        
        return Path.cwd()
    
    @property
    def project_root(self) -> Path:
        """取得專案根目錄"""
        return self._project_root
    
    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """載入 YAML 配置檔案"""
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            print("[WARN] PyYAML 未安裝，無法載入 YAML 配置")
            return {}
        except FileNotFoundError:
            print(f"[WARN] 配置檔案不存在: {path}")
            return {}
        except Exception as e:
            print(f"[ERROR] 載入配置失敗: {e}")
            return {}
    
    def _load_json(self, path: Path) -> dict[str, Any]:
        """載入 JSON 配置檔案"""
        import json
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[WARN] 配置檔案不存在: {path}")
            return {}
        except Exception as e:
            print(f"[ERROR] 載入配置失敗: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """取得配置值"""
        return self._config.get(key, default)
    
    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """取得嵌套配置值"""
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value
    
    @property
    def meta(self) -> dict[str, Any]:
        """取得元資訊"""
        return self._config.get('meta', {})
    
    @property
    def version(self) -> str:
        """取得版本號"""
        return self.meta.get('version', '0.0.0')
