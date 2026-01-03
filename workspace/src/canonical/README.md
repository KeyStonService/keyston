# Canonical Naming Governance v1.0

**Single Source of Truth for Kubernetes Naming Standards**

> 本文檔是 Platform Engineer 快速理解完整命名治理策略的單頁摘要。
> 詳細規範請參考 [`machine-spec.yaml`](./machine-spec.yaml)

---

## 🎯 核心規則

### 基礎約束

- **允許字符**: `a-z`, `0-9`, `-` (RFC-1123 DNS_LABEL)
- **大小寫**: 僅小寫
- **最大長度**: 63 字符
- **Canonical Regex**: `^(team|tenant|dev|test|staging|prod|learn)-[a-z0-9-]{1,56}[a-z0-9]$`

### 命名段結構

```
[domain] - [component] - [environment] - [region] - [version] - [suffix]
   └─┬─┘      └──┬──┘       └────┬────┘    └──┬─┘    └──┬──┘    └──┬─┘
   必需        必需           必需          可選      可選       可選
```

### 標準環境

| 環境 | 名稱 | 別名 |
|------|------|------|
| 開發 | `dev` | develop, development |
| 測試 | `test` | testing, qa |
| 預生產 | `staging` | stage, preprod, uat |
| 生產 | `prod` | production, live |
| 學習/沙箱 | `learn` | sandbox, demo |

### 保留關鍵字（禁止使用）

`core`, `internal`, `system`, `legacy`, `experimental`, `kube`, `kubernetes`, `default`

---

## 📋 三種 Canonical 命名模式

### 模式 1: `team-domain-env`

```yaml
Pattern: team-{domain}-{environment}
Example: team-frontend-prod
Use Cases:
  - 團隊級 Namespace
  - 微服務命名空間
Required Labels:
  - team
  - environment
  - domain
```

### 模式 2: `tenant-workload-env-region`

```yaml
Pattern: tenant-{workload}-{environment}-{region}
Example: tenant-payment-prod-uswest
Use Cases:
  - 多租戶環境
  - 跨區域部署
Required Labels:
  - tenant
  - workload
  - environment
  - region
```

### 模式 3: `env-app-version`

```yaml
Pattern: {environment}-{app}-{version}
Example: prod-api-v2
Use Cases:
  - 多版本共存
  - 藍綠部署
  - 金絲雀發布
Required Labels:
  - environment
  - app
  - version
```

---

## 🏷️ 必需標籤

所有 Namespace 必須包含：

| 標籤 Key | 值範例 | 驗證 Regex | 範圍 |
|---------|--------|-----------|------|
| `environment` | `prod` | `^(dev\|test\|staging\|prod\|learn)$` | All Namespaces |
| `tenant` | `platform-team` | `^[a-z0-9-]{2,32}$` | All Namespaces |
| `app.kubernetes.io/name` | `frontend` | `^[a-z0-9-]{2,63}$` | Workloads |
| `app.kubernetes.io/managed-by` | `helm` | `^(helm\|kubectl\|terraform\|argocd\|flux)$` | All Resources |

**豁免**: `kube-system`, `kube-public`, `kube-node-lease`, `default`

---

## 🔗 URN/URI 映射

所有 Namespace 必須包含 `machinenativeops.io/canonical-urn` annotation：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-frontend-prod
  annotations:
    machinenativeops.io/canonical-urn: "urn:machinenativeops:team:frontend:env:prod:v1"
  labels:
    environment: "prod"
    team: "frontend-team"
    tenant: "platform"
```

**URN 格式**: `urn:machinenativeops:{domain}:{component}:env:{environment}:{version}`

---

## ✅ 驗證工具鏈

### CI/CD 驗證（PR 時阻斷）

```bash
# GitHub Actions
.github/workflows/naming-validation.yml

# 驗證命令
python tools/governance/python/validate_naming.py \
  --spec canonical/machine-spec.yaml \
  --resource manifests/
```

### Conftest (OPA Rego)

```bash
# 策略文件
templates/conftest/naming.rego

# 執行驗證
conftest test manifests/ --policy templates/conftest/
```

### Gatekeeper (Admission Control)

```yaml
# ConstraintTemplate
policies/gatekeeper/namespace-constraints.yaml

