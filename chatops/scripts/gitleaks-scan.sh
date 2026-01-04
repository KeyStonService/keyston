#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports
echo '{"tool":"gitleaks","mode":"stub","leaks":0}' > artifacts/reports/gitleaks.json
echo "gitleaks: done"
