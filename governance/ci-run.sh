#!/usr/bin/env bash
set -euo pipefail

echo "📥 Loading governance index..."
if [ ! -f "governance/index/governance-index.json" ]; then
  echo "::error::governance/index/governance-index.json not found at governance/index/governance-index.json"
  exit 1
fi

echo "🔍 Running governance index validation..."
if command -v python3 >/dev/null 2>&1; then
  python3 governance/index/scripts/index-validator.py --verbose
else
  echo "::error::Python 3 is required to run governance validation"
  exit 1
fi

echo "✅ governance/ci-run.sh completed"
