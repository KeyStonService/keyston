# File Reorganization Plan

## 文件分類

### 1. 保留在根目錄（必要文件）

- README.md (需要重寫)
- .gitignore
- .gitignore.prod
- .env.example
- todo.md
- root.bootstrap.yaml (引導文件)
- root.env.sh (環境變數)
- root.fs.map (文件系統映射)

### 2. 移動到 controlplane/governance/reports/

**報告類文件**:

- AAPS_INTEGRATION_SUMMARY.md
- AAPS_PHASE1_COMPLETION_SUMMARY.md
- AAPS_UNIFIED_GATES_OPTIMIZATION.md
- AUTOMATED_MEMORY_SYSTEM_COMPLETE.md
- CI_FIX_SUMMARY.md
- CI_ISSUES_FIX_REPORT.md
- CONTROLPLANE_IMPLEMENTATION_REPORT.md
- FALSE_SUCCESS_METRICS_FIXED_REPORT.md
- FINAL_MACHINE_NATIVE_OPS_COMPLETION_REPORT.md
- LOCAL_FIXES_SUMMARY.md
- PLATFORM_CLOSURE_SUCCESS_REPORT.md
- PR_666_IMPLEMENTATION_SUMMARY.md
- ROOT_SPECS_IMPLEMENTATION_REPORT.md
- STEP2_COMPLETION_SUMMARY.md
- SUPERAGENT_NAMESPACE_CONVERSION_SUMMARY.md
- VERIFICATION_REPORT.md
- conversion-report-new.md
- memory-update-summary.md
- restructure_log.md
- validation-report-final.md
- validation-report-new.md

### 3. 移動到 controlplane/governance/docs/

**治理文檔**:

- ACCEPTANCE_CHECKLIST.md
- AGENTS.md
- ARCHITECTURE.md
- CHANGELOG.md
- DIRECTORY.md
- IMPLEMENTATION_GUIDE.md
- IMPLEMENTATION_ROADMAP.md
- MULTI_AGENT_MPC_ARCHITECTURE_DESIGN.md
- MULTI_AGENT_V1_SPECIFICATION_PACKAGE.md
- PHASE1_COMPREHENSIVE_AUDIT.md
- PHASE2_DETAILED_ROADMAP.md
- PROJECT_MEMORY.md
- RISK_ASSESSMENT.md
- ROOT_ARCHITECTURE.md
- ROOT_SPECS_GUIDE.md

### 4. 移動到 controlplane/governance/policies/

**政策和配置文件**:

- governance-config.yaml
- gates.map.yaml
- auto-fix-bot.yml

### 5. 移動到 controlplane/baseline/config/ (已存在的重複文件)

**這些文件已經在 controlplane/baseline/config/ 中，根目錄的應該刪除**:

- root.config.yaml
- root.devices.map
- root.governance.yaml
- root.integrity.yaml
- root.kernel.map
- root.modules.yaml
- root.naming-policy.yaml
- root.provenance.yaml
- root.super-execution.yaml
- root.trust.yaml

### 6. 移動到 controlplane/baseline/specifications/ (已存在的重複文件)

**這些文件已經在 controlplane/baseline/specifications/ 中，根目錄的應該刪除**:

- root.specs.context.yaml
- root.specs.logic.yaml
- root.specs.mapping.yaml
- root.specs.naming.yaml
- root.specs.references.yaml

### 7. 移動到 controlplane/baseline/registries/ (已存在的重複文件)

**這些文件已經在 controlplane/baseline/registries/ 中，根目錄的應該刪除**:

- root.registry.modules.yaml
- root.registry.urns.yaml

### 8. 移動到 workspace/projects/

**專案相關文件**:

- AAPS_MARKETPLACE_INTEGRATION_PLAN.md
- CONVERSATION_LOG.md
- IMMEDIATE_TASKS.md
- INTEGRATION_TODO.md
- axiom-namespace-migration-plan.md
- governance-closed-loop-system.md

### 9. 移動到 workspace/config/

**專案配置文件**:

- machinenativeops.yaml
- mno-namespace.yaml
- root.bootstrap.minimal.yaml
- root.validator.schema.yaml
- docker-compose.prod.yml

### 10. 其他文件

- CNAME (GitHub Pages 配置，保留在根目錄)
- Cargo.toml (Rust 配置，移到 workspace/projects/)
- Dockerfile (Docker 配置，移到 workspace/config/)
- MANIFEST.in (Python 配置，移到 workspace/config/)
- replit.md (Replit 文檔，移到 workspace/docs/)
- .replit (Replit 配置，保留在根目錄)

## 執行順序

1. 創建目標目錄結構
2. 移動文件到對應位置
3. 刪除重複文件
4. 更新根目錄 README.md
5. 驗證移動結果
6. Git 提交
