# Subdirectory Restructuring Guide

## Overview

This guide provides detailed instructions for Phase 2 of the MachineNativeOps restructuring: subdirectory-level reorganization and standardization.

**Specification Version:** 1.0.0  
**Parent Spec:** machinenativeops-restructure-spec.json v4.0.0  
**Created:** 2025-12-18

## Objectives

1. **Standardize Naming**: Convert all subdirectories to kebab-case
2. **Eliminate Duplication**: Merge overlapping and duplicate directories
3. **Improve Organization**: Group related components logically
4. **Remove Legacy Code**: Clean up scratch, legacy, and deprecated directories
5. **Enhance Maintainability**: Create clear, intuitive directory structure

## Current Issues

### src/ Directory

- Multiple overlapping directories (automation/, autonomous/, bridges/)
- Inconsistent naming (apps/ vs client/ vs frontend/)
- Scratch and legacy directories mixed with production code
- Unclear separation between services and shared code

### config/ Directory

- 60+ files at root level without clear organization
- Mixed concerns (CI, dev, docker, agents, etc.)
- Duplicate configuration files
- No clear environment separation

### scripts/ Directory

- Mixed script types at root level
- Unclear categorization
- Legacy and duplicate scripts

### governance/ Directory

- Currently located in src/governance/ (should be at root)
- 40+ numbered directories (00-40+)
- Mixed content types
- Unclear hierarchy

## Target Structure

### src/ - Application Source Code

```
src/
├── ai/                          # AI decision engine and ML pipelines
│   ├── agents/                  # Autonomous AI agents
│   ├── collaboration/           # Multi-agent collaboration
│   ├── inference/               # Model inference and serving
│   ├── training/                # Model training pipelines
│   └── examples/                # AI usage examples
├── core/                        # Core orchestration engine
│   ├── engine/                  # Core execution engine
│   ├── plugins/                 # Plugin system
│   ├── contracts/               # API contracts
│   ├── monitoring/              # System monitoring
│   ├── safety/                  # Safety mechanisms
│   └── integrations/            # External integrations
├── autonomous/                  # Autonomous operations
│   ├── infrastructure/          # IaC management
│   ├── deployment/              # Deployment automation
│   ├── agents/                  # Operation agents
│   └── self-healing/            # Self-healing systems
├── services/                    # Microservices
│   ├── api-gateway/             # API gateway
│   ├── auth/                    # Authentication service
│   ├── config-management/       # Config service
│   └── observability/           # Observability service
├── web/                         # Web applications
│   ├── admin/                   # Admin dashboard
│   ├── api/                     # Web API backend
│   ├── client/                  # Client application
│   └── shared/                  # Shared components
├── shared/                      # Shared libraries
│   ├── types/                   # TypeScript types
│   ├── utils/                   # Utility functions
│   ├── constants/               # Constants
│   └── schemas/                 # Data schemas
└── mcp-servers/                 # MCP servers
```

### config/ - Configuration Management

```
config/
├── environments/                # Environment-specific configs
│   ├── dev/                     # Development
│   ├── staging/                 # Staging
│   └── prod/                    # Production
├── ci-cd/                       # CI/CD configurations
├── docker/                      # Docker configurations
│   ├── compose/                 # Docker Compose files
│   └── templates/               # Dockerfile templates
├── agents/                      # Agent configurations
├── automation/                  # Automation configs
├── monitoring/                  # Monitoring configs
├── security/                    # Security configs
├── governance/                  # Governance configs
├── build/                       # Build tool configs
├── linting/                     # Linting configs
├── integrations/                # Integration configs
├── templates/                   # Config templates
└── system/                      # System-level configs
```

### scripts/ - Automation Scripts

```
scripts/
├── dev/                         # Development scripts
├── ci/                          # CI/CD scripts
├── ops/                         # Operations scripts
│   ├── migration/               # Migration scripts
│   ├── onboarding/              # Onboarding scripts
│   ├── reports/                 # Report generation
│   ├── runbooks/                # Operational runbooks
│   └── artifacts/               # Build artifacts
├── deployment/                  # Deployment scripts
│   └── k8s/                     # Kubernetes scripts
├── governance/                  # Governance scripts
│   ├── naming/                  # Naming enforcement
│   └── migration/               # Migration scripts
├── automation/                  # General automation
└── utils/                       # Utility scripts
```

