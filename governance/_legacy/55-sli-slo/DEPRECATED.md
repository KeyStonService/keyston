# DEPRECATED: 55-sli-slo

**Status**: Deprecated and moved to _legacy  
**Date**: 2025-12-12  
**Reason**: Naming inconsistency - standardized to `55-slo-sli`

## Migration Path

This directory has been **deprecated** and replaced by `55-slo-sli` to maintain
consistency with the governance naming convention.

### What Changed

- **Old name**: `55-sli-slo` (SLI/SLO)
- **New name**: `55-slo-sli` (SLO/SLI)
- **Location**: `governance/55-slo-sli/`

### Why the Change

The governance framework standardized on alphabetically ordered acronym pairs
(e.g., SLO/SLI instead of SLI/SLO) to ensure consistency across all dimensions.

This aligns with:
- `governance/index/dimensions.json` (uses `55-slo-sli`)
- `governance/dimensions/55-slo-sli/` (uses `55-slo-sli`)
- Standard naming conventions in the governance layer

### Migration Actions Taken

1. ✅ Copied all files from `55-sli-slo/` to `55-slo-sli/`
2. ✅ Updated metadata IDs in `dimension.yaml`
3. ✅ Updated `governance-map.yaml` registry
4. ✅ Moved old directory to `_legacy/55-sli-slo/`

### References

- New location: `governance/55-slo-sli/`
- Registry: `governance/governance-map.yaml`
- Dimension index: `governance/index/dimensions.json`

## Do Not Use

This directory is kept for historical reference only. All new work should use
`governance/55-slo-sli/`.
