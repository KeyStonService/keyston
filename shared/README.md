# shared

共享資源目錄 - SynergyMesh v1 和 v2 共用的配置、工具和常數

此目錄包含在 v1-python-drones 和 v2-multi-islands 之間共享的資源。

## 🔗 目錄結構

```
shared/
├── README.md               # 本文檔
├── __init__.py             # Python 套件初始化
├── config/                 # 共享配置
│   ├── __init__.py
│   └── base_config.py      # 基礎配置類別
├── utils/                  # 共享工具
│   ├── __init__.py
│   └── common_helpers.py   # 通用輔助函數
└── constants/              # 共享常數
    ├── __init__.py
    └── system_constants.py # 系統常數
```

## 🔄 與版本系統的映射關係

| 共享資源                        | v1-python-drones         | v2-multi-islands          |
| ------------------------------- | ------------------------ | ------------------------- |
| `config/base_config.py`         | `config/drone_config.py` | `config/island_config.py` |
| `utils/common_helpers.py`       | `utils/helpers.py`       | `utils/helpers.py`        |
| `constants/system_constants.py` | 內建常數                 | 內建常數                  |

## 📝 使用方式

### 在 v1-python-drones 中使用

```python
from shared.config import BaseConfig
from shared.utils import print_banner, get_project_root
from shared.constants import VERSION, SUPPORTED_MODES
```

### 在 v2-multi-islands 中使用

```python
from shared.config import BaseConfig
from shared.utils import print_banner, get_project_root
from shared.constants import ISLAND_TYPES, BRIDGE_PROTOCOLS
```

## 🎯 設計原則

1. **DRY (Don't Repeat Yourself)**: 避免在 v1 和 v2 中重複相同的代碼
2. **向後兼容**: 新增功能不破壞現有 API
3. **版本無關**: 共享資源不依賴特定版本的實作細節
