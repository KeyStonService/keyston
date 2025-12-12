# Baseline YAML Integration Plan / 基線 YAML 集成方案

**Version:** v1.0.0  
**Date:** 2025-12-07  
**Status:** Planning Phase

---

## 1. 《解構摘要》Deconstruction Summary

### 從 6 個 baseline YAML 檔案抽取的核心邏輯與功能

#### 📦 baseline-01-namespace-governance.v1.0.yaml

**核心概念 Core Concepts:**

- 命名空間治理與隔離 (Namespace Governance & Isolation)
- 標籤規範與強制執行 (Label Standards & Enforcement)
- 能力註冊與聲明機制 (Capability Registry & Declaration)
- 生命週期狀態機 (Lifecycle State Machine)

**功能模組 Functional Modules:**

1. **Namespace Naming Convention**: 生產/預備/開發/特性/租戶環境命名規則
2. **Mandatory Labels Policy**: 9 個必要標籤 + 3 個可選標籤
3. **Lifecycle State Machine**: 8 個狀態轉換 (DECLARED → REGISTERED →
   COORDINATED → ACTIVE → ...)
4. **Capability Registry Schema**: 能力聲明的 JSON Schema 定義
5. **Governance Controller**: ClusterRole/ClusterRoleBinding 配置

**對外依賴 External Dependencies:**

- Kubernetes Namespace API
- Admission Webhooks (ValidatingWebhookConfiguration,
  MutatingWebhookConfiguration)
- etcd 儲存
- GitOps 同步機制

**可重用邏輯 Reusable Logic:**

- 正則表達式驗證模式 (regex patterns)
- 標籤驗證規則 (label validation rules)
- 狀態機定義 (state machine definitions)
- 能力聲明 schema (capability declaration schema)

---

#### 🔐 baseline-02-security-rbac.v1.0.yaml

**核心概念 Core Concepts:**

- 零信任架構原則 (Zero Trust Principles)
- 基於角色的存取控制矩陣 (RBAC Role Matrix)
- 加密標準 (Encryption Standards)
- 審計策略 (Audit Policy)

**功能模組 Functional Modules:**

1. **Zero Trust Principles**: 明確驗證、最小權限、假設入侵
2. **RBAC Role Matrix**: 5 個角色層級 (cluster-admin, platform-operator,
   developer, viewer, ci-cd-automation)
3. **Encryption Standards**:
   - Data at Rest: AES-256-GCM, Vault 後端
   - Data in Transit: mTLS STRICT, TLS 1.3
   - Post-Quantum Cryptography: CRYSTALS-Kyber, CRYSTALS-Dilithium
4. **Authentication Config**: OIDC, Service Account, Certificate
5. **Audit Policy**: 3 級日誌 (metadata, request, request_response)
6. **Pod Security Standards**: 受限安全上下文配置

**對外依賴 External Dependencies:**

- OIDC Provider (Identity Provider)
- HashiCorp Vault (Key Management)
- External KMS (Key Management Service)
- Cert-Manager (Certificate Management)
- Rekor (Transparency Log)

**可重用邏輯 Reusable Logic:**

- 角色權限映射表 (role permission matrix)
- 加密算法配置 (encryption algorithm configs)
- 審計日誌保留策略 (audit log retention policies)
- Pod 安全上下文模板 (pod security context templates)

---

#### 📊 baseline-03-resource-management.v1.0.yaml

**核心概念 Core Concepts:**

- 資源配額與限制 (Resource Quotas & Limits)
- 多租戶隔離 (Multi-tenant Isolation)
- 資源優化策略 (Resource Optimization Strategies)
- 成本分配模型 (Cost Allocation Model)

**功能模組 Functional Modules:**

1. **ResourceQuota**: CPU/Memory/Storage/Object Count 限制
2. **LimitRange**: Pod/Container/PVC 限制範圍
3. **Tenant Tier Definitions**: 4 個租戶層級 (enterprise, business, startup,
   development)
4. **Resource Optimization Rules**:
   - Vertical Pod Autoscaler (VPA)
   - Horizontal Pod Autoscaler (HPA)
   - Resource Bin Packing
   - Overcommitment Policy
5. **Cost Allocation Model**: 計算/儲存/網路/支援成本模型
6. **Quota Enforcement Policy**: 硬限制/軟限制/突發允許
7. **Cluster Capacity Planning**: 50 節點容量規劃
8. **Node Affinity Rules**: 租戶隔離/環境分離/可用區分散/成本優化

**對外依賴 External Dependencies:**

- Kubernetes Metrics Server
- Vertical Pod Autoscaler Operator
- Prometheus (Monitoring)
- Cost Management System

