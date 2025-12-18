# 可观测性验证 (Observability Validation)

> **治理模块**: 可观测性与监控 (Observability and Monitoring)
> **版本**: v1.0.0
> **状态**: 已批准 (Approved)
> **最后更新**: 2025-01-15

## 概述

可观测性验证确保所有系统和服务都具备充分的监控、日志和追踪能力。通过标准化的可观测性要求和自动化验证，我们实现问题的快速发现和定位。

## 目标

- 👀 **全面可见**: 所有关键服务都有完善的监控
- 🚨 **主动告警**: 问题出现时立即发现
- 🔍 **快速定位**: 通过日志和追踪快速找到根因
- 📊 **标准化**: 统一的监控和日志格式
- ✅ **可验证**: 自动验证可观测性要求

## 可观测性三大支柱

### 1. 指标 (Metrics)

**定义**: 数值型的时间序列数据，用于追踪系统状态和性能

#### 必需指标

所有服务必须导出以下指标：

```yaml
# RED 方法 (Request-based services)
必需指标:
  - http_requests_total: 请求总数
    labels: [method, path, status_code]
    type: counter

  - http_request_duration_seconds: 请求延迟
    labels: [method, path]
    type: histogram

  - http_requests_in_flight: 当前处理中的请求
    type: gauge

# USE 方法 (Resource-based services)
必需指标:
  - system_cpu_usage: CPU 使用率
    type: gauge

  - system_memory_usage_bytes: 内存使用量
    type: gauge

  - system_disk_io_bytes: 磁盘 I/O
    labels: [device, direction]
    type: counter

# 业务指标（示例）
推荐指标:
  - business_transactions_total: 业务交易总数
    labels: [type, status]
    type: counter

  - business_revenue_total: 收入总额
    labels: [product, currency]
    type: counter
```

#### Prometheus 集成

**服务配置**:

```yaml
# Kubernetes Service
apiVersion: v1
kind: Service
metadata:
  name: prod-payment-api-svc-v1.3.0
  annotations:
    prometheus.io/scrape: "true"     # 启用抓取
    prometheus.io/port: "8080"        # 指标端口
    prometheus.io/path: "/metrics"    # 指标路径
spec:
  selector:
    app: payment-api
  ports:
    - name: http
      port: 80
      targetPort: 8080
    - name: metrics
      port: 8080
      targetPort: 8080
```

**Prometheus 配置**:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'kubernetes-services'
    kubernetes_sd_configs:
      - role: service
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

#### 指标验证

```bash
# 验证服务是否导出指标
curl http://service:8080/metrics

# 检查必需指标是否存在
python tools/governance/python/validate_metrics.py \
  --service payment-api \
  --endpoint http://service:8080/metrics \
  --required-metrics config/required-metrics.yaml
```

### 2. 日志 (Logging)

**定义**: 结构化的事件记录，用于审计和故障排查

#### 日志标准

**结构化日志格式（JSON）**:

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "payment-api",
  "message": "Payment processed successfully",
  "context": {
    "environment": "production",
    "service": "payment-api",
    "version": "v1.3.0",
    "namespace": "production",
    "pod": "prod-payment-api-deploy-v1.3.0-abc123",
    "node": "node-01",
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "span_id": "00f067aa0ba902b7"
  },
  "fields": {
    "transaction_id": "TXN-2025-001234",
    "user_id": "user-12345",
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "credit_card",
    "duration_ms": 245
  }
}
```

**必需字段**:

```yaml
基础字段（所有日志）:
  - timestamp: ISO 8601 格式
  - level: DEBUG | INFO | WARN | ERROR | FATAL
  - logger: 日志记录器名称
  - message: 人类可读的消息

上下文字段（所有日志）:
  - environment: 环境标识
  - service: 服务名称
  - version: 服务版本
  - namespace: Kubernetes 命名空间
  - pod: Pod 名称（如果在 K8s 中）

追踪字段（推荐）:
  - trace_id: 分布式追踪 ID
  - span_id: Span ID
  - parent_span_id: 父 Span ID（如果有）

业务字段（按需）:
  - 特定于业务逻辑的字段