# 強制模式: deny | dryrun | warn
Enforcement: deny
```

### 監控告警

- **Prometheus Metrics**: `policies/observability/naming-metrics-policy.yaml`
- **Alert Rules**: `templates/prometheus/naming-alert-rules.yaml`
- **Grafana Dashboard**: `templates/grafana/naming-compliance-dashboard.json`

---

## 🚀 快速開始

### 1. 創建符合規範的 Namespace

```bash
# 使用模板
kubectl apply -f templates/k8s/namespace.canonical.template.yaml
```

### 2. 驗證現有資源

```bash
# 掃描所有 Namespace
python tools/governance/python/validate_naming.py \
  --spec canonical/machine-spec.yaml \
  --scan-cluster

# 檢測衝突
python tools/governance/python/naming-migration.py \
  --spec canonical/machine-spec.yaml \
  --detect-conflicts
```

### 3. 遷移不合規資源

```bash
# 生成遷移建議
python tools/governance/python/naming-migration.py \
  --spec canonical/machine-spec.yaml \
  --generate-suggestions \
  --output migration-plan.yaml

# 執行遷移（Dry-run）
python tools/governance/python/naming-migration.py \
  --plan migration-plan.yaml \
  --dry-run

# 執行遷移（實際）
python tools/governance/python/naming-migration.py \
  --plan migration-plan.yaml \
  --execute
```

---

## 📊 SLA 目標

| 指標 | 目標 | 告警閾值 |
|------|------|---------|
| Naming Compliance Rate (NCR) | 99.9% | < 95% |
| Validation Failure Rate (VFR) | < 1% | > 5% |
| Migration Success Rate (MSR) | > 95% | < 85% |

---

## 🔒 治理強制

### 驗證階段

1. **Pre-commit**: Git hooks (可選)
2. **PR Validation**: GitHub Actions (阻斷)
3. **Admission Control**: Gatekeeper (強制)
4. **Runtime Monitoring**: Prometheus + Grafana (持續)

### 豁免流程

需要豁免的資源必須：

1. 在 `machine-spec.yaml` 的 `exemptions` 中註冊
2. 提供豁免原因
3. 指定批准人和過期時間
4. 記錄在審計日誌

---

## 📚 相關資源

| 資源 | 路徑 |
|------|------|
| 完整規範 | `canonical/machine-spec.yaml` |
| 版本歷史 | `canonical/CHANGELOG.md` |
| 詳細文檔 | `docs/governance/04-canonical-naming-governance.md` |
| 驗證 Schema | `schemas/naming-spec.schema.yaml` |
| 示例資源 | `src/governance/dimensions/27-templates/examples/` |
| 遷移工具 | `tools/governance/python/naming-migration.py` |
| 參考資料 | `references/canonical-naming-governance.yaml` |

---

## 🎓 最佳實踐

### ✅ 推薦做法

- 使用三種 Canonical 模式之一
- 為所有 Namespace 添加 URN annotation
- 在 PR 階段驗證命名合規性
- 啟用 Gatekeeper admission control
- 定期審查豁免清單

### ❌ 避免做法

- 使用保留關鍵字
- 混合大小寫
- 超過 63 字符長度限制
- 缺少必需標籤
- 繞過驗證流程

---

## 🆘 疑難排解

### 問題: Namespace 創建被 Gatekeeper 拒絕

```bash
# 檢查驗證規則
kubectl get constrainttemplates
kubectl describe constraint namespace-naming-constraint

# 查看詳細錯誤
kubectl get events --sort-by='.lastTimestamp'
```

### 問題: 遷移檢測到命名衝突

```bash
# 查看衝突詳情
python tools/governance/python/naming-migration.py \
  --spec canonical/machine-spec.yaml \
  --list-conflicts

# 生成替代建議
python tools/governance/python/naming-migration.py \
  --spec canonical/machine-spec.yaml \
  --suggest-alternatives \
  --conflict-id CONFLICT-001
```

---

## 📞 聯絡支持

- **Governance Team**: <governance-team@example.com>
- **Slack Channel**: `#governance-support`
- **Issue Tracker**: <https://github.com/machinenativeops/governance/issues>
- **Runbook**: <https://wiki.example.com/runbooks/naming-governance>

---

**版本**: v1.0 | **RFC**: RFC-2025-10-25 | **最後更新**: 2025-01-15
