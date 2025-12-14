# Refactor Playbook: governance

**Generated:** 2025-12-07T06:55:01.446758  
**Cluster Score:** 0  
**Status:** Draft (LLM generation required for complete playbook)

---

## 1. Cluster 概覽

**Cluster Path:** `governance`  
**Current Status:** 需要重構與語言治理改進

這個 cluster 在 Unmanned Island System 中的角色：
- 路徑位置：governance
- 違規數量：0
- Hotspot 檔案：1
- 安全問題：0

---

## 2. 問題盤點

### 語言治理違規 (0)

✅ 無語言治理違規

### Hotspot 檔案 (1)

- **governance/audit/checker.rb** (score: 55)

### Semgrep 安全問題 (0)

✅ 無安全問題


---

## 3. 語言與結構重構策略

**注意：** 此部分需要使用 LLM 生成完整建議。

預期內容：
- 語言層級策略（保留/遷出語言）
- 目錄結構優化建議
- 語言遷移路徑

---

## 4. 分級重構計畫（P0 / P1 / P2）

**注意：** 此部分需要使用 LLM 生成具體行動計畫。

### P0（24–48 小時內必須處理）
- 待 LLM 生成

### P1（一週內）
- 待 LLM 生成

### P2（持續重構）
- 待 LLM 生成

---

## 5. 適合交給 Auto-Fix Bot 的項目

**可自動修復：**
- 待 LLM 分析

**需人工審查：**
- 待 LLM 分析

---

## 6. 驗收條件與成功指標

**語言治理目標：**
- 違規數 < 5
- 安全問題 HIGH severity = 0
- Cluster score < 20

**改善方向：**
- 待 LLM 生成具體建議

---

## 7. 檔案與目錄結構（交付視圖）

### 受影響目錄

- governance

### 結構示意（變更範圍）

```
governance
├── _scratch/
│   ├── .gitkeep
│   └── README.md
├── audit/
│   ├── append-only-log-client.js
│   └── format.yaml
├── deployment/
│   └── matechat-services.yml
├── environment-matrix/
│   ├── LANGUAGE_DIMENSION_MAPPING.md
│   └── module-environment-matrix.yml
├── policies/
│   ├── conftest/
│   │   ├── matechat-integration/
│   │   └── naming_policy.rego
│   ├── base-policies.yaml
│   ├── base-policy.yaml
│   ├── ci-policy-gate.yaml
│   ├── cli-safe-mode.rego
│   └── manifest-policies.rego
├── registry/
│   ├── module-A.yaml
│   ├── module-contracts-l1.yaml
│   ├── schema.json
│   └── services.yaml
├── rules/
│   └── language-policy.yml
├── sbom/
│   ├── docs-provenance.json
│   ├── provenance.json
│   ├── signing-policy.yml
│   └── synergymesh.spdx.json
├── schemas/
│   ├── mndoc/
│   │   ├── entity-component-collection.schema.json
│   │   ├── entity-component.schema.json
│   │   ├── entity-configuration.schema.json
│   │   ├── entity-governance.schema.json
│   │   ├── entity-subsystem.schema.json
│   │   ├── entity-system.schema.json
│   │   ├── knowledge-graph.schema.json
│   │   ├── mapping-rules.schema.json
│   │   ├── mndoc-index.schema.json
│   │   └── mndoc.schema.json
│   ├── ai-constitution.schema.json
│   ├── auto-fix-bot-v2.schema.json
│   ├── cloud-agent-delegation.schema.json
│   ├── code-analysis.schema.json
│   ├── dependencies.schema.json
│   ├── docs-index.schema.json
│   ├── environment.schema.json
│   ├── osv-advisory.schema.json
│   ├── repair.schema.json
│   ├── safety-mechanisms.schema.json
│   ├── virtual-experts.schema.json
│   └── vulnerability.schema.json
├── README.md
├── ai-refactor-suggestions.md
├── hotspot-data.json
├── language-governance-report.md
├── mapping-rules.yaml
├── migration-flow.json
├── sankey-data.json
└── semgrep-report.json
```

### 檔案說明

- `governance/README.md` — 說明文檔
- `governance/_scratch/README.md` — 說明文檔
- `governance/policies/conftest/matechat-integration/README.md` — 說明文檔

---

## 如何使用本 Playbook

1. **立即執行 P0 項目**：處理高優先級問題
2. **規劃 P1 重構**：安排一週內執行
3. **持續改進**：納入 P2 到長期技術債計畫
4. **交給 Auto-Fix Bot**：自動化可修復項目
5. **人工審查**：關鍵架構調整需要工程師參與