### governance/ - Governance Hub

```
governance/
├── policies/                    # Policy definitions
├── strategies/                  # Strategic frameworks
├── architecture/                # Architecture decisions
├── compliance/                  # Compliance frameworks
├── security/                    # Security policies
├── processes/                   # Process definitions
├── metrics/                     # Metrics frameworks
├── tools/                       # Governance tools
├── docs/                        # Documentation
├── templates/                   # Templates
├── schemas/                     # Data schemas
└── automation/                  # Automation scripts
```

### examples/ - Educational Content

```
examples/
├── namespace-tutorial/          # Kubernetes tutorial
├── governance/                  # Governance examples
├── integrations/                # Integration examples
└── workflows/                   # Workflow examples
```

### tests/ - Test Suites

```
tests/
├── unit/                        # Unit tests
├── integration/                 # Integration tests
├── e2e/                         # End-to-end tests
└── fixtures/                    # Test fixtures
```

## Migration Phases

### Phase 1: Preparation and Backup

**Duration:** 30 minutes

1. **Create Feature Branch**

   ```bash
   git checkout -b refactor/subdirectory-restructure
   ```

2. **Create Backup Tag**

   ```bash
   git tag -a subdirectory-backup-$(date +%Y%m%d-%H%M%S) -m "Backup before subdirectory restructure"
   git push origin --tags
   ```

3. **Generate Directory Tree Snapshot**

   ```bash
   tree -L 4 -I 'node_modules|.git' > docs/directory-tree-before.txt
   ```

4. **Run Dependency Analysis**

   ```bash
   npx madge --circular --extensions ts,js,py src/ > docs/dependency-graph-before.txt
   ```

5. **Document Current Import Paths**

   ```bash
   grep -r "from.*import" src/ > docs/import-paths-before.txt
   grep -r "import.*from" src/ >> docs/import-paths-before.txt
   ```

### Phase 2: src/ Restructuring

**Duration:** 2-3 hours

#### Step 1: Create New Structure

```bash
# AI subdirectories
mkdir -p src/ai/{inference,training}

# Core subdirectories
mkdir -p src/core/{engine,plugins,contracts,monitoring,safety,integrations}

# Autonomous subdirectories
mkdir -p src/autonomous/self-healing

# Services subdirectories
mkdir -p src/services/{api-gateway,auth,config-management,observability}

# Web subdirectories
mkdir -p src/web/{admin,api,client,shared}

# Shared subdirectories
mkdir -p src/shared/{types,utils,constants}
```

#### Step 2: Merge AI Directories

```bash
# Keep existing: ai/agents/, ai/collaboration/, ai/examples/
# Remove: ai/__tests__/
rm -rf src/ai/__tests__/
```

#### Step 3: Consolidate Core Components

```bash
# Merge execution engines
rsync -av src/core/execution_engine/ src/core/engine/
rsync -av src/core/execution_architecture/ src/core/engine/
rsync -av src/core/hlp_executor/ src/core/engine/

# Merge plugins
cp src/core/plugin_system.py src/core/plugins/
rsync -av src/core/modules/ src/core/plugins/

# Merge contracts
rsync -av src/core/contract_service/ src/core/contracts/
rsync -av src/contracts/ src/core/contracts/

# Merge monitoring
rsync -av src/core/monitoring_system/ src/core/monitoring/

# Merge safety mechanisms
rsync -av src/core/safety_mechanisms/ src/core/safety/
cp src/core/hallucination_detector.py src/core/safety/
cp src/core/autonomous_trust_engine.py src/core/safety/

# Merge integrations
rsync -av src/core/unified_integration/ src/core/integrations/
rsync -av src/core/mcp_servers_enhanced/ src/core/integrations/

# Remove deprecated directories
rm -rf src/core/{_scratch,advisory-database,ai_constitution,ci_error_handler}
rm -rf src/core/{cloud_agent_delegation,island_ai_runtime,main_system}
rm -rf src/core/{project_factory,slsa_provenance,tech_stack,training_system}
rm -rf src/core/{validators,virtual_experts,yaml_module_system}
```

#### Step 4: Reorganize Autonomous Operations

