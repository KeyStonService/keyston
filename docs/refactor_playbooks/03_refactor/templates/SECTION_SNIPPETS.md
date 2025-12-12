# Section Snippets - 重構劇本章節範本

本文件提供常用的章節片段與範本，用於快速組裝重構劇本。

---

## 1. 典型 P0 任務清單

### 移除禁用語言

```markdown
### P0（24–48 小時內必須處理）

- 目標：移除所有禁用語言檔案，確保 CI 通過語言治理檢查。
- 行動項目：
  - `path/to/file.php` — **刪除**（PHP 為禁用語言）
  - `path/to/script.perl` — **刪除**（Perl 為禁用語言）
  - `path/to/template.rb` — **移動至** `_legacy_scratch/`（Ruby 待評估）
- 驗收條件：
  - 語言治理違規數 = 0
  - CI 語言治理檢查通過
```

### 修復高嚴重性安全問題

```markdown
### P0（24–48 小時內必須處理）

- 目標：修復所有 Semgrep HIGH severity 問題。
- 行動項目：
  - `services/api/auth.ts:42` — **修正** SQL injection 漏洞（使用參數化查詢）
  - `core/config/secrets.ts:15` — **移除** 硬編碼密鑰（改用環境變數）
  - `apps/web/api/upload.ts:78` — **新增** 檔案類型驗證
- 驗收條件：
  - Semgrep HIGH severity = 0
  - 所有安全掃描通過
```

### 處理阻塞性 Hotspot

```markdown
### P0（24–48 小時內必須處理）

- 目標：重構或拆分 Hotspot score > 90 的檔案。
- 行動項目：
  - `core/legacy/monolith.js` (score: 95) — **拆分為** 3 個模組
  - `services/gateway/router.ts` (score: 92) — **重構** 複雜路由邏輯
- 驗收條件：
  - 所有檔案 Hotspot score < 80
  - 單一檔案行數 < 500
```

---

## 2. 典型 P1 任務清單

### 語言遷移

```markdown
### P1（一週內完成）

- 目標：將 JavaScript 檔案遷移至 TypeScript，提升型別安全性。
- 行動項目：
  - `apps/web/utils/*.js` — **改寫為** TypeScript
  - `services/mcp/**/*.js` — **改寫為** TypeScript
  - 新增 `tsconfig.json` 配置
  - 更新 build scripts
- 驗收條件：
  - JavaScript 檔案數量減少 80%
  - 所有新增檔案必須使用 TypeScript
```

### 模組邊界調整

