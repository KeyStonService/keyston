# HLP Executor Core Plugin - P0/P1/P2 行動清單

## 清單說明

- **P0 (立即執行)**: 關鍵路徑檔案，必須立即創建/移動以確保系統核心功能可運作
- **P1 (一週內完成)**: 重要但非阻塞性檔案，一週內完成重構
- **P2 (長期優化)**: 優化與增強功能，可逐步完成

**動作類型**:
- `CREATE`: 創建新檔案
- `UPDATE`: 更新現有檔案
- `MOVE`: 移動檔案
- `MERGE`: 合併多個檔案
- `DELETE`: 刪除檔案（僅針對 legacy_scratch）

---

## P0 行動清單（立即執行）

### P0-1: 註冊插件到治理體系
**目標檔案**: `governance/registry/plugins/hlp-executor-core.yaml`  
**動作類型**: CREATE  
**理由**: 建立插件正式註冊清單，使其可被服務發現系統識別

**內容要點**:
```yaml
plugin_id: "hlp-executor-core"
version: "1.0.0"
plugin_type: "executor-engine"
security_clearance: "L3-enterprise"
compliance_tags: ["SLSA-L3", "quantum-safe", "enterprise-ready"]
dependencies:
  hard:
    - kubernetes-api
    - trust-bundle
  soft:
    - quantum-scheduler
```

---

### P0-2: 更新系統模組映射
**目標檔案**: `config/system-module-map.yaml`  
**動作類型**: UPDATE  
**理由**: 將 HLP Executor 整合到系統模組映射中，建立模組發現路徑

**新增條目**:
```yaml
modules:
  execution:
    hlp-executor-core:
      path: "core/hlp_executor"
      type: "execution-engine"
      provides: ["dag-orchestration", "partial-rollback", "state-management"]
      requires: ["kubernetes-api", "trust-bundle"]
```

---

### P0-3: 創建 Kubernetes 部署清單
**目標檔案**: `infrastructure/kubernetes/deployments/hlp-executor-core.yaml`  
**動作類型**: CREATE  
**理由**: 定義 K8s 部署規格，使插件可在集群中運行

**從 legacy_scratch 提取**:
- Deployment spec (replicas, image, resources)
- Container ports (8080, 9090, 50051)
- Environment variables
- Volume mounts (trust-bundle, config, state-storage)
- Probes (liveness, readiness)

**修改點**:
- Namespace: `unmanned-island-system` → `unmanned-island-system`
- Image registry: `registry.local` → 使用實際 registry
- GPU 要求設為 optional

---

### P0-4: 創建 RBAC 配置
**目標檔案**: `infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml`  
**動作類型**: CREATE  
**理由**: 定義服務帳戶與權限，確保安全存取 K8s API

**內容要點**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: hlp-executor-sa
  namespace: unmanned-island-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: hlp-executor-role
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  # ... (其他規則)
```

---

### P0-5: 創建網絡策略
**目標檔案**: `infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml`  
**動作類型**: CREATE  
**理由**: 限制網絡存取，遵循最小權限原則

**內容要點**:
- Ingress: 僅允許來自 `unmanned-island-system` namespace
- Egress: 僅允許到資料庫、Redis、其他系統服務

---

### P0-6: 創建持久化存儲配置
**目標檔案**: `infrastructure/kubernetes/storage/hlp-executor-storage.yaml`  
**動作類型**: CREATE  
**理由**: 定義 PVC 與 ConfigMap，確保狀態持久化

**內容要點**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hlp-executor-state
  namespace: unmanned-island-system
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 100Gi
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: hlp-executor-config
data:
  executor.yaml: |
    # 執行器配置
```

---

### P0-7: 建立 SLSA 證據目錄結構
**目標檔案**: `core/slsa_provenance/plugins/hlp-executor-core/`  
**動作類型**: CREATE (directory)  
**理由**: 準備 SLSA L3 供應鏈安全證據存放位置

