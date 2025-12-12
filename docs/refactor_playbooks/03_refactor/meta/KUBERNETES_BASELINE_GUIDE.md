# Kubernetes Baseline Deployment Guide / Kubernetes 基線部署指南

## 📋 Purpose / 目的

This guide provides step-by-step instructions for deploying the 6 baseline YAML
files to establish constitutional-level (L-A) governance, security, and
operational standards for Kubernetes clusters.

本指南提供逐步說明，用於部署 6 個基線 YAML 檔案，為 Kubernetes 集群建立憲法級別 (L-A) 的治理、安全和營運標準。

---

## 🎯 Prerequisites / 前置條件

### Required / 必要條件

1. **Kubernetes Cluster:** v1.26+ with admission webhooks enabled
2. **kubectl:** v1.26+ configured with cluster-admin access
3. **Storage:** S3-compatible bucket for compliance evidence

### Optional / 可選條件

1. **Policy Engines:**
   - OPA Gatekeeper v3.14.0
   - Kyverno v1.11.0
   - Conftest v0.47.0
2. **Service Mesh:** Istio v1.18+ (for network policies)
3. **Quantum Backend:** IBM Quantum or AWS Braket (for quantum orchestration)
4. **Monitoring:** Prometheus + Grafana
5. **Secret Management:** HashiCorp Vault

---

## 📦 Baseline Components Overview / 基線組件概覽

| Baseline                      | Priority   | Dependencies                          | Purpose                                                  |
| ----------------------------- | ---------- | ------------------------------------- | -------------------------------------------------------- |
| **01-namespace-governance**   | L-A (1000) | None                                  | Namespace naming, labels, lifecycle, capability registry |
| **02-security-rbac**          | L-A (950)  | baseline-01                           | Zero Trust, RBAC, encryption, audit                      |
| **03-resource-management**    | L-A (900)  | baseline-01, baseline-02              | Resource quotas, tenant tiers, cost model                |
| **04-network-policy**         | L-A (850)  | baseline-01, baseline-02, baseline-03 | Network segmentation, service mesh, ingress/egress       |
| **05-compliance-attestation** | L-A (800)  | baseline-01~04                        | Compliance frameworks, attestation, drift detection      |
| **06-quantum-orchestration**  | L-A (750)  | baseline-01~05                        | Quantum circuits, hybrid workflows (experimental)        |

---

## 🚀 Deployment Steps / 部署步驟

### Phase 1: Pre-Deployment Validation / 部署前驗證

```bash
# 1. Verify cluster version
kubectl version --short

# 2. Check admission webhook support
kubectl api-versions | grep admissionregistration

# 3. Verify cluster-admin access
kubectl auth can-i '*' '*' --all-namespaces

# 4. Check available resources
kubectl top nodes
kubectl get nodes -o wide

# 5. Verify policy engines (optional)
kubectl get crd | grep gatekeeper
kubectl get crd | grep kyverno
```

---

### Phase 2: Deploy Baseline 01 - Namespace Governance / 部署基線 01 - 命名空間治理

```bash
# Deploy namespace governance baseline
kubectl apply -f infrastructure/kubernetes/baseline/baseline-01-namespace-governance.yaml

# Verify deployment
kubectl get namespace intelligent-hyperautomation-baseline
kubectl get configmap -n intelligent-hyperautomation-baseline
kubectl get service -n intelligent-hyperautomation-baseline

# Check capability registry service
kubectl get svc capability-registry-service -n intelligent-hyperautomation-baseline

# Verify RBAC
kubectl get clusterrole namespace-governance-controller
kubectl get clusterrolebinding namespace-governance-controller

# Test namespace naming policy (should fail for invalid names)
kubectl create namespace invalid_name  # Should be rejected
kubectl create namespace valid-service-dev  # Should succeed
```

**Expected Resources:**

- ✅ Namespace: `intelligent-hyperautomation-baseline`
- ✅ ConfigMaps: `namespace-governance-policy`, `capability-registry-schema`
- ✅ Service: `capability-registry-service`
- ✅ ServiceAccount: `namespace-governance-controller`
- ✅ ClusterRole + ClusterRoleBinding

---

### Phase 3: Deploy Baseline 02 - Security & RBAC / 部署基線 02 - 安全與 RBAC

