# HLP Executor Core Plugin - 目錄與檔案整合藍圖

## 藍圖說明

此文件展示 HLP Executor Core Plugin 整合後的目錄結構變化，只涵蓋受影響的範圍。

**圖例**:
- 📁 目錄
- 📄 新建檔案（P0/P1/P2）
- 📝 更新檔案
- 🗑️ 將被清理的檔案

---

## 一、完整整合目錄樹

```
unmanned-island/
├── config/                                    # 配置目錄
│   ├── dependencies.yaml                      # 📝 更新：新增 HLP 依賴 (P0)
│   ├── system-module-map.yaml                 # 📝 更新：新增 HLP 模組映射 (P0)
│   ├── unified-config-index.yaml              # 📝 更新：新增向量配置 (P1)
│   ├── monitoring.yaml                        # 📝 更新：新增 HLP 日誌配置 (P1)
│   ├── safety-mechanisms.yaml                 # 📝 更新：新增斷路器與回滾配置 (P1)
│   ├── security-network-config.yml            # 📝 更新：新增量子安全密碼 (P2)
│   └── integrations/                          # 📁 整合端點配置目錄
│       ├── quantum-integration.yaml           # 📄 新建：量子後端整合 (P1)
│       ├── knowledge-graph-integration.yaml   # 📄 新建：知識圖譜整合 (P1)
│       └── observability-integration.yaml     # 📄 新建：可觀測性整合 (P2)
│
├── core/                                      # 核心功能目錄
│   ├── safety_mechanisms/                     # 📁 安全機制目錄
│   │   ├── partial_rollback.py               # 📄 新建：部分回滾管理器 (P0)
│   │   ├── checkpoint_manager.py             # 📄 新建：檢查點管理器 (P1)
│   │   └── retry_policies.py                 # 📝 更新：新增 HLP 重試策略 (P1)
│   │
│   └── slsa_provenance/                       # 📁 SLSA 證據目錄
│       └── plugins/                           # 📁 插件證據目錄
│           └── hlp-executor-core/             # 📄 新建：HLP 證據目錄 (P0)
│               ├── README.md                  # 供應鏈安全說明
│               ├── sbom.spdx.json             # SBOM (軟體物料清單)
│               ├── provenance.intoto.json     # 構建證明
│               └── signatures/                # 簽名目錄
│                   └── cosign.bundle          # Cosign 簽名
│
├── governance/                                # 治理目錄
│   ├── registry/                              # 📁 註冊表目錄
│   │   └── plugins/                           # 📁 插件註冊目錄
│   │       └── hlp-executor-core.yaml         # 📄 新建：HLP 插件註冊清單 (P0)
│   │
│   ├── schemas/                               # 📁 Schema 目錄
│   │   └── state-machine.schema.json          # 📄 新建：狀態機 JSON Schema (P1)
│   │
│   └── policies/                              # 📁 政策目錄
│       └── security/                          # 📁 安全政策目錄
│           └── hlp-executor-security-policy.yaml  # 📄 新建：HLP 安全政策 (P1)
│
├── infrastructure/                            # 基礎設施目錄
│   ├── kubernetes/                            # 📁 Kubernetes 配置目錄
│   │   ├── deployments/                       # 📁 部署目錄
│   │   │   └── hlp-executor-core.yaml         # 📄 新建：HLP Deployment (P0)
│   │   │
│   │   ├── rbac/                              # 📁 RBAC 目錄
│   │   │   └── hlp-executor-rbac.yaml         # 📄 新建：ServiceAccount + Role (P0)
│   │   │
│   │   ├── network-policies/                  # 📁 網絡策略目錄
│   │   │   └── hlp-executor-netpol.yaml       # 📄 新建：網絡策略 (P0)
│   │   │
│   │   ├── storage/                           # 📁 存儲目錄
│   │   │   └── hlp-executor-storage.yaml      # 📄 新建：PVC + ConfigMap (P0)
│   │   │
│   │   └── autoscaling/                       # 📁 自動擴展目錄
│   │       └── hlp-executor-hpa.yaml          # 📄 新建：HPA 配置 (P1)
│   │
│   ├── monitoring/                            # 📁 監控目錄
│   │   ├── prometheus/                        # 📁 Prometheus 目錄
│   │   │   └── servicemonitors/               # 📁 ServiceMonitor 目錄
│   │   │       └── hlp-executor-metrics.yaml  # 📄 新建：指標抓取配置 (P1)
│   │   │
│   │   ├── grafana/                           # 📁 Grafana 目錄
│   │   │   └── dashboards/                    # 📁 儀表板目錄
│   │   │       └── hlp-executor-dashboard.json # 📄 新建：可視化儀表板 (P2)
│   │   │
│   │   └── otel/                              # 📁 OpenTelemetry 目錄
│   │       └── hlp-executor-otel-config.yaml  # 📄 新建：OTel 配置 (P2)
│   │
│   └── canary/                                # 📁 Canary 部署目錄
│       └── hlp-executor-canary.yaml           # 📄 新建：Canary 配置 (P2)
│
├── automation/                                # 自動化目錄
│   └── intelligent/                           # 📁 智能自動化目錄
│       ├── dag_executor.py                    # 📄 新建：DAG 執行器 (P2)
│       └── rollback_analyzer.py               # 📄 新建：回滾分析器 (P2)
│
├── tools/                                     # 工具目錄
│   ├── governance/                            # 📁 治理工具目錄
│   │   └── state-machine-validator.py         # 📄 新建：狀態機驗證工具 (P2)
│   │
│   ├── scripts/                               # 📁 腳本目錄
│   │   ├── verify-hlp-integration-p0.sh       # 📄 新建：P0 驗證腳本
│   │   └── cleanup-hlp-legacy-scratch.sh      # 📄 新建：清理腳本
│   │
│   └── maintenance/                           # 📁 維護工具目錄
│       └── cleanup-executor-state.sh          # 📄 新建：狀態清理腳本 (P1)
│
├── docs/                                      # 文件目錄
│   ├── DOCUMENTATION_INDEX.md                 # 📝 更新：新增 HLP 文件索引 (P1)
│   │
│   ├── architecture/                          # 📁 架構目錄
│   │   ├── EXECUTION_MODEL.md                 # 📄 新建：執行模型文件 (P0)
│   │   ├── CHECKPOINT_STRATEGY.md             # 📄 新建：檢查點策略文件 (P1)
│   │   └── RECOVERY_MODE.md                   # 📄 新建：恢復模式文件 (P1)
│   │
│   ├── operations/                            # 📁 運維目錄
│   │   ├── runbooks/                          # 📁 運維手冊目錄
│   │   │   ├── HLP_EXECUTOR_ERROR_HANDLING.md # 📄 新建：錯誤處理手冊 (P1)
│   │   │   ├── HLP_EXECUTOR_EMERGENCY.md      # 📄 新建：緊急程序手冊 (P1)
│   │   │   └── HLP_EXECUTOR_MAINTENANCE.md    # 📄 新建：維護程序手冊 (P1)
│   │   │
│   │   ├── deployment/                        # 📁 部署目錄
│   │   │   ├── HLP_EXECUTOR_DEPLOYMENT_CHECKLIST.md # 📄 新建：部署檢查清單 (P1)
│   │   │   └── BLUE_GREEN_STRATEGY.md         # 📄 新建：Blue-Green 策略 (P2)
│   │   │
│   │   └── slo/                               # 📁 SLO 目錄
│   │       └── HLP_EXECUTOR_SLO.md            # 📄 新建：SLO 指標文件 (P1)
│   │
│   └── refactor_playbooks/                    # 📁 重構劇本目錄
│       ├── 01_deconstruction/                 # 📁 解構劇本目錄
│       │   └── HLP_EXECUTOR_CORE_DECONSTRUCTION.md # 📄 已創建：解構分析
│       │
│       ├── 02_integration/                    # 📁 集成劇本目錄
│       │   └── HLP_EXECUTOR_CORE_INTEGRATION_MAPPING.md # 📄 已創建：整合映射
│       │
│       ├── 03_refactor/                       # 📁 重構劇本目錄
│       │   ├── HLP_EXECUTOR_CORE_ACTION_PLAN.md # 📄 已創建：行動計畫
│       │   ├── HLP_EXECUTOR_CORE_LEGACY_CLEANUP.md # 📄 已創建：清理計畫
│       │   └── HLP_EXECUTOR_CORE_DIRECTORY_BLUEPRINT.md # 📄 本文件
│       │
│       └── _legacy_scratch/                   # 📁 暫存目錄
│           ├── README.md                      # 🗑️ 將被清理（整合完成後）
│           └── README.md.INTEGRATED           # 📄 整合標記（清理時創建）
│
├── tests/                                     # 測試目錄
│   ├── unit/                                  # 📁 單元測試目錄
│   │   └── hlp-executor/                      # 📄 新建：HLP 單元測試目錄 (P1)
│   │       ├── jest.config.js                 # Jest 配置
│   │       ├── partial_rollback.test.ts       # 部分回滾測試
│   │       └── checkpoint_manager.test.ts     # 檢查點管理測試
│   │
│   ├── integration/                           # 📁 整合測試目錄
│   │   └── hlp-executor/                      # 📄 新建：HLP 整合測試 (P2)
│   │       └── test-setup.yaml                # 測試環境配置
│   │
│   ├── chaos/                                 # 📁 混沌工程目錄
│   │   └── hlp-executor-chaos-scenarios.yaml  # 📄 新建：混沌場景 (P2)
│   │
│   └── performance/                           # 📁 性能測試目錄
│       └── hlp-executor-k6-script.js          # 📄 新建：k6 腳本 (P2)
│
├── templates/                                 # 模板目錄
│   └── plugins/                               # 📁 插件模板目錄
│       └── quantum-yaml-plugin-template.yaml  # 📄 新建：插件模板 (P2)
│
└── CHANGELOG.md                               # 📝 更新：新增 HLP Executor Core (P1)
```

