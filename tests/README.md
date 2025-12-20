# Tests

MachineNativeOps 測試套件，確保代碼質量和功能正確性。

## 測試架構

```
tests/
├── unit/         # 單元測試（快速、獨立）
├── integration/  # 整合測試（模組協作）
├── e2e/          # 端對端測試（完整流程）
└── fixtures/     # 測試資料與配置
```

## 快速開始

```bash
# 安裝測試依賴
pip install -r requirements-dev.txt

# 執行所有測試
pytest

# 執行特定類型測試
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# 帶覆蓋率報告
pytest --cov=src --cov-report=html
```

## 測試類型

### 單元測試 (unit/)

獨立功能的快速測試：

| 目錄 | 測試對象 |
|------|----------|
| test_models/ | 資料模型 |
| test_services/ | 服務邏輯 |
| test_utils/ | 工具函數 |

### 整合測試 (integration/)

模組間協作測試：

| 目錄 | 測試對象 |
|------|----------|
| test_api/ | API 端點 |
| test_workflows/ | 工作流程 |

### 端對端測試 (e2e/)

完整使用者流程：

| 目錄 | 測試對象 |
|------|----------|
| test_system_integration/ | 系統整合 |
| test_user_journeys/ | 使用者旅程 |

## 根目錄測試

| 測試檔 | 說明 |
|--------|------|
| test_enterprise_integration.py | 企業功能整合 |
| test_enterprise_orchestrator.py | 編排器核心功能 |
| test_performance_benchmarks.py | 效能基準測試 |
| test_refactoring_integration.py | 重構驗證 |
| test_tool_executor_validation.py | 工具執行器驗證 |

## 測試資料 (fixtures/)

- `mock_data/` - 模擬資料
- `test_configs/` - 測試用配置

## 相關資源

- [DIRECTORY.md](./DIRECTORY.md) - 詳細目錄說明
- [src/](../src/) - 被測試的源代碼
