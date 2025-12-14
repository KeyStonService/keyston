# Auto-Fix Bot 2.0 使用指南

## 📋 概述

Auto-Fix Bot 2.0 是 Isynergymesh 專案的自動修復機器人配置系統，整合了深度可驗證模組、Policy Gate 驗證、多層證據生成與審計追蹤功能。

### 版本資訊

- **版本**: 2.0.0
- **配置檔案**: `auto-fix-bot.yml`
- **架構模式**: 去AXIOM化重構策略
- **合規標準**: SLSA-L3, in-toto, audit-trail, axiom-free

## 🎯 核心功能

### 1. 專案結構映射

配置檔案完整映射了 Isynergymesh 專案的目錄結構：

```yaml
project_mapping:
  config_root: ".config"
  policies_root: "governance/policies/conftest"
  governance_root: ".governance"
  evidence_root: "root-evidence"
  schemas_root: "schemas"
  scripts_root: "scripts"
  templates_root: "templates"
  docs_root: "docs"
  mcp_servers_root: "mcp-servers"
  test_vectors_root: "test-vectors"
```

### 2. Bot 配置範圍

Bot 支援四個主要驗證範圍：

#### 2.1 Deep YAML 驗證

- 路徑：`templates/**/*.yaml`, `schemas/**/*.json`, `.config/**/*.yaml`, `governance/**/*.yaml`
- 功能：深度驗證 YAML 檔案結構和內容

#### 2.2 MCP Servers 驗證

- 路徑：`mcp-servers/**/*.py`, `mcp-servers/**/*.json`
- 功能：確保 MCP servers 符合安全和型別標註要求

#### 2.3 Advanced Architecture 同步

- 路徑：`advanced-architecture/**/*`, `advanced-system-src/**/*`, `advanced-system-dist/**/*`
- 功能：同步源碼與建置輸出

#### 2.4 Evidence Chain 驗證

- 路徑：`root-evidence/**/*.json`, `attest-build-provenance-main/**/*`
- 功能：驗證證據鏈的完整性和簽章

## 🔧 修復規則

### 1. Deep YAML Schema Validation (Critical)

**觸發條件**:

- 檔案符合模式：`templates/**/*.yaml`
- Schema 違規
- 缺少必要欄位

**自動修復動作**:

1. Schema 驗證
2. 自動補充缺失的 metadata
3. 生成測試向量

### 2. MCP Servers Compliance (High)

**觸發條件**:

- 檔案符合模式：`mcp-servers/**/*.py`
- 導入違規
- 缺少型別提示

**自動修復動作**:

1. 修復不當的導入
2. 添加型別標註

### 3. Architecture Consistency (Medium)

**觸發條件**:

- 檔案符合模式：`advanced-system-src/**/*`
- 建置不一致

**自動修復動作**:

1. 同步到 dist 目錄
2. 驗證完整性

### 4. Evidence Chain Integrity (Critical)

**觸發條件**:

- 檔案符合模式：`root-evidence/**/*.json`
- 簽章遺失
- 認證無效

**自動修復動作**:

1. 驗證簽章
2. 重新生成認證

## 🚪 Policy Gates

### Pre-Validation Gate (前置檢查門)

**驗證內容**:

- OPA 策略：`governance/policies/conftest/yaml-structure.rego`
- Kyverno 策略：`governance/security-policy.yaml`

**失敗動作**: 阻擋執行

### Post-Fix Validation Gate (後置驗證門)

**驗證內容**:

- OPA 策略：`governance/policies/conftest/deep-validation.rego`
- JSON Schema：`schemas/complete-validation-schema.json`

**證據要求**:

- SBOM 已生成
- Attestation 已簽署
- Provenance 完整
- Audit trail 不可變

**失敗動作**: 建立 Issue  
**成功動作**: 自動批准

## 📊 證據生成

### 1. SBOM Generator

**觸發時機**: 任何程式碼變更  
**工具**: Syft + Cosign  
**輸出位置**: `root-evidence/provenance/rag-provenance/sbom/`

### 2. Attestation Generator