---

## 二、按階段劃分的目錄變化

### 階段一：P0 整合（關鍵路徑）

```
unmanned-island/
├── config/
│   ├── dependencies.yaml                      # ✅ 更新
│   └── system-module-map.yaml                 # ✅ 更新
│
├── core/
│   ├── safety_mechanisms/
│   │   └── partial_rollback.py               # ✅ 新建
│   └── slsa_provenance/plugins/
│       └── hlp-executor-core/                 # ✅ 新建目錄
│
├── governance/registry/plugins/
│   └── hlp-executor-core.yaml                 # ✅ 新建
│
├── infrastructure/kubernetes/
│   ├── deployments/hlp-executor-core.yaml     # ✅ 新建
│   ├── rbac/hlp-executor-rbac.yaml            # ✅ 新建
│   ├── network-policies/hlp-executor-netpol.yaml # ✅ 新建
│   └── storage/hlp-executor-storage.yaml      # ✅ 新建
│
└── docs/
    ├── architecture/EXECUTION_MODEL.md        # ✅ 新建
    └── refactor_playbooks/
        ├── 01_deconstruction/HLP_EXECUTOR_CORE_DECONSTRUCTION.md
        ├── 02_integration/HLP_EXECUTOR_CORE_INTEGRATION_MAPPING.md
        └── 03_refactor/HLP_EXECUTOR_CORE_ACTION_PLAN.md
```