```bash
# Deploy security baseline
kubectl apply -f infrastructure/kubernetes/baseline/baseline-02-security-rbac.yaml

# Verify deployment
kubectl get configmap security-baseline-policy -n intelligent-hyperautomation-baseline
kubectl get role -n intelligent-hyperautomation-baseline
kubectl get secret encryption-key-rotation-schedule -n intelligent-hyperautomation-baseline

# Check RBAC roles
kubectl get clusterrole security-baseline-enforcer
kubectl get role developer-restricted -n intelligent-hyperautomation-baseline
kubectl get role ci-cd-deployer -n intelligent-hyperautomation-baseline

# Verify pod security standards
kubectl get configmap pod-security-standards -n intelligent-hyperautomation-baseline
```

**Expected Resources:**

- ✅ ConfigMap: `security-baseline-policy`
- ✅ Roles: `developer-restricted`, `ci-cd-deployer`
- ✅ Secret: `encryption-key-rotation-schedule`
- ✅ ConfigMap: `pod-security-standards`

**Test RBAC:**

```bash
# Create test service account
kubectl create serviceaccount test-developer -n intelligent-hyperautomation-baseline

# Bind developer role
kubectl create rolebinding test-developer-binding \
  --role=developer-restricted \
  --serviceaccount=intelligent-hyperautomation-baseline:test-developer \
  -n intelligent-hyperautomation-baseline

# Test permissions
kubectl auth can-i get pods --as=system:serviceaccount:intelligent-hyperautomation-baseline:test-developer
```

---

### Phase 4: Deploy Baseline 03 - Resource Management / 部署基線 03 - 資源管理

```bash
# Deploy resource management baseline
kubectl apply -f infrastructure/kubernetes/baseline/baseline-03-resource-management.yaml

# Verify deployment
kubectl get resourcequota baseline-resource-quota -n intelligent-hyperautomation-baseline
kubectl get limitrange baseline-limit-range -n intelligent-hyperautomation-baseline

# Check quotas
kubectl describe resourcequota baseline-resource-quota -n intelligent-hyperautomation-baseline
kubectl describe limitrange baseline-limit-range -n intelligent-hyperautomation-baseline

# Verify configuration
kubectl get configmap resource-allocation-policy -n intelligent-hyperautomation-baseline
kubectl get configmap cluster-capacity-planning -n intelligent-hyperautomation-baseline
```

**Expected Resources:**

- ✅ ResourceQuota: `baseline-resource-quota`
- ✅ LimitRange: `baseline-limit-range`
- ✅ ConfigMaps: `resource-allocation-policy`, `cluster-capacity-planning`

**Test Resource Limits:**

```bash
# Try to create a pod exceeding limits (should fail)
kubectl run test-pod --image=nginx --requests='cpu=100,memory=100Gi' -n intelligent-hyperautomation-baseline
```

---

### Phase 5: Deploy Baseline 04 - Network Policy / 部署基線 04 - 網路策略

**Prerequisites:** Istio service mesh installed

```bash
# Verify Istio installation
kubectl get namespace istio-system
kubectl get pods -n istio-system

# Deploy network policy baseline
kubectl apply -f infrastructure/kubernetes/baseline/baseline-04-network-policy.yaml

# Verify deployment
kubectl get networkpolicy -n intelligent-hyperautomation-baseline
kubectl get configmap network-segmentation-policy -n intelligent-hyperautomation-baseline

# Check network policies
kubectl describe networkpolicy baseline-default-deny-all -n intelligent-hyperautomation-baseline
kubectl describe networkpolicy baseline-allow-same-namespace -n intelligent-hyperautomation-baseline
```

**Expected Resources:**

- ✅ NetworkPolicies: `baseline-default-deny-all`,
  `baseline-allow-same-namespace`, `baseline-allow-dns`,
  `baseline-api-gateway-ingress`
- ✅ ConfigMaps: `network-segmentation-policy`, `network-observability-config`

**Test Network Isolation:**

```bash
# Create test pods
kubectl run test-pod-1 --image=nginx -n intelligent-hyperautomation-baseline
kubectl run test-pod-2 --image=busybox --command -n intelligent-hyperautomation-baseline -- sleep 3600

# Test connectivity (same namespace should work)
kubectl exec -it test-pod-2 -n intelligent-hyperautomation-baseline -- wget -O- test-pod-1
```

---

### Phase 6: Deploy Baseline 05 - Compliance Attestation / 部署基線 05 - 合規證明

**Prerequisites:** OPA Gatekeeper, Kyverno installed