**觸發時機**: 修復套用後  
**格式**: in-toto  
**輸出位置**: `root-evidence/attestation/`

### 3. Provenance Generator

**觸發時機**: 工作流程完成  
**格式**: SLSA v1.0  
**輸出位置**: `root-evidence/provenance/`

## 🔔 通知系統

### Slack 通知

**頻道**: `#isynergymesh-auto-fix`  
**失敗時提及**: `@platform-team`, `@security-team`

### Email 通知

**收件人**:

- <platform@isynergymesh.com>
- <security@isynergymesh.com>

### GitHub 通知

**動作**:

- 建立 Issue
- 指派給 `platform-lead`
- 標籤：`auto-fix`, `governance`, `priority-high`

## 📝 審計追蹤

### 配置

- **存儲路徑**: `root-evidence/audit/auto-fix/`
- **保留期限**: 365 天
- **不可變存儲**: 已啟用

### 追蹤事件

- 修復觸發
- 修復套用
- 修復失敗
- Policy Gate 檢查
- 證據生成
- 通知發送

## 🔄 回滾機制

### 觸發條件

1. **測試失敗** → 還原提交
2. **Policy Gate 失敗** → 建立 Issue 並阻擋
3. **證據損壞** → 緊急停止

### 回滾步驟

1. 備份當前狀態
2. 還原變更
3. 驗證回滾結果

## 🔌 整合配置

### GitHub Actions

**工作流程檔案**: `.github/workflows/auto-fix-validation.yml`

**所需環境變數**:

- `COSIGN_PRIVATE_KEY`
- `SLACK_WEBHOOK_URL`
- `SMTP_SERVER`
- `GITHUB_TOKEN`

### DevContainer

**Dockerfile**: `.devcontainer/Dockerfile`

**擴展**:

- ms-python.python
- ms-vscode.vscode-yaml
- redhat.vscode-yaml

## 🛡️ MCP Servers 安全規則

### 允許的導入

```python
# 允許的模組
json, asyncio, logging, pathlib, typing, dataclasses,
enum, abc, contextlib, mcp.server, mcp.types
```

### 禁止的導入

```python
# 禁止的模組
os.system, subprocess, eval, exec, __import__
```

### 安全檢查

- 禁止 Shell 執行
- 沙箱外不可寫入檔案系統
- 未經批准不可進行網路呼叫
- 必須進行輸入驗證

### 型別標註要求

- 所有函數必須有型別標註
- 所有類別方法必須有型別標註
- 必須指定返回型別
- 必須指定參數型別

## 🏗️ Advanced Architecture 同步

### 同步模式

| 檔案類型 | 轉換方式 | 驗證方式 |
|---------|---------|---------|
| `*.py` | 編譯與優化 | 執行單元測試 |
| `*.yaml` | 驗證與壓縮 | Schema 檢查 |
| `*.json` | 驗證與壓縮 | JSON Schema 驗證 |

### 同步命令

1. **前置驗證** - 驗證架構完整性
2. **同步轉換** - 套用轉換並驗證
3. **後置驗證** - 驗證同步完整性

## 🔗 Cross-Layer Bridges

### Evidence-to-Trust 橋接

**認證格式**: in-toto  
**簽章方式**: Cosign  
**信任根**: `root-evidence/trust-anchors/`

### 生成器

1. **Build Attestation** - 建置完成時生成
2. **Deployment Attestation** - 部署完成時生成

## 📐 深度驗證架構

### YAML 結構要求

**必要區段**:

- metadata
- version
- owner
- audit

**元數據要求**:

- created_at (RFC3339 格式)
- updated_at (RFC3339 格式)
- labels (至少 2 個)
- compliance_tags (必須來自允許清單)

### 版本控制要求

- **格式**: 語意化版本 (Semantic Versioning)
- **模式**: `^\\d+\\.\\d+\\.\\d+$`
- **必須**: Changelog

## 🔐 證據鏈驗證

### 簽章要求

- **演算法**: ES256
- **金鑰類型**: ECDSA P-256
- **證書鏈**: 必須
- **時間戳**: 必須

