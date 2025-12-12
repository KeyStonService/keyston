# SynergyMesh 監控系統參照文件

# SynergyMesh Monitoring System Reference Documentation

## 📋 概述 | Overview

本文件為 SynergyMesh 專案的監控系統參照指南，提供給所有工作人員、代理駕駛、智能體使用。目的是確保關鍵目錄與檔案的變更都能被追蹤、審核與管理。

This document serves as the monitoring system reference guide for the
SynergyMesh project, providing guidance for all workers, agents, and intelligent
systems. The goal is to ensure that changes to critical directories and files
are tracked, audited, and managed.

---

## 🎯 優先監控目錄 | Priority Monitoring Directories

以下目錄按重要性與敏感度排序，建議依序部署監控機制：

The following directories are sorted by importance and sensitivity. It is
recommended to deploy monitoring mechanisms in this order:

### 1. `config/` - 設定檔與部署參數

**說明**: 包含系統設定、憑證、部署參數  
**監控重點**: 所有變更（創建、修改、刪除）  
**風險等級**: 🔴 高 (High)  
**檔案範例**:

- `elasticsearch-config.sh`
- `prometheus-config.yml`
- `security-network-config.yml`
- `grafana-dashboard.json`

### 2. `core/contract_service/` - 合約與關鍵邏輯

**說明**: 核心業務邏輯、合約管理服務  
**監控重點**: 程式碼變更、API 修改  
**風險等級**: 🔴 高 (High)  
**子目錄**: `contracts-L1/contracts/`

### 3. `advanced-system-src/` & `advanced-system-dist/` - 核心系統

**說明**: 核心系統原始碼與編譯產出  
**監控重點**: 原始碼變更、建置產出物完整性  
**風險等級**: 🔴 高 (High)

### 4. `mcp-servers/` - MCP 伺服器

**說明**: Model Context Protocol 伺服器實作與工具  
**監控重點**: 服務邏輯、驗證器、安全掃描器  
**風險等級**: 🟠 中高 (Medium-High)

### 5. `scripts/` - 自動化腳本

**說明**: 部署、維運、遷移用自動化腳本  
**監控重點**: Shell 腳本、Python 腳本變更  
**風險等級**: 🟠 中高 (Medium-High)  
**檔案範例**:

- `advanced-push-protection.sh`
- `build-matrix.sh`
- `manage-secret-patterns.py`
- `vulnerability-alert-handler.py`

### 6. `governance/policies/conftest/` - 安全與合規政策

**說明**: OPA/Conftest 政策定義檔  
**監控重點**: 政策規則變更  
**風險等級**: 🟠 中高 (Medium-High)

### 7. `schemas/` - 資料結構定義

**說明**: JSON Schema 與資料驗證定義  
**監控重點**: Schema 變更（影響資料完整性）  
**風險等級**: 🟡 中 (Medium)

### 8. `docs/` - 操作手冊與部署指引

**說明**: 系統文件、runbook、部署指南  
**監控重點**: 重要操作流程文件變更  
**風險等級**: 🟡 中 (Medium)

---

## 🔐 變更流程與權限管理 | Change Process and Permission Management

### 誰可以變更？ | Who Can Make Changes?

#### 高風險目錄 (🔴 High Risk)

- **授權人員**: 資深工程師、DevOps Lead、Security Team
- **審核流程**: 必須經過 PR review + 至少 2 位 reviewer 批准
- **緊急變更**: 需事後補齊文件與審核

#### 中高風險目錄 (🟠 Medium-High Risk)

- **授權人員**: 工程團隊成員
- **審核流程**: 必須經過 PR review + 至少 1 位 reviewer 批准

#### 中等風險目錄 (🟡 Medium Risk)

- **授權人員**: 所有貢獻者
- **審核流程**: PR review（建議）

### PR 模板要求 | PR Template Requirements

所有涉及監控目錄的 PR 必須包含：

All PRs affecting monitored directories must include:

1. **變更說明**: 清楚描述變更內容與原因
2. **影響評估**: 說明對系統的潛在影響
3. **測試結果**: 提供測試證據（logs, screenshots）
4. **Rollback 計畫**: 如果變更失敗，如何回滾
5. **CHANGELOG 更新**: 在 `CHANGELOG.md` 中記錄此次變更

---

## 👥 緊急聯絡人清單 | Emergency Contact List

### Security Team (資安團隊)

- **職責**: 安全事件回應、存取控制、漏洞管理
- **聯絡方式**: `security@synergymesh.example.com`
- **Slack**: `#security-alerts`

### DevOps Team (維運團隊)

