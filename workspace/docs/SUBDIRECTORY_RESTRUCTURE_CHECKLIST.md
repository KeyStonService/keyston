# Subdirectory Restructuring - Quick Reference Checklist

## Pre-Migration Checklist

- [ ] Review [Subdirectory Restructure Spec](../config/subdirectory-restructure-spec.json)
- [ ] Review [Migration Guide](./SUBDIRECTORY_RESTRUCTURE_GUIDE.md)
- [ ] Ensure working directory is clean (`git status`)
- [ ] Ensure all changes are committed
- [ ] Notify team of upcoming restructure

## Phase 1: Preparation (30 min)

- [ ] Create feature branch

  ```bash
  git checkout -b refactor/subdirectory-restructure
  ```

- [ ] Create backup tag

  ```bash
  git tag -a subdirectory-backup-$(date +%Y%m%d-%H%M%S) -m "Backup before subdirectory restructure"
  git push origin --tags
  ```

- [ ] Generate directory tree snapshot

  ```bash
  tree -L 4 -I 'node_modules|.git' > docs/directory-tree-before.txt
  ```

- [ ] Run dependency analysis

  ```bash
  npx madge --circular --extensions ts,js,py src/ > docs/dependency-graph-before.txt
  ```

- [ ] Document import paths

  ```bash
  grep -r "from.*import" src/ > docs/import-paths-before.txt
  grep -r "import.*from" src/ >> docs/import-paths-before.txt
  ```

## Phase 2: src/ Restructuring (2-3 hours)

### Create New Structure

- [ ] Create AI subdirectories

  ```bash
  mkdir -p src/ai/{inference,training}
  ```

- [ ] Create Core subdirectories

  ```bash
  mkdir -p src/core/{engine,plugins,contracts,monitoring,safety,integrations}
  ```

- [ ] Create Autonomous subdirectories

  ```bash
  mkdir -p src/autonomous/self-healing
  ```

- [ ] Create Services subdirectories

  ```bash
  mkdir -p src/services/{api-gateway,auth,config-management,observability}
  ```

- [ ] Create Web subdirectories

  ```bash
  mkdir -p src/web/{admin,api,client,shared}
  ```

- [ ] Create Shared subdirectories

  ```bash
  mkdir -p src/shared/{types,utils,constants}
  ```

### Merge and Consolidate

#### AI Components

- [ ] Remove `src/ai/__tests__/`

#### Core Components

- [ ] Merge execution engines to `src/core/engine/`
- [ ] Merge plugins to `src/core/plugins/`
- [ ] Merge contracts to `src/core/contracts/`
- [ ] Merge monitoring to `src/core/monitoring/`
- [ ] Merge safety mechanisms to `src/core/safety/`
- [ ] Merge integrations to `src/core/integrations/`
- [ ] Remove deprecated core directories

#### Autonomous Components

- [ ] Merge infrastructure components
- [ ] Merge deployment components
- [ ] Merge agent components
- [ ] Remove `src/autonomous/core/`

#### Services and Web

- [ ] Merge services directories
- [ ] Merge web application directories
- [ ] Move schemas to `src/shared/schemas/`

### Clean Up

- [ ] Remove deprecated src/ root directories
- [ ] Move `src/governance/` to root `governance/`
- [ ] Move `src/tests/` to root `tests/`
- [ ] Move templates to config

### Verification

- [ ] Verify directory structure
- [ ] Check for orphaned files
- [ ] Commit changes

  ```bash
  git add src/
  git commit -m "refactor(src): restructure subdirectories"
  ```

## Phase 3: config/ Reorganization (1-2 hours)

### Create Structure

- [ ] Create environment directories

  ```bash
  mkdir -p config/environments/{dev,staging,prod}
  ```

- [ ] Create organizational directories

  ```bash
  mkdir -p config/{ci-cd,monitoring,security,governance,build,linting,system}
  mkdir -p config/docker/{compose,templates}
  ```

### Move Files

- [ ] Move environment files to `config/environments/`
- [ ] Move CI/CD configs to `config/ci-cd/`
- [ ] Move Docker configs to `config/docker/`
- [ ] Move monitoring configs to `config/monitoring/`
- [ ] Move security configs to `config/security/`
- [ ] Move governance configs to `config/governance/`
- [ ] Move build configs to `config/build/`
- [ ] Move linting configs to `config/linting/`
- [ ] Move system configs to `config/system/`

### Clean Up

- [ ] Remove deprecated config files
- [ ] Remove deprecated config directories
- [ ] Verify no orphaned files

### Verification

- [ ] Check config references in code
- [ ] Commit changes

  ```bash
  git add config/
  git commit -m "refactor(config): reorganize configuration files"
  ```

## Phase 4: scripts/ Cleanup (1 hour)

### Create Structure

- [ ] Create script directories

  ```bash
  mkdir -p scripts/{dev,deployment,automation,utils}
  mkdir -p scripts/governance/{naming,migration}
  mkdir -p scripts/deployment/k8s
  ```

### Move Scripts

- [ ] Move development scripts to `scripts/dev/`
- [ ] Move deployment scripts to `scripts/deployment/`
- [ ] Move governance scripts to `scripts/governance/`
- [ ] Move automation scripts to `scripts/automation/`
- [ ] Move utility scripts to `scripts/utils/`

### Clean Up

