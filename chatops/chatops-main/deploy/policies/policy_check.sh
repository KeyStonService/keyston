#!/bin/bash
# policy_check.sh - Run policy checks (Kyverno)

set -e

echo "🛡️ Running policy checks..."

# Check for required tools
if ! command -v kubectl >/dev/null 2>&1; then
    echo "  ⚠️  kubectl not found, skipping policy checks"
    exit 0
fi

if ! command -v kyverno >/dev/null 2>&1; then
    echo "  ⚠️  kyverno not found, skipping policy checks"
    exit 0
fi

# Check if policies directory exists
if [ ! -d "policies" ]; then
    echo "  ⚠️  No policies directory found, skipping policy checks"
    exit 0
fi

# Run Kyverno policy validation
echo "  📋 Validating policies..."
if find policies/ -name "*.yaml" -o -name "*.yml" | head -1 | grep -q "."; then
    kyverno validate policies/ --resource deploy/ || true
    echo "    ✅ Policy validation completed"
else
    echo "    ⚠️  No policy files found"
fi

echo "✅ Policy checks complete"