#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts/reports
# conftest is optional; if missing, we still produce a report stub.
if command -v conftest >/dev/null 2>&1; then
  conftest test deploy ops --policy .config/conftest/policies
  echo '{"tool":"conftest","status":"ok"}' > artifacts/reports/conftest.json
else
  echo '{"tool":"conftest","status":"skipped","reason":"conftest not installed"}' > artifacts/reports/conftest.json
fi

echo "policy-validate: done"
