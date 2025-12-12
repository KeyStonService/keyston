# Legacy Governance Dimensions

**This directory contains deprecated governance dimensions that conflicted with
the new layered framework.**

## Migrated Directories

### 10-stakeholder → Deprecated

- **Conflict**: Number 10 is now used by `10-policy` (Policy as Code Framework)
- **Content**: Stakeholder management, engagement plans, satisfaction surveys
- **New Location**: Content consolidated or deprecated
- **Reason**: The new layered governance architecture uses 10-policy for the
  Policy as Code framework

### 20-information → Deprecated

- **Conflict**: Number 20 is now used by `20-intent` (Intent-based
  Orchestration)
- **Content**: Minimal - only dimension.yaml and README
- **New Location**: Content deprecated or consolidated into other dimensions
- **Reason**: The new layered governance architecture uses 20-intent for
  Intent-based Orchestration

### 30-integration → Deprecated

- **Conflict**: Number 30 is now used by `30-agents` (AI Agent Governance)
- **Content**: Integration coordination, dependency maps, governance integration
  matrix
- **New Location**: Content consolidated into `30-agents/` coordination
  subdirectory or other relevant dimensions
- **Reason**: The new layered governance architecture uses 30-agents for AI
  Agent Governance

## New Layered Governance Framework

The SynergyMesh governance system has transitioned to a layered closed-loop
architecture:

```
10-policy     → Strategy Layer: Policy as Code Framework
20-intent     → Orchestration Layer: Intent-based Orchestration
30-agents     → Execution Layer: AI Agent Governance
39-automation → Execution Layer: Automation Engine
40-self-healing → Execution Layer: Self-Healing Framework
60-contracts  → Observability Layer: Contract Registry
70-audit      → Observability Layer: Audit & Traceability
80-feedback   → Feedback Layer: Closed-Loop Optimization
```

See
[GOVERNANCE_INTEGRATION_ARCHITECTURE.md](../GOVERNANCE_INTEGRATION_ARCHITECTURE.md)
for complete details.

## Migration Timeline

- **Deprecated**: 2025-12-12
- **Migration Deadline**: 2026-03-31
- **Status**: Files preserved for reference but not actively maintained

## What to Do

If you have references to these legacy dimensions:

1. **10-stakeholder**: Use dimensions/11-tools-systems or create stakeholder
   content in appropriate governance dimensions
2. **20-information**: Content was minimal, information architecture is now part
   of overall governance
3. **30-integration**: Integration coordination is now handled by `30-agents/`
   and the automation framework

## Questions?

Contact the SynergyMesh Governance Team for migration assistance.

---

**Last Updated**: 2025-12-12 **Maintained By**: Governance Restructuring
Initiative