**可重用邏輯 Reusable Logic:**

- 租戶層級配額模板 (tenant tier quota templates)
- 自動擴縮容策略 (autoscaling strategies)
- 成本計算公式 (cost calculation formulas)
- 節點親和性規則 (node affinity rules)

---

#### 🌐 baseline-04-network-policy.v1.0.yaml

**核心概念 Core Concepts:**

- 零信任網路架構 (Zero Trust Network Architecture)
- 微分段策略 (Microsegmentation Strategy)
- 服務網格整合 (Service Mesh Integration)
- 出入口控制 (Ingress/Egress Control)

**功能模組 Functional Modules:**

1. **Default Deny NetworkPolicy**: 預設拒絕所有流量
2. **Microsegmentation Rules**: 4 個網路區域 (DMZ, Application, Data,
   Management)
3. **Service Mesh Policy** (Istio):
   - mTLS STRICT 模式
   - Circuit Breaking
   - Retry Policy
   - Load Balancing
   - Authorization Policies
4. **Ingress Gateway Config**: Public/Private Gateway 配置
5. **Egress Control Policy**: 外部 API 白名單、資料庫出口控制
6. **Network Observability**: Flow Monitoring, Anomaly Detection

**對外依賴 External Dependencies:**

- Istio Service Mesh
- Ingress Controller (Istio Gateway)
- Certificate Manager (TLS Certificates)
- Elastic Flow Collector
- WAF (Web Application Firewall)

**可重用邏輯 Reusable Logic:**

- 網路分段模板 (network segmentation templates)
- mTLS 配置 (mTLS configurations)
- 熔斷器策略 (circuit breaker policies)
- 流量監控規則 (traffic monitoring rules)

---

#### ✅ baseline-05-compliance-attestation.v1.0.yaml

**核心概念 Core Concepts:**

- 合規框架支援 (Compliance Framework Support)
- 策略即代碼引擎 (Policy-as-Code Engine)
- 證明生成機制 (Attestation Generation)
- 配置漂移檢測 (Drift Detection)
- 證據收集系統 (Evidence Collection)

**功能模組 Functional Modules:**

1. **Compliance Standards**:
   - SOC 2 Type II
   - GDPR
   - PCI DSS 4.0
2. **Policy-as-Code Engines**:
   - OPA Gatekeeper (v3.14.0)
   - Kyverno (v1.11.0)
   - Conftest (v0.47.0)
3. **Attestation Providers**:
   - Cosign (Sigstore)
   - in-toto
   - SLSA Provenance
4. **Drift Detection Engine**: 配置漂移/狀態漂移/策略漂移
5. **Evidence Collection**:
   - Audit Logs (7 年保留)
   - Configuration Snapshots (hourly)
   - Security Scans (daily)
   - Access Reviews (quarterly)
   - Incident Records
6. **Merkle Tree Attestation**: 配置樹/部署樹/審計樹
7. **Compliance Attestation CronJob**: 每 6 小時執行

**對外依賴 External Dependencies:**

- OPA Gatekeeper
- Kyverno
- Conftest
- Sigstore/Cosign
- Rekor (Transparency Log)
- S3-compatible Storage (Evidence Bucket)
- etcd (Merkle Root Store)
- Trivy (Vulnerability Scanner)
- kube-bench (CIS Benchmark)

**可重用邏輯 Reusable Logic:**

- 合規控制映射表 (compliance control mappings)
- 策略模板 (policy templates)
- 證明生成腳本 (attestation generation scripts)
- 漂移檢測規則 (drift detection rules)
- 證據收集工作流 (evidence collection workflows)

---

#### ⚛️ baseline-06-quantum-orchestration.v1.0.yaml

**核心概念 Core Concepts:**

- 混合量子-經典計算編排 (Hybrid Quantum-Classical Orchestration)
- 量子線路定義與執行 (Quantum Circuit Definitions & Execution)
- 量子資源池管理 (Quantum Resource Pool Management)
- 量子工作流範本 (Quantum Workflow Templates)

**功能模組 Functional Modules:**

1. **Quantum Circuit Definitions**:
   - QAOA Optimization (16 qubits, 8 depth)
   - VQE Ground State (4 qubits, 12 depth)
   - QNN Classification (8 qubits, 16 depth)
   - QSVM Kernel (6 qubits)
2. **Quantum Resource Pool**:
   - QPU Primary: IBM Brisbane (127 qubits, QV=32768)
   - QPU Secondary: Rigetti Aspen-M-3 (80 qubits, QV=16384)
   - QPU Simulator: Aer Simulator (32 qubits, statevector)
