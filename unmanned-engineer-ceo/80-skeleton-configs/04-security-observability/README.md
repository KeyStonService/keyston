# 骨架 4: Security & Observability (安全與可觀測性)

**目的**: 建立企業級安全和可觀測性基礎設施，確保系統的安全性、合規性和可監測性。

## 📋 概述

安全與可觀測性骨架提供了完整的安全、身份、授權、審計和監測解決方案，涵蓋認證、RBAC、日誌、指標和分散式追蹤。

### 核心能力

- **認證 (Authentication)**: OAuth 2.0, API Keys, Service Accounts
- **授權 (Authorization)**: RBAC (Role-Based) 和 ABAC (Attribute-Based)
- **審計 (Audit)**: 完整的事件日誌和變更追蹤
- **可觀測性**: 日誌、指標、追蹤 (Logs, Metrics, Traces)

## 📁 文件結構

### 文檔 (docs/)

#### security-model.md - 安全模型

定義完整的安全策略，包括:

- **認證機制**
  - OAuth 2.0 Authorization Code Flow (with PKCE)
  - API Keys (Hash with bcrypt)
  - Service Account (JWT with RS256)
  - Token 管理 (生命週期、輪換、撤銷)

- **授權機制**
  - RBAC: 超級管理員、租戶管理員、專案管理員、開發者、檢視者
  - ABAC: 租戶隔離、專案成員檢查

- **審計**
  - 必審計操作: CREATE、UPDATE、DELETE、權限變更、敏感資料存取、認證失敗
  - 審計日誌格式 (JSON，包含時間戳、事件類型、行為者、資源、變更)

#### observability-standards.md - 可觀測性標準

三支柱的可觀測性實踐:

- **日誌 (Logs)**
  - 結構化 JSON 日誌格式
  - 日誌級別: debug, info, warn, error, fatal
  - 敏感資訊過濾 (密碼、Token、PII 遮罩)

- **指標 (Metrics)**
  - RED Metrics: Request Rate, Error Rate, Duration
  - USE Metrics: Utilization, Saturation, Errors
  - 業務指標: Orders, Revenue 等

- **追蹤 (Traces)**
  - Span 命名規範: `<operation_type>.<resource>.<action>`
  - 必須的 Span 屬性
  - 取樣策略: 默認 10%，錯誤 100%，健康檢查 1%

### 配置 (config/)

#### rbac-policies.yaml - RBAC 策略配置

- 5 個內建角色定義 (super_admin, tenant_admin, project_admin, developer, viewer)
- 權限定義 (租戶、專案、部署、Agent、知識庫、帳務)
- 角色分配權限矩陣

#### log-schema.json - 日誌 JSON Schema

- 標準化日誌格式定義
- 必要字段: timestamp, level, service, message
- 可選字段: trace_id, span_id, context, error, http, performance
- 敏感資訊驗證

#### trace-config.yaml - 追蹤配置

- OpenTelemetry (OTEL) 導出器配置
- 資源屬性定義
- 取樣策略規則
- Span 處理器配置
- 屬性過濾和遮罩
- Instrumentation (HTTP、Database、gRPC、Redis、MQ)

### 工具 (tools/)

#### security-scan.ts - 安全掃描工具

自動掃描代碼中的安全問題:

- 硬編碼密碼檢測
- SQL 注入風險
- 代碼注入 (eval 使用)
- 弱隨機性
- 缺失輸入驗證
- 敏感資訊日誌外洩

使用 CLI:

```bash
npx ts-node tools/security-scan.ts [patterns]
npx ts-node tools/security-scan.ts '**/*.ts' '**/*.js'
```

#### log-validator.ts - 日誌驗證工具

驗證日誌是否符合標準 schema:

- JSON Schema 驗證
- 敏感資訊檢測
- 格式驗證報告

使用 CLI:

```bash
npx ts-node tools/log-validator.ts [schema-path] <log-file>
npx ts-node tools/log-validator.ts ./config/log-schema.json app.log
```

## 🚀 使用方式

### 1. 應用 RBAC 策略

```yaml
# 在部署時應用角色配置
kubectl apply -f config/rbac-policies.yaml
```

### 2. 配置日誌管道

```typescript
import * as fs from 'fs';
import Ajv from 'ajv';

const schema = JSON.parse(fs.readFileSync('./config/log-schema.json', 'utf8'));
const ajv = new Ajv();

const log = {
  timestamp: new Date().toISOString(),
  level: 'info',
  service: 'billing-api',
  message: 'Order processed',
  trace_id: 'abc123def456',
};

const valid = ajv.validate(schema, log);
if (!valid) {
  console.error('Log validation failed:', ajv.errors);
}
```

### 3. 配置分散式追蹤

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';

const traceExporter = new OTLPTraceExporter({
  url: 'http://otel-collector:4317',
});

const sdk = new NodeSDK({
  traceExporter,
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
```

### 4. 運行安全掃描

```bash
# 在 CI/CD 中運行
npm run security:scan

# 檢查關鍵問題
npx ts-node tools/security-scan.ts '**/*.ts' '**/*.js'
```

## 📊 日誌流向

```
┌──────────────────────┐
│  Application Logs    │
│  (Structured JSON)   │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│   Log Collection     │
│  (Fluentd/Logstash)  │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  Log Aggregation     │
│  (Elasticsearch)     │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│  Visualization       │
│  (Kibana/Grafana)    │
└──────────────────────┘
```

## 🔐 安全檢查清單

在部署前，請確保:

- [ ] 所有外部端點已啟用認證
- [ ] RBAC 角色已根據需求定義
- [ ] 審計日誌已正確配置
- [ ] 敏感資訊已從日誌中過濾
- [ ] 定期運行安全掃描
- [ ] Token 輪換策略已啟用
- [ ] API Keys 已使用 bcrypt 加密存儲

## 📈 可觀測性檢查清單

- [ ] 所有服務已配置結構化日誌
- [ ] RED Metrics 已集成 (Request Rate, Error, Duration)
- [ ] 分散式追蹤已啟用
- [ ] 取樣策略已根據流量調整
- [ ] 儀表板已設置
- [ ] 告警規則已定義

## 🔗 相關文檔

- [安全模型](./docs/security-model.md)
- [可觀測性標準](./docs/observability-standards.md)
- [RBAC 策略配置](./config/rbac-policies.yaml)
- [日誌 Schema](./config/log-schema.json)
- [追蹤配置](./config/trace-config.yaml)

## 📖 依賴項

- OpenTelemetry (OTEL)
- Prometheus (指標收集)
- Elasticsearch (日誌存儲)
- Grafana / Kibana (可視化)
- OPA/Conftest (策略執行)

## 🔗 引用

- **系統**: Unmanned Island System (SynergyMesh)
- **版本**: 1.0.0
- **最後更新**: 2024-12-05
