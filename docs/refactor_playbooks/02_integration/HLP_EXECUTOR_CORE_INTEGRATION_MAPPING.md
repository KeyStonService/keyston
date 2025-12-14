# HLP Executor Core Plugin - 邏輯→目標位置對應表

## 對應原則

- ✅ 優先整合到既有目錄
- ✅ 遵循現有專案結構（core/, services/, automation/, governance/, config/, docs/, infrastructure/）
- ✅ 不隨意創建新頂層目錄
- ✅ 每個邏輯元件給出具體檔案路徑

---

## 一、邏輯 → 目標位置對應表

| # | 邏輯名稱 | 說明 | 建議目標路徑 | 檔案角色 | 優先級 |
|---|---------|------|------------|---------|--------|
| **1. 核心概念與治理** | | | | | |
| 1.1 | Plugin Metadata & Governance | 插件 ID、類型、安全級別、合規標籤 | `governance/registry/plugins/hlp-executor-core.yaml` | 插件註冊清單 | P0 |
| 1.2 | Registry Binding | 插件註冊表命名空間與運行時類別 | `config/system-module-map.yaml` | 模組映射條目（新增 HLP 執行器） | P0 |
| 1.3 | Vector Alignment Map | 語義向量嵌入配置 | `config/unified-config-index.yaml` | 向量配置區塊 | P1 |
| **2. 架構與執行模型** | | | | | |
| 2.1 | Execution Model (Async DAG) | DAG 編排器架構設計 | `docs/architecture/EXECUTION_MODEL.md` | 執行模型架構文件 | P0 |
| 2.2 | State Machine Definition | 狀態機定義與轉換規則 | `governance/schemas/state-machine.schema.json` | 狀態機 JSON Schema | P1 |
| 2.3 | Checkpoint Strategy | Phase-level 檢查點策略 | `docs/architecture/CHECKPOINT_STRATEGY.md` | 檢查點策略文件 | P1 |
| 2.4 | Recovery Mode Logic | 部分回滾恢復邏輯 | `docs/architecture/RECOVERY_MODE.md` | 恢復模式文件 | P1 |
| **3. Kubernetes 部署規格** | | | | | |
| 3.1 | Deployment Manifest | K8s Deployment YAML | `infrastructure/kubernetes/deployments/hlp-executor-core.yaml` | K8s 部署清單 | P0 |
| 3.2 | Service Account & RBAC | ServiceAccount + Role/RoleBinding | `infrastructure/kubernetes/rbac/hlp-executor-rbac.yaml` | RBAC 配置 | P0 |
| 3.3 | PVC & ConfigMap | 持久化存儲與配置 | `infrastructure/kubernetes/storage/hlp-executor-storage.yaml` | 存儲配置 | P0 |
| 3.4 | HPA Configuration | 水平自動擴展 | `infrastructure/kubernetes/autoscaling/hlp-executor-hpa.yaml` | HPA 配置 | P1 |
| **4. 安全配置** | | | | | |
| 4.1 | Network Policies | 入口/出口網絡策略 | `infrastructure/kubernetes/network-policies/hlp-executor-netpol.yaml` | 網絡策略 | P0 |
| 4.2 | Supply Chain Security | Cosign, SBOM, Provenance | `core/slsa_provenance/plugins/hlp-executor-core/` | SLSA 證據目錄 | P0 |
| 4.3 | Security Policy | 安全政策 (GDPR, SOC2, Quantum-Safe) | `governance/policies/security/hlp-executor-security-policy.yaml` | 安全政策文件 | P1 |
| 4.4 | Quantum-Safe Crypto Config | ML-KEM-768, ML-DSA-65 配置 | `config/security-network-config.yml` | 量子安全密碼配置 | P2 |
| **5. 可觀測性配置** | | | | | |
| 5.1 | Prometheus Metrics | 指標定義與 ServiceMonitor | `infrastructure/monitoring/prometheus/servicemonitors/hlp-executor-metrics.yaml` | Prometheus 監控配置 | P1 |
| 5.2 | Grafana Dashboard | 可視化儀表板 JSON | `infrastructure/monitoring/grafana/dashboards/hlp-executor-dashboard.json` | Grafana 儀表板 | P2 |
| 5.3 | Logging Configuration | 結構化日誌配置 | `config/monitoring.yaml` | 日誌配置區塊（新增 HLP） | P1 |
| 5.4 | OpenTelemetry Config | 分散式追蹤配置 | `infrastructure/monitoring/otel/hlp-executor-otel-config.yaml` | OTel 配置 | P2 |
| **6. 重試與錯誤處理** | | | | | |
| 6.1 | Retry Policy Logic | 指數退避 + Jitter + Risk-Adaptive | `core/safety_mechanisms/retry_policies.py` | 重試策略模組（新增 HLP 策略） | P1 |
| 6.2 | Circuit Breaker Config | 斷路器參數 | `config/safety-mechanisms.yaml` | 安全機制配置（新增斷路器） | P1 |
| 6.3 | Error Handling Runbook | 故障模式與恢復步驟 | `docs/operations/runbooks/HLP_EXECUTOR_ERROR_HANDLING.md` | 運維手冊 | P1 |
| **7. 部分回滾機制** | | | | | |
| 7.1 | Partial Rollback Logic | Phase/Plan-unit/Artifact 粒度回滾 | `core/safety_mechanisms/partial_rollback.py` | 部分回滾模組 | P0 |
| 7.2 | Checkpoint Management | Copy-on-Write, 保留最近 5 個檢查點 | `core/safety_mechanisms/checkpoint_manager.py` | 檢查點管理模組 | P1 |
| 7.3 | Rollback Configuration | 觸發條件與動作映射 | `config/safety-mechanisms.yaml` | 回滾配置區塊 | P1 |
| **8. 整合點配置** | | | | | |
| 8.1 | Quantum Integration Endpoints | Scheduler + Circuit Optimizer | `config/integrations/quantum-integration.yaml` | 量子後端整合配置 | P1 |
| 8.2 | Knowledge Graph Endpoints | KG Builder + Vector Search | `config/integrations/knowledge-graph-integration.yaml` | 知識圖譜整合配置 | P1 |
| 8.3 | Observability Endpoints | Prometheus, Grafana, Jaeger | `config/integrations/observability-integration.yaml` | 可觀測性整合配置 | P2 |
| **9. 部署生命週期策略** | | | | | |
| 9.1 | Canary Deployment Config | 10% 流量分割 + 成功標準 | `infrastructure/canary/hlp-executor-canary.yaml` | Canary 部署配置 | P2 |
| 9.2 | Blue-Green Deployment | 驗證期 5 分鐘 + 手動晉級 | `docs/operations/deployment/BLUE_GREEN_STRATEGY.md` | Blue-Green 策略文件 | P2 |
| 9.3 | Rolling Update Policy | MaxUnavailable 25%, MaxSurge 25% | `infrastructure/kubernetes/deployments/hlp-executor-core.yaml` | （整合到 Deployment） | P1 |
| **10. 測試配置** | | | | | |
| 10.1 | Unit Test Config | Jest + 90% Coverage | `tests/unit/hlp-executor/jest.config.js` | Jest 配置 | P1 |
| 10.2 | Integration Test Setup | Kind + Quantum Simulation | `tests/integration/hlp-executor/test-setup.yaml` | 整合測試環境配置 | P2 |
| 10.3 | Chaos Engineering Scenarios | Pod-kill, Network-latency, Resource-exhaustion | `tests/chaos/hlp-executor-chaos-scenarios.yaml` | 混沌工程場景 | P2 |
| 10.4 | Performance Test Config | k6 + 1000 RPS + 10min | `tests/performance/hlp-executor-k6-script.js` | k6 性能測試腳本 | P2 |
| **11. 運維手冊** | | | | | |
| 11.1 | Emergency Procedures | P1/P2 緊急程序 + 升級路徑 | `docs/operations/runbooks/HLP_EXECUTOR_EMERGENCY.md` | 緊急程序手冊 | P1 |
| 11.2 | Maintenance Procedures | Rolling-restart, State-cleanup | `docs/operations/runbooks/HLP_EXECUTOR_MAINTENANCE.md` | 維護程序手冊 | P1 |
| 11.3 | SLO Metrics & Monitoring | DAG 解析延遲, RTO, 可用性 | `docs/operations/slo/HLP_EXECUTOR_SLO.md` | SLO 指標文件 | P1 |
| **12. 依賴管理** | | | | | |
| 12.1 | Hard Dependencies | axiom-kernel-compute, axiom-bootstrap-core | `config/dependencies.yaml` | 依賴配置（新增 HLP 依賴） | P0 |
| 12.2 | Soft Dependencies | quantum-scheduler (優雅降級) | `config/dependencies.yaml` | 軟依賴配置 | P1 |
| **13. AI/自動化腳本** | | | | | |
| 13.1 | DAG Execution Graph Builder | 拓撲排序 + 關鍵路徑分析 | `automation/intelligent/dag_executor.py` | DAG 執行器自動化腳本 | P2 |
| 13.2 | State Machine Validator | 驗證狀態轉換合法性 | `tools/governance/state-machine-validator.py` | 狀態機驗證工具 | P2 |
| 13.3 | Rollback Trigger Analyzer | 分析回滾觸發條件 | `automation/intelligent/rollback_analyzer.py` | 回滾分析器 | P2 |
| **14. 文件與模板** | | | | | |
| 14.1 | Plugin Template (Quantum-YAML) | 可重用的插件規格模板 | `templates/plugins/quantum-yaml-plugin-template.yaml` | 插件模板 | P2 |
| 14.2 | Deployment Checklist | 部署前驗證清單 | `docs/operations/deployment/HLP_EXECUTOR_DEPLOYMENT_CHECKLIST.md` | 部署檢查清單 | P1 |
| 14.3 | Version History Tracking | 版本歷史與變更日誌 | `CHANGELOG.md` | （新增 HLP Executor Core 條目） | P1 |

