# CI/CD Hardening Recommendations

## 📋 Overview

This document outlines recommendations for addressing the GitHub Actions cost
issues identified in the repository. These are pre-existing infrastructure
concerns that should be addressed in a dedicated CI/CD optimization effort.

**Status**: 🔴 Action Required  
**Priority**: 🔥 Critical - Cost Impact  
**Estimated Effort**: 48 hours

---

## 🚨 Current Issues

### 1. Excessive Workflow Count

- **Current**: 47 workflow files
- **Problem**: Too many workflows increase maintenance burden and trigger
  complexity
- **Impact**: High compute minutes consumption

### 2. Trigger Proliferation

- **Problem**: Workflows trigger on every push, commit, and file change
- **Impact**: Unnecessary runs consuming minutes
- **Example**: CodeQL, full-repo-scan running on all branches

### 3. Missing Cost Protection

- **Problem**: No timeouts or concurrency controls
- **Impact**: Long-running jobs and parallel runs multiply costs
- **Missing**:
  - `timeout-minutes` limits
  - `concurrency` groups
  - `cancel-in-progress` flags

### 4. Self-Triggering Loops

- **Problem**: Some workflows trigger other workflows
- **Impact**: Infinite loop scenarios possible
- **Example**: auto-comment, auto-fix workflows

### 5. Failed Jobs Retry Indefinitely

- **Problem**: No retry limits on failed jobs
- **Impact**: Failed jobs consume minutes repeatedly

### 6. Non-Blocking Errors

- **Problem**: Jobs show green status despite internal errors
- **Impact**: Hidden problems continue consuming resources

---

## ✅ Required Deliverables

### Deliverable 1: Fix All CI Errors

**Goal**: Achieve 100% green status with zero annotation errors

**Actions**:

- [ ] Fix all CodeQL configuration errors
- [ ] Resolve repo scan syntax issues
- [ ] Fix github-script errors
- [ ] Correct auto-comment issues
- [ ] Fix devcontainer.json syntax errors
- [ ] Fix settings.json syntax errors

**Validation**: All workflows run clean on main branch

### Deliverable 2: Stop Unnecessary Triggers

**Goal**: Reduce workflow runs by 80%

**Actions**:

- [ ] Limit expensive scans to:
  - `pull_request` events only
  - `push` to `main` branch only
  - Manual `workflow_dispatch` only
- [ ] Remove cron triggers from expensive jobs
- [ ] Disable self-triggering workflows
- [ ] Remove `on: [push]` from scanning workflows

**Validation**: Document trigger conditions for each workflow

### Deliverable 3: Add Cost Protection Mechanisms

**Goal**: Prevent runaway costs

**Template to add to ALL workflows**:

```yaml
name: Workflow Name

on:
  pull_request:
  push:
    branches: [main]
  workflow_dispatch:

# Add this to EVERY workflow
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 5 # Adjust per job needs

    steps:
      # ... existing steps
```

**Specific Timeout Recommendations**:

- Linting jobs: 3 minutes
- Test jobs: 10 minutes
- Build jobs: 15 minutes
- Deploy jobs: 20 minutes
- Security scans: 15 minutes
- Full repo scans: 10 minutes

**Actions**:

- [ ] Add `concurrency` group to all workflows
- [ ] Add `cancel-in-progress: true` to all workflows
- [ ] Add `timeout-minutes` to all jobs
- [ ] Review and adjust timeout values per job type

**Validation**: Test that concurrent runs cancel properly

### Deliverable 4: Implement Fail-Fast Rules

**Goal**: Stop workflows immediately on errors

**Actions**:

- [ ] Change full-repo-scan to `exit 1` on errors
- [ ] Add `set -e` to all shell scripts
- [ ] Use `--max-warnings 0` for linters
- [ ] Remove `continue-on-error: true` unless absolutely necessary
- [ ] Add explicit error checking to github-scripts

**Example**:

```yaml
- name: Full Repo Scan
  run: |
    set -e  # Exit on any error
    ./scan-script.sh
    if [ $? -ne 0 ]; then
      echo "❌ Scan failed"
      exit 1
    fi
```

**Validation**: Verify that failures properly mark workflow as failed

### Deliverable 5: CI Summary Dashboard

**Goal**: Daily visibility into CI costs and performance

**Actions**:

- [ ] Create workflow that generates daily summary
- [ ] Track per-workflow:
  - Trigger count
  - Total runtime
  - Success/failure rate
  - Estimated cost
- [ ] Post summary as issue comment or to dashboard
- [ ] Alert on anomalies (sudden increases)

**Example Implementation**:

```yaml
name: CI Cost Dashboard

on:
  schedule:
    - cron: '0 9 * * *' # Daily at 9 AM
  workflow_dispatch:

jobs:
  generate-report:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - name: Generate CI Summary
        uses: actions/github-script@v7
        with:
          script: |
            // Fetch workflow runs from last 24 hours
            // Calculate costs
            // Generate report
            // Post as issue comment
```

