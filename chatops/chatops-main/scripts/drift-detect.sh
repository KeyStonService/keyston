#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports
echo '{"tool":"drift","mode":"stub","drift":0}' > artifacts/reports/drift.json
echo "drift-detect: done"
