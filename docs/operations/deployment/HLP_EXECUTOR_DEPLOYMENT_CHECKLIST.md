# HLP Executor 部署檢查清單 | HLP Executor Deployment Checklist

**文件版本 | Document Version**: 1.0.0  
**最後更新 | Last Updated**: 2025-12-07  
**負責團隊 | Responsible Team**: Platform Engineering / DevOps  
**用途 | Purpose**: Pre-deployment verification and post-deployment validation

---

## 📋 文件目的 | Document Purpose

本文件提供 HLP Executor Core
Plugin 的完整部署檢查清單，確保所有前置條件滿足、部署順利進行，並驗證部署後系統正常運作。

This document provides a comprehensive deployment checklist for the HLP Executor
Core Plugin, ensuring all prerequisites are met, deployment proceeds smoothly,
and post-deployment validation confirms system health.

---

## 🎯 部署概覽 | Deployment Overview

### 部署階段 | Deployment Phases

```
┌─────────────────────────────────────────────────────────┐
│              HLP Executor 部署流程 | Deployment Flow     │
└─────────────────────────────────────────────────────────┘

Phase 1: Pre-Deployment Preparation (30-45 min)
   ├── Infrastructure verification
   ├── Configuration preparation
   └── Security setup

Phase 2: Deployment Execution (15-30 min)
   ├── Image verification
   ├── Resource deployment
   └── Service startup

Phase 3: Post-Deployment Validation (15-20 min)
   ├── Health checks
   ├── Functional testing
   └── Monitoring verification

Phase 4: Rollout & Handover (10-15 min)
   ├── Documentation update
   ├── Team notification
   └── Monitoring handover
```

### 預計時間 | Estimated Time

- **總計 | Total**: 70-110 分鐘 | 70-110 minutes
- **最小團隊規模 | Minimum Team**: 2 人 (1 Deployer + 1 Verifier)
- **建議窗口 | Recommended Window**: 非高峰時段 | Off-peak hours

---

## ✅ Phase 1: 部署前準備 | Pre-Deployment Preparation

### 1.1 Kubernetes 集群驗證 | Kubernetes Cluster Verification

#### ☑️ 集群版本要求 | Cluster Version Requirement

```bash
# Check Kubernetes version (must be >= 1.24)
kubectl version --short

# Expected output:
# Server Version: v1.24.x or higher
```

**最低版本 | Minimum Version**: v1.24  
**推薦版本 | Recommended Version**: v1.28+  
**驗證標準 | Validation Criteria**: ✅ 版本 >= 1.24

#### ☑️ 節點資源檢查 | Node Resource Check

```bash
# Check node status and resources
kubectl get nodes -o wide
kubectl top nodes

# Minimum requirements per node:
# - CPU: 4+ cores available
# - Memory: 8+ GB available
# - Disk: 50+ GB available
```

**資源需求 | Resource Requirements**:

- **CPU**: 每節點至少 4 核心可用 | At least 4 cores available per node
- **Memory**: 每節點至少 8 GB 可用 | At least 8 GB available per node
- **Disk**: 每節點至少 50 GB 可用 | At least 50 GB available per node
- **節點數量 | Node Count**: 至少 3 個 worker 節點 | At least 3 worker nodes

**驗證命令 | Verification Command**:

```bash
# Verify sufficient resources
NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
if [ "$NODE_COUNT" -lt 3 ]; then
  echo "❌ FAIL: Need at least 3 nodes, found $NODE_COUNT"
else
  echo "✅ PASS: Found $NODE_COUNT nodes"
fi
```

#### ☑️ 存儲類驗證 | StorageClass Verification

```bash
# Check available storage classes
kubectl get storageclass

# Verify default storage class exists
kubectl get storageclass -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}'

# Check if storage class supports volume expansion
kubectl get storageclass -o json | \
  jq -r '.items[] | select(.allowVolumeExpansion == true) | .metadata.name'
```

**要求 | Requirements**:

- ✅ 至少一個 StorageClass 可用 | At least one StorageClass available
- ✅ StorageClass 支援動態配置 | StorageClass supports dynamic provisioning
- ✅ (推薦) 支援卷擴展 | (Recommended) Supports volume expansion

---

### 1.2 命名空間準備 | Namespace Preparation

#### ☑️ 創建命名空間 | Create Namespace

