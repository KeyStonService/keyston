#!/bin/bash
# SuperAgent Deployment Script with Kustomize support

set -euo pipefail

# Configuration
ENVIRONMENT="${1:-dev}"  # Default to dev environment
IMAGE_NAME="machinenativeops/super-agent"
DOCKERFILE="Dockerfile"

# Environment-specific configuration
case "${ENVIRONMENT}" in
    dev)
        NAMESPACE="machinenativeops-dev"
        IMAGE_TAG="${IMAGE_TAG:-dev-latest}"
        RESOURCE_PREFIX="dev-"
        ;;
    staging)
        NAMESPACE="machinenativeops-staging"
        IMAGE_TAG="${IMAGE_TAG:-staging-v1.0.0}"
        RESOURCE_PREFIX="staging-"
        ;;
    prod)
        NAMESPACE="machinenativeops"
        IMAGE_TAG="${IMAGE_TAG:-v1.0.0}"
        RESOURCE_PREFIX="prod-"
        ;;
    *)
        echo "❌ Invalid environment: ${ENVIRONMENT}"
        echo "Usage: $0 [dev|staging|prod]"
        exit 1
        ;;
esac

SERVICE_NAME="${RESOURCE_PREFIX}super-agent"
DEPLOYMENT_NAME="${RESOURCE_PREFIX}super-agent"

echo "🚀 Deploying MachineNativeOps SuperAgent to ${ENVIRONMENT} environment..."
echo "📍 Namespace: ${NAMESPACE}"
echo "🏷️  Image Tag: ${IMAGE_TAG}"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi


# Check if kustomize is available
if ! command -v kustomize &> /dev/null; then
    echo "⚠️  kustomize is not installed, falling back to kubectl kustomize"
    KUSTOMIZE_CMD="kubectl kustomize"
else
    KUSTOMIZE_CMD="kustomize build"
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

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes using Kustomize..."
# Create temporary directory for kustomize with dynamic image tag
TMP_KUSTOMIZE_DIR="$(mktemp -d)"
cp -R "overlays/${ENVIRONMENT}/" "${TMP_KUSTOMIZE_DIR}/"
cp -R "base/" "${TMP_KUSTOMIZE_DIR}/base/"

(
  cd "${TMP_KUSTOMIZE_DIR}" || exit 1
  # Update image tag to match IMAGE_TAG environment variable
  if command -v kustomize &> /dev/null; then
    kustomize edit set image "${IMAGE_NAME}=${IMAGE_NAME}:${IMAGE_TAG}"
  else
    # Fallback: manually update kustomization.yaml
    sed -i "s|newTag:.*|newTag: ${IMAGE_TAG}|g" kustomization.yaml
  fi
  $KUSTOMIZE_CMD .
) | kubectl apply -f -

# Cleanup temporary directory
rm -rf "${TMP_KUSTOMIZE_DIR}"

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/${DEPLOYMENT_NAME} -n ${NAMESPACE}

# Verify deployment
echo "✅ Verifying deployment..."
kubectl get pods -n ${NAMESPACE} -l app=super-agent
kubectl get services -n ${NAMESPACE} -l app=super-agent

# Test the deployed service
echo "🔍 Testing deployed service..."

# Test the deployed service using port-forward (ClusterIP not accessible from outside)
echo "🔍 Testing deployed service via port-forward..."
LOCAL_PORT=18080
echo "🌐 Port-forwarding service ${SERVICE_NAME} to localhost:${LOCAL_PORT}"
kubectl port-forward -n "${NAMESPACE}" "svc/${SERVICE_NAME}" "${LOCAL_PORT}:8080" >/dev/null 2>&1 &
PORT_FORWARD_PID=$!

# Ensure we clean up port-forward on exit
cleanup_port_forward() {
    if kill -0 "${PORT_FORWARD_PID}" 2>/dev/null; then
        kill "${PORT_FORWARD_PID}" 2>/dev/null || true
    fi
}

trap cleanup_port_forward EXIT

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
        echo "⚠️  Integration tests had issues, but deployment succeeded"
        echo "🔍 Checking pod logs..."
        kubectl logs -n ${NAMESPACE} -l app=super-agent --tail=50
    fi
else
    echo "❌ Service health check failed"
    echo "🔍 Checking pod logs..."
    kubectl logs -n ${NAMESPACE} -l app=super-agent --tail=20
    exit 1
fi

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
echo "  Check pods: kubectl get pods -n ${NAMESPACE} -l app=super-agent"
echo "  View logs: kubectl logs -n ${NAMESPACE} -l app=super-agent -f"
echo "  Port forward: kubectl port-forward -n ${NAMESPACE} svc/${SERVICE_NAME} 8080:8080"
echo "  Test locally: python3 test_super_agent.py http://localhost:8080"
echo ""
echo "🔧 Kustomize Commands:"
echo "  Preview changes: kustomize build overlays/${ENVIRONMENT}"
echo "  Apply directly: kustomize build overlays/${ENVIRONMENT} | kubectl apply -f -"
echo ""
echo "📚 Documentation: ./README.md"
