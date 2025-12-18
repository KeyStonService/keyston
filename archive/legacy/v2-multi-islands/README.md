# v2-multi-islands

第二版：多語言自動化無人之島系統 (Automated Unmanned Islands)

此目錄包含 SynergyMesh 多語言自動化無人之島系統的實作，作為高階應用整合層。

## 🏝️ 核心概念

**無人之島概念**比無人機更具抽象性和擴展性：

- 🏝️ **無人之島**：每個功能域都是獨立的自治島嶼
- 🌊 **海洋連接**：島嶼間通過標準化協議通信
- ⚡ **自主運行**：每個島嶼內部完全自動化運作
- 🔄 **生態循環**：自我維護、自我進化的閉環系統

## 🏗️ 目錄結構

```
v2-multi-islands/
├── README.md                    # 本文檔
├── __init__.py                  # Python 套件初始化
├── main.py                      # 主執行入口
├── config/                      # 配置管理
│   ├── __init__.py
│   └── island_config.py         # 島嶼配置載入器
├── orchestrator/                # 島嶼協調器
│   ├── __init__.py
│   └── island_orchestrator.py   # 協調器核心
├── islands/                     # 各語言島嶼實作
│   ├── __init__.py
│   ├── base_island.py           # 基礎島嶼類別
│   ├── rust_island.py           # 🦀 Rust 島嶼
│   ├── go_island.py             # 🌊 Go 島嶼
│   ├── typescript_island.py     # ⚡ TypeScript 島嶼
│   ├── python_island.py         # 🐍 Python 島嶼
│   └── java_island.py           # ☕ Java 島嶼
├── bridges/                     # 多語言橋接層
│   ├── __init__.py
│   └── language_bridge.py       # 語言橋接器
└── utils/                       # 工具函數
    ├── __init__.py
    └── helpers.py               # 通用輔助函數
```

## 🌐 多語言島嶼分工

| 語言 | 島嶼類型 | 功能域 |
|------|---------|--------|
| 🦀 Rust | 性能核心島 | 性能監控、安全守護、數據管道 |
| 🌊 Go | 雲原生服務島 | API 網關、微服務網格、容器管理 |
| ⚡ TypeScript | 全棧開發島 | Web 儀表板、API 客戶端、實時監控 |
| 🐍 Python | AI 數據島 | AI 助手、數據分析、機器學習 |
| ☕ Java | 企業服務島 | 企業整合、消息隊列、批處理 |

## 🔗 與核心系統的映射關係

| v2-multi-islands | .devcontainer/automation | v1-python-drones |
|------------------|-------------------------|------------------|
| `orchestrator/island_orchestrator.py` | `drone-coordinator.py` | `coordinator_drone.py` |
| `islands/python_island.py` | `auto-pilot.js` | `autopilot_drone.py` |
| `bridges/language_bridge.py` | `code-generator.ts` | - |
| `config/island_config.py` | `drone-config.yml` | `drone_config.py` |

## 🚀 使用方式

### 直接執行

```bash
# 從專案根目錄
python3 v2-multi-islands/main.py --mode=auto

# 或指定特定島嶼
python3 v2-multi-islands/main.py --island=python
python3 v2-multi-islands/main.py --island=rust
python3 v2-multi-islands/main.py --island=go
```

### 透過自動化入口

```bash
./tools/scripts/automation-entry.sh
# 選擇選項 8: v2-multi-islands
```

### 作為 Python 模組導入

```python
from v2_multi_islands.orchestrator import IslandOrchestrator
from v2_multi_islands.islands import PythonIsland, RustIsland

# 建立協調器
orchestrator = IslandOrchestrator()
orchestrator.start()

# 啟動特定島嶼
python_island = PythonIsland()
python_island.activate()
```

## 📋 配置

島嶼配置從根目錄的 `island-control.yml` 載入：

```python
from v2_multi_islands.config import IslandConfig

config = IslandConfig.load()
print(config.islands)
```

## 🔄 從 v1 遷移

如需從 v1-python-drones 遷移至 v2-multi-islands，請使用：

```bash
./tools/scripts/automation-entry.sh
# 選擇選項 5: 版本遷移
# 選擇 1: v1 → v2
```

## 📝 版本歷史

- **v2.0.0** - 初始版本，多語言無人之島系統
