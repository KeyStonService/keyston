# Ops

MachineNativeOps 運維中心，包含自動化、監控和運維政策。

## 目錄結構

```
ops/
├── automation/    # 運維自動化
│   ├── pipelines/ # CI/CD 管道
│   ├── scripts/   # 自動化腳本
│   └── workflows/ # 工作流程
├── monitoring/    # 監控系統
│   ├── alerts/    # 告警規則
│   ├── dashboards/# 儀表板
│   └── logs/      # 日誌配置
└── policies/      # 運維政策
```

## 核心功能

### Automation（自動化）

運維自動化工具和工作流程：

- **pipelines/**：CI/CD 管道配置
- **scripts/**：日常運維腳本
- **workflows/**：複合工作流程定義

### Monitoring（監控）

系統監控與告警：

- **alerts/**：告警規則定義
- **dashboards/**：Grafana 等儀表板配置
- **logs/**：日誌收集與處理配置

### Policies（政策）

運維政策與規範：

| 政策 | 說明 |
|------|------|
| access-control.md | 存取控制政策 |
| backup-policy.md | 備份與恢復政策 |

## 根目錄文件

- `axiom-axm-gate-fused-v2r1.yaml.txt` - Axiom 閘門融合配置

## 與其他目錄的關係

| 目錄 | 關係 |
|------|------|
| deploy/ | ops 負責部署後的運維工作 |
| scripts/ | 通用腳本，ops 專注運維腳本 |
| config/monitoring/ | 監控相關的環境配置 |

## 相關資源

- [DIRECTORY.md](./DIRECTORY.md) - 詳細目錄說明
- [docs/operations/](../docs/operations/) - 運維文檔