- **職責**: 系統部署、監控維護、基礎設施
- **聯絡方式**: `devops@synergymesh.example.com`
- **Slack**: `#devops-on-call`

### Development Lead (開發主管)

- **職責**: 程式碼審核、架構決策
- **聯絡方式**: `dev-lead@synergymesh.example.com`
- **Slack**: `#dev-leads`

### On-Call Engineer (值班工程師)

- **職責**: 24/7 緊急事件處理
- **聯絡方式**: `oncall@synergymesh.example.com`
- **PagerDuty**: 查看 PagerDuty rotation

---

## 📊 基線管理說明 | Baseline Management

### 什麼是基線？ | What is a Baseline?

基線是系統檔案在特定時間點的「可信狀態快照」，用於偵測未授權變更。

A baseline is a "trusted state snapshot" of system files at a specific point in
time, used to detect unauthorized changes.

### 基線建立流程 | Baseline Creation Process

1. **初始部署後**: 系統首次部署完成，執行首次基線掃描
2. **重大更新後**: 每次重大版本更新後，重新建立基線
3. **定期更新**: 每季度或每半年重新驗證並更新基線

### 基線雜湊演算法 | Baseline Hash Algorithm

- **建議使用**: SHA-256
- **備選方案**: SHA-512（更高安全性需求）
- **不建議**: MD5, SHA-1（已知安全弱點）

### 基線儲存位置 | Baseline Storage Location

- **FIM 工具**: 由 FIM 工具（如 OSSEC, Tripwire）管理
- **備份位置**: 安全備份伺服器（離線或唯讀掛載）
- **版本控制**: 基線檔案本身也應納入版本控制

---

## 🔍 監控工具整合 | Monitoring Tool Integration

### 建議監控工具 | Recommended Monitoring Tools

1. **FIM (File Integrity Monitoring)**
   - OSSEC
   - Tripwire
   - AIDE (Advanced Intrusion Detection Environment)

2. **auditd (Linux Audit Daemon)**
   - 系統層級稽核
   - 記錄所有檔案存取與變更

3. **inotify (Real-time Monitoring)**
   - 即時檔案系統事件監控
   - 用於測試與開發環境驗證

4. **SIEM (Security Information and Event Management)**
   - Splunk
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Wazuh

### 詳細設定指引 | Detailed Configuration Guide

請參閱 `MONITORING_GUIDE.md` 獲取完整的設定指引與工作人員提示詞。

For complete configuration guides and worker prompts, please refer to
`MONITORING_GUIDE.md`.

---

## 📝 變更記錄要求 | Change Log Requirements

所有對監控目錄的變更必須在 `CHANGELOG.md` 中記錄，格式如下：

All changes to monitored directories must be recorded in `CHANGELOG.md` with the
following format:

```
YYYY-MM-DD | <username> | <path> | <change_type> | <reason>
```

**範例 | Example**:

```
2025-11-24 | john.doe | config/prometheus-config.yml | modify | Update retention policy from 15d to 30d
2025-11-24 | jane.smith | core/contract_service/contracts-L1/contracts/src/routes.ts | add | Add new health check endpoint
```

---

## 🚨 異常行為偵測 | Anomaly Detection

### 應立即調查的行為 | Behaviors to Investigate Immediately

1. ❌ 非授權帳號的檔案變更
2. ❌ 非工作時間的批次變更（除非有預先排程）
3. ❌ 大量檔案同時變更（可能為攻擊或誤操作）
4. ❌ 重複失敗的存取嘗試
5. ❌ 權限提升行為（sudo, chmod）

### 回應流程 | Response Workflow

1. **偵測**: FIM/auditd 觸發 alert
2. **隔離**: SIEM 自動標記主機為 quarantine
3. **通知**: 自動通知資安與值班工程師
4. **調查**: 檢視完整稽核日誌與變更細節
5. **處置**: 根據調查結果採取行動（回滾、封鎖帳號、升級事件）

---

## 📚 相關文件 | Related Documentation

- [`CHANGELOG.md`](./CHANGELOG.md) - 變更記錄
- [`MONITORING_GUIDE.md`](./MONITORING_GUIDE.md) - 詳細監控設定指引
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) - 貢獻指南
- [`SECURITY.md`](./SECURITY.md) - 安全政策
- [`docs/QUICK_START.md`](./docs/QUICK_START.md) - 快速開始指南

---

## 🔄 文件更新歷史 | Document Update History

- **[Document Creation Date]**: 初始版本建立 (Initial version created)

---

**維護者 | Maintainer**: SynergyMesh Team  
**最後更新 | Last Updated**: [Document Creation Date]
