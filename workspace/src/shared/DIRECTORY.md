# shared

## 目錄職責

此目錄為 MachineNativeOps 的**共享資源層**，包含 SynergyMesh v1 和 v2 共用的配置、工具、常數和類型定義。作為系統的基礎設施層，它被所有其他模組依賴。

## 子目錄說明

| 子目錄 | 職責 |
|--------|------|
| `config/` | 共享配置 - 基礎配置類別 |
| `constants/` | 共享常數 - 系統常數定義 |
| `types/` | 共享類型 - TypeScript/Python 類型定義 |
| `utils/` | 共享工具 - 通用輔助函數 |

## 根目錄檔案說明

### **init**.py

- **職責**：Python 套件初始化
- **功能**：模組導出定義

### language_bridges.py

- **職責**：語言橋接
- **功能**：跨語言調用的橋接實現

### schema.ts

- **職責**：TypeScript Schema 定義
- **功能**：共用的資料結構 Schema

## 版本系統映射

| 共享資源 | v1-python-drones | v2-multi-islands |
|---------|------------------|------------------|
| `config/base_config.py` | `config/drone_config.py` | `config/island_config.py` |
| `utils/common_helpers.py` | `utils/helpers.py` | `utils/helpers.py` |
| `constants/system_constants.py` | 內建常數 | 內建常數 |

## 使用方式

```python
from shared.config import BaseConfig
from shared.utils import print_banner, get_project_root
from shared.constants import VERSION, SUPPORTED_MODES
```

## 設計原則

1. **DRY (Don't Repeat Yourself)**：避免在 v1 和 v2 中重複相同的代碼
2. **向後兼容**：新增功能不破壞現有 API
3. **版本無關**：共享資源不依賴特定版本的實作細節
4. **最小依賴**：盡量減少對其他模組的依賴

## 依賴規則

**可以依賴**：

- 標準庫（Python、Node.js）
- 第三方基礎庫

**不可依賴**：

- `src/core/` - 共享層是基礎層，不應反向依賴核心
- `src/services/` - 共享層不應依賴服務層
- `src/automation/` - 共享層不應依賴自動化層

## 與其他目錄的關係

- **所有 src/ 子目錄**：可被所有模組導入使用
- **config/**：共享配置補充 config/ 的配置
- **tests/**：對應的測試代碼
