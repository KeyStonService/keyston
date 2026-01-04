#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports/naming
echo '{"tool":"naming","stage":"staged-rename","waves":[10,25,50,100],"status":"stub-ok"}' > artifacts/reports/naming/staged-rename.json
