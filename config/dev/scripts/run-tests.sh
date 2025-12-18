#!/bin/bash
set -e

# Automated Test Suite for Kind Cluster
# Tests cluster functionality, deployments, and integrations

CLUSTER_NAME="${KIND_CLUSTER_NAME:-governance-test}"
CONTEXT="kind-${CLUSTER_NAME}"
TEST_NAMESPACE="kind-test"
RESULTS_FILE="/tmp/kind-cluster-test-results.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Initialize test results
echo "🧪 Kind Cluster Automated Test Suite" > "${RESULTS_FILE}"
echo "Cluster: ${CLUSTER_NAME}" >> "${RESULTS_FILE}"
echo "Started: $(date)" >> "${RESULTS_FILE}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "${RESULTS_FILE}"
echo "" >> "${RESULTS_FILE}"

# Test helper functions
test_start() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "[$TESTS_TOTAL] Testing: $1... "
    echo "[$TESTS_TOTAL] Testing: $1" >> "${RESULTS_FILE}"
}

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✅ PASS${NC}"
    echo "  Result: PASS" >> "${RESULTS_FILE}"
    echo "" >> "${RESULTS_FILE}"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}❌ FAIL${NC}"
    echo "  Result: FAIL" >> "${RESULTS_FILE}"
    echo "  Error: $1" >> "${RESULTS_FILE}"
    echo "" >> "${RESULTS_FILE}"
}

# Test 1: Cluster connectivity
test_cluster_connectivity() {
    test_start "Cluster API connectivity"
    
    if kubectl cluster-info --context="${CONTEXT}" &>/dev/null; then
        test_pass
        return 0
    else
        test_fail "Cannot connect to cluster API"
        return 1
    fi
}

# Test 2: Node readiness
test_node_readiness() {
    test_start "Node readiness status"
    
    local nodes=$(kubectl get nodes --context="${CONTEXT}" --no-headers 2>/dev/null)
    local total=$(echo "${nodes}" | wc -l)
    local ready=$(echo "${nodes}" | grep -c " Ready " || echo 0)
    
    if [ "${ready}" -eq "${total}" ] && [ "${total}" -gt 0 ]; then
        test_pass
        return 0
    else
        test_fail "Nodes not ready: ${ready}/${total}"
        return 1
    fi
}

# Test 3: Core system pods
test_system_pods() {
    test_start "Core system pods health"
    
    local not_running=$(kubectl get pods -n kube-system --context="${CONTEXT}" --no-headers 2>/dev/null | grep -v "Running" | wc -l)
    
    if [ "${not_running}" -eq 0 ]; then
        test_pass
        return 0
    else
        test_fail "System pods not running: ${not_running}"
        return 1
    fi
}

# Test 4: DNS resolution
test_dns_resolution() {
    test_start "DNS resolution inside cluster"
    
    kubectl run test-dns --image=busybox --context="${CONTEXT}" --restart=Never --rm -i --quiet -- nslookup kubernetes.default &>/dev/null
    
    if [ $? -eq 0 ]; then
        test_pass
        return 0
    else
        test_fail "DNS resolution failed"
        return 1
    fi
}

# Test 5: Service deployment
test_service_deployment() {
    test_start "Deploy and expose a test service"
    
    kubectl create namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" --dry-run=client -o yaml | kubectl apply -f - --context="${CONTEXT}" &>/dev/null
    
    kubectl run test-nginx --image=nginx:alpine --context="${CONTEXT}" -n "${TEST_NAMESPACE}" &>/dev/null
    kubectl expose pod test-nginx --port=80 --context="${CONTEXT}" -n "${TEST_NAMESPACE}" &>/dev/null
    
    sleep 5
    
    local pod_status=$(kubectl get pod test-nginx -n "${TEST_NAMESPACE}" --context="${CONTEXT}" -o jsonpath='{.status.phase}' 2>/dev/null)
    
    if [ "${pod_status}" = "Running" ]; then
        test_pass
        kubectl delete namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" &>/dev/null
        return 0
    else
        test_fail "Pod status: ${pod_status}"
        kubectl delete namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" &>/dev/null
        return 1
    fi
}

