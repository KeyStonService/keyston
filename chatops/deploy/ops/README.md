# ChatOps Operations Directory

運維文檔和標準操作程序 (SOP) 中心。

## 目錄結構

```
ops/
├── incident-response/     # 事件響應流程
│   ├── playbooks/         # 事件處理手冊
│   ├── severity-levels.md # 嚴重性等級定義
│   └── escalation.md      # 升級流程
├── runbooks/              # 操作手冊
│   ├── deployment/        # 部署相關
│   ├── database/          # 數據庫操作
│   ├── kubernetes/        # K8s 操作
│   └── troubleshooting/   # 故障排查
├── disaster-recovery/     # 災難恢復
│   ├── dr-plan.md         # DR 計劃
│   ├── backup-restore.md  # 備份恢復
│   └── failover/          # 故障切換程序
└── on-call/               # 值班相關
    ├── schedule.md        # 值班排程
    └── handoff.md         # 交接流程
```

## 快速連結

| 場景 | 文檔 |
|------|------|
| 生產事件 | [事件響應流程](incident-response/playbooks/general-incident.md) |
| 數據庫問題 | [數據庫 Runbook](runbooks/database/README.md) |
| 部署失敗 | [部署 Runbook](runbooks/deployment/rollback.md) |
| 災難恢復 | [DR 計劃](disaster-recovery/dr-plan.md) |

## 嚴重性等級

| 等級 | 描述 | 響應時間 | 示例 |
|------|------|----------|------|
| P0 | 全面服務中斷 | 15 分鐘 | 所有用戶無法訪問 |
| P1 | 重大功能降級 | 30 分鐘 | 核心功能不可用 |
| P2 | 部分功能受影響 | 2 小時 | 非關鍵功能故障 |
| P3 | 輕微問題 | 24 小時 | UI 問題、非緊急 bug |

## 聯繫方式

- **On-Call**: 查看 PagerDuty 排程
- **Slack**: #chatops-incidents
- **Email**: oncall@chatops.example.com
