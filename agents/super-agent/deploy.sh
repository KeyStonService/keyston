#!/bin/bash
# SuperAgent Deployment Script

set -euo pipefail

# Configuration
NAMESPACE="axiom-system"
IMAGE_NAME="axiom-system/super-agent"
IMAGE_TAG="v1.0.0"
DOCKERFILE="Dockerfile"

echo "🚀 Deploying AAPS SuperAgent..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
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

# Ensure python3 and dependencies are available before running integration tests
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 is not installed or not in PATH"
    docker stop super-agent-test
    docker rm super-agent-test
    exit 1
fi

echo "📦 Ensuring Python dependencies for integration tests..."
if ! python3 -m pip show requests > /dev/null 2>&1; then
    if ! python3 -m pip install --user requests > /dev/null 2>&1; then
        echo "❌ Failed to install Python dependency 'requests'"
        docker stop super-agent-test
        docker rm super-agent-test
        exit 1
    fi
fi
# Run integration tests
echo "🧪 Running integration tests..."
python3 test_super_agent.py http://localhost:8080
TEST_RESULT=$?

# Stop test container (with error handling)
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

# Deploy to Kubernetes
echo "🚀 Deploying to Kubernetes..."
kubectl apply -f deployment.yaml

# Wait for deployment
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/super-agent -n ${NAMESPACE}

# Verify deployment
echo "✅ Verifying deployment..."
kubectl get pods -n ${NAMESPACE} -l app=super-agent
kubectl get services -n ${NAMESPACE} -l app=super-agent

# Test the deployed service
echo "🔍 Testing deployed service..."
LOCAL_PORT=18080
echo "🌐 Port-forwarding service super-agent to localhost:${LOCAL_PORT}"
kubectl port-forward -n "${NAMESPACE}" svc/super-agent "${LOCAL_PORT}:8080" >/dev/null 2>&1 &
PORT_FORWARD_PID=$!

# Ensure we clean up port-forward on exit from this block
cleanup_port_forward() {
    if kill -0 "${PORT_FORWARD_PID}" >/dev/null 2>&1; then
        kill "${PORT_FORWARD_PID}" >/dev/null 2>&1 || true
    fi
}

# Wait a moment for port-forward and service to be fully ready
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
echo "  Namespace: ${NAMESPACE}"
echo "  Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  Service: super-agent.${NAMESPACE}.svc.cluster.local:8080"
echo ""
echo "🔍 Useful Commands:"
echo "  Check pods: kubectl get pods -n ${NAMESPACE} -l app=super-agent"
echo "  View logs: kubectl logs -n ${NAMESPACE} -l app=super-agent -f"
echo "  Port forward: kubectl port-forward -n ${NAMESPACE} svc/super-agent 8080:8080"
echo "  Test locally: python3 test_super_agent.py http://localhost:8080"
echo ""
echo "📚 Documentation: ./README.md"