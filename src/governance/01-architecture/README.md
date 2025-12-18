# 🏛️ 架構治理 | Architecture Governance (Skeleton #1: architecture-stability)

> Aligns governance with the Architecture Stability skeleton rules, invariants, and layer boundaries.

## 📋 Overview

Architecture Governance enforces:

- Layered isolation and one-way dependencies (per skeleton #1 invariants)
- Core-to-platform-to-services guardrails mapped to SynergyMesh layers
- Architecture linting and exemptions tracking
- Integration of autonomous implementation (`automation/autonomous/architecture-stability`) with governance source-of-truth configs

## 📁 Structure

```
01-architecture/
├── config/
│   ├── architecture-policy.yaml   # Skeleton #1 governance policy & source-of-truth mapping
│   ├── layers-domains.yaml        # Layer/domain definitions and validation rules
│   └── api-policy.yaml            # Legacy API policy (kept for backward references; deprecation review scheduled for 2026-03-31)
├── schemas/
│   └── architecture-schema.json   # Architecture metadata schema
├── governance-standards.md        # Bilingual governance standards
├── governance-framework.yaml      # Integrated governance dimensions
└── README.md                      # This file
```

## 🔗 Skeleton #1 (Architecture Stability) Links

All paths below use the `repo://` prefix to denote repository-root-relative references.

- **Governance Source of Truth** (`repo://` prefix): `repo://unmanned-engineer-ceo/80-skeleton-configs/01-architecture-stability/`
  - Invariants: `repo://unmanned-engineer-ceo/80-skeleton-configs/01-architecture-stability/docs/invariants.md`
  - Layer rules: `repo://unmanned-engineer-ceo/80-skeleton-configs/01-architecture-stability/docs/layering-rules.md`
  - Dependency rules: `repo://unmanned-engineer-ceo/80-skeleton-configs/01-architecture-stability/docs/dependency-rules.md`
  - Linter config: `repo://unmanned-engineer-ceo/80-skeleton-configs/01-architecture-stability/tools/arch-lint.config.yml`
  - Linter implementation: `repo://unmanned-engineer-ceo/80-skeleton-configs/01-architecture-stability/tools/arch-lint.ts`
- **Implementation (operational layer)**: `repo://automation/autonomous/architecture-stability/` (Layer 0 runtime + ROS2 flight control)

## 🎯 Governance Scope

- Enforce skeleton #1 guardrails across SynergyMesh layers and domains (see `config/layers-domains.yaml`)
- Validate architecture changes against invariants and dependency matrix
- Coordinate with CI agents that run Architecture Lint using the skeleton configs

## ✅ Status

- Governance domain: **Active**
- Skeleton alignment: **architecture-stability (production)**
- Last Updated: 2025-12-16
