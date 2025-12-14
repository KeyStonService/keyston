# Refactor Playbook: core/

**Generated:** 2025-12-12T01:18:24.727830  
**Cluster Score:** 75  
**Status:** Draft (LLM generation required for complete playbook)

---

## 1. Cluster 概覽

**Cluster Path:** `core/`  
**Current Status:** 需要重構與語言治理改進

這個 cluster 在 Unmanned Island System 中的角色：
- 路徑位置：core/
- 違規數量：0
- Hotspot 檔案：2
- 安全問題：0

---

## 2. 問題盤點

### 語言治理違規 (0)

✅ 無語言治理違規

### Hotspot 檔案 (2)

- **core/legacy_module/old_api.php** (score: 95)
- **core/mind_matrix/brain.js** (score: 75)

### Semgrep 安全問題 (0)

✅ 無安全問題


---

## 3. 語言與結構重構策略

**注意：** 此部分需要使用 LLM 生成完整建議。

預期內容：
- 語言層級策略（保留/遷出語言）
- 目錄結構優化建議
- 語言遷移路徑

---

## 4. 分級重構計畫（P0 / P1 / P2）

**注意：** 此部分需要使用 LLM 生成具體行動計畫。

### P0（24–48 小時內必須處理）
- 待 LLM 生成

### P1（一週內）
- 待 LLM 生成

### P2（持續重構）
- 待 LLM 生成

---

## 5. 適合交給 Auto-Fix Bot 的項目

**可自動修復：**
- 待 LLM 分析

**需人工審查：**
- 待 LLM 分析

---

## 6. 驗收條件與成功指標

**語言治理目標：**
- 違規數 < 5
- 安全問題 HIGH severity = 0
- Cluster score < 20

**改善方向：**
- 待 LLM 生成具體建議

---

## 7. 檔案與目錄結構（交付視圖）

### 受影響目錄

- core/

### 結構示意（變更範圍）

