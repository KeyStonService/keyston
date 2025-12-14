# 自動化元件概覽

## Pipeline 類型

| 名稱 | 功能 |
|------|------|
| Schema Pipeline | 統一資料與 API 契約演進 |
| Auto-Fix Pipeline | 靜/動態分析 + 自動修復 |
| Deployment Pipeline | 多階段審批 + Canary + 回滾 |
| Knowledge Pipeline | 資料抽取、轉換、嵌入 |

## 編排引擎

- 基於事件觸發 (GitHub, CI, Alert)
- 任務編排語言（YAML DSL）
- 支援並行、重試、超時策略
- 內建審核節點（L2-L4）

## 範例

```yaml
workflows:
  auto_fix:
    trigger: codeql_alert
    steps:
      - run: mcp://codeql/analyze
      - agent: developer
      - decision_level: L3
      - git:
          action: create_pr
```

## 指標

- 平均修復時間 (MTTR)
- 自動化覆蓋率
- Pipeline 成功率
- 人工干預率
