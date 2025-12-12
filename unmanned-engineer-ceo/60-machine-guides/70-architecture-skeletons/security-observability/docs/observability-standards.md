# Observability Standards

## 日誌 (Logs)

### 結構化日誌格式

使用 JSON 格式，必須包含以下欄位:

```json
{
  "timestamp": "2024-12-04T10:30:00.123Z",
  "level": "info",
  "service": "billing-api",
  "trace_id": "abc123def456",
  "span_id": "789ghi012jkl",
  "message": "Order processed successfully",
  "context": {
    "order_id": "ord_12345",
    "user_id": "usr_67890",
    "amount": 99.99
  }
}
```

### 日誌級別

- **debug**: 開發除錯資訊
- **info**: 一般資訊事件
- **warn**: 警告但不影響功能
- **error**: 錯誤需要處理
- **fatal**: 嚴重錯誤導致服務停止

### 敏感資訊處理

禁止記錄以下內容:

- 密碼、Token
- 信用卡號、CVV
- 完整的電子郵件 (可記錄 hash 或遮罩)

## 指標 (Metrics)

### 必須的指標

#### 1. RED Metrics (服務健康)

```yaml
metrics:
  - name: request_rate
    type: counter
    labels: [service, endpoint, method]

  - name: request_duration_seconds
    type: histogram
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]
    labels: [service, endpoint, method]

  - name: request_errors_total
    type: counter
    labels: [service, endpoint, method, error_type]
```

#### 2. USE Metrics (資源利用)

```yaml
metrics:
  - name: cpu_usage_percent
    type: gauge
    labels: [service, instance]

  - name: memory_usage_bytes
    type: gauge
    labels: [service, instance]

  - name: disk_io_operations_total
    type: counter
    labels: [service, instance, operation]
```

#### 3. 業務指標

```yaml
metrics:
  - name: orders_total
    type: counter
    labels: [service, status]

  - name: revenue_total
    type: counter
    labels: [service, currency]
```

## 追蹤 (Traces)

### Span 命名規範

```
<operation_type>.<resource>.<action>

範例:
- http.server.request
- db.query.select
- queue.publish.message
- llm.completion.generate
```

### 必須的 Span 屬性

```yaml
attributes:
  - http.method
  - http.url
  - http.status_code
  - service.name
  - service.version
  - tenant.id
  - user.id (if applicable)
```

### 取樣策略

```yaml
sampling:
  default_rate: 0.1 # 10% 取樣

  rules:
    - condition: http.status_code >= 500
      rate: 1.0 # 錯誤全部追蹤

    - condition: http.url.path == "/health"
      rate: 0.01 # 健康檢查低取樣
```
