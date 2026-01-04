#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports/naming
echo '{"tool":"naming","stage":"rollback","rto_minutes":20,"status":"stub-ok"}' > artifacts/reports/naming/rollback.json
