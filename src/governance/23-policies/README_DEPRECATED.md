# Deprecated: policies/

**This directory has been deprecated and consolidated into `23-policies/`.**

## Migration Guide

All policy files from this directory have been moved to:

- **New Location**: `governance/23-policies/`
- **Purpose**: Centralized policy management within the numbered governance
  dimension structure

## Why This Change?

To resolve duplicate directory issues and align with the governance
restructuring:

- Eliminates confusion between root-level `policies/` and `23-policies/`
- Provides single source of truth for all governance policies
- Aligns with the numbered dimension structure

## What to Do

1. Update all references from `governance/policies/` to
   `governance/23-policies/`
2. Update import paths in Python code
3. Update file paths in YAML configurations
4. Update documentation links

## Backward Compatibility

The original files remain available in:

- `governance/23-policies/` - **Use this location going forward**

---

**Deprecated**: 2025-12-12 **Migration Deadline**: 2026-03-31
