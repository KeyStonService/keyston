#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports/naming
echo '{"tool":"naming","stage":"cutover","status":"stub-ok"}' > artifacts/reports/naming/cutover.json
