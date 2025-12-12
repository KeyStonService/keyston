# CI/CD 策略

## 概述

本文檔定義了 Intelligent
Hyperautomation 模板套件的持續整合與持續部署策略，確保安全、可追溯與自動化的軟體交付流程。

## CI/CD 原則

### 核心原則

1. **自動化優先**：最大化自動化，減少人為錯誤
2. **安全為本**：每個階段內建安全檢查
3. **快速回饋**：快速發現並修復問題
4. **可追溯性**：完整的審計追蹤
5. **零停機部署**：滾動更新與灰度發布

### 治理要求

- 所有變更通過 Pull Request
- 必須通過所有自動化檢查
- 高風險變更需要人工審批
- 保持完整的變更歷史

## Pre-commit 階段

在代碼提交前執行的本地檢查。

### YAML 驗證

```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit Validation

on:
  pull_request:
    paths:
      - '**.yaml'
      - '**.yml'

jobs:
  yaml-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install yamllint
        run: pip install yamllint

      - name: Lint YAML files
        run: yamllint -c .yamllint .
```

### Kubernetes 清單驗證

```yaml
kubeconform:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Install kubeconform
      run: |
        curl -L https://github.com/yannh/kubeconform/releases/download/v0.6.3/kubeconform-linux-amd64.tar.gz | tar xz
        sudo mv kubeconform /usr/local/bin/

    - name: Validate manifests
      run: |
        kubeconform -strict -summary \
          -kubernetes-version 1.30.0 \
          -output json \
          intelligent-hyperautomation/policies/gatekeeper/
```

### Conftest 策略驗證

```yaml
conftest:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Install Conftest
      run: |
        curl -L https://github.com/open-policy-agent/conftest/releases/download/v0.47.0/conftest_0.47.0_Linux_x86_64.tar.gz | tar xz
        sudo mv conftest /usr/local/bin/

    - name: Test policies
      run: |
        conftest test \
          intelligent-hyperautomation/policies/gatekeeper/ \
          -p intelligent-hyperautomation/policies/rego/ \
          --output json
```

## CI 階段

在 Pull Request 或提交後執行的持續整合檢查。

### Gatekeeper 約束驗證

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  gatekeeper-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Kubernetes
        uses: helm/kind-action@v1.8.0
        with:
          cluster_name: test-cluster

      # Gatekeeper v3.14.0 已驗證與 Kubernetes 1.30 相容，採用明確版本標籤以確保可重現性與審計追蹤
      - name: Install Gatekeeper
        run: |
          kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.14.0/deploy/gatekeeper.yaml
          kubectl wait --for=condition=Ready pod -l control-plane=controller-manager -n gatekeeper-system --timeout=300s

      - name: Dry-run constraints
        run: |
          kubectl apply -f intelligent-hyperautomation/policies/gatekeeper/uav-ad-labels.yaml --dry-run=server
          kubectl apply -f intelligent-hyperautomation/policies/gatekeeper/geo-fencing.yaml --dry-run=server
```

### 文件雜湊計算

```yaml
hash-calculation:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Install b3sum
      run: |
        curl -L https://github.com/BLAKE3-team/BLAKE3/releases/download/1.5.0/b3sum_linux_x64_bin -o b3sum
        chmod +x b3sum
        sudo mv b3sum /usr/local/bin/

    - name: Calculate BLAKE3 hashes
      run: |
        b3sum intelligent-hyperautomation/docs/core-principles.md
        b3sum intelligent-hyperautomation/docs/uav-autonomous-driving-governance.md
        b3sum intelligent-hyperautomation/policies/rego/uav_ad.rego

    - name: Calculate SHA3-512 hashes
      run: |
        openssl dgst -sha3-512 intelligent-hyperautomation/docs/core-principles.md
        openssl dgst -sha3-512 intelligent-hyperautomation/policies/gatekeeper/uav-ad-labels.yaml
```

### SBOM 生成

```yaml
sbom-generation:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Install Syft
      run: |
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

    - name: Generate SBOM
      run: |
        syft packages dir:intelligent-hyperautomation \
          -o cyclonedx-json \
          > intelligent-hyperautomation/docs/sbom.json

    - name: Upload SBOM
      uses: actions/upload-artifact@v4
      with:
        name: sbom
        path: intelligent-hyperautomation/docs/sbom.json
```

### 安全掃描

```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'config'
        scan-ref: 'intelligent-hyperautomation/'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy results
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: 'trivy-results.sarif'
```

## CD 階段

持續部署到目標環境。

### GitOps 部署 (ArgoCD)

```yaml
# argocd-deploy.yml
name: Deploy with ArgoCD

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install ArgoCD CLI
        run: |
          curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
          chmod +x argocd
          sudo mv argocd /usr/local/bin/

      - name: Login to ArgoCD
        run: |
          argocd login ${{ secrets.ARGOCD_SERVER }} \
            --username ${{ secrets.ARGOCD_USERNAME }} \
            --password ${{ secrets.ARGOCD_PASSWORD }}

      - name: Sync application
        run: |
          argocd app sync intelligent-hyperautomation \
            --revision ${{ github.ref_name }}

      - name: Wait for sync
        run: |
          argocd app wait intelligent-hyperautomation \
            --sync \
            --health \
            --timeout 600
