# Teams 工作團隊目錄

統一管理所有 AI 代理團隊的單一真相來源 (Single Source of Truth, SSOT)。

## 目錄結構

```
teams/
├── README.md                    # 本文件
├── registry.yaml                # 代理註冊表（所有代理的統一索引）
└── default-team/                # 預設團隊
    ├── team.yaml                # 團隊配置
    ├── playbooks/               # 工作流程劇本
    │   ├── boot.yaml            # 啟動流程
    │   ├── on_run_created.yaml  # 任務建立流程
    │   └── on_chat_message.yaml # 聊天訊息流程
    └── profiles/                # 角色人設檔案
        ├── role.career_counselor.md
        ├── role.statistician.md
        ├── role.tech_writer.md
        └── ...
```

## 核心概念

### 1. 團隊 (Team)

團隊是一組協作的代理，透過 `team.yaml` 定義成員、激活規則和協作模式。

### 2. 劇本 (Playbook)

劇本定義團隊的工作流程，包括：

- **觸發條件**：何時啟動流程
- **執行步驟**：按順序或並行執行的任務
- **代理調度**：哪個代理負責哪個步驟
- **工件產出**：每步產生的 artifacts

### 3. 角色人設 (Persona Profile)

人設檔案定義代理的：

- 角色定義
- 核心能力
- 工作模式
- 輸出格式
- 適用場景

### 4. 註冊表 (Registry)

`registry.yaml` 統一索引所有代理，包括：

- 代理 ID 和名稱
- 實現語言和位置
- 能力列表
- 狀態

## 激活機制

### 自動激活

當 `auto_activate: true` 時，Orchestrator 啟動後自動激活團隊：

1. 載入 `registry.yaml`
2. 執行 `boot.yaml` 劇本
3. 健康檢查所有成員
4. 生成啟動報告

### 事件驅動

團隊監聽以下事件並執行對應劇本：

- `RUN_CREATED` → `on_run_created.yaml`
- `CHAT_MESSAGE_CREATED` → `on_chat_message.yaml`
- `CODE_CHANGE_DETECTED` → 自定義劇本

## 代理清單

| 層級 | 數量 | 語言 |
|------|------|------|
| 中央編排層 | 1 | Python |
| AI 專家層 | 6 | TypeScript |
| 服務代理層 | 5 | Python |
| 即時生成層 | 6 | Python |
| 自主系統層 | 7 | Python |
| **總計** | **25+** | 混合 |

## 使用方式

### 啟動團隊

```bash
# Orchestrator 啟動時自動激活

python orchestrator/main.py

# 或手動激活

curl -X POST http://localhost:5000/v1/teams/default-team/activate
```

### 建立任務

```bash
# 建立新任務，觸發 on_run_created 流程

curl -X POST http://localhost:5000/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"request": "設計一個電商網站架構"}'
```

### 檢視工件

```bash
# 查看生成的工件

ls artifacts/runs/<run_id>/
# architecture_proposal.md

# security_review.md

# devops_plan.md

# exec_summary.md

```

## 審計與追蹤

所有操作都會記錄到 `audit/events.jsonl`：

```json
{"event": "TEAM_ACTIVATED", "team_id": "default-team", "timestamp": "..."}
{"event": "PLAYBOOK_STARTED", "playbook": "on_run_created", "run_id": "..."}
{"event": "AGENT_DISPATCHED", "agent_id": "ai.architect", "step_id": "..."}
{"event": "ARTIFACT_WRITTEN", "name": "architecture_proposal", "path": "..."}
```

## 擴展團隊

### 新增代理

1. 在 `registry.yaml` 添加代理條目
2. 在 `team.yaml` 的 `members` 添加成員
3. 更新相關 playbook 的步驟

### 新增角色人設

1. 在 `profiles/` 創建 `role.<name>.md`
2. 在 `team.yaml` 的 `personas` 添加引用

### 新增劇本

1. 在 `playbooks/` 創建新的 `.yaml` 檔案
2. 在 `team.yaml` 的 `playbooks` 添加引用
3. 定義觸發事件和執行步驟
