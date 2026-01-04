#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports/auto-fix
cat > artifacts/reports/auto-fix/summary.json <<'EOF'
{"version":"1.0","generatedAt":"1970-01-01T00:00:00Z","traceId":"trace-autofix","changes":[],"risk":{"level":"low","notes":"stub"}}
EOF
echo "collect-issues: wrote artifacts/reports/auto-fix/summary.json"
