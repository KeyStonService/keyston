# 版本遷移工具

此目錄包含 SynergyMesh v1-python-drones 和 v2-multi-islands 之間的版本遷移工具。

## 🔄 支援的遷移路徑

| 遷移方向 | 說明 | 狀態 |
|---------|------|------|
| v1 → v2 | Python 無人機 → 多語言島嶼 | ✅ 支援 |
| v2 → v1 | 多語言島嶼 → Python 無人機 (降級) | ✅ 支援 |

## 📁 目錄結構

```
migration/
├── README.md               # 本文檔
├── __init__.py             # Python 套件初始化
├── migrator.py             # 遷移核心邏輯
├── scripts/                # 遷移腳本
│   ├── v1_to_v2.py         # v1 → v2 遷移腳本
│   └── v2_to_v1.py         # v2 → v1 降級腳本
└── templates/              # 遷移模板
    └── migration_report.md # 遷移報告模板
```

## 🚀 使用方式

### 透過 automation-entry.sh

```bash
./tools/scripts/automation-entry.sh
# 選擇選項 5: 版本遷移 (v1 ↔ v2)
```

### 直接執行遷移腳本

```bash
# v1 → v2 遷移
python3 migration/scripts/v1_to_v2.py

# v2 → v1 遷移 (降級)
python3 migration/scripts/v2_to_v1.py

# 使用遷移器類別
python3 -m migration.migrator --direction=v1-to-v2
python3 -m migration.migrator --direction=v2-to-v1
```

### 作為 Python 模組使用

```python
from migration import Migrator

# 建立遷移器
migrator = Migrator()

# 檢查遷移前狀態
migrator.pre_check()

# 執行 v1 → v2 遷移
result = migrator.migrate_v1_to_v2()

# 執行 v2 → v1 降級
result = migrator.migrate_v2_to_v1()
```

## 🗺️ 遷移映射表

### v1-python-drones → v2-multi-islands

| v1 組件 | v2 組件 | 說明 |
|--------|--------|------|
| `drones/coordinator_drone.py` | `orchestrator/island_orchestrator.py` | 協調器 |
| `drones/autopilot_drone.py` | `islands/python_island.py` | Python 功能 |
| `drones/deployment_drone.py` | `islands/*.py` | 部署功能分散到各島嶼 |
| `config/drone_config.py` | `config/island_config.py` | 配置載入 |
| `utils/helpers.py` | `utils/helpers.py` | 工具函數 |

## ⚠️ 注意事項

1. **備份**: 遷移前會自動建立備份至 `migration/backups/` 目錄
2. **版本控制**: 請確保所有變更已提交至 Git
3. **測試環境**: 生產環境遷移前請先在測試環境驗證
4. **配置遷移**: 配置檔案會自動轉換，但自訂配置需手動檢查

## 📝 遷移報告

遷移完成後會生成報告至 `migration/reports/` 目錄，包含：

- 遷移的檔案清單
- 配置變更摘要
- 需要手動處理的項目
- 驗證結果
