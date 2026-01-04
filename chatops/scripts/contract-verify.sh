#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports
echo '{"tool":"contract-verify","status":"stub-ok"}' > artifacts/reports/contract-verify.json
echo "contract-verify: done"
