# Phase 3-5 Implementation Plan: Complete Restructuring Guide

## Overview

This document provides a detailed, step-by-step implementation guide for completing Phases 3-5 of the MachineNativeOps directory restructuring project. It serves as a roadmap for continuing work initiated in Phase 0-2.

## Phase 3: Duplicate Directory Consolidation

### Objective

Merge duplicate/redundant directories that exist at the root level and within src/ into unified, consistent locations.

### 3.1 AI Module Consolidation

**Current State**:

- `ai/` (root level) - contains AI components
- `island-ai/` (root level) - contains multi-agent AI system
- `src/ai/` (destination) - prepared target directory

**Action Steps**:

```bash
# Step 1: Analyze dependencies
grep -r "from ai import\|import ai\|require.*ai" src/ > ai_dependencies.txt
grep -r "from island-ai\|import island-ai\|require.*island-ai" src/ > island_ai_dependencies.txt

# Step 2: Backup and merge
mkdir -p src/ai/agents src/ai/models src/ai/pipelines
rsync -av ai/* src/ai/
rsync -av island-ai/src/* src/ai/
rsync -av island-ai/dist/* src/ai/dist/

# Step 3: Update package.json references
find src/ai -name "package.json" -exec sed -i 's|"ai/|"../|g' {} \;

# Step 4: Update imports in codebase
find . -name "*.py" -o -name "*.ts" -o -name "*.js" | \
  xargs sed -i \
    -e 's|from ai import|from src.ai import|g' \
    -e 's|from island-ai|from src.ai|g' \
    -e 's|require.*ai/|require("../src/ai/|g'

# Step 5: Git operations
git rm -r ai/ island-ai/
git add src/ai/
git commit -m "refactor(phase3): consolidate ai/ and island-ai/ into src/ai/"
```

**Validation**:

- [ ] No remaining references to ai/ or island-ai/ (except in src/ai/)
- [ ] All imports updated
- [ ] Build passes
- [ ] Tests still pass

### 3.2 Infrastructure Consolidation

**Current State**:

- `infra/` (root level) - legacy infrastructure code
- `infrastructure/` (root level) - newer infrastructure code
- `src/autonomous/infrastructure/` (destination) - prepared target

**Action Steps**:

```bash
# Analyze overlaps
diff -qr infra/ infrastructure/ > infra_diff.txt

# Merge infra into autonomous/infrastructure
rsync -av infra/infrastructure/* src/autonomous/infrastructure/ --backup-dir=backup-infra-old
rsync -av infrastructure/* src/autonomous/infrastructure/ --backup-dir=backup-infrastructure-old

# Update references in Kubernetes manifests, Terraform, etc.
find . -name "*.yaml" -o -name "*.yml" -o -name "*.tf" | \
  xargs sed -i \
    -e 's|infra/|src/autonomous/infrastructure/|g' \
    -e 's|infrastructure/|src/autonomous/infrastructure/|g'

# Commit
git rm -r infra/ infrastructure/
git add src/autonomous/infrastructure/
git commit -m "refactor(phase3): consolidate infra/ and infrastructure/ into src/autonomous/infrastructure/"
```

**Validation**:

- [ ] All Terraform/IaC files updated
- [ ] Kubernetes manifests paths corrected
- [ ] No orphaned references

### 3.3 Deployment Consolidation

**Current State**:

- `deployment/` (root) - deployment scripts
- `deploy/` (root) - Kubernetes deployment configs
- `src/autonomous/deployment/` (destination) - target

**Action Steps**:

```bash
# Merge deployment systems
rsync -av deployment/* src/autonomous/deployment/
rsync -av deploy/k8s/* src/autonomous/deployment/k8s/

# Update deployment references
find . -name "*.sh" -o -name "*.py" | \
  xargs sed -i \
    -e 's|deployment/|src/autonomous/deployment/|g' \
    -e 's|deploy/|src/autonomous/deployment/|g'

# Commit
git rm -r deployment/ deploy/
git add src/autonomous/deployment/
git commit -m "refactor(phase3): consolidate deployment/ and deploy/ into src/autonomous/deployment/"
```

### 3.4 Configuration Consolidation

**Current State**:

- `.config/` - legacy dotfile configs
- `config/` - newer central config
- `.devcontainer/` - dev container configs

**Action Steps**:

```bash
# Consolidate all configs
rsync -av .config/* config/ --exclude-from=ignore-patterns.txt
rsync -av .devcontainer/* config/dev/

# Update references in all files
find . -name "*.yaml" -o -name "*.json" -o -name "*.py" -o -name "*.ts" -o -name "*.sh" | \
  xargs sed -i \
    -e 's|\.config/|config/|g' \
    -e 's|\.devcontainer|config/dev|g'

# Update .gitignore
echo ".config/" >> .gitignore
echo ".devcontainer/" >> .gitignore

# Commit
git rm -r .config/ .devcontainer/
git add config/
git add .gitignore
git commit -m "refactor(phase3): consolidate configs into config/ directory"
```

---

## Phase 4: Import Path Updates

### Objective

Update all code references throughout the project to use new, consistent paths.

### 4.1 TypeScript/JavaScript Updates

```bash
# Update @synergymesh to @machinenativeops
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) | \
  xargs sed -i \
    -e 's/@synergymesh\//@machinenativeops\//g' \
    -e 's|from @synergymesh/|from @machinenativeops/|g' \
    -e "s|from 'synergymesh|from '@machinenativeops|g" \
    -e 's|require.*synergymesh|require("@machinenativeops|g'

# Update relative paths in src/
find src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) | \
  xargs sed -i \
    -e 's|\.\.\/\.\.\/ai/|..\/..\/src\/ai\/|g' \
    -e 's|\.\.\/\.\.\/core/|..\/..\/src\/core\/|g' \
    -e 's|\.\.\/\.\.\/governance/|..\/..\/src\/governance\/|g'

git add src/ && git commit -m "refactor(phase4): update TypeScript/JavaScript imports to new paths"
```

