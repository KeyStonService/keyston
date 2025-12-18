# Deprecated: schemas/

**This directory has been deprecated and consolidated into `31-schemas/`.**

## Migration Guide

All schema files from this directory have been moved to:

- **New Location**: `governance/31-schemas/`
- **Purpose**: Centralized schema management within the numbered governance
  dimension structure

## Why This Change?

To resolve duplicate directory issues and align with the governance
restructuring:

- Eliminates confusion between root-level `schemas/` and `31-schemas/`
- Provides single source of truth for all governance schemas
- Aligns with the numbered dimension structure

## What to Do

1. Update all references from `governance/schemas/` to `governance/31-schemas/`
2. Update import paths in Python code
3. Update file paths in YAML configurations
4. Update documentation links

## Backward Compatibility

The original files remain available in:

- `governance/31-schemas/` - **Use this location going forward**

---

**Deprecated**: 2025-12-12 **Migration Deadline**: 2026-03-31