### 認證要求

- **格式**: in-toto
- **Statement Type**: `https://in-toto.io/Statement/v0.1`
- **Predicate**: 必須
- **Subject Digest**: SHA-256

### Provenance 要求

- **格式**: SLSA v1.0
- **Builder ID**: 必須
- **Build Type**: 必須
- **Invocation**: 必須
- **Materials**: 必須完整

## 🚨 錯誤恢復程序

### 1. Schema 驗證失敗

**步驟**:

1. 備份當前檔案
2. 從範本還原
3. 合併現有資料
4. 重新驗證
5. 通知團隊

### 2. 證據損壞檢測

**步驟**:

1. 隔離損壞的證據
2. 從備份還原
3. 重新生成簽章
4. 審計損壞原因
5. 上報安全團隊

### 3. Policy Gate 持續失敗

**步驟**:

1. 建立緊急 Issue
2. 停用自動合併
3. 要求人工審查
4. 上報治理團隊
5. 記錄例外請求

## 📊 監控與可觀察性

### 核心指標

| 指標名稱 | 類型 | 閾值 | 告警條件 |
|---------|-----|------|---------|
| 修復成功率 | 百分比 | 95% | 低於閾值 |
| 平均修復時間 | 時長 | 5分鐘 | 超過閾值 |
| Policy Gate 失敗率 | 百分比 | 5% | 超過閾值 |

### 儀表板

#### Auto Fix Overview

- 修復嘗試趨勢
- 按規則類型的成功率
- 平均解決時間
- Policy Gate 狀態
- 證據生成狀態

#### Security Compliance

- 簽章驗證狀態
- 認證覆蓋率
- 審計追蹤完整性
- 漏洞檢測率

## 📚 使用範例

### 基本使用

```bash
# 使用配置檔案執行 Auto-Fix Bot
python scripts/auto_fix_bot.py --config auto-fix-bot.yml
```

### 僅驗證不修復

```bash
# 乾跑模式
python scripts/auto_fix_bot.py --config auto-fix-bot.yml --dry-run
```

### 指定範圍執行

```bash
# 僅執行 MCP Servers 驗證
python scripts/auto_fix_bot.py --config auto-fix-bot.yml --scope mcp-servers-validation
```

## 🔍 疑難排解

### 常見問題

#### Q1: Policy Gate 驗證失敗

**解決方案**:

1. 檢查 `governance/policies/conftest/` 下的策略檔案
2. 確認 YAML 檔案符合必要的結構要求
3. 查看審計日誌：`root-evidence/audit/auto-fix/`

#### Q2: 簽章驗證失敗

**解決方案**:

1. 確認 `COSIGN_PRIVATE_KEY` 環境變數已設定
2. 檢查證書識別符是否正確
3. 驗證 OIDC 發行者設定

#### Q3: 證據生成失敗

**解決方案**:

1. 確認 `syft` 和 `cosign` 工具已安裝
2. 檢查 `root-evidence/` 目錄權限
3. 查看生成命令的輸出日誌

## 📞 支援與聯絡

- **平台團隊**: <platform@isynergymesh.com>
- **安全團隊**: <security@isynergymesh.com>
- **Slack 頻道**: #isynergymesh-auto-fix
- **GitHub Issues**: <https://github.com/we-can-fix/synergymesh/issues>

## 📜 版本歷史

### 2.0.0 (2025-01-17)

- 完整整合深度可驗證模組
- 實作去標籤化架構策略
- 適配 Isynergymesh 專案架構
- 新增 Policy Gate 驗證
- 整合證據鏈生成

### 1.5.0 (2025-01-17)

- 新增 Policy Gate 整合
- 新增證據鏈生成功能

### 1.0.0 (2025-01-17)

- 初始版本
- 基本 YAML 驗證與修復功能

## 📄 授權

MIT License - 詳見 LICENSE 檔案

## 🙏 致謝

感謝 Isynergymesh 專案的所有貢獻者，以及平台治理團隊和安全團隊的支持。
