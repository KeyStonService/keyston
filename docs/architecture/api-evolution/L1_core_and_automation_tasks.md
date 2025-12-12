# 🔄 API & Module Evolution — Core + Automation

## 文件說明 / Document Purpose

本文件描述本輪針對 Core Engine（SynergyMesh）與 Automation 層的 API 演化計畫。  
This document describes the current round of API evolution planning for the Core
Engine (SynergyMesh) and Automation layer.

## 版本資訊 / Version Information

- **階段 / Phase**: L1 Core + Automation Enhancement
- **版本 / Version**: v1.0.0
- **日期 / Date**: 2025-12-07
- **負責人 / Owner**: SynergyMesh Platform Team

## 對齊檢查 / Alignment Checklist

所有變更必須對齊：  
All changes must align with:

- ✅ **語言堆疊 / Language Stack**:
  - Core: TypeScript（控制）+ Python（認知）+ C++（必要時）
  - Automation: TypeScript / Python 為主
- ✅ **模組映射 / Module Map**:
  - `core.*` 不直接依賴 `apps.*`
  - `automation.*` 透過 `core.unified_integration` 與其他服務協作
- ✅ **架構骨架 / Architecture Skeletons**:
  - architecture-stability
  - api-governance
  - security-observability

---

## 1. automation.hyperautomation — 新增 7 個治理/安全 API

> **目標 /
> Objective**: 讓 Hyperautomation 模組可以作為「治理與安全決策 API 中心」。

### 📦 模組資訊 / Module Information

- **模組路徑 / Module Path**: `automation/hyperautomation/`
- **預期語言 / Expected Languages**:
  - 實作入口 / Implementation Entry: TypeScript（HTTP/API 層）
  - 核心邏輯 / Core Logic: Python/Policy 引擎（OPA / Rego）
  - 備註 / Notes: 透過 TS adapter 呼叫

### 🆕 新增 API / New APIs

#### 1. `POST /policy/validate`

- **功能 / Functionality**: 對輸入的政策（Rego/JSON）進行驗證與靜態分析。
- **輸入 / Input**:
  - `policy`: 政策定義（Rego/JSON 格式）
  - `test_cases`: 測試案例（選填，array）
- **輸出 / Output**:
  - `valid`: boolean - 政策是否有效
  - `issues`: array - 問題清單
  - `recommendations`: array - 改進建議
- **備註 / Notes**: 支援 OPA Rego 與 JSON Schema 驗證

#### 2. `POST /systems/register`

- **功能 / Functionality**: 註冊系統的安全等級（L0–L5）。
- **輸入 / Input**:
  - `system_id`: string - 系統唯一識別碼
  - `safety_level`: string - 安全等級（L0-L5）
  - `description`: string - 系統描述
  - `owner`: string - 系統擁有者
- **輸出 / Output**:
  - `registration_id`: string - 註冊 ID
  - `token`: string - 認證 token
  - `status`: string - 註冊狀態
- **備註 / Notes**: 整合 SLSA 溯源與合約服務

#### 3. `POST /geofence/validate`

- **功能 / Functionality**: 驗證給定的任務/路徑是否在地理圍欄內。
- **輸入 / Input**:
  - `mission_path`: array - 任務路徑座標列表
  - `geofence_polygon`: array - 地理圍欄多邊形範圍
  - `rules`: object - 驗證規則
- **輸出 / Output**:
  - `is_compliant`: boolean - 是否合規
  - `violations`: array - 違規點列表
  - `violation_reasons`: array - 違規原因
- **備註 / Notes**: 支援 GeoJSON 格式，整合 autonomous 層

#### 4. `POST /sbom/generate`

- **功能 / Functionality**: 生成雙雜湊（dual-hash）SBOM。
- **輸入 / Input**:
  - `source_repo`: string - 來源倉庫 URL
  - `build_artifact`: object - 建置產物資訊
  - `include_dependencies`: boolean - 是否包含依賴
- **輸出 / Output**:
  - `sbom`: object - SBOM（JSON 格式）
  - `hash_list`: array - hash 列表（SHA256 + SHA512）
  - `signature`: string - Sigstore 簽名
- **備註 / Notes**: 整合 core/slsa_provenance

#### 5. `POST /contracts/verify`