**目錄結構**:
```
core/slsa_provenance/plugins/hlp-executor-core/
├── README.md
├── sbom.spdx.json
├── provenance.intoto.json
└── signatures/
    └── cosign.bundle
```

---

### P0-8: 更新依賴配置
**目標檔案**: `config/dependencies.yaml`  
**動作類型**: UPDATE  
**理由**: 聲明 HLP Executor 的依賴關係，支援依賴解析

**新增條目**:
```yaml
components:
  hlp-executor-core:
    version: "1.0.0"
    dependencies:
      required:
        - kubernetes-api: ">= 1.24"
        - trust-bundle: ">= 1.0.0"
      optional:
        - quantum-scheduler: ">= 0.9.0"
          graceful_degradation: true
```

---

### P0-9: 創建執行模型架構文件
**目標檔案**: `docs/architecture/EXECUTION_MODEL.md`  
**動作類型**: CREATE  
**理由**: 記錄核心架構決策，供開發者與維運人員參考

**章節**:
1. 概述（Async DAG Orchestrator）
2. 執行圖構建算法（拓撲排序 + 風險權重）
3. 並行化策略（最大寬度調度）
4. 狀態持久化機制（K8s etcd）
5. 架構圖（Mermaid）

---

### P0-10: 創建部分回滾模組
**目標檔案**: `core/safety_mechanisms/partial_rollback.py`  
**動作類型**: CREATE  
**理由**: 實現核心安全功能，確保執行失敗時可安全回滾

**功能要點**:
- Phase-level rollback
- Plan-unit-level rollback
- Artifact-level rollback
- Dependency tracking (forward & backward)
- Rollback trigger evaluation

**接口**:
```python
class PartialRollbackManager:
    def evaluate_rollback_trigger(self, condition: str, scope: str) -> RollbackAction
    def execute_rollback(self, scope: str, target: str) -> RollbackResult
    def create_checkpoint(self, phase_id: str) -> Checkpoint
    def restore_from_checkpoint(self, checkpoint_id: str) -> RestoreResult
```

---

## P1 行動清單（一週內完成）

### P1-1: 創建狀態機 JSON Schema
**目標檔案**: `governance/schemas/state-machine.schema.json`  
**動作類型**: CREATE  
**理由**: 定義狀態機規範，使其可被驗證工具檢查

**Schema 要點**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "initial_state": {"type": "string"},
    "states": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "transitions": {"type": "array"},
          "timeout_seconds": {"type": "integer"},
          "final_state": {"type": "boolean"},
          "recovery_state": {"type": "boolean"}
        }
      }
    }
  }
}
```

---

### P1-2: 更新向量配置索引
**目標檔案**: `config/unified-config-index.yaml`  
**動作類型**: UPDATE  
**理由**: 整合 HLP Executor 的語義向量配置

**新增區塊**:
```yaml
vector_alignment:
  hlp_executor:
    - intent: "task-execution"
      embedding_model: "axiom-embed-v2"
      dimension: 1024
      similarity_threshold: 0.85
    - intent: "state-management"
      embedding_model: "axiom-embed-v2"
      dimension: 1024
      similarity_threshold: 0.80