```

#### 日志级别使用指南

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| **DEBUG** | 详细的调试信息 | "Entering function X with params Y" |
| **INFO** | 正常的业务流程 | "Payment processed successfully" |
| **WARN** | 警告，但不影响功能 | "Retry attempt 2/3" |
| **ERROR** | 错误，需要处理 | "Payment gateway timeout" |
| **FATAL** | 严重错误，服务终止 | "Database connection failed, shutting down" |

#### 日志聚合

**ELK Stack 集成**:

```yaml
# Filebeat 配置
filebeat.inputs:
  - type: container
    paths:
      - /var/log/containers/*.log
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
          - logs_path:
              logs_path: "/var/log/containers/"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "logs-%{[environment]}-%{+yyyy.MM.dd}"

# 日志保留策略
setup.ilm.policy:
  phases:
    hot:
      actions:
        rollover:
          max_size: "50GB"
          max_age: "1d"
    delete:
      min_age: "30d"
      actions:
        delete: {}
```

**查询示例**:

```bash
# Elasticsearch 查询
curl -X GET "elasticsearch:9200/logs-production-*/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "context.service": "payment-api" } },
        { "match": { "level": "ERROR" } },
        { "range": { "timestamp": { "gte": "now-1h" } } }
      ]
    }
  }
}
'
```

#### 日志验证

```bash
# 验证日志格式
python tools/governance/python/validate_logs.py \
  --service payment-api \
  --sample-size 100 \
  --check-structure \
  --check-required-fields

# CI/CD 中验证
- name: Validate Log Format
  run: |
    # 启动服务
    docker run -d --name test-service my-service:latest

    # 等待日志产生
    sleep 5

    # 验证日志格式
    docker logs test-service | \
      python tools/governance/python/validate_logs.py --stdin
```

### 3. 追踪 (Tracing)

**定义**: 分布式请求追踪，用于理解跨服务调用链

#### OpenTelemetry 集成

**服务配置**:

```yaml
# Python 示例
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# 初始化追踪
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# 配置导出器
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317")
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

# 自动 instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# 手动创建 span
@app.post("/payment")
async def process_payment(payment: Payment):
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("payment.amount", payment.amount)
        span.set_attribute("payment.method", payment.method)

        # 业务逻辑
        result = await payment_service.process(payment)

        span.set_attribute("payment.status", result.status)
        return result
```

**追踪必需属性**:

```yaml
Span 属性:
  系统属性:
    - service.name: 服务名称
    - service.version: 服务版本
    - service.namespace: 命名空间
    - deployment.environment: 环境

  HTTP 请求:
    - http.method: HTTP 方法
    - http.url: 完整 URL
    - http.status_code: 状态码
    - http.user_agent: User Agent

  数据库操作:
    - db.system: 数据库类型 (postgresql, mongodb, etc.)
    - db.operation: 操作类型 (SELECT, INSERT, etc.)
    - db.statement: SQL 语句（脱敏）

  业务操作:
    - 业务相关的关键属性
    - 用户 ID、交易 ID 等
```

#### Jaeger/Tempo 集成

```yaml
# OpenTelemetry Collector 配置
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger]
```

## 健康检查

### 必需健康检查端点

所有服务必须实现以下端点：

```yaml
# /health - 存活检查 (Liveness Probe)
GET /health
Response:
  200 OK: 服务存活
  503 Service Unavailable: 服务无法响应

用途: Kubernetes 使用此端点判断是否重启 Pod

# /ready - 就绪检查 (Readiness Probe)
GET /ready
Response:
  200 OK: 服务就绪，可接收流量
  503 Service Unavailable: 服务未就绪

用途: Kubernetes 使用此端点判断是否加入负载均衡

# /health/详细 - 详细健康信息
GET /health/detailed
Response:
  {
    "status": "healthy",
    "checks": {
      "database": {
        "status": "healthy",
        "latency_ms": 5
      },
      "cache": {
        "status": "healthy",
        "latency_ms": 1
      },
      "external_api": {
        "status": "degraded",
        "latency_ms": 500,
        "message": "Slow response"
      }
    },
    "uptime_seconds": 86400,
    "version": "v1.3.0"
  }
```

### Kubernetes 配置

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: payment-api
        image: payment-api:v1.3.0

        # 存活探针
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        # 就绪探针
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3

        # 启动探针（可选，用于慢启动服务）
        startupProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 0
          periodSeconds: 5
          failureThreshold: 30  # 最多等待 150 秒
```

## 告警规则

### 服务级别告警