```bash
# Create namespace if not exists
kubectl create namespace unmanned-island-system --dry-run=client -o yaml | kubectl apply -f -

# Verify namespace
kubectl get namespace unmanned-island-system

# Add labels
kubectl label namespace unmanned-island-system \
  name=unmanned-island-system \
  environment=production \
  team=platform-engineering \
  --overwrite
```

**驗證 | Verification**:

```bash
kubectl get namespace unmanned-island-system -o yaml | grep -A 5 "labels:"
```

#### ☑️ 設定資源配額 (可選) | Set Resource Quotas (Optional)

```yaml
# File: infrastructure/kubernetes/namespace/resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: hlp-executor-quota
  namespace: unmanned-island-system
spec:
  hard:
    requests.cpu: '20'
    requests.memory: '40Gi'
    requests.storage: '100Gi'
    persistentvolumeclaims: '10'
    pods: '50'
```

```bash
# Apply resource quota
kubectl apply -f infrastructure/kubernetes/namespace/resource-quota.yaml

# Verify
kubectl describe resourcequota hlp-executor-quota -n unmanned-island-system
```

---

### 1.3 信任捆綁部署 | Trust Bundle Deployment

#### ☑️ 部署 CA 證書 ConfigMap | Deploy CA Certificate ConfigMap

```bash
# Create trust bundle ConfigMap
kubectl create configmap hlp-executor-trust-bundle \
  --from-file=ca.crt=/path/to/ca-bundle.crt \
  --namespace=unmanned-island-system \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify ConfigMap
kubectl get configmap hlp-executor-trust-bundle -n unmanned-island-system
kubectl describe configmap hlp-executor-trust-bundle -n unmanned-island-system
```

**驗證內容 | Verify Content**:

```bash
kubectl get configmap hlp-executor-trust-bundle -n unmanned-island-system -o jsonpath='{.data.ca\.crt}' | \
  openssl x509 -noout -text
```

#### ☑️ TLS Secret (如需要) | TLS Secret (If Needed)

```bash
# Create TLS secret for ingress/service mesh
kubectl create secret tls hlp-executor-tls \
  --cert=/path/to/tls.crt \
  --key=/path/to/tls.key \
  --namespace=unmanned-island-system \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify secret
kubectl get secret hlp-executor-tls -n unmanned-island-system
```

---

### 1.4 RBAC 配置 | RBAC Configuration

#### ☑️ 創建 ServiceAccount | Create ServiceAccount

```yaml
# File: infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: hlp-executor-sa
  namespace: unmanned-island-system
  labels:
    app: hlp-executor-core
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: hlp-executor-role
  namespace: unmanned-island-system
rules:
  - apiGroups: ['']
    resources: ['pods', 'pods/log', 'pods/status']
    verbs: ['get', 'list', 'watch']
  - apiGroups: ['']
    resources: ['configmaps']
    verbs: ['get', 'list', 'watch']
  - apiGroups: ['']
    resources: ['secrets']
    verbs: ['get', 'list']
  - apiGroups: ['batch']
    resources: ['jobs', 'cronjobs']
    verbs: ['get', 'list', 'watch', 'create', 'update', 'patch']
  - apiGroups: ['']
    resources: ['events']
    verbs: ['create', 'patch']
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: hlp-executor-binding
  namespace: unmanned-island-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: hlp-executor-role
subjects:
  - kind: ServiceAccount
    name: hlp-executor-sa
    namespace: unmanned-island-system
```

```bash
# Apply RBAC configuration
kubectl apply -f infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml

# Verify RBAC
kubectl get serviceaccount hlp-executor-sa -n unmanned-island-system
kubectl get role hlp-executor-role -n unmanned-island-system
kubectl get rolebinding hlp-executor-binding -n unmanned-island-system

# Test permissions
kubectl auth can-i get pods \
  --as=system:serviceaccount:unmanned-island-system:hlp-executor-sa \
  -n unmanned-island-system
```

**預期輸出 | Expected Output**: `yes`

---

### 1.5 網路策略 | Network Policies

#### ☑️ 應用網路策略 | Apply Network Policies