### 階段二：P1 整合（核心功能）

```
unmanned-island/
├── config/
│   ├── unified-config-index.yaml              # ✅ 更新
│   ├── monitoring.yaml                        # ✅ 更新
│   ├── safety-mechanisms.yaml                 # ✅ 更新
│   └── integrations/
│       ├── quantum-integration.yaml           # ✅ 新建
│       └── knowledge-graph-integration.yaml   # ✅ 新建
│
├── core/safety_mechanisms/
│   ├── checkpoint_manager.py                  # ✅ 新建
│   └── retry_policies.py                     # ✅ 更新
│
├── governance/
│   ├── schemas/state-machine.schema.json      # ✅ 新建
│   └── policies/security/hlp-executor-security-policy.yaml # ✅ 新建
│
├── infrastructure/
│   ├── kubernetes/autoscaling/hlp-executor-hpa.yaml # ✅ 新建
│   └── monitoring/prometheus/servicemonitors/
│       └── hlp-executor-metrics.yaml          # ✅ 新建
│
├── docs/
│   ├── DOCUMENTATION_INDEX.md                 # ✅ 更新
│   ├── architecture/
│   │   ├── CHECKPOINT_STRATEGY.md             # ✅ 新建
│   │   └── RECOVERY_MODE.md                   # ✅ 新建
│   └── operations/
│       ├── runbooks/
│       │   ├── HLP_EXECUTOR_ERROR_HANDLING.md # ✅ 新建
│       │   ├── HLP_EXECUTOR_EMERGENCY.md      # ✅ 新建
│       │   └── HLP_EXECUTOR_MAINTENANCE.md    # ✅ 新建
│       ├── deployment/HLP_EXECUTOR_DEPLOYMENT_CHECKLIST.md # ✅ 新建
│       └── slo/HLP_EXECUTOR_SLO.md            # ✅ 新建
│
├── tests/unit/hlp-executor/                   # ✅ 新建目錄
│
├── tools/maintenance/cleanup-executor-state.sh # ✅ 新建
│
└── CHANGELOG.md                               # ✅ 更新
```

