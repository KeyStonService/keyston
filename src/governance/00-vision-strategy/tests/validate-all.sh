#!/bin/bash
# GaC Validation Script
# Validates all generated CRDs, K8s instances, and OPA policies
# Phase: 2 - Operational Implementation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STRATEGY_DIR="$SCRIPT_DIR/.."

echo "🔍 GaC Phase 2 Validation"
echo "========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0
SUCCESS=0

# Function to validate YAML syntax
validate_yaml() {
  local file=$1
  if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Valid YAML: $(basename $file)"
    ((SUCCESS++))
    return 0
  else
    echo -e "  ${RED}✗${NC} Invalid YAML: $(basename $file)"
    python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>&1 | head -3
    ((ERRORS++))
    return 1
  fi
}

# Function to validate Rego syntax
validate_rego() {
  local file=$1
  if command -v opa &> /dev/null; then
    if opa check "$file" &> /dev/null; then
      echo -e "  ${GREEN}✓${NC} Valid Rego: $(basename $file)"
      ((SUCCESS++))
    else
      echo -e "  ${RED}✗${NC} Invalid Rego: $(basename $file)"
      ((ERRORS++))
    fi
  else
    echo -e "  ${YELLOW}⚠${NC} OPA not installed, skipping: $(basename $file)"
    ((WARNINGS++))
  fi
}

# Validate CRDs
echo "📋 Validating CRDs..."
for file in "$STRATEGY_DIR/crd"/*.yaml; do
  [ -f "$file" ] || continue
  validate_yaml "$file"
done
echo ""

# Validate K8s instances
echo "🔧 Validating K8s Instances..."
for file in "$STRATEGY_DIR/k8s"/*.yaml; do
  [ -f "$file" ] || continue
  validate_yaml "$file"
done
echo ""

# Validate OPA policies
echo "🛡️  Validating OPA Policies..."
for file in "$STRATEGY_DIR/policy"/*.rego; do
  [ -f "$file" ] || continue
  validate_rego "$file"
done
echo ""

# Check file counts
echo "📊 File Count Verification..."
CRD_COUNT=$(find "$STRATEGY_DIR/crd" -name "*.yaml" -type f | wc -l)
K8S_COUNT=$(find "$STRATEGY_DIR/k8s" -name "*.yaml" -type f | wc -l)
POLICY_COUNT=$(find "$STRATEGY_DIR/policy" -name "*.rego" -type f | wc -l)

echo "  CRDs: $CRD_COUNT (expected: 9)"
echo "  K8s instances: $K8S_COUNT (expected: 9)"
echo "  OPA policies: $POLICY_COUNT (expected: 9)"

if [ "$CRD_COUNT" -eq 9 ] && [ "$K8S_COUNT" -eq 9 ] && [ "$POLICY_COUNT" -eq 9 ]; then
  echo -e "  ${GREEN}✓${NC} File count matches expected"
  ((SUCCESS++))
else
  echo -e "  ${RED}✗${NC} File count mismatch"
  ((ERRORS++))
fi
echo ""

# Summary
echo "================================"
echo "Validation Summary"
echo "================================"
echo -e "${GREEN}Success:${NC} $SUCCESS"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Errors:${NC} $ERRORS"
echo ""

if [ $ERRORS -eq 0 ]; then
  echo -e "${GREEN}✅ All validations passed!${NC}"
  exit 0
else
  echo -e "${RED}❌ Validation failed with $ERRORS error(s)${NC}"
  exit 1
fi