```bash
# Deploy compliance baseline
kubectl apply -f infrastructure/kubernetes/baseline/baseline-05-compliance-attestation.yaml

# Verify deployment
kubectl get configmap compliance-framework-baseline -n intelligent-hyperautomation-baseline
kubectl get configmap merkle-tree-attestation-config -n intelligent-hyperautomation-baseline
kubectl get cronjob compliance-attestation-job -n intelligent-hyperautomation-baseline

# Check CronJob status
kubectl get cronjob compliance-attestation-job -n intelligent-hyperautomation-baseline
kubectl describe cronjob compliance-attestation-job -n intelligent-hyperautomation-baseline

# Verify RBAC
kubectl get clusterrole compliance-attestation-reader
```

**Expected Resources:**

- ✅ ConfigMaps: `compliance-framework-baseline`,
  `merkle-tree-attestation-config`
- ✅ CronJob: `compliance-attestation-job` (runs every 6 hours)
- ✅ ServiceAccount: `compliance-attestation-sa`
- ✅ ClusterRole + ClusterRoleBinding

**Trigger Manual Attestation:**

```bash
# Create a manual job from the CronJob
kubectl create job --from=cronjob/compliance-attestation-job manual-attestation-1 -n intelligent-hyperautomation-baseline

# Check job status
kubectl get job manual-attestation-1 -n intelligent-hyperautomation-baseline
kubectl logs -l job-name=manual-attestation-1 -n intelligent-hyperautomation-baseline
```

---

### Phase 7: Deploy Baseline 06 - Quantum Orchestration (Optional) / 部署基線 06 - 量子編排（可選）

**Prerequisites:** IBM Quantum API token or AWS Braket access

```bash
# Deploy quantum orchestration baseline
kubectl apply -f infrastructure/kubernetes/baseline/baseline-06-quantum-orchestration.yaml

# Verify deployment
kubectl get configmap quantum-orchestration-baseline -n intelligent-hyperautomation-baseline
kubectl get configmap quantum-execution-scripts -n intelligent-hyperautomation-baseline
kubectl get service quantum-orchestration-service -n intelligent-hyperautomation-baseline

# Check service
kubectl get svc quantum-orchestration-service -n intelligent-hyperautomation-baseline

# Verify RBAC
kubectl get role quantum-job-executor -n intelligent-hyperautomation-baseline
```

**Expected Resources:**

- ✅ ConfigMaps: `quantum-orchestration-baseline`, `quantum-execution-scripts`
- ✅ Service: `quantum-orchestration-service`
- ✅ ServiceAccount: `quantum-orchestrator-sa`
- ✅ Role + RoleBinding

**Note:** Quantum orchestration is experimental and requires external quantum
backend access.

---

## ✅ Post-Deployment Validation / 部署後驗證

### System-Wide Checks / 全系統檢查

```bash
# 1. Check all baseline resources
kubectl get all,configmap,secret,networkpolicy,resourcequota,limitrange,cronjob \
  -n intelligent-hyperautomation-baseline

# 2. Verify admission webhooks
kubectl get validatingwebhookconfigurations
kubectl get mutatingwebhookconfigurations

# 3. Check policy engines
kubectl get constrainttemplates  # OPA Gatekeeper
kubectl get kyverno policies     # Kyverno

# 4. Verify RBAC
kubectl get clusterroles | grep baseline
kubectl get clusterrolebindings | grep baseline

# 5. Check network policies across cluster
kubectl get networkpolicy --all-namespaces
```

### Compliance Validation / 合規驗證

```bash
# Run compliance check (if tools installed)
kubectl krew install policy-report  # Install krew plugin
kubectl policy-report --namespace intelligent-hyperautomation-baseline

# Check Gatekeeper constraints
kubectl get constraints

# Check Kyverno policy reports
kubectl get policyreport --all-namespaces
```

---

## 🔧 Troubleshooting / 疑難排解

### Common Issues / 常見問題

#### 1. Admission Webhook Timeout

**Symptom:** Resource creation hangs or times out

**Solution:**

```bash
# Check webhook service
kubectl get svc -n intelligent-hyperautomation-baseline
kubectl get endpoints -n intelligent-hyperautomation-baseline

# Check controller logs
kubectl logs -n intelligent-hyperautomation-baseline deployment/namespace-governance-controller

# Temporarily disable webhook (for debugging only)
kubectl delete validatingwebhookconfigurations <webhook-name>
```