### 階段三：P2 整合（優化增強）

```
unmanned-island/
├── config/
│   ├── security-network-config.yml            # ✅ 更新
│   └── integrations/observability-integration.yaml # ✅ 新建
│
├── automation/intelligent/
│   ├── dag_executor.py                        # ✅ 新建
│   └── rollback_analyzer.py                   # ✅ 新建
│
├── infrastructure/
│   ├── monitoring/
│   │   ├── grafana/dashboards/hlp-executor-dashboard.json # ✅ 新建
│   │   └── otel/hlp-executor-otel-config.yaml # ✅ 新建
│   └── canary/hlp-executor-canary.yaml        # ✅ 新建
│
├── tools/governance/state-machine-validator.py # ✅ 新建
│
├── docs/operations/deployment/BLUE_GREEN_STRATEGY.md # ✅ 新建
│
├── tests/
│   ├── integration/hlp-executor/              # ✅ 新建目錄
│   ├── chaos/hlp-executor-chaos-scenarios.yaml # ✅ 新建
│   └── performance/hlp-executor-k6-script.js  # ✅ 新建
│
└── templates/plugins/quantum-yaml-plugin-template.yaml # ✅ 新建
```

---

## 三、檔案統計

### 新增檔案統計

| 類別 | P0 | P1 | P2 | 總計 |
|------|----|----|----|----|
| **配置檔案** | 2 | 5 | 2 | 9 |
| **Python 模組** | 1 | 2 | 3 | 6 |
| **K8s 清單** | 4 | 2 | 2 | 8 |
| **架構文件** | 1 | 2 | 1 | 4 |
| **運維手冊** | 0 | 7 | 0 | 7 |
| **監控配置** | 0 | 1 | 3 | 4 |
| **測試配置** | 0 | 1 | 3 | 4 |
| **工具腳本** | 0 | 1 | 2 | 3 |
| **模板** | 0 | 0 | 1 | 1 |
| **治理檔案** | 1 | 2 | 0 | 3 |
| **SLSA 目錄** | 1 | 0 | 0 | 1 |
| **總計** | **10** | **23** | **17** | **50** |

### 更新檔案統計

| 檔案 | 優先級 | 變更類型 |
|------|--------|---------|
| `config/dependencies.yaml` | P0 | 新增 HLP 依賴條目 |
| `config/system-module-map.yaml` | P0 | 新增 HLP 模組映射 |
| `config/unified-config-index.yaml` | P1 | 新增向量配置 |
| `config/monitoring.yaml` | P1 | 新增日誌配置 |
| `config/safety-mechanisms.yaml` | P1 | 新增斷路器與回滾配置 |
| `config/security-network-config.yml` | P2 | 新增量子安全密碼 |
| `core/safety_mechanisms/retry_policies.py` | P1 | 新增 HLP 重試策略函數 |
| `docs/DOCUMENTATION_INDEX.md` | P1 | 新增 HLP 文件索引 |
| `CHANGELOG.md` | P1 | 新增版本變更記錄 |

---

## 四、目錄所有權與維護責任

| 目錄 | 負責團隊 | 維護週期 | 變更審批 |
|------|---------|---------|---------|
| `config/` | Platform Team | 每次配置變更 | Tech Lead |
| `core/safety_mechanisms/` | Safety Team | 每次代碼變更 | Security Review |
| `governance/` | Governance Team | 每季度審查 | Compliance Officer |
| `infrastructure/kubernetes/` | DevOps Team | 每次部署 | SRE Lead |
| `infrastructure/monitoring/` | Observability Team | 每月優化 | SRE Lead |
| `docs/architecture/` | Architecture Team | 每季度更新 | Tech Architect |
| `docs/operations/` | SRE Team | 每次運維變更 | SRE Lead |
| `automation/` | Automation Team | 持續改進 | Platform Lead |
| `tests/` | QA Team | 每次發布 | QA Lead |

---

## 五、整合影響範圍分析

