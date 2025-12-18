#!/bin/bash

# Cluster Health Monitoring Script
# Continuously monitors cluster health and reports issues

CLUSTER_NAME="${KIND_CLUSTER_NAME:-governance-test}"
CONTEXT="kind-${CLUSTER_NAME}"
CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-60}"
LOG_FILE="/tmp/kind-cluster-health.log"

echo "🏥 Starting cluster health monitoring for '${CLUSTER_NAME}'..."
echo "📝 Logging to: ${LOG_FILE}"

# Initialize log file
echo "[$(date)] Health monitoring started" > "${LOG_FILE}"

# Function to check node health
check_nodes() {
    local status=$(kubectl get nodes --context="${CONTEXT}" --no-headers 2>/dev/null)
    local ready_count=$(echo "${status}" | grep -c " Ready ")
    local total_count=$(echo "${status}" | wc -l)
    
    if [ "${ready_count}" -eq "${total_count}" ] && [ "${total_count}" -gt 0 ]; then
        echo "[$(date)] ✅ Nodes: ${ready_count}/${total_count} Ready" | tee -a "${LOG_FILE}"
        return 0
    else
        echo "[$(date)] ⚠️  Nodes: ${ready_count}/${total_count} Ready (Issue detected)" | tee -a "${LOG_FILE}"
        return 1
    fi
}

# Function to check pod health
check_pods() {
    local critical_namespaces="kube-system ingress-nginx monitoring cert-manager"
    local issues=0
    
    for ns in ${critical_namespaces}; do
        local pod_status=$(kubectl get pods -n "${ns}" --context="${CONTEXT}" --no-headers 2>/dev/null)
        if [ -n "${pod_status}" ]; then
            local running=$(echo "${pod_status}" | grep -c "Running")
            local total=$(echo "${pod_status}" | wc -l)
            
            if [ "${running}" -eq "${total}" ]; then
                echo "[$(date)] ✅ Pods in ${ns}: ${running}/${total} Running" | tee -a "${LOG_FILE}"
            else
                echo "[$(date)] ⚠️  Pods in ${ns}: ${running}/${total} Running (Issue)" | tee -a "${LOG_FILE}"
                issues=$((issues + 1))
            fi
        fi
    done
    
    return ${issues}
}

# Function to check API server
check_api_server() {
    if kubectl cluster-info --context="${CONTEXT}" &>/dev/null; then
        echo "[$(date)] ✅ API Server: Responsive" | tee -a "${LOG_FILE}"
        return 0
    else
        echo "[$(date)] ❌ API Server: Unreachable" | tee -a "${LOG_FILE}"
        return 1
    fi
}

# Function to check resource usage
check_resources() {
    if command -v kubectl-top &>/dev/null || kubectl top nodes --context="${CONTEXT}" &>/dev/null 2>&1; then
        local node_metrics=$(kubectl top nodes --context="${CONTEXT}" 2>/dev/null)
        if [ -n "${node_metrics}" ]; then
            echo "[$(date)] 📊 Resource metrics:" | tee -a "${LOG_FILE}"
            echo "${node_metrics}" | tee -a "${LOG_FILE}"
        fi
    fi
}

# Main monitoring loop
monitor_loop() {
    while true; do
        echo "" | tee -a "${LOG_FILE}"
        echo "[$(date)] 🔍 Running health checks..." | tee -a "${LOG_FILE}"
        
        local overall_health="healthy"
        
        # Run all checks
        check_api_server || overall_health="unhealthy"
        check_nodes || overall_health="degraded"
        check_pods || overall_health="degraded"
        check_resources
        
        # Overall status
        case "${overall_health}" in
            "healthy")
                echo "[$(date)] ✅ Overall Status: HEALTHY" | tee -a "${LOG_FILE}"
                ;;
            "degraded")
                echo "[$(date)] ⚠️  Overall Status: DEGRADED" | tee -a "${LOG_FILE}"
                ;;
            "unhealthy")
                echo "[$(date)] ❌ Overall Status: UNHEALTHY" | tee -a "${LOG_FILE}"
                ;;
        esac
        
        sleep "${CHECK_INTERVAL}"
    done
}

# Run in background mode or foreground
if [ "${1}" = "background" ]; then
    nohup bash -c "$(declare -f monitor_loop check_api_server check_nodes check_pods check_resources); monitor_loop" >> "${LOG_FILE}" 2>&1 &
    echo "✅ Health monitoring started in background (PID: $!)"
    echo "📝 View logs: tail -f ${LOG_FILE}"
else
    monitor_loop
fi
