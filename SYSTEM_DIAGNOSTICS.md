# 📈 系統監控與診斷 / System Monitoring & Diagnostics

## 概述 / Overview

本指南涵蓋系統監控、診斷、日誌收集和故障排除程序。

This guide covers system monitoring, diagnostics, log collection, and troubleshooting procedures.

---

## 🔍 系統診斷 / System Diagnostics

### 快速診斷 / Quick Diagnostics

```bash
# 運行系統診斷
bash tools/scripts/analyze.sh

# 或使用 Python
python3 automation/self_awareness_report.py --verbose

# 輸出診斷報告
python3 automation/self_awareness_report.py --output diagnosis-report.json
```

### 組件狀態檢查 / Component Health Checks

```bash
# 檢查核心服務
curl http://localhost:3000/health
curl http://localhost:8000/health

# 檢查資料庫
curl http://localhost:3000/api/v1/db/status

# 檢查 Redis
redis-cli ping

# 檢查所有服務
curl http://localhost:3000/api/v1/services/status
```

### Kubernetes 診斷 / Kubernetes Diagnostics

```bash
# 檢查 Pod 狀態
kubectl get pods -n synergymesh
kubectl describe pod <pod-name> -n synergymesh

# 查看 Pod 日誌
kubectl logs <pod-name> -n synergymesh
kubectl logs -f <pod-name> -n synergymesh

# 進入 Pod
kubectl exec -it <pod-name> -- sh

# 查看事件
kubectl get events -n synergymesh
kubectl describe node
```

---

## 📊 監控系統 / Monitoring System

### Prometheus 指標 / Prometheus Metrics

```bash
# 訪問 Prometheus
http://localhost:9090

# 常用查詢 / Common Queries:
# 請求速率
rate(http_requests_total[5m])

# 錯誤率
rate(http_requests_failed_total[5m])

# 响應時間
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# CPU 使用率
process_cpu_seconds_total

# 記憶體使用率
process_resident_memory_bytes
```

### Grafana 儀表板 / Grafana Dashboards

```bash
# 訪問 Grafana
http://localhost:3000 (admin/admin)

# 常用儀表板 / Common Dashboards:
# - System Overview
# - Application Performance
# - Infrastructure Metrics
# - Error Tracking
```

---

## 📝 日誌管理 / Log Management

### 日誌位置 / Log Locations

```
Docker:
  docker-compose logs -f
  /var/lib/docker/containers/<container-id>/<container-id>-json.log

Kubernetes:
  kubectl logs -f <pod-name> -n synergymesh
  /var/log/pods/<pod-name>/<container-name>/*.log

Local:
  logs/
  logs/error.log
  logs/access.log
```

### 日誌查詢 / Log Queries

```bash
# 查看特定級別的日誌
grep "ERROR" logs/*.log
grep "WARN" logs/*.log

# 查看特定時間範圍
grep "2025-01-15" logs/*.log

# 統計日誌數量
wc -l logs/*.log

# 查看最後 N 行
tail -f logs/error.log
```

---

## 🆘 常見問題 / Troubleshooting

### Connection Timeout
```bash
# 檢查防火牆
sudo ufw status
sudo ufw allow 3000/tcp

# 檢查服務狀態
systemctl status synergymesh

# 查看日誌
tail -f logs/error.log
```

### Out of Memory
```bash
# 檢查記憶體使用
free -h
top -p $(pgrep -f node)

# 增加 Node 堆大小
node --max-old-space-size=4096 app.js
```

### Database Connection Error
```bash
# 檢查資料庫服務
sudo systemctl status postgresql

# 測試連接
psql -h localhost -U user -d synergymesh

# 重啟服務
sudo systemctl restart postgresql
```

---

## 📋 監控檢查清單 / Monitoring Checklist

### 日常檢查 / Daily Checks
- [ ] 系統可用性 > 99%
- [ ] 錯誤率 < 0.1%
- [ ] 無待處理告警
- [ ] 磁盤空間 > 20%
- [ ] 資料庫備份完成

### 周期性檢查 / Weekly Checks
- [ ] 效能趨勢分析
- [ ] 容量規劃評估
- [ ] 安全掃描
- [ ] 依賴更新檢查
- [ ] 備份驗證

---

## 📞 支援 / Support

- 📖 [監控文檔](./docs/operations/)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
