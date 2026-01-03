# 🧭 架構現況診斷與整合路徑 | Reality Check & Remediation

> 針對「架構完成但實際無用」「治理目錄混亂」「整體邏輯不清晰」「完成定義模糊」四大問題，提供可執行的修復方案與驗證標準。

## 1. 問題診斷 (Diagnosis)

- **虛假完成度**：模組在 README 標註 ✅，但未在下列檔案被引用或啟用，缺乏運行證據與遙測 (telemetry)。
  - `machinenativeops.yaml`
  - `config/governance/system-manifest.yaml`
  - `config/governance/system-module-map.yaml`
- **來源分裂**：`src/governance/`、`config/governance/`、根層 `governance/` 並存，缺少單一入口 (routing) 與命名規則，導致團隊不知道正確存放地。
- **邏輯斷裂**：SynergyMesh Core / Structural Governance / Autonomous / Build & Deployment / Island AI 五大塊缺少統一路徑，模組互相獨立、無依存關係圖或啟用狀態。
- **完成定義缺失**：沒有統一定義何時可以宣稱「Production Ready」，缺少測試覆蓋、SLO、運行證明、維運責任與觀測數據。

## 2. 架構重整建議 (Layered Re-organization)

- **單一事實來源 (SoT)**：以 `machinenativeops.yaml` → `config/governance/system-manifest.yaml` → `config/governance/system-module-map.yaml` 為唯一啟用鏈路，其他文檔只能引用，不得脫離此鏈。
- **分層對照 (路徑/責任)**：
  - **SynergyMesh Core** → `src/core/` (運行時服務)；對應 manifest 條目 `core.*`
  - **Structural Governance** → `src/governance/` (維持政策/維度/OPA 測試)；對應 manifest 條目 `governance.*`
  - **Autonomous Framework** → `src/automation/` (自主骨架/無人機)；對應 manifest 條目 `automation.*`
  - **Build & Deployment** → `scripts/`, `docs/architecture/DEPLOYMENT_INFRASTRUCTURE.md`，CI/CD 清單在 `.github/`；對應 manifest 條目 `build.*`
  - **Island AI Multi-Agent** → `src/governance/30-agents/` + `src/ai/`；對應 manifest 條目 `agents.*`
- **依存關係呈現**：以 `config/governance/system-module-map.yaml` 作為目錄映射，任何新模組必須先寫入此檔，再落地程式碼/政策。

## 3. Governance 目錄統一規則 (Directory Conventions)

- **主存放區**：`src/governance/` → 原始政策、維度、測試、腳本；所有新增治理資產必須先放此處。
- **環境/租戶配置**：`config/governance/` → 租戶/環境/拓撲/系統清單 (manifest、module-map、tenant-tier)；不得存放原始政策檔。
- **分發工件/落地策略**：根層 `governance/` → 發佈給 Gatekeeper/OPA/管線的策略包 (e.g., `governance/policies/**`)；只存放由 src 產出的成品或同步副本。
- **路由原則**：
  - 新治理檔 → `src/governance/`，在 `config/governance/system-module-map.yaml` 登記來源。
  - 部署/同步時才複製到根層 `governance/`，並在 `src/governance/scripts/routing-config.yaml`（如需）登記。
  - 停用或重構時，在 manifest 標記 `status: deprecated` 並移除根層副本，避免「有等於沒有」的僵屍策略。

## 4. 「完成 (Production Ready)」統一定義

要標註 ✅，必須同時滿足：

- **啟用證據**：在 `machinenativeops.yaml` + `config/governance/system-manifest.yaml` 標記 `status: PRODUCTION_READY`，並於 `config/governance/system-module-map.yaml` 對應條目非 `planning/keep` 類型（如 `infrastructure-ready` 或實際運行狀態）。
  `config/governance/system-manifest.yaml`

  ```yaml
  governance:
    vision_strategy:
      status: "PRODUCTION_READY"
  ```

  `config/governance/system-module-map.yaml`

  ```yaml
  root_directory_restructuring:
    status: "planning"
  hidden_directories_policy:
    - path: "config/"
      status: "keep"
    - path: ".github/"
      status: "keep"
    - path: ".refactor-backups/"
      status: "keep"
  ```

- **測試**：對應單元/整合/政策測試存在並可運行（含 OPA rego 測試或語言原生測試），測試路徑於 module-map 註記。
- **觀測性**：定義 SLO/SLA 指標、健康探針或遙測 (telemetry) 事件 (e.g., `src/governance/40-self-healing/monitoring/*` 或對應服務的 metrics)。
- **運維責任**：明確 owner、runbook、rollback 程序 (參考 [src/governance/03-change/README.md](../../src/governance/03-change/README.md), [src/governance/dimensions/45-recovery/dimension.yaml](../../src/governance/dimensions/45-recovery/dimension.yaml))。
- **交付證據**：CI/CD 工件或包（例如 `governance/policies/**`、Docker/包產物）與簽章/溯源記錄。
未達成上述條件的模組一律標記為 🚧（In Progress）而非 ✅。

## 5. 實施路徑 (Action Plan)

1) **凍結標註**：將 README 的「✅ 已完成」視為暫定聲明，需依本頁標準重新審核。  
2) **清點與對齊**：以 `module-map` 為主，逐一核對 SynergyMesh Core / Governance / Autonomous / Build / Agents 是否在 manifest 中標記 `status: PRODUCTION_READY`（或對應運行狀態），並確認 `module-map` 狀態非 `planning/keep`。  
3) **路徑統一**：將分散於 `governance*/` 的策略與文檔搬遷或同步到 `src/governance/`，僅保留根層發佈包；同步更新 routing 設定。  
4) **完成度驗證**：為每個模組補齊測試、觀測、runbook、CI 工件連結，並記錄於 manifest/module-map。  
5) **強制門檻**：在 CI 中加入（或啟用既有）policy/rego 檢查，未滿足「完成定義」的模組禁止標記 ✅。  
6) **週期性審核**：每個版本週期跑一次治理健康檢查（現有套件：`src/governance/28-tests/` 及政策測試）。檢查後更新 README 狀態。

本頁為後續整改與驗證的權威對照表；所有狀態更新請以此為基準，同步到 manifest/module-map 及 README。
