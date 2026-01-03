# 根目錄

## 為什麼會來這裡 / 入口

- **位置**: `.`
- **我在這裡通常要解決什麼**：找到整個平台的入口、全域配置與操作指南。
- **首選入口**：`README.md`（平台概覽）、`machinenativeops.yaml`（統一配置）、`Makefile`（常用自動化任務）。
- **常見任務**：
  - 確認平台願景 / 快速開始（`README.md`、`README_INSTANT_GENERATION.md`）
  - 執行文檔與知識圖生成（Makefile：`mndoc`、`kg`、`all-kg`）
  - 安裝 / 同步依賴（`package.json`、`requirements-*.txt`）
  - 決定要深入的子系統（`src/`、`config/`、`deploy/`、`governance/`、`docs/`）
- **子目錄速覽**：
  - `config/` 環境與治理配置
  - `docs/` 文檔系統
  - `src/` 核心源碼與服務
  - `tools/` 工具與生成器
  - `scripts/` 自動化腳本
  - `tests/` 測試
  - `deploy/` 部署配置
  - `ops/` 運維
  - `examples/` 範例模板
  - `archive/` 歷史資料

## 推薦閱讀路線

1. `README.md`（平台概覽與目錄導覽）
2. `machinenativeops.yaml`（統一配置來源）
3. `docs/DIRECTORY.md` 或 `governance/README.md` 依需求深入
4. `Makefile`（常用自動化任務）
5. 對應子系統的 `DIRECTORY.md`（例如 `src/DIRECTORY.md`、`tools/DIRECTORY.md`）

## 輸入 / 輸出（直覺版）

- **輸入**：統一配置 (`machinenativeops.yaml`)、工作區 package 配置、Python/Node 依賴清單、環境變數。
- **輸出**：生成的文檔 / 知識圖 (`docs/generated/*`)、構建產物、CI 報告、部署工件。
- **主要上下游/協作者**：CI/CD 工作流、開發者工具（`tools/`、`scripts/`）、部署 / 運維（`deploy/`、`ops/`）、核心服務（`src/`）。

## 變更影響範圍（Blast radius）

- 修改 `machinenativeops.yaml` 會影響所有下游配置與工具。
- 修改 `package.json` / `requirements-*.txt` 會影響開發/CI 環境依賴。
- 修改 `Makefile` 會影響文檔與知識圖生成流程。
- 調整根級 README / 計劃文件會影響入門與治理敘述。

## 檔案速覽（人話版）

### README.md

- **一句話摘要**：平台總覽、設計理念與快速開始入口。
- **我不確定/待釐清**：需與 `docs/` 中的最新細節保持同步。
- **相關連結**：`docs/`、`governance/00-vision-strategy/`

### machinenativeops.yaml

- **一句話摘要**：整個平台的統一配置（入口與真實來源）。
- **我不確定/待釐清**：與 `config/` 下環境覆蓋的優先序。
- **相關連結**：`config/`、`deploy/`

### Makefile

- **一句話摘要**：文檔與知識圖生成、治理驗證等常用任務集合。
- **我不確定/待釐清**：各任務的依賴安裝前置。
- **相關連結**：`tools/docs/`、`docs/generated/`

### package.json

- **一句話摘要**：多工作區的 Node/NPM 入口與通用腳本。
- **我不確定/待釐清**：各 workspace 安裝順序及互斥版本。
- **相關連結**：`src/mcp-servers/`、`src/core/contract_service/contracts-L1/contracts/`

### requirements-prod.txt

- **一句話摘要**：生產環境 Python 依賴清單。
- **我不確定/待釐清**：與 dev/workflow 需求的差異。
- **相關連結**：`requirements-debug.txt`、`requirements-workflow.txt`

### Dockerfile

- **一句話摘要**：基礎容器鏡像定義（平台根鏡像）。
- **我不確定/待釐清**：對應的 compose / 部署流程。
- **相關連結**：`docker-compose.prod.yml`、`deploy/docker/`

### docs/

- **一句話摘要**：全域文檔與治理說明集合。
- **我不確定/待釐清**：哪些生成檔案需重新產出。
- **相關連結**：`docs/DIRECTORY.md`、`Makefile`

### src/

- **一句話摘要**：核心源碼與服務、自主 / 治理引擎。
- **我不確定/待釐清**：子模組間的依賴邊界。
- **相關連結**：`src/DIRECTORY.md`、`governance/`

### scripts/

- **一句話摘要**：CI/CD、部署與運維相關的自動化腳本。
- **我不確定/待釐清**：各腳本的執行前提與目標環境。
- **相關連結**：`scripts/DIRECTORY.md`、`ops/`、`deploy/`

### tools/

- **一句話摘要**：生成器、驗證器與開發輔助工具（含 DIRECTORY 生成）。
- **我不確定/待釐清**：哪些工具會改寫生成產物。
- **相關連結**：`tools/DIRECTORY.md`、`tools/directory_doc_generator.py`

## 待釐清 / TODO

- 子目錄的 `DIRECTORY.md` 需逐步補齊導航與影響範圍。
- 確認 `config/` 與 `machinenativeops.yaml` 的覆蓋策略並記錄。
- 標記 `docs/generated/*` 的再生成條件。

## 未來可轉 JSON 的錨點

- **path**: `.`
- **entrypoints**: ["README.md", "machinenativeops.yaml", "Makefile"]
- **status**: draft
