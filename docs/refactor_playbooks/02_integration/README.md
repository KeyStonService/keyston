# 02_integration：集成劇本層（Integration Playbook Layer）

> 本目錄是 **Unmanned Island
> System 重構系統的第二層**，專門用於設計「新世界」的組合方式、模組邊界與整合策略。

---

## 角色與定位

`02_integration/` 是重構流程的**中間層**，負責：

1. **介面設計**：定義清晰的 API 邊界與契約
2. **契約制定**：指定資料格式、通訊協議、錯誤處理
3. **依賴管理**：決定模組間的依賴方向與耦合度
4. **整合策略**：規劃漸進式遷移路徑
5. **邊界劃分**：明確哪些屬於這個模組，哪些不屬於

---

## 與其他層的關係

```text
01_deconstruction (分析舊世界)
    ↓
02_integration (設計新世界) ← 本層
    ↓
03_refactor (執行重構)
```

- **輸入**：解構劇本（01_deconstruction）、系統需求、架構原則
- **輸出**：集成劇本（\*\_integration.md）
- **使用者**：03_refactor 作為重構的設計依據

---

## 目錄結構

```text
02_integration/
├─ README.md                              # 本說明文件
├─ core__architecture_integration.md     # core/ 的集成劇本
├─ services__gateway_integration.md      # services/gateway 的集成劇本
└─ ...                                   # 其他 cluster 的集成劇本
```

---

## 集成劇本必備內容

每個 `*_integration.md` 應包含：

1. **邊界定義**
   - 哪些功能屬於這個模組？
   - 哪些功能不屬於（應該在其他模組）？
   - 與其他模組的交界線在哪裡？

2. **介面規格**
   - **API Signature**：函式簽名、參數、回傳值
   - **資料格式**：JSON Schema、Protocol Buffers、TypeScript interfaces
   - **通訊協議**：REST、gRPC、Event Bus、直接 import
   - **錯誤處理**：錯誤碼定義、異常傳播策略

3. **依賴策略**
   - **上游依賴**：本模組依賴哪些其他模組？
   - **下游使用者**：哪些模組依賴本模組？
   - **依賴方向**：確保依賴單向流動（避免循環依賴）
   - **耦合度控制**：如何最小化耦合？

4. **遷移步驟**
   - **從舊架構到新架構的路徑**
   - **Phase 1, 2, 3... 的具體步驟**
   - **每個階段的驗證方式**
   - **向後相容性策略**

5. **整合測試**
   - 如何驗證集成是否正確？
   - 需要哪些測試場景？
   - 效能與可靠性指標

---

## 設計原則

### 1. 單向依賴

```text
✅ 正確的依賴方向
apps/ → services/ → core/ → shared/

❌ 錯誤的依賴（循環）
core/ ← services/ → core/
```

### 2. 介面隔離

- 公開介面應該明確、穩定、文件完整
- 內部實作可以隨時重構，不影響使用者

### 3. 契約優先

- 在開始實作前，先定義好介面契約
- 契約變更需要有 deprecation 流程

### 4. 漸進式遷移

- 避免 big-bang 式重構
- 使用 feature flag、adapter pattern 支援漸進遷移

---

## 如何新增集成劇本

1. **參考解構劇本**
   - 閱讀對應的 `01_deconstruction/*_deconstruction.md`
   - 理解舊架構的問題與限制

2. **設計新架構**
   - 定義模組邊界
   - 設計公開介面
   - 規劃依賴關係

3. **撰寫集成劇本**
   - 建立 `{domain}__{cluster}_integration.md`
   - 按照標準格式填寫各章節
   - 提供具體的 API 範例與測試場景

4. **審查與迭代**
   - 與團隊討論設計
   - 驗證依賴方向是否正確
   - 確認遷移步驟可行

5. **關聯到重構層**
   - 在 `03_refactor/` 的對應劇本中引用本集成劇本
   - 確保重構計畫符合集成設計

---

## 集成劇本範例結構

````markdown
# {cluster} 集成劇本（Integration Playbook）

## 1. 模組邊界定義

- 屬於本模組的職責
- 不屬於本模組的職責
- 與其他模組的交界

## 2. 公開介面規格

### API Endpoints

\```typescript interface UserService { getUser(id: string): Promise<User>;
createUser(data: CreateUserRequest): Promise<User>; } \```

### 資料格式

\```json { "user": { "id": "string", "name": "string" } } \```

### 通訊協議

- REST API: `GET /api/users/:id`
- gRPC: `UserService.GetUser`

## 3. 依賴關係

### 上游依賴

- core/auth: 認證與授權
- core/database: 資料存取層

### 下游使用者

- apps/web: 前端呼叫
- services/notifications: 通知服務

### 依賴方向圖

\```text apps/web → services/users → core/auth → core/database \```

## 4. 遷移策略

### Phase 1: 建立新介面

- 新增 API endpoints
- 保持舊介面運作

### Phase 2: 漸進遷移使用者

- 前端逐步切換到新 API
- 使用 feature flag 控制

### Phase 3: 下線舊介面

- 標記舊 API 為 deprecated
- 30 天後移除

## 5. 整合測試

### 測試場景

- [ ] 正常流程測試
- [ ] 錯誤處理測試
- [ ] 效能測試
- [ ] 相容性測試

### 驗收條件

- API 回應時間 < 100ms
- 錯誤率 < 0.1%
- 所有下游服務正常運作
````

---

## 最佳實踐

### ✅ 應該做的

- **明確邊界**：清楚定義「什麼屬於我」「什麼不屬於我」
- **契約優先**：先定義介面，再實作
- **文件完整**：所有公開介面要有範例與說明
- **測試驅動**：先寫整合測試，再實作介面
- **漸進遷移**：提供向後相容性與遷移路徑

### ❌ 不應該做的

- 不要在集成劇本中寫實作細節（那是 03_refactor 的事）
- 不要忽略向後相容性
- 不要設計複雜的介面（保持簡單）
- 不要忘記考慮錯誤處理與邊界情況

---

## 與 03_refactor 的協作

集成劇本產出的設計，在 `03_refactor/` 中會轉換為：

- **P0/P1/P2 任務**：具體實作步驟
- **Auto-Fix 範圍**：哪些可以自動化
- **驗收條件**：如何驗證集成是否成功

---

## 🎯 Active Integration Projects / 進行中的集成專案

### ✅ Baseline YAML Integration (COMPLETED P0)

**Project:** Integration of 6 baseline YAML files from `_legacy_scratch` to
production locations

**Documentation:**

- 📋 [Integration Plan](./BASELINE_YAML_INTEGRATION_PLAN.md) - Comprehensive
  plan with 44 action items
- 📊 [P0 Completion Report](./P0_COMPLETION_REPORT.md) - Detailed metrics and
  analysis

**Status:** P0 Complete (8/8 critical files integrated)

**Key Deliverables:**

- ✅ Governance policies (namespace naming, RBAC, audit, compliance)
- ✅ Governance schemas (namespace labels)
- ✅ Configuration (tenant tiers, cost model)
- ✅ Documentation (deployment guide, baseline README)

**Next Phase:** P1 - Full baseline integration (21 files, target 2025-12-14)

---

最後更新：2025-12-07
