#!/usr/bin/env python3
"""
Rust 島嶼 - 高性能核心

負責性能監控、安全守護、數據管道等高性能任務。
"""

from datetime import datetime
from typing import Any

from .base_island import BaseIsland, IslandStatus


class RustIsland(BaseIsland):
    """
    🦀 Rust 性能核心島
    
    優勢：
    - 極致性能與內存安全
    - 並發處理能力強
    - 系統級操作優勢
    
    能力：
    - performance_monitor: 性能監控
    - security_guardian: 安全守護
    - data_pipeline: 數據管道
    - system_orchestrator: 系統協調
    """

    def __init__(self) -> None:
        super().__init__(
            name="🦀 Rust 性能核心島",
            island_id="rust",
            language="rust"
        )
        self.capabilities = [
            "performance_monitor",
            "security_guardian",
            "data_pipeline",
            "system_orchestrator"
        ]

    def _get_language_check_command(self) -> tuple[str, str]:
        return ("rustc", "--version")

    def activate(self) -> bool:
        """啟動 Rust 島嶼"""
        self.log_info("啟動 Rust 性能核心島...")

        # 檢查 Rust 工具鏈
        available, version = self.check_language_tool()
        if not available:
            self.log_warn("Rust 未安裝，島嶼將以受限模式運行")
        else:
            self.log_info(f"Rust 版本: {version}")

        self.status = IslandStatus.ACTIVATING
        self.activated_at = datetime.now()

        # 初始化性能監控
        self._init_performance_monitor()

        self.status = IslandStatus.ACTIVE
        self.log_success("Rust 性能核心島已啟動")
        return True

    def deactivate(self) -> bool:
        """停止 Rust 島嶼"""
        self.log_info("停止 Rust 性能核心島...")
        self.status = IslandStatus.DORMANT
        self.activated_at = None
        self.log_success("Rust 性能核心島已停止")
        return True

    def execute(self) -> dict[str, Any]:
        """執行性能分析任務"""
        self.log_info("🔍 執行性能分析...")

        result = {
            'island': self.island_id,
            'task': 'performance_analysis',
            'timestamp': datetime.now().isoformat(),
            'metrics': self._collect_metrics(),
        }

        self._display_metrics(result['metrics'])
        return result

    def _init_performance_monitor(self) -> None:
        """初始化性能監控器"""
        self.log_info("  初始化性能監控器...")

    def _collect_metrics(self) -> dict[str, Any]:
        """收集性能指標"""
        import os

        try:
            load_avg = os.getloadavg()
        except (OSError, AttributeError):
            load_avg = (0.0, 0.0, 0.0)

        return {
            'cpu_load': {
                '1min': load_avg[0],
                '5min': load_avg[1],
                '15min': load_avg[2],
            },
            'rust_available': self.check_language_tool()[0],
        }

    def _display_metrics(self, metrics: dict[str, Any]) -> None:
        """顯示性能指標"""
        self.log_info("📊 性能指標:")
        print(f"  CPU 負載: {metrics['cpu_load']['1min']:.2f} (1min)")
        print(f"  Rust 可用: {'✅' if metrics['rust_available'] else '❌'}")
