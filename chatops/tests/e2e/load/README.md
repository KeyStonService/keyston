# 負載測試

## 概述

使用 k6 進行負載測試，驗證系統在各種負載條件下的性能表現。

## 測試類型

| 類型 | 目的 | VUs | 時長 |
|------|------|-----|------|
| **Smoke** | 驗證基本功能 | 1-2 | 1 分鐘 |
| **Load** | 驗證正常負載 | 100 | 10 分鐘 |
| **Stress** | 找出系統極限 | 300 | 20 分鐘 |
| **Spike** | 測試突發流量 | 250 | 10 分鐘 |

## 安裝 k6

```bash
# macOS
brew install k6

# Linux (Debian/Ubuntu)
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Docker
docker pull grafana/k6
```

## 運行測試

### 基本命令

```bash
# 冒煙測試
k6 run tests/e2e/load/k6/smoke.js

# 負載測試
k6 run tests/e2e/load/k6/load.js

# 壓力測試
k6 run tests/e2e/load/k6/stress.js

# 峰值測試
k6 run tests/e2e/load/k6/spike.js
```

### 使用環境變量

```bash
# 指定目標 URL
k6 run -e CHATOPS_API_URL=https://api.chatops.example.com tests/e2e/load/k6/load.js

# 指定認證 Token
k6 run -e AUTH_TOKEN=your-token tests/e2e/load/k6/load.js
```

### 輸出結果

```bash
# 輸出 JSON 格式
k6 run --out json=results.json tests/e2e/load/k6/load.js

# 輸出到 InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 tests/e2e/load/k6/load.js

# 輸出到 Cloud (k6 Cloud)
k6 cloud tests/e2e/load/k6/load.js
```

## 性能指標

### 關鍵指標

| 指標 | 說明 | 目標 |
|------|------|------|
| `http_req_duration` | 請求延遲 | p95 < 1s |
| `http_req_failed` | 請求失敗率 | < 1% |
| `http_reqs` | 每秒請求數 | - |
| `vus` | 併發用戶數 | - |

### 自定義指標

```javascript
import { Rate, Trend, Counter } from 'k6/metrics';

const errorRate = new Rate('errors');
const apiLatency = new Trend('api_latency');
const requestsTotal = new Counter('requests_total');
```

## 閾值設置

```javascript
export const options = {
  thresholds: {
    // 95% 請求延遲 < 500ms
    http_req_duration: ['p(95)<500'],

    // 錯誤率 < 1%
    http_req_failed: ['rate<0.01'],

    // 自定義指標
    errors: ['rate<0.05'],
  },
};
```

## CI/CD 整合

### GitHub Actions

```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 0 * * *' # 每天運行
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run Smoke Test
        run: k6 run tests/e2e/load/k6/smoke.js
        env:
          CHATOPS_API_URL: ${{ secrets.STAGING_API_URL }}

      - name: Run Load Test
        run: k6 run tests/e2e/load/k6/load.js
        env:
          CHATOPS_API_URL: ${{ secrets.STAGING_API_URL }}

      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: results/
```

## 結果分析

### Grafana 儀表板

1. 設置 InfluxDB 作為數據源
2. 導入 k6 儀表板 (ID: 2587)
3. 運行測試時輸出到 InfluxDB

### 報告生成

```bash
# 生成 HTML 報告
k6 run --out json=results.json tests/e2e/load/k6/load.js
# 使用第三方工具轉換 JSON 到 HTML
```

## 最佳實踐

1. **隔離測試環境**: 不要在生產環境運行負載測試
2. **漸進增加負載**: 先從冒煙測試開始
3. **監控系統指標**: 同時監控 CPU、內存、數據庫連接等
4. **記錄基線**: 保存正常性能數據作為基線
5. **定期運行**: 在 CI/CD 中定期運行負載測試
