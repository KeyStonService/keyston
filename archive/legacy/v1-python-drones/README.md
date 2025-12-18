# v1-python-drones

第一版：Python 無人機系統 - 高階應用整合

此目錄包含 SynergyMesh 自動化開發系統的 Python 無人機實作，作為高階應用整合層。

## 🏗️ 目錄結構

```
v1-python-drones/
├── README.md                    # 本文檔
├── __init__.py                  # Python 套件初始化
├── config/                      # 配置管理
│   ├── __init__.py
│   └── drone_config.py          # 無人機配置載入器
├── drones/                      # 無人機實作
│   ├── __init__.py
│   ├── base_drone.py            # 基礎無人機類別
│   ├── coordinator_drone.py     # 協調器無人機
│   ├── autopilot_drone.py       # 自動駕駛無人機
│   └── deployment_drone.py      # 部署無人機
├── utils/                       # 工具函數
│   ├── __init__.py
│   └── helpers.py               # 通用輔助函數
└── main.py                      # 主執行入口
```

## 🔗 與核心系統的映射關係

| v1-python-drones           | .devcontainer/automation        | 功能描述           |
|---------------------------|--------------------------------|-------------------|
| `drones/coordinator_drone.py` | `drone-coordinator.py`       | 主協調器           |
| `drones/autopilot_drone.py`   | `auto-pilot.js`             | 自動駕駛 (Python 版) |
| `drones/deployment_drone.py`  | `deployment-drone.sh`        | 部署無人機         |
| `config/drone_config.py`      | `drone-config.yml`          | 配置載入器         |

## 🚀 使用方式

### 直接執行

```bash
# 從專案根目錄
python -m v1_python_drones.main --mode=auto

# 或指定特定無人機
python -m v1_python_drones.main --drone=coordinator
python -m v1_python_drones.main --drone=autopilot
python -m v1_python_drones.main --drone=deployment
```

### 透過自動化入口

```bash
./tools/scripts/automation-entry.sh
# 選擇選項 1: 自動模式
```

### 作為 Python 模組導入

```python
from v1_python_drones.drones import CoordinatorDrone, AutopilotDrone

# 建立協調器
coordinator = CoordinatorDrone()
coordinator.start()

# 啟動自動駕駛
autopilot = AutopilotDrone()
autopilot.execute()
```

## 📋 配置

無人機配置從根目錄的 `drone-config.yml` 載入：

```python
from v1_python_drones.config import DroneConfig

config = DroneConfig.load()
print(config.drone_fleet)
```

## 🔧 開發

### 安裝依賴

```bash
pip install pyyaml
```

### 執行測試

```bash
python -m pytest v1-python-drones/tests/
```

## 📝 版本歷史

- **v1.0.0** - 初始版本，Python 無人機系統
- **v1.1.0** - 整合 .devcontainer/automation 核心系統

## 🔄 遷移至 v2

如需遷移至 v2 多語言島嶼系統，請參考 `/migration` 目錄中的遷移工具。

```bash
./tools/scripts/automation-entry.sh
# 選擇選項 5: 版本遷移
# 選擇 1: v1 → v2
```
