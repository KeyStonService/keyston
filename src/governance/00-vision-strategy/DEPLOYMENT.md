# GaC Deployment Guide / GaC 部署指南

## 🎯 Purpose / 目的

This guide provides instructions for deploying the Governance-as-Code (GaC) resources to a Kubernetes cluster.  
本指南提供將治理即代碼 (GaC) 資源部署到 Kubernetes 集群的說明。

---

## 📋 Prerequisites / 先決條件

### Required / 必需

- Kubernetes cluster (v1.20+)  
  Kubernetes 集群 (v1.20+)
- `kubectl` configured to access your cluster  
  已配置 `kubectl` 以訪問您的集群

### Optional (for full features) / 可選（完整功能）

- **Argo CD** - For GitOps automation  
  **Argo CD** - 用於 GitOps 自動化
- **OPA Gatekeeper** - For policy enforcement  
  **OPA Gatekeeper** - 用於策略執行
- **Prometheus + Grafana** - For monitoring  
  **Prometheus + Grafana** - 用於監控

---

## 🚀 Deployment Options / 部署選項

### Option 1: Manual Deployment (Basic) / 選項 1：手動部署（基本）

This deploys CRDs and instances directly to your cluster without GitOps.  
這會將 CRDs 和實例直接部署到您的集群，無需 GitOps。

```bash
# Step 1: Create namespace
kubectl create namespace governance

# Step 2: Deploy CRDs
kubectl apply -f governance/00-vision-strategy/crd/

# Step 3: Verify CRDs are installed
kubectl get crds | grep governance.kai

# Expected output: 9 CRDs
# - alignmentframeworks.governance.kai
# - changeprotocols.governance.kai
# - communicationplans.governance.kai
# - governancecharters.governance.kai
# - implementationroadmaps.governance.kai
# - metricsdashboards.governance.kai
# - riskregisters.governance.kai
# - strategicobjectives.governance.kai
# - visionstatements.governance.kai

# Step 4: Deploy instances
kubectl apply -f governance/00-vision-strategy/k8s/

# Step 5: Verify instances
kubectl get visionstatements,strategicobjectives,governancecharters -n governance

# Expected: 9 resources total (1 of each type)
```

**Validation / 驗證:**

```bash
# Check all GaC resources
kubectl get visionstatements,strategicobjectives,governancecharters,alignmentframeworks,riskregisters,implementationroadmaps,communicationplans,metricsdashboards,changeprotocols -n governance

# Check resource details
kubectl describe visionstatement vision-synergymesh-2025 -n governance
```

---

### Option 2: GitOps Deployment (Recommended) / 選項 2：GitOps 部署（推薦）

This uses Argo CD to automatically deploy and sync GaC resources.  
這使用 Argo CD 自動部署和同步 GaC 資源。

#### Prerequisites / 先決條件

```bash
# Install Argo CD (if not already installed)
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for Argo CD to be ready
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

#### Deploy GaC with Argo CD / 使用 Argo CD 部署 GaC

```bash
# Deploy ApplicationSet
kubectl apply -f governance/00-vision-strategy/gitops/applicationset.yaml

# Verify applications created
kubectl get applications -n argocd | grep gac-

# Expected output:
# gac-governance-crds       ...
# gac-governance-instances  ...

# Check sync status
kubectl get applications -n argocd -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.health.status}{"\t"}{.status.sync.status}{"\n"}{end}' | grep gac-

# Wait for sync to complete
kubectl wait --for=condition=synced --timeout=300s application/gac-governance-crds -n argocd
kubectl wait --for=condition=synced --timeout=300s application/gac-governance-instances -n argocd
```

**Monitoring / 監控:**

```bash
# Access Argo CD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Open browser to: https://localhost:8080
# Username: admin
# Password: (from earlier step)
```

---

### Option 3: Kustomize Deployment / 選項 3：Kustomize 部署

This uses Kustomize to bundle and deploy resources.  
這使用 Kustomize 來捆綁和部署資源。

```bash
# Deploy CRDs using Kustomize
kubectl apply -k governance/00-vision-strategy/gitops/kustomization-crds.yaml

# Wait for CRDs to be established
kubectl wait --for condition=established --timeout=60s crd/visionstatements.governance.kai

# Deploy instances using Kustomize
kubectl apply -k governance/00-vision-strategy/gitops/kustomization-instances.yaml

# Verify
kubectl get all -n governance -l app.kubernetes.io/part-of=synergymesh-gac
```

---

## 🛡️ OPA Gatekeeper Deployment (Optional) / OPA Gatekeeper 部署（可選）

Deploy OPA Gatekeeper for real-time policy enforcement.  
部署 OPA Gatekeeper 以實現實時策略執行。

```bash
# Install Gatekeeper (if not already installed)
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Wait for Gatekeeper to be ready
kubectl wait --for=condition=available --timeout=300s deployment/gatekeeper-controller-manager -n gatekeeper-system

# Deploy GaC ConstraintTemplates
kubectl apply -f governance/00-vision-strategy/gatekeeper/constrainttemplate-vision.yaml

# Deploy Constraints
kubectl apply -f governance/00-vision-strategy/gatekeeper/constraint-vision.yaml

# Deploy Gatekeeper Config
kubectl apply -f governance/00-vision-strategy/gatekeeper/config.yaml

# Verify
kubectl get constrainttemplates
kubectl get constraints
```

**Test policy enforcement / 測試策略執行:**

```bash
# Try to create an invalid VisionStatement (should fail)
cat <<EOF | kubectl apply -f -
apiVersion: governance.kai/v1
kind: VisionStatement
metadata:
  name: test-invalid
  namespace: governance
spec:
  mission:
    statement: "Test"
  # Missing vision field - should be rejected
