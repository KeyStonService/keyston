#!/usr/bin/env bash
set -euo pipefail

echo "📥 Loading governance index..."
if [ ! -f "governance/index/governance-index.json" ]; then
  echo "::error::governance/index/governance-index.json not found"
  exit 1
fi

echo "🔍 Running governance index validation..."
python governance/index/scripts/index-validator.py --verbose

echo "✅ governance/ci-run.sh completed"
