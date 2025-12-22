#!/bin/bash
# SuperAgent Deployment Script with Kustomize support

set -euo pipefail

# Get environment from command line argument (default to dev)
ENVIRONMENT="${1:-dev}"
IMAGE_NAME="axiom-system/super-agent"
DOCKERFILE="Dockerfile"

# Environment-specific settings
case "$ENVIRONMENT" in
    dev)
        NAMESPACE="axiom-system-dev"
        IMAGE_TAG="dev-latest"
        ;;
    staging)
        NAMESPACE="axiom-system-staging"
        IMAGE_TAG="v1.0.0-rc"
        ;;
    prod)
        NAMESPACE="axiom-system"
        IMAGE_TAG="v1.0.0"
        ;;
    *)
        echo "❌ Invalid environment: $ENVIRONMENT. Use: dev, staging, or prod"
        exit 1
        ;;
esac

echo "🚀 Deploying AAPS SuperAgent to ${ENVIRONMENT} environment..."
echo "📍 Namespace: ${NAMESPACE}"
echo "🏷️  Image Tag: ${IMAGE_TAG}"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if kustomize is available (or use kubectl with -k)
if ! command -v kustomize &> /dev/null; then
    echo "⚠️  kustomize not found, will use kubectl with -k flag"
    USE_KUBECTL_KUSTOMIZE=true
else
    echo "✅ Found kustomize"
    USE_KUBECTL_KUSTOMIZE=false
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo "❌ curl is not installed or not in PATH"
    exit 1
fi

# Build Docker image
echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

# Test Docker image
echo "🧪 Testing Docker image..."
docker run --rm -d -p 8080:8080 --name super-agent-test ${IMAGE_NAME}:${IMAGE_TAG}

# Wait for container to start
echo "⏳ Waiting for SuperAgent to start..."
sleep 10

# Test health endpoint
echo "🔍 Testing health endpoint..."
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    docker stop super-agent-test 2>/dev/null || true
    docker rm super-agent-test 2>/dev/null || true
    exit 1
fi

# Ensure python3 is available before running integration tests
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 is not installed or not in PATH"
    docker stop super-agent-test 2>/dev/null || true
    docker rm super-agent-test 2>/dev/null || true
    exit 1
fi

# Ensure python3 is available before running integration tests
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 is not installed or not in PATH"
    docker stop super-agent-test 2>/dev/null || true
    docker rm super-agent-test 2>/dev/null || true
    exit 1
fi

# Run integration tests
echo "🧪 Running integration tests..."
python3 test_super_agent.py http://localhost:8080
TEST_RESULT=$?

# Stop test container
docker stop super-agent-test 2>/dev/null || true
docker rm super-agent-test 2>/dev/null || true

if [ $TEST_RESULT -ne 0 ]; then
    echo "❌ Integration tests failed"
    exit 1
fi

echo "✅ Docker image and tests passed"

# Create namespace
echo "🏗️ Creating namespace..."
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Deploy to Kubernetes using Kustomize
echo "🚀 Deploying to Kubernetes using Kustomize..."
if [ "$USE_KUBECTL_KUSTOMIZE" = true ]; then
    kubectl apply -k k8s/overlays/${ENVIRONMENT}
else
    kustomize build k8s/overlays/${ENVIRONMENT} | kubectl apply -f -
fi

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
DEPLOYMENT_NAME="super-agent"
if [ "$ENVIRONMENT" = "dev" ]; then
    DEPLOYMENT_NAME="dev-super-agent"
elif [ "$ENVIRONMENT" = "staging" ]; then
    DEPLOYMENT_NAME="staging-super-agent"
fi

kubectl wait --for=condition=available --timeout=300s deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE}

# Verify deployment
echo "✅ Verifying deployment..."
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=super-agent
kubectl get services -n ${NAMESPACE} -l app.kubernetes.io/name=super-agent

# Test the deployed service
echo "🔍 Testing deployed service..."
SERVICE_NAME="super-agent"
if [ "$ENVIRONMENT" = "dev" ]; then
    SERVICE_NAME="dev-super-agent"
elif [ "$ENVIRONMENT" = "staging" ]; then
    SERVICE_NAME="staging-super-agent"
fi

SUPER_AGENT_IP=$(kubectl get svc ${SERVICE_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
# Test the deployed service using port-forward (ClusterIP not accessible from outside)
echo "🔍 Testing deployed service via port-forward..."
LOCAL_PORT=18080
echo "🌐 Port-forwarding service super-agent to localhost:${LOCAL_PORT}"
kubectl port-forward -n "${NAMESPACE}" svc/super-agent "${LOCAL_PORT}:8080" >/dev/null 2>&1 &
PORT_FORWARD_PID=$!

# Ensure we clean up port-forward on exit
cleanup_port_forward() {
    if kill -0 "${PORT_FORWARD_PID}" 2>/dev/null; then
        kill "${PORT_FORWARD_PID}" 2>/dev/null || true
    fi
}

# Wait for port-forward and service to be fully ready
sleep 5

if curl -f "http://127.0.0.1:${LOCAL_PORT}/health" > /dev/null 2>&1; then
    echo "✅ Service health check passed"
    
    # Run integration tests against deployed service
    echo "🧪 Running integration tests against deployed service..."
    python3 test_super_agent.py "http://127.0.0.1:${LOCAL_PORT}"
    
    if [ $? -eq 0 ]; then
        echo "✅ Integration tests passed"
    else
        echo "❌ Service health check failed"
        echo "🔍 Checking pod logs..."
        kubectl logs -n ${NAMESPACE} -l app.kubernetes.io/name=super-agent --tail=20
        exit 1
        echo "⚠️  Integration tests had issues, but deployment succeeded"
    fi
else
    echo "❌ Service health check failed"
    echo "🔍 Checking pod logs..."
    kubectl logs -n ${NAMESPACE} -l app=super-agent --tail=20
    cleanup_port_forward
    exit 1
fi

cleanup_port_forward

echo ""
echo "🎉 SuperAgent deployment completed successfully!"
echo ""
echo "📋 Service Information:"
echo "  Environment: ${ENVIRONMENT}"
echo "  Namespace: ${NAMESPACE}"
echo "  Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  Service: ${SERVICE_NAME}.${NAMESPACE}.svc.cluster.local:8080"
echo ""
echo "🔍 Useful Commands:"
echo "  Check pods: kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=super-agent"
echo "  View logs: kubectl logs -n ${NAMESPACE} -l app.kubernetes.io/name=super-agent -f"
echo "  Port forward: kubectl port-forward -n ${NAMESPACE} svc/${SERVICE_NAME} 8080:8080"
echo "  Test locally: python3 test_super_agent.py http://localhost:8080"
echo ""
echo "📚 Documentation: ./README.md"
echo ""
echo "💡 Deploy to different environment:"
echo "  ./deploy.sh dev      # Deploy to dev environment"
echo "  ./deploy.sh staging  # Deploy to staging environment"
echo "  ./deploy.sh prod     # Deploy to production environment"