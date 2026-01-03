# Meta Conventions - 重構劇本命名與結構規範

本文件定義 `03_refactor/` 中所有重構劇本的命名規則、檔案結構與約定，確保系統一致性。

---

## 1. 檔名命名規則

所有重構劇本檔案遵循以下格式：

```
{domain}__{cluster}_refactor.md
```

### 規則說明

- **domain**：對應 repo 的頂層目錄或子系統名稱
  - 有效值：`core`, `services`, `automation`, `apps`, `governance`, `infra`, `knowledge`
  - 使用小寫，單字間用底線分隔（snake_case）

- **cluster**：目標群集或模組的具體名稱
  - 範例：`architecture`, `autonomous`, `gateway`, `web`, `schemas`
  - 使用小寫，單字間用底線分隔（snake_case）

- **後綴**：固定為 `_refactor.md`

### 命名範例

| 檔名 | Cluster Path | 說明 |
|------|--------------|------|
| `core__architecture_refactor.md` | `core/architecture-stability` | Core 架構穩定性重構 |
| `services__gateway_refactor.md` | `services/gateway` | Gateway 服務重構 |
| `automation__autonomous_refactor.md` | `automation/autonomous` | 自主系統重構 |
| `apps__web_refactor.md` | `apps/web` | Web 應用重構 |
| `governance__schemas_refactor.md` | `governance/schemas` | Schema 治理重構 |

---

## 2. Cluster ID 命名規則

Cluster ID 是機器可讀索引中使用的標準識別符。

### 格式

```
{domain}/{module-name}
```

### 規則

- 使用 repo 中的實際目錄路徑
- 使用短橫線分隔（kebab-case）而非底線
- 必須對應真實存在的目錄結構

### 範例

```yaml
clusters:
  - cluster_id: "core/architecture-stability"
    domain: "core"
    refactor_file: "core/core__architecture_refactor.md"
  
  - cluster_id: "services/agents"
    domain: "services"
    refactor_file: "services/services__agents_refactor.md"
```

---

## 3. 目錄結構對應

### Domain 分組

所有重構劇本根據 domain 分組到對應子目錄：

```text
03_refactor/
  ├─ core/                    # 核心引擎與平台服務
  ├─ services/                # 後端服務與 gateway
  ├─ automation/              # 自動化與智能系統
  ├─ apps/                    # 前端與 CLI 應用
  ├─ governance/              # 治理系統
  ├─ infra/                   # 基礎設施
  └─ knowledge/               # 活體知識庫
```

### 一對一映射

每個重構劇本應該對應：

1. **一個 Cluster** - 明確的目錄或模組群組
2. **一個解構劇本** - `01_deconstruction/{domain}__{cluster}_deconstruction.md`
3. **一個集成劇本** - `02_integration/{domain}__{cluster}_integration.md`

---

## 4. 檔頭格式規範

每個重構劇本的檔頭必須包含以下欄位：

```markdown
# {Cluster Name} 重構劇本（Refactor Playbook）

- Cluster ID：`{domain}/{module-name}`
- 對應目錄：`{actual/repo/paths}`
- 對應集成劇本：
  - `docs/refactor_playbooks/02_integration/{integration_file}.md`
- 對應解構劇本：
  - `docs/refactor_playbooks/01_deconstruction/{deconstruction_file}.md`
- Legacy Assets：
  - `{legacy_asset_id_1}` (from legacy_assets_index.yaml)
  - `{legacy_asset_id_2}`
```

### 必填欄位

- **Cluster ID** - 標準化的 cluster 識別符
- **對應目錄** - 受影響的實際 repo 路徑（可多個）
- **對應集成劇本** - 02_integration 中的對應檔案
- **對應解構劇本** - 01_deconstruction 中的對應檔案（可選）
- **Legacy Assets** - 舊資產 ID 列表（若適用）

---

## 5. 章節結構規範

所有重構劇本必須包含以下標準章節（按順序）：

1. **Cluster 概覽** - 角色、邊界、語言組成
2. **問題盤點** - 語言治理、Hotspot、安全問題、Flow
3. **語言與結構重構策略** - 語言遷移、目錄調整、集成對齊
4. **分級重構計畫（P0/P1/P2）** - 優先順序行動清單
5. **Auto-Fix Bot 可以處理的項目** - 自動化範圍界定
6. **驗收條件與成功指標** - 量化目標
7. **檔案與目錄結構（交付視圖）** - Tree 結構與註解
8. **集成對齊** - 上下游依賴、步驟、回滾策略

---

## 6. 索引維護規則

### index.yaml 更新

每次新增重構劇本時，必須同步更新：

```yaml
clusters:
  - cluster_id: "{domain}/{module}"
    domain: "{domain}"
    refactor_file: "{domain}/{domain}__{cluster}_refactor.md"
    deconstruction_file: "../01_deconstruction/{domain}__{cluster}_deconstruction.md"
    integration_file: "../02_integration/{domain}__{cluster}_integration.md"
    legacy_assets:
      - "{asset_id}"
```

### INDEX.md 更新

人類可讀索引應包含：

- 檔案名稱與連結
- Cluster ID
- 狀態（Draft / In Progress / Complete）
- 最後更新日期

---

## 7. 版本控制規範

### Git 提交訊息格式

```
refactor(playbook): {action} {cluster_id}

{description}
```

範例：

```
refactor(playbook): add core/architecture-stability refactor plan

- 新增 P0/P1/P2 行動清單
- 定義 Auto-Fix 範圍
- 對齊 integration 劇本約束
```

### 分支命名

```
refactor/{domain}-{cluster}-playbook
```