```bash
# Merge infrastructure
rsync -av src/automation/autonomous/ src/autonomous/infrastructure/

# Merge deployment
rsync -av src/automation/pipelines/ src/autonomous/deployment/

# Merge agents
rsync -av src/autonomous/ops/ src/autonomous/agents/
rsync -av src/automation/intelligent/ src/autonomous/agents/

# Remove deprecated
rm -rf src/autonomous/core/
```

#### Step 5: Migrate Services and Web

```bash
# Merge services
rsync -av src/services/ src/services/
rsync -av src/server/ src/services/

# Merge web applications
rsync -av src/apps/web/ src/web/admin/
rsync -av src/frontend/ui/ src/web/admin/
rsync -av src/apps/web-backend/ src/web/api/
rsync -av src/client/ src/web/client/
rsync -av src/shared/ src/web/shared/
```

#### Step 6: Create Shared Libraries

```bash
# Move schemas
rsync -av src/schemas/ src/shared/schemas/
```

#### Step 7: Clean Up Root Level

```bash
# Remove deprecated directories
rm -rf src/{automation,apps,bridges,canonical,contracts}
rm -rf src/{docker-templates,frontend,runtime,server}
rm -rf src/{supply-chain,templates}
rm -rf src/{machinenativeops.egg-info,synergymesh.egg-info}
```

#### Step 8: Move to Other Roots

```bash
# Move governance to root
mv src/governance/ governance/

# Move tests to root
mv src/tests/ tests/

# Move templates to config
mv src/templates/ config/templates/
mv src/docker-templates/ config/docker/templates/
```

### Phase 3: config/ Reorganization

**Duration:** 1-2 hours

#### Step 1: Create Environment Structure

```bash
mkdir -p config/environments/{dev,staging,prod}

# Move environment files
mv config/dev/environments/development.env config/environments/dev/
mv config/dev/environments/staging.env config/environments/staging/
mv config/dev/environments/production.env config/environments/prod/
mv config/docker-compose.dev.yml config/environments/dev/
```

#### Step 2: Group CI/CD Configurations

```bash
mkdir -p config/ci-cd
mv config/ci-*.yaml config/ci-cd/
mv config/drone-config.yml config/ci-cd/
```

#### Step 3: Organize Docker Configurations

```bash
mkdir -p config/docker/compose
mv config/docker-compose*.yml config/docker/compose/
mv config/Dockerfile config/docker/
mv config/.dockerignore config/docker/
rsync -av config/docker/ config/docker/templates/
```

#### Step 4: Group Monitoring Configs

```bash
mkdir -p config/monitoring
mv config/monitoring.yaml config/monitoring/
mv config/prometheus-*.yml config/monitoring/
mv config/grafana-dashboard.json config/monitoring/
mv config/elasticsearch-config.sh config/monitoring/
```

#### Step 5: Group Security Configs

```bash
mkdir -p config/security
mv config/security-network-config.yml config/security/
mv config/safety-mechanisms.yaml config/security/
```

#### Step 6: Group Governance Configs

```bash
mkdir -p config/governance
mv config/governance-manifest.yaml config/governance/
mv config/language-policy.yaml config/governance/
mv config/ai-constitution.yaml config/governance/
```

#### Step 7: Group Build Configs

```bash
mkdir -p config/build
mv config/vite.config.ts config/build/
mv config/tsconfig.json config/build/
mv config/eslint.config.js config/build/
mv config/.eslintrc.yaml config/build/
mv config/jest.config.js config/build/
mv config/postcss.config.js config/build/
mv config/tailwind.config.ts config/build/
mv config/drizzle.config.ts config/build/
mv config/peachy-build.toml config/build/
```

#### Step 8: Group Linting Configs

```bash
mkdir -p config/linting
mv config/.prettierrc config/linting/
mv config/.markdownlint.json config/linting/
mv config/.markdownlintignore config/linting/
mv config/.pre-commit-config.yaml config/linting/
```

#### Step 9: Group System Configs

```bash
mkdir -p config/system
mv config/machinenativeops-restructure-spec.json config/system/
mv config/subdirectory-restructure-spec.json config/system/
mv config/system-manifest.yaml config/system/
mv config/system-module-map.yaml config/system/
mv config/system-evolution.yaml config/system/
mv config/unified-config-index.yaml config/system/
mv config/dependencies.yaml config/system/
mv config/environment.yaml config/system/
```