3. **Hybrid Workflow Orchestration** (Argo Workflows):
   - Quantum-Classical Optimization Workflow
   - Quantum ML Training Pipeline
4. **Quantum Execution Scripts**:
   - QAOA Executor (Python/Qiskit)
   - VQE Executor (Python/Qiskit)

**對外依賴 External Dependencies:**

- IBM Quantum (QiskitRuntimeService)
- AWS Braket (Rigetti Backend)
- Argo Workflows
- Qiskit SDK
- Qiskit IBM Runtime
- Container Registry (gcr.io)

**可重用邏輯 Reusable Logic:**

- 量子線路模板 (quantum circuit templates)
- 優化器配置 (optimizer configurations)
- 資源調度策略 (resource scheduling policies)
- 混合工作流編排模式 (hybrid workflow orchestration patterns)
- 量子執行腳本 (quantum execution scripts)

---

## 2. 《邏輯 → 目標位置對應表》Logic to Target Location Mapping

| 邏輯名稱 Logic Name             | 說明 Description | 建議目標路徑 Target Path                                      | 檔案角色 File Role           |
| ------------------------------- | ---------------- | ------------------------------------------------------------- | ---------------------------- |
| **Namespace Naming Convention** | 命名空間命名規則 | `governance/policies/namespace-naming-policy.yaml`            | 治理策略定義                 |
| **Mandatory Labels Schema**     | 必要標籤 Schema  | `governance/schemas/namespace-labels.schema.json`             | JSON Schema 驗證             |
| **Lifecycle State Machine**     | 生命週期狀態機   | `governance/schemas/state-machine.yaml`                       | 狀態轉換定義 (已存在，擴充)  |
| **Capability Registry Schema**  | 能力註冊 Schema  | `governance/schemas/capability-registry.schema.json`          | 能力聲明 Schema              |
| **Zero Trust Principles**       | 零信任原則文檔   | `docs/architecture/security/zero-trust-architecture.md`       | 架構指導文件                 |
| **RBAC Role Matrix**            | 角色權限矩陣     | `governance/policies/security/rbac-role-matrix.yaml`          | 角色定義策略                 |
| **Encryption Standards**        | 加密標準配置     | `config/security-network-config.yml`                          | 安全配置 (已存在，擴充)      |
| **Audit Policy**                | 審計策略         | `governance/policies/security/audit-policy.yaml`              | 審計日誌策略                 |
| **Pod Security Standards**      | Pod 安全標準     | `governance/policies/security/pod-security-standards.yaml`    | Pod 安全策略                 |
| **Tenant Tier Definitions**     | 租戶層級定義     | `config/tenant-tier-definitions.yaml`                         | 租戶配額配置                 |
| **Resource Quota Templates**    | 資源配額模板     | `infrastructure/kubernetes/templates/resource-quotas/`        | K8s 資源範本                 |
| **Autoscaling Strategies**      | 自動擴縮容策略   | `governance/policies/resource-optimization.yaml`              | 資源優化策略                 |
| **Cost Allocation Model**       | 成本分配模型     | `config/cost-allocation-model.yaml`                           | 成本計算配置                 |
| **Microsegmentation Rules**     | 微分段規則       | `infrastructure/kubernetes/templates/network-policies/`       | 網路策略範本                 |
| **Service Mesh Policy**         | 服務網格策略     | `infrastructure/kubernetes/istio/service-mesh-policy.yaml`    | Istio 配置                   |
| **Ingress Gateway Config**      | 入口閘道配置     | `infrastructure/kubernetes/istio/ingress-gateway-config.yaml` | Istio Gateway                |
| **Compliance Standards**        | 合規標準定義     | `governance/policies/compliance/compliance-standards.yaml`    | 合規框架策略                 |
| **Policy-as-Code Templates**    | 策略即代碼範本   | `governance/policies/conftest/`                               | OPA/Kyverno/Conftest 策略    |
| **Attestation Generation**      | 證明生成配置     | `core/slsa_provenance/attestation-config.yaml`                | SLSA 證明配置 (已存在，擴充) |
| **Drift Detection Rules**       | 漂移檢測規則     | `automation/intelligent/drift-detection-rules.yaml`           | 自動化漂移檢測               |
| **Evidence Collection**         | 證據收集工作流   | `governance/audit/evidence-collection-workflow.yaml`          | 審計證據收集                 |
| **Quantum Circuit Library**     | 量子線路庫       | `core/quantum-circuits/`                                      | 量子計算核心 (新建)          |
| **Quantum Resource Pool**       | 量子資源池配置   | `config/quantum-resource-pool.yaml`                           | 量子資源配置                 |
| **Hybrid Workflow Templates**   | 混合工作流範本   | `automation/quantum-workflows/`                               | 量子工作流自動化 (新建)      |
| **Quantum Execution Scripts**   | 量子執行腳本     | `tools/quantum/`                                              | 量子執行工具 (新建)          |
| **Kubernetes Manifests**        | K8s 資源清單     | `infrastructure/kubernetes/baseline/`                         | 基線 K8s 資源 (新建)         |