範例：`refactor/core-architecture-playbook`

---

## 8. 驗證檢查清單

在提交新的重構劇本前，確保：

- [ ] 檔名符合 `{domain}__{cluster}_refactor.md` 格式
- [ ] 檔案放在正確的 domain 子目錄下
- [ ] 檔頭包含所有必填欄位
- [ ] 包含所有 8 個標準章節
- [ ] `index.yaml` 已更新
- [ ] `INDEX.md` 已更新
- [ ] Legacy Assets（如有）在 `legacy_assets_index.yaml` 中已定義
- [ ] 對應的 deconstruction 與 integration 劇本存在

---

## 9. 自動化工具整合

### CI 檢查

建議在 CI 中加入以下檢查：

```bash
# 檢查檔名格式
# 檢查檔頭必填欄位
# 驗證 cluster_id 格式
# 確認 index.yaml 與實際檔案一致
# 驗證 legacy_assets 引用正確
```

### 生成工具

使用腳本從模板生成新劇本：

```bash
python tools/generate-refactor-playbook.py \
  --cluster "core/architecture-stability" \
  --domain "core" \
  --template "03_refactor/templates/REFRACTOR_PLAYBOOK_TEMPLATE.md"
```

---

## 10. 風格指南

### 語言使用

- 主要使用繁體中文（Traditional Chinese）
- 技術術語保留英文（例如：P0, Auto-Fix, CI）
- 檔案路徑與程式碼使用英文

### 格式化


- 清單使用一致的縮排（2 空格）

### 一致性

- 所有劇本使用相同的標題層級結構
- 相似章節使用相同的用語與格式
- 範例保持一致的風格

---

## 11. 檔案類型策略

### 1. 03_refactor 層（重構劇本）

- 使用 `*.md` 作為主要載體（重構劇本、說明、程式碼範例）。
- 可以在檔頭使用 YAML front-matter 承載結構化欄位（cluster_id、legacy_assets、P0/P1/P2 等）。
- 不使用 `*.txt` 作為正式劇本格式。
- 不在 `03_refactor/` 內放可執行程式碼檔案（.ts / .py / .go / .sh ...）。
  - 實際實作一律回寫到 `core/`, `services/`, `apps/`, `automation/`, `tools/` 等主目錄。

### 2. 實際執行程式碼

- 一律放在專案根下的主目錄中：
  - `core/`, `services/`, `apps/`, `automation/`, `tools/`, `mcp-servers/` 等。
- 使用對應語言的副檔名（`.ts`, `.py`, `.go`, `.cpp`, ...）。
- CI / build / deploy 只對這些目錄中的程式碼負責，不會直接執行 `docs/refactor_playbooks/` 內的內容。

### 3. 暫存筆記（notes）與 scratch（草稿 / 思考過程）

> 這一類是「幫助思考與設計」的資料，不是正式規範或執行程式碼。

- **檔案類型**：
  - 可使用 `*.md`, `*.txt`, `*.drawio`, `*.mermaid`, `*.ipynb` 等。
  
- **允許放置位置**（範圍擴大）：
  - `docs/refactor_playbooks/_legacy_scratch/`          # 舊程式碼與重構相關的暫存區（重點給 01/02/03 用）
  - `docs/scratch/`                                     # 全域架構/流程的草稿、比較方案、設計日誌
  - `experiments/`                                      # 原型程式、試驗性腳本（可選擇是否進 git）
  - 各 domain 專屬 `_scratch/` 目錄，例如：
    - `core/_scratch/`
    - `services/_scratch/`
    - `automation/_scratch/`
    - `apps/_scratch/`
    - `governance/_scratch/`
    - `infra/_scratch/`
    - `tools/_scratch/`

- **命名建議**（便於識別、日後清理）：
  - 前綴：`scratch-*.md`、`notes-*.md`
  - 或後綴：`*.scratch.md`、`*.notes.md`
  
- **規則**：
  - 這些檔案**不作為 CI / 語言治理的正式輸入來源**（除非在未來某個流程中明確指定）。
  - 可以 commit，但預設不視為「系統事實來源」，而是「思考/設計痕跡」。
  - 若 scratch 演化成熟、內容穩定，應：
    - 升級為正式文件（移到 `docs/` 正式路徑），或
    - 抽象成 YAML / schema / 配置，交給治理系統管理。

### 4. 舊程式資產（Legacy Code Assets）

> 這一類是「舊 code / 舊模板 / 舊配置」，用來解構與比對，但不應長期留在專案裡。

- **實際暫存目錄**：
  - `docs/refactor_playbooks/_legacy_scratch/`
  
- **規則**：
  - `_legacy_scratch/` 應在 `.gitignore` 中排除，只保留 `.gitkeep`。
  - 舊程式檔案僅在重構期間暫存，完成集成與新實作後，必須刪除。
  - 舊資產的「知識層」透過：
    - `01_deconstruction/legacy_assets_index.yaml`（定義 legacy_asset_id → 來源 repo / ref / 描述）
    - `03_refactor/*_refactor.md` 檔頭中的 `legacy_assets` 欄位
    來保留，而不是靠原始檔案本身。

### 5. Scratch 空間管理建議

**定期清理流程**：

- 建議每隔 1-2 個月檢視 `*/_scratch/` 目錄
- 識別超過 60 天未更新的檔案
- 決策：
  - 升級為正式文件
  - 歸檔到 `docs/archive/`
  - 刪除已過時內容

**Scratch 檔案模板**：

參考 `templates/SCRATCH_NOTES_TEMPLATE.md` 作為起點，保持一致性。

---

最後更新：2025-12-06