### 5.1 高影響模組（需要協調）
- ✅ **config/system-module-map.yaml**: 影響服務發現
- ✅ **governance/registry/**: 影響插件註冊系統
- ✅ **infrastructure/kubernetes/**: 影響集群資源
- ✅ **core/safety_mechanisms/**: 影響安全機制

### 5.2 中影響模組（需要通知）
- ✅ **config/monitoring.yaml**: 影響日誌收集
- ✅ **docs/DOCUMENTATION_INDEX.md**: 影響文件查找
- ✅ **CHANGELOG.md**: 影響版本追蹤

### 5.3 低影響模組（獨立新增）
- ✅ **tests/**: 新增測試，不影響現有測試
- ✅ **templates/**: 新增模板，可選使用
- ✅ **automation/intelligent/**: 新增工具，獨立運行

---

## 六、整合後的系統架構視圖

```
┌─────────────────────────────────────────────────────────────┐
│                  Unmanned Island System                      │
│                                                              │
│  ┌────────────────┐   ┌────────────────┐   ┌──────────────┐│
│  │  Entry Points  │   │  Core Modules  │   │ Governance   ││
│  │                │   │                │   │              ││
│  │  • REST API    │──▶│  • AI Engine   │──▶│  • Policies  ││
│  │  • gRPC API    │   │  • Safety Mech │   │  • Registry  ││
│  │  • GraphQL     │   │  • HLP Executor│◀──│  • Schemas   ││
│  └────────────────┘   └────────────────┘   └──────────────┘│
│           │                     │                     │      │
│           ▼                     ▼                     ▼      │
│  ┌────────────────┐   ┌────────────────┐   ┌──────────────┐│
│  │ Infrastructure │   │  Observability │   │  Automation  ││
│  │                │   │                │   │              ││
│  │  • K8s Deploy  │   │  • Prometheus  │   │  • DAG Exec  ││
│  │  • RBAC        │   │  • Grafana     │   │  • Rollback  ││
│  │  • NetPol      │   │  • OTel        │   │  • Analyzer  ││
│  │  • Storage     │   │  • Logging     │   │              ││
│  └────────────────┘   └────────────────┘   └──────────────┘│
│                                                              │
│             HLP Executor Core Plugin Layer                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 七、驗證檢查點

### 7.1 目錄結構驗證

```bash
# 驗證所有目錄已創建
for dir in \
  "config/integrations" \
  "core/slsa_provenance/plugins/hlp-executor-core" \
  "governance/registry/plugins" \
  "governance/schemas" \
  "governance/policies/security" \
  "infrastructure/kubernetes/deployments" \
  "infrastructure/kubernetes/rbac" \
  "infrastructure/kubernetes/network-policies" \
  "infrastructure/kubernetes/storage" \
  "infrastructure/kubernetes/autoscaling" \
  "infrastructure/monitoring/prometheus/servicemonitors" \
  "infrastructure/monitoring/grafana/dashboards" \
  "infrastructure/monitoring/otel" \
  "infrastructure/canary" \
  "automation/intelligent" \
  "tools/governance" \
  "tools/scripts" \
  "tools/maintenance" \
  "docs/architecture" \
  "docs/operations/runbooks" \
  "docs/operations/deployment" \
  "docs/operations/slo" \
  "tests/unit/hlp-executor" \
  "tests/integration/hlp-executor" \
  "tests/chaos" \
  "tests/performance" \
  "templates/plugins"
do
  if [ -d "$dir" ]; then
    echo "✅ $dir exists"
  else
    echo "❌ $dir missing"
  fi
done
```

### 7.2 檔案完整性驗證

```bash
# 驗證所有 P0 檔案已創建
cat > /tmp/verify-p0-files.txt << 'EOF'
governance/registry/plugins/hlp-executor-core.yaml
infrastructure/kubernetes/deployments/hlp-executor-core.yaml
infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml
infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml
infrastructure/kubernetes/storage/hlp-executor-storage.yaml
core/safety_mechanisms/partial_rollback.py
core/slsa_provenance/plugins/hlp-executor-core/README.md
docs/architecture/EXECUTION_MODEL.md
EOF

while IFS= read -r file; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ $file missing"
  fi
done < /tmp/verify-p0-files.txt
```

### 7.3 YAML 語法驗證

```bash
# 驗證所有 YAML 檔案語法正確
find config/ infrastructure/ governance/ -name "*.yaml" -o -name "*.yml" | \
  xargs -I {} bash -c 'python3 -c "import yaml; yaml.safe_load(open(\"{}\"))" && echo "✅ {}" || echo "❌ {}"'
```

---

## 八、回滾指引

如果整合出現問題，需要回滾到整合前狀態：

### 8.1 快速回滾（保留新檔案，恢復修改）

```bash
# 1. 恢復被修改的檔案
git checkout HEAD -- \
  config/dependencies.yaml \
  config/system-module-map.yaml \
  config/unified-config-index.yaml \
  config/monitoring.yaml \
  config/safety-mechanisms.yaml \
  config/security-network-config.yml \
  core/safety_mechanisms/retry_policies.py \
  docs/DOCUMENTATION_INDEX.md \
  CHANGELOG.md

# 2. 移除新增的 K8s 資源（如已部署）
kubectl delete -f infrastructure/kubernetes/deployments/hlp-executor-core.yaml --ignore-not-found
kubectl delete -f infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml --ignore-not-found
kubectl delete -f infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml --ignore-not-found
kubectl delete -f infrastructure/kubernetes/storage/hlp-executor-storage.yaml --ignore-not-found

echo "✅ 回滾完成，新增檔案已保留"
```

### 8.2 完全回滾（刪除所有新檔案）

```bash
# 警告：此操作將刪除所有 HLP Executor 相關檔案

# 1. 恢復被修改的檔案
git checkout HEAD -- config/ core/ docs/DOCUMENTATION_INDEX.md CHANGELOG.md

# 2. 刪除新增的目錄與檔案
rm -rf \
  governance/registry/plugins/hlp-executor-core.yaml \
  governance/schemas/state-machine.schema.json \
  governance/policies/security/hlp-executor-security-policy.yaml \
  infrastructure/kubernetes/deployments/hlp-executor-core.yaml \
  infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml \
  infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml \
  infrastructure/kubernetes/storage/hlp-executor-storage.yaml \
  infrastructure/kubernetes/autoscaling/hlp-executor-hpa.yaml \
  infrastructure/monitoring/prometheus/servicemonitors/hlp-executor-metrics.yaml \
  infrastructure/monitoring/grafana/dashboards/hlp-executor-dashboard.json \
  infrastructure/monitoring/otel/hlp-executor-otel-config.yaml \
  infrastructure/canary/hlp-executor-canary.yaml \
  core/safety_mechanisms/partial_rollback.py \
  core/safety_mechanisms/checkpoint_manager.py \
  core/slsa_provenance/plugins/hlp-executor-core/ \
  automation/intelligent/dag_executor.py \
  automation/intelligent/rollback_analyzer.py \
  tools/governance/state-machine-validator.py \
  docs/architecture/EXECUTION_MODEL.md \
  docs/architecture/CHECKPOINT_STRATEGY.md \
  docs/architecture/RECOVERY_MODE.md \
  docs/operations/runbooks/HLP_EXECUTOR_* \
  docs/operations/deployment/HLP_EXECUTOR_* \
  docs/operations/deployment/BLUE_GREEN_STRATEGY.md \
  docs/operations/slo/HLP_EXECUTOR_SLO.md \
  tests/unit/hlp-executor/ \
  tests/integration/hlp-executor/ \
  tests/chaos/hlp-executor-chaos-scenarios.yaml \
  tests/performance/hlp-executor-k6-script.js \
  templates/plugins/quantum-yaml-plugin-template.yaml

echo "⚠️  完全回滾完成，所有 HLP Executor 檔案已刪除"
```

---

## 九、後續維護指引

### 9.1 定期檢查

- **每週**: 檢查 K8s 資源狀態、日誌異常
- **每月**: 審查 SLO 達成率、性能指標
- **每季**: 更新架構文件、運維手冊

### 9.2 版本升級

當 HLP Executor Core 版本升級時，需要更新：

1. `governance/registry/plugins/hlp-executor-core.yaml` (版本號)
2. `infrastructure/kubernetes/deployments/hlp-executor-core.yaml` (image tag)
3. `CHANGELOG.md` (變更記錄)
4. `core/slsa_provenance/plugins/hlp-executor-core/` (新版本證據)

### 9.3 廢棄流程

如果未來需要廢棄 HLP Executor Core：

1. 標記為 `deprecated` in registry
2. 通知所有依賴方
3. 提供遷移指引
4. 保留 6 個月觀察期
5. 執行完全回滾流程
6. 歸檔相關文件

---

## 十、總結

此藍圖涵蓋了 HLP Executor Core Plugin 整合的完整目錄結構變化：

- ✅ **50 個新檔案**（10 個 P0，23 個 P1，17 個 P2）
- ✅ **9 個更新檔案**
- ✅ **25 個新目錄**
- ✅ **9 個系統模組**受影響

整合完成後，系統將具備：
- 強大的 DAG 編排能力
- 精細的部分回滾機制
- 完善的可觀測性
- 企業級安全合規
- 完整的運維手冊

**下一步**: 參考 `HLP_EXECUTOR_CORE_ACTION_PLAN.md` 執行 P0/P1/P2 行動。