---

## 3. 《目錄與檔案整合藍圖》Directory & File Integration Blueprint

```
unmanned-island/
├── config/
│   ├── tenant-tier-definitions.yaml              # 從 baseline-03 抽取
│   ├── cost-allocation-model.yaml                # 從 baseline-03 抽取
│   ├── quantum-resource-pool.yaml                # 從 baseline-06 抽取
│   └── security-network-config.yml               # 擴充 baseline-02 加密標準
│
├── core/
│   ├── quantum-circuits/                         # 新建，從 baseline-06 抽取
│   │   ├── README.md                             # 量子線路庫說明
│   │   ├── qaoa-optimization.yaml                # QAOA 線路定義
│   │   ├── vqe-ground-state.yaml                 # VQE 線路定義
│   │   ├── qnn-classification.yaml               # QNN 線路定義
│   │   └── qsvm-kernel.yaml                      # QSVM 線路定義
│   │
│   └── slsa_provenance/
│       └── attestation-config.yaml               # 擴充 baseline-05 證明配置
│
├── docs/
│   ├── architecture/
│   │   └── security/
│   │       ├── zero-trust-architecture.md        # 從 baseline-02 抽取
│   │       ├── encryption-standards.md           # 從 baseline-02 抽取
│   │       └── network-segmentation.md           # 從 baseline-04 抽取
│   │
│   └── refactor_playbooks/
│       ├── 02_integration/
│       │   └── BASELINE_YAML_INTEGRATION_PLAN.md # 本文件
│       │
│       └── 03_refactor/
│           └── meta/
│               ├── KUBERNETES_BASELINE_GUIDE.md  # 基線部署指南
│               └── QUANTUM_ORCHESTRATION_GUIDE.md # 量子編排指南
│
├── governance/
│   ├── audit/
│   │   └── evidence-collection-workflow.yaml     # 從 baseline-05 抽取
│   │
│   ├── policies/
│   │   ├── namespace-naming-policy.yaml          # 從 baseline-01 抽取
│   │   ├── resource-optimization.yaml            # 從 baseline-03 抽取
│   │   │
│   │   ├── compliance/
│   │   │   ├── compliance-standards.yaml         # 從 baseline-05 抽取
│   │   │   ├── soc2-controls.yaml                # 從 baseline-05 細分
│   │   │   ├── gdpr-principles.yaml              # 從 baseline-05 細分
│   │   │   └── pci-dss-requirements.yaml         # 從 baseline-05 細分
│   │   │
│   │   ├── conftest/
│   │   │   └── deployment-best-practices.rego    # 從 baseline-05 抽取
│   │   │
│   │   └── security/
│   │       ├── rbac-role-matrix.yaml             # 從 baseline-02 抽取
│   │       ├── audit-policy.yaml                 # 從 baseline-02 抽取
│   │       └── pod-security-standards.yaml       # 從 baseline-02 抽取
│   │
│   └── schemas/
│       ├── namespace-labels.schema.json          # 從 baseline-01 抽取
│       ├── capability-registry.schema.json       # 從 baseline-01 抽取
│       ├── state-machine.yaml                    # 擴充 baseline-01 生命週期
│       └── tenant-tier.schema.json               # 從 baseline-03 抽取
│
├── infrastructure/
│   └── kubernetes/
│       ├── baseline/                             # 新建，從 6 個 baseline 抽取
│       │   ├── README.md                         # 基線部署說明
│       │   ├── namespace-governance.yaml         # 從 baseline-01 K8s 資源
│       │   ├── security-rbac.yaml                # 從 baseline-02 K8s 資源
│       │   ├── resource-management.yaml          # 從 baseline-03 K8s 資源
│       │   ├── network-policy.yaml               # 從 baseline-04 K8s 資源
│       │   ├── compliance-attestation.yaml       # 從 baseline-05 K8s 資源
│       │   └── quantum-orchestration.yaml        # 從 baseline-06 K8s 資源
│       │
│       ├── istio/
│       │   ├── service-mesh-policy.yaml          # 從 baseline-04 抽取
│       │   └── ingress-gateway-config.yaml       # 從 baseline-04 抽取
│       │
│       └── templates/
│           ├── resource-quotas/                  # 從 baseline-03 抽取
│           │   ├── enterprise-tier.yaml
│           │   ├── business-tier.yaml
│           │   ├── startup-tier.yaml
│           │   └── development-tier.yaml
│           │
│           └── network-policies/                 # 從 baseline-04 抽取
│               ├── default-deny-all.yaml
│               ├── allow-same-namespace.yaml
│               ├── allow-dns.yaml
│               └── microsegmentation-zones.yaml
│
├── automation/
│   ├── intelligent/
│   │   └── drift-detection-rules.yaml            # 從 baseline-05 抽取
│   │
│   └── quantum-workflows/                        # 新建，從 baseline-06 抽取
│       ├── README.md                             # 量子工作流說明
│       ├── qaoa-optimization-workflow.yaml       # QAOA 優化工作流
│       └── qnn-training-pipeline.yaml            # QNN 訓練流水線
│
└── tools/
    └── quantum/                                  # 新建，從 baseline-06 抽取
        ├── README.md                             # 量子工具說明
        ├── qaoa-executor.py                      # QAOA 執行器
        └── vqe-executor.py                       # VQE 執行器
```