#### Step 10: Remove Deprecated Files

```bash
rm -f config/auto-fix-bot\ .prompt.yml
rm -f config/synergymesh.config.yaml
rm -f config/island-control.yml
rm -f config/topology-mind-matrix.yaml
rm -f config/tenant-tier-definitions.yaml
rm -f config/recovery-system.yaml
rm -f config/refactor-evolution.yaml
rm -f config/sync-refactor-config.yaml
rm -f config/instant-execution-pipeline.yaml
rm -f config/cloud-agent-delegation.yml
rm -f config/builder-system-prompt.yaml
rm -f config/brand-mapping.yaml
rm -f config/yaml-module-system.yaml
rm -f config/island-ai-runtime.yaml

rm -rf config/autofix/
rm -rf config/conftest/
rm -rf config/pipelines/
```

### Phase 4: scripts/ Cleanup

**Duration:** 1 hour

#### Step 1: Categorize Scripts

```bash
mkdir -p scripts/{dev,deployment,automation,utils}
mkdir -p scripts/governance/{naming,migration}
mkdir -p scripts/deployment/k8s
```

#### Step 2: Move Scripts

```bash
# Development scripts
mv scripts/start-synergymesh-dev.sh scripts/dev/
mv scripts/start-automation-engine.sh scripts/dev/

# Deployment scripts
mv scripts/deploy.sh scripts/deployment/
mv scripts/comprehensive-deploy.sh scripts/deployment/
mv scripts/run-instant-execution.sh scripts/deployment/
mv scripts/k8s/ scripts/deployment/

# Governance scripts
mv scripts/brand-migration.sh scripts/governance/migration/
mv scripts/brand-replacer.py scripts/governance/migration/
mv scripts/naming/ scripts/governance/

# Automation scripts
mv scripts/automation_launcher.py scripts/automation/
mv scripts/emergency_recovery.py scripts/automation/

# Utility scripts
mv scripts/bootstrap-from-manifest.sh scripts/utils/
mv scripts/fix-island-ai.sh scripts/utils/
```

#### Step 3: Remove Deprecated

```bash
rm -f scripts/auto_sync_flow.mermaid.txt
rm -f scripts/github_sync_workflow.txt
rm -f scripts/system_interconnection.mermaid.txt
rm -f scripts/post_commit_hook.sh
rm -rf scripts/hooks/
rm -rf scripts/sync/
```

#### Step 4: Move to Other Locations

```bash
# Move hooks to .github
mkdir -p .github/hooks
mv scripts/hooks/ .github/

# Move build.ts to src
mv scripts/build.ts src/build/
```

### Phase 5: governance/ Migration

**Duration:** 2-3 hours

#### Step 1: Create New Structure

```bash
mkdir -p governance/{policies,strategies,architecture,compliance}
mkdir -p governance/{security,processes,metrics,tools}
mkdir -p governance/{docs,templates,schemas,automation}
```

#### Step 2: Merge Directories

```bash
# Policies
rsync -av src/governance/23-policies/ governance/policies/
rsync -av src/governance/10-policy/ governance/policies/

# Strategies
rsync -av src/governance/00-vision-strategy/ governance/strategies/
rsync -av src/governance/20-intent/ governance/strategies/

# Architecture
rsync -av src/governance/01-architecture/ governance/architecture/
rsync -av src/governance/18-complex-system/ governance/architecture/

# Compliance
rsync -av src/governance/05-compliance/ governance/compliance/
rsync -av src/governance/07-audit/ governance/compliance/
rsync -av src/governance/70-audit/ governance/compliance/

# Security
rsync -av src/governance/06-security/ governance/security/

# Processes
rsync -av src/governance/08-process/ governance/processes/
rsync -av src/governance/03-change/ governance/processes/

# Metrics
rsync -av src/governance/09-performance/ governance/metrics/
rsync -av src/governance/13-metrics-reporting/ governance/metrics/

# Tools
rsync -av src/governance/26-tools/ governance/tools/
rsync -av src/governance/11-tools-systems/ governance/tools/

# Docs
rsync -av src/governance/29-docs/ governance/docs/

# Templates
rsync -av src/governance/27-templates/ governance/templates/

# Schemas
rsync -av src/governance/31-schemas/ governance/schemas/
rsync -av src/governance/schemas/ governance/schemas/

# Automation
rsync -av src/governance/39-automation/ governance/automation/
rsync -av src/governance/40-self-healing/ governance/automation/
```