- **功能 / Functionality**: 驗證合約文件（如安全 SLA、API 合約）是否合規。
- **輸入 / Input**:
  - `contract_content`: string - 合約內容
  - `contract_type`: string - 合約類型（SLA/API/Security）
  - `validation_rules`: array - 驗證規則集
- **輸出 / Output**:
  - `is_valid`: boolean - 是否有效
  - `validation_results`: array - 驗證結果詳情
  - `recommendations`: array - 改進建議
- **備註 / Notes**: 整合 core/contract_service

#### 6. `POST /safety/assess`

- **功能 / Functionality**: 根據已註冊資訊與即時狀態產生安全風險評估。
- **輸入 / Input**:
  - `system_id`: string - 系統 ID
  - `current_state`: object - 當前系統狀態
  - `environment`: object - 環境資訊
- **輸出 / Output**:
  - `risk_level`: string - 風險等級（LOW/MEDIUM/HIGH/CRITICAL）
  - `risk_score`: number - 風險分數（0-100）
  - `recommended_actions`: array - 建議措施
  - `compliance_status`: object - 合規狀態
- **備註 / Notes**: 整合 core/safety_mechanisms

#### 7. `GET /emergency/status`

- **功能 / Functionality**: 查詢系統緊急停止（Emergency Stop）狀態。
- **輸入 / Input**:
  - `system_id`: string - 系統 ID（query parameter）
- **輸出 / Output**:
  - `e_stop_status`: string - E-Stop 狀態（ACTIVE/INACTIVE）
  - `trigger_source`: string - 觸發來源
  - `last_updated`: string - 最後更新時間（ISO 8601）
  - `details`: object - 詳細資訊
- **備註 / Notes**: 即時查詢，低延遲要求 (<100ms)

---

## 2. core.unified_integration — 增強 orchestrator 能力（+3 endpoints）

> **目標 / Objective**: 讓 `core.unified_integration`
> 成為所有跨服務工作流的唯一入口。

### 📦 模組資訊 / Module Information

- **模組路徑 / Module Path**: `core/unified_integration/`
- **預期語言 / Expected Languages**: TypeScript

### 🆕 新增 API / New APIs

#### 1. `POST /workflows/execute`

- **功能 / Functionality**: 執行多服務工作流，支援 rollback。
- **輸入 / Input**:
  - `workflow_id`: string - 工作流 ID
  - `steps`: array - 步驟列表（服務 + 操作 + 參數）
  - `rollback_strategy`: object - Rollback 策略
- **輸出 / Output**:
  - `execution_id`: string - 執行 ID
  - `status`: string - 執行狀態
  - `results`: array - 各步驟執行結果
  - `rollback_status`: object - Rollback 狀態（失敗時）
- **備註 / Notes**: 支援 DAG 排程與部分 rollback

#### 2. `POST /dependencies/resolve`

- **功能 / Functionality**: 進行拓撲排序，解析模組依賴順序。
- **輸入 / Input**:
  - `modules`: array - 模組列表
  - `dependencies`: object - 依賴關係圖
  - `constraints`: object - 約束條件（選填）
- **輸出 / Output**:
  - `sorted_order`: array - 排序後的部署順序
  - `dependency_graph`: object - 依賴圖
  - `warnings`: array - 警告訊息（循環依賴等）
- **備註 / Notes**: 用於部署順序、migration 排程

#### 3. `GET /health/system`

- **功能 / Functionality**: 聚合所有核心服務健康狀態。
- **輸入 / Input**: 無（透過 service registry 自動查詢）
- **輸出 / Output**:
  - `overall_status`: string - 整體狀態（HEALTHY/DEGRADED/UNHEALTHY）
  - `services`: array - 各服務狀態列表
  - `last_check`: string - 最後檢查時間
  - `metrics`: object - 聚合指標
- **備註 / Notes**: 透過 service registry 查詢各服務 `/health` endpoint

---

## 3. core.mind_matrix — 增強認知/模型能力（+3 endpoints）

> **目標 / Objective**: 提供統一的 AI / 模型調用入口。

### 📦 模組資訊 / Module Information

- **模組路徑 / Module Path**: `core/mind_matrix/` (runtime/mind_matrix/)
- **預期語言 / Expected Languages**:
  - API + routing: TypeScript
  - 模型調用/推論: Python

### 🆕 新增 API / New APIs

#### 1. `POST /inference`