---

## 4. 《P0 / P1 / P2 行動清單》Action Plan by Priority

### 🔴 P0: 立刻執行 (Immediate Actions) - 本週完成

| 動作 Action | 目標檔案路徑 Target Path                                                | 動作類型 Action Type | 理由 Reason                                     |
| ----------- | ----------------------------------------------------------------------- | -------------------- | ----------------------------------------------- |
| 1           | `governance/policies/namespace-naming-policy.yaml`                      | 新建                 | 從 baseline-01 抽取命名規則，納入正式治理策略   |
| 2           | `governance/schemas/namespace-labels.schema.json`                       | 新建                 | 從 baseline-01 抽取標籤 schema，供驗證使用      |
| 3           | `governance/policies/security/rbac-role-matrix.yaml`                    | 新建                 | 從 baseline-02 抽取 RBAC 矩陣，定義標準角色     |
| 4           | `governance/policies/security/audit-policy.yaml`                        | 新建                 | 從 baseline-02 抽取審計策略，滿足合規需求       |
| 5           | `config/tenant-tier-definitions.yaml`                                   | 新建                 | 從 baseline-03 抽取租戶層級，配額管理基礎       |
| 6           | `governance/policies/compliance/compliance-standards.yaml`              | 新建                 | 從 baseline-05 抽取合規框架，建立合規基準       |
| 7           | `infrastructure/kubernetes/baseline/README.md`                          | 新建                 | 建立 baseline 部署指南，說明 6 個 baseline 用途 |
| 8           | `docs/refactor_playbooks/03_refactor/meta/KUBERNETES_BASELINE_GUIDE.md` | 新建                 | 建立基線部署文檔，指導如何應用 baseline 到集群  |

**P0 預期成果 Expected Outcomes:**

- 關鍵治理策略移出 `_legacy_scratch`，進入正式目錄
- 建立合規與安全基準
- 提供清晰的部署指南

---

### 🟡 P1: 一週內完成 (Within 1 Week)

