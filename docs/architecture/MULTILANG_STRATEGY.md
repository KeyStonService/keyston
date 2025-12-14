# 多語言策略

## 原則

1. 為需求選擇最適語言，不追求單一技術堆疊
2. 以統一治理層收斂語言差異
3. 提供跨語言工具鏈與 API 契約

## 語言地圖

| 層級 | 語言 | 主要任務 |
|------|------|----------|
| 基礎設施 | Rust | 高性能運算、監控代理 |
| 服務層 | Go | 微服務、API Gateway |
| 應用層 | TypeScript | Web/CLI/業務邏輯 |
| AI/ML | Python | 數據管道、ML 服務 |
| 企業整合 | Java | 遺留系統、批處理 |

## 整合策略

- 統一 API（gRPC + GraphQL）
- Schema 儲存在 `system-module-map.yaml`
- 使用 Bazel/Pants 管理跨語言建置
- 共享 Observability SDK

## 風險控管

- 所有語言遵循相同 lint/test 標準
- 每個島嶼有維護者與 SLO
- 發生跨語言變更時引入架構師 Agent
