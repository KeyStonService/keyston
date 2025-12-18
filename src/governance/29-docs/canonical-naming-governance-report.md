# Canonical Naming Governance v1.0 | 單一權威命名治理研究報告

## 🎯 Purpose 目的
- 將上傳的「Canonical Naming Governance v1.0」內容落地為可執行規範。
- 建立單一權威 machine-spec，支援 URN/URI、Gatekeeper、CI/Conftest、Kubeval 與遷移腳本。
- 先對現有目錄給出對齊的 canonical 命名方案（不強制立即改名），確保後續自動化驗證有依據。

## 📌 Machine-Spec 單一權威配置
- 來源：`governance/34-config/naming/canonical-naming-machine-spec.yaml`
- 核心規則：
  - `allowed_chars: [a-z0-9-]`，`case: lower`，`max_length: 63`
  - `segments: [domain, component, environment, region, version, suffix]`
  - `environments: [dev, test, staging, prod, learn, sandbox]`
  - `reserved_tokens: [core, internal, system, legacy, experimental]`
  - `canonical_regex`: 參見 `governance/34-config/naming/canonical-naming-machine-spec.yaml` (`naming.canonical_regex`，含 `--` 禁止與 team/tenant/環境/sandbox 前綴，長度 ≤ 63)
  - 必要標籤：`environment`, `tenant`, `app.kubernetes.io/managed-by`
  - URN 模板：`urn:axiom:{domain}:{component}:env:{environment}:{version}`
  - Segment → URN：`domain->{domain}`、`component->{component}`、`environment->{environment}`、`version->{version}`、`region->qualifier:region`、`suffix->suffix_map.*`

## 🗂️ Directory Canonical Mapping (non-disruptive)
| Path | Canonical name (regex compliant) | URN sample | Notes |
| --- | --- | --- | --- |
| `governance/23-policies` | `dev-governance-policies` | `urn:axiom:governance:policies:env:dev:v1` | 與 Gatekeeper / Conftest 政策對齊，標記 `managed-by=axiom-naming-controller` |
| `governance/33-common` | `dev-governance-common` | `urn:axiom:governance:common:env:dev:v1` | 共用 Rego/schema/工具，保留 `tenant=platform` |
| `core/contract_service/contracts-L1/contracts` | `dev-core-contracts-l1-service` | `urn:axiom:core:contracts-l1:env:dev:v1` | 路徑驗證/自我修復模組，後綴採 `service` |
| `services/scheduler-service` | `dev-scheduler-service` | `urn:axiom:platform:scheduler:env:dev:v1` | 對應排程服務，可映射 `suffix_map.deployment` |

> 說明：表格提供「推薦 canonical 名稱」與 URN 樣板，先用於 labels/annotations 與 CI 驗證，不強迫立即改動實體目錄，避免破壞既有引用。

## 🔐 Enforcement / 驗證流程
- **Admission**：Gatekeeper 使用 machine-spec 中 `K8sRequiredLabels`、`K8sNamingPattern` 參數，`failurePolicy: Fail`。
- **CI**：`conftest`/`yamllint`/`kubeval` 讀取 machine-spec，阻擋不符 regex 或缺標籤的 manifest（`naming_policy.rego` 已改為 canonical regex）。
- **URN/URI**：Annotations `axiom.io/canonical-urn`、`axiom.io/qualifiers` 由機器生成，確保與 labels 一致。
- **Prefix/Env 對齊**：若名稱以 machine-spec 定義的環境前綴起始，必須與 `environment` 標籤值一致以避免衝突。
- **映射檔**：`governance/34-config/naming/namespace-mapping.yaml` 提供舊 namespace → canonical → URN/labels 的轉換表（含 unmanned-island-system、axiom-system、island-ai、uav/ad-production 等），供遷移腳本/工具套用。

## 🛠️ Migration & Acceptance / 遷移與驗收
- 遷移策略：`warn-and-plan`，先輸出 `reports/canonical-naming-mapping.csv`（dry-run），標示高/中/低風險。
- 驗收條件：
  - 目錄與資源命名可被 `canonical_regex` 驗證通過。
  - 必要 labels 存在且與 URN 對齊（environment/tenant/managed-by）。
  - Gatekeeper + CI (conftest/kubeval) 同步採用 machine-spec 參數，無規則漂移。