```yaml
# File: infrastructure/kubernetes/network/hlp-executor-netpol.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: hlp-executor-netpol
  namespace: unmanned-island-system
spec:
  podSelector:
    matchLabels:
      app: hlp-executor-core
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: unmanned-island-system
        - podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - protocol: TCP
          port: 8080
        - protocol: TCP
          port: 8081
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: TCP
          port: 443 # Kubernetes API
    - to:
        - namespaceSelector:
            matchLabels:
              name: quantum-system
      ports:
        - protocol: TCP
          port: 8080 # Quantum backend
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 53 # DNS
        - protocol: UDP
          port: 53 # DNS
    - to:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 9090 # Prometheus
```

```bash
# Apply network policy
kubectl apply -f infrastructure/kubernetes/network/hlp-executor-netpol.yaml

# Verify network policy
kubectl get networkpolicy hlp-executor-netpol -n unmanned-island-system
kubectl describe networkpolicy hlp-executor-netpol -n unmanned-island-system
```

---

### 1.6 持久化存儲 | Persistent Storage

#### ☑️ 創建並綁定 PVC | Create and Bind PVC

```yaml
# File: infrastructure/kubernetes/storage/hlp-executor-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hlp-executor-state-pvc
  namespace: unmanned-island-system
  labels:
    app: hlp-executor-core
    component: state-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard # Adjust based on your cluster
```

```bash
# Apply PVC
kubectl apply -f infrastructure/kubernetes/storage/hlp-executor-pvc.yaml

# Wait for PVC to be bound
kubectl wait --for=condition=Bound pvc/hlp-executor-state-pvc -n unmanned-island-system --timeout=300s

# Verify PVC
kubectl get pvc hlp-executor-state-pvc -n unmanned-island-system
kubectl describe pvc hlp-executor-state-pvc -n unmanned-island-system
```

**驗證狀態 | Verify Status**:

- **Status**: `Bound`
- **Capacity**: `10Gi`
- **Access Mode**: `RWO`

---

### 1.7 配置管理 | Configuration Management

#### ☑️ 部署 ConfigMap | Deploy ConfigMap

```yaml
# File: infrastructure/kubernetes/config/hlp-executor-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hlp-executor-config
  namespace: unmanned-island-system
  labels:
    app: hlp-executor-core
data:
  config.yaml: |
    server:
      port: 8080
      admin_port: 8081
      
    logging:
      level: INFO
      format: json
      
    state_persistence:
      enabled: true
      path: /var/lib/hlp-executor/state
      checkpoint_interval: 60s
      retention_days: 7
      
    circuit_breaker:
      enabled: true
      failure_threshold: 5
      timeout: 30s
      
    quantum_backend:
      enabled: false  # ⚠️ Disabled by default. See config/integrations/quantum-integration.yaml
      endpoint: http://quantum-backend-service.quantum-system.svc.cluster.local:8080
      timeout: 30s
      fallback_mode: classical  # Gracefully degrade to classical computation
      
    monitoring:
      prometheus:
        enabled: true
        port: 8080
        path: /metrics
```

```bash
# Apply ConfigMap
kubectl apply -f infrastructure/kubernetes/config/hlp-executor-config.yaml

# Verify ConfigMap
kubectl get configmap hlp-executor-config -n unmanned-island-system
kubectl describe configmap hlp-executor-config -n unmanned-island-system
```

#### ☑️ 部署 Secrets | Deploy Secrets

```bash
# Create secrets for sensitive data
kubectl create secret generic hlp-executor-secrets \
  --from-literal=quantum-api-key='YOUR_QUANTUM_API_KEY' \
  --from-literal=db-password='YOUR_DB_PASSWORD' \
  --namespace=unmanned-island-system \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify secret (do not display values)
kubectl get secret hlp-executor-secrets -n unmanned-island-system
```

---

## 🚀 Phase 2: 部署執行 | Deployment Execution

### 2.1 容器映像驗證 | Container Image Verification

#### ☑️ 映像簽名驗證 (Cosign) | Image Signature Verification (Cosign)

```bash
# Verify image signature with Cosign
export IMAGE_TAG="ghcr.io/unmanned-island/hlp-executor-core:v1.0.0"

# Verify signature
cosign verify \
  --key cosign.pub \
  "${IMAGE_TAG}"

# Expected output: Verification successful
```

**驗證標準 | Validation Criteria**:

- ✅ 簽名驗證成功 | Signature verification successful
- ✅ 簽名者身份正確 | Signer identity correct
- ✅ 映像摘要匹配 | Image digest matches

#### ☑️ SLSA Provenance 驗證 | SLSA Provenance Verification

