#!/usr/bin/env bash
# Local validation script for GaC resources
# Tests syntax and structure without requiring a full Kubernetes cluster
# Phase 3 - Deployment Validation
#
# NOTE: This script validates YAML syntax and structure only.
#       For actual deployment to a Kubernetes cluster, see DEPLOYMENT.md

set -e

echo "🚀 GaC Resource Validation (Local)"
echo "==================================="
echo ""
echo "ℹ️  This script validates YAML syntax only."
echo "ℹ️  For actual deployment, see: DEPLOYMENT.md"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "📍 Current directory: $(pwd)"
echo ""

# Function to validate YAML
validate_yaml() {
    local file=$1
    if command -v yq >/dev/null 2>&1; then
        if yq eval '.' "$file" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $file"
            return 0
        else
            echo -e "${RED}✗${NC} $file"
            return 1
        fi
    elif command -v python3 >/dev/null 2>&1; then
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $file"
            return 0
        else
            echo -e "${RED}✗${NC} $file"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠${NC} $file (validation skipped - no YAML validator found)"
        return 0
    fi
}

# Function to check kubectl dry-run
kubectl_dry_run() {
    local file=$1
    if command -v kubectl >/dev/null 2>&1; then
        if kubectl apply --dry-run=client -f "$file" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $file (kubectl dry-run)"
            return 0
        else
            echo -e "${RED}✗${NC} $file (kubectl dry-run failed)"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠${NC} $file (kubectl not installed - skipping dry-run)"
        return 0
    fi
}

