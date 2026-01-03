# Canonical Naming Governance v1.0

**RFC-2025-10-25 | Status: Approved | Version: 1.0**

---

## 📋 Executive Summary

Canonical Naming Governance 是 MachineNativeOps 治理框架的核心組成部分，旨在通過**單一權威規範 (Single Source of Truth)** 統一 Kubernetes 資源命名標準，並在 CI/CD、Admission Control、運行時監控等多個階段實現自動化驗證和強制執行。

### 核心目標

1. **統一性**: 所有 Gatekeeper、Conftest、CI/CD 規則從同一個 `machine-spec.yaml` 派生
2. **可追溯性**: 通過 URN/URI 映射實現資源的全局唯一標識
3. **自動化**: 從驗證、修復到遷移的全流程自動化
4. **可擴展性**: 支持多種命名模式和自定義擴展

### 關鍵指標

| 指標 | 目標 | 現狀 | 改進方向 |
|------|------|------|---------|
| Naming Compliance Rate (NCR) | 99.9% | - | 部署 Gatekeeper |
| Validation Failure Rate (VFR) | < 1% | - | CI/CD 集成 |
| Migration Success Rate (MSR) | > 95% | - | 遷移工具開發 |
| Mean Time to Remediation (MTTR) | < 1 hour | - | 自動修復 Playbook |

---

## 🎯 問題背景

### 現有痛點

#### 1. 命名不一致導致的運維困難

```yaml
# 現狀：各團隊命名風格各異
frontend-prod-v2          # 團隊 A
prod-backend-api          # 團隊 B
PaymentService-Production # 團隊 C (大小寫混合)
legacy_auth_system        # 團隊 D (底線)
```

**影響**:

- 自動化工具難以識別環境
- 監控告警規則需要大量正則表達式
- 成本分配和資源盤點困難
- 新人學習曲線陡峭

#### 2. 缺乏統一的命名規範來源

```
當前問題:
├── Gatekeeper: policies/gatekeeper/naming-constraint.yaml (正則: [a-z0-9-]+)
├── Conftest: policies/conftest/naming.rego (正則: ^[a-z-]+$)
├── CI/CD: .github/workflows/validation.yml (正則: [a-z0-9]+)
└── 文檔: docs/naming-guide.md (文字描述: "使用小寫和破折號")

結果: 四處規則不同步，修改一處需要同步四處
```

#### 3. 資源關聯困難

```bash
# 問題：如何關聯以下資源？
Namespace: team-frontend-prod
Service: frontend-api
Ingress: api.frontend.prod.example.com
PVC: frontend-prod-data-pvc

# 缺少統一的 URN 標識
```

#### 4. 遷移和重構風險高

```
歷史遺留資源遷移時的挑戰:
- 不知道哪些資源會發生命名衝突
- 手動遷移容易遺漏依賴關係
- 回滾困難，影響範圍不清
- 缺乏自動化建議工具
```

---

## 🏗️ 解決方案架構

### 1. Single Source of Truth: `machine-spec.yaml`

```yaml
canonical/
└── machine-spec.yaml  ← 唯一權威規範
    ├── naming.canonical_regex: "^(team|tenant|dev|...)$"
    ├── naming.segments: [domain, component, environment, ...]
    ├── required_labels: [environment, tenant, ...]
    ├── urn_mapping.format: "urn:machinenativeops:{domain}:..."
    └── validation_rules: [RULE-001, RULE-002, ...]

衍生工具 (全部從 machine-spec.yaml 自動生成或讀取):
├── Gatekeeper: policies/gatekeeper/namespace-constraints.yaml
├── Conftest: templates/conftest/naming.rego
├── CI/CD: .github/workflows/naming-validation.yml
├── Migration Tool: tools/governance/python/naming-migration.py
├── Examples: src/governance/dimensions/27-templates/examples/
└── Monitoring: policies/observability/naming-metrics-policy.yaml
```

**核心原則**:

