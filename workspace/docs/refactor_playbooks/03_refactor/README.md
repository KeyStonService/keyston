# 03_refactor：重構劇本層（Refactor Playbook Layer）

> 本目錄是 **Unmanned Island System 語言治理與架構重構的「最後一層控制平面」**，  
> 每一個檔案都是一份「可派工、可 Auto-Fix、可審計」的重構任務說明書。

---

## 1. 角色與定位

`03_refactor` 是整個重構系統的第三層，對應以下三階段流程的「重構」階段：

1. `01_deconstruction/`：**解構（Deconstruction）**  
   - 分析舊世界：舊架構、舊程式碼、舊語言堆疊、舊 anti-pattern。  
   - 產出：各 cluster 的解構劇本（\*_deconstruction.md）與 `legacy_assets_index.yaml`。

2. `02_integration/`：**集成（Integration）**  
   - 設計新世界的「組合方式」：語言層級、模組邊界、API / 契約、跨 cluster 接線。  
   - 產出：各 cluster / 子系統的集成劇本（\*_integration.md）。

3. `03_refactor/`：**重構（Refactor）** ← 本目錄  
   - 將「解構 + 集成」的設計，轉換為 **可執行的重構計畫**：  
     - P0 / P1 / P2 行動清單  
     - Auto-Fix Bot 可以處理的項目  
     - 必須人工審查的項目  
     - 目錄與檔案結構的最終形狀  
   - 產出：各 cluster 的重構劇本（\*_refactor.md），由 CI / Bot / 人類工程師共同遵守。

---

## 2. 舊資產與三層目錄的關係

舊程式碼 / 舊模板等「Legacy Assets」**不屬於最終系統的一部分**，只在重構過程中短暫存在：

```text
docs/refactor_playbooks/
  _legacy_scratch/                          # 🧨 舊資產暫存工作區（不進 git）
    .gitkeep                                #    只保留這個；實際舊檔一律由 .gitignore 排除

  01_deconstruction/                        # 🟠 解構劇本（描述舊世界）
    legacy_assets_index.yaml                #    舊資產索引：legacy_asset_id → 來源 repo / ref / 描述
    core__architecture_deconstruction.md    #    core/architecture-stability 的舊架構解構說明
    services__gateway_deconstruction.md     #    services/gateway 的舊設計解構說明
    ...

  02_integration/                           # 🔵 集成劇本（設計新世界）
    core__architecture_integration.md       #    core/ 如何在新架構下與其他模組整合
    services__gateway_integration.md        #    gateway 與 core/apps/web/外部服務的接線方案
    ...

  03_refactor/                              # ✅ 重構劇本層（本目錄）
    ...                                     #    依 cluster/domain 分組的最終重構計畫
```

**舊資產生命週期規則：**

- 真實舊檔案只允許暫存在 `_legacy_scratch/` 中，用於解構與比較。
- `_legacy_scratch/` 受 `.gitignore` 保護，**任何實際程式檔不得被 commit**。
- 一旦新的實作已寫入正式目錄（例如 `core/`, `services/`,
  `automation/`），對應舊資產必須從 `_legacy_scratch/` 刪除。
- 舊資產的「知識層」則透過：
  - `01_deconstruction/legacy_assets_index.yaml`（ID + 來源 + 描述）
  - `03_refactor/*_refactor.md` 檔頭中的 `legacy_assets`
    欄位保留追溯關係，而不是保留原始檔案。
  對應舊資產必須從 `_legacy_scratch/` 刪除。
- 舊資產的「知識層」則透過：


---

## 3. 目錄結構與用途說明

```text
docs/
  refactor_playbooks/
    03_refactor/
      README.md                             # 本說明文件
      INDEX.md                              # 人類可讀索引：列出所有重構劇本與狀態
      index.yaml                            # 機器可讀索引：cluster_id → 各種檔案路徑與 legacy IDs

      templates/                            # 🎭 劇本模板與共用片段
        REFRACTOR_PLAYBOOK_TEMPLATE.md      # 單一 cluster 的標準重構劇本模板
        SECTION_SNIPPETS.md                 # 常用章節片段（P0/P1/P2 行動範本、驗收條件等）
        META_CONVENTIONS.md                 # 命名規範：檔名格式、Cluster ID 規則、目錄對應

      core/                                 # core/ 相關重構劇本（核心平台服務）
        core__architecture_refactor.md      # core/architecture-stability 重構計畫
        core__safety_mechanisms_refactor.md # core/safety_mechanisms 安全機制重構
        core__slsa_provenance_refactor.md   # core/slsa_provenance 溯源/簽名重構

      services/                             # services/ 後端服務與 gateway
        services__gateway_refactor.md       # services/gateway API/邊界/語言重構
        services__agents_refactor.md        # services/agents 長生命週期代理服務重構
        services__contract_service_refactor.md # 合約服務相關重構（contracts-L1 等）

      automation/                           # automation/ 自動化模組
        automation__autonomous_refactor.md  # 五骨架自主系統重構計畫
        automation__architect_refactor.md   # 架構分析/修復重構
        automation__hyperautomation_refactor.md # 超自動化策略重構

      apps/                                 # 前端 / CLI / Web App 層
        apps__web_refactor.md               # apps/web（前端 + 代碼分析 API）重構計畫
        apps__admin_cli_refactor.md         # Admin Copilot CLI 等應用重構

      governance/                           # 治理與策略自身的重構
        governance__schemas_refactor.md     # JSON Schema / SuperRoot 命名空間重構
        governance__policies_refactor.md    # OPA / Conftest 策略重構
        governance__language_pipeline_refactor.md # 語言治理 pipeline（CodeQL / Semgrep 等）重構

      infra/                                # 基礎設施層
        infra__kubernetes_refactor.md       # K8s 部署與結構重構
        infra__monitoring_refactor.md       # 監控與告警重構
        infra__drift_detection_refactor.md  # 漂移偵測與修復流程重構

      knowledge/                            # 活體知識庫相關重構
        knowledge__living_kb_refactor.md    # knowledge/ + runtime/ + pipelines/ 整體重構計畫

      meta/                                 # 03_refactor 與其他系統的整合說明
        CI_INTEGRATION.md                   # CI / Auto-Fix Bot / 語言治理 workflow 如何使用這裡的劇本
        AI_PROMPTS.md                       # 專給 LLM / Agent 用的提示詞（產生/更新重構劇本）
```

