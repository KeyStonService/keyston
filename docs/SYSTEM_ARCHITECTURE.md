# 系統架構總覽

## 三大子系統

1. **AI Agents Ecosystem**
   - 7 類專業 Agent
   - 決策與協作匯流排
   - MCP/CLI 介面
2. **Governance Framework**
   - Schema 命名空間
   - 十階段管道
   - SLSA Provenance
3. **Autonomous Systems**
   - 五骨架架構
   - 無人機/自駕整合
   - 安全監控

## 分層結構

- 表層：island-cli、Web 控制台、API
- 中層：Agent Runtime、Knowledge Engine、Workflow Orchestrator
- 底層：Rust/Go 服務網格、觀測與治理底座

## 技術選型

| 層級     | 技術                                   |
| -------- | -------------------------------------- |
| 基礎設施 | Rust + Tokio、OpenTelemetry、NATS      |
| 服務層   | Go + gRPC、Envoy、Kubernetes           |
| 應用層   | TypeScript + Next.js、FastAPI、GraphQL |
| 治理層   | Rego (OPA)、SLSA、Sigstore             |

## 關鍵模組

- `core/island_ai_runtime/*`
- `config/island-ai-runtime.yaml`
- `automation/*`
- `docs/GOVERNANCE/*`

## 伸縮性

- Agent Pool 自動擴縮
- 任務分片 + 工作流重試
- 多雲部署（AWS/GCP/Azure）