- ✅ 修改命名規則 = 只修改 `machine-spec.yaml`
- ✅ 所有工具自動同步或代碼生成更新
- ✅ 版本控制和 Changelog 追蹤所有變更

### 2. 三種 Canonical 命名模式

#### 模式 1: `team-domain-env` (團隊級命名空間)

```yaml
pattern: "^team-{domain}-{environment}$"
regex: "^team-[a-z0-9-]+-(?:dev|test|staging|prod|learn)$"
example: "team-frontend-prod"

use_cases:
  - 微服務團隊命名空間
  - 按團隊隔離資源
  - 適合中小型組織

required_labels:
  team: "frontend-team"
  environment: "prod"
  domain: "frontend"

urn: "urn:machinenativeops:team:frontend:env:prod:v1"
```

**適用場景**:

- 10-50 人的工程團隊
- 每個團隊負責 1-3 個微服務
- 團隊自主管理命名空間

**示例資源結構**:

```
team-frontend-prod/
├── Deployment: frontend-api
├── Service: frontend-api-svc
├── Ingress: api.frontend.prod.example.com
└── ConfigMap: frontend-api-config
```

#### 模式 2: `tenant-workload-env-region` (多租戶多區域)

```yaml
pattern: "^{tenant}-{workload}-{environment}-{region}$"
regex: "^tenant-[a-z0-9-]+-(?:dev|test|staging|prod)-[a-z0-9-]+$"
example: "tenant-payment-prod-uswest"

use_cases:
  - SaaS 多租戶平台
  - 跨區域部署
  - 租戶隔離需求

required_labels:
  tenant: "enterprise-customer-a"
  workload: "payment"
  environment: "prod"
  region: "us-west-2"

urn: "urn:machinenativeops:tenant:payment:env:prod:region:uswest"
```

**適用場景**:

- SaaS 提供商
- 多租戶隔離
- 全球化部署（多區域）

**示例資源結構**:

```
tenant-payment-prod-uswest/
├── StatefulSet: payment-processor
├── Service: payment-api
├── PVC: payment-data-uswest
└── NetworkPolicy: tenant-isolation
```

#### 模式 3: `env-app-version` (多版本共存)

```yaml
pattern: "^{environment}-{app}-{version}$"
regex: "^(?:dev|test|staging|prod)-[a-z0-9-]+-v[0-9]+$"
example: "prod-api-v2"

use_cases:
  - 藍綠部署
  - 金絲雀發布
  - API 版本並存
  - A/B 測試

required_labels:
  environment: "prod"
  app: "api"
  version: "v2"

urn: "urn:machinenativeops:env:prod:app:api:version:v2"
```

**適用場景**:

- 需要多版本 API 共存
- 漸進式發布策略
- 長期維護多個版本

**示例資源結構**:

```
prod-api-v2/
├── Deployment: api-v2
├── Service: api-v2-svc (ClusterIP)
├── Ingress: /v2/* → api-v2-svc
└── ConfigMap: api-v2-config

prod-api-v1/  # 舊版本繼續運行
├── Deployment: api-v1
├── Service: api-v1-svc
└── Ingress: /v1/* → api-v1-svc
```

### 3. URN/URI 映射系統

#### URN 格式定義

```
urn:machinenativeops:{domain}:{component}:env:{environment}:{version}

範例:
urn:machinenativeops:team:frontend:env:prod:v1
urn:machinenativeops:tenant:payment:env:prod:region:uswest
urn:machinenativeops:env:prod:app:api:version:v2
```

#### Kubernetes 資源中的應用

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-frontend-prod
  annotations:
    # Canonical URN - 全局唯一標識
    machinenativeops.io/canonical-urn: "urn:machinenativeops:team:frontend:env:prod:v1"

    # 可選：URI 映射到外部系統
    machinenativeops.io/service-mesh-id: "frontend.prod.svc.cluster.local"
    machinenativeops.io/cost-center: "CC-1234"
    machinenativeops.io/owner: "frontend-team@example.com"

  labels:
    environment: "prod"
    team: "frontend-team"
    tenant: "platform"
    app.kubernetes.io/managed-by: "helm"
