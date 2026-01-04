# Naming Migration Playbook

## Goals
- Discovery -> Plan -> Dry-run -> Staged Rename -> Cutover -> Rollback
- RTO <= 20 minutes
- Auditable artifacts written to `artifacts/reports/naming/*`

## 1) Discovery
Run:
```bash
bash scripts/naming/discover.sh
cat artifacts/reports/naming/compliance_report.json
```

Acceptance:
- `summary.total` > 0 (for real repos)
- `violations[]` enumerates file/kind/name

## 2) Plan
Plan table should be generated from violations (not auto in this scaffold).
Required columns:
- file, kind, old_name, new_name, risk_level, owner, wave

## 3) Dry-run
Run:
```bash
bash scripts/naming/dry-run.sh
```

## 4) Staged Rename (10/25/50/100)
Run:
```bash
bash scripts/naming/staged-rename.sh
```

Gates:
- Post-wave conftest naming must pass
- Alert rate must not exceed thresholds

## 5) Cutover
Run:
```bash
bash scripts/naming/cutover.sh
```

## 6) Rollback
Run:
```bash
bash scripts/naming/rollback.sh
```

Verify:
```bash
bash scripts/naming/verify-post-rollback.sh
```

## SLA report
Run:
```bash
node scripts/naming/report-sla.mjs
cat artifacts/reports/naming/sla_metrics.json
```
