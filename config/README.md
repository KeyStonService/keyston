# ⚙️ Config - 配置中心 / Configuration Center

## 概述 / Overview

`config/` 目錄是所有系統配置的統一中心，包含業務、基礎設施、安全、監控等配置。

The `config/` directory is the unified center for all system configurations,
including business, infrastructure, security, and monitoring configurations.

---

## 📁 目錄結構 / Directory Structure

```
config/
├── README.md                           # 配置中心說明
│
├── 📋 主配置檔案 / Master Configs
├── system-manifest.yaml                # 系統宣告清單
├── unified-config-index.yaml           # 統一配置索引 v3.0.0
├── system-module-map.yaml              # 模組映射
├── environment.yaml                    # 環境配置
├── dependencies.yaml                   # 依賴定義
│
├── 🤖 AI 與決策 / AI & Decision
├── ai-constitution.yaml                # AI 憲法 (三層體系)
├── virtual-experts.yaml                # 虛擬專家團隊
├── island-ai-runtime.yaml              # Island AI 執行時
│
├── ⚖️ 治理與安全 / Governance & Security
├── safety-mechanisms.yaml              # 安全機制配置
├── cloud-agent-delegation.yml          # 雲端代理委派
├── security-network-config.yml         # 安全網絡配置
├── island-control.yml                  # 控制配置
│
├── 🏗️ 基礎設施 / Infrastructure
├── topology-mind-matrix.yaml           # 心智矩陣拓撲
├── monitoring.yaml                     # 監控配置
├── prometheus-config.yml               # Prometheus 配置
├── prometheus-rules.yml                # Prometheus 告警規則
├── grafana-dashboard.json              # Grafana 儀表板
├── elasticsearch-config.sh             # Elasticsearch 設定
│
├── 🚀 自動化 / Automation
├── auto-fix-bot.yml                    # Auto-Fix Bot 配置
├── auto-fix-bot.prompt.yml             # Auto-Fix Prompt
├── ci-error-handler.yaml               # CI 錯誤處理
├── ci-comprehensive-solution.yaml      # CI 綜合方案
│
├── 🐳 容器 / Container Configuration
├── docker/                             # Docker 配置
│   ├── Dockerfile.prod
│   ├── Dockerfile.dev
│   └── docker-entrypoint.sh
├── auto-scaffold.json                  # 自動生成腳本
├── peachy-build.toml                   # 構建配置
│
├── 🔄 工具鏈 / Toolchain
├── conftest/                           # Conftest 策略目錄
│   ├── deployment.rego
│   └── security.rego
└── yaml-module-system.yaml             # YAML 模組系統
```

---

## 🔑 主要配置檔案說明 / Key Configuration Files

### 系統宣告 (system-manifest.yaml)

定義系統的核心元件、依賴和服務聲明。

```yaml
system:
  name: SynergyMesh
  version: 4.0.0
  components:
    - name: core-engine
      status: active
    - name: governance-system
      status: active
```

### 統一配置索引 (unified-config-index.yaml)

所有配置的集中索引，便於快速查找。

### AI 憲法 (ai-constitution.yaml)

三層憲法體系：

- 第一層：系統原則
- 第二層：業務規則
- 第三層：實施指南

### 安全機制 (safety-mechanisms.yaml)

- 斷路器 (Circuit Breaker)
- 緊急停止 (Emergency Stop)
- 回滾策略 (Rollback Policy)

### 監控配置 (monitoring.yaml)

- Prometheus 指標收集
- Grafana 儀表板定義
- 告警規則配置

---

## 🚀 使用指南 / Usage Guide

### 驗證配置 / Validate Configuration

```bash
# 驗證所有 YAML 配置
python3 tools/docs/validate_index.py --verbose

# 驗證特定配置
python3 tools/docs/validate_index.py --config config/system-manifest.yaml
```

### 應用配置 / Apply Configuration

```bash
# Kubernetes 部署
kubectl apply -f infrastructure/kubernetes/manifests/

# Docker 部署
docker-compose -f docker-compose.yml up -d
```

### 更新配置 / Update Configuration

1. 編輯相應的 YAML 檔案
2. 運行驗證: `make all-kg`
3. 提交變更: `git add . && git commit -m "Update config"`

---

## 📊 配置優先級 / Configuration Priority

```
環境變數 (.env)
    ↓
命令行參數 (CLI args)
    ↓
系統配置 (synergymesh.yaml)
    ↓
本地配置 (config/*.yaml)
    ↓
預設值 (defaults)
```

---

## 🔐 敏感資訊管理 / Sensitive Information Management

### ❌ 不要在配置檔案中包含

- API 金鑰
- 資料庫密碼
- JWT 密鑰
- 任何密鑰

### ✅ 改用環境變數

```bash
# .env 檔案
DATABASE_URL=postgresql://...
JWT_SECRET=<random-secret>
API_KEY=<secret-key>
```

### 🔒 Git 保護

```bash
# .gitignore
.env
.env.*.local
config/secrets/
```

---

## 🔄 配置同步 / Configuration Synchronization

### 本地開發

```bash
cp .env.example .env
# 編輯 .env 並填入本地值
```

### 預發佈環境 (Staging)

```bash
cp .env.staging .env
# 使用預發佈特定值
```

### 生產環境 (Production)

```bash
# 從 CI/CD 系統注入，不在倉庫中儲存
```

---

## 📈 配置演變歷史 / Configuration Evolution

| 版本  | 日期    | 更新         |
| ----- | ------- | ------------ |
| 1.0.0 | 2024-01 | 初始配置     |
| 2.0.0 | 2024-06 | 引入統一索引 |
| 2.5.0 | 2024-09 | 新增監控配置 |
| 3.0.0 | 2024-11 | 統一配置索引 |
| 3.5.0 | 2024-12 | Phase 4 整合 |
| 4.0.0 | 2025-01 | 完全重構     |

---

## 📖 詳細文檔 / Detailed Documentation

- [系統宣告](./system-manifest.yaml)
- [統一配置索引](./unified-config-index.yaml)
- [AI 憲法](./ai-constitution.yaml)
- [安全機制](./safety-mechanisms.yaml)
- [監控配置](./monitoring.yaml)

---

## 🤝 貢獻指南 / Contributing

在修改配置時：

1. 遵循 YAML 格式規範
2. 更新相應的說明文檔
3. 運行驗證: `python3 tools/docs/validate_index.py --verbose`
4. 提交前檢查 `.gitignore`

---

## 📞 支援 / Support

- 📖 [配置文檔](./README.md)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