```

#### 跨資源關聯查詢

```bash
# 通過 URN 查找所有相關資源
kubectl get all --all-namespaces \
  -l machinenativeops.io/canonical-urn=urn:machinenativeops:team:frontend:env:prod:v1

# 查找特定租戶的所有資源
kubectl get namespaces \
  -l tenant=enterprise-customer-a

# 查找特定環境的所有命名空間
kubectl get namespaces \
  -l environment=prod
```

---

## 🔧 實施細節

### 階段 1: 基礎設施準備

#### 1.1 部署 Gatekeeper

```bash
# 安裝 Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml

# 驗證安裝
kubectl get pods -n gatekeeper-system
kubectl get constrainttemplates

# 部署命名約束
kubectl apply -f policies/gatekeeper/namespace-constraints.yaml

# 測試約束 (Dry-run 模式)
kubectl apply -f src/governance/dimensions/27-templates/examples/sample-namespace.yaml --dry-run=server
```

#### 1.2 配置 Conftest (OPA Rego)

```bash
# 安裝 Conftest
brew install conftest  # macOS
# 或
curl -L -o conftest.tar.gz https://github.com/open-policy-agent/conftest/releases/download/v0.48.0/conftest_0.48.0_Linux_x86_64.tar.gz
tar xzf conftest.tar.gz
sudo mv conftest /usr/local/bin/

# 測試策略
conftest test manifests/ --policy templates/conftest/

# 預期輸出
PASS - manifests/namespace.yaml - Namespace naming follows canonical pattern
FAIL - manifests/bad-namespace.yaml - Namespace name 'BadNamespace' violates naming policy
```

#### 1.3 配置 CI/CD 驗證

**GitHub Actions 配置**:

```yaml
# .github/workflows/naming-validation.yml
name: Naming Governance Validation

on:
  pull_request:
    paths:
      - 'manifests/**'
      - 'terraform/**'
      - 'helm/**'

