# E2E 測試框架

## 概述

ChatOps 平台端到端測試框架，包含整合測試、合約測試和負載測試。

## 目錄結構

```
tests/e2e/
├── integration/          # 整合測試
│   ├── conftest.py       # pytest 配置
│   ├── test_gateway.py   # Gateway API 測試
│   ├── test_engine.py    # Engine 服務測試
│   └── test_workflows.py # 端到端流程測試
├── contract/             # Pact 合約測試
│   ├── consumer/         # 消費者測試
│   └── provider/         # 提供者驗證
├── load/                 # 負載測試
│   ├── k6/               # k6 腳本
│   └── scenarios/        # 測試場景
└── fixtures/             # 測試數據
```

## 快速開始

### 安裝依賴

```bash
# Python 依賴
pip install -r tests/e2e/requirements.txt

# k6 (負載測試)
brew install k6  # macOS
# or
sudo apt-get install k6  # Linux
```

### 運行測試

```bash
# 整合測試
pytest tests/e2e/integration/ -v

# 合約測試
pytest tests/e2e/contract/ -v

# 負載測試
k6 run tests/e2e/load/k6/smoke.js
```

## 環境配置

### 環境變量

```bash
export CHATOPS_API_URL=http://localhost:8080
export CHATOPS_ENGINE_URL=http://localhost:8000
export DATABASE_URL=postgresql://user:pass@localhost:5432/chatops_test
export REDIS_URL=redis://localhost:6379
```

### Docker Compose 測試環境

```bash
docker-compose -f tests/e2e/docker-compose.test.yml up -d
```

## 測試類型

### 整合測試
- API 端點驗證
- 服務間通信
- 數據庫交互
- 緩存行為

### 合約測試
- API 合約驗證
- 消費者驅動測試
- 提供者驗證

### 負載測試
- 冒煙測試
- 負載測試
- 壓力測試
- 峰值測試
