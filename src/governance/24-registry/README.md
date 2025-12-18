# 24-registry - Registry Governance

> **Dimension**: 24  
> **Status**: ACTIVE  
> **Last Updated**: 2025-12-15

## 🎯 Purpose

Central registry for governance modules, services, and plugins, ensuring every
component is discoverable, versioned, and policy-aligned.

## 📋 Scope

- Maintain registry definitions for modules and services
- Track contracts and plugins with ownership and version metadata
- Enforce schema alignment via `schema.json` and `dimension.yaml`

## 📁 Structure

```
24-registry/
├── dimension.yaml            # Dimension metadata
├── README.md                 # This file
├── module-A.yaml             # Example module registration
├── module-contracts-l1.yaml  # Contract registry entries
├── services.yaml             # Service registry records
├── plugins/                  # Plugin registrations
└── schema.json               # Registry schema
```

## 🚀 Quick Use

- Update registry entries in `module-*.yaml` and `services.yaml` when adding or
  changing components.
- Keep `dimension.yaml` and `schema.json` in sync with registry field changes.
- Place plugin definitions under `plugins/` to enable discovery by automation
  pipelines.