```bash
# Verify SLSA provenance
cosign verify-attestation \
  --key cosign.pub \
  --type slsaprovenance \
  "${IMAGE_TAG}"

# Check provenance details
cosign verify-attestation \
  --key cosign.pub \
  --type slsaprovenance \
  "${IMAGE_TAG}" | jq -r '.payload' | base64 -d | jq
```

**驗證項目 | Verification Items**:

- ✅ Builder ID 正確 | Builder ID correct
- ✅ 構建參數完整 | Build parameters complete
- ✅ 來源倉庫匹配 | Source repository matches

#### ☑️ 容器掃描報告 | Container Scan Report

```bash
# Pull vulnerability scan report
trivy image "${IMAGE_TAG}" --severity HIGH,CRITICAL

# Expected: No HIGH or CRITICAL vulnerabilities
```

---

### 2.2 Deployment 部署 | Deployment Deployment

#### ☑️ 應用 Deployment 配置 | Apply Deployment Configuration

```yaml
# File: infrastructure/kubernetes/deployment/hlp-executor-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hlp-executor-core
  namespace: unmanned-island-system
  labels:
    app: hlp-executor-core
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: hlp-executor-core
  template:
    metadata:
      labels:
        app: hlp-executor-core
        version: v1.0.0
      annotations:
        prometheus.io/scrape: 'true'
        prometheus.io/port: '8080'
        prometheus.io/path: '/metrics'
    spec:
      serviceAccountName: hlp-executor-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: executor
          image: ghcr.io/unmanned-island/hlp-executor-core:v1.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: admin
              containerPort: 8081
              protocol: TCP
          env:
            - name: CONFIG_PATH
              value: /etc/hlp-executor/config.yaml
            - name: QUANTUM_API_KEY
              valueFrom:
                secretKeyRef:
                  name: hlp-executor-secrets
                  key: quantum-api-key
          volumeMounts:
            - name: config
              mountPath: /etc/hlp-executor
              readOnly: true
            - name: state
              mountPath: /var/lib/hlp-executor/state
            - name: trust-bundle
              mountPath: /etc/ssl/certs/ca-bundle.crt
              subPath: ca.crt
              readOnly: true
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
      volumes:
        - name: config
          configMap:
            name: hlp-executor-config
        - name: state
          persistentVolumeClaim:
            claimName: hlp-executor-state-pvc
        - name: trust-bundle
          configMap:
            name: hlp-executor-trust-bundle
```

```bash
# Apply deployment
kubectl apply -f infrastructure/kubernetes/deployment/hlp-executor-deployment.yaml

# Monitor rollout
kubectl rollout status deployment/hlp-executor-core -n unmanned-island-system --timeout=5m

# Check deployment status
kubectl get deployment hlp-executor-core -n unmanned-island-system
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core
```

**預期結果 | Expected Result**:

- **Replicas**: 3/3 ready
- **Pod Status**: All Running
- **Restarts**: 0

---

### 2.3 Service 部署 | Service Deployment

#### ☑️ 部署 Service | Deploy Service

```yaml
# File: infrastructure/kubernetes/service/hlp-executor-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: hlp-executor-service
  namespace: unmanned-island-system
  labels:
    app: hlp-executor-core
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 8080
      targetPort: 8080
      protocol: TCP
    - name: admin
      port: 8081
      targetPort: 8081
      protocol: TCP
  selector:
    app: hlp-executor-core
```

```bash
# Apply service
kubectl apply -f infrastructure/kubernetes/service/hlp-executor-service.yaml

# Verify service
kubectl get service hlp-executor-service -n unmanned-island-system
kubectl describe service hlp-executor-service -n unmanned-island-system

# Check endpoints
kubectl get endpoints hlp-executor-service -n unmanned-island-system
```

---

### 2.4 HPA 配置 | HPA Configuration

#### ☑️ 部署 HorizontalPodAutoscaler | Deploy HorizontalPodAutoscaler

```yaml
# File: infrastructure/kubernetes/hpa/hlp-executor-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hlp-executor-hpa
  namespace: unmanned-island-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hlp-executor-core
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
```

```bash
# Apply HPA
kubectl apply -f infrastructure/kubernetes/hpa/hlp-executor-hpa.yaml

# Verify HPA
kubectl get hpa hlp-executor-hpa -n unmanned-island-system
kubectl describe hpa hlp-executor-hpa -n unmanned-island-system
```