# Step 1: Validate CRDs
echo "Step 1: Validating CRDs"
echo "----------------------"
CRD_ERRORS=0
for file in crd/*.yaml; do
    if [ -f "$file" ]; then
        validate_yaml "$file" || ((CRD_ERRORS++))
    fi
done
echo ""

# Step 2: Validate K8s instances
echo "Step 2: Validating K8s Instances"
echo "--------------------------------"
K8S_ERRORS=0
for file in k8s/*.yaml; do
    if [ -f "$file" ]; then
        validate_yaml "$file" || ((K8S_ERRORS++))
    fi
done
echo ""

# Step 3: Validate OPA policies
echo "Step 3: Validating OPA Policies"
echo "--------------------------------"
POLICY_ERRORS=0
for file in policy/*.rego; do
    if [ -f "$file" ]; then
        if command -v opa >/dev/null 2>&1; then
            if opa check "$file" >/dev/null 2>&1; then
                echo -e "${GREEN}✓${NC} $file"
            else
                echo -e "${RED}✗${NC} $file"
                ((POLICY_ERRORS++))
            fi
        else
            echo -e "${YELLOW}⚠${NC} $file (OPA not installed - skipping validation)"
        fi
    fi
done
echo ""

# Step 4: Validate GitOps configs
echo "Step 4: Validating GitOps Configurations"
echo "----------------------------------------"
GITOPS_ERRORS=0
for file in gitops/*.yaml; do
    if [ -f "$file" ]; then
        validate_yaml "$file" || ((GITOPS_ERRORS++))
    fi
done
echo ""

# Step 5: Validate Gatekeeper configs
echo "Step 5: Validating Gatekeeper Configurations"
echo "---------------------------------------------"
GATEKEEPER_ERRORS=0
for file in gatekeeper/*.yaml; do
    if [ -f "$file" ]; then
        validate_yaml "$file" || ((GATEKEEPER_ERRORS++))
    fi
done
echo ""

# Step 6: Validate Monitoring configs
echo "Step 6: Validating Monitoring Configurations"
echo "---------------------------------------------"
MONITORING_ERRORS=0
for file in monitoring/*.yaml monitoring/*.json; do
    if [ -f "$file" ]; then
        case "$file" in
            *.yaml)
                validate_yaml "$file" || ((MONITORING_ERRORS++))
                ;;
            *.json)
                if python3 -c "import sys, json; sys.exit(0 if json.load(open('$file')) else 1)" 2>/dev/null; then
                    echo -e "${GREEN}✓${NC} $file"
                else
                    echo -e "${RED}✗${NC} $file (JSON validation failed)"
                    ((MONITORING_ERRORS++))
                fi
                ;;
        esac
    fi
done
echo ""

# Step 7: kubectl dry-run (optional - requires cluster)
echo "Step 7: kubectl Dry-Run Validation (Optional)"
echo "----------------------------------------------"
if command -v kubectl >/dev/null 2>&1; then
    # Check if we can connect to a cluster
    if kubectl cluster-info >/dev/null 2>&1; then
        echo "Testing CRD deployment with kubectl dry-run..."
        KUBECTL_ERRORS=0
        for file in crd/*.yaml; do
            kubectl_dry_run "$file" || ((KUBECTL_ERRORS++))
        done
        echo ""
        
        if [ $KUBECTL_ERRORS -eq 0 ]; then
            echo -e "${GREEN}✓${NC} All CRDs passed kubectl dry-run validation"
        else
            echo -e "${RED}✗${NC} $KUBECTL_ERRORS CRD(s) failed kubectl dry-run"
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠${NC} No Kubernetes cluster accessible - skipping dry-run"
        echo "   This is normal for CI/CD environments"
        echo "   Syntax validation was successful"
        echo ""
    fi
else
    echo -e "${YELLOW}⚠${NC} kubectl not found - skipping dry-run validation"
    echo "   Install kubectl to enable dry-run testing"
    echo ""
fi

# Summary
echo "Summary"
echo "======="
TOTAL_ERRORS=$((CRD_ERRORS + K8S_ERRORS + POLICY_ERRORS + GITOPS_ERRORS + GATEKEEPER_ERRORS + MONITORING_ERRORS))

if [ $TOTAL_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All validations passed!${NC}"
    echo ""
    echo "Resources validated:"
    # Count files efficiently using shell globbing
    CRD_COUNT=$(compgen -G "crd/*.yaml" 2>/dev/null | wc -l)
    K8S_COUNT=$(compgen -G "k8s/*.yaml" 2>/dev/null | wc -l)
    POLICY_COUNT=$(compgen -G "policy/*.rego" 2>/dev/null | wc -l)
    GITOPS_COUNT=$(compgen -G "gitops/*.yaml" 2>/dev/null | wc -l)
    GATEKEEPER_COUNT=$(compgen -G "gatekeeper/*.yaml" 2>/dev/null | wc -l)
    MONITORING_COUNT=$(compgen -G "monitoring/*.*" 2>/dev/null | wc -l)
    
    echo "  - CRDs: ${CRD_COUNT}"
    echo "  - K8s instances: ${K8S_COUNT}"
    echo "  - OPA policies: ${POLICY_COUNT}"
    echo "  - GitOps configs: ${GITOPS_COUNT}"
    echo "  - Gatekeeper configs: ${GATEKEEPER_COUNT}"
    echo "  - Monitoring configs: ${MONITORING_COUNT}"
    echo ""
    echo "✅ Ready for deployment!"
    echo ""
    echo "📖 Next steps:"
    echo "   1. Review DEPLOYMENT.md for deployment options"
    echo "   2. Choose deployment method (Manual, GitOps, or Kustomize)"
    echo "   3. Deploy to your Kubernetes cluster"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Validation failed with $TOTAL_ERRORS error(s)${NC}"
    echo ""
    echo "Errors by category:"
    [ $CRD_ERRORS -gt 0 ] && echo "  - CRDs: $CRD_ERRORS"
    [ $K8S_ERRORS -gt 0 ] && echo "  - K8s instances: $K8S_ERRORS"
    [ $POLICY_ERRORS -gt 0 ] && echo "  - OPA policies: $POLICY_ERRORS"
    [ $GITOPS_ERRORS -gt 0 ] && echo "  - GitOps configs: $GITOPS_ERRORS"
    [ $GATEKEEPER_ERRORS -gt 0 ] && echo "  - Gatekeeper configs: $GATEKEEPER_ERRORS"
    [ $MONITORING_ERRORS -gt 0 ] && echo "  - Monitoring configs: $MONITORING_ERRORS"
    echo ""
    echo "❌ Please fix the errors before deployment"
    exit 1
fi
