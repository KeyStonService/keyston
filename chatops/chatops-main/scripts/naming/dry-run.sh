#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports/naming
echo '{"tool":"naming","stage":"dry-run","status":"stub-ok"}' > artifacts/reports/naming/dryrun.json