| 動作 Action | 目標檔案路徑 Target Path                                      | 動作類型 Action Type | 理由 Reason                                   |
| ----------- | ------------------------------------------------------------- | -------------------- | --------------------------------------------- |
| 9           | `governance/schemas/capability-registry.schema.json`          | 新建                 | 從 baseline-01 抽取能力註冊 schema            |
| 10          | `governance/schemas/state-machine.yaml`                       | 擴充                 | 擴充現有狀態機，加入 baseline-01 生命週期     |
| 11          | `governance/policies/security/pod-security-standards.yaml`    | 新建                 | 從 baseline-02 抽取 Pod 安全標準              |
| 12          | `config/security-network-config.yml`                          | 擴充                 | 擴充現有安全配置，加入 baseline-02 加密標準   |
| 13          | `config/cost-allocation-model.yaml`                           | 新建                 | 從 baseline-03 抽取成本模型                   |
| 14          | `governance/policies/resource-optimization.yaml`              | 新建                 | 從 baseline-03 抽取資源優化策略               |
| 15          | `infrastructure/kubernetes/templates/resource-quotas/*.yaml`  | 新建                 | 從 baseline-03 建立 4 個租戶層級範本          |
| 16          | `infrastructure/kubernetes/templates/network-policies/*.yaml` | 新建                 | 從 baseline-04 建立網路策略範本               |
| 17          | `infrastructure/kubernetes/istio/service-mesh-policy.yaml`    | 新建                 | 從 baseline-04 抽取 Istio 服務網格配置        |
| 18          | `infrastructure/kubernetes/istio/ingress-gateway-config.yaml` | 新建                 | 從 baseline-04 抽取 Ingress Gateway 配置      |
| 19          | `governance/policies/compliance/soc2-controls.yaml`           | 新建                 | 從 baseline-05 細分 SOC 2 控制                |
| 20          | `governance/policies/compliance/gdpr-principles.yaml`         | 新建                 | 從 baseline-05 細分 GDPR 原則                 |
| 21          | `governance/policies/compliance/pci-dss-requirements.yaml`    | 新建                 | 從 baseline-05 細分 PCI DSS 需求              |
| 22          | `governance/policies/conftest/deployment-best-practices.rego` | 新建                 | 從 baseline-05 抽取 Conftest 策略             |
| 23          | `core/slsa_provenance/attestation-config.yaml`                | 擴充                 | 擴充現有 SLSA 配置，加入 baseline-05 證明機制 |
| 24          | `automation/intelligent/drift-detection-rules.yaml`           | 新建                 | 從 baseline-05 抽取漂移檢測規則               |
| 25          | `governance/audit/evidence-collection-workflow.yaml`          | 新建                 | 從 baseline-05 抽取證據收集工作流             |
| 26          | `infrastructure/kubernetes/baseline/*.yaml`                   | 新建                 | 建立 6 個 baseline 的 K8s 資源清單            |
| 27          | `docs/architecture/security/zero-trust-architecture.md`       | 新建                 | 從 baseline-02 抽取零信任架構文檔             |
| 28          | `docs/architecture/security/encryption-standards.md`          | 新建                 | 從 baseline-02 抽取加密標準文檔               |
| 29          | `docs/architecture/security/network-segmentation.md`          | 新建                 | 從 baseline-04 抽取網路分段文檔               |

**P1 預期成果 Expected Outcomes:**

- 完成所有非量子相關的治理策略、配置、範本遷移
- 建立完整的 Kubernetes 基線資源清單
- 補充安全架構文檔

---

### 🟢 P2: 長期優化 (Long-term Optimization) - 2-4 週內完成

| 動作 Action | 目標檔案路徑 Target Path                                                  | 動作類型 Action Type | 理由 Reason                        |
| ----------- | ------------------------------------------------------------------------- | -------------------- | ---------------------------------- |
| 30          | `core/quantum-circuits/README.md`                                         | 新建                 | 建立量子線路庫文檔                 |
| 31          | `core/quantum-circuits/qaoa-optimization.yaml`                            | 新建                 | 從 baseline-06 抽取 QAOA 線路定義  |
| 32          | `core/quantum-circuits/vqe-ground-state.yaml`                             | 新建                 | 從 baseline-06 抽取 VQE 線路定義   |
| 33          | `core/quantum-circuits/qnn-classification.yaml`                           | 新建                 | 從 baseline-06 抽取 QNN 線路定義   |
| 34          | `core/quantum-circuits/qsvm-kernel.yaml`                                  | 新建                 | 從 baseline-06 抽取 QSVM 線路定義  |
| 35          | `config/quantum-resource-pool.yaml`                                       | 新建                 | 從 baseline-06 抽取量子資源池配置  |
| 36          | `automation/quantum-workflows/README.md`                                  | 新建                 | 建立量子工作流文檔                 |
| 37          | `automation/quantum-workflows/qaoa-optimization-workflow.yaml`            | 新建                 | 從 baseline-06 抽取 QAOA 工作流    |
| 38          | `automation/quantum-workflows/qnn-training-pipeline.yaml`                 | 新建                 | 從 baseline-06 抽取 QNN 訓練流水線 |
| 39          | `tools/quantum/README.md`                                                 | 新建                 | 建立量子工具文檔                   |
| 40          | `tools/quantum/qaoa-executor.py`                                          | 新建                 | 從 baseline-06 抽取 QAOA 執行腳本  |
| 41          | `tools/quantum/vqe-executor.py`                                           | 新建                 | 從 baseline-06 抽取 VQE 執行腳本   |
| 42          | `docs/refactor_playbooks/03_refactor/meta/QUANTUM_ORCHESTRATION_GUIDE.md` | 新建                 | 建立量子編排指南                   |
| 43          | `governance/schemas/tenant-tier.schema.json`                              | 新建                 | 從 baseline-03 抽取租戶層級 schema |
| 44          | `docs/refactor_playbooks/_legacy_scratch/*.yaml`                          | 刪除                 | 整合完成後清理暫存檔案             |