# Test 6: Persistent storage
test_persistent_storage() {
    test_start "Persistent volume provisioning"
    
    kubectl create namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" --dry-run=client -o yaml | kubectl apply -f - --context="${CONTEXT}" &>/dev/null
    
    cat <<EOF | kubectl apply -f - --context="${CONTEXT}" &>/dev/null
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
  namespace: ${TEST_NAMESPACE}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF
    
    sleep 3
    
    local pvc_status=$(kubectl get pvc test-pvc -n "${TEST_NAMESPACE}" --context="${CONTEXT}" -o jsonpath='{.status.phase}' 2>/dev/null)
    
    if [ "${pvc_status}" = "Bound" ] || [ "${pvc_status}" = "Pending" ]; then
        test_pass
        kubectl delete namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" &>/dev/null
        return 0
    else
        test_fail "PVC status: ${pvc_status}"
        kubectl delete namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" &>/dev/null
        return 1
    fi
}

# Test 7: Network policies
test_network_policies() {
    test_start "Network policy support"
    
    kubectl create namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" --dry-run=client -o yaml | kubectl apply -f - --context="${CONTEXT}" &>/dev/null
    
    cat <<EOF | kubectl apply -f - --context="${CONTEXT}" &>/dev/null
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: test-netpol
  namespace: ${TEST_NAMESPACE}
spec:
  podSelector:
    matchLabels:
      app: test
  policyTypes:
  - Ingress
EOF
    
    if kubectl get networkpolicy test-netpol -n "${TEST_NAMESPACE}" --context="${CONTEXT}" &>/dev/null; then
        test_pass
        kubectl delete namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" &>/dev/null
        return 0
    else
        test_fail "Network policy creation failed"
        kubectl delete namespace "${TEST_NAMESPACE}" --context="${CONTEXT}" &>/dev/null
        return 1
    fi
}

# Test 8: Ingress controller
test_ingress_controller() {
    test_start "Ingress controller availability"
    
    if kubectl get pods -n ingress-nginx --context="${CONTEXT}" &>/dev/null; then
        local running=$(kubectl get pods -n ingress-nginx --context="${CONTEXT}" --no-headers 2>/dev/null | grep -c "Running" || echo 0)
        if [ "${running}" -gt 0 ]; then
            test_pass
            return 0
        fi
    fi
    
    test_fail "Ingress controller not found or not running"
    return 1
}

# Test 9: Metrics server
test_metrics_server() {
    test_start "Metrics server functionality"
    
    if kubectl top nodes --context="${CONTEXT}" &>/dev/null 2>&1; then
        test_pass
        return 0
    else
        test_fail "Metrics server not available"
        return 1
    fi
}

# Test 10: Helm functionality
test_helm_functionality() {
    test_start "Helm deployment functionality"
    
    if command -v helm &>/dev/null; then
        if helm list --all-namespaces --kube-context="${CONTEXT}" &>/dev/null; then
            test_pass
            return 0
        fi
    fi
    
    test_fail "Helm not functional"
    return 1
}

# Generate summary report
generate_report() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Test Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Total Tests:  ${TESTS_TOTAL}"
    echo -e "  Passed:       ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "  Failed:       ${RED}${TESTS_FAILED}${NC}"
    echo ""
    
    local pass_rate=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    echo "  Pass Rate:    ${pass_rate}%"
    echo ""
    
    if [ "${TESTS_FAILED}" -eq 0 ]; then
        echo -e "  Overall:      ${GREEN}✅ ALL TESTS PASSED${NC}"
    else
        echo -e "  Overall:      ${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 Detailed results saved to: ${RESULTS_FILE}"
    
    # Append summary to results file
    echo "" >> "${RESULTS_FILE}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "${RESULTS_FILE}"
    echo "Test Summary:" >> "${RESULTS_FILE}"
    echo "  Total: ${TESTS_TOTAL}" >> "${RESULTS_FILE}"
    echo "  Passed: ${TESTS_PASSED}" >> "${RESULTS_FILE}"
    echo "  Failed: ${TESTS_FAILED}" >> "${RESULTS_FILE}"
    echo "  Pass Rate: ${pass_rate}%" >> "${RESULTS_FILE}"
    echo "Completed: $(date)" >> "${RESULTS_FILE}"
}

# Main test execution
main() {
    echo "🧪 Starting Kind Cluster Automated Test Suite"
    echo "   Cluster: ${CLUSTER_NAME}"
    echo "   Context: ${CONTEXT}"
    echo ""
    
    # Run all tests
    test_cluster_connectivity
    test_node_readiness
    test_system_pods
    test_dns_resolution
    test_service_deployment
    test_persistent_storage
    test_network_policies
    test_ingress_controller
    test_metrics_server
    test_helm_functionality
    
    # Generate report
    generate_report
    
    # Exit with appropriate code
    if [ "${TESTS_FAILED}" -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run tests
main