```

---

### P1-3: 創建檢查點策略文件
**目標檔案**: `docs/architecture/CHECKPOINT_STRATEGY.md`  
**動作類型**: CREATE  
**理由**: 記錄檢查點機制設計，供實現者參考

**章節**:
1. Phase-level 檢查點設計
2. Copy-on-Write 策略
3. 保留策略（最近 5 個檢查點）
4. 壓縮策略（gzip）
5. 恢復流程

---

### P1-4: 創建恢復模式文件
**目標檔案**: `docs/architecture/RECOVERY_MODE.md`  
**動作類型**: CREATE  
**理由**: 記錄部分回滾與恢復邏輯

**章節**:
1. 回滾粒度（Phase, Plan-unit, Artifact）
2. 觸發條件與動作映射
3. Last-known-good-state 策略
4. 依賴追蹤（前向與後向）
5. 恢復流程圖

---

### P1-5: 創建 HPA 配置
**目標檔案**: `infrastructure/kubernetes/autoscaling/hlp-executor-hpa.yaml`  
**動作類型**: CREATE  
**理由**: 實現水平自動擴展，滿足彈性需求

**內容要點**:
```yaml
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
  maxReplicas: 20
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
```

---

### P1-6: 創建安全政策文件
**目標檔案**: `governance/policies/security/hlp-executor-security-policy.yaml`  
**動作類型**: CREATE  
**理由**: 定義合規要求（GDPR, SOC2, Quantum-Safe）

**內容要點**:
```yaml
policy_id: "hlp-executor-security-policy"
version: "1.0.0"
compliance:
  gdpr:
    data_retention: "7d"
    data_portability: true
    lawfulness: "legitimate-interest"
  soc2_type2:
    security_controls: ["access-logging", "encryption-at-rest", "encryption-in-transit"]
    availability_controls: ["multi-az-deployment", "automated-failover"]
  quantum_safe:
    enabled: true
    algorithms: ["ML-KEM-768", "ML-DSA-65"]
    transition_plan: "hybrid-classical-pq"
```

---

### P1-7: 創建 Prometheus ServiceMonitor
**目標檔案**: `infrastructure/monitoring/prometheus/servicemonitors/hlp-executor-metrics.yaml`  
**動作類型**: CREATE  
**理由**: 配置 Prometheus 抓取指標

**內容要點**:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: hlp-executor-metrics
  namespace: unmanned-island-system
spec:
  selector:
    matchLabels:
      app: hlp-executor-core
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

---

### P1-8: 更新日誌配置
**目標檔案**: `config/monitoring.yaml`  
**動作類型**: UPDATE  
**理由**: 整合 HLP Executor 的日誌配置

**新增區塊**:
```yaml
logging:
  hlp_executor:
    format: "json"
    level: "INFO"
    correlation_id: "trace-context"
    structured: true
```

---

### P1-9: 創建重試策略模組
**目標檔案**: `core/safety_mechanisms/retry_policies.py`  
**動作類型**: UPDATE (如已存在) 或 CREATE  
**理由**: 實現重試邏輯，支援指數退避 + Jitter + Risk-Adaptive

**新增函數**:
```python
def hlp_executor_retry_policy(attempt: int, risk_score: float) -> int:
    """
    計算 HLP Executor 的重試延遲
    
    Args:
        attempt: 當前重試次數 (0-based)
        risk_score: 風險評分 (0.0-1.0)
    
    Returns:
        延遲毫秒數
    """
    base_delay_ms = 2000
    max_delay_ms = 30000
    jitter = random.uniform(0.8, 1.2)
    risk_factor = 1 + risk_score  # 高風險延長重試間隔
    
    delay = min(base_delay_ms * (2 ** attempt) * risk_factor * jitter, max_delay_ms)
    return int(delay)
```

---

### P1-10: 更新斷路器配置
**目標檔案**: `config/safety-mechanisms.yaml`  
**動作類型**: UPDATE  
**理由**: 新增 HLP Executor 的斷路器參數

**新增區塊**:
```yaml
circuit_breakers:
  hlp_executor:
    failure_threshold: 5
    recovery_timeout: "30s"
    half_open_max_calls: 3