- **功能 / Functionality**: 批次模型推論（支援多模型、批次輸入）。
- **輸入 / Input**:
  - `model_id`: string - 模型 ID
  - `inputs`: array - 輸入資料（批次）
  - `options`: object - 推論選項（溫度、top_p 等）
- **輸出 / Output**:
  - `results`: array - 推論結果列表
  - `model_info`: object - 模型資訊
  - `inference_time`: number - 推論時間（ms）
- **備註 / Notes**: 支援 Transformer、LLM 等多種模型類型

#### 2. `POST /knowledge/query`

- **功能 / Functionality**: 語意查詢（向量搜尋、知識庫查詢）。
- **輸入 / Input**:
  - `query`: string - 查詢字串
  - `query_type`: string - 查詢類型（semantic/keyword/hybrid）
  - `filters`: object - 篩選條件（選填）
  - `top_k`: number - 返回前 K 個結果
- **輸出 / Output**:
  - `results`: array - 查詢結果列表（含相似度分數）
  - `total_count`: number - 總結果數
  - `query_time`: number - 查詢時間（ms）
- **備註 / Notes**: 整合 knowledge_processing 模組與向量資料庫

#### 3. `POST /models/{model_id}/evaluate`

- **功能 / Functionality**: 根據測試集與指標對模型做評估。
- **輸入 / Input**:
  - `model_id`: string - 模型 ID（path parameter）
  - `test_dataset`: array - 測試資料集
  - `metrics`: array - 評估指標（accuracy, F1, etc.）
- **輸出 / Output**:
  - `evaluation_results`: object - 評估結果
  - `metrics_scores`: object - 各指標分數
  - `confusion_matrix`: array - 混淆矩陣（分類任務）
  - `report`: string - 詳細報告
- **備註 / Notes**: 支援分類、回歸、生成等多種任務類型

---

## 4. automation.autonomous — 自主任務控制（+2 endpoints）

> **目標 / Objective**: 提供任務規劃與狀態查詢能力。

### 📦 模組資訊 / Module Information

- **模組路徑 / Module Path**: `automation/autonomous/`
- **預期語言 / Expected Languages**: TypeScript / Python

### 🆕 新增 API / New APIs

#### 1. `POST /missions/{mission_id}/path`

- **功能 / Functionality**: 為任務生成路徑（path planning）。
- **輸入 / Input**:
  - `mission_id`: string - 任務 ID（path parameter）
  - `start_point`: object - 起點座標
  - `end_point`: object - 終點座標
  - `constraints`: object - 約束條件（障礙物、地理圍欄等）
  - `optimization`: string - 優化目標（shortest/safest/fastest）
- **輸出 / Output**:
  - `path`: array - 規劃路徑（座標列表）
  - `estimated_time`: number - 預估時間（秒）
  - `estimated_distance`: number - 預估距離（米）
  - `waypoints`: array - 路徑點列表
- **備註 / Notes**: 整合 geofence/validate API

#### 2. `GET /missions/{mission_id}/status`

- **功能 / Functionality**: 查詢任務執行狀態（progress、狀態碼、最近事件）。
- **輸入 / Input**:
  - `mission_id`: string - 任務 ID（path parameter）
- **輸出 / Output**:
  - `status`: string - 任務狀態（PENDING/IN_PROGRESS/COMPLETED/FAILED）
  - `progress`: number - 進度百分比（0-100）
  - `current_position`: object - 當前位置
  - `recent_events`: array - 最近事件列表
  - `last_updated`: string - 最後更新時間
- **備註 / Notes**: 即時狀態查詢，支援 WebSocket 訂閱

---

## 5. services.mcp — 工具列舉（+1 endpoint）

> **目標 / Objective**: 提供 MCP 工具發現能力。

### 📦 模組資訊 / Module Information

- **模組路徑 / Module Path**: `services/mcp/` (mcp-servers/)
- **預期語言 / Expected Languages**: TypeScript / JavaScript

### 🆕 新增 API / New APIs

#### 1. `GET /tools`

- **功能 / Functionality**: 列出所有可用 MCP 工具與能力，供前端/代理選擇。
- **輸入 / Input**: 無（或可選的 `category` query parameter）
- **輸出 / Output**:
  - `tools`: array - 工具列表
    - `tool_id`: string - 工具 ID
    - `name`: string - 工具名稱
    - `description`: string - 工具描述
    - `capabilities`: array - 能力列表
    - `version`: string - 版本
    - `status`: string - 狀態（ACTIVE/INACTIVE）
  - `total_count`: number - 工具總數