#### 2. Policy Violation

**Symptom:** Resources rejected by admission controller

**Solution:**

```bash
# Check constraint details
kubectl get constraints
kubectl describe constraint <constraint-name>

# View policy violation logs
kubectl get events --all-namespaces | grep "denied by policy"

# Check OPA Gatekeeper logs
kubectl logs -n gatekeeper-system deployment/gatekeeper-controller-manager
```

#### 3. Resource Quota Exceeded

**Symptom:** Pods fail to schedule due to quota

**Solution:**

```bash
# Check quota usage
kubectl describe resourcequota -n <namespace>

# Check actual resource usage
kubectl top nodes
kubectl top pods -n <namespace>

# Adjust quota (if needed)
kubectl edit resourcequota baseline-resource-quota -n intelligent-hyperautomation-baseline
```

#### 4. Network Policy Blocking Traffic

**Symptom:** Pods cannot communicate

**Solution:**

```bash
# Check network policies
kubectl get networkpolicy -n <namespace>
kubectl describe networkpolicy <policy-name> -n <namespace>

# Test connectivity
kubectl run test-pod --image=busybox --rm -it --restart=Never -- wget -O- <target-service>

# Temporarily allow all traffic (debugging only)
kubectl delete networkpolicy baseline-default-deny-all -n <namespace>
```

---

## 📊 Monitoring & Observability / 監控與可觀測性

### Key Metrics to Monitor / 關鍵監控指標

1. **Namespace Lifecycle:**
   - State transitions
   - Capability conflicts
   - Label compliance rate

2. **RBAC & Security:**
   - Failed authentication attempts
   - Privilege escalation attempts
   - Secret access events

3. **Resource Management:**
   - Quota utilization (CPU, memory, storage)
   - Pod evictions
   - Autoscaling events

4. **Network:**
   - Policy violations
   - Anomalous traffic patterns
   - Ingress/egress volumes

5. **Compliance:**
   - Policy violations
   - Drift detection events
   - Attestation generation failures

### Recommended Dashboards / 建議儀表板

- **Grafana Dashboards:**
  - Kubernetes Baseline Health
  - RBAC Audit Dashboard
  - Resource Quota Utilization
  - Network Policy Compliance

---

## 🔄 Maintenance & Updates / 維護與更新

### Regular Tasks / 定期任務

**Daily:**

- Monitor compliance attestation CronJob execution
- Review audit logs for security events

**Weekly:**

- Check resource quota utilization
- Review network policy violations
- Update policy engines (if new versions available)

**Monthly:**

- Conduct access reviews
- Review and rotate encryption keys
- Update baseline configurations (if needed)

**Quarterly:**

- Penetration testing (for PCI-DSS compliance)
- External audit preparation (SOC2)
- Review and update RBAC role matrix

### Backup & Disaster Recovery / 備份與災難恢復

```bash
# Backup all baseline configurations
kubectl get all,configmap,secret,networkpolicy,resourcequota,limitrange,cronjob \
  -n intelligent-hyperautomation-baseline -o yaml > baseline-backup.yaml

# Export RBAC
kubectl get clusterroles,clusterrolebindings,roles,rolebindings \
  -o yaml > rbac-backup.yaml

# Restore (if needed)
kubectl apply -f baseline-backup.yaml
kubectl apply -f rbac-backup.yaml
```

---

## 📚 Related Documentation / 相關文檔

- 📋
  [Baseline Integration Plan](../../02_integration/BASELINE_YAML_INTEGRATION_PLAN.md)
- 🏗️
  [Infrastructure Baseline README](../../../../infrastructure/kubernetes/baseline/README.md)
- 🔐 [Governance Policies](../../../../governance/policies/)
- ⚙️ [Configuration Files](../../../../config/)
- 📖 [Documentation Index](../../../../DOCUMENTATION_INDEX.md)

---

## 📞 Support & Feedback / 支援與回饋

- 📧 **Email:** <platform-team@example.com>
- 💬 **Slack:** #kubernetes-baseline
- 🐛 **Issues:** GitHub Issues
- 📖 **Docs:** [DOCUMENTATION_INDEX.md](../../../../DOCUMENTATION_INDEX.md)

---

**Version:** v1.0.0  
**Last Updated:** 2025-12-07  
**Maintainers:** Platform Engineering Team  
**Status:** ✅ Production Ready