```

---

### P1-11: 創建錯誤處理運維手冊
**目標檔案**: `docs/operations/runbooks/HLP_EXECUTOR_ERROR_HANDLING.md`  
**動作類型**: CREATE  
**理由**: 提供運維人員故障排查指引

**章節**:
1. 常見故障模式
   - Kubernetes API 不可用
   - 狀態持久化失敗
   - Quantum Backend 不可用
2. 診斷步驟
3. 恢復策略
4. 升級路徑

---

### P1-12: 創建檢查點管理模組
**目標檔案**: `core/safety_mechanisms/checkpoint_manager.py`  
**動作類型**: CREATE  
**理由**: 實現檢查點創建、壓縮、恢復功能

**接口**:
```python
class CheckpointManager:
    def create_checkpoint(self, execution_id: str, phase_id: str, state: dict) -> str
    def list_checkpoints(self, execution_id: str) -> List[Checkpoint]
    def restore_checkpoint(self, checkpoint_id: str) -> dict
    def cleanup_old_checkpoints(self, execution_id: str, keep_count: int = 5)
    def compress_checkpoint(self, checkpoint_id: str) -> int  # 返回壓縮後大小
```

---

### P1-13: 更新回滾配置
**目標檔案**: `config/safety-mechanisms.yaml`  
**動作類型**: UPDATE  
**理由**: 定義回滾觸發條件與動作映射

**新增區塊**:
```yaml
rollback_configuration:
  hlp_executor:
    partial_phase_rollback:
      enabled: true
      scope_levels: ["phase", "plan-unit", "artifact"]
      triggers:
        - condition: "validation-failure"
          scope: "phase"
          action: "rollback-current-phase"
        - condition: "resource-exhaustion"
          scope: "plan-unit"
          action: "reschedule-with-backoff"
        - condition: "security-violation"
          scope: "entire-execution"
          action: "emergency-stop-and-rollback"
```

---

### P1-14: 創建量子整合配置
**目標檔案**: `config/integrations/quantum-integration.yaml`  
**動作類型**: CREATE  
**理由**: 定義與量子後端的整合端點

**內容要點**:
```yaml
quantum_integration:
  enabled: false  # 預設禁用，等量子後端就緒
  scheduler_endpoint: "quantum-scheduler.unmanned-island-system.svc.cluster.local:8888"
  circuit_optimizer: "quantum-circuit-optimizer.unmanned-island-system.svc.cluster.local:8889"
  fallback_mode: "classical"  # 降級到經典模式
```

---

### P1-15: 創建知識圖譜整合配置
**目標檔案**: `config/integrations/knowledge-graph-integration.yaml`  
**動作類型**: CREATE  
**理由**: 定義與知識圖譜的整合端點

**內容要點**:
```yaml
knowledge_graph_integration:
  kg_builder_endpoint: "kg-graph-builder.unmanned-island-system.svc.cluster.local:8890"
  vector_search_endpoint: "kg-vector-hybrid.unmanned-island-system.svc.cluster.local:8891"
  enabled: true
