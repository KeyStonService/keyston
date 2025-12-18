#!/bin/bash
set -e

# GitOps Workflow Integration
# Implements GitOps practices for cluster management

CLUSTER_NAME="${KIND_CLUSTER_NAME:-governance-test}"
CONTEXT="kind-${CLUSTER_NAME}"
GITOPS_REPO="${GITOPS_REPO:-}"
GITOPS_DIR="${GITOPS_DIR:-./gitops}"

echo "🔄 Setting up GitOps workflow integration..."

# Install ArgoCD
install_argocd() {
    echo "📦 Installing ArgoCD..."
    
    kubectl create namespace argocd --context="${CONTEXT}" --dry-run=client -o yaml | kubectl apply -f - --context="${CONTEXT}"
    
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --context="${CONTEXT}"
    
    echo "⏳ Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd --context="${CONTEXT}" || echo "⚠️  ArgoCD deployment timeout, continuing..."
    
    # Patch ArgoCD server for insecure mode (development only)
    kubectl patch deploy argocd-server -n argocd --context="${CONTEXT}" \
        --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/command/-", "value": "--insecure"}]' 2>/dev/null || true
    
    echo "✅ ArgoCD installed"
}

# Install Flux CD
install_flux() {
    echo "📦 Installing Flux CD..."
    
    # Install Flux CLI if not present
    if ! command -v flux &> /dev/null; then
        echo "Installing Flux CLI..."
        curl -s https://fluxcd.io/install.sh | bash
    fi
    
    # Bootstrap Flux (without git repo for now)
    flux install --context="${CONTEXT}" || echo "⚠️  Flux installation skipped or already exists"
    
    echo "✅ Flux CD installed"
}

# Setup GitOps directory structure
setup_gitops_structure() {
    echo "📁 Setting up GitOps directory structure..."
    
    mkdir -p "${GITOPS_DIR}"/{apps,infrastructure,clusters}
    
    # Create base kustomization
    cat > "${GITOPS_DIR}/kustomization.yaml" << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - apps
  - infrastructure
  - clusters
EOF
    
    # Create apps structure
    cat > "${GITOPS_DIR}/apps/kustomization.yaml" << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: []
EOF
    
    # Create infrastructure structure
    cat > "${GITOPS_DIR}/infrastructure/kustomization.yaml" << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources: []
EOF
    
    # Create clusters structure
    cat > "${GITOPS_DIR}/clusters/${CLUSTER_NAME}/kustomization.yaml" << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../apps
  - ../../infrastructure
EOF
    
    echo "✅ GitOps structure created at ${GITOPS_DIR}"
}

# Create example application manifest
create_example_app() {
    echo "📝 Creating example application manifests..."
    
    mkdir -p "${GITOPS_DIR}/apps/nginx-example"
    
    cat > "${GITOPS_DIR}/apps/nginx-example/deployment.yaml" << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-example
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.24
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-example
  namespace: default
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF
    
    cat > "${GITOPS_DIR}/apps/nginx-example/kustomization.yaml" << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
EOF
    
    # Update apps kustomization
    cat > "${GITOPS_DIR}/apps/kustomization.yaml" << 'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - nginx-example
EOF
    
    echo "✅ Example application created"
}

# Setup ArgoCD application
setup_argocd_app() {
    echo "🎯 Configuring ArgoCD application..."
    
    cat > /tmp/argocd-app.yaml << EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ${CLUSTER_NAME}-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: ${GITOPS_REPO:-file://${PWD}/${GITOPS_DIR}}
    targetRevision: HEAD
    path: clusters/${CLUSTER_NAME}
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
EOF
    
    kubectl apply -f /tmp/argocd-app.yaml --context="${CONTEXT}" 2>/dev/null || echo "⚠️  ArgoCD app configuration skipped"
    rm -f /tmp/argocd-app.yaml
    
    echo "✅ ArgoCD configured"
}

# Get ArgoCD credentials
get_argocd_credentials() {
    echo ""
    echo "🔐 ArgoCD Access Information:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Get initial admin password
    local password=$(kubectl -n argocd get secret argocd-initial-admin-secret \
        -o jsonpath="{.data.password}" --context="${CONTEXT}" 2>/dev/null | base64 -d 2>/dev/null || echo "Password not available yet")
    
    echo "  Username: admin"
    echo "  Password: ${password}"
    echo ""
    echo "  Port Forward: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    echo "  Access URL:   https://localhost:8080"
    echo ""
}

# Main setup flow
main() {
    # Choose GitOps tool
    local gitops_tool="${1:-argocd}"
    
    case "${gitops_tool}" in
        argocd)
            install_argocd
            setup_gitops_structure
            create_example_app
            setup_argocd_app
            get_argocd_credentials
            ;;
        flux)
            install_flux
            setup_gitops_structure
            create_example_app
            ;;
        both)
            install_argocd
            install_flux
            setup_gitops_structure
            create_example_app
            setup_argocd_app
            get_argocd_credentials
            ;;
        *)
            echo "❌ Unknown GitOps tool: ${gitops_tool}"
            echo "Available options: argocd, flux, both"
            exit 1
            ;;
    esac
    
    echo ""
    echo "✅ GitOps workflow integration complete!"
    echo ""
    echo "📚 Next steps:"
    echo "  1. Review GitOps manifests in: ${GITOPS_DIR}"
    echo "  2. Connect to your Git repository"
    echo "  3. Configure sync policies"
    echo "  4. Deploy applications via GitOps"
    echo ""
    echo "🔧 Useful commands:"
    echo "  • Apply manifests:       kubectl apply -k ${GITOPS_DIR}/clusters/${CLUSTER_NAME}"
    echo "  • ArgoCD CLI:            argocd app list"
    echo "  • Flux status:           flux get all"
}

# Run main with arguments
main "${@}"