---

## 🚑 Immediate Stop-Gap Measures

**To implement RIGHT NOW to stop the bleeding**:

### Option 1: Disable Expensive Workflows (Recommended)

```bash
# Disable these workflows immediately:
# 1. CodeQL (unless required by policy)
# 2. project-self-awareness-nightly.yml
# 3. project-self-awareness.yml
# 4. All auto-* workflows except critical ones
# 5. All *-cd.yml workflows in non-production branches
```

Navigate to: `Settings → Actions → Workflows` and disable selectively.

### Option 2: Branch Protection Rules

Add required status checks ONLY for:

- Validation
- Unit Tests
- Security Gate (PR only)

Remove requirements for:

- Full repo scans
- CodeQL (run weekly instead)
- Nightly jobs
- Auto-update jobs

### Option 3: Reduce Runner Minutes Quota

Set monthly limits in organization settings to prevent runaway costs.

---

## 📊 Workflow Audit Results

### High-Cost Workflows (Prioritize These)

1. **codeql.yml** - Runs on every push, very expensive
2. **project-self-awareness-nightly.yml** - Runs daily
3. **project-self-awareness.yml** - Runs frequently
4. **mndoc-knowledge-graph.yml** - Full repo scan
5. **osv-scanner.yml** - Security scan on all commits

### Medium-Cost Workflows

1. **auto-update-knowledge-graph.yml**
2. **autonomous-ci-guardian.yml**
3. **ci-failure-auto-solution.yml**
4. **contracts-cd.yml**
5. **core-services-ci.yml**

### Recommended Actions Per Workflow

| Workflow                           | Current Trigger    | Recommended Trigger    | Expected Savings |
| ---------------------------------- | ------------------ | ---------------------- | ---------------- |
| codeql.yml                         | push, pull_request | weekly cron, main only | 90%              |
| project-self-awareness-nightly.yml | daily cron         | weekly cron            | 85%              |
| osv-scanner.yml                    | push               | pull_request only      | 80%              |
| mndoc-knowledge-graph.yml          | push               | main only, manual      | 75%              |
| auto-update-knowledge-graph.yml    | push               | main only              | 70%              |

---

## 🎯 Success Metrics

After implementing CI hardening, you should see:

- [ ] **Cost Reduction**: 80-90% reduction in GitHub Actions minutes
- [ ] **Workflow Runs**: 50-70% fewer workflow runs per week
- [ ] **Build Times**: Faster feedback (failed jobs stop immediately)
- [ ] **Visibility**: Daily cost reports available
- [ ] **Reliability**: No more infinite loop scenarios

---

## 📋 Implementation Checklist

### Week 1: Critical Fixes

- [ ] Day 1: Disable expensive workflows immediately
- [ ] Day 2: Add timeout-minutes to all workflows
- [ ] Day 3: Add concurrency controls to all workflows
- [ ] Day 4: Fix trigger conditions (remove unnecessary triggers)
- [ ] Day 5: Test and validate changes

### Week 2: Optimization

- [ ] Day 1: Implement fail-fast rules
- [ ] Day 2: Create CI cost dashboard
- [ ] Day 3: Document all workflow triggers
- [ ] Day 4: Re-enable workflows with new protections
- [ ] Day 5: Monitor and fine-tune

---

## 🔧 Code Templates

### Standard Workflow Header

```yaml
name: Workflow Name

on:
  pull_request:
    paths:
      - 'relevant/**' # Only trigger on relevant changes
  push:
    branches: [main]
  workflow_dispatch:

# Cost protection
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Global defaults
defaults:
  run:
    shell: bash

jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4

      - name: Run Task
        run: |
          set -e  # Fail fast
          # ... commands
```

### Conditional Expensive Job

```yaml
expensive-scan:
  # Only run on main or when manually triggered
  if:
    github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'
  runs-on: ubuntu-latest
  timeout-minutes: 15

  steps:
    - name: Run Expensive Scan
      run: ./expensive-scan.sh
```

---

## 📞 Next Steps

1. **Create Issue**: File a new issue titled "CI/CD Hardening - Cost Reduction"
2. **Assign Owner**: Assign to DevOps/Infrastructure team
3. **Set Deadline**: Target completion within 1 week
4. **Track Progress**: Use this document as acceptance criteria

---

## 📚 References

- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions)
- [Concurrency in Workflows](https://docs.github.com/en/actions/using-jobs/using-concurrency)
- [Billing for GitHub Actions](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

---

**Document Status**: 🟡 Draft - Ready for Implementation  
**Last Updated**: 2025-12-05  
**Author**: CI/CD Optimization Team
