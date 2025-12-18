# Observability Model / 觀測模型

## 三合一模型

- **Logs**：結構化 JSON，集中在 Elasticsearch；每筆包含 trace/span IDs。
- **Metrics**：Prometheus scraping，支援 RED + USE 指標。
- **Traces**：OpenTelemetry，串接 core/contract_service 與 automation/stack。

## 設計原則

1. **Domain-Centric Dashboards**：以 system-module-map 分組。
2. **SLO 先行**：設定目標 → 指標 → 警報。
3. **可重播**：保留 30 天事件以供 RCA。

## 實施步驟

- 定義信號 → 配置 exporters → 建置 dashboards/ → 連接 rca-playbook。