```

---

### P1-16: 創建緊急程序手冊
**目標檔案**: `docs/operations/runbooks/HLP_EXECUTOR_EMERGENCY.md`  
**動作類型**: CREATE  
**理由**: 定義 P1/P2 緊急程序與升級路徑

**內容要點**:
1. **executor-core-down** (P1)
   - 症狀: 所有副本無法就緒
   - 診斷: 檢查 Pod 日誌、事件
   - 升級路徑: oncall → platform-lead → CTO

2. **state-corruption-detected** (P2)
   - 症狀: 狀態機卡住或狀態不一致
   - 恢復步驟: 啟用狀態備份恢復 → 驗證數據完整性

---

### P1-17: 創建維護程序手冊
**目標檔案**: `docs/operations/runbooks/HLP_EXECUTOR_MAINTENANCE.md`  
**動作類型**: CREATE  
**理由**: 定義常規維護程序

**內容要點**:
1. **Rolling Restart**
   - 頻率: 每週
   - 維護窗口: 02:00-04:00 UTC
   - 步驟: kubectl rollout restart deployment/hlp-executor-core

2. **State Cleanup**
   - 頻率: 每日
   - 保留期: 7 天
   - 腳本: `/tools/maintenance/cleanup-executor-state.sh`

---

### P1-18: 創建 SLO 指標文件
**目標檔案**: `docs/operations/slo/HLP_EXECUTOR_SLO.md`  
**動作類型**: CREATE  
**理由**: 定義服務水平目標（SLO）

**內容要點**:
| 指標 | 目標值 | 測量方法 |
|------|--------|---------|
| DAG 解析延遲 (P95) | < 120ms | Prometheus histogram |
| 狀態轉換延遲 (P90) | < 50ms | Prometheus histogram |
| 恢復時間目標 (RTO) | < 30s | 手動測試 |
| 可用性 | > 99.9% | Uptime monitoring |

---

### P1-19: 創建單元測試配置
**目標檔案**: `tests/unit/hlp-executor/jest.config.js`  
**動作類型**: CREATE  
**理由**: 配置單元測試環境

**內容要點**:
```javascript
module.exports = {
  displayName: 'hlp-executor-core',
  testMatch: ['**/*.test.ts'],
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  }
};
```

---

### P1-20: 創建部署檢查清單
**目標檔案**: `docs/operations/deployment/HLP_EXECUTOR_DEPLOYMENT_CHECKLIST.md`  
**動作類型**: CREATE  
**理由**: 提供部署前驗證清單

**檢查項目**:
- [ ] K8s 集群版本 >= 1.24
- [ ] Namespace `unmanned-island-system` 已創建
- [ ] Trust bundle ConfigMap 已部署
- [ ] RBAC 配置已應用
- [ ] Network Policies 已應用
- [ ] PVC 已創建並綁定
- [ ] Image 已簽名並驗證（Cosign）
- [ ] Prometheus ServiceMonitor 已配置
- [ ] HPA 已配置

---

### P1-21: 更新 CHANGELOG
**目標檔案**: `CHANGELOG.md`  
**動作類型**: UPDATE  
**理由**: 記錄 HLP Executor Core 的新增

**新增條目**:
```markdown
## [Unreleased]

### Added
- **HLP Executor Core Plugin** (v1.0.0): 新增 Async DAG 編排引擎
  - 支援 Phase-level 部分回滾
  - 整合 Quantum Backend（優雅降級）
  - SLSA L3 供應鏈安全
  - 指數退避 + Risk-Adaptive 重試策略
  - 斷路器錯誤處理
```

---

## P2 行動清單（長期優化）

### P2-1: 創建 Grafana 儀表板
**目標檔案**: `infrastructure/monitoring/grafana/dashboards/hlp-executor-dashboard.json`  
**動作類型**: CREATE  
**理由**: 提供可視化監控儀表板

**面板**:
1. 任務總數（按狀態分組）
2. 執行時長 (P50/P90/P95/P99)
3. 回滾操作數
4. 錯誤率
5. 資源使用率（CPU, Memory, GPU）

---

### P2-2: 更新量子安全密碼配置
**目標檔案**: `config/security-network-config.yml`  
**動作類型**: UPDATE  
**理由**: 整合量子安全加密算法

**新增區塊**:
```yaml
quantum_safe_cryptography:
  hlp_executor:
    enabled: true
    algorithms: ["ML-KEM-768", "ML-DSA-65"]
    transition_plan: "hybrid-classical-pq"
```

---

### P2-3: 創建 OpenTelemetry 配置
**目標檔案**: `infrastructure/monitoring/otel/hlp-executor-otel-config.yaml`  
**動作類型**: CREATE  
**理由**: 配置分散式追蹤

**內容要點**:
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024
  
exporters:
  jaeger:
    endpoint: "jaeger-collector.unmanned-island-system.svc.cluster.local:14250"
  
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger]
```

---

### P2-4: 創建可觀測性整合配置
**目標檔案**: `config/integrations/observability-integration.yaml`  
**動作類型**: CREATE  
**理由**: 統一可觀測性端點配置

