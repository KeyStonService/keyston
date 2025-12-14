# 虛擬專家系統

## Agent 一覽

| 名稱 | 角色 | 關鍵能力 |
| ------ | ------ | ---------- |
| Architect | 架構優化 | 技術雷達、性能建模 |
| Developer | 代碼實作 | 多語言生成、重構 |
| Security | 安全防護 | SAST/DAST、供應鏈掃描 |
| DevOps | 部署營運 | CI/CD、觀測、混沌測試 |
| QA | 測試治理 | 測試生成、覆蓋率分析 |
| Data Scientist | 數據洞察 | 特徵工程、模型監控 |
| Product | 需求策展 | 優先級、用戶洞察 |

## 能力模型

- **感知**：解析程式碼、日誌、指標、工單
- **決策**：結合治理等級與策略引擎
- **執行**：透過工具鏈與 GitHub 整合
- **學習**：回寫知識庫與決策記錄

## 配置樣板

```yaml
agents:
  developer:
    triggers:
      - push
      - issue:labeled:feature
    tools:
      - codegen
      - refactor
  security:
    triggers:
      - dependency:update
      - alert:severity=high
    policies:
      min_level: L2
```

## 擴充流程

1. 定義角色能力矩陣
2. 建立觸發與輸入解析
3. 綁定工具與執行上下文
4. 加入治理審批點
5. 設定成功量測指標
