# island-cli 指南

## 目標

- 將 AI Agent 能力帶入終端
- 統一人機互動入口
- 打通 GitHub / CI / 知識庫

## 安裝

```bash
cd tools/cli
npm install
npm run build
npm link
```

## 常用指令

| 指令                        | 說明               |
| --------------------------- | ------------------ |
| `island-cli chat`           | 啟動互動模式       |
| `island-cli analyze <path>` | 靜態分析目錄       |
| `island-cli fix --auto`     | 啟動 Auto-Fix 流程 |
| `island-cli agent:<role>`   | 指派特定 Agent     |
| `island-cli collaborate`    | 多 Agent 協作      |
| `island-cli github:*`       | GitHub 整合操作    |

## 組態

```yaml
cli:
  default_agents:
    - developer
    - qa
  knowledge_base: local
  transport: websocket
```

## 開發指南

1. 新增 command 於 `src/commands`
2. 透過 `AgentBus` 發送請求
3. 使用 `Adapters` 串接 GitHub / CI