#### Step 3: Remove Deprecated

```bash
rm -rf src/governance/{_legacy,_scratch}
rm -rf src/governance/{02-decision,04-risk,10-stakeholder}
rm -rf src/governance/{12-culture-capability,14-improvement}
rm -rf src/governance/{15-economic,16-psychological,17-sociological}
rm -rf src/governance/{19-evolutionary,21-ecological,22-aesthetic}
rm -rf src/governance/{24-registry,25-principles,28-tests}
rm -rf src/governance/{30-agents,30-integration,32-rules}
rm -rf src/governance/{33-common,34-config,35-scripts}
rm -rf src/governance/{36-modules,37-behavior-contracts,38-sbom}
rm -rf src/governance/{60-contracts,80-feedback}
rm -rf src/governance/{ci,dimensions,index,packages}
```

### Phase 6: Verification and Documentation

**Duration:** 1-2 hours

#### Step 1: Update Import Paths

Run automated import path updater:

```bash
node scripts/ops/migration/update-import-paths.js
```

#### Step 2: Run Tests

```bash
npm test
npm run build
```

#### Step 3: Verify Structure

```bash
tree -L 4 -I 'node_modules|.git' > docs/directory-tree-after.txt
npx madge --circular --extensions ts,js,py src/ > docs/dependency-graph-after.txt
```

#### Step 4: Update Documentation

- Update README.md with new structure
- Update CONTRIBUTING.md with new paths
- Create migration report
- Update API documentation

#### Step 5: Commit Changes

```bash
git add .
git commit -m "refactor: complete subdirectory restructuring

- Standardized all subdirectories to kebab-case
- Merged duplicate and overlapping directories
- Removed legacy and scratch directories
- Improved logical organization
- Updated all import paths
- Verified builds and tests pass

Closes #[issue-number]"
```

## Validation Rules

### Naming Conventions

- **Format:** kebab-case only
- **Max Depth:** 4 levels
- **Prohibited:** _scratch,_legacy, temp, tmp, old, backup

### Structure Requirements

- No empty directories
- No orphaned files
- Consistent naming throughout
- Clear separation of concerns

### Import Requirements

- No absolute paths
- Use path aliases
- No circular dependencies

## Rollback Procedure

If issues arise:

```bash
# Reset to backup
git reset --hard HEAD
git checkout subdirectory-backup-<timestamp>
git clean -fd

# Reinstall dependencies
npm install

# Rebuild
npm run build
```

## Success Criteria

### Structure

- ✅ All directories follow kebab-case naming
- ✅ No duplicate or overlapping directories
- ✅ Clear separation of concerns
- ✅ Maximum 3-4 levels of nesting

### Functionality

- ✅ All tests pass
- ✅ Build succeeds without errors
- ✅ No broken imports
- ✅ CI/CD pipelines work

### Documentation

- ✅ Updated README files
- ✅ Migration guide created
- ✅ New directory tree documented
- ✅ Import path guide updated

## Troubleshooting

### Common Issues

**Issue:** Import paths not resolving
**Solution:** Run `npm run update-imports` or manually update tsconfig.json paths

**Issue:** Tests failing after migration
**Solution:** Update test file paths in jest.config.js

**Issue:** CI/CD pipeline failures
**Solution:** Update workflow files in .github/workflows/

**Issue:** Missing files after migration
**Solution:** Check backup tag and restore specific files

## Next Steps

After completing subdirectory restructuring:

1. **Update CI/CD Pipelines:** Ensure all workflows reference new paths
2. **Update Documentation:** Reflect new structure in all docs
3. **Team Communication:** Notify team of new structure
4. **Monitor:** Watch for issues in first few days
5. **Iterate:** Make adjustments based on feedback

## References

- [Parent Restructure Spec](../config/machinenativeops-restructure-spec.json)
- [Subdirectory Restructure Spec](../config/subdirectory-restructure-spec.json)
- [Naming Conventions](../docs/NAMING_CONVENTIONS.md)
- [Architecture Guide](../docs/ARCHITECTURE_DETAILED.md)

## Support

For questions or issues:

- Create an issue in the repository
- Contact the architecture team
- Refer to the troubleshooting section above
