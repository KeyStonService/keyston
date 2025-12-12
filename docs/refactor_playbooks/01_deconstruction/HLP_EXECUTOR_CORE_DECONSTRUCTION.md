# HLP Executor Core Plugin - 完整解構分析

## 文件來源

- **原始檔案**: `docs/refactor_playbooks/_legacy_scratch/README.md`
- **文件類型**: Quantum-YAML 插件規格 (v1.0.0)
- **系統**: AXIOM-v1 / HLP (Hard Logic Plugin) System

---

## 一、核心概念（Core Concepts）

### 1.1 插件身份與治理

- **Plugin ID**: `hlp-executor-core`
- **Plugin Type**: 執行引擎 (executor-engine)
- **Security Clearance**: L31-supreme
- **Quantum Enabled**: 支援量子增強運算
- **Compliance Tags**: SLSA-L3, quantum-safe, enterprise-ready

### 1.2 核心功能（Core Capabilities）

1. **Runtime Execution Graph**: 執行時圖構建與調度
2. **State Machine Orchestration**: 狀態機編排系統
3. **Partial Rollback Management**: 部分回滾管理（Phase-level granularity）
4. **Dynamic Retry Policies**: 動態重試策略（指數退避 + 風險自適應）

### 1.3 架構模型

- **Execution Model**: Async DAG Orchestrator（非同步有向無環圖編排器）
- **State Persistence**: Kubernetes etcd
- **Checkpoint Strategy**: Phase-level（階段級檢查點）
- **Recovery Mode**: Partial rollback（部分回滾）

---

## 二、功能模組解構（Functional Modules）

### 2.1 執行引擎模組（Execution Engine）

**位置**: `plugin_implementation.core_logic.execution_graph_builder`

**功能**:

- 拓撲排序 + 風險權重分析
- 關鍵路徑分析（Critical Path Analysis）
- 最大寬度調度（Max-Width Scheduling）並行化

**依賴**:

- `kubernetes-api`
- `axiom-quantum-runtime`
- `axiom-trust-bundle`

### 2.2 狀態管理模組（State Management）

**位置**: `architecture.state_machine`

**狀態流轉**:

```
PENDING → SCHEDULING → EXECUTING → VERIFYING → COMMIT
                ↓           ↓            ↓
              FAILED     FAILED      ROLLBACK → PENDING
```

**特性**:

- 持久化層: Kubernetes Custom Resources
- 檢查點頻率: Per-phase
- 恢復策略: Last-known-good-state

### 2.3 部分回滾模組（Partial Rollback）

**位置**: `rollback_configuration.partial_phase_rollback`

**粒度層級**:

- Phase（階段）
- Plan-unit（計劃單元）
- Artifact（工件）

**觸發條件**:

- 驗證失敗 → 回滾當前階段
- 資源耗盡 → 重新調度 + 退避
- 安全違規 → 緊急停止 + 完整回滾

### 2.4 重試策略模組（Retry Policy）

**位置**: `architecture.retry_policy`

**策略**:

- 基礎延遲: 2000ms
- 最大嘗試次數: 4
- 最大延遲: 30000ms
- Jitter: 啟用
- Risk Adaptive: 啟用

### 2.5 錯誤處理模組（Error Handling）

**位置**: `error_handling.failure_modes`

**故障模式**:

1. **Kubernetes API 不可用**: 指數退避 + 斷路器
2. **狀態持久化失敗**: 降級到記憶體狀態
3. **Quantum Backend 不可用**: 優雅降級到經典模式

**斷路器參數**:

- 失敗閾值: 5
- 恢復超時: 30s
- 半開最大調用: 3

---

## 三、部署與基礎設施（Deployment & Infrastructure）

### 3.1 Kubernetes 部署規格

**位置**: `runtime_configuration.kubernetes_deployment`

**關鍵配置**:

- Replicas: 3（基本） → 20（最大，HPA）
- Service Account: `hlp-executor-sa`
- Priority Class: `axiom-critical`
- Security Context: Non-root (UID 65534)

**容器配置**:

- Image: `registry.local/axiom/hlp-executor-core:v1.0.0@sha256:secure-digest`
- Ports: 8080 (HTTP), 9090 (Metrics), 50051 (gRPC)

**資源需求**:

- Requests: 4 CPU, 16Gi Memory, 1 GPU
- Limits: 8 CPU, 32Gi Memory, 2 GPU

### 3.2 Volume 掛載

- **trust-bundle**: `/etc/axiom/trust` (ReadOnly)
- **config**: `/etc/axiom/config` (ReadOnly)
- **state-storage**: `/var/lib/axiom/state` (PVC)

### 3.3 健康檢查

- **Liveness Probe**: `/health/live` (30s initial delay, 10s period)
- **Readiness Probe**: `/health/ready` (10s initial delay, 5s period)

---

## 四、安全與合規（Security & Compliance）

### 4.1 RBAC 權限

**位置**: `security_configuration.rbac`

**資源權限**:

- Core API: pods, services, configmaps (CRUD)
- Apps API: deployments, replicasets (CRUD except delete)
- Batch API: jobs, cronjobs (CRUD)
- Custom API (axiom.io): quantumjobs, executionplans (全權限)

### 4.2 Network Policies

**Ingress**:

- 允許來源: `unmanned-island-system` namespace + `axiom-kernel` pod
- 允許端口: 8080 (TCP), 50051 (TCP)

**Egress**:

- 允許目標: `unmanned-island-system` namespace
- 允許端口: 443, 5432, 6379 (TCP)

### 4.3 Supply Chain Security

**位置**: `supply_chain_security`

**要求**:

- Cosign Verification: 啟用
- SBOM Format: SPDX-JSON
- Vulnerability Scanning: Block Critical/High
- SLSA Level: 3
- Build Platform: axiom-secure-build

### 4.4 Compliance

- **GDPR**: 7 天日誌保留，JSON Export API
- **SOC2 Type 2**: 存取日誌、靜態/傳輸加密、多 AZ 部署
- **Quantum-Safe Crypto**: ML-KEM-768, ML-DSA-65

---

## 五、可觀測性（Observability）

### 5.1 Prometheus Metrics

**位置**: `observability_configuration.metrics.prometheus_metrics`

**指標**:

1. `hlp_executor_tasks_total` (counter): 總任務數（按狀態、階段）
2. `hlp_executor_execution_duration_seconds` (histogram): 執行時長
3. `hlp_executor_rollback_operations_total` (counter): 回滾操作數

### 5.2 日誌配置

- **格式**: JSON
- **Correlation ID**: Trace Context
- **結構化日誌**: 啟用

### 5.3 分散式追蹤

- **OpenTelemetry**: 啟用
- **Sampling Rate**: 0.1 (10%)
- **Exporters**: Jaeger, axiom-trace-collector

---

## 六、整合點（Integration Points）

### 6.1 Quantum Integration

- **Scheduler Endpoint**:
  `quantum-scheduler.unmanned-island-system.svc.cluster.local:8888`
- **Circuit Optimizer**:
  `quantum-circuit-optimizer.unmanned-island-system.svc.cluster.local:8889`

### 6.2 Knowledge Graph

- **KG Builder**:
  `kg-graph-builder.unmanned-island-system.svc.cluster.local:8890`
- **Vector Search**:
  `kg-vector-hybrid.unmanned-island-system.svc.cluster.local:8891`

### 6.3 Observability Stack

- **Prometheus**: `prometheus.unmanned-island-system.svc.cluster.local:9090`
- **Grafana**: `grafana.unmanned-island-system.svc.cluster.local:3000`
- **Trace Collector**:
  `axiom-trace-collector.unmanned-island-system.svc.cluster.local:14268`

---

## 七、部署生命週期（Deployment Lifecycle）

### 7.1 Canary Deployment

- **Traffic Split**: 10%
- **Success Criteria**: 錯誤率 < 1%, P95 延遲 < 200ms

### 7.2 Blue-Green Deployment

- **Validation Period**: 5 分鐘
- **Auto Promotion**: 禁用（手動確認）

### 7.3 Rolling Update

- **Max Unavailable**: 25%
- **Max Surge**: 25%
- **Revision History**: 10

---

## 八、測試配置（Testing Configuration）

### 8.1 單元測試

- **Framework**: Jest
- **Coverage Threshold**: 90%

### 8.2 整合測試

- **Quantum Backend Simulation**: 啟用
- **K8s Test Environment**: Kind

### 8.3 混沌工程

- **Scenarios**: pod-kill, network-latency, resource-exhaustion

### 8.4 性能測試

- **Tool**: k6
- **Target RPS**: 1000
- **Duration**: 10 分鐘

---

## 九、運維手冊（Operational Runbooks）

### 9.1 緊急程序

1. **executor-core-down** (P1)
   - 升級路徑: oncall-engineer → platform-team-lead → CTO

2. **state-corruption-detected** (P2)
   - 恢復步驟: 啟用狀態備份恢復 → 驗證數據完整性

### 9.2 維護程序

1. **rolling-restart**
   - 頻率: 每週
   - 維護窗口: 02:00-04:00 UTC

2. **state-cleanup**
   - 頻率: 每日
   - 保留期: 7 天

---

## 十、依賴關係（Dependencies）

### 10.1 Hard Dependencies

- `axiom-kernel-compute` (>= 1.0.0)
- `axiom-bootstrap-core` (>= 1.0.0)

### 10.2 Soft Dependencies

- `quantum-scheduler` (>= 0.9.0) - 優雅降級

---

## 十一、性能目標（Performance Targets）

### 11.1 SLO Metrics

- DAG 解析延遲 (P95): 120ms
- 狀態轉換延遲 (P90): 50ms
- 恢復時間目標 (RTO): 30s
- 可用性: 99.9%

### 11.2 資源限制

- 最大並發執行: 1000
- 每次執行最大計劃單元: 500
- 狀態歷史保留: 7 天

### 11.3 自動擴展

- HPA: 3-20 個副本
- CPU 目標: 70%
- Memory 目標: 80%

---

## 十二、版本歷史（Version History）

### v1.0.0 (2025-09-14)

- 初始版本
- 核心執行引擎
- 部分回滾支援
- Quantum Backend 整合
- 企業安全功能

---

## 解構總結

此文檔從 548 行的 Quantum-YAML 規格中提取了：

1. **12 個主要概念領域**
2. **5 個核心功能模組**
3. **3 層安全配置**（RBAC, Network Policies, Supply Chain）
4. **6 個整合點**（Quantum, KG, Observability）
5. **4 種部署策略**（Canary, Blue-Green, Rolling, HPA）
6. **11 組 SLO 指標**

下一步：將這些邏輯元件映射到 Unmanned Island 系統的正式結構中。