---

## 4. index.yaml 結構（機器可讀索引）

`index.yaml` 用於讓 CI / 工具 / Agent 能夠根據 `cluster_id` 快速找到對應檔案與舊資產：

```yaml
clusters:
  - cluster_id: "core/architecture-stability"
    domain: "core"
    refactor_file: "core/core__architecture_refactor.md"
    deconstruction_file: "../01_deconstruction/core__architecture_deconstruction.md"
    integration_file: "../02_integration/core__architecture_integration.md"
    legacy_assets:
      - "core-v1-legacy-modules"        # 參照 01_deconstruction/legacy_assets_index.yaml 中的 ID

  - cluster_id: "services/gateway"
    domain: "services"
    refactor_file: "services/services__gateway_refactor.md"
    deconstruction_file: "../01_deconstruction/services__gateway_deconstruction.md"
    integration_file: "../02_integration/services__gateway_integration.md"
    legacy_assets:
      - "gateway-old-ts-templates"
```


---

## 5. 單一重構劇本必備內容

所有 `*_refactor.md` 檔案，都應由 `templates/REFRACTOR_PLAYBOOK_TEMPLATE.md` 派生，並至少包含以下區塊：

1. **檔頭：來源鏈結與基本資訊**
   - Cluster ID
   - 對應目錄（實際會被修改的目錄列表）
   - 來源鏈結（必填）：

     - 解構劇本：`01_deconstruction/..._deconstruction.md`
     - 集成劇本：`02_integration/..._integration.md`
     - 舊資產 ID 清單：對應 `legacy_assets_index.yaml` 中的 ID

2. **Cluster 概覽**

   - 在整個 Unmanned Island System 中的角色與邊界
   - 目前語言組成與健康狀態（TypeScript / Python / Go / C++ 等）

3. **問題盤點**

   - 語言治理問題彙總（language-governance-report）
   - Hotspot 檔案（hotspot.json）
   - Semgrep 安全問題（semgrep-report.json）
   - Migration Flow 觀察（migration-flow.json）

4. **語言與結構重構策略**

   - 語言層級策略（要移除/遷出/統一的語言）
   - 目錄與模組邊界調整（拆分 / 合併 / 上移 / 下沉）
   - 與集成劇本對齊的關鍵約束

5. **分級重構計畫（P0 / P1 / P2）**

   - P0（24–48 小時內）：阻塞 CI / 高風險問題
   - P1（一週內）：架構清晰化、語言統一
   - P2（持續）：技術債收斂與最佳化
   - 每個等級都應列出具體檔案與動作（刪除 / 移動 / 改寫為某語言）

6. **Auto-Fix Bot 可以處理的項目**

   - 適合全自動修復的變更範圍
   - 必須人工審查的變更範圍
   - 建議的 Auto-Fix 規則（例如只限格式/型別/路徑，不動業務邏輯）

7. **驗收條件與成功指標**

   - 語言治理指標（違規數門檻）
   - 安全指標（Semgrep HIGH/MEDIUM 上限）
   - 架構指標（是否符合 integration 劇本的邊界與 API 約束）

8. **檔案與目錄結構（交付視圖）**

   - 與本次重構相關的目錄/檔案 tree
   - 每個關鍵檔案/目錄的一行註解說明

9. **集成對齊與回滾策略**


---

## 6. 如何新增一份重構劇本（標準流程）

1. 在 `01_deconstruction/` 填寫（或確認存在）：
   - 對應 cluster 的 `*_deconstruction.md`
   - `legacy_assets_index.yaml` 中相關舊資產 ID

2. 在 `02_integration/` 撰寫對應的 `*_integration.md`：


1. 在 `03_refactor/` 中：

   1. 依 domain 選擇目錄（例如 `core/`, `services/`）
   2. 以 `REFRACTOR_PLAYBOOK_TEMPLATE.md` 為基礎，新建檔案：
      - 例如：`core__architecture_refactor.md`

      - 例如：`core__architecture_refactor.md`
   3. 檔頭填入：

      - cluster_id
      - 對應目錄
      - deconstruction_file / integration_file
      - legacy_assets IDs
   4. 依照「必備內容」填寫各章節。

2. 更新 `index.yaml` 與 `INDEX.md`：

   - 增加此 cluster 的索引條目。

3. （可選）更新 `meta/CI_INTEGRATION.md` 或 CI 設定：


---

## 7. 與 CI / Auto-Fix / Dashboard 的關係

`03_refactor/` 本身不執行任何程式碼，而是：

- CI / 語言治理 Pipeline 的「決策依據」
- Auto-Fix Bot 在動手前必須參考的「行動邊界說明書」
- Dashboard（語言治理儀表板）在顯示某個 cluster 時應同步展示的「重構計畫」

詳細整合方式請參考：

- `meta/CI_INTEGRATION.md`
- `meta/AI_PROMPTS.md`

---