**內容要點**:
```yaml
observability_integration:
  prometheus_endpoint: "prometheus.unmanned-island-system.svc.cluster.local:9090"
  grafana_endpoint: "grafana.unmanned-island-system.svc.cluster.local:3000"
  trace_collector: "otel-collector.unmanned-island-system.svc.cluster.local:14268"
```

---

### P2-5: 創建 Canary 部署配置
**目標檔案**: `infrastructure/canary/hlp-executor-canary.yaml`  
**動作類型**: CREATE  
**理由**: 支援 Canary 部署策略

**內容要點**:
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: hlp-executor-core
  namespace: unmanned-island-system
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hlp-executor-core
  service:
    port: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 200
      interval: 1m
```

---

### P2-6: 創建 Blue-Green 策略文件
**目標檔案**: `docs/operations/deployment/BLUE_GREEN_STRATEGY.md`  
**動作類型**: CREATE  
**理由**: 記錄 Blue-Green 部署流程

**章節**:
1. 概述（5 分鐘驗證期 + 手動晉級）
2. 部署流程
3. 驗證標準
4. 回滾程序
5. 自動化腳本

---

### P2-7: 創建整合測試環境配置
**目標檔案**: `tests/integration/hlp-executor/test-setup.yaml`  
**動作類型**: CREATE  
**理由**: 配置整合測試環境（Kind + Quantum Simulation）

**內容要點**:
```yaml
kind_cluster:
  name: "hlp-executor-test"
  nodes: 3
  config: |
    kind: Cluster
    apiVersion: kind.x-k8s.io/v1alpha4
    nodes:
    - role: control-plane
    - role: worker
    - role: worker

quantum_simulation:
  enabled: true
  backend: "mock-quantum-scheduler"
```

---

### P2-8: 創建混沌工程場景
**目標檔案**: `tests/chaos/hlp-executor-chaos-scenarios.yaml`  
**動作類型**: CREATE  
**理由**: 定義混沌工程測試場景

**場景**:
1. **pod-kill**: 隨機終止 Pod
2. **network-latency**: 注入網絡延遲（200ms）
3. **resource-exhaustion**: 模擬 CPU/Memory 耗盡

---

### P2-9: 創建性能測試腳本
**目標檔案**: `tests/performance/hlp-executor-k6-script.js`  
**動作類型**: CREATE  
**理由**: k6 性能測試腳本（1000 RPS, 10 分鐘）

**內容要點**:
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 500 },  // Ramp-up
    { duration: '6m', target: 1000 }, // Steady state
    { duration: '2m', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests < 200ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};

export default function () {
  const res = http.post('http://hlp-executor-core:8080/execute', JSON.stringify({
    plan_units: [/* ... */]
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
}
```

---

### P2-10: 創建 DAG 執行器自動化腳本
**目標檔案**: `automation/intelligent/dag_executor.py`  
**動作類型**: CREATE  
**理由**: 實現 DAG 執行邏輯（拓撲排序 + 關鍵路徑分析）

**功能要點**:
```python
class DAGExecutor:
    def parse_dag(self, plan_units: List[PlanUnit]) -> ExecutionGraph
    def topological_sort(self, graph: ExecutionGraph) -> List[Phase]
    def critical_path_analysis(self, graph: ExecutionGraph) -> CriticalPath
    def schedule_with_max_width(self, phases: List[Phase]) -> SchedulePlan
```

---

### P2-11: 創建狀態機驗證工具
**目標檔案**: `tools/governance/state-machine-validator.py`  
**動作類型**: CREATE  
**理由**: 驗證狀態轉換合法性

**功能要點**:
```python
def validate_state_machine(state_machine: dict) -> ValidationResult:
    """
    驗證狀態機定義
    
    檢查項目:
    - 初始狀態存在
    - 所有轉換目標狀態存在
    - 無孤立狀態
    - 至少一個 final_state
    - Timeout 設定合理
    """
```

