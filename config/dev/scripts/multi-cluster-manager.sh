#!/bin/bash
set -e

# Multi-Cluster Management Script
# Manage multiple Kind clusters for different environments

CLUSTERS_CONFIG_DIR="${HOME}/.kind-clusters"
mkdir -p "${CLUSTERS_CONFIG_DIR}"

show_help() {
    cat << EOF
🎛️  Kind Multi-Cluster Manager

Usage: $(basename "$0") <command> [options]

Commands:
    list                    List all Kind clusters
    create <name> [nodes]   Create a new cluster with optional node count
    delete <name>           Delete a cluster
    switch <name>           Switch to a different cluster context
    info <name>             Show cluster information
    status                  Show status of all clusters
    sync                    Sync cluster configurations

Examples:
    $(basename "$0") create dev 1          # Create 'dev' cluster with 1 worker
    $(basename "$0") create staging 2      # Create 'staging' cluster with 2 workers
    $(basename "$0") switch dev            # Switch to 'dev' cluster
    $(basename "$0") list                  # List all clusters
    $(basename "$0") status                # Show all cluster statuses
EOF
}

list_clusters() {
    echo "📋 Available Kind Clusters:"
    kind get clusters 2>/dev/null || echo "  No clusters found"
    echo ""
    echo "🎯 Current Context:"
    kubectl config current-context 2>/dev/null || echo "  No context set"
}

create_cluster() {
    local cluster_name="${1:-dev-cluster}"
    local worker_nodes="${2:-1}"
    
    echo "🚀 Creating cluster '${cluster_name}' with ${worker_nodes} worker node(s)..."
    
    # Generate cluster config
    local config_file="${CLUSTERS_CONFIG_DIR}/${cluster_name}-config.yaml"
    cat > "${config_file}" << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${cluster_name}
networking:
  apiServerAddress: "127.0.0.1"
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.96.0.0/12"
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
EOF

    # Add worker nodes
    for i in $(seq 1 "${worker_nodes}"); do
        cat >> "${config_file}" << EOF
  - role: worker
    labels:
      tier: worker
      zone: zone-${i}
EOF
    done
    
    # Create cluster using config
    KIND_EXPERIMENTAL_PROVIDER=podman kind create cluster --config="${config_file}"
    
    echo "✅ Cluster '${cluster_name}' created successfully"
    echo "📝 Config saved to: ${config_file}"
}

delete_cluster() {
    local cluster_name="${1}"
    
    if [ -z "${cluster_name}" ]; then
        echo "❌ Error: Cluster name required"
        echo "Usage: $(basename "$0") delete <cluster_name>"
        return 1
    fi
    
    echo "🗑️  Deleting cluster '${cluster_name}'..."
    kind delete cluster --name="${cluster_name}"
    
    # Remove config file
    rm -f "${CLUSTERS_CONFIG_DIR}/${cluster_name}-config.yaml"
    
    echo "✅ Cluster '${cluster_name}' deleted"
}

switch_cluster() {
    local cluster_name="${1}"
    
    if [ -z "${cluster_name}" ]; then
        echo "❌ Error: Cluster name required"
        echo "Usage: $(basename "$0") switch <cluster_name>"
        return 1
    fi
    
    local context="kind-${cluster_name}"
    
    if kubectl config use-context "${context}"; then
        echo "✅ Switched to cluster '${cluster_name}'"
        echo "🎯 Current context: ${context}"
    else
        echo "❌ Failed to switch to cluster '${cluster_name}'"
        echo "💡 Available clusters:"
        kind get clusters
        return 1
    fi
}

cluster_info() {
    local cluster_name="${1:-$(kubectl config current-context | sed 's/kind-//')}"
    local context="kind-${cluster_name}"
    
    echo "ℹ️  Cluster Information: ${cluster_name}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "📍 Context: ${context}"
    kubectl cluster-info --context="${context}"
    
    echo ""
    echo "🖥️  Nodes:"
    kubectl get nodes --context="${context}"
    
    echo ""
    echo "📦 Namespaces:"
    kubectl get namespaces --context="${context}"
    
    if [ -f "${CLUSTERS_CONFIG_DIR}/${cluster_name}-config.yaml" ]; then
        echo ""
        echo "⚙️  Configuration: ${CLUSTERS_CONFIG_DIR}/${cluster_name}-config.yaml"
    fi
}

cluster_status() {
    echo "📊 Multi-Cluster Status Report"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local clusters=$(kind get clusters 2>/dev/null)
    
    if [ -z "${clusters}" ]; then
        echo "  No clusters found"
        return 0
    fi
    
    for cluster in ${clusters}; do
        local context="kind-${cluster}"
        echo ""
        echo "Cluster: ${cluster}"
        
        if kubectl cluster-info --context="${context}" &>/dev/null; then
            local nodes=$(kubectl get nodes --context="${context}" --no-headers 2>/dev/null | wc -l)
            local ready=$(kubectl get nodes --context="${context}" --no-headers 2>/dev/null | grep -c " Ready " || echo 0)
            echo "  Status: ✅ Running"
            echo "  Nodes:  ${ready}/${nodes} Ready"
            
            # Show resource usage if available
            if kubectl top nodes --context="${context}" &>/dev/null 2>&1; then
                echo "  Resources:"
                kubectl top nodes --context="${context}" 2>/dev/null | tail -n +2 | while read -r line; do
                    echo "    ${line}"
                done
            fi
        else
            echo "  Status: ❌ Unreachable"
        fi
    done
    
    echo ""
    echo "🎯 Current Context: $(kubectl config current-context 2>/dev/null || echo 'None')"
}

sync_clusters() {
    echo "🔄 Syncing cluster configurations..."
    
    local clusters=$(kind get clusters 2>/dev/null)
    
    for cluster in ${clusters}; do
        if [ ! -f "${CLUSTERS_CONFIG_DIR}/${cluster}-config.yaml" ]; then
            echo "  • Generating config for '${cluster}'..."
            # Create basic config for existing clusters
            create_cluster_config_backup "${cluster}"
        fi
    done
    
    echo "✅ Cluster configurations synced"
}

create_cluster_config_backup() {
    local cluster_name="${1}"
    local config_file="${CLUSTERS_CONFIG_DIR}/${cluster_name}-config.yaml"
    
    cat > "${config_file}" << EOF
# Auto-generated configuration for cluster: ${cluster_name}
# Generated: $(date)
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${cluster_name}
EOF
    
    echo "  ✅ Config created: ${config_file}"
}

# Main command dispatcher
case "${1}" in
    list)
        list_clusters
        ;;
    create)
        create_cluster "${2}" "${3}"
        ;;
    delete)
        delete_cluster "${2}"
        ;;
    switch)
        switch_cluster "${2}"
        ;;
    info)
        cluster_info "${2}"
        ;;
    status)
        cluster_status
        ;;
    sync)
        sync_clusters
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -z "${1}" ]; then
            show_help
        else
            echo "❌ Unknown command: ${1}"
            echo ""
            show_help
        fi
        exit 1
        ;;
esac
