# 🏗️ 系統架構說明 (System Architecture)

> **版本**: 1.0.0  
> **最後更新**: 2025-12-21 02:13:25
> **狀態**: 🟢 Active  
> **自動更新**: 啟用

---

<!-- AUTO-ARCHITECTURE-SYNC:START -->
### 🗺️ 自動架構同步（2025-12-25T02:45:58Z）

- Commit: c82116af489eb36593d93694b1a6e13b4a862ce6 (chore: implement acceptance automation)
- 檔案結構快照：

```
controlplane/
├── CONTROLPLANE_USAGE.md
├── baseline/
│   ├── config/
│   ├── documentation/
│   ├── integration/
│   ├── registries/
│   ├── specifications/
│   └── validation/
├── governance/
│   ├── docs/
│   ├── policies/
│   └── reports/
└── overlay/
    └── evidence/

workspace/
├── archive/
│   ├── Screenshot_20251223_184259.jpg
│   ├── cleanup-root-directory.sh
│   ├── cleanup-root-to-minimal-skeleton.sh
│   ├── cleanup-workspace-root.sh
│   ├── conversations/
│   ├── fhs-simulation/
│   ├── fix_indentation.py
│   ├── fix_main_function.py
│   ├── legacy/
│   ├── setup-fhs-directories.sh
│   └── summarized_conversations/
├── artifacts/
│   ├── governance-execution-report.json
│   ├── root.bootstrap.yaml.backup
│   ├── root.config.yaml.backup
│   ├── root.governance.yaml.backup2
│   ├── root.integrity.yaml.backup
│   ├── root.provenance.yaml.backup
│   ├── root.super-execution.yaml.backup
│   ├── root.trust.yaml.backup
│   ├── test-results.json
│   └── validation_report.json
├── attached_assets/
│   ├── Screenshot_20251223_143236_1766472174748.jpg
│   └── Screenshot_20251223_143236_1766472194994.jpg
├── chatops/
├── chatops-assistant/
│   └── package.json
├── client/
│   ├── index.html
│   └── src/
├── config/
│   ├── DIRECTORY.md
│   ├── Dockerfile
│   ├── MANIFEST.in
│   ├── Makefile
│   ├── README.md
│   ├── agents/
│   ├── autofix/
│   ├── automation/
│   ├── axioms/
│   ├── brand-mapping.yaml
│   ├── build-tools/
│   ├── builder-system-prompt.yaml
│   ├── ci-cd/
│   ├── cloud-agent-delegation.yml
│   ├── conftest/
│   ├── dependencies.yaml
│   ├── deployment/
│   ├── dev/
│   ├── docker/
│   ├── docker-compose.prod.yml
│   ├── drizzle.config.ts
│   ├── elasticsearch-config.sh
│   ├── environments/
│   ├── etc/
│   ├── external_repos.yaml.example
│   ├── go.work
│   ├── governance/
│   ├── integrations/
│   ├── integrations-index.yaml
│   ├── island-control.yml
│   ├── machinenativeops.yaml
│   ├── mno-namespace.yaml
│   ├── monitoring/
│   ├── package-lock.json
│   ├── package.json
│   ├── pipelines/
│   ├── pom.xml
│   ├── postcss.config.js
│   ├── prod/
│   ├── pyproject.toml
│   ├── requirements-debug.txt
│   ├── requirements-prod.txt
│   ├── requirements-workflow.txt
│   ├── root.bootstrap.minimal.yaml
│   ├── root.validator.schema.yaml
│   ├── security/
│   ├── tailwind.config.js
│   ├── templates/
│   ├── tsconfig.json
│   ├── unified-config-index.yaml
│   ├── uv.lock
│   ├── vite.config.ts
│   ├── wrangler.toml
│   └── yaml-module-system.yaml
├── db/
│   └── index.ts
├── deploy/
│   ├── cloudflare/
│   └── deploy/
├── docs/
│   ├── 00-VISION-STRATEGY-ANALYSIS.md
│   ├── AAPS_ANALYSIS_REPORT.md
│   ├── ADMIN_COPILOT_CLI.md
│   ├── ADVANCED_ESCALATION_SYSTEM.md
│   ├── ADVANCED_FEATURES_SUMMARY.md
│   ├── AGENT_CONSOLIDATION_SUMMARY.md
│   ├── AI_MODEL_DEPLOYMENT.md
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE_DETAILED.md
│   ├── ARCHITECTURE_HEALTH_REPORT.md
│   ├── ARCHITECTURE_IMPLEMENTATION_SUMMARY.md
│   ├── ARCHITECTURE_OPTIMIZATION_DASHBOARD.md
│   ├── ARCHITECTURE_RESTRUCTURING_PLAN.md
│   ├── ARCHITECTURE_SKELETON_ANALYSIS.md
│   ├── AUTOMATION_TOOLS_COMPLETION_REPORT.md
│   ├── AUTO_ASSIGNMENT_API.md
│   ├── AUTO_ASSIGNMENT_DEMO.md
│   ├── AUTO_ASSIGNMENT_SUMMARY.md
│   ├── AUTO_ASSIGNMENT_SYSTEM.md
│   ├── AUTO_FIX_BOT_V2_GUIDE.md
│   ├── AUTO_MERGE.md
│   ├── AUTO_MONITOR_INTEGRATION.md
│   ├── AUTO_REFACTOR_EVOLUTION.md
│   ├── AUTO_REVIEW_MERGE.md
│   ├── AXIOM.md
│   ├── BUILD.md
│   ├── BUILD_COMPAT.md
│   ├── CHANGELOG.md
│   ├── CI_AUTO_COMMENT_SYSTEM.md
│   ├── CI_BATCH_UPGRADE_SUMMARY.md
│   ├── CI_CONSOLIDATED_REPORT.md
│   ├── CI_CONSOLIDATED_REPORT_MIGRATION_GUIDE.md
│   ├── CI_DEPLOYMENT_UPGRADE_PLAN.md
│   ├── CI_GLOBAL_STATUS_FIX.md
│   ├── CI_HARDENING_COMPLETION.md
│   ├── CI_HARDENING_NEXT_STEPS.md
│   ├── CI_HARDENING_RECOMMENDATIONS.md
│   ├── CI_INTEGRATION_DEPLOYMENT_WORKFLOW.md
│   ├── CLOUDFLARE_DEPLOYMENT_FIX.md
│   ├── CLOUD_DELEGATION.md
│   ├── CODEQL_SETUP.md
│   ├── CODESPACE_SETUP.md
│   ├── CODE_OF_CONDUCT.md
│   ├── COMPLETION_REPORT.md
│   ├── COMPLETION_SUMMARY.md
│   ├── CONFIGURATION_TEMPLATES.md
│   ├── CONTRACT.md
│   ├── CONTRIBUTING.md
│   ├── CONTRIBUTION_GUIDE.md
│   ├── COPILOT_SETUP.md
│   ├── CURSOR_2_2_VISUAL_EDITOR.md
│   ├── DEEP_WORKFLOW_ANALYSIS.md
│   ├── DEPLOYMENT_ASSESSMENT.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_INTEGRATION_SUMMARY.md
│   ├── DEPLOYMENT_MANIFEST.md
│   ├── DEPLOYMENT_VALIDATION_REPORT.md
│   ├── DEVCONTAINER_RUNBOOK.txt
│   ├── DIRECTORY.md
│   ├── DIRECTORY_RESTRUCTURE_AUTOMATION_GUIDE.md
│   ├── DIRECTORY_TREE.md
│   ├── DISASTER_RECOVERY.md
│   ├── DOCUMENTATION_INDEX.md
│   ├── DOCUMENTATION_SYNC_REPORT.md
│   ├── DYNAMIC_CI_ASSISTANT.md
│   ├── EFFICIENCY_METRICS.md
│   ├── ENGINEER_CORE_FILES_GUIDE.md
│   ├── EXAMPLES.md
│   ├── EXTRACTION_COMPLETION_REPORT.md
│   ├── FHS_DIRECTORY_STRUCTURE.md
│   ├── FINAL_COMPLETION_SUMMARY.md
│   ├── FINAL_DELIVERY_REPORT.md
│   ├── FINAL_PHASE2_COMPLETION_REPORT.md
│   ├── FINAL_REPOSITORY_STATUS_REPORT.md
│   ├── FINAL_ROOT_STRUCTURE_VERIFICATION.md
│   ├── FINAL_SUMMARY.txt
│   ├── GHAS_COMPLETE_GUIDE.md
│   ├── GHAS_DEPLOYMENT.md
│   ├── GLOBAL_TECH_REVIEW.txt
│   ├── GOVERNANCE_FRAMEWORK.md
│   ├── GOVERNANCE_INTEGRATION_NOTE.md
│   ├── HOTSPOT_HEATMAP.md
│   ├── IMPLEMENTATION_PROGRESS.md
│   ├── IMPLEMENTATION_REPORT_AUTO_REFACTOR.md
│   ├── IMPLEMENTATION_SUMMARY_CI_CONSOLIDATED_REPORT.md
│   ├── IMPROVED_ARCHITECTURE.md
│   ├── INCOMPLETE_TASKS_SCAN_REPORT.md
│   ├── INSTALL.md
│   ├── INSTANT_EXECUTION_COMPLETION_REPORT.md
│   ├── INSTANT_EXECUTION_INTEGRATION_MAP.md
│   ├── INSTANT_EXECUTION_SUMMARY.md
│   ├── INSTANT_FIX_TEMPLATE_UPDATE.md
│   ├── INTEGRATION_DEPLOYMENT_SCAN_REPORT.md
│   ├── INTEGRATION_GUIDE.md
│   ├── INTELLIGENT_AUTOMATION_INTEGRATION.md
│   ├── INTERACTIVE_CI_UPGRADE_GUIDE.md
│   ├── ISLAND_AI_SETUP.md
│   ├── ISSUE_RESOLUTION_SUMMARY.md
│   ├── Island-AI 專案目錄結構圖譜註解.docx
│   ├── Island-AI 專案目錄結構圖譜註解.pdf
│   ├── KNOWLEDGE_HEALTH.md
│   ├── LANGUAGE_GOVERNANCE_DASHBOARD.md
│   ├── LANGUAGE_GOVERNANCE_FIX_REPORT.md
│   ├── LANGUAGE_GOVERNANCE_IMPLEMENTATION.md
│   ├── LAYER0_OPTIMIZATION_SUMMARY.md
│   ├── LEGACY_EXTRACTION_SUMMARY.md
│   ├── LEGACY_REFACTORING_EVOLUTION_REPORT.md
│   ├── LICENSE
│   ├── LIVING_KNOWLEDGE_BASE.md
│   ├── MACHINENATIVEOPS_NAMESPACE_STANDARDIZATION.md
│   ├── MATECHAT_INTEGRATION_SUMMARY.md
│   ├── MERGE_BLOCKED_FIX.md
│   ├── MERGE_STATUS_LOADING_FIX.md
│   ├── MIGRATION.md
│   ├── MIGRATION_FLOW.md
│   ├── MIGRATION_GUIDE.md
│   ├── MULTI_REPO_INTEGRATION_GUIDE.md
│   ├── MULTI_REPO_QUICKSTART.md
│   ├── NAMESPACE_SPECIFICATION_COMPLETE.md
│   ├── NAMING_GUIDELINES_MANUAL.md
│   ├── P0_SAFETY_VERIFICATION_REPORT.json
│   ├── PERMISSION_SIMPLIFICATION.md
│   ├── PHASE1_ARCHITECTURE.md
│   ├── PHASE1_COMPLETE_CHECKLIST.md
│   ├── PHASE1_COMPLETION.md
│   ├── PHASE1_DELIVERY_COMPARISON.md
│   ├── PHASE1_IMPLEMENTATION_SUMMARY.md
│   ├── PHASE1_SETUP_GUIDE.md
│   ├── PHASE2_SUBDIRECTORY_RESTRUCTURE_COMPLETION.md
│   ├── PHASE3_COMPLETION.md
│   ├── PHASE3_IMPLEMENTATION_PLAN.md
│   ├── PHASE3_TRIGGER_ANALYSIS.md
│   ├── PHASE4_COMPLETION.md
│   ├── PHASE5_COMPLETION.md
│   ├── PHASE_1_6_COMPLETION_REPORT.md
│   ├── PHOENIX_AGENT.md
│   ├── PR106_STRUCTURE_ANALYSIS.md
│   ├── PR10_CONTINUATION_SUMMARY.md
│   ├── PR110_COMPLETION_SUMMARY.md
│   ├── PR110_DEPLOYMENT_COMPLETION.md
│   ├── PR1_DEEP_ANALYSIS.md
│   ├── PR351_COMPLETION_REPORT.md
│   ├── PR351_CONSISTENCY_SUMMARY.md
│   ├── PR49_WORKFLOW_FAILURE_ANALYSIS.md
│   ├── PRODUCT_OVERVIEW.md
│   ├── PROJECT_DELIVERY_CHECKLIST.md
│   ├── PROJECT_GENERATION_IMPLEMENTATION_SUMMARY.md
│   ├── PROJECT_MAPPING_DEPENDENCY_ANALYSIS.md
│   ├── PROJECT_REORGANIZATION_REPORT.md
│   ├── PROJECT_STRUCTURE.md
│   ├── PR_491_COMPLETION_REPORT.md
│   ├── PR_ANALYSIS_AND_ACTION_PLAN.md
│   ├── PR_REVIEW_COMPLETION_REPORT.md
│   ├── PR_REVIEW_REPORT.md
│   ├── PYTHON_SYNTAX_FIX_COMPLETION_REPORT.md
│   ├── PYTHON_VALIDATION_COMPLETION_REPORT.md
│   ├── QUICK_START.md
│   ├── QUICK_START.production.md
│   ├── QUICK_START_INSTANT_EXECUTION.md
│   ├── README.en.md
│   ├── README.md
│   ├── README_STRUCTURE_CHECK.md
│   ├── RECOVERY_PLAYBOOK.md
│   ├── RECOVERY_SYSTEM_SUMMARY.md
│   ├── REFACTOR_PLAYBOOK_NEXT_STEPS.md
│   ├── REFERENCE_VALIDATION_REPORT.md
│   ├── RELEASE.md
│   ├── REPLIT_DEPLOYMENT.md
│   ├── REPLIT_SYNC_VERIFICATION.md
│   ├── REPOSITORY_SYNC_INTEGRATION_SCAN.md
│   ├── RESTRUCTURE_COMPLETION_REPORT.md
│   ├── RESTRUCTURE_PHASE2_STATUS.md
│   ├── RESTRUCTURE_SUMMARY.txt
│   ├── RESTRUCTURING_COMPLETE.md
│   ├── RESTRUCTURING_SUMMARY.md
│   ├── ROOT_CLEANUP_SUMMARY.md
│   ├── ROOT_DIRECTORY_STRUCTURE.md
│   ├── ROOT_README.md
│   ├── RUN_DEBUG_IMPLEMENTATION_SUMMARY.md
│   ├── RUN_DEBUG_QUICKSTART.md
│   ├── RUN_DEBUG_SYSTEM.md
│   ├── SECRET_SCANNING.md
│   ├── SECURITY.md
│   ├── SECURITY_TRAINING.md
│   ├── SESSION_CONTINUATION_SUMMARY.md
│   ├── SKELETON_INTEGRATION_COMPLETION.md
│   ├── SKIPPED_WORKFLOWS_ANALYSIS.md
│   ├── STRUCTURE_ANALYSIS_REPORT.md
│   ├── STRUCTURE_FIX_COMPLETION_REPORT.md
│   ├── SUBDIRECTORY_RESTRUCTURE_CHECKLIST.md
│   ├── SUBDIRECTORY_RESTRUCTURE_COMPLETION.md
│   ├── SUBDIRECTORY_RESTRUCTURE_GUIDE.md
│   ├── SUBDIRECTORY_RESTRUCTURE_SUMMARY.md
│   ├── SYNC_REFACTOR_MIGRATION_GUIDE.md
│   ├── SYNC_REFACTOR_OPTIMIZATION.md
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── SYSTEM_BRIDGING_ASSESSMENT.md
│   ├── SYSTEM_DIAGNOSTICS.md
│   ├── SYSTEM_EVOLUTION_REPORT.md
│   ├── Screenshot_20251223_131939.jpg
│   ├── Screenshot_20251223_131947.jpg
│   ├── TECH_DEBT_SCAN_REPORT.json
│   ├── TIER1_CONTRACTS_L1_DEPLOYMENT_PLAN.md
│   ├── VALIDATION_GUIDE.md
│   ├── VERSION_MANAGEMENT.md
│   ├── VISION-STRATEGY-ALIGNMENT-SUMMARY.md
│   ├── VISUAL_ELEMENTS.md
│   ├── VULNERABILITY_MANAGEMENT.md
│   ├── WORKFLOW_FAILURE_ANALYSIS.md
│   ├── WORKFLOW_FILES_CREATED.md
│   ├── WORKFLOW_INDEX.md
│   ├── WORKFLOW_INTEGRATION_GUIDE.md
│   ├── WORKFLOW_INTEGRATION_SUMMARY.md
│   ├── WORKFLOW_README.md
│   ├── WORKFLOW_SYSTEM.md
│   ├── WORKFLOW_SYSTEM_SUMMARY.md
│   ├── WORKSPACE_REORGANIZATION_COMPLETE.md
│   ├── _config.yml
│   ├── _fix_structure.sh
│   ├── agents/
│   ├── api/
│   ├── architecture/
│   ├── architecture.zh.md
│   ├── automation/
│   ├── autonomous-ci-compliance.md
│   ├── billion_dollar_automation_plan.md
│   ├── ci/
│   ├── ci-cd/
│   ├── ci-troubleshooting.md
│   ├── configuration/
│   ├── deep-integration-guide.zh.md
│   ├── deployment/
│   ├── design_guidelines.md
│   ├── directory-tree-before.txt
│   ├── docs-index.json
│   ├── enterprise_copilot_prompt_system (1).md
│   ├── enterprise_copilot_prompt_system.md
│   ├── evolution/
│   ├── examples/
│   ├── file-reorganization-plan.md
│   ├── first_push_checklist.md
│   ├── fixes/
│   ├── governance/
│   ├── guides/
│   ├── index.md
│   ├── island-ai-phases.txt
│   ├── island-ai-readme.md
│   ├── island-ai.md
│   ├── island.bootstrap.stage0.yaml
│   ├── issues/
│   ├── knowledge/
│   ├── knowledge_index.yaml
│   ├── migration/
│   ├── mndoc/
│   ├── operations/
│   ├── policies/
│   ├── production-deployment-guide.zh.md
│   ├── project-manifest.md
│   ├── refactor_playbooks/
│   ├── references/
│   ├── reorganize-to-workspace.md
│   ├── replit.md
│   ├── reports/
│   ├── reports-analysis.md
│   ├── roadmap-2026.md
│   ├── roadmap-2026.yaml
│   ├── runbook.zh.md
│   ├── scheduler/
│   ├── scratch/
│   ├── security/
│   ├── stage0_implementation.md
│   ├── templates/
│   ├── todo.md
│   ├── troubleshooting/
│   ├── tutorials/
│   ├── ui/
│   ├── unmanned-island.mndoc.yaml
│   └── workflows/
├── ops/
│   ├── governance/
│   ├── ops/
│   └── schemas/
├── package-lock.json
├── package.json
├── private/
├── projects/
│   ├── AAPS_MARKETPLACE_INTEGRATION_PLAN.md
│   ├── CONVERSATION_LOG.md
│   ├── Cargo.toml
│   ├── IMMEDIATE_TASKS.md
│   ├── INTEGRATION_TODO.md
│   ├── axiom-namespace-migration-plan.md
│   ├── chat_app.py
│   ├── code_assistant.py
│   ├── governance-closed-loop-system.md
│   ├── governance-system-implementation.py
│   ├── guardrails_client.py
│   ├── namespace-converter.py
│   ├── namespace-validator.py
│   ├── restructure_project.py
│   ├── setup.py
│   ├── supply-chain-complete-verifier.py
│   └── verify_refactoring.py
├── runtime/
│   ├── workspace_output_1766487061_5415.txt
│   └── workspace_output_1766487066_7141.txt
├── services/
│   └── server/
├── shared/
│   ├── schema.ts
│   └── types.ts
├── src/
│   ├── bin/
│   ├── scripts/
│   ├── src/
│   └── tooling/
└── tests/
    └── tests/
```
<!-- AUTO-ARCHITECTURE-SYNC:END -->

