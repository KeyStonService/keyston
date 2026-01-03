# tests

## 目錄職責

此目錄包含 MachineNativeOps 的**測試套件**，涵蓋單元測試、整合測試、端對端測試和效能基準測試。

## 子目錄說明

| 子目錄 | 職責 | 內容 |
|--------|------|------|
| `unit/` | 單元測試 | test_models, test_services, test_utils |
| `integration/` | 整合測試 | test_api, test_workflows |
| `e2e/` | 端對端測試 | test_system_integration, test_user_journeys |
| `fixtures/` | 測試資料 | mock_data, test_configs |

## 目錄結構

```
tests/
├── unit/                    # 單元測試
│   ├── test_models/        # 模型測試
│   ├── test_services/      # 服務測試
│   └── test_utils/         # 工具函數測試
├── integration/             # 整合測試
│   ├── test_api/           # API 整合測試
│   └── test_workflows/     # 工作流測試
├── e2e/                     # 端對端測試
│   ├── test_system_integration/  # 系統整合
│   └── test_user_journeys/ # 使用者旅程
├── fixtures/                # 測試資料
│   ├── mock_data/          # 模擬資料
│   └── test_configs/       # 測試配置
└── *.py                     # 根目錄測試檔
```

## 根目錄測試檔說明

### test_enterprise_integration.py

- **職責**：企業級整合測試
- **功能**：測試多租戶、資源配額、審計等企業功能的整合

### test_enterprise_orchestrator.py

- **職責**：企業編排器測試
- **功能**：測試 SynergyMesh Orchestrator 的核心功能

### test_performance_benchmarks.py

- **職責**：效能基準測試
- **功能**：測量系統效能指標（TPS、延遲、資源使用）

### test_refactoring_integration.py

- **職責**：重構整合測試
- **功能**：驗證重構後的代碼行為一致性

### test_tool_executor_validation.py

- **職責**：工具執行器驗證
- **功能**：測試工具執行器的正確性和安全性

## 執行測試

```bash
# 執行所有測試
pytest

# 執行單元測試
pytest tests/unit/

# 執行整合測試
pytest tests/integration/

# 執行效能測試
pytest tests/test_performance_benchmarks.py
```

## 職責分離說明

- **unit/**：獨立功能測試，無外部依賴
- **integration/**：模組間協作測試
- **e2e/**：完整流程測試
- **fixtures/**：共享測試資料

## 與其他目錄的關係

- **src/**：被測試的源代碼
- **config/**：測試可能需要的配置
- **.github/workflows/**：CI 中自動執行測試
