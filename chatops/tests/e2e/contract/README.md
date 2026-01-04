# Pact 合約測試

## 概述

使用 Pact 進行消費者驅動的合約測試 (Consumer-Driven Contract Testing)。

## 什麼是合約測試？

合約測試確保服務間的 API 契約保持一致。與傳統的整合測試不同，合約測試：

1. **獨立運行**: 不需要所有服務同時運行
2. **快速反饋**: 在 CI 中快速發現契約破壞
3. **消費者驅動**: 由 API 消費者定義期望

## 目錄結構

```
contract/
├── consumer/                 # 消費者合約測試
│   ├── test_gateway_consumer.py  # Gateway 作為消費者
│   └── conftest.py
├── provider/                 # 提供者驗證測試
│   ├── test_engine_provider.py   # Engine 提供者驗證
│   └── conftest.py
├── pacts/                    # 生成的 Pact 文件
│   └── chatopsgateway-chatopsengine.json
└── README.md
```

## 工作流程

### 1. 消費者定義契約

```python
# consumer/test_gateway_consumer.py
def test_process_message(pact):
    (pact
     .given("Engine is available")
     .upon_receiving("a request to process a message")
     .with_request(method="POST", path="/api/v1/process", ...)
     .will_respond_with(200, body={...}))
```

### 2. 生成 Pact 文件

```bash
pytest tests/e2e/contract/consumer/ -v
# 生成 pacts/chatopsgateway-chatopsengine.json
```

### 3. 提供者驗證

```bash
pytest tests/e2e/contract/provider/ -v
```

### 4. 發布到 Pact Broker

```bash
pact-broker publish ./pacts \
  --consumer-app-version 1.0.0 \
  --broker-base-url http://pact-broker:9292
```

## 運行測試

### 消費者測試

```bash
# 運行所有消費者測試
pytest tests/e2e/contract/consumer/ -v

# 運行特定消費者
pytest tests/e2e/contract/consumer/test_gateway_consumer.py -v
```

### 提供者驗證

```bash
# 確保 Engine 服務運行中
# 運行提供者驗證
pytest tests/e2e/contract/provider/test_engine_provider.py -v
```

## Pact Broker 設置

### 使用 Docker Compose

```yaml
version: '3'
services:
  pact-broker:
    image: pactfoundation/pact-broker:latest
    ports:
      - "9292:9292"
    environment:
      PACT_BROKER_DATABASE_URL: "postgres://pact:pact@postgres/pact"
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: pact
      POSTGRES_PASSWORD: pact
      POSTGRES_DB: pact
```

### CI/CD 整合

```yaml
# .github/workflows/pact.yml
name: Pact Tests

on: [push, pull_request]

jobs:
  consumer-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run consumer tests
        run: pytest tests/e2e/contract/consumer/ -v
      - name: Publish pacts
        if: github.ref == 'refs/heads/main'
        run: |
          pact-broker publish ./pacts \
            --consumer-app-version ${{ github.sha }} \
            --broker-base-url ${{ secrets.PACT_BROKER_URL }}

  provider-verification:
    needs: consumer-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start Engine
        run: docker-compose up -d engine
      - name: Verify pacts
        run: pytest tests/e2e/contract/provider/ -v
```

## 最佳實踐

### 1. 保持合約簡潔
只測試你實際使用的字段，使用 `Like()` 匹配類型而非具體值。

### 2. 有意義的 Provider States
使用描述性的 provider state 名稱，如 "a user with ID 123 exists"。

### 3. 版本管理
使用語義化版本和 Git SHA 標記 pact 版本。

### 4. Can-I-Deploy
在部署前使用 `pact-broker can-i-deploy` 檢查兼容性：

```bash
pact-broker can-i-deploy \
  --pacticipant ChatOpsGateway \
  --version 1.0.0 \
  --to production
```

## 故障排除

### 常見問題

**Pact 驗證失敗**
- 檢查 provider state 設置是否正確
- 確認 provider URL 正確
- 查看詳細日誌確定不匹配的字段

**Broker 連接失敗**
- 確認 Broker URL 正確
- 檢查認證憑證
- 驗證網絡連通性
