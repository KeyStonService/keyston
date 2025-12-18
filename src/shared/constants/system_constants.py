#!/usr/bin/env python3
"""
系統常數

定義 v1-python-drones 和 v2-multi-islands 共用的常數。
"""

# 系統版本
VERSION = "2.0.0"
SYSTEM_NAME = "SynergyMesh"

# 支援的運行模式
SUPPORTED_MODES = [
    "auto",      # 自動模式
    "manual",    # 手動模式
    "quick",     # 快速啟動
    "debug",     # 除錯模式
]

# 島嶼類型 (v2-multi-islands)
ISLAND_TYPES = [
    "rust",       # 🦀 Rust 性能核心島
    "go",         # 🌊 Go 雲原生服務島
    "typescript", # ⚡ TypeScript 全棧開發島
    "python",     # 🐍 Python AI 數據島
    "java",       # ☕ Java 企業服務島
]

# 無人機類型 (v1-python-drones)
DRONE_TYPES = [
    "coordinator",  # 協調器無人機
    "autopilot",    # 自動駕駛無人機
    "deployment",   # 部署無人機
]

# 橋接協議
BRIDGE_PROTOCOLS = [
    "grpc",          # gRPC 協議
    "rest",          # REST API
    "websocket",     # WebSocket
    "message_queue", # 消息隊列
]

# 預設超時時間（秒）
DEFAULT_TIMEOUT = 30

# 配置檔案
CONFIG_FILES = {
    "drone": "drone-config.yml",
    "island": "island-control.yml",
    "scaffold": "auto-scaffold.json",
}

# 環境類型
ENVIRONMENTS = [
    "development",
    "staging",
    "production",
]

# 健康檢查間隔（秒）
HEALTH_CHECK_INTERVAL = 30

# 最大重試次數
MAX_RETRIES = 3

# 重試延遲（秒）
RETRY_DELAY = 5
