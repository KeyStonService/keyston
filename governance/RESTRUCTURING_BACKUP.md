# Governance Restructuring Backup Documentation

## Date: 2025-12-12

## Original Structure Issues

### Problem 1: Conflicting Directory Numbers

- 10-stakeholder (legacy) vs 10-policy (new layered framework)
- 20-information (legacy) vs 20-intent (new layered framework)
- 30-integration (legacy) vs 30-agents (new layered framework)

### Problem 2: Duplicate Audit Directories

- 07-audit (strategy layer - policy definition)
- 70-audit (feedback layer - audit trail)
- Both serve different purposes per GOVERNANCE_INTEGRATION_ARCHITECTURE.md

### Problem 3: Shared Resources Duplication

- policies/ (root) vs 23-policies/
- schemas/ (root) vs 31-schemas/
- scripts/ (root) vs 35-scripts/

## Resolution Strategy

### Keep Layered Framework (Primary Architecture)

These directories represent the new layered governance framework:

- 10-policy: Policy as Code Framework
- 20-intent: Intent-based Orchestration
- 30-agents: AI Agent Governance
- 60-contracts: Contract Registry
- 70-audit: Audit & Traceability (Feedback Layer)
- 80-feedback: Closed-Loop Feedback

### Rename Legacy Directories

To avoid conflicts, legacy dimensions are renamed:

- 10-stakeholder → 11-stakeholder (moved to next available number)
- 20-information → 21-information (moved to next available number, but
  21-ecological exists, so use different approach)
- 30-integration → Will consolidate into 30-agents or create coordination
  subdirectory

### Consolidate Shared Resources

- Move policies/ content into 23-policies/
- Move schemas/ content into 31-schemas/
- Move scripts/ content into 35-scripts/

### Preserve 07-audit

Keep 07-audit as it serves strategy-level audit (policy definition), distinct
from 70-audit (execution audit trail)

## Original File Inventory

### 10-stakeholder files

$(find 10-stakeholder -type f 2>/dev/null | wc -l) files

### 20-information files

$(find 20-information -type f 2>/dev/null | wc -l) files

### 30-integration files

$(find 30-integration -type f 2>/dev/null | wc -l) files

### Root-level shared resources

- policies/: $(find policies -type f 2>/dev/null | wc -l) files
- schemas/: $(find schemas -type f 2>/dev/null | wc -l) files
- scripts/: $(find scripts -type f 2>/dev/null | wc -l) files

## Migration Plan

1. Rename 10-stakeholder to avoid conflict with 10-policy
2. Consolidate 20-information content (minimal, just dimension.yaml and README)
3. Merge 30-integration functionality into 30-agents or create subdirectory
4. Move root-level policies/ into 23-policies/
5. Move root-level schemas/ into 31-schemas/
6. Move root-level scripts/ into 35-scripts/
7. Update all references in code and configuration
