# Naming Migration Playbook (Discovery → Plan → Dry-run → Staged Rename → Cutover → Rollback)

This playbook implements an auditable, staged migration process for resource naming governance.

## Stages
1. **Discovery**
   - Collect naming violations and impacted manifests/resources.
   - Output: `artifacts/reports/naming-discovery.json`

2. **Plan**
   - Generate an actionable plan table.
   - Output: `artifacts/reports/naming-plan.csv`

3. **Dry-run**
   - Simulate rename changes and produce a diff-like report.
   - Output: `artifacts/reports/naming-dryrun.json`

4. **Staged Rename**
   - Apply changes in waves (10/25/50/100) with verification gates.
   - Output: `artifacts/reports/naming-staged-rename.json`

5. **Cutover**
   - Switch endpoints (DNS/Service selectors) where applicable.
   - Output: `artifacts/reports/naming-cutover.json`

6. **Rollback**
   - Revert within 20 minutes including name/DNS/traffic route.
   - Output: `artifacts/reports/naming-rollback.json`

## SLA / SLI
Tracked metrics (exported via `scripts/observability/metrics_exporter.py`):
- NCR: Naming Compliance Rate
- VFC: Validation Failure Count
- MFR: Migration Failure Rate
- ARS: Auto Repair Success

---

## Quickstart (local)
```bash
make bootstrap
make naming-discovery
make naming-plan
make naming-dryrun
```
