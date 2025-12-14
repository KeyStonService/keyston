# Refactor Playbook: tools

**Generated:** 2025-12-07T06:55:01.555366  
**Cluster Score:** 0  
**Status:** Draft (LLM generation required for complete playbook)

---

## 1. Cluster 概覽

**Cluster Path:** `tools`  
**Current Status:** 需要重構與語言治理改進

這個 cluster 在 Unmanned Island System 中的角色：
- 路徑位置：tools
- 違規數量：0
- Hotspot 檔案：1
- 安全問題：0

---

## 2. 問題盤點

### 語言治理違規 (0)

✅ 無語言治理違規

### Hotspot 檔案 (1)

- **tools/scripts/helper.js** (score: 50)

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

- tools

### 結構示意（變更範圍）

```
tools
├── _scratch/
│   ├── .gitkeep
│   └── README.md
├── ci/
│   ├── contract-checker.js
│   ├── language-checker.js
│   └── policy-simulate.yml
├── cli/
│   ├── bin/
│   │   └── admin-copilot.js
│   ├── src/
│   │   └── index.ts
│   ├── README.md
│   ├── package-lock.json
│   ├── package.json
│   └── tsconfig.json
├── docs/
│   ├── generate_knowledge_graph.py
│   ├── generate_mndoc_from_readme.py
│   ├── pr_comment_summary.py
│   ├── project_to_superroot.py
│   ├── provenance_injector.py
│   ├── scan_repo_generate_index.py
│   └── validate_index.py
├── evolution/
│   └── generate_evolution_report.py
├── governance/
│   ├── check-language-policy.py
│   ├── generate-consolidated-report.py
│   └── language-governance-analyzer.py
├── scripts/
│   ├── artifacts/
│   │   └── build.sh
│   ├── backup/
│   │   ├── backup.sh
│   │   └── restore.sh
│   ├── naming/
│   │   ├── check-naming.sh
│   │   ├── language-checker.mjs
│   │   └── suggest-name.mjs
│   ├── README.md
│   ├── advanced-push-protection.sh
│   ├── analyze.sh
│   ├── automation-entry.sh
│   ├── build-matrix.sh
│   ├── check-env.sh
│   ├── check-sync-contracts.js
│   ├── conditional-deploy.sh
│   ├── generate-directory-tree.sh
│   ├── manage-secret-patterns.py
│   ├── repair.sh
│   ├── run-v2.sh
│   ├── setup.sh
│   ├── validate-config.js
│   ├── validate_auto_fix_bot_config.py
│   └── vulnerability-alert-handler.py
├── utilities/
│   ├── validate_vectors.py
│   └── validate_yaml.py
├── README.md
├── ai-auto-fix.py
├── ai-refactor-review.py
├── bootstrap_from_manifest.py
├── ci-cost-dashboard.py
├── generate-hotspot-heatmap.py
├── generate-language-dashboard.py
├── generate-migration-flow.py
├── generate-refactor-playbook.py
├── generate-sankey-data.py
├── language-dashboard-data.yaml
├── language-health-score.py
└── ... (6 more items)
```

### 檔案說明

- `tools/README.md` — 說明文檔
- `tools/scripts/README.md` — 說明文檔
- `tools/cli/README.md` — 說明文檔
- `tools/cli/package.json` — Node.js 專案配置
- `tools/cli/tsconfig.json` — TypeScript 編譯配置
- `tools/_scratch/README.md` — 說明文檔
- `tools/cli/src/index.ts` — 模組入口點

---

## 如何使用本 Playbook

1. **立即執行 P0 項目**：處理高優先級問題
2. **規劃 P1 重構**：安排一週內執行
3. **持續改進**：納入 P2 到長期技術債計畫
4. **交給 Auto-Fix Bot**：自動化可修復項目
5. **人工審查**：關鍵架構調整需要工程師參與