jobs:
  validate-naming:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install validation tools
        run: |
          pip install pyyaml jsonschema
          curl -L -o conftest https://github.com/open-policy-agent/conftest/releases/download/v0.48.0/conftest_0.48.0_Linux_x86_64
          chmod +x conftest

      - name: Validate against machine-spec
        run: |
          python tools/governance/python/validate_naming.py \
            --spec canonical/machine-spec.yaml \
            --resource manifests/ \
            --strict

      - name: Run Conftest
        run: |
          ./conftest test manifests/ \
            --policy templates/conftest/ \
            --output json > conftest-results.json

      - name: Upload results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: validation-results
          path: |
            conftest-results.json
            validation-report.html

      - name: Comment PR
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('conftest-results.json'));
            const comment = `## ❌ Naming Validation Failed\n\n${results}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### 階段 2: 驗證規則實施

#### 2.1 Gatekeeper ConstraintTemplate

```yaml
# policies/gatekeeper/namespace-constraints.yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8snamespacenamingcanonical
spec:
  crd:
    spec:
      names:
        kind: K8sNamespaceNamingCanonical
      validation:
        openAPIV3Schema:
          type: object
          properties:
            canonicalRegex:
              type: string
            allowedEnvironments:
              type: array
              items:
                type: string
            requiredLabels:
              type: array
              items:
                type: string

  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8snamespacenamingcanonical

        violation[{"msg": msg}] {
          # 檢查資源類型
          input.review.kind.kind == "Namespace"

          # 獲取 Namespace 名稱
          name := input.review.object.metadata.name

          # 檢查是否為豁免資源
          not is_exempted(name)

          # 驗證命名格式
          not regex.match(input.parameters.canonicalRegex, name)

          msg := sprintf("Namespace '%v' does not match canonical pattern '%v'", [name, input.parameters.canonicalRegex])
        }

        violation[{"msg": msg}] {
          input.review.kind.kind == "Namespace"
          name := input.review.object.metadata.name
          not is_exempted(name)

          # 驗證必需標籤
          required := input.parameters.requiredLabels[_]
          not input.review.object.metadata.labels[required]

          msg := sprintf("Namespace '%v' missing required label '%v'", [name, required])
        }

        violation[{"msg": msg}] {
          input.review.kind.kind == "Namespace"
          name := input.review.object.metadata.name
          not is_exempted(name)

          # 驗證環境標籤值
          env := input.review.object.metadata.labels.environment
          allowed := input.parameters.allowedEnvironments
          not contains(allowed, env)

          msg := sprintf("Namespace '%v' has invalid environment '%v', must be one of %v", [name, env, allowed])
        }

        violation[{"msg": msg}] {
          input.review.kind.kind == "Namespace"
          name := input.review.object.metadata.name
          not is_exempted(name)

          # 驗證 URN annotation
          not input.review.object.metadata.annotations["machinenativeops.io/canonical-urn"]

          msg := sprintf("Namespace '%v' missing required annotation 'machinenativeops.io/canonical-urn'", [name])
        }

        is_exempted(name) {
          exemptions := ["kube-system", "kube-public", "kube-node-lease", "default"]
          exemptions[_] == name
        }

        contains(arr, elem) {
          arr[_] == elem
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sNamespaceNamingCanonical
metadata:
  name: namespace-naming-constraint
spec:
  enforcementAction: deny  # deny | dryrun | warn
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
  parameters:
    canonicalRegex: "^(team|tenant|dev|test|staging|prod|learn)-[a-z0-9-]{1,56}[a-z0-9]$"
    allowedEnvironments: ["dev", "test", "staging", "prod", "learn"]
    requiredLabels: ["environment", "tenant"]
```

#### 2.2 Conftest Rego 策略

```rego
# templates/conftest/naming.rego
package main

import future.keywords.contains
import future.keywords.if

# 從 machine-spec.yaml 讀取配置（實際應該動態載入）
canonical_regex := "^(team|tenant|dev|test|staging|prod|learn)-[a-z0-9-]{1,56}[a-z0-9]$"
allowed_environments := ["dev", "test", "staging", "prod", "learn"]
required_labels := ["environment", "tenant"]
exempted_namespaces := ["kube-system", "kube-public", "kube-node-lease", "default"]

# 規則 1: Namespace 命名格式驗證
deny[msg] {
  input.kind == "Namespace"
  name := input.metadata.name
  not is_exempted(name)
  not regex.match(canonical_regex, name)

  msg := sprintf("Namespace '%s' does not match canonical naming pattern. Expected: %s", [name, canonical_regex])
}

# 規則 2: 必需標籤驗證
deny[msg] {
  input.kind == "Namespace"
  name := input.metadata.name
  not is_exempted(name)

  required_label := required_labels[_]
  not input.metadata.labels[required_label]

  msg := sprintf("Namespace '%s' is missing required label '%s'", [name, required_label])
}

# 規則 3: 環境標籤值驗證
deny[msg] {
  input.kind == "Namespace"
  name := input.metadata.name
  not is_exempted(name)

  env := input.metadata.labels.environment
  not contains(allowed_environments, env)

  msg := sprintf("Namespace '%s' has invalid environment '%s'. Allowed: %v", [name, env, allowed_environments])
}

# 規則 4: URN annotation 驗證
warn[msg] {
  input.kind == "Namespace"
  name := input.metadata.name
  not is_exempted(name)
  not input.metadata.annotations["machinenativeops.io/canonical-urn"]

  msg := sprintf("Namespace '%s' is missing recommended URN annotation 'machinenativeops.io/canonical-urn'", [name])
}

# 規則 5: 保留關鍵字驗證
deny[msg] {
  input.kind == "Namespace"
  name := input.metadata.name

  reserved := ["core", "internal", "system", "legacy", "experimental", "kube", "kubernetes"]
  contains_reserved(name, reserved)

  msg := sprintf("Namespace '%s' contains reserved keyword from: %v", [name, reserved])
}

# 輔助函數
is_exempted(name) {
  exempted_namespaces[_] == name
}

contains(arr, elem) {
  arr[_] == elem
}

contains_reserved(name, keywords) {
  keyword := keywords[_]
  contains(name, keyword)
}
```

### 階段 3: 遷移工具開發

#### 3.1 Python 遷移工具

```python
# tools/governance/python/naming-migration.py
#!/usr/bin/env python3
"""
Canonical Naming Migration Tool
用於檢測命名衝突、生成遷移建議、執行批量遷移
"""

import yaml
import argparse
import re
import sys
from typing import Dict, List, Tuple
from kubernetes import client, config

class NamingMigrationTool:
    def __init__(self, spec_path: str):
        """載入 machine-spec.yaml"""
        with open(spec_path, 'r') as f:
            self.spec = yaml.safe_load(f)

        self.canonical_regex = self.spec['spec']['naming']['canonical_regex']
        self.naming_modes = self.spec['spec']['naming']['naming_modes']
        self.reserved_tokens = self.spec['spec']['naming']['reserved_tokens']
        self.environments = [e['name'] for e in self.spec['spec']['naming']['environments']]

    def scan_cluster(self) -> List[Dict]:
        """掃描集群中的所有 Namespace"""
        try:
            config.load_kube_config()
            v1 = client.CoreV1Api()
            namespaces = v1.list_namespace()

            results = []
            for ns in namespaces.items:
                name = ns.metadata.name
                labels = ns.metadata.labels or {}
                annotations = ns.metadata.annotations or {}

                result = {
                    'name': name,
                    'labels': labels,
                    'annotations': annotations,
                    'compliant': self.validate_name(name),
                    'issues': self.check_issues(name, labels, annotations)
                }
                results.append(result)

            return results
        except Exception as e:
            print(f"Error scanning cluster: {e}", file=sys.stderr)
            sys.exit(1)

    def validate_name(self, name: str) -> bool:
        """驗證命名是否符合 canonical pattern"""
        return bool(re.match(self.canonical_regex, name))

    def check_issues(self, name: str, labels: Dict, annotations: Dict) -> List[str]:
        """檢查所有潛在問題"""
        issues = []

        # 檢查命名格式
        if not self.validate_name(name):
            issues.append(f"Name '{name}' does not match canonical pattern")

        # 檢查保留關鍵字
        for token in self.reserved_tokens:
            if token in name:
                issues.append(f"Name contains reserved keyword '{token}'")

        # 檢查必需標籤
        if 'environment' not in labels:
            issues.append("Missing required label 'environment'")
        elif labels['environment'] not in self.environments:
            issues.append(f"Invalid environment '{labels['environment']}'")

        if 'tenant' not in labels:
            issues.append("Missing required label 'tenant'")

        # 檢查 URN annotation
        if 'machinenativeops.io/canonical-urn' not in annotations:
            issues.append("Missing URN annotation 'machinenativeops.io/canonical-urn'")

        return issues

    def detect_conflicts(self, namespaces: List[Dict]) -> List[Dict]:
        """檢測命名衝突"""
        conflicts = []
        name_map = {}

        for ns in namespaces:
            name = ns['name']

            # 檢查重複命名
            if name in name_map:
                conflicts.append({
                    'type': 'duplicate',
                    'name': name,
                    'conflict_with': name_map[name]
                })
            name_map[name] = ns

            # 檢查相似命名（可能導致混淆）
            similar = self.find_similar_names(name, list(name_map.keys()))
            if similar:
                conflicts.append({
                    'type': 'similar',
                    'name': name,
                    'similar_to': similar
                })

        return conflicts

    def find_similar_names(self, name: str, existing: List[str]) -> List[str]:
        """查找相似命名（Levenshtein 距離）"""
        similar = []
        for existing_name in existing:
            if existing_name == name:
                continue

            distance = self.levenshtein_distance(name, existing_name)
            if distance <= 2:  # 距離閾值
                similar.append(existing_name)

        return similar

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """計算編輯距離"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def generate_suggestions(self, namespace: Dict) -> List[str]:
        """為不合規 Namespace 生成命名建議"""
        name = namespace['name']
        labels = namespace['labels']
        suggestions = []

        # 嘗試匹配各種命名模式
        for mode in self.naming_modes:
            try:
                suggestion = self.apply_naming_mode(name, labels, mode)
                if suggestion:
                    suggestions.append({
                        'pattern': mode['id'],
                        'suggested_name': suggestion,
                        'example': mode['example']
                    })
            except Exception as e:
                continue

        # 如果無法匹配，使用 fallback
        if not suggestions:
            env = labels.get('environment', 'dev')
            suggestions.append({
                'pattern': 'fallback',
                'suggested_name': f"team-{self.sanitize_name(name)}-{env}",
                'example': 'team-myapp-prod'
            })

        return suggestions

    def apply_naming_mode(self, name: str, labels: Dict, mode: Dict) -> str:
        """應用特定命名模式"""
        mode_id = mode['id']

        if mode_id == 'team-domain-env':
            domain = labels.get('domain', self.extract_domain(name))
            env = labels.get('environment', 'dev')
            return f"team-{domain}-{env}"

        elif mode_id == 'tenant-workload-env-region':
            tenant = labels.get('tenant', 'default')
            workload = labels.get('workload', self.extract_domain(name))
            env = labels.get('environment', 'dev')
            region = labels.get('region', 'useast')
            return f"tenant-{tenant}-{workload}-{env}-{region}"

        elif mode_id == 'env-app-version':
            env = labels.get('environment', 'dev')
            app = labels.get('app', self.extract_domain(name))
            version = labels.get('version', 'v1')
            return f"{env}-{app}-{version}"

        return None

    def extract_domain(self, name: str) -> str:
        """從現有名稱中提取 domain"""
        # 移除常見前綴/後綴
        cleaned = name.replace('prod-', '').replace('-prod', '')
        cleaned = cleaned.replace('staging-', '').replace('-staging', '')
        cleaned = cleaned.replace('dev-', '').replace('-dev', '')
        cleaned = self.sanitize_name(cleaned)
        return cleaned[:20]  # 限制長度

    def sanitize_name(self, name: str) -> str:
        """清理名稱使其符合規範"""
        # 轉小寫
        name = name.lower()
        # 移除非法字符
        name = re.sub(r'[^a-z0-9-]', '-', name)
        # 移除連續破折號
        name = re.sub(r'-+', '-', name)
        # 移除首尾破折號
        name = name.strip('-')
        return name

    def generate_migration_plan(self, namespaces: List[Dict], output_path: str):
        """生成完整遷移計劃"""
        plan = {
            'apiVersion': 'governance.machinenativeops.io/v1alpha1',
            'kind': 'MigrationPlan',
            'metadata': {
                'name': 'naming-migration-plan',
                'generated_at': '2025-01-15T00:00:00Z'
            },
            'spec': {
                'total_resources': len(namespaces),
                'non_compliant': sum(1 for ns in namespaces if not ns['compliant']),
                'batches': []
            }
        }

        # 分批遷移
        non_compliant = [ns for ns in namespaces if not ns['compliant']]
        batch_size = 10

        for i in range(0, len(non_compliant), batch_size):
            batch = non_compliant[i:i+batch_size]
            batch_plan = {
                'batch_id': f"batch-{i//batch_size + 1}",
                'resources': []
            }

            for ns in batch:
                suggestions = self.generate_suggestions(ns)
                batch_plan['resources'].append({
                    'current_name': ns['name'],
                    'issues': ns['issues'],
                    'suggestions': suggestions
                })

            plan['spec']['batches'].append(batch_plan)

        # 寫入文件
        with open(output_path, 'w') as f:
            yaml.dump(plan, f, default_flow_style=False, allow_unicode=True)

        print(f"Migration plan generated: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Canonical Naming Migration Tool')
    parser.add_argument('--spec', required=True, help='Path to machine-spec.yaml')
    parser.add_argument('--scan', action='store_true', help='Scan cluster for namespaces')
    parser.add_argument('--detect-conflicts', action='store_true', help='Detect naming conflicts')
    parser.add_argument('--generate-plan', help='Generate migration plan (output path)')

    args = parser.parse_args()

    tool = NamingMigrationTool(args.spec)

    if args.scan:
        namespaces = tool.scan_cluster()

        # 統計
        total = len(namespaces)
        compliant = sum(1 for ns in namespaces if ns['compliant'])
        non_compliant = total - compliant

        print(f"\n=== Namespace Scan Results ===")
        print(f"Total: {total}")
        print(f"Compliant: {compliant} ({compliant/total*100:.1f}%)")
        print(f"Non-compliant: {non_compliant} ({non_compliant/total*100:.1f}%)")

        print(f"\n=== Non-compliant Namespaces ===")
        for ns in namespaces:
            if not ns['compliant']:
                print(f"\n{ns['name']}:")
                for issue in ns['issues']:
                    print(f"  - {issue}")

        if args.detect_conflicts:
            conflicts = tool.detect_conflicts(namespaces)
            if conflicts:
                print(f"\n=== Detected Conflicts ===")
                for conflict in conflicts:
                    print(f"{conflict['type']}: {conflict}")

        if args.generate_plan:
            tool.generate_migration_plan(namespaces, args.generate_plan)

if __name__ == '__main__':
    main()
```

---

## 📊 監控和可觀測性

### Prometheus Metrics

```yaml
# 從 policies/observability/naming-metrics-policy.yaml 引用
metrics:
  - naming_compliance_rate
  - naming_compliance_good
  - naming_compliance_bad
  - naming_validation_failure_total
  - naming_migration_success_total
  - naming_migration_failure_total
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Canonical Naming Governance",
    "panels": [
      {
        "title": "Naming Compliance Rate",
        "targets": [
          {
            "expr": "(sum(naming_compliance_good) / (sum(naming_compliance_good) + sum(naming_compliance_bad))) * 100"
          }
        ],
        "type": "gauge",
        "thresholds": [95, 99]
      },
      {
        "title": "Non-compliant Resources by Environment",
        "targets": [
          {
            "expr": "sum(naming_compliance_bad) by (environment)"
          }
        ],
        "type": "bar"
      }
    ]
  }
}
```

---

## 🔄 遷移最佳實踐

### 遷移階段 (6 階段)

詳見 `policies/migration/naming-migration-policy.yaml`:

1. **Discovery (資產發現)**: 掃描並盤點所有資源
2. **Benchmark (制定基準)**: 定義新命名規範
3. **Dry-run (模擬驗證)**: 測試環境模擬執行
4. **Staged Rename (分階段重命名)**: 按批次逐步遷移
5. **Cutover (正式切換)**: 切換流量到新資源
6. **Rollback Plan (回滾預案)**: 準備完整回滾方案

---

## 📚 參考資料

### 內部文檔

- [`canonical/machine-spec.yaml`](../canonical/machine-spec.yaml) - Single Source of Truth
- [`policies/migration/naming-migration-policy.yaml`](../policies/migration/naming-migration-policy.yaml)
- [`policies/validation/ci-validation-policy.yaml`](../policies/validation/ci-validation-policy.yaml)

### 外部參考

詳見 `references/canonical-naming-governance.yaml`

---

**文檔版本**: v1.0
**最後更新**: 2025-01-15
**維護團隊**: Platform Engineering Team