## 📋 目錄

1. [總覽](#總覽)
2. [Root Layer 架構](#root-layer-架構)
3. [檔案結構](#檔案結構)
4. [資料流程](#資料流程)
5. [模組關係](#模組關係)
6. [驗證系統](#驗證系統)
7. [自動化系統](#自動化系統)

---

## 🎯 總覽

### 系統定位

MachineNativeOps 是一個**企業級治理框架**，專注於 Root Layer 的配置管理、驗證和自動化。

### 核心價值

- ✅ **機器可驗證** - 所有規則都可自動執行
- ✅ **單一事實來源** - 註冊表作為權威資料
- ✅ **自動化執行** - GitHub Actions 自動驗證
- ✅ **持續記憶** - 自動更新專案知識

### 設計原則

1. **配置即代碼** (Configuration as Code)
2. **驗證優先** (Validation First)
3. **自動化一切** (Automate Everything)
4. **記憶持續** (Continuous Memory)

---

## 🏛️ Root Layer 架構

### 三層架構設計

```
┌─────────────────────────────────────────────────────────┐
│                    應用層 (Application)                   │
│  - 業務邏輯                                               │
│  - 用戶介面                                               │
│  - API 服務                                               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   治理層 (Governance)                     │
│  - 規範定義 (root.specs.*.yaml)                          │
│  - 驗證系統 (validate-root-specs.py)                     │
│  - 閘門控制 (gate-root-specs.yml)                        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Root Layer (基礎層)                     │
│  - 全域配置 (root.config.yaml)                           │
│  - 模組註冊 (root.registry.modules.yaml)                 │
│  - 信任鏈 (root.trust.yaml)                              │
│  - 完整性驗證 (root.integrity.yaml)                      │
└─────────────────────────────────────────────────────────┘
```

### Root Layer 組成

#### 1. 配置檔案層 (Configuration Files)

```yaml
root.config.yaml          # 全域配置
root.governance.yaml      # 治理規則
root.modules.yaml         # 模組配置
root.trust.yaml           # 信任鏈
root.provenance.yaml      # 來源追溯
root.integrity.yaml       # 完整性驗證
root.bootstrap.yaml       # 啟動配置
root.naming-policy.yaml   # 命名政策
```

**職責**: 定義系統行為和配置
**更新頻率**: 低 (架構變更時)
**驗證**: 所有變更必須通過 gate-root-specs

#### 2. 規範檔案層 (Specification Files)

```yaml
root.specs.naming.yaml      # 命名規範
root.specs.references.yaml  # 引用規範
root.specs.mapping.yaml     # 映射規範
root.specs.logic.yaml       # 邏輯規範
root.specs.context.yaml     # 上下文規範
```

**職責**: 定義驗證規則
**更新頻率**: 中 (規則調整時)
**驗證**: 規範變更需要治理委員會審核

#### 3. 註冊表層 (Registry Files - SSOT)

```yaml
root.registry.modules.yaml  # 模組註冊表
root.registry.urns.yaml     # URN 註冊表
```

**職責**: 作為唯一事實來源
**更新頻率**: 高 (新增/修改模組時)
**驗證**: 嚴格的一致性檢查

#### 4. 映射檔案層 (Mapping Files)

```
root.devices.map    # 設備映射
root.fs.map         # 檔案系統映射
root.kernel.map     # 核心模組映射
```

**職責**: 定義資源映射關係
**更新頻率**: 低 (系統架構變更時)
**驗證**: 映射完整性檢查

#### 5. 環境檔案層 (Environment Files)

```bash
root.env.sh         # Shell 環境設定
```

**職責**: 定義執行環境
**更新頻率**: 低 (環境變更時)
**驗證**: Shell 語法檢查

---

## 📂 檔案結構

### 完整目錄樹 (已實現狀態更新)

```
MachineNativeOps/
│
├── 📋 Root Layer 配置 (12/12 files implemented)
│   ├── controlplane/baseline/config/root.config.yaml ✅
│   ├── controlplane/baseline/config/root.governance.yaml ✅
│   ├── controlplane/baseline/config/root.modules.yaml ✅
│   ├── controlplane/baseline/config/root.trust.yaml ✅
│   ├── controlplane/baseline/config/root.provenance.yaml ✅
│   ├── controlplane/baseline/config/root.integrity.yaml ✅
│   ├── root.bootstrap.yaml ✅
│   ├── controlplane/baseline/config/root.naming-policy.yaml ✅
│   ├── controlplane/baseline/config/root.devices.map ✅
│   ├── root.fs.map ✅
│   ├── controlplane/baseline/config/root.kernel.map ✅
│   ├── root.env.sh ✅
│   └── controlplane/baseline/config/gates.map.yaml ✅
│
├── 📋 規範檔案 (8 files - exceeds planning)
│   ├── controlplane/baseline/specifications/root.specs.naming.yaml ✅
│   ├── controlplane/baseline/specifications/root.specs.references.yaml ✅
│   ├── controlplane/baseline/specifications/root.specs.mapping.yaml ✅
│   ├── controlplane/baseline/specifications/root.specs.logic.yaml ✅
│   ├── controlplane/baseline/specifications/root.specs.context.yaml ✅
│   ├── controlplane/baseline/specifications/root.specs.namespace.yaml ✅
│   ├── controlplane/baseline/specifications/root.specs.paths.yaml ✅
│   └── controlplane/baseline/specifications/root.specs.urn.yaml ✅
│
├── 📦 註冊表 (4 files - exceeds planning)
│   ├── controlplane/baseline/registries/root.registry.modules.yaml ✅
│   ├── controlplane/baseline/registries/root.registry.urns.yaml ✅
│   ├── controlplane/baseline/registries/root.registry.devices.yaml ✅
│   └── controlplane/baseline/registries/root.registry.namespaces.yaml ✅
│
├── 🧠 記憶系統 (4 files)
│   ├── PROJECT_MEMORY.md
│   ├── ARCHITECTURE.md (本檔案)
│   ├── CONVERSATION_LOG.md
│   └── ACCEPTANCE_CHECKLIST.md
│
├── 📚 文檔 (3 files)
│   ├── ROOT_SPECS_GUIDE.md
│   ├── ROOT_ARCHITECTURE.md
│   └── ROOT_SPECS_IMPLEMENTATION_REPORT.md
│
├── 🔍 驗證系統
│   ├── scripts/validation/
│   │   └── validate-root-specs.py
│   └── .github/workflows/
│       ├── gate-root-specs.yml
│       ├── gate-pr-evidence.yml
│       └── gate-root-naming.yml
│
├── 🚀 初始化系統
│   └── init.d/
│       ├── 00-init.sh
│       ├── 01-governance-init.sh
│       ├── 02-modules-init.sh
│       ├── 03-super-execution-init.sh
│       ├── 04-trust-init.sh
│       ├── 05-provenance-init.sh
│       ├── 06-database-init.sh
│       ├── 07-config-init.sh
│       ├── 08-dependencies-init.sh
│       ├── 09-logging-init.sh
│       ├── 10-security-init.sh
│       ├── 11-multiplatform-init.sh
│       ├── 12-api-gateway-init.sh
│       ├── 13-services-init.sh
│       └── 99-finalize.sh
│
└── 🗂️ FHS 標準目錄
    ├── bin/
    ├── sbin/
    ├── etc/
    ├── lib/
    ├── var/
    ├── usr/
    ├── home/
    ├── tmp/
    ├── opt/
    └── srv/
```

### 檔案命名規範

#### Root Layer 檔案

- **格式**: `root.<category>.<ext>`
- **範例**: `root.config.yaml`, `root.devices.map`
- **規則**:
  - 必須小寫
  - 使用 `.yaml` 而非 `.yml`
  - 不可包含空白或大寫

#### 規範檔案

- **格式**: `root.specs.<category>.yaml`
- **範例**: `root.specs.naming.yaml`
- **規則**:
  - 必須在 root.specs. 命名空間下
  - category 使用 kebab-case

#### 註冊表檔案

- **格式**: `root.registry.<type>.yaml`
- **範例**: `root.registry.modules.yaml`
- **規則**:
  - 必須在 root.registry. 命名空間下
  - 作為 SSOT，不可重複定義

---

## 🔄 資料流程

### 1. 開發流程

```
┌─────────────┐
│ 開發者修改   │
│ root.*.yaml │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  創建 PR    │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│     GitHub Actions 自動觸發          │
│  1. gate-pr-evidence.yml            │
│  2. gate-root-naming.yml            │
│  3. gate-root-specs.yml             │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│        執行驗證                      │
│  - 命名規範檢查                      │
│  - 引用格式檢查                      │
│  - 映射一致性檢查                    │
│  - 邏輯完整性檢查                    │
│  - 上下文一致性檢查                  │
└──────┬──────────────────────────────┘
       │
       ↓
    通過？
    /    \
   是     否
   │      │
   │      ↓
   │   ┌─────────────┐
   │   │ PR 被阻擋   │
   │   │ 顯示錯誤    │
   │   └─────────────┘
   │
   ↓
┌─────────────┐
│  可以合併   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 合併到 main │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│      自動更新記憶系統                │
│  - PROJECT_MEMORY.md                │
│  - CONVERSATION_LOG.md              │
│  - ARCHITECTURE.md                  │
└─────────────────────────────────────┘
```

### 2. 驗證流程

```
┌─────────────────┐
│  PR 觸發驗證    │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      載入規範檔案                    │
│  - root.specs.naming.yaml           │
│  - root.specs.references.yaml       │
│  - root.specs.mapping.yaml          │
│  - root.specs.logic.yaml            │
│  - root.specs.context.yaml          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      載入註冊表                      │
│  - root.registry.modules.yaml       │
│  - root.registry.urns.yaml          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      載入 Root 檔案                  │
│  - root.*.yaml (9 files)            │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      執行 5 類驗證                   │
│  1. 命名規範驗證                     │
│  2. 引用格式驗證                     │
│  3. 映射一致性驗證                   │
│  4. 邏輯完整性驗證                   │
│  5. 上下文一致性驗證                 │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      生成驗證報告                    │
│  - root-specs-validation-report.md  │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      更新 PR 狀態                    │
│  - 通過: ✅ 綠色勾勾                 │
│  - 失敗: ❌ 紅色叉叉 + 詳細報告      │
└─────────────────────────────────────┘
```

### 3. 記憶更新流程 (自動化)

```
┌─────────────────┐
│  代碼合併到 main │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      分析變更內容                    │
│  - 新增了哪些檔案？                  │
│  - 修改了哪些配置？                  │
│  - 刪除了哪些內容？                  │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      提取關鍵資訊                    │
│  - 功能變更                          │
│  - 架構調整                          │
│  - 決策記錄                          │
│  - 問題修復                          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      更新記憶文檔                    │
│  - PROJECT_MEMORY.md                │
│    * 更新功能清單                    │
│    * 記錄已知問題                    │
│    * 更新下一步計劃                  │
│  - CONVERSATION_LOG.md              │
│    * 記錄變更摘要                    │
│    * 記錄決策原因                    │
│  - ARCHITECTURE.md                  │
│    * 更新架構圖                      │
│    * 更新檔案結構                    │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────┐
│  自動提交變更   │
└─────────────────┘
```

---

## 🔗 模組關係

### 模組依賴圖

```
config-manager (核心)
    ↓
    ├─→ logging-service
    │       ↓
    │       ├─→ governance-engine
    │       │       ↓
    │       │       └─→ super-execution-engine
    │       │
    │       ├─→ provenance-tracker
    │       │
    │       └─→ monitoring-service
    │
    ├─→ trust-manager
    │       ↓
    │       └─→ integrity-validator
    │
    └─→ (其他模組)
```

### 模組載入順序

1. **config-manager** (優先級: 100)

   - 無依賴
   - 提供: 配置驗證、載入、監控

2. **logging-service** (優先級: 90)

   - 依賴: config-manager
   - 提供: 結構化日誌、聚合、輪轉

3. **trust-manager** (優先級: 90)

   - 依賴: config-manager, crypto-provider, storage-backend
   - 提供: 證書管理、信任鏈驗證、金鑰輪轉

4. **governance-engine** (優先級: 80)

   - 依賴: config-manager, logging-service, database-connector
   - 提供: 政策執行、RBAC 管理、審計日誌

5. **provenance-tracker** (優先級: 70)

   - 依賴: config-manager, logging-service, database-connector
   - 提供: 審計軌跡、來源追溯、事件溯源

6. **integrity-validator** (優先級: 70)

   - 依賴: config-manager, crypto-provider
   - 提供: 雜湊驗證、完整性檢查、篡改檢測

7. **super-execution-engine** (優先級: 60)

   - 依賴: config-manager, logging-service, governance-engine
   - 提供: 工作流編排、任務調度、執行監控

8. **monitoring-service** (優先級: 50)

   - 依賴: config-manager, logging-service
   - 提供: 指標收集、健康監控、告警

### 模組通訊

```
┌─────────────────┐
│ Application     │
└────────┬────────┘
         │ API Calls
         ↓
┌─────────────────────────────────────┐
│     super-execution-engine          │
│  (工作流編排)                        │
└────────┬────────────────────────────┘
         │
         ├─→ governance-engine (政策檢查)
         │
         ├─→ provenance-tracker (記錄追溯)
         │
         ├─→ integrity-validator (完整性驗證)
         │
         └─→ monitoring-service (監控)
                 │
                 ↓
         ┌─────────────────┐
         │ logging-service │
         │  (集中日誌)      │
         └─────────────────┘
```

---

## 🔍 驗證系統

### 驗證層級

#### Level 1: 語法驗證

- **檢查項目**: YAML 語法、檔案格式
- **工具**: Python yaml.safe_load()
- **執行時機**: PR 創建時
- **失敗處理**: 立即阻擋

#### Level 2: 命名驗證

- **檢查項目**: 檔名、鍵名、值名
- **工具**: Regex 模式匹配
- **執行時機**: PR 創建時
- **失敗處理**: 阻擋 + 提供修復建議

#### Level 3: 引用驗證

- **檢查項目**: URN 格式、引用存在性
- **工具**: 註冊表查詢
- **執行時機**: PR 創建時
- **失敗處理**: 阻擋 + 列出缺失引用

#### Level 4: 邏輯驗證

- **檢查項目**: 循環依賴、狀態一致性
- **工具**: DFS 算法、拓撲排序
- **執行時機**: PR 創建時
- **失敗處理**: 阻擋 + 顯示循環路徑

#### Level 5: 上下文驗證

- **檢查項目**: 跨檔案一致性、漂移檢測
- **工具**: 相似度分析
- **執行時機**: PR 創建時
- **失敗處理**: 警告或阻擋 (視嚴重程度)

### 驗證工具鏈

```
┌─────────────────────────────────────┐
│     validate-root-specs.py          │
│  (Python 驗證器)                     │
│                                      │
│  ├─ load_specifications()           │
│  ├─ load_registries()               │
│  ├─ load_root_files()               │
│  ├─ validate_naming_spec()          │
│  ├─ validate_references_spec()      │
│  ├─ validate_mapping_spec()         │
│  ├─ validate_logic_spec()           │
│  ├─ validate_context_spec()         │
│  └─ generate_report()               │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│     gate-root-specs.yml             │
│  (GitHub Actions 工作流)             │
│                                      │
│  ├─ Naming Validation               │
│  ├─ Reference Validation            │
│  ├─ Mapping Validation              │
│  ├─ Logic Validation                │
│  ├─ Context Validation              │
│  └─ Python Validator                │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  root-specs-validation-report.md    │
│  (驗證報告)                          │
└─────────────────────────────────────┘
```

---

## 🤖 自動化系統

### 自動化層級

#### Level 1: 自動驗證

- **觸發**: PR 創建/更新
- **執行**: GitHub Actions
- **結果**: 通過/失敗 + 報告

#### Level 2: 自動記憶更新

- **觸發**: 合併到 main
- **執行**: GitHub Actions
- **結果**: 更新 PROJECT_MEMORY.md

#### Level 3: 自動架構同步

- **觸發**: 檔案結構變更
- **執行**: GitHub Actions
- **結果**: 更新 ARCHITECTURE.md

#### Level 4: 自動對話記錄

- **觸發**: PR 合併
- **執行**: GitHub Actions
- **結果**: 更新 CONVERSATION_LOG.md

#### Level 5: 自動知識萃取

- **觸發**: 重大變更
- **執行**: AI 分析
- **結果**: 更新知識圖譜

### 自動化工作流

```yaml
# .github/workflows/auto-memory-update.yml

name: Auto Memory Update

on:
  push:
    branches: [main]

jobs:
  update-memory:
    runs-on: ubuntu-latest
    steps:

      - name: Checkout
      - name: Analyze Changes
      - name: Update PROJECT_MEMORY.md
      - name: Update CONVERSATION_LOG.md
      - name: Update ARCHITECTURE.md
      - name: Commit Changes
```

---

## 📊 架構決策記錄 (ADR)

### ADR-001: 採用 YAML 作為配置格式

- **日期**: 2024-12-20
- **狀態**: ✅ 已採用
- **決策**: 使用 YAML 作為所有配置檔案格式
- **理由**: 人類可讀、支援註解、工具豐富
- **影響**: 所有配置必須是有效的 YAML

### ADR-002: 建立 SSOT 註冊表

- **日期**: 2024-12-21
- **狀態**: ✅ 已採用
- **決策**: 創建 root.registry.*.yaml 作為唯一事實來源
- **理由**: 避免資料重複和不一致
- **影響**: 所有模組資訊必須先在註冊表定義

### ADR-003: 使用 URN 作為引用格式

- **日期**: 2024-12-21
- **狀態**: ✅ 已採用
- **決策**: 採用 URN 格式作為主要引用方式
- **理由**: 全域唯一、版本控制、類型安全
- **影響**: 所有引用必須使用 URN 格式

### ADR-004: 自動化 PR 阻擋

- **日期**: 2024-12-21
- **狀態**: ✅ 已採用
- **決策**: 使用 GitHub Actions 自動阻擋不合規 PR
- **理由**: 即時反饋、防止錯誤、減少人工負擔
- **影響**: 所有 PR 必須通過驗證

### ADR-005: 建立自動記憶系統

- **日期**: 2024-12-21
- **狀態**: 🔄 實施中
- **決策**: 建立自動更新的記憶系統
- **理由**: 防止知識碎片化、維持上下文連續性
- **影響**: 每次變更都會更新記憶文檔

---

## 🔄 版本歷史

### v1.0.0 (2024-12-21)

- ✅ 完成 Root Layer 規範系統
- ✅ 建立 5 個規範檔案
- ✅ 建立 2 個註冊表檔案
- ✅ 實現自動化驗證系統
- ✅ 創建統一閘門映射
- ✅ 完成完整文檔系統

- 🔄 修復 monitoring-service 不一致問題 (2025-12-21 02:13:25)

### v1.1.0 (計劃中)

- 📋 實現自動記憶更新
- 📋 建立知識圖譜
- 📋 增強驗證覆蓋率
- 📋 優化自動化流程

---

## 📞 維護資訊

### 文檔維護

- **負責人**: MachineNativeOps Governance Team
- **更新頻率**: 自動更新 (每次 commit)
- **手動審查**: 每月一次

### 架構審查

- **頻率**: 每季度
- **參與者**: 技術委員會
- **輸出**: 架構改進建議

---

**文檔版本**: 1.0.0  
**最後更新**: 2024-12-21  
**自動更新**: 🟢 啟用  
**維護者**: AI Agent + Automation System
