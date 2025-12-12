# Architecture Stability Guardrails

## 硬性邊界（Hard Guardrails）

AI 在提出任何架構變更時，**必須遵守**以下原則。違反任何原則將導致提案被駁回。

### 1. 禁止繞過層級（No Layer Bypass）

```
應用層 (apps)
    ↓ (只能依賴)
服務層 (services)
    ↓ (只能依賴)
平台層 (platform/agents)
    ↓ (只能依賴)
核心層 (core)
```

**禁止行為：**

- ❌ services 直接依賴 applications
- ❌ agents 直接依賴 core 內部細節（只能透過明確的 API 或 SDK）
- ❌ apps 層跳過 services 層直接存取 core
- ❌ 任何下層模組反向依賴上層（例如 core 引用 services 的實現）

**合法方式：**

- ✅ 透過 REST/gRPC API 跨層通信
- ✅ 透過事件驅動（Event Bus）進行異步通信
- ✅ 透過公開 SDK 或介面層進行互動

### 2. 禁止跨 Bounded Context 的直接資料存取

**禁止行為：**

- ❌ Service A 直接存取 Service B 的資料庫
- ❌ Agent 直接查詢其他 domain 的資料表
- ❌ 共享資料庫連線池用於多個 bounded context
- ❌ 跨 context 的外鍵約束

**合法方式：**

- ✅ Service A 透過 Service B 的 API 取得資料
- ✅ 透過事件流（Event Stream）同步資料副本
- ✅ 使用 API Gateway 進行跨界資料聚合

### 3. 禁止隱藏通道（No Hidden Channels）

**禁止行為：**

- ❌ 未記錄在案的 side-channel 通信（例如直接寫共享檔案系統作為整合渠道）
- ❌ 硬編碼的 IP 位址或內部埠號直連
- ❌ 繞過監控/審計的資料傳輸
- ❌ 未在 manifests 中定義的 inter-service 通信

**合法方式：**

- ✅ 在 `config/system-module-map.yaml` 中明確定義所有依賴
- ✅ 使用服務網格（Service Mesh）統一管理通信
- ✅ 所有通道均需通過監控和日誌系統

---

## 軟性指引（Soft Guidelines）

以下原則不是硬性要求，但應盡可能遵守：

1. **最小化服務間通信**
   - 減少微服務間的直接調用頻率
   - 優先使用非同步通信（消息隊列、事件流）

2. **保持高內聚，低耦合**
   - 同一 domain 的模組應聚集在一起
   - 跨 domain 依賴應明確且受限

3. **版本相容性**
   - API 變更應向後相容
   - 若必須 breaking change，應有廢棄期（deprecation period）

4. **測試覆蓋**
   - 跨層/跨 context 的集成測試覆蓋率應 > 80%
   - 關鍵路徑應包含 E2E 測試

---

## 例外處理（Exception Handling）

若 AI 的提案無法在遵守上述邊界的前提下實現：

1. **標記為「需要審查」**
   - 在 `stability_report` 中設置 `overall_status = "fail"`
   - 明確列出違規項目和原因

2. **提供修正建議**
   - 在 `suggested_changes` 中說明如何調整架構
   - 列出所有替代方案

3. **要求人類決策**
   - 審查員可選擇接受風險或要求重新設計
   - 所有例外必須記錄於 `architecture-exceptions.md`

---

## 驗證流程

每個架構變更都應通過以下驗證：

| 檢查項               | 工具                      | 觸發時機 |
| -------------------- | ------------------------- | -------- |
| Layer 檢查           | `check-layering.py`       | PR 提交  |
| 依賴分析             | `analyze-dependencies.py` | PR 提交  |
| Bounded Context 檢查 | `check-boundaries.py`     | PR 提交  |
| 通道審計             | `audit-channels.yaml`     | 部署前   |

所有檢查必須 pass 才能進入 `DEPLOYMENT_CHECKLIST`。
