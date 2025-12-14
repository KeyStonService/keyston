# 自動審核與合併工作流程指南

此文件說明 `.github/workflows/auto-review-merge.yml` 的設計與使用方法，協助在組織內自動核准並合併符合條件的 Pull Request 至 `main` 分支。

## 🎯 目標

- 降低例行、低風險 PR 的人工審核成本。
- 保留必要的品質保護（測試、lint、組織成員身份）。
- 以標籤控制可自動合併的 PR，避免無意外觸發。

## ✅ 觸發條件

工作流於下列事件觸發：`opened`, `synchronize`, `reopened`, `ready_for_review`, `labeled`。
僅處理目標分支為 `main` 的 PR。

## 🧪 驗證步驟

1. 作者是否為組織成員或 repo 協作者（雙重檢查機制）。
2. 安裝依賴並執行：`lint` / `test` / `build`（腳本存在才執行）。
3. 自動送出核准（若為授權成員）。
4. 重新取得最新 PR 狀態，檢查：
   - 非 draft
   - 有 `auto-merge` 標籤
   - `mergeable_state` 不是 `blocked`
5. 若符合條件，執行 squash merge。

## 🏷️ 標籤策略

- 加上 `auto-merge` 標籤代表 PR 可被自動合併。
- 可以再新增例如：`safe-change`、`docs-only` 等標籤並擴充邏輯。

## 🔐 安全注意事項

| 風險 | 說明 | 緩解建議 |
|------|------|----------|
| fork PR 權限 | `GITHUB_TOKEN` 對 fork 來源有限制 | 避免在 fork PR 執行敏感腳本 |
| `pull_request_target` 風險 | 若改成使用可讀 base 的 context 會有權限提升風險 | 避免使用，除非有嚴格檢查 |
| 組織成員驗證 | 私有成員可能查不到 | 使用 secret `ORG_NAME` 並限制須有 `auto-merge` 標籤 |
| 惡意依賴注入 | 自動安裝依賴可能執行 postinstall | 加入 `npm audit` / 使用 lockfile / 加白名單 |
| 測試覆蓋不足 | 自動合併可能忽略邊界狀況 | 強制 coverage 閾值（CI 另行檢查） |

## 🔧 可擴充方向

- 加入 Sigstore / SLSA 驗證（整合現有 `slsa-validator.js`）。
- 只允許變更特定目錄（使用 `git diff --name-only` 檢查）。
- 加入檔案規模限制（LOC / diff size）。
- 驗證 commit 是否 GPG / OIDC 簽署。
- 加入依賴變更偵測（若 `package.json` 變更則禁止自動合併）。

## 🚀 啟用步驟

1. 設定組織或 repository secret：`ORG_NAME=<你的組織名稱>`。
2. 確認分支保護規則允許機器人核准計入所需 reviewer 數量。
3. 為欲自動合併的 PR 加上標籤 `auto-merge`。
4. （可選）設定必需的 CI 狀態檢查（tests、lint）。

## 🧩 常見問題

### 無法判斷作者是成員

- **原因**: 組織成員未公開，或使用個人 repo（無組織）。
- **解法**: Workflow 已改為同時檢查 **組織成員** 與 **repo 協作者**（需 write/admin/maintain 權限），更靈活支援個人與組織場景。

### 標籤已加但未合併

- **檢查項目**:
  1. PR 是否為 **draft** 狀態（draft 無法合併）
  2. 前面步驟是否失敗（lint/test/build）
  3. 分支保護規則是否要求額外條件（如 required status checks、required reviewers）
  4. `mergeable_state` 是否為 `blocked`（查看 Actions log）
- **解法**: 確保所有 required checks 通過、PR 非 draft、已獲得足夠審核數

### 分支保護阻擋合併

- **原因**: `main` 分支設定了嚴格保護規則（如需 2 位 reviewer、特定 status checks）
- **解法**:
  1. 在分支保護設定中，允許機器人審核計入所需數量
  2. 或降低 reviewer 要求（至少 1 位）
  3. 確保所有 required status checks 已設定並通過

## 🛡️ 建議增加的檢查（範例片段）

```yaml
      - name: 限制變更檔案路徑
        uses: actions/github-script@v7
        with:
          script: |
            const diff = await github.rest.pulls.listFiles({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.payload.pull_request.number,
              per_page: 300
            });
            const invalid = diff.data.some(f => f.filename.startsWith('core/secrets/'));
            if (invalid) core.setFailed('包含受保護路徑，禁止自動合併');
```

## 📌 後續最佳化

- 加入覆蓋率檢查：解析 Jest coverage summary。
- 整合安全掃描：OWASP Dependency Check / npm audit。
- 紀錄自動合併審計：將結果推送到內部審計系統或 issue comment。

---
如需擴充上述邏輯，提出需求即可協助調整。
