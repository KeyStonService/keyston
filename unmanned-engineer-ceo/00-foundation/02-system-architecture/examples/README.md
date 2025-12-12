# Architecture Examples

| Case                   | 說明                                      | 來源                                                                    |
| ---------------------- | ----------------------------------------- | ----------------------------------------------------------------------- |
| Core Contract Service  | L1 合約服務，採 Event Sourcing + REST API | core/contract_service                                                   |
| Autonomous Drone Stack | 五骨架 ROS2 + Python API Gateway          | automation/autonomous                                                   |
| Knowledge Health Loop  | Docs 生成 + 自我診斷流水線                | docs/knowledge-health-report.yaml + automation/self_awareness_report.py |

> 每個案例需提供：系統圖、資料流、SLO、依賴、風險。新增案例時請建立
> `case-<name>.md`，並連結至 manifest。