---

### P2-12: 創建回滾分析器
**目標檔案**: `automation/intelligent/rollback_analyzer.py`  
**動作類型**: CREATE  
**理由**: 分析回滾觸發條件與歷史趨勢

**功能要點**:
```python
class RollbackAnalyzer:
    def analyze_rollback_history(self, time_range: TimeRange) -> RollbackReport
    def identify_common_triggers(self) -> List[TriggerPattern]
    def recommend_policy_adjustments(self) -> List[PolicyRecommendation]
```

---

### P2-13: 創建插件模板
**目標檔案**: `templates/plugins/quantum-yaml-plugin-template.yaml`  
**動作類型**: CREATE  
**理由**: 可重用的 Quantum-YAML 插件規格模板

**模板結構**:
```yaml
%YAML 1.2
---
document_metadata:
  unique_id: "{{PLUGIN_ID}}-v{{VERSION}}"
  actual_filename: "{{PLUGIN_ID}}.plugin.yaml"
  version: "{{VERSION}}"
  format_type: "quantum-yaml"

plugin_specification:
  id: "{{PLUGIN_ID}}"
  name: "{{PLUGIN_NAME}}"
  version: "{{VERSION}}"
  kind: ["{{PLUGIN_KIND}}"]
  
  provides:
    - "{{CAPABILITY_1}}"
  
  requires:
    - "{{DEPENDENCY_1}}"
```

---

## 整合順序建議

### 第一階段（P0，1-2 天）
1. 創建治理註冊 (P0-1)
2. 更新系統模組映射 (P0-2)
3. 創建 K8s 基礎清單 (P0-3, P0-4, P0-5, P0-6)
4. 建立 SLSA 目錄 (P0-7)
5. 更新依賴配置 (P0-8)
6. 創建核心架構文件 (P0-9)
7. 實現部分回滾模組 (P0-10)

### 第二階段（P1，3-7 天）
1. 創建治理 Schema (P1-1)
2. 創建架構文件 (P1-3, P1-4)
3. 創建監控配置 (P1-7, P1-8)
4. 實現安全機制模組 (P1-9, P1-10, P1-12, P1-13)
5. 創建整合配置 (P1-14, P1-15)
6. 創建運維手冊 (P1-11, P1-16, P1-17, P1-18)
7. 創建測試配置 (P1-19)
8. 創建部署檢查清單 (P1-20)
9. 更新 CHANGELOG (P1-21)

### 第三階段（P2，2-4 週）
1. 創建監控儀表板 (P2-1)
2. 創建進階配置 (P2-2, P2-3, P2-4, P2-5, P2-6)
3. 創建測試場景 (P2-7, P2-8, P2-9)
4. 實現自動化腳本 (P2-10, P2-11, P2-12)
5. 創建插件模板 (P2-13)

---

## 驗證檢查點

### 階段一完成驗證
```bash
# 驗證 K8s 清單
kubectl apply --dry-run=client -f infrastructure/kubernetes/

# 驗證配置檔案
python tools/docs/validate_index.py --verbose

# 驗證 SLSA 目錄結構
ls -la core/slsa_provenance/plugins/hlp-executor-core/
```

### 階段二完成驗證
```bash
# 驗證 Schema
jsonschema -i governance/schemas/state-machine.schema.json

# 驗證政策
conftest test governance/policies/security/

# 運行單元測試
npm test -w tests/unit/hlp-executor
```

### 階段三完成驗證
```bash
# 運行整合測試
npm test -w tests/integration/hlp-executor

# 運行性能測試
k6 run tests/performance/hlp-executor-k6-script.js

# 運行混沌工程測試
chaos-mesh apply -f tests/chaos/hlp-executor-chaos-scenarios.yaml
```

---

## 下一步：legacy_scratch 清理計畫（參考單獨文件）