```yaml
# templates/governance/k8s/prometheus-rule-service-alert.template.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: service-observability-alerts
spec:
  groups:
  - name: service.availability
    interval: 30s
    rules:
      # 服务不可用
      - alert: ServiceDown
        expr: up{job="kubernetes-services"} == 0
        for: 1m
        labels:
          severity: critical
          category: availability
        annotations:
          summary: "服务 {{ $labels.service }} 不可用"
          description: "服务已停止响应超过 1 分钟"

      # 高错误率
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (service) /
            sum(rate(http_requests_total[5m])) by (service)
          ) > 0.05
        for: 5m
        labels:
          severity: warning
          category: errors
        annotations:
          summary: "服务 {{ $labels.service }} 错误率高"
          description: "5xx 错误率为 {{ $value | humanizePercentage }}"

      # 高延迟
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (service, le)
          ) > 1
        for: 10m
        labels:
          severity: warning
          category: performance
        annotations:
          summary: "服务 {{ $labels.service }} 延迟高"
          description: "P95 延迟为 {{ $value }}秒"

  - name: service.observability
    interval: 5m
    rules:
      # 缺少指标
      - alert: MissingMetrics
        expr: |
          absent(http_requests_total{service="payment-api"})
        for: 5m
        labels:
          severity: warning
          category: observability
        annotations:
          summary: "服务 payment-api 缺少指标"
          description: "无法获取 http_requests_total 指标"

      # 缺少日志
      - alert: MissingLogs
        expr: |
          absent(log_entries_total{service="payment-api"})
        for: 10m
        labels:
          severity: warning
          category: observability
        annotations:
          summary: "服务 payment-api 缺少日志"
          description: "10 分钟内未收到任何日志"
```

## 验证清单

### 新服务上线前

```yaml
可观测性验证清单:
  指标:
    - [ ] 导出 /metrics 端点
    - [ ] 包含所有必需指标（RED/USE）
    - [ ] Prometheus 能够抓取指标
    - [ ] 在 Grafana 中可见
    - [ ] 配置基础告警规则

  日志:
    - [ ] 使用结构化日志（JSON）
    - [ ] 包含所有必需字段
    - [ ] 日志发送到集中式日志系统
    - [ ] 在 Kibana/Grafana 中可查询
    - [ ] 日志级别设置合理

  追踪:
    - [ ] 集成 OpenTelemetry
    - [ ] 自动 instrument 框架
    - [ ] 手动 instrument 关键业务逻辑
    - [ ] 追踪数据发送到 Jaeger/Tempo
    - [ ] 在追踪 UI 中可见

  健康检查:
    - [ ] 实现 /health 端点
    - [ ] 实现 /ready 端点
    - [ ] 配置 Kubernetes 探针
    - [ ] 健康检查包含依赖检查

  文档:
    - [ ] 记录关键指标和含义
    - [ ] 记录告警规则和阈值
    - [ ] 记录日志格式和字段
    - [ ] 提供 troubleshooting 指南

  验证:
    - [ ] 运行自动化验证工具
    - [ ] 在测试环境验证端到端
    - [ ] SRE 团队审查
```

### 自动化验证

```bash
# CI/CD 中运行可观测性验证
python tools/governance/python/validate_observability.py \
  --service payment-api \
  --environment staging \
  --config config/observability-requirements.yaml

# 验证内容:
# - 指标端点可访问
# - 必需指标存在
# - 日志格式正确
# - 健康检查端点可用
# - Prometheus 抓取配置正确
```

## 仪表板模板

### Grafana 服务仪表板

标准服务仪表板包含以下面板：

```yaml
仪表板结构:
  行1 - 总览:
    - 服务状态（存活/就绪）
    - 请求速率（RPS）
    - 错误率
    - P50/P95/P99 延迟

  行2 - 请求详情:
    - 按路径分组的请求量
    - 按状态码分组的请求
    - 请求延迟热力图

  行3 - 系统资源:
    - CPU 使用率
    - 内存使用量
    - 网络 I/O
    - 磁盘 I/O

  行4 - 业务指标:
    - 业务交易量
    - 业务成功率
    - 自定义业务指标

  行5 - 依赖:
    - 数据库连接池
    - 缓存命中率
    - 外部 API 调用延迟
```

**导入仪表板**:

```bash
# 使用模板创建服务仪表板
python tools/governance/python/generate_dashboard.py \
  --service payment-api \
  --template templates/governance/monitoring/grafana-dashboard-service.json \
  --output dashboards/payment-api-dashboard.json

# 导入到 Grafana
curl -X POST \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @dashboards/payment-api-dashboard.json \
  http://grafana:3000/api/dashboards/db
```

## SLI/SLO 定义

### Service Level Indicators (SLIs)