```markdown
### P1（一週內完成）

- 目標：清晰化模組邊界，減少跨目錄依賴。
- 行動項目：
  - `core/utils/shared.ts` — **上移至** `shared/utils/`
  - `services/gateway/auth/*` — **拆分為** 獨立 auth 服務
  - 更新所有 import 路徑
- 驗收條件：
  - 跨 domain 直接依賴減少 50%
  - 所有 shared 程式碼集中在 `shared/` 目錄
```

### 目錄結構優化

```markdown
### P1（一週內完成）

- 目標：重組目錄結構，符合 domain 分層原則。
- 行動項目：
  - 建立 `core/interfaces/` 存放公開 API 定義
  - 建立 `services/internal/` 存放內部共用邏輯
  - 移動 `legacy/` 下的可用模組到對應 domain
- 驗收條件：
  - 目錄結構符合 02_integration 劇本定義
  - 所有模組有明確的 README.md
```

---

## 3. 典型 P2 任務清單

### 技術債清理

```markdown
### P2（持續重構）

- 目標：清理技術債，改善程式碼品質。
- 行動項目：
  - 補充缺少的單元測試（目標覆蓋率 > 80%）
  - 重構複雜函式（Cyclomatic Complexity > 10）
  - 統一程式碼風格（執行 ESLint/Prettier）
  - 更新過時的依賴套件
- 驗收條件：
  - 測試覆蓋率 > 80%
  - 所有函式 Complexity < 10
  - 無 ESLint 錯誤
```

### 語言混用減少

```markdown
### P2（持續重構）

- 目標：減少不必要的語言混用，統一技術棧。
- 行動項目：
  - 評估是否可將 Shell scripts 改寫為 Python/TypeScript
  - 將簡單的 Python scripts 整合到主要服務中
  - 統一 build/deploy scripts 語言
- 驗收條件：
  - 專案主要語言數量 <= 3
  - 所有 scripts 有清晰的用途說明
```

---

## 4. Auto-Fix 範圍範本

### 可自動修復項目

```markdown
## 5. Auto-Fix Bot 可以處理的項目

### 適合 Auto-Fix 的變更

以下項目可以安全地交給 Auto-Fix Bot 自動處理：

1. **型別註解補強**
   - 為現有函式新增 TypeScript 型別註解
   - 將 `any` 型別改為具體型別
   - 新增缺少的 interface 定義

2. **Import 路徑修正**
   - 更新模組移動後的 import 路徑
   - 統一相對/絕對路徑使用
   - 移除未使用的 import

3. **格式化與風格**
   - 執行 Prettier 格式化
   - 修正 ESLint 自動可修復的問題
   - 統一縮排與換行

4. **簡單重構**
   - 變數重新命名（根據 naming convention）
   - 移除 console.log 除錯語句
   - 更新 deprecated API 使用

### 必須人工審查的變更

以下項目必須由人類工程師審查：

1. **業務邏輯變更**
   - 修改演算法或計算邏輯
   - 變更資料流向
   - 調整錯誤處理策略

2. **API 合約變更**
   - 修改公開 API 簽名
   - 變更 gRPC/REST endpoint
   - 調整資料結構

3. **安全相關變更**
   - 修改認證/授權邏輯
   - 變更加密方法
   - 調整安全邊界

4. **架構決策**
   - 新增或移除依賴
   - 變更模組邊界
   - 調整部署架構
```

---

## 5. 驗收條件範本

### 語言治理指標

```markdown
## 6. 驗收條件與成功指標

### 語言治理指標

| 指標            | 當前值 | 目標值 | 驗證方式                   |
| --------------- | ------ | ------ | -------------------------- |
| 語言違規數      | 25     | <= 2   | `npm run governance:check` |
| 禁用語言檔案    | 5      | 0      | 手動檢查 + CI              |
| JavaScript 檔案 | 120    | <= 30  | `find . -name "*.js"`      |
| Hotspot 檔案    | 15     | <= 5   | 檢視 hotspot.json          |
```

### 安全指標

```markdown
### 安全指標

| 嚴重性 | 當前數量 | 目標數量 | 驗證方式     |
| ------ | -------- | -------- | ------------ |
| HIGH   | 3        | 0        | Semgrep 掃描 |
| MEDIUM | 12       | <= 5     | Semgrep 掃描 |
| LOW    | 28       | <= 15    | Semgrep 掃描 |
```

### 架構指標

```markdown
### 架構指標

- **模組邊界**：所有跨 domain import 必須透過公開 interface
- **依賴方向**：禁止 apps/ 直接依賴 core/ 內部模組
- **API 穩定性**：公開 API 變更需有 deprecation notice
- **測試覆蓋率**：關鍵模組測試覆蓋率 > 80%
```

---

## 6. 檔案結構範本

### 標準 Tree 格式

````markdown
## 7. 檔案與目錄結構（交付視圖）

### 受影響目錄

- `core/unified_integration/`
- `core/mind_matrix/`
- `core/safety_mechanisms/`

### 結構示意（重構後）

\```text core/ ├─ unified_integration/ │ ├─ src/ │ │ ├─
cognitive_processor.ts # 認知處理器主入口 │ │ ├─
service_registry.ts # 服務註冊表 │ │ └─ config_optimizer.ts # 配置優化器 │ ├─
tests/ # 單元測試 │ ├─ README.md # 模組說明 │ └─ package.json # 依賴定義 ├─
mind_matrix/ │ ├─ src/ │ │ ├─ ceo_system.ts # CEO 執行長系統 │ │ └─
multi_agent_hypergraph.ts # 多代理超圖 │ └─ README.md └─ safety_mechanisms/ ├─
src/ │ ├─ circuit_breaker.ts # 斷路器 │ ├─ emergency_stop.ts # 緊急停止 │ └─
rollback_system.ts # 回滾系統 └─ README.md \```

### 關鍵檔案說明

- **cognitive_processor.ts** - 四層認知架構的核心實作（感知→推理→執行→證明）
- **service_registry.ts** - 服務發現與健康監控入口
- **ceo_system.ts** - 決策引擎與幻覺偵測整合點
- **circuit_breaker.ts** - 保護機制，防止級聯失效
````

---

## 7. 集成對齊範本

```markdown
## 8. 集成對齊（Integration Alignment）

### 上游依賴

本 cluster 依賴以下上游服務：

| 服務                    | 介面類型          | 用途           |
| ----------------------- | ----------------- | -------------- |
| `core/contract_service` | gRPC              | 合約驗證與執行 |
| `governance/schemas`    | JSON Schema       | 型別定義與驗證 |
| `shared/utils`          | TypeScript Module | 共用工具函式   |

### 下游使用者

本 cluster 被以下下游服務使用：

| 服務                   | 介面類型      | 使用方式         |
| ---------------------- | ------------- | ---------------- |
| `apps/web`             | REST API      | 前端呼叫業務邏輯 |
| `services/agents`      | Event Bus     | 訂閱狀態變更事件 |
| `automation/architect` | Direct Import | 讀取架構元資料   |

### 集成步驟

重構需按以下順序進行，確保不破壞現有整合：

1. **Phase 1**：更新 interface 定義（不破壞現有 API）
   - 新增 TypeScript interface 定義
   - 部署到測試環境
   - 執行整合測試

2. **Phase 2**：遷移內部實作
   - 重構內部邏輯
   - 保持 API 相容性
   - 執行回歸測試

3. **Phase 3**：清理 deprecated API
   - 標記舊 API 為 deprecated
   - 通知下游使用者
   - 設定 sunset 日期（例如：30 天後移除）

### 回滾策略

若重構失敗，按以下步驟回滾：

1. 切換 feature flag：`ENABLE_NEW_INTEGRATION=false`
2. 回滾到前一個穩定版本：`git checkout {stable_tag}`
3. 重新部署：`./deploy.sh rollback`
4. 驗證所有下游服務正常運作

### 風險管控

- **Branch 策略**：使用 feature branch + PR review
- **Feature Flag**：所有 breaking changes 需有 feature flag 保護
- **Canary Deployment**：先部署到 10% 流量觀察
- **監控告警**：設定關鍵指標告警（error rate, latency）
```

---

## 8. 使用範例

### 組裝一個完整劇本

1. 從 `REFRACTOR_PLAYBOOK_TEMPLATE.md` 複製基礎結構
2. 填入檔頭資訊（Cluster ID, 對應目錄等）
3. 從本文件選擇適合的 section snippets
4. 根據實際情況調整細節
5. 更新 `index.yaml` 和 `INDEX.md`

### 快速生成範例

```bash
# 使用腳本生成劇本框架
python tools/generate-refactor-playbook.py \
  --cluster "core/architecture-stability" \
  --domain "core" \
  --include-snippets
```

---

最後更新：2025-12-06