---

### 2.5 監控整合 | Monitoring Integration

#### ☑️ 配置 Prometheus ServiceMonitor | Configure Prometheus ServiceMonitor

```yaml
# File: infrastructure/monitoring/prometheus/hlp-executor-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hlp-executor-monitor
  namespace: unmanned-island-system
  labels:
    app: hlp-executor-core
    prometheus: kube-prometheus
spec:
  selector:
    matchLabels:
      app: hlp-executor-core
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
```

```bash
# Apply ServiceMonitor
kubectl apply -f infrastructure/monitoring/prometheus/hlp-executor-servicemonitor.yaml

# Verify ServiceMonitor
kubectl get servicemonitor hlp-executor-monitor -n unmanned-island-system

# Check if Prometheus is scraping (wait 1-2 min)
kubectl exec -it -n monitoring prometheus-k8s-0 -- \
  wget -qO- http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.labels.job=="hlp-executor-service")'
```

---

## ✔️ Phase 3: 部署後驗證 | Post-Deployment Validation

### 3.1 健康檢查 | Health Checks

#### ☑️ Pod 健康檢查 | Pod Health Check

```bash
# Check all pods are running
kubectl get pods -n unmanned-island-system -l app=hlp-executor-core

# Expected: All pods in Running status with 1/1 Ready

# Check pod events
kubectl get events -n unmanned-island-system --field-selector involvedObject.kind=Pod \
  --sort-by='.lastTimestamp' | grep hlp-executor

# No error events expected
```

#### ☑️ 服務端點健康 | Service Endpoint Health

```bash
# Test /healthz endpoint
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -f http://localhost:8080/healthz

# Expected output: {"status": "healthy", "timestamp": "..."}

# Test /readyz endpoint
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -f http://localhost:8080/readyz

# Expected output: {"status": "ready", "checks": {...}}

# Test /status endpoint
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -f http://localhost:8080/status

# Expected output: Service status details
```

#### ☑️ 日誌檢查 | Log Check

```bash
# Check recent logs for errors
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=100 | \
  grep -E "(ERROR|FATAL|panic)"

# Expected: No ERROR/FATAL/panic messages

# Check startup logs
kubectl logs -n unmanned-island-system -l app=hlp-executor-core --tail=50 | \
  grep -E "(started|listening|ready)"

# Expected: Successful startup messages
```

---

### 3.2 功能測試 | Functional Testing

#### ☑️ 基本 API 測試 | Basic API Test

```bash
# Submit test execution
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl -X POST http://localhost:8080/api/v1/executions \
  -H "Content-Type: application/json" \
  -d '{
    "dag_definition": {
      "version": "1.0",
      "phases": [
        {
          "name": "test-phase",
          "actions": ["echo test"]
        }
      ]
    }
  }'

# Expected: {"execution_id": "...", "status": "PENDING"}

# Query execution status
EXEC_ID="<execution_id_from_above>"
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl http://localhost:8080/api/v1/executions/$EXEC_ID

# Expected: Execution details with status
```

#### ☑️ State Persistence 測試 | State Persistence Test

```bash
# Verify checkpoints are being created
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  ls -lh /var/lib/hlp-executor/state/checkpoints/

# Expected: Checkpoint files present

# Run checkpoint validation
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager validate --recent 5

# Expected: All checkpoints valid
```

#### ☑️ Circuit Breaker 測試 | Circuit Breaker Test

```bash
# Check circuit breaker status
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl http://localhost:8080/metrics | grep circuit_breaker_state

# Expected: All circuit breakers in CLOSED state
```

---

### 3.3 性能驗證 | Performance Validation

#### ☑️ 延遲測試 | Latency Test

```bash
# Test DAG parsing latency
for i in {1..10}; do
  kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
    curl -w "@curl-format.txt" -o /dev/null -s \
    http://localhost:8080/api/v1/parse-dag \
    -X POST -H "Content-Type: application/json" \
    -d '{"dag": "..."}'
done

# Expected: P95 < 120ms
```

#### ☑️ 負載測試 (可選) | Load Test (Optional)

```bash
# Run basic load test
kubectl run load-test --rm -it --restart=Never --image=busybox -- sh -c \
  'for i in $(seq 1 100); do
     wget -qO- http://hlp-executor-service.unmanned-island-system.svc.cluster.local:8080/healthz
   done'

# Monitor resource usage during test
kubectl top pods -n unmanned-island-system -l app=hlp-executor-core
```