**P2 預期成果 Expected Outcomes:**

- 完成量子計算相關模組的整合（實驗性功能）
- 補充量子編排文檔與工具
- 清空 `_legacy_scratch` 目錄

---

## 5. 《legacy_scratch 清理計畫》Legacy Cleanup Plan

### 清理條件 Cleanup Conditions

| 檔案 File                                      | 清理條件 Condition | 依賴檢查 Dependency Check                                 |
| ---------------------------------------------- | ------------------ | --------------------------------------------------------- |
| `baseline-01-namespace-governance.v1.0.yaml`   | P0 完成 + P1 完成  | ✓ 策略已遷移至 `governance/policies/`                     |
|                                                |                    | ✓ Schema 已遷移至 `governance/schemas/`                   |
|                                                |                    | ✓ K8s 資源已遷移至 `infrastructure/kubernetes/baseline/`  |
| `baseline-02-security-rbac.v1.0.yaml`          | P0 完成 + P1 完成  | ✓ 安全策略已遷移至 `governance/policies/security/`        |
|                                                |                    | ✓ 配置已整合至 `config/security-network-config.yml`       |
|                                                |                    | ✓ 文檔已建立於 `docs/architecture/security/`              |
| `baseline-03-resource-management.v1.0.yaml`    | P0 完成 + P1 完成  | ✓ 租戶配置已遷移至 `config/`                              |
|                                                |                    | ✓ 範本已建立於 `infrastructure/kubernetes/templates/`     |
|                                                |                    | ✓ 策略已遷移至 `governance/policies/`                     |
| `baseline-04-network-policy.v1.0.yaml`         | P1 完成            | ✓ 網路策略已遷移至 `infrastructure/kubernetes/templates/` |
|                                                |                    | ✓ Istio 配置已遷移至 `infrastructure/kubernetes/istio/`   |
|                                                |                    | ✓ 文檔已建立於 `docs/architecture/security/`              |
| `baseline-05-compliance-attestation.v1.0.yaml` | P0 完成 + P1 完成  | ✓ 合規策略已遷移至 `governance/policies/compliance/`      |
|                                                |                    | ✓ 證明配置已整合至 `core/slsa_provenance/`                |
|                                                |                    | ✓ 審計工作流已遷移至 `governance/audit/`                  |
| `baseline-06-quantum-orchestration.v1.0.yaml`  | P2 完成            | ✓ 量子線路已遷移至 `core/quantum-circuits/`               |
|                                                |                    | ✓ 量子工作流已遷移至 `automation/quantum-workflows/`      |
|                                                |                    | ✓ 量子工具已遷移至 `tools/quantum/`                       |

### 清理步驟 Cleanup Steps

1. **P0 完成後** (本週末):
   - ✅ 驗證 P0 行動清單完成
   - ✅ 執行驗證腳本：`tools/docs/validate_baseline_migration.py --phase P0`
   - ⏸️ 暫不刪除 `_legacy_scratch` 檔案

2. **P1 完成後** (下週末):
   - ✅ 驗證 P1 行動清單完成
   - ✅ 執行驗證腳本：`tools/docs/validate_baseline_migration.py --phase P1`
   - ✅ 刪除 baseline-01 至 baseline-05（保留 baseline-06）
   - ✅ 更新 `_legacy_scratch/.gitkeep` 註明原因

3. **P2 完成後** (2-4 週後):
   - ✅ 驗證 P2 行動清單完成
   - ✅ 執行驗證腳本：`tools/docs/validate_baseline_migration.py --phase P2`
   - ✅ 刪除 baseline-06
   - ✅ 移除 `_legacy_scratch` 目錄（保留歷史記錄於 Git）
   - ✅ 更新 `docs/refactor_playbooks/02_integration/` 索引

### 最終狀態 Final State

```
docs/refactor_playbooks/
├── 01_deconstruction/          # 解構劇本
├── 02_integration/             # 集成劇本
│   └── BASELINE_YAML_INTEGRATION_PLAN.md  # 本文件，永久保留
├── 03_refactor/                # 最終重構劇本
│   └── meta/
│       ├── KUBERNETES_BASELINE_GUIDE.md
│       └── QUANTUM_ORCHESTRATION_GUIDE.md
└── _legacy_scratch/            # 🗑️ 刪除（Git 歷史保留）
```

---

## 6. 驗證與品質保證 Validation & Quality Assurance

### 自動化驗證腳本 Automated Validation Script

建議建立 `tools/docs/validate_baseline_migration.py`:

