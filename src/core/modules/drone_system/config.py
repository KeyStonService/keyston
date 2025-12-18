#!/usr/bin/env python3
"""
無人機系統配置模組

管理無人機系統的配置載入和驗證。
"""

from pathlib import Path
from typing import Any

from .utils import print_error, print_info, print_success, print_warn


class DroneConfig:
    """
    無人機系統配置管理器

    負責：
    - 載入配置檔案
    - 驗證配置
    - 提供配置存取
    """

    DEFAULT_CONFIG: dict[str, Any] = {
        "meta": {"version": "2.0.0", "name": "SynergyMesh Automation"},
        "drone_fleet": {},
        "automation": {"code_generation": {"enabled": True}},
    }

    def __init__(self, config_path: Path | str | None = None) -> None:
        """
        初始化配置管理器

        Args:
            config_path: 配置檔案路徑
        """
        self._config_path = Path(config_path) if config_path else None
        self._config: dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._loaded = False

    def load(self, config_path: Path | str | None = None) -> bool:
        """
        載入配置檔案

        Args:
            config_path: 配置檔案路徑（可選，覆蓋初始化時的路徑）

        Returns:
            是否成功載入
        """
        if config_path:
            self._config_path = Path(config_path)

        if not self._config_path:
            # 嘗試自動找尋配置檔案
            self._config_path = self._find_config_file()

        if not self._config_path or not self._config_path.exists():
            print_warn("配置檔案不存在，使用預設配置")
            self._config = self.DEFAULT_CONFIG.copy()
            return False

        print_info(f"載入配置: {self._config_path}")

        try:
            # 嘗試使用 PyYAML
            try:
                import yaml

                with open(self._config_path, encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or self.DEFAULT_CONFIG
            except ImportError:
                print_warn("PyYAML 未安裝，使用預設配置")
                self._config = self.DEFAULT_CONFIG.copy()

            self._loaded = True
            print_success("配置載入成功")
            return True

        except Exception as e:
            print_error(f"載入配置失敗: {e}")
            self._config = self.DEFAULT_CONFIG.copy()
            return False

    def _find_config_file(self) -> Path | None:
        """尋找配置檔案"""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            config_file = current / "drone-config.yml"
            if config_file.exists():
                return config_file
            current = current.parent
        return None

    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取配置值

        Args:
            key: 配置鍵（支援點分隔，如 'meta.version'）
            default: 預設值

        Returns:
            配置值
        """
        keys = key.split(".")
        value: Any = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        設定配置值

        Args:
            key: 配置鍵（支援點分隔）
            value: 配置值
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def get_all(self) -> dict[str, Any]:
        """
        獲取所有配置

        Returns:
            完整配置字典
        """
        return self._config.copy()

    def is_loaded(self) -> bool:
        """
        檢查配置是否已載入

        Returns:
            是否已載入
        """
        return self._loaded

    def validate(self) -> tuple[bool, list[str]]:
        """
        驗證配置

        Returns:
            (是否有效, 錯誤訊息列表)
        """
        errors: list[str] = []

        # 檢查必要欄位
        if "meta" not in self._config:
            errors.append("缺少 'meta' 配置區塊")

        if "drone_fleet" not in self._config:
            errors.append("缺少 'drone_fleet' 配置區塊")

        # 檢查版本
        version = self.get("meta.version")
        if not version:
            errors.append("缺少版本資訊 'meta.version'")

        return len(errors) == 0, errors

    def get_drone_fleet_config(self) -> dict[str, Any]:
        """
        獲取無人機編隊配置

        Returns:
            無人機編隊配置
        """
        return self.get("drone_fleet", {})

    def get_automation_config(self) -> dict[str, Any]:
        """
        獲取自動化配置

        Returns:
            自動化配置
        """
        return self.get("automation", {})

    def __repr__(self) -> str:
        return f"DroneConfig(path={self._config_path!r}, loaded={self._loaded})"