```
core/
├── _scratch/
│   ├── .gitkeep
│   └── README.md
├── advisory-database/
│   ├── src/
│   │   ├── __tests__/
│   │   ├── services/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── validators/
│   │   └── index.ts
│   ├── .eslintrc.json
│   ├── README.md
│   ├── jest.config.cjs
│   ├── jest.config.js
│   ├── package.json
│   └── tsconfig.json
├── ai_constitution/
│   ├── __init__.py
│   ├── adaptive_guidelines.py
│   ├── constitution_engine.py
│   ├── fundamental_laws.py
│   ├── guardrails.py
│   ├── operational_rules.py
│   └── policy_as_prompt.py
├── ci_error_handler/
│   ├── __init__.py
│   ├── auto_fix_engine.py
│   ├── ci_error_analyzer.py
│   ├── fix_status_tracker.py
│   └── issue_manager.py
├── cloud_agent_delegation/
│   ├── __init__.py
│   ├── cloud_provider_adapter.py
│   ├── delegation_manager.py
│   ├── load_balancer.py
│   └── task_router.py
├── contract_service/
│   ├── contracts-L1/
│   │   ├── ai-chat-service/
│   │   └── contracts/
│   ├── external/
│   │   ├── README.md
│   │   └── external-api.json
│   └── README.md
├── execution_architecture/
│   ├── README.md
│   ├── __init__.py
│   ├── agent_orchestration.py
│   ├── function_calling.py
│   ├── langchain_integration.py
│   ├── mcp_integration.py
│   └── tool_system.py
├── execution_engine/
│   ├── README.md
│   ├── __init__.py
│   ├── action_executor.py
│   ├── capability_registry.py
│   ├── connector_manager.py
│   ├── execution_engine.py
│   ├── rollback_manager.py
│   └── verification_engine.py
├── hlp_executor/
│   ├── README.md
│   ├── __init__.py
│   ├── dag_engine.py
│   ├── partial_rollback.py
│   └── state_machine.py
├── island_ai_runtime/
│   ├── __init__.py
│   ├── agent_framework.py
│   ├── knowledge_engine.py
│   ├── model_gateway.py
│   ├── runtime.py
│   ├── safety_constitution.py
│   ├── session_memory.py
│   └── tool_executor.py
├── main_system/
│   ├── __init__.py
│   ├── automation_pipeline.py
│   ├── phase_orchestrator.py
│   ├── synergymesh_core.py
│   └── system_bootstrap.py
├── mcp_servers_enhanced/
│   ├── __init__.py
│   ├── mcp_server_manager.py
│   ├── realtime_connector.py
│   ├── tool_registry.py
│   └── workflow_orchestrator.py
├── modules/
│   ├── ai_constitution/
│   │   ├── __init__.py
│   │   ├── adaptive_guidelines.py
│   │   ├── constitution_engine.py
│   │   ├── fundamental_laws.py
│   │   ├── guardrails.py
│   │   ├── operational_rules.py
│   │   └── policy_as_prompt.py
│   ├── ci_error_handler/
│   │   ├── __init__.py
│   │   ├── auto_fix_engine.py
│   │   ├── ci_error_analyzer.py
│   │   ├── fix_status_tracker.py
│   │   └── issue_manager.py
│   ├── cloud_agent_delegation/
│   │   ├── __init__.py
│   │   ├── cloud_provider_adapter.py
│   │   ├── delegation_manager.py
│   │   ├── load_balancer.py
│   │   └── task_router.py
│   ├── drone_system/
│   │   ├── __init__.py
│   │   ├── autopilot.py
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── coordinator.py
│   │   ├── deployment.py
│   │   ├── py.typed
│   │   └── utils.py
│   ├── execution_architecture/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── agent_orchestration.py
│   │   ├── function_calling.py
│   │   ├── langchain_integration.py
│   │   ├── mcp_integration.py
│   │   └── tool_system.py
│   ├── execution_engine/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── action_executor.py
│   │   ├── capability_registry.py
│   │   ├── connector_manager.py
│   │   ├── execution_engine.py
│   │   ├── rollback_manager.py
│   │   └── verification_engine.py
│   ├── main_system/
│   │   ├── __init__.py
│   │   ├── automation_pipeline.py
│   │   ├── phase_orchestrator.py
│   │   ├── synergymesh_core.py
│   │   └── system_bootstrap.py
│   ├── mcp_servers_enhanced/
│   │   ├── __init__.py
│   │   ├── mcp_server_manager.py
│   │   ├── realtime_connector.py
│   │   ├── tool_registry.py
│   │   └── workflow_orchestrator.py
│   ├── mind_matrix/
│   │   ├── RUNTIME_README.md
│   │   ├── __init__.py
│   │   ├── executive_auto.py
│   │   └── main.py
│   ├── monitoring_system/
│   │   ├── __init__.py
│   │   ├── auto_diagnosis.py
│   │   ├── auto_remediation.py
│   │   ├── intelligent_monitoring.py
│   │   ├── observability_platform.py
│   │   ├── self_learning.py
│   │   └── smart_anomaly_detector.py
│   ├── tech_stack/
│   │   ├── __init__.py
│   │   ├── architecture_config.py
│   │   ├── framework_integrations.py
│   │   ├── multi_agent_coordinator.py
│   │   └── python_bridge.py
│   ├── training_system/
│   │   ├── __init__.py
│   │   ├── example_library.py
│   │   ├── knowledge_base.py
│   │   └── skills_training.py
│   ├── virtual_experts/
│   │   ├── __init__.py
│   │   ├── domain_experts.py
│   │   ├── expert_base.py
│   │   └── expert_team.py
│   ├── yaml_module_system/
│   │   ├── __init__.py
│   │   ├── audit_trail.py
│   │   ├── ci_verification_pipeline.py
│   │   ├── policy_gate.py
│   │   ├── slsa_compliance.py
│   │   ├── yaml_module_definition.py
│   │   └── yaml_schema_validator.py
│   └── __init__.py
├── monitoring_system/
│   ├── __init__.py
│   ├── auto_diagnosis.py
│   ├── auto_remediation.py
│   ├── intelligent_monitoring.py
│   ├── observability_platform.py
│   ├── self_learning.py
│   └── smart_anomaly_detector.py
├── safety_mechanisms/
│   ├── __init__.py
│   ├── anomaly_detector.py
│   ├── checkpoint_manager.py
│   ├── circuit_breaker.py
│   ├── emergency_stop.py
│   ├── escalation_ladder.py
│   ├── partial_rollback.py
│   ├── retry_policies.py
│   ├── rollback_system.py
│   └── safety_net.py
├── slsa_provenance/
│   ├── plugins/
│   │   └── hlp-executor-core/
│   ├── __init__.py
│   ├── artifact_verifier.py
│   ├── attestation_manager.py
│   ├── provenance_generator.py
│   └── signature_verifier.py
├── tech_stack/
│   ├── __init__.py
│   ├── architecture_config.py
│   ├── framework_integrations.py
│   ├── multi_agent_coordinator.py
│   └── python_bridge.py
├── training_system/
│   ├── __init__.py
│   ├── example_library.py
│   ├── knowledge_base.py
│   └── skills_training.py
├── unified_integration/
│   ├── __init__.py
│   ├── cli_bridge.py
│   ├── cognitive_processor.py
│   ├── configuration_manager.py
│   ├── configuration_optimizer.py
│   ├── deep_execution_system.py
│   ├── integration_hub.py
│   ├── service_registry.py
│   ├── system_orchestrator.py
│   ├── unified_controller.py
│   └── work_configuration_manager.py
├── validators/
│   ├── __init__.py
│   ├── multi_layer_validator.py
│   ├── security_validator.py
│   ├── semantic_validator.py
│   └── syntax_validator.py
└── ... (12 more items)
```

### 檔案說明

- `core/README.md` — 說明文檔
- `core/__init__.py` — Python 套件初始化
- `core/main_system/__init__.py` — Python 套件初始化
- `core/slsa_provenance/__init__.py` — Python 套件初始化
- `core/slsa_provenance/plugins/hlp-executor-core/README.md` — 說明文檔
- `core/training_system/__init__.py` — Python 套件初始化
- `core/mcp_servers_enhanced/__init__.py` — Python 套件初始化
- `core/tech_stack/__init__.py` — Python 套件初始化
- `core/validators/__init__.py` — Python 套件初始化
- `core/yaml_module_system/__init__.py` — Python 套件初始化

---

## 如何使用本 Playbook

1. **立即執行 P0 項目**：處理高優先級問題
2. **規劃 P1 重構**：安排一週內執行
3. **持續改進**：納入 P2 到長期技術債計畫
4. **交給 Auto-Fix Bot**：自動化可修復項目
5. **人工審查**：關鍵架構調整需要工程師參與

