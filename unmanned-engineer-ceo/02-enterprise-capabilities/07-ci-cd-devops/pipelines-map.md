# Pipelines Map / 流水線地圖

| Pipeline            | 描述                              | 入口                                           |
| ------------------- | --------------------------------- | ---------------------------------------------- |
| Core Build          | 單一 workspace 所有 TS/Go/Py 建置 | `npm run build --workspaces`                   |
| Contract Service L1 | 合約服務 BFF                      | `core/contract_service/contracts-L1/contracts` |
| Docs Knowledge Loop | 再生 docs/knowledge-graph.yaml    | `make all-kg`                                  |
| Autonomous Stack    | Drone/自駕                        | `.devcontainer/automation/auto-pilot.js start` |
| Observability       | Grafana/Prometheus 打包           | `infrastructure/monitoring`                    |

> 以 Mermaid 或 JSON 將 pipelines-map 匯出給 manifest，以利治理系統掌握依賴。