---

## 二、與現有結構的關係

### 2.1 引用關係（References）

#### HLP Executor Core → 現有系統
- `config/system-manifest.yaml`: 新增 HLP Executor 作為 enhanced_integration 元件
- `config/unified-config-index.yaml`: 引用 HLP 的向量配置與整合端點
- `governance/registry/`: 註冊 HLP Executor 插件
- `core/slsa_provenance/`: 引用 HLP 的 SLSA L3 證據

#### 現有系統 → HLP Executor Core
- `core/unified_integration/service_registry.py`: 發現並管理 HLP Executor 服務
- `automation/intelligent/`: 調用 HLP 的 DAG 執行能力
- `infrastructure/kubernetes/`: 部署 HLP Executor 到 K8s 集群

### 2.2 替代關係（Replaces）
- **無直接替代**: HLP Executor Core 是新增功能，不替代現有模組
- **增強關係**: 增強 `automation/` 下的執行能力，提供更強大的編排機制

### 2.3 被引用關係（Referenced By）
- `docs/DOCUMENTATION_INDEX.md`: 新增 HLP Executor 架構與運維文件的索引條目
- `docs/refactor_playbooks/03_refactor/meta/AI_PROMPTS.md`: 新增 HLP Executor 相關 AI 提示
- `.github/workflows/`: 新增 HLP Executor 的 CI/CD 工作流

