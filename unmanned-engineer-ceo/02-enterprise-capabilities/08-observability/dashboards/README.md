# Dashboard Patterns

| Panel            | 指標                         | 資料來源                            |
| ---------------- | ---------------------------- | ----------------------------------- |
| Contract Latency | p50/p95 latency              | Prometheus histograms               |
| Drone Health     | Battery, GPS lock, CPU       | automation/autonomous telemetry     |
| Knowledge Loop   | Regen duration, drift alerts | automation/self_awareness_report.py |

> 建議以 JSON (Grafana) 或 YAML (k3d
> dashboards) 描述，並連結至 infrastructure/monitoring。
