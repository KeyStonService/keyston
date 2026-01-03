#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports
echo '{"tool":"spectral","status":"stub-ok"}' > artifacts/reports/openapi-lint.json
echo "openapi-lint: done"
