# 必要核心檔案工程師指南 / Essential Core Files Guide

> 本指南提供工程師在 SynergyMesh 平台上必須掌握的 15 份核心檔案。依照「讀取優先順序 → 內容要點 → 驗證方式」的格式，確保在開發、部署與維運過程中不會遺漏關鍵資訊。

## 0. 快速索引（按優先順序）

| 序號 | 檔案 | 核心職責 | 常見陷阱 |
| --- | --- | --- | --- |
| 1 | [synergymesh.yaml](synergymesh.yaml) | 全域真實來源（Single Source of Truth） | 與模組地圖、實際部署不同步 |
| 2 | [config/system-manifest.yaml](config/system-manifest.yaml) | 系統元件宣告與狀態矩陣 | 忘記更新狀態欄位 / 擁有者 |
| 3 | [config/unified-config-index.yaml](config/unified-config-index.yaml) | 統一配置索引 + 模組引用關係 | 缺少新模組或環境參數 |
| 4 | [config/system-module-map.yaml](config/system-module-map.yaml) | 模組間依賴、部署邊界 | 環境特定依賴未標註 |
| 5 | [.env](.env) | 生產級環境變數模板 | 留空敏感值、未同步到 K8s Secret |
| 6 | [config/safety-mechanisms.yaml](config/safety-mechanisms.yaml) | 零信任安全配置、Kill Switch | 未跑治理驗證導致 CI 阻擋 |
| 7 | [DEPLOYMENT_MANIFEST.md](DEPLOYMENT_MANIFEST.md) | Docker + K8s 部署手冊 | 忽略前置檢查 / 缺少 artifact 版本 |
| 8 | [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | 99 項部署驗證清單 | 未完成即開部署造成回滾 |
| 9 | [SYSTEM_DIAGNOSTICS.md](SYSTEM_DIAGNOSTICS.md) | 監控、告警、健康檢查程序 | 未啟動自我診斷腳本 |
| 10 | [QUICK_START.production.md](QUICK_START.production.md) | 生產快速啟動（繁/英） | 沒有依序完成 5 分鐘檢查 |
| 11 | [core/README.md](core/README.md) | 核心心智矩陣與 AI 流程 | 忽略安全鉤子導致測試失敗 |
| 12 | [automation/README.md](automation/README.md) | 五骨架自主框架 | 未遵循骨架邊界導致 ROS/K8s 衝突 |
| 13 | [services/README.md](services/README.md) | 代理與 MCP 服務 | 認證/授權流程遺漏 |
| 14 | [infrastructure/README.md](infrastructure/README.md) | K8s、監控、Scaling 策略 | 忽略 HPA/VPA 配置 |
| 15 | [FINAL_DELIVERY_REPORT.md](FINAL_DELIVERY_REPORT.md) | 交付統計、後續任務 | 沒有回填交付紀錄，導致稽核缺口 |

---

## 1. 統一配置來源層

### 1.1 [synergymesh.yaml](synergymesh.yaml)

- **使命**：定義整體平台的模組、執行模式、治理指標，是所有 Pipeline 的入口參數。
- **必讀欄位**：`capabilities`, `service_registry`, `safety.posture`, `knowledge_cycle`。
- **更新節奏**：任何新服務、AI 模組、或 SLSA 承諾變更時立即更新。
- **驗證**：`npm run lint --workspaces --if-present` 會對其 Schema 做靜態檢查。

### 1.2 [config/system-manifest.yaml](config/system-manifest.yaml)

- **使命**：列出每個子系統的狀態、擁有者、SLA、版本。
- **必備內容**：`id`, `owner`, `lifecycle`, `deployment`, `observability`。
- **常見錯誤**：忘記同步 `status`（例如 `ga`, `beta`）。
- **驗證**：`python tools/docs/validate_index.py --verbose`。

### 1.3 [config/unified-config-index.yaml](config/unified-config-index.yaml)

- **使命**：整合所有配置檔的索引，描述每個檔案的 domain、優先順序、使用場景。
- **必備內容**：`entries[].path`, `layer`, `environment`, `checksum`。
- **驗證**：`make all-kg` 會讀取此索引並生成知識圖譜。

### 1.4 [config/system-module-map.yaml](config/system-module-map.yaml)

- **使命**：標註模組依賴與部署邊界，供架構師與 DevOps 溝通。
- **建議內容**：`modules[].inputs`, `modules[].outputs`, `runtime`, `compliance`。
- **驗證**：`python automation/self_awareness_report.py --check modules`。

---

## 2. 安全與治理層

### 2.1 [.env](.env)

- **使命**：提供生產級環境變數樣板，對照 K8s Secret 與 CI Variables。
- **必填欄位**：`DATABASE_URL`, `API_GATEWAY_KEY`, `JWT_SECRET`, `PROMETHEUS_URL` 等。
- **守則**：不直接 commit 真實密鑰，僅填占位符；確保與 `config/environment.yaml` 對齊。

### 2.2 [config/safety-mechanisms.yaml](config/safety-mechanisms.yaml)

- **使命**：定義 Kill Switch、降級策略、SLSA 鑑別流程。
- **內容要點**：`circuit_breakers`, `rollback`, `incident_bridge`, `audit_hooks`。
- **驗證**：`npm run dev:stack` 會在啟動時載入並檢查必填欄位。

### 2.3 [config/ai-constitution.yaml](config/ai-constitution.yaml)

- **使命**：AI 三層憲法，約束決策引擎、虛擬專家與自動化代理。
- **必讀段落**：`supreme_directives`, `delegation_matrix`, `redline_policies`。
- **治理要求**：重大改動需透過架構評審並更新 `FINAL_DELIVERY_REPORT`。

### 2.4 [governance/policies/](governance/policies)

- **使命**：Conftest/OPA Policy Gate，保證 K8s、容器、CI 維持合規。
- **流程**：每次 PR 由 CI 自動執行 `npm run docs:lint` + `policy test`。

---

## 3. 部署與營運層

### 3.1 [DEPLOYMENT_MANIFEST.md](DEPLOYMENT_MANIFEST.md)

- **使命**：提供 Docker Compose 與 Kubernetes 兩條部署流程。
- **必查章節**：`Pre-deployment Checklist`, `Dependency Manifest`, `Troubleshooting`。
- **實務建議**：在 PR 描述中貼上執行過的段落與結果。

### 3.2 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

- **使命**：99 項部署驗證清單，覆蓋環境、依賴、安全、文件、驗證。
- **操作方式**：逐項打勾並在 MR/PR 訊息附上完成時間戳。

### 3.3 [QUICK_START.production.md](QUICK_START.production.md)

- **使命**：繁/英雙語的 5 分鐘生產啟動指引。
- **段落**：環境準備 → 依賴安裝 → 模組啟動 → Docker → K8s → 監控 → 安全。

### 3.4 [SYSTEM_DIAGNOSTICS.md](SYSTEM_DIAGNOSTICS.md)

- **使命**：健康檢查、Prometheus 查詢、Grafana 儀表板、ELK 日誌流程。
- **CICD 務必執行**：`python automation/self_awareness_report.py --mode=health`。

### 3.5 [PROJECT_DELIVERY_CHECKLIST.md](PROJECT_DELIVERY_CHECKLIST.md)

- **使命**：交付驗證（檔案、README、CI、可靠度指標、SLSA）
- **建議**：作為每次版本切換的 Release Gate。

### 3.6 [FINAL_DELIVERY_REPORT.md](FINAL_DELIVERY_REPORT.md)

- **使命**：統計交付內容、後續任務、品質指標，方便稽核與回溯。
- **必填欄位**：`Achievement Summary`, `Next Steps`, `Verification Steps`。

---

## 4. 模組與程式碼層

| 模組 | 檔案 | 重點 | 驗證 |
| --- | --- | --- | --- |
| 核心引擎 | [core/README.md](core/README.md) | 感知→推理→執行→證明四層架構 | `npm run test -w core/contract_service/contracts-L1/contracts` |
| 自動化骨架 | [automation/README.md](automation/README.md) | 五骨架（架構穩定性、API 治理等） | `npm run dev:stack` |
| 服務層 | [services/README.md](services/README.md) | Agents、MCP、API gateway | `npm run lint --workspaces --if-present services/*` |
| 應用層 | [apps/README.md](apps/README.md) | React 18 + FastAPI 雙棧流程 | `npm run dev -w apps/web` + `pytest apps/web/backend` |
| 基礎設施 | [infrastructure/README.md](infrastructure/README.md) | K8s manifests、監控、Scaling | `kubectl kustomize infrastructure/kubernetes` |
| 工具層 | [tools/README.md](tools/README.md) | CLI、索引生成、驗證腳本 | `python tools/docs/validate_index.py --verbose` + `make all-kg` |

> **實務建議**：任何程式碼修改前，先閱讀對應模組 README 的「Guard Rails」章節，再決定要更新的配置或腳本。

---

## 5. 知識庫與觀測層

### 5.1 [docs/KNOWLEDGE_HEALTH.md](docs/KNOWLEDGE_HEALTH.md)

- 敘述活體知識庫健康狀態、突出指標、Open Issues。

### 5.2 [docs/generated-mndoc.yaml](docs/generated-mndoc.yaml) / [docs/knowledge-graph.yaml](docs/knowledge-graph.yaml) / [docs/superroot-entities.yaml](docs/superroot-entities.yaml)

- 由 `make all-kg` 自動產出，**禁止手動修改**。
- 當 README 或配置變更後，務必重新生成並提交。

### 5.3 [automation/self_awareness_report.py](automation/self_awareness_report.py)


---

## 6. 變更流程建議

1. **變更前**：
   - 檢查是否需要同步 `synergymesh.yaml`, `system-manifest`, `unified-config-index`。
   - 閱讀對應模組 README 的治理規則。
2. **變更中**：
   - 更新 `.env` 占位符與 Secrets；確保安全鉤子不被繞過。
   - 若新增服務，先更新 `system-module-map` → `system-manifest` → `documentation index`。
3. **變更後**：
   - 執行 `make all-kg`, `npm run lint`, `npm run test`, `npm run build`。
   - 將結果記錄於 `FINAL_DELIVERY_REPORT.md` 與 `PROJECT_DELIVERY_CHECKLIST.md`。
   - 在 PR Template 中貼上相對應的 Checklist 片段。

---

## 7. 最佳實務速查

- **單一來源**：`synergymesh.yaml` 與 `system-manifest` 不同步時，後者優先；務必立刻修正。
- **密鑰治理**：`.env` 只存模板；實際值放入 Vault/K8s Secret，並記錄於 `FINAL_DELIVERY_REPORT.md` 的「安全摘要」。
- **部署責任**：若 `DEPLOYMENT_CHECKLIST.md` 未完成 100%，禁止進入 `DEPLOYMENT_MANIFEST.md` 的實際步驟。
- **監控閉環**：任何事故後，`SYSTEM_DIAGNOSTICS.md` + `docs/KNOWLEDGE_HEALTH.md` 必須同步更新。
- **稽核備份**：`FINAL_DELIVERY_REPORT.md` + `PROJECT_DELIVERY_CHECKLIST.md` 是審計與交付佐證，遺漏將導致發布退件。

---

> 持續維護此指南，確保新進工程師 30 分鐘內即可掌握 SynergyMesh 的必要檔案、生產流程與驗證節奏。若需新增條目，請先更新 `config/unified-config-index.yaml` 再提交 PR。
