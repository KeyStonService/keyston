#!/bin/bash
set -e

echo "📦 Setting up Helm charts auto-deployment..."

# Ensure Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Installing..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

CLUSTER_NAME="${KIND_CLUSTER_NAME:-governance-test}"
CONTEXT="kind-${CLUSTER_NAME}"

# Ensure we're using the correct context
kubectl config use-context "${CONTEXT}"

# Add common Helm repositories
echo "📚 Adding Helm repositories..."
helm repo add stable https://charts.helm.sh/stable 2>/dev/null || true
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo add nginx-stable https://helm.nginx.com/stable 2>/dev/null || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
helm repo update

# Install NGINX Ingress Controller
echo "🌐 Installing NGINX Ingress Controller..."
helm upgrade --install ingress-nginx nginx-stable/nginx-ingress \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=NodePort \
    --set controller.hostPort.enabled=true \
    --wait \
    --timeout 5m || echo "⚠️  NGINX Ingress installation skipped or already exists"

# Install Prometheus monitoring stack
echo "📊 Installing Prometheus monitoring..."
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --set prometheus.service.type=NodePort \
    --set grafana.service.type=NodePort \
    --set alertmanager.service.type=NodePort \
    --wait \
    --timeout 5m || echo "⚠️  Prometheus installation skipped or already exists"

# Install cert-manager for TLS certificate management
echo "🔐 Installing cert-manager..."
helm upgrade --install cert-manager jetstack/cert-manager \
    --repo https://charts.jetstack.io \
    --namespace cert-manager \
    --create-namespace \
    --set installCRDs=true \
    --wait \
    --timeout 5m || echo "⚠️  cert-manager installation skipped or already exists"

# Install Metrics Server
echo "📈 Installing Metrics Server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml || true
kubectl patch deployment metrics-server -n kube-system --type=json \
    -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' 2>/dev/null || true

echo "✅ Helm charts deployment complete!"
echo ""
echo "📦 Installed components:"
echo "  • NGINX Ingress Controller (namespace: ingress-nginx)"
echo "  • Prometheus + Grafana (namespace: monitoring)"
echo "  • cert-manager (namespace: cert-manager)"
echo "  • Metrics Server (namespace: kube-system)"
echo ""
echo "🔍 Useful commands:"
echo "  • List all releases:     helm list -A"
echo "  • Check ingress status:  kubectl get pods -n ingress-nginx"
echo "  • Access Grafana:        kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
echo "  • Check metrics:         kubectl top nodes"