### 4.2 Python Updates

```bash
# Update import statements
find . -type f -name "*.py" | \
  xargs sed -i \
    -e 's|^from ai |from src.ai |g' \
    -e 's|^from core |from src.core |g' \
    -e 's|^from governance |from src.governance |g' \
    -e 's|^from autonomous |from src.autonomous |g' \
    -e 's|^from synergymesh|from machinenativeops|g'

git add . && git commit -m "refactor(phase4): update Python imports to new paths"
```

### 4.3 Configuration File References

```bash
# Update paths in YAML/JSON configs
find config -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) | \
  xargs sed -i \
    -e 's|ai/|src/ai/|g' \
    -e 's|core/|src/core/|g' \
    -e 's|governance/|src/governance/|g' \
    -e 's|autonomous/|src/autonomous/|g'

git add config/ && git commit -m "refactor(phase4): update config file references"
```

---

## Phase 5: CI/CD & Final Verification

### Objective

Update automation pipelines and validate the entire restructure.

### 5.1 GitHub Actions Workflow Updates

```bash
# Update .github/workflows files
find .github/workflows -type f \( -name "*.yaml" -o -name "*.yml" \) | while read file; do
  sed -i \
    -e 's|ai/|src/ai/|g' \
    -e 's|deployment/|src/autonomous/deployment/|g' \
    -e 's|\.config/|config/|g' \
    "$file"
done

# Validate YAML syntax
find .github/workflows -name "*.yaml" -o -name "*.yml" | \
  xargs yamllint

git add .github/ && git commit -m "ci(phase5): update workflow paths"
```

### 5.2 Build & Test Validation

```bash
# Run comprehensive validation
echo "=== Building Project ===" && npm run build
echo "=== Running Tests ===" && npm test -- --passWithNoTests
echo "=== Linting ===" && npm run lint
echo "=== Type Checking ===" && npm run type-check 2>/dev/null || true

# Generate dependency graph
npx madge --circular --extensions ts,js src/ > dependency-report.txt

# Report results
git add dependency-report.txt && git commit -m "docs(phase5): add final dependency analysis"
```

### 5.3 Final Verification Checklist

```bash
#!/bin/bash
# verify-restructure.sh

echo "=== Final Restructuring Verification ==="
echo ""

checks_passed=0
checks_total=0

check_dir() {
  checks_total=$((checks_total + 1))
  if [ -d "$1" ]; then
    echo "✅ Directory exists: $1"
    checks_passed=$((checks_passed + 1))
  else
    echo "❌ Missing directory: $1"
  fi
}

check_no_dir() {
  checks_total=$((checks_total + 1))
  if [ ! -d "$1" ]; then
    echo "✅ Removed duplicate: $1"
    checks_passed=$((checks_passed + 1))
  else
    echo "❌ Still exists (should be removed): $1"
  fi
}

# Check standard directories exist
check_dir "src/ai"
check_dir "src/core"
check_dir "src/governance"
check_dir "src/autonomous/infrastructure"
check_dir "src/autonomous/deployment"
check_dir "config/dev"
check_dir "config/staging"
check_dir "config/prod"
check_dir "scripts/dev"
check_dir "scripts/ci"
check_dir "scripts/ops"

# Check duplicates removed
check_no_dir "ai"
check_no_dir "island-ai"
check_no_dir "infra"
check_no_dir "infrastructure"
check_no_dir "deployment"
check_no_dir "deploy"
check_no_dir ".config"
check_no_dir ".devcontainer"

# Check key files
checks_total=$((checks_total + 1))
if grep -q "name: \"MachineNativeOps\"" machinenativeops.yaml; then
  echo "✅ Config file name updated"
  checks_passed=$((checks_passed + 1))
else
  echo "❌ Config file name not updated"
fi

echo ""
echo "Summary: $checks_passed / $checks_total checks passed"

if [ $checks_passed -eq $checks_total ]; then
  echo "🎉 All verification checks passed!"
  exit 0
else
  echo "⚠️ Some checks failed - review above"
  exit 1
fi
```

### 5.4 Documentation Updates

```bash
# Update README.md with new structure
cat >> README.md << 'EOF'

## Project Structure (Post-Restructure)

The MachineNativeOps project follows a standardized directory layout:

- **src/** - Application source code
  - ai/ - AI decision engine and ML pipelines
  - core/ - Core orchestration service
  - governance/ - Policy enforcement
  - autonomous/ - Infrastructure automation
- **config/** - Centralized configuration
  - dev/, staging/, prod/ - Environment-specific configs
- **scripts/** - Automation scripts
  - dev/, ci/, ops/, governance/ - Script categories
- **governance/** - Governance content hub
- **examples/** - Educational examples
- **docs/** - Project documentation

For more details, see CONTRIBUTING.md
EOF

git add README.md && git commit -m "docs(phase5): update README with new structure"
```

---

## Summary of Changes

| Phase | What | Commits | Files | Status |
|-------|------|---------|-------|--------|
| 3 | Merge duplicates | 4-5 | 50+ | Pending |
| 4 | Update imports | 3-4 | 200+ | Pending |
| 5 | CI/CD validation | 3-4 | 30+ | Pending |
| **TOTAL** | **Complete restructure** | **~10-15** | **~2,952** | **Pending** |

## Rollback Procedure

At any point, revert to the backup:

```bash
git reset --hard pre-restructure-backup-20251218-041816
```

---

**Last Updated**: 2025-12-18
**Status**: Ready for Phase 3 implementation
**Next Step**: Execute Phase 3 consolidation