```

### GitOps 部署 (Flux)

```yaml
# flux-deploy.yml
name: Deploy with Flux

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Flux CLI
        run: |
          curl -s https://fluxcd.io/install.sh | sudo bash

      - name: Setup Kubeconfig
        run: |
          echo "${{ secrets.KUBECONFIG }}" > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Reconcile Flux
        run: |
          flux reconcile source git intelligent-hyperautomation
          flux reconcile kustomization intelligent-hyperautomation
```

### Server-side Apply

```yaml
server-side-apply:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Setup Kubeconfig
      run: |
        echo "${{ secrets.KUBECONFIG }}" > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Apply constraints
      run: |
        kubectl apply --server-side=true \
          -f intelligent-hyperautomation/policies/gatekeeper/ \
          --force-conflicts
```

## 審計與追蹤

### 變更記錄

每次部署自動生成變更記錄：

```yaml
changelog:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Generate changelog
      run: |
        git log --oneline --no-merges $(git describe --tags --abbrev=0)..HEAD > CHANGELOG.txt

    - name: Append metadata
      run: |
        echo "---" >> CHANGELOG.txt
        echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> CHANGELOG.txt
        echo "Version: ${{ github.ref_name }}" >> CHANGELOG.txt
        echo "Committer: ${{ github.actor }}" >> CHANGELOG.txt
        echo "Commit SHA: ${{ github.sha }}" >> CHANGELOG.txt
```

### 部署審計

記錄所有部署操作：

```yaml
audit-log:
  runs-on: ubuntu-latest
  steps:
    - name: Create audit record
      run: |
        cat << EOF > audit-record.json
        {
          "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
          "version": "${{ github.ref_name }}",
          "actor": "${{ github.actor }}",
          "event": "deployment",
          "target": "production",
          "commit": "${{ github.sha }}",
          "status": "success"
        }
        EOF

    - name: Send to audit system
      run: |
        curl -X POST ${{ secrets.AUDIT_ENDPOINT }} \
          -H "Content-Type: application/json" \
          -d @audit-record.json
```

## 回滾策略

### 自動回滾

檢測到失敗時自動回滾：

```yaml
auto-rollback:
  runs-on: ubuntu-latest
  steps:
    - name: Check deployment health
      id: health
      run: |
        kubectl rollout status deployment/uav-controller -n production --timeout=5m
      continue-on-error: true

    - name: Rollback on failure
      if: steps.health.outcome == 'failure'
      run: |
        kubectl rollout undo deployment/uav-controller -n production
        echo "Deployment rolled back due to health check failure"
```

### 手動回滾流程

```bash
# 1. 識別要回滾的版本
kubectl rollout history deployment/uav-controller -n production

# 2. 回滾到特定版本
kubectl rollout undo deployment/uav-controller -n production --to-revision=3

# 3. 驗證回滾狀態
kubectl rollout status deployment/uav-controller -n production

# 4. Git 標記回滾
git revert <commit-id>
git tag v2.0.1-rollback
git push --tags
```

## 環境策略

### 環境分層

```
Development → Staging → Production
     ↓           ↓          ↓
  自動部署    自動+審批   手動審批
```

### 環境配置

```yaml
# environments/dev.yaml
environment: development
auto_deploy: true
approval_required: false
health_check_timeout: 60s

# environments/staging.yaml
environment: staging
auto_deploy: true
approval_required: true
approvers: ["team-lead"]
health_check_timeout: 120s

# environments/prod.yaml
environment: production
auto_deploy: false
approval_required: true
approvers: ["team-lead", "sre-lead"]
health_check_timeout: 300s
```

## 效能與可靠性

### 並行執行

```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]
    include:
      - environment: dev
        auto_deploy: true
      - environment: staging
        auto_deploy: true
      - environment: prod
        auto_deploy: false
```

### 快取機制

```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.npm
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
```

## 監控與告警

### 部署監控

```yaml
monitoring:
  runs-on: ubuntu-latest
  steps:
    - name: Check deployment metrics
      run: |
        kubectl top deployment uav-controller -n production

    - name: Alert on anomalies
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: 'Deployment monitoring detected anomalies'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 最佳實踐

### DO ✅

- 使用語義化版本 (Semantic Versioning)
- 每次部署打標籤
- 保持完整的審計日誌
- 自動化所有可重複的任務
- 實施健康檢查與自動回滾
- 使用 server-side apply 避免衝突

### DON'T ❌

- 不要手動修改生產環境
- 不要跳過安全掃描
- 不要使用增量補丁（使用全量重發）
- 不要忽略失敗的健康檢查
- 不要在沒有測試的情況下部署

## 故障排除

### CI 失敗

1. 檢查測試日誌
2. 驗證依賴版本
3. 確認環境變數正確

### 部署失敗

1. 查看 rollout 狀態
2. 檢查事件日誌：`kubectl get events`
3. 驗證資源配額
4. 執行回滾操作

### 策略驗證失敗

1. 審查策略錯誤訊息
2. 使用 dry-run 測試
3. 驗證資源標籤完整性

---

**版本**：2.0.0  
**最後更新**：2025-11-25  
**維護者**：Platform Team  
**審核者**：DevOps Team