---

### 3.4 監控驗證 | Monitoring Verification

#### ☑️ Prometheus Metrics | Prometheus Metrics

```bash
# Verify metrics are being collected
kubectl exec -it -n monitoring prometheus-k8s-0 -- \
  wget -qO- 'http://localhost:9090/api/v1/query?query=up{job="hlp-executor-service"}' | \
  jq '.data.result[0].value[1]'

# Expected: "1" (up)

# Check key metrics
kubectl exec -it -n monitoring prometheus-k8s-0 -- \
  wget -qO- 'http://localhost:9090/api/v1/query?query=hlp_executor_requests_total' | \
  jq '.data.result'

# Expected: Metrics data present
```

#### ☑️ Grafana Dashboard | Grafana Dashboard

```bash
# Check if Grafana dashboard is accessible
# (Manual step: Navigate to Grafana and verify HLP Executor dashboard)

# Dashboard URL: https://grafana/d/hlp-executor-overview
# Expected: All panels loading with data
```

---

## 📝 Phase 4: 交接與文檔 | Rollout & Handover

### 4.1 文檔更新 | Documentation Update

#### ☑️ 更新部署記錄 | Update Deployment Record

```bash
# Record deployment in changelog
cat >> /docs/DEPLOYMENT_CHANGELOG.md <<EOF

## $(date +%Y-%m-%d) - HLP Executor Core v1.0.0 Deployment

- **Deployment Time**: $(date -Iseconds)
- **Deployed By**: <YOUR_NAME>
- **Environment**: Production
- **Namespace**: unmanned-island-system
- **Image**: ghcr.io/unmanned-island/hlp-executor-core:v1.0.0
- **Replicas**: 3
- **Status**: ✅ Successful

### Changes:
- Initial deployment of HLP Executor Core Plugin
- Configured with 3 replicas and HPA (3-10)
- Integrated with Prometheus monitoring

### Post-Deployment Notes:
- All health checks passed
- Functional tests successful
- Performance within SLO targets

EOF
```

#### ☑️ 更新運維文檔 | Update Operations Documentation

```bash
# Update service inventory
cat >> /docs/SERVICE_INVENTORY.md <<EOF

### HLP Executor Core
- **Service Name**: hlp-executor-service
- **Namespace**: unmanned-island-system
- **Replicas**: 3 (HPA: 3-10)
- **Endpoints**:
  - HTTP: http://hlp-executor-service:8080
  - Admin: http://hlp-executor-service:8081
- **Monitoring**: Prometheus ServiceMonitor configured
- **Runbooks**:
  - [Error Handling](./operations/runbooks/HLP_EXECUTOR_ERROR_HANDLING.md)
  - [Emergency](./operations/runbooks/HLP_EXECUTOR_EMERGENCY.md)
  - [Maintenance](./operations/runbooks/HLP_EXECUTOR_MAINTENANCE.md)
- **SLO**: [HLP Executor SLO](./operations/slo/HLP_EXECUTOR_SLO.md)

EOF
```

---

### 4.2 團隊通知 | Team Notification

#### ☑️ 發送部署通知 | Send Deployment Notification

```bash
# Post to Slack #deployments channel
curl -X POST https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🚀 HLP Executor Core v1.0.0 Deployed to Production",
    "attachments": [
      {
        "color": "good",
        "fields": [
          {"title": "Environment", "value": "Production", "short": true},
          {"title": "Namespace", "value": "unmanned-island-system", "short": true},
          {"title": "Replicas", "value": "3", "short": true},
          {"title": "Status", "value": "✅ Healthy", "short": true}
        ]
      }
    ]
  }'
```

#### ☑️ Email 通知 | Email Notification

```bash
# Send email to platform team
mail -s "HLP Executor Deployment - $(date +%Y-%m-%d)" platform-team@unmanned-island.com <<EOF
HLP Executor Core v1.0.0 has been successfully deployed to production.

Deployment Details:
- Time: $(date -Iseconds)
- Namespace: unmanned-island-system
- Replicas: 3 (HPA enabled)
- Health Status: All checks passed

Monitoring:
- Prometheus: Metrics being collected
- Grafana Dashboard: https://grafana/d/hlp-executor-overview

Runbooks:
- Error Handling: docs/operations/runbooks/HLP_EXECUTOR_ERROR_HANDLING.md
- Emergency: docs/operations/runbooks/HLP_EXECUTOR_EMERGENCY.md
- Maintenance: docs/operations/runbooks/HLP_EXECUTOR_MAINTENANCE.md

On-Call Contact: PagerDuty Service ID P1234

EOF
```