EOF

# Expected: Error from Gatekeeper admission webhook
```

---

## 📊 Monitoring Deployment (Optional) / 監控部署（可選）

Deploy Prometheus rules and Grafana dashboard for GaC monitoring.  
部署 Prometheus 規則和 Grafana 儀表板以進行 GaC 監控。

```bash
# Prerequisite: Prometheus Operator installed
# Deploy Prometheus rules
kubectl apply -f governance/00-vision-strategy/monitoring/prometheus-rules.yaml -n monitoring

# Import Grafana dashboard
# Method 1: Via UI
# - Login to Grafana
# - Go to Dashboards → Import
# - Upload: governance/00-vision-strategy/monitoring/grafana-dashboard.json

# Method 2: Via ConfigMap (if using Grafana sidecar)
kubectl create configmap gac-dashboard \
  --from-file=governance/00-vision-strategy/monitoring/grafana-dashboard.json \
  -n monitoring \
  -o yaml --dry-run=client | kubectl label -f - grafana_dashboard=1 --dry-run=client -o yaml | kubectl apply -f -

# Verify Prometheus rules
kubectl get prometheusrules -n monitoring | grep governance
```

---

## ✅ Verification / 驗證

### Check all components / 檢查所有組件

```bash
# 1. CRDs installed
kubectl get crds | grep governance.kai | wc -l
# Expected: 9

# 2. Instances running
kubectl get all -n governance
# Expected: 9 custom resources

# 3. GitOps applications (if using Argo CD)
kubectl get applications -n argocd | grep gac-
# Expected: 2 applications

# 4. Gatekeeper (if deployed)
kubectl get constrainttemplates,constraints | grep -i governance
# Expected: 1 ConstraintTemplate, 1+ Constraints

# 5. Monitoring (if deployed)
kubectl get prometheusrules -n monitoring | grep governance
# Expected: 1 PrometheusRule
```

### Resource count verification / 資源計數驗證

```bash
#!/bin/bash
echo "GaC Resource Count:"
echo "==================="
kubectl get visionstatements -n governance --no-headers 2>/dev/null | wc -l | xargs echo "VisionStatements:"
kubectl get strategicobjectives -n governance --no-headers 2>/dev/null | wc -l | xargs echo "StrategicObjectives:"
kubectl get governancecharters -n governance --no-headers 2>/dev/null | wc -l | xargs echo "GovernanceCharters:"
kubectl get alignmentframeworks -n governance --no-headers 2>/dev/null | wc -l | xargs echo "AlignmentFrameworks:"
kubectl get riskregisters -n governance --no-headers 2>/dev/null | wc -l | xargs echo "RiskRegisters:"
kubectl get implementationroadmaps -n governance --no-headers 2>/dev/null | wc -l | xargs echo "ImplementationRoadmaps:"
kubectl get communicationplans -n governance --no-headers 2>/dev/null | wc -l | xargs echo "CommunicationPlans:"
kubectl get metricsdashboards -n governance --no-headers 2>/dev/null | wc -l | xargs echo "MetricsDashboards:"
kubectl get changeprotocols -n governance --no-headers 2>/dev/null | wc -l | xargs echo "ChangeProtocols:"
echo "==================="
echo "Total should be: 9"
```

---

## 🔄 Continuous Deployment / 持續部署

Once deployed with GitOps (Option 2), changes to strategic YAMLs will automatically trigger updates:  
一旦使用 GitOps（選項 2）部署，對戰略 YAML 的更改將自動觸發更新：

1. **Edit strategic YAML** / 編輯戰略 YAML

   ```bash
   vim governance/00-vision-strategy/vision-statement.yaml
   ```

2. **Commit and push** / 提交並推送

   ```bash
   git add governance/00-vision-strategy/vision-statement.yaml
   git commit -m "Update vision statement"
   git push
   ```

3. **GitHub Actions** automatically:  
   **GitHub Actions** 自動：
   - Detects change / 檢測更改
   - Regenerates GaC resources / 重新生成 GaC 資源
   - Commits updated resources / 提交更新的資源

4. **Argo CD** automatically:  
   **Argo CD** 自動：
   - Detects repository change / 檢測存儲庫更改
   - Syncs to cluster / 同步到集群
   - Updates K8s resources / 更新 K8s 資源

**Time to production**: Strategic update → Deployed < 5 minutes 🚀  
**生產時間**: 戰略更新 → 部署 < 5 分鐘 🚀

---

## 🧹 Cleanup / 清理

To remove GaC resources from your cluster / 從集群中刪除 GaC 資源:

```bash
# Remove instances
kubectl delete -f governance/00-vision-strategy/k8s/ --ignore-not-found

# Remove CRDs (this will delete all instances too)
kubectl delete -f governance/00-vision-strategy/crd/ --ignore-not-found

# Remove Argo CD applications (if deployed)
kubectl delete -f governance/00-vision-strategy/gitops/applicationset.yaml --ignore-not-found

# Remove Gatekeeper resources (if deployed)
kubectl delete -f governance/00-vision-strategy/gatekeeper/ --ignore-not-found

# Remove Prometheus rules (if deployed)
kubectl delete -f governance/00-vision-strategy/monitoring/prometheus-rules.yaml -n monitoring --ignore-not-found

# Remove namespace
kubectl delete namespace governance --ignore-not-found
```

---

## 📚 References / 參考資料

- **Phase 3 README**: `governance/00-vision-strategy/PHASE3_README.md`
- **Architecture Blueprint**: `governance/00-vision-strategy/gac-architecture.yaml`
- **Project State**: `governance/00-vision-strategy/PROJECT_STATE_SNAPSHOT.md`

---

**Status**: ✅ Ready for deployment  
**狀態**: ✅ 準備部署
