#!/usr/bin/env python3
"""
基礎島嶼類別

所有語言島嶼的抽象基礎類別，定義共通介面和功能。
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import subprocess
import sys

_current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_current_dir.parent))


class IslandStatus:
    """島嶼狀態"""
    DORMANT = "dormant"       # 休眠
    ACTIVATING = "activating"  # 啟動中
    ACTIVE = "active"         # 活躍
    SUSPENDED = "suspended"   # 暫停
    ERROR = "error"          # 錯誤


class Colors:
    """終端機顏色輸出"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


class BaseIsland(ABC):
    """
    基礎島嶼抽象類別
    
    所有具體語言島嶼都應繼承此類別並實作抽象方法。
    
    Attributes:
        name: 島嶼名稱
        island_id: 島嶼識別碼
        language: 主要程式語言
        status: 當前狀態
        capabilities: 島嶼能力列表
    """
    
    def __init__(self, name: str, island_id: str, language: str) -> None:
        self.name = name
        self.island_id = island_id
        self.language = language
        self.status = IslandStatus.DORMANT
        self.capabilities: list[str] = []
        self.config: dict[str, Any] = {}
        self.activated_at: Optional[datetime] = None
        self._project_root = self._find_project_root()
    
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
    
    @property
    def project_root(self) -> Path:
        """取得專案根目錄"""
        return self._project_root
    
    # 日誌輸出方法
    def log_info(self, message: str) -> None:
        """輸出資訊訊息"""
        print(f"{Colors.BLUE}[{self.name}][INFO]{Colors.NC} {message}")
    
    def log_success(self, message: str) -> None:
        """輸出成功訊息"""
        print(f"{Colors.GREEN}[{self.name}][SUCCESS]{Colors.NC} {message}")
    
    def log_warn(self, message: str) -> None:
        """輸出警告訊息"""
        print(f"{Colors.YELLOW}[{self.name}][WARN]{Colors.NC} {message}")
    
    def log_error(self, message: str) -> None:
        """輸出錯誤訊息"""
        print(f"{Colors.RED}[{self.name}][ERROR]{Colors.NC} {message}")
    
    def load_config(self) -> bool:
        """載入島嶼配置"""
        try:
            from config import IslandConfig
            island_config = IslandConfig.load()
            self.config = island_config.get_island(self.island_id) or {}
            self.capabilities = self.config.get('capabilities', [])
            self.log_success("配置已載入")
            return True
        except Exception as e:
            self.log_error(f"載入配置失敗: {e}")
            return False
    
    def check_language_tool(self) -> tuple[bool, Optional[str]]:
        """
        檢查語言工具是否可用
        
        Returns:
            (是否可用, 版本資訊)
        """
        cmd, arg = self._get_language_check_command()
        try:
            result = subprocess.run(
                [cmd, arg],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                return True, version
            return False, None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, None
    
    @abstractmethod
    def _get_language_check_command(self) -> tuple[str, str]:
        """取得語言檢查命令"""
        pass
    
    @abstractmethod
    def activate(self) -> bool:
        """
        啟動島嶼
        
        Returns:
            是否啟動成功
        """
        pass
    
    @abstractmethod
    def deactivate(self) -> bool:
        """
        停止島嶼
        
        Returns:
            是否停止成功
        """
        pass
    
    @abstractmethod
    def execute(self) -> Any:
        """
        執行島嶼主要任務
        
        Returns:
            執行結果
        """
        pass
    
    def health_check(self) -> bool:
        """
        健康檢查
        
        Returns:
            是否健康
        """
        available, _ = self.check_language_tool()
        return available and self.status in [IslandStatus.DORMANT, IslandStatus.ACTIVE]
    
    def get_status(self) -> dict[str, Any]:
        """取得島嶼狀態資訊"""
        available, version = self.check_language_tool()
        return {
            "name": self.name,
            "island_id": self.island_id,
            "language": self.language,
            "status": self.status,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "capabilities": self.capabilities,
            "tool_available": available,
            "tool_version": version,
            "healthy": self.health_check(),
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', status='{self.status}')>"