---

### 4.3 監控移交 | Monitoring Handover

#### ☑️ 確認告警規則已啟用 | Confirm Alerting Rules Enabled

```bash
# Verify Prometheus alerting rules
kubectl exec -it -n monitoring prometheus-k8s-0 -- \
  wget -qO- 'http://localhost:9090/api/v1/rules' | \
  jq '.data.groups[] | select(.name | contains("hlp_executor"))'

# Expected: HLP Executor alert rules present and active
```

#### ☑️ PagerDuty 整合驗證 | PagerDuty Integration Verification

```bash
# Verify PagerDuty service configuration
# (Manual step: Check PagerDuty dashboard for HLP Executor service)

# Service ID: P1234
# Expected: Service active with escalation policy configured
```

---

## 📊 部署後監控清單 | Post-Deployment Monitoring Checklist

### 第一週監控重點 | First Week Monitoring Focus

- [ ] **Day 1-2**: 每 2 小時檢查一次健康狀態 | Check health every 2 hours
- [ ] **Day 3-5**: 每 6 小時檢查一次 | Check every 6 hours
- [ ] **Day 6-7**: 每日檢查一次 | Check daily

### 關鍵指標監控 | Key Metrics to Monitor

```yaml
first_week_metrics:
  availability:
    target: '> 99.9%'
    check_frequency: 'hourly'

  error_rate:
    target: '< 1%'
    check_frequency: 'hourly'

  latency_p95:
    target: '< 120ms'
    check_frequency: 'every 4 hours'

  resource_usage:
    cpu: '< 80%'
    memory: '< 85%'
    disk: '< 70%'
    check_frequency: 'daily'
```

---

## 🔄 回滾計劃 | Rollback Plan

### 回滾觸發條件 | Rollback Triggers

如遇以下情況應立即回滾：

- ❌ 健康檢查失敗超過 5 分鐘
- ❌ 錯誤率 > 5%
- ❌ P95 延遲 > 200ms 持續 10 分鐘
- ❌ 任何 P1 嚴重性事件

### 回滾程序 | Rollback Procedure

```bash
# Step 1: Rollback deployment
kubectl rollout undo deployment/hlp-executor-core -n unmanned-island-system

# Step 2: Monitor rollback
kubectl rollout status deployment/hlp-executor-core -n unmanned-island-system

# Step 3: Verify health after rollback
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  curl http://localhost:8080/healthz

# Step 4: Restore state if needed (from backup)
kubectl exec -it deployment/hlp-executor-core -n unmanned-island-system -- \
  python3 -m core.safety_mechanisms.checkpoint_manager restore \
  --checkpoint-id <LAST_KNOWN_GOOD>

# Step 5: Notify team
# Post rollback notification to Slack #incidents
```

---

## 📚 相關資源 | Related Resources

- [HLP Executor Error Handling Runbook](../runbooks/HLP_EXECUTOR_ERROR_HANDLING.md)
- [HLP Executor Emergency Runbook](../runbooks/HLP_EXECUTOR_EMERGENCY.md)
- [HLP Executor Maintenance Guide](../runbooks/HLP_EXECUTOR_MAINTENANCE.md)
- [HLP Executor SLO](../slo/HLP_EXECUTOR_SLO.md)
- [Kubernetes Deployment Best Practices](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

## ✅ 簽核 | Sign-off

```yaml
deployment_signoff:
  date: '2025-12-07'
  deployer:
    name: '<YOUR_NAME>'
    role: 'Platform Engineer'
    signature: '________'

  verifier:
    name: '<VERIFIER_NAME>'
    role: 'SRE'
    signature: '________'

  approval:
    name: '<PLATFORM_LEAD_NAME>'
    role: 'Platform Engineering Lead'
    signature: '________'
    date_approved: '________'
```

---

**文件維護者 | Document Maintainer**: Platform Engineering Team  
**審核週期 | Review Cycle**: After each major deployment  
**版本控制 | Version Control**: This checklist should be updated based on
deployment learnings