---

## 三、整合衝突與解決方案

### 3.1 命名空間與依賴適配

#### Namespace 適配（已完成）
- ✅ **原始**: `axiom-system` 
- ✅ **適配**: `unmanned-island-system`
- ✅ **理由**: 與 Unmanned Island 系統命名約定一致

#### 依賴項目適配策略

| 原始依賴 | 適配策略 | 優先級 |
|---------|---------|--------|
| `axiom-quantum-runtime` | 映射到 `quantum-scheduler` (Soft Dependency, 優雅降級) | P1 |
| `axiom-trust-bundle` | 映射到 Unmanned Island 的 trust bundle (ConfigMap) | P0 |
| `axiom-kernel-compute` | 映射到 `core/` 下的計算模組 | P1 |
| `axiom-bootstrap-core` | 整合到 `core/unified_integration/` | P1 |
| `axiom-trace-collector` | 使用標準 OpenTelemetry Collector | P1 |
| `axiom.io` API Group | 改用 `unmanned-island.io` 或 `synergymesh.io` | P0 |

#### Priority Class 適配
- **原始**: `axiom-critical`
- **適配**: `system-cluster-critical` (K8s 標準) 或自定義 `unmanned-island-critical`

#### Image Registry 適配
- **原始**: `registry.local/axiom/`
- **適配**: 使用專案實際 registry（例如 `ghcr.io/synergymesh-admin/`）

