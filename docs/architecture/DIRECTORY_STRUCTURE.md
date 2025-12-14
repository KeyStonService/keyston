# SynergyMesh 專案目錄結構圖譜

> 產生時間 / Generated at: 2025-11-30 00:10:00 UTC
> 專案根目錄 / Project root: `/home/runner/work/SynergyMesh/SynergyMesh`
> **Status**: Consolidated directory structure completed

---

## 🗺️ 系統模組映射 / System Module Map

> **重要**: 完整的目錄分類與元件映射請參閱 [`config/system-module-map.yaml`](../../config/system-module-map.yaml)

該配置提供:

- 目錄分類與群組化 (Directory classification and grouping)
- 高度映射/引用整合 (High-level mapping/reference integration)  
- 技能與能力矩陣 (Skill & Capability matrix)
- 交叉引用索引 (Cross-reference index)
- 根目錄清理指南 (Root directory cleanup guidelines)

---

## 📂 統一目錄結構 / Consolidated Directory Structure

```
.
├── README.md                    # 主要說明文件
├── README.en.md                 # English README
├── CHANGELOG.md                 # 變更日誌
├── CONTRIBUTING.md              # 貢獻指南
├── CODE_OF_CONDUCT.md           # 行為準則
├── SECURITY.md                  # 安全政策
├── package.json                 # 根專案配置
├── tsconfig.json                # TypeScript 配置
├── jest.config.js               # Jest 測試配置
├── Dockerfile                   # Docker 配置
├── docker-compose.yml           # Docker Compose
├── docker-compose.dev.yml       # 開發環境 Docker Compose
│
├── automation/                  # 🤖 自動化系統 (已整合)
│   ├── intelligent/            # 智能自動化 (原 intelligent-automation/)
│   ├── hyperautomation/        # 超自動化 (原 intelligent-hyperautomation/)
│   ├── architect/              # 自動化架構師 (原 automation-architect/)
│   ├── autonomous/             # 自主系統 (原 autonomous-system/)
│   └── zero_touch_deployment.py
│
├── frontend/                    # 🎨 前端應用 (已整合)
│   ├── ui/                     # 統一 UI 套件 (整合自 architecture + system-ui)
│   └── dist/                   # 編譯產出 (原 advanced-system-dist/)
│
├── infrastructure/              # 🏗️ 基礎設施 (已整合)
│   ├── kubernetes/             # K8s 配置 (原 k8s/)
│   ├── monitoring/             # 監控配置 (原 monitoring/)
│   ├── canary/                 # Canary 部署 (原 canary/)
│   └── drift/                  # 漂移檢測 (原 drift/)
│
├── tests/                       # 🧪 測試 (已整合)
│   ├── unit/                   # 單元測試 (原 tests/)
│   ├── vectors/                # 測試向量 (原 test-vectors/)
│   └── performance/            # 效能測試 (原 performance-tests/)
│
├── governance/                  # ⚖️ 治理與政策 (已整合)
│   ├── rules/                  # 治理規則 (原 governance/)
│   ├── policies/               # 政策定義 (原 policy/)
│   ├── schemas/                # Schema 定義 (原 schemas/)
│   ├── sbom/                   # SBOM (原 sbom/)
│   └── audit/                  # 稽核日誌 (原 audit/)
│
├── tools/                       # 🔧 工具與腳本 (已整合)
│   ├── scripts/                # 自動化腳本 (原 scripts/)
│   ├── utilities/              # 工具程式 (原 tools/)
│   └── ci/                     # CI 輔助工具 (原 ci/)
│
├── ops/                         # 📋 運維 (已整合)
│   ├── runbooks/               # 運維手冊 (原 runbooks/)
│   ├── reports/                # 報告 (原 reports/)
│   ├── artifacts/              # 建置產物 (原 artifacts/)
│   ├── migration/              # 遷移工具 (原 migration/)
│   └── onboarding/             # 入門指南 (原 onboarding/)
│
├── docs/                        # 📚 文件 (已整合)
│   ├── architecture/           # 架構文件
│   ├── automation/             # 自動化文件
│   ├── operations/             # 運維文件
│   ├── security/               # 安全文件
│   ├── reports/                # 報告
│   └── ci-cd/                  # CI/CD 文件
│
├── config/                      # ⚙️ 配置文件 (已整合)
│   ├── system-manifest.yaml    # 主系統宣告
│   ├── system-module-map.yaml  # 模組映射
│   ├── unified-config-index.yaml # 統一配置索引
│   ├── auto-fix-bot.yml        # Auto-fix bot 配置
│   ├── cloud-agent-delegation.yml # 雲代理委派
│   └── ...                     # 其他配置
│
├── core/                        # 🏛️ 核心平台服務
│   ├── contracts/              # 合約管理
│   │   └── contracts-L1/       # L1 合約服務
│   ├── advisory-database/      # 漏洞資料庫
│   └── unified_integration/    # 統一整合層
│
├── mcp-servers/                 # 🖥️ MCP 伺服器實作
├── agent/                       # 🤖 代理程式
├── runtime/                     # ⚡ 運行時
├── shared/                      # 📦 共用資源
├── bridges/                     # 🌉 系統橋接
├── contracts/                   # 📝 外部合約定義
├── attest-build-provenance-main/ # 🔐 建置認證
├── v1-python-drones/            # 🚁 V1 Python 無人機
└── v2-multi-islands/            # 🏝️ V2 多島嶼系統
```

