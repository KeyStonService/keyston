# Multi-Team Collaboration Models

## 模式

1. **Platform + Product Pods**：Platform 維護基礎建設；Product 擁有垂直能力。
2. **Guild / Chapter**：跨團隊能力群（Architecture Guild, Reliability Guild）。
3. **Embedded SRE**：SRE 進駐高風險產品線。

## CODEOWNERS 策略

- 依 core/、automation/、docs/ 區塊分 ownership。
- 重要檔案（synergymesh.yaml, config/*）必須由 Governance 團隊審核。

## 工具

- CODEOWNERS
- GitHub Teams + Slack 通知
- services/agents/orchestrator 自動派工

## 多儲存庫協作 / Cross-Repo Federation

1. **建立 Block 索引**：用 `config/system-module-map.yaml` 的區塊分類（core/automation/infra/docs 等）為 96 個儲存庫打上唯一歸屬，集中到同一張表（本 repo `config/` 或每週同步的 Google Sheet）。先釐清歸屬再協作，避免「誰管哪個 repo」的模糊地帶。
2. **權限與審核一致化**：每個 Block 一組 GitHub Team + CODEOWNERS；統一 Branch Protection（必須 PR、至少 1–2 reviewer、禁用直接 push）；跨 Block 變更必須有對應 Block reviewer。
3. **自動化協同**：把標準 CI/CD 封裝成 Reusable Workflow，其餘儲存庫只 `uses:` 同一份。重大基線升級時用 `repository_dispatch` 由中央 orchestrator（例如 `services/agents/orchestrator`）一次觸發，確保各 Block 同步執行測試/部署。
4. **節奏與版本對齊**：採用 Block-based Release Train（例如核心每週、前端每兩週、infra 每月），在對應時間窗口進行批次合併；若跨 Block 依賴，先在 Sandbox/Preview 環境做合併驗證再推 Production。
5. **風險控制**：維護「共用依賴白名單」與「破壞性變更日曆」，由 Governance 小組每週審視；任何跨 Block 破壞性變更需附回滾方案與相依清單。