#### 路徑與端點適配
- **Trust Bundle**: `/etc/axiom/trust` → `/etc/unmanned-island/trust`
- **Config**: `/etc/axiom/config` → `/etc/unmanned-island/config`
- **State Storage**: `/var/lib/axiom/state` → `/var/lib/unmanned-island/state`

### 3.2 潛在衝突與解決方案

1. **Quantum Backend Dependency**: 目前可能無 quantum-scheduler 實現
   - **解決方案**: 利用 Soft Dependency 的優雅降級特性，先以經典模式運行
   - **配置**: `quantum_integration.enabled: false` + `fallback_mode: "classical"`

2. **GPU Resource**: 要求 GPU 資源，可能不是所有環境都支援
   - **解決方案**: 將 GPU 改為 Optional，或提供 CPU-only 部署變體
   - **配置**: 在 K8s Deployment 中將 GPU limits 設為註解狀態

3. **Custom API Group**: `axiom.io` API group 可能不存在
   - **解決方案**: 創建 `unmanned-island.io` API group 或使用標準 K8s resources
   - **替代方案**: 使用 ConfigMap + Annotations 代替 CRD（Phase 1）

### 3.3 版本對齊
- **Kubernetes**: 確保目標集群 >= 1.24（支援 CustomResources, HPA v2）
- **Prometheus**: 確保 >= 2.30（支援 ServiceMonitor CRD）
- **Sigstore/Cosign**: 確保 >= 2.0（供應鏈安全）

---

## 四、整合檢查清單

- [ ] 所有 P0 檔案已創建或更新
- [ ] 所有 P1 檔案已創建或更新
- [ ] P2 檔案視情況創建
- [ ] `config/system-manifest.yaml` 已更新（新增 HLP Executor）
- [ ] `governance/registry/plugins/` 已註冊 HLP Executor
- [ ] `infrastructure/kubernetes/` 下已創建所有 K8s 清單
- [ ] `core/slsa_provenance/plugins/hlp-executor-core/` 已建立證據目錄
- [ ] `docs/DOCUMENTATION_INDEX.md` 已更新索引
- [ ] `CHANGELOG.md` 已新增 HLP Executor 條目
- [ ] 所有整合點配置檔案已創建（quantum, KG, observability）
- [ ] 驗證腳本已添加到 `tools/governance/`
- [ ] 運維手冊已添加到 `docs/operations/runbooks/`
- [ ] 測試配置已添加到 `tests/{unit,integration,chaos,performance}/`

---

## 五、整合完成標準

### 必要條件（Must-Have）
1. ✅ 所有 P0 檔案已創建且通過驗證
2. ✅ K8s 清單可成功 `kubectl apply --dry-run`
3. ✅ 所有配置檔案通過 YAML schema 驗證
4. ✅ `governance/policies/` 下的政策通過 Conftest/OPA 檢查
5. ✅ 文件索引更新完成

### 推薦條件（Should-Have）
1. ✅ 所有 P1 檔案已創建
2. ✅ 運維手冊已撰寫完成
3. ✅ 測試配置已準備就緒
4. ✅ CI/CD 工作流已配置

### 優化條件（Nice-to-Have）
1. ✅ 所有 P2 檔案已創建
2. ✅ Grafana 儀表板已設計
3. ✅ 混沌工程場景已配置
4. ✅ 性能測試腳本已準備

---

## 下一步：執行整合（參考 P0/P1/P2 行動清單）
