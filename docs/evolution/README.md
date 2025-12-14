# 🧬 System Evolution 子系統

本子系統的目標是讓 **Unmanned Island System** 能夠：

1. 明確宣告「自己想變成什麼樣」
2. 定期量測「目前距離目標有多遠」
3. 輸出「高階演化建議」，供 Refactor Playbooks、Auto-Fix Bot 與人類架構師使用

---

## 組成元件

- `config/system-evolution.yaml`
  - 定義演化目標（objectives）、約束（constraints）、指標來源（metrics_sources）、報告輸出位置（outputs）。

- `tools/evolution/generate_evolution_report.py`
  - 掃描：
    - `governance/language-governance-report.md`
    - `governance/semgrep-report.json`
    - `apps/web/public/data/cluster-heatmap.json`
    - `docs/refactor_playbooks/03_refactor/**`
  - 產生：
    - `knowledge/evolution-state.yaml`
    - `docs/SYSTEM_EVOLUTION_REPORT.md`

- `.github/workflows/system-evolution.yml`
  - 在 push / 排程時自動執行報告生成流程。

---

## 介面與下游使用者

- 給 **AI Refactor Agents / Monica / GPT**：
  - 請優先讀取：
    - `knowledge/evolution-state.yaml`（機器可讀現狀）
    - `docs/SYSTEM_EVOLUTION_REPORT.md`（高階人類摘要）
  - 依據其中「分數最低的 objective」與「建議區塊」，決定下一個要優先處理的 cluster / module。

- 給 **03_refactor Playbooks**：
  - 可將 System Evolution Report 中的「高風險 cluster」對應到：
    - `docs/refactor_playbooks/03_refactor/<domain>/*_refactor.md`
  - 確保所有高風險區域至少有一份 Playbook。

---

## 下一步建議

短期：
- 先讓 pipeline 穩定執行（報告成功產出即可），不必馬上自動 commit。
- 視實際情況調整 `config/system-evolution.yaml` 中的目標與權重。

長期：
- 在工具層接上 AI，用 evolution-state.yaml 作為輸入，產出更細緻的重構計畫與 Auto-Fix PR。
- 將「演化目標」擴充到成本、可靠性、延遲等維度。
