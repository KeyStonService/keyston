# ops

## 目錄職責

此目錄為 MachineNativeOps 的**運維中心**，包含自動化工作流、監控配置和運維政策。

## 子目錄說明

| 子目錄 | 職責 | 內容 |
|--------|------|------|
| `automation/` | 運維自動化 | pipelines, scripts, workflows |
| `monitoring/` | 監控與告警 | alerts, dashboards, logs |
| `policies/` | 運維政策 | 存取控制、備份政策 |

## 目錄結構

```
ops/
├── automation/               # 運維自動化
│   ├── pipelines/           # CI/CD 管道配置
│   ├── scripts/             # 自動化腳本
│   └── workflows/           # 工作流程定義
├── monitoring/               # 監控系統
│   ├── alerts/              # 告警規則
│   ├── dashboards/          # 監控儀表板
│   └── logs/                # 日誌配置
├── policies/                 # 運維政策
│   ├── access-control.md    # 存取控制政策
│   ├── backup-policy.md     # 備份政策
│   └── pipeline.memory.policy.v1.0.0.yaml.txt  # Pipeline 記憶體政策
└── machinenativeops-axm-gate-fused-v2r1.yaml.txt  # Axiom 閘門配置
```

## 檔案說明

### machinenativeops-axm-gate-fused-v2r1.yaml.txt

- **職責**：Axiom AXM Gate 融合配置
- **功能**：定義系統閘門控制規則與驗證邏輯
- **格式**：YAML 配置（.txt 副檔名）

## 職責分離說明

- **automation/**：自動化執行邏輯，由 DevOps 團隊維護
- **monitoring/**：觀測與告警配置，由 SRE 團隊維護
- **policies/**：運維規範與約束，由運維架構師維護

## 與其他目錄的關係

- **deploy/**：部署配置（ops 負責部署後的運維）
- **scripts/**：通用腳本（ops/automation 專注運維腳本）
- **config/monitoring/**：監控相關的環境配置

## 設計原則

1. **可觀測性優先**：所有運維操作應有日誌和指標
2. **自動化優先**：重複性任務應自動化執行
3. **政策即代碼**：運維政策應可版本控制和自動驗證