```yaml
# Payment API SLIs
slis:
  availability:
    description: "服务可用性"
    query: |
      sum(rate(http_requests_total{job="payment-api"}[5m])) -
      sum(rate(http_requests_total{job="payment-api",status_code=~"5.."}[5m]))
      /
      sum(rate(http_requests_total{job="payment-api"}[5m]))
    unit: "%"

  latency:
    description: "请求延迟 P95"
    query: |
      histogram_quantile(0.95,
        sum(rate(http_request_duration_seconds_bucket{job="payment-api"}[5m])) by (le)
      )
    unit: "seconds"

  error_rate:
    description: "错误率"
    query: |
      sum(rate(http_requests_total{job="payment-api",status_code=~"5.."}[5m])) /
      sum(rate(http_requests_total{job="payment-api"}[5m]))
    unit: "%"
```

### Service Level Objectives (SLOs)

```yaml
# Payment API SLOs
slos:
  availability:
    target: 99.9%
    description: "99.9% 的请求成功（非 5xx）"
    time_window: "30d"

  latency:
    target: 500ms
    percentile: 95
    description: "95% 的请求在 500ms 内完成"
    time_window: "30d"

  error_rate:
    target: 0.1%
    description: "错误率低于 0.1%"
    time_window: "30d"
```

### Error Budget

```yaml
# 30 天错误预算
error_budget:
  availability:
    slo: 99.9%
    allowed_downtime: 43.2m  # (1 - 0.999) * 30d
    current_downtime: 15m
    remaining: 28.2m
    burn_rate: 0.35  # 当前消耗速度

告警:
  - alert: ErrorBudgetBurnRateHigh
    expr: slo_burn_rate{slo="availability"} > 1.0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "错误预算消耗速度过快"
      description: "按当前速度，错误预算将在 {{ $value }}天内耗尽"
```

## 最佳实践

### ✅ DO

1. **使用结构化日志**: JSON 格式，便于解析和查询
2. **添加追踪 ID**: 关联分布式请求
3. **合理的日志级别**: 避免过度或不足
4. **监控业务指标**: 不只是技术指标
5. **设置告警**: 主动发现问题
6. **定期审查**: 检查仪表板和告警是否有效
7. **文档化**: 记录指标含义和告警处理

### ❌ DON'T

1. **避免过度日志**: 不要记录所有内容
2. **避免敏感信息**: 不要记录密码、token 等
3. **避免同步调用**: 日志和追踪应异步发送
4. **避免硬编码**: 使用配置管理日志级别
5. **避免告警疲劳**: 只告警真正需要人工处理的问题

## 工具和资源

### 验证工具

- `tools/governance/python/validate_observability.py` - 可观测性验证
- `tools/governance/python/validate_metrics.py` - 指标验证
- `tools/governance/python/validate_logs.py` - 日志验证

### 模板

- `templates/governance/monitoring/grafana-dashboard-service.json` - 服务仪表板模板
- `templates/governance/k8s/prometheus-rule-service-alert.template.yaml` - 告警规则模板

### 示例

- `examples/governance/observability/prometheus-rules.yaml` - Prometheus 规则示例

## 参考资料

### 外部标准

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Google SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [The Twelve-Factor App - Logs](https://12factor.net/logs)
- [Semantic Conventions for Spans](https://github.com/open-telemetry/opentelemetry-specification/tree/main/specification/trace/semantic_conventions)

### 内部资源

- `docs/governance/06-metrics-and-audit.md` - 指标和审计
- `governance-manifest.yaml` - 治理框架总览

## FAQ

### Q: 所有日志都必须是 JSON 格式吗？

A: 是的。结构化日志便于解析、查询和分析。大多数日志库都支持 JSON 输出。

### Q: 追踪会影响性能吗？

A: 影响很小。OpenTelemetry 使用异步导出，典型开销 < 5%。可以配置采样率进一步降低开销。

### Q: 如何处理敏感信息？

A: 使用脱敏（masking）处理敏感字段。例如，只记录信用卡号后 4 位。

### Q: 健康检查应该包含哪些依赖？

A: 包含关键依赖（数据库、缓存），但要避免级联故障。使用超时和断路器保护。

### Q: SLO 应该设置多高？

A: 基于业务需求和实际能力。99.9% 是常见起点。过高的 SLO 会增加成本。

## 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0.0 | 2025-01-15 | 初始版本，定义可观测性标准 | Governance Team |

---

**下一步**: 阅读 [09-security-compliance.md](./09-security-compliance.md) 了解安全合规要求。
