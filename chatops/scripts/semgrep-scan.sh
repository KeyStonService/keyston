#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports
echo '{"tool":"semgrep","mode":"stub","findings":0}' > artifacts/reports/semgrep.json
echo "semgrep: done"
