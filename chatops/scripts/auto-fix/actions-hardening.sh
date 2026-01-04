#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports/auto-fix/details
python3 scripts/repair/actions_hardening.py --out artifacts/reports/auto-fix/details/actions-hardening.report.json
echo "actions-hardening: done"