- [ ] Remove deprecated script files
- [ ] Remove deprecated script directories
- [ ] Move hooks to `.github/hooks/`

### Verification

- [ ] Check script references in CI/CD
- [ ] Commit changes

  ```bash
  git add scripts/
  git commit -m "refactor(scripts): reorganize automation scripts"
  ```

## Phase 5: governance/ Migration (2-3 hours)

### Create Structure

- [ ] Create governance directories

  ```bash
  mkdir -p governance/{policies,strategies,architecture,compliance}
  mkdir -p governance/{security,processes,metrics,tools}
  mkdir -p governance/{docs,templates,schemas,automation}
  ```

### Merge Directories

- [ ] Merge policies directories
- [ ] Merge strategies directories
- [ ] Merge architecture directories
- [ ] Merge compliance directories
- [ ] Merge security directories
- [ ] Merge processes directories
- [ ] Merge metrics directories
- [ ] Merge tools directories
- [ ] Merge docs directories
- [ ] Merge templates directories
- [ ] Merge schemas directories
- [ ] Merge automation directories

### Clean Up

- [ ] Remove deprecated governance directories
- [ ] Remove legacy and scratch directories

### Verification

- [ ] Check governance references
- [ ] Commit changes

  ```bash
  git add governance/
  git commit -m "refactor(governance): consolidate governance structure"
  ```

## Phase 6: Verification and Documentation (1-2 hours)

### Update Code

- [ ] Update import paths in TypeScript/JavaScript files
- [ ] Update import paths in Python files
- [ ] Update config references
- [ ] Update script references

### Run Tests

- [ ] Run unit tests

  ```bash
  npm test
  ```

- [ ] Run build

  ```bash
  npm run build
  ```

- [ ] Check for circular dependencies

  ```bash
  npx madge --circular --extensions ts,js,py src/
  ```

### Generate Documentation

- [ ] Generate new directory tree

  ```bash
  tree -L 4 -I 'node_modules|.git' > docs/directory-tree-after.txt
  ```

- [ ] Generate new dependency graph

  ```bash
  npx madge --circular --extensions ts,js,py src/ > docs/dependency-graph-after.txt
  ```

- [ ] Create migration report
- [ ] Update README.md
- [ ] Update CONTRIBUTING.md
- [ ] Update API documentation

### Final Commit

- [ ] Review all changes

  ```bash
  git status
  git diff --stat
  ```

- [ ] Commit final changes

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

- [ ] Push to remote

  ```bash
  git push origin refactor/subdirectory-restructure
  ```

## Post-Migration Checklist

### Verification

- [ ] All tests pass
- [ ] Build succeeds without errors
- [ ] No broken imports
- [ ] CI/CD pipelines work
- [ ] No circular dependencies
- [ ] No empty directories
- [ ] All files follow naming conventions

### Documentation

- [ ] README updated
- [ ] CONTRIBUTING updated
- [ ] Migration report created
- [ ] Directory tree documented
- [ ] Import path guide updated

### Communication

- [ ] Create pull request
- [ ] Notify team of changes
- [ ] Update project documentation
- [ ] Schedule team walkthrough

### Monitoring

- [ ] Monitor CI/CD for issues
- [ ] Watch for import errors
- [ ] Check for missing files
- [ ] Gather team feedback

## Rollback Procedure (If Needed)

- [ ] Reset to backup tag

  ```bash
  git reset --hard HEAD
  git checkout subdirectory-backup-<timestamp>
  git clean -fd
  ```

- [ ] Reinstall dependencies

  ```bash
  npm install
  ```

- [ ] Rebuild

  ```bash
  npm run build
  ```

- [ ] Verify rollback successful

  ```bash
  npm test
  ```

## Success Criteria

### Structure ✅

- [ ] All directories follow kebab-case naming
- [ ] No duplicate or overlapping directories
- [ ] Clear separation of concerns
- [ ] Maximum 3-4 levels of nesting
- [ ] No scratch or legacy directories
- [ ] Logical grouping by function

### Functionality ✅

- [ ] All tests pass
- [ ] Build succeeds without errors
- [ ] No broken imports
- [ ] No circular dependencies
- [ ] CI/CD pipelines work
- [ ] All scripts executable

### Documentation ✅

- [ ] Updated README files
- [ ] Migration guide complete
- [ ] New directory tree documented
- [ ] Import path guide updated
- [ ] API documentation current
- [ ] Team notified

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Preparation | 30 min | 30 min |
| Phase 2: src/ Restructuring | 2-3 hours | 3-3.5 hours |
| Phase 3: config/ Reorganization | 1-2 hours | 4-5.5 hours |
| Phase 4: scripts/ Cleanup | 1 hour | 5-6.5 hours |
| Phase 5: governance/ Migration | 2-3 hours | 7-9.5 hours |
| Phase 6: Verification | 1-2 hours | 8-11.5 hours |
| **Total** | **8-11.5 hours** | |

## Notes

- Take breaks between phases
- Commit after each major phase
- Test frequently
- Keep backup tag accessible
- Document any issues encountered
- Update this checklist as needed

## References

- [Subdirectory Restructure Spec](../config/subdirectory-restructure-spec.json)
- [Migration Guide](./SUBDIRECTORY_RESTRUCTURE_GUIDE.md)
- [Parent Restructure Spec](../config/machinenativeops-restructure-spec.json)