---

## 📊 目錄整合摘要 / Directory Consolidation Summary

| 整合前目錄 | 整合後位置 | 說明 |
|-----------|-----------|------|
| `intelligent-automation/` | `automation/intelligent/` | 智能自動化 |
| `intelligent-hyperautomation/` | `automation/hyperautomation/` | 超自動化 |
| `automation-architect/` | `automation/architect/` | 自動化架構師 |
| `autonomous-system/` | `automation/autonomous/` | 自主系統 |
| `advanced-architecture/` | `frontend/ui/` | 架構視覺化 (已整合) |
| `advanced-system-src/` | `frontend/ui/` | 系統 UI 源碼 (已整合) |
| `advanced-system-dist/` | `frontend/dist/` | 編譯產出 |
| `k8s/` | `infrastructure/kubernetes/` | Kubernetes 配置 |
| `monitoring/` | `infrastructure/monitoring/` | 監控配置 |
| `canary/` | `infrastructure/canary/` | Canary 部署 |
| `drift/` | `infrastructure/drift/` | 漂移檢測 |
| `test-vectors/` | `tests/vectors/` | 測試向量 |
| `performance-tests/` | `tests/performance/` | 效能測試 |
| `policy/` | `governance/policies/` | 政策定義 |
| `schemas/` | `governance/schemas/` | Schema 定義 |
| `sbom/` | `governance/sbom/` | SBOM |
| `audit/` | `governance/audit/` | 稽核日誌 |
| `scripts/` | `tools/scripts/` | 自動化腳本 |
| `ci/` | `tools/ci/` | CI 輔助工具 |
| `runbooks/` | `ops/runbooks/` | 運維手冊 |
| `reports/` | `ops/reports/` | 報告 |
| `artifacts/` | `ops/artifacts/` | 建置產物 |
| `migration/` | `ops/migration/` | 遷移工具 |
| `onboarding/` | `ops/onboarding/` | 入門指南 |

---

## 📈 統計 / Statistics

- **整合前根目錄數**: ~40+
- **整合後根目錄數**: ~21
- **減少比例**: ~50%

---

## 🔍 目錄用途說明 / Directory Purpose Description

| 目錄 | 說明 |
|------|------|
| `automation/` | 所有自動化相關模組 |
| `frontend/` | 所有前端應用 |
| `infrastructure/` | 基礎設施配置 (K8s, 監控等) |
| `tests/` | 所有測試相關 |
| `governance/` | 治理、政策、Schema |
| `tools/` | 工具與腳本 |
| `ops/` | 運維相關 |
| `docs/` | 文件 |
| `config/` | 配置文件 |
| `core/` | 核心平台服務 |
| `mcp-servers/` | MCP 伺服器實作 |
| `agent/` | 代理程式 |
| `runtime/` | 運行時 |
| `shared/` | 共用資源 |

---

**產生腳本 / Generated by**: Manual update after directory consolidation  
**專案 / Project**: SynergyMesh  
**儲存庫 / Repository**: [Unmanned-Island-admin/SynergyMesh](https://github.com/Unmanned-Island-admin/SynergyMesh)
