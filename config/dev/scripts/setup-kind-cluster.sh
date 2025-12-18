#!/bin/bash
set -e

echo "🚀 Setting up Kind cluster with Podman (Full Production Stack)..."

# Set Podman as the Kind provider
export KIND_EXPERIMENTAL_PROVIDER=podman

# Check if Kind is installed
if ! command -v kind &> /dev/null; then
    echo "❌ Kind is not installed. Please check Dockerfile."
    exit 1
fi

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please check devcontainer features."
    exit 1
fi

# Check if cluster already exists
CLUSTER_NAME="${KIND_CLUSTER_NAME:-governance-test}"
if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "✅ Kind cluster '${CLUSTER_NAME}' already exists"
    kubectl cluster-info --context "kind-${CLUSTER_NAME}"
    echo ""
    echo "🔄 Verifying and updating cluster components..."
    # Run post-setup even for existing clusters
    bash "$(dirname "$0")/setup-helm-charts.sh" || echo "⚠️  Helm charts setup skipped"
    bash "$(dirname "$0")/setup-gitops.sh" argocd || echo "⚠️  GitOps setup skipped"
    exit 0
fi

# Use configuration file if available
CONFIG_FILE="${KIND_CLUSTER_CONFIG:-$(dirname "$0")/../kind-cluster-config.yaml}"
if [ -f "${CONFIG_FILE}" ]; then
    echo "📦 Creating Kind cluster '${CLUSTER_NAME}' with custom configuration..."
    kind create cluster --config="${CONFIG_FILE}"
else
    echo "📦 Creating Kind cluster '${CLUSTER_NAME}' with default configuration..."
    kind create cluster --name "${CLUSTER_NAME}"
fi

# Wait for cluster to be ready
echo "⏳ Waiting for cluster to be ready..."
for i in {1..30}; do
    if kubectl get nodes --context "kind-${CLUSTER_NAME}" &>/dev/null; then
        echo "✅ Cluster is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Timeout waiting for cluster to be ready"
        exit 1
    fi
    sleep 2
done

# Verify cluster is running
echo "🔍 Verifying cluster..."
kubectl cluster-info --context "kind-${CLUSTER_NAME}"

# Get nodes
echo "📋 Cluster nodes:"
kubectl get nodes

echo "✅ Kind cluster created successfully!"
echo ""

# Install Helm charts automatically
echo "📦 Installing production-ready Helm charts..."
bash "$(dirname "$0")/setup-helm-charts.sh" || echo "⚠️  Helm charts installation encountered issues"

# Setup GitOps workflow
echo "🔄 Setting up GitOps workflow (ArgoCD)..."
bash "$(dirname "$0")/setup-gitops.sh" argocd || echo "⚠️  GitOps setup encountered issues"

# Start health monitoring in background
echo "🏥 Starting cluster health monitoring..."
bash "$(dirname "$0")/health-monitor.sh" background || echo "⚠️  Health monitoring setup skipped"

# Run automated tests
echo "🧪 Running automated test suite..."
bash "$(dirname "$0")/run-tests.sh" || echo "⚠️  Some tests failed, check logs for details"

echo ""
echo "✅ Complete Kind cluster stack deployment finished!"
echo ""
echo "🎯 Cluster Information:"
echo "  • Cluster Name: ${CLUSTER_NAME}"
echo "  • Context: kind-${CLUSTER_NAME}"
echo "  • Provider: Podman"
echo "  • Nodes: $(kubectl get nodes --context="kind-${CLUSTER_NAME}" --no-headers 2>/dev/null | wc -l)"
echo ""
echo "📦 Installed Components:"
echo "  • NGINX Ingress Controller"
echo "  • Prometheus + Grafana Monitoring"
echo "  • cert-manager (TLS Certificates)"
echo "  • Metrics Server"
echo "  • ArgoCD (GitOps)"
echo "  • Health Monitor (Background)"
echo ""
echo "🔧 Management Commands:"
echo "  • Multi-cluster:     config/dev/scripts/multi-cluster-manager.sh"
echo "  • Health check:      tail -f /tmp/kind-cluster-health.log"
echo "  • Run tests:         config/dev/scripts/run-tests.sh"
echo "  • GitOps setup:      config/dev/scripts/setup-gitops.sh"
echo ""
echo "🌐 Access Services:"
echo "  • ArgoCD:            kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "  • Grafana:           kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
echo "  • Prometheus:        kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