- **備註 / Notes**: 可整合到 UI 工具選擇器

---

## 6. apps.web.ui — 匯出功能（+1 endpoint）

> **目標 / Objective**: 提供資料匯出能力。

### 📦 模組資訊 / Module Information

- **模組路徑 / Module Path**: `apps/web/ui/` (frontend/ui/)
- **預期語言 / Expected Languages**: TypeScript

### 🆕 新增 API / New APIs

#### 1. `POST /export`

- **功能 / Functionality**: 匯出多格式資料（CSV/JSON/Markdown/報告）。
- **輸入 / Input**:
  - `data_source`: string - 資料來源（reports/metrics/logs等）
  - `format`: string - 匯出格式（csv/json/markdown/pdf）
  - `filters`: object - 篩選條件
  - `date_range`: object - 時間範圍（選填）
- **輸出 / Output**:
  - `export_id`: string - 匯出任務 ID
  - `download_url`: string - 下載連結（非同步生成）
  - `status`: string - 匯出狀態
  - `estimated_completion`: string - 預估完成時間
- **備註 / Notes**: 大量資料使用非同步生成，小量資料可同步返回

---

## 驗證與測試 / Validation & Testing

完成所有 endpoint 實施後，必須執行：  
After completing all endpoint implementations, you must perform:

### 1. 程式碼審查 / Code Review

- [ ] 執行 `code_review` 工具
- [ ] 執行 `codeql_checker`
- [ ] 修正所有 HIGH / CRITICAL 問題

### 2. 建置與測試 / Build & Test

- [ ] 建置所有 workspace

  ```bash
  npm run build --workspaces --if-present
  ```

- [ ] 執行 Lint（TS/Py）

  ```bash
  npm run lint --workspaces --if-present
  python -m pylint automation/ core/
  ```

- [ ] 執行現有測試

  ```bash
  npm run test --workspaces --if-present
  pytest
  ```

- [ ] 新增 endpoint 對應測試
  - 單元測試：每個 API 至少 3 個測試案例
  - 整合測試：跨服務工作流測試
  - E2E 測試：完整業務流程測試
- [ ] 驗證所有 endpoint 在本機與 CI 上正常運作

### 3. 文件更新 / Documentation Update

- [ ] 更新 API 參考文件
- [ ] 更新相關 README
- [ ] 更新 `config/system-module-map.yaml`
- [ ] 更新知識圖譜（Knowledge Graph）

  ```bash
  make all-kg
  ```

### 4. 性能與安全 / Performance & Security

- [ ] API 回應時間 < 2 秒（P95）
- [ ] 支援 100+ 併發請求
- [ ] 通過 OWASP Top 10 檢查
- [ ] 所有敏感資料加密傳輸
- [ ] 實施 Rate Limiting

---

## 相關文件 / Related Documents

- [System Module Map](../../../config/system-module-map.yaml)
- [System Manifest](../../../config/system-manifest.yaml)
- [Language Governance](../language-governance.md)
- [Language Stack](../language-stack.md)
- [Architecture Layers](../layers.md)
- [API Evolution Template](./TEMPLATE.md)

---

## 實施時間表 / Implementation Timeline

| 模組 / Module              | 預估時間 / Estimated Time | 優先級 / Priority |
| -------------------------- | ------------------------- | ----------------- |
| automation.hyperautomation | 5-7 天                    | HIGH              |
| core.unified_integration   | 3-5 天                    | HIGH              |
| core.mind_matrix           | 4-6 天                    | MEDIUM            |
| automation.autonomous      | 3-4 天                    | MEDIUM            |
| services.mcp               | 1-2 天                    | LOW               |
| apps.web.ui                | 2-3 天                    | LOW               |

**總計 / Total**: 約 18-27 天（依團隊規模與並行度調整）

---

## 變更歷史 / Change Log

| 日期 / Date | 版本 / Version | 變更內容 / Changes               | 負責人 / Owner |
| ----------- | -------------- | -------------------------------- | -------------- |
| 2025-12-07  | v1.0.0         | 初始版本，定義 18 個新 endpoints | Platform Team  |

---

**維護團隊 / Maintenance Team**: SynergyMesh Platform Team  
**文件版本 / Document Version**: 1.0.0  
**最後更新 / Last Updated**: 2025-12-07
