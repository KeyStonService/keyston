# 🔄 API & Module Evolution Template

## 文件說明 / Document Purpose

本模板用於記錄每一輪 API 與模組的演化計畫。  
This template is used to document each round of API and module evolution
planning.

## 版本資訊 / Version Information

- **階段 / Phase**: [填入階段編號，如 Phase 0, Phase 1 等]
- **版本 / Version**: [填入版本號，如 v1.0.0]
- **日期 / Date**: [填入日期，如 2025-12-07]
- **負責人 / Owner**: [填入負責人或團隊名稱]

## 對齊檢查 / Alignment Checklist

在開始實施前，請確認：  
Before implementation, please confirm:

- [ ] 所有變更符合語言堆疊策略 (Language Stack Policy)
  - Core: TypeScript (控制) + Python (認知) + C++ (必要時)
  - Automation: TypeScript / Python 為主
- [ ] 所有變更符合模組映射 (Module Map)
  - `core.*` 不直接依賴 `apps.*`
  - `automation.*` 透過 `core.unified_integration` 協作
- [ ] 所有 endpoint 已在 `config/system-module-map.yaml` 中註冊
- [ ] 所有依賴關係符合架構骨架規則 (Architecture Skeleton Rules)

---

## 模組演化計畫 / Module Evolution Plan

### [模組名稱 / Module Name]

> **目標 / Objective**: [簡述本輪演化的目標]

#### 📦 模組資訊 / Module Information

- **模組路徑 / Module Path**: `[填入模組路徑，如 automation/hyperautomation]`
- **預期語言 / Expected Languages**:
  - 實作入口 / Implementation Entry: [如 TypeScript]
  - 核心邏輯 / Core Logic: [如 Python / Policy 引擎]
  - 備註 / Notes: [如「透過 TS adapter 呼叫」]

#### 🆕 新增 API / New APIs

##### 1. `[HTTP Method] /[endpoint-path]`

- **功能 / Functionality**: 描述此 API 的功能
- **輸入 / Input**:
  - 參數名稱: 參數類型與說明
  - 參數名稱: 參數類型與說明
- **輸出 / Output**:
  - 欄位名稱: 欄位類型與說明
- **備註 / Notes**: 任何額外說明

##### 2. `[HTTP Method] /[endpoint-path]`

- **功能 / Functionality**: 描述此 API 的功能
- **輸入 / Input**:
  - 參數名稱: 參數類型與說明
- **輸出 / Output**:
  - 欄位名稱: 欄位類型與說明

重複上述格式，為每個新增的 API 建立條目

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

- [ ] 執行 Lint (TypeScript/Python)

  ```bash
  npm run lint --workspaces --if-present
  python -m pylint core/ automation/
  ```

- [ ] 執行現有測試

  ```bash
  npm run test --workspaces --if-present
  pytest
  ```

- [ ] 新增 endpoint 對應測試
- [ ] 驗證所有 endpoint 在本機與 CI 上正常運作

### 3. 文件更新 / Documentation Update

- [ ] 更新 API 參考文件
- [ ] 更新相關 README
- [ ] 更新 `config/system-module-map.yaml`
- [ ] 更新知識圖譜 (Knowledge Graph)

  ```bash
  make all-kg
  ```

---

## 相關文件 / Related Documents

- [System Module Map](../../../config/system-module-map.yaml)
- [Language Governance](../language-governance.md)
- [Language Stack](../language-stack.md)
- [Architecture Layers](../layers.md)

---

## 變更歷史 / Change Log

| 日期 / Date | 版本 / Version | 變更內容 / Changes | 負責人 / Owner |
| ----------- | -------------- | ------------------ | -------------- |
| [日期]      | [版本]         | [變更描述]         | [負責人]       |

---

**維護團隊 / Maintenance Team**: SynergyMesh Development Team  
**文件版本 / Document Version**: 1.0.0  
**最後更新 / Last Updated**: 2025-12-07