```python
#!/usr/bin/env python3
"""
Baseline YAML 遷移驗證腳本
Validates the migration of baseline YAML files from legacy_scratch to proper locations.
"""

import os
import sys
import yaml
import json
from pathlib import Path

VALIDATION_RULES = {
    "P0": [
        "governance/policies/namespace-naming-policy.yaml",
        "governance/schemas/namespace-labels.schema.json",
        "governance/policies/security/rbac-role-matrix.yaml",
        "governance/policies/security/audit-policy.yaml",
        "config/tenant-tier-definitions.yaml",
        "governance/policies/compliance/compliance-standards.yaml",
        "infrastructure/kubernetes/baseline/README.md",
        "docs/refactor_playbooks/03_refactor/meta/KUBERNETES_BASELINE_GUIDE.md",
    ],
    "P1": [
        # ... (省略完整列表)
    ],
    "P2": [
        # ... (省略完整列表)
    ]
}

def validate_phase(phase: str, repo_root: Path) -> bool:
    """驗證指定階段的檔案是否已建立"""
    missing_files = []
    for file_path in VALIDATION_RULES[phase]:
        full_path = repo_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ {phase} 驗證失敗，缺少以下檔案:")
        for f in missing_files:
            print(f"  - {f}")
        return False
    else:
        print(f"✅ {phase} 驗證通過，所有檔案已建立")
        return True

if __name__ == "__main__":
    # ... (完整實現)
```

### 手動檢查清單 Manual Checklist

- [ ] 所有 YAML 檔案語法正確 (`yamllint`)
- [ ] 所有 JSON Schema 有效 (`jsonschema`)
- [ ] 所有 Markdown 文檔格式正確 (`markdownlint`)
- [ ] 跨檔案引用正確（例如 schema 引用、policy 引用）
- [ ] 文檔中的檔案路徑正確
- [ ] 所有新建目錄包含 README.md
- [ ] Git commit message 清晰描述變更

---

## 7. 風險與緩解措施 Risks & Mitigation

| 風險 Risk              | 影響 Impact | 緩解措施 Mitigation                                 |
| ---------------------- | ----------- | --------------------------------------------------- |
| 遷移過程中遺失關鍵配置 | 高          | 使用 Git 版本控制，保留 legacy_scratch 直到完全驗證 |
| 跨檔案引用斷裂         | 中          | 建立自動化驗證腳本檢查引用完整性                    |
| 量子計算模組實驗性質高 | 低          | 量子模組放在 P2，不影響核心功能                     |
| 文檔與實際配置不一致   | 中          | 建立 CI 檢查，確保文檔範例與實際配置同步            |
| 團隊成員不熟悉新結構   | 中          | 建立遷移指南與培訓文檔                              |

---

## 8. 後續行動 Next Steps

1. **立即行動 (本週)**:
   - 執行 P0 行動清單 (8 項)
   - 建立驗證腳本 `tools/docs/validate_baseline_migration.py`
   - 更新 `DOCUMENTATION_INDEX.md` 包含新建檔案

2. **短期行動 (下週)**:
   - 執行 P1 行動清單 (21 項)
   - 建立 CI 工作流驗證遷移完整性
   - 刪除 baseline-01 至 baseline-05

3. **長期行動 (2-4 週)**:
   - 執行 P2 行動清單 (15 項)
   - 完成量子計算模組整合
   - 清空 `_legacy_scratch` 目錄
   - 更新知識圖譜 (`make all-kg`)

---

## 9. 附錄 Appendix

### A. 參考文件 Reference Documents

- 🏗️ [Refactor Playbook README](../README.md)
- 📋 [AI Behavior Contract](../../../.github/AI-BEHAVIOR-CONTRACT.md)
- 🔧 [GitHub Copilot Instructions](../../../.github/copilot-instructions.md)
- 🗂️ [Documentation Index](../../../DOCUMENTATION_INDEX.md)
- 🏛️ [Governance README](../../../governance/README.md)

### B. 相關議題 Related Issues

- Issue #XXX: Baseline YAML 重構追蹤
- Issue #YYY: 量子計算模組整合
- Issue #ZZZ: 合規框架實施

### C. 變更歷史 Change History

| 日期 Date  | 版本 Version | 變更說明 Changes             | 作者 Author    |
| ---------- | ------------ | ---------------------------- | -------------- |
| 2025-12-07 | v1.0.0       | 初始版本：完整解構與整合計畫 | GitHub Copilot |

---

**文件狀態 Document Status:** ✅ 規劃完成，等待執行  
**下一步審查 Next Review:** P0 執行完成後  
**負責人 Owner:** Repository Maintainers
