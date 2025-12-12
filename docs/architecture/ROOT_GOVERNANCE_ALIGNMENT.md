# Root Refactor Governance Alignment

> Scope: Keep `governance/` and `core/` fixed; other root items may move, but **must** stay aligned with governance conventions.

## Governance Sources Reviewed

- `governance/RESTRUCTURING_GUIDE.md` — layered dimensions, dual audit directories (`07-audit/` vs `70-audit/`), shared resource consolidation.
- `governance/README.md` + `governance/29-docs/GOVERNANCE_STRUCTURE_INDEX.md` — canonical roles, capabilities, naming, and mappings across 00-80 dimensions.
- `config/system-module-map.yaml` — root directory cleanup guidelines and consolidation targets (automation/, services/, infrastructure/, docs/, tools/, tests/, ops/, shared/, legacy/).

## Alignment Rules for Root Moves

1. **Vocabulary & Naming**: Use numbered dimensions and existing governance terms; do not create new namespaces. Preserve the semantic split between `07-audit/` (strategy) and `70-audit/` (feedback).
2. **Path Mapping**: When relocating root files, place them into the targets defined in `config/system-module-map.yaml` (e.g., automation/, services/, infrastructure/, docs/, tools/, tests/, ops/). Avoid touching `governance/` and `core/`.
3. **Dependency Order**: Maintain the governance execution order `10-policy → 20-intent → 30/39/40 execution → 60/70 observability → 80 feedback`; root relocations must not break these references.
4. **Schema & Policy References**: Keep references to `23-policies/`, `31-schemas/`, and `35-scripts/` paths intact; if a root file points to legacy paths, update it to the consolidated governance paths.

## Validation Checklist

- Confirm new locations follow `root_directory_guidelines` in `config/system-module-map.yaml`.
- Re-run `tools/governance/validate-governance-matrix.py` if paths change.
- Ensure any renamed paths continue to satisfy the layered governance matrix and dependency flow.
