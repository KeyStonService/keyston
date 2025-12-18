#!/bin/bash

echo "🔍 Life System Health Check"
echo "=========================="

# Function to check service
check_service() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    if curl -s "$url" | grep -q "$expected"; then
        echo "✅ $name: Healthy"
    else
        echo "❌ $name: Unhealthy"
    fi
}

# Check supporting services
echo "📊 Supporting Services:"
check_service "PostgreSQL" "pg_isready -h localhost -U life_admin" "accepting connections"
check_service "Redis" "redis-cli ping" "PONG"
check_service "Prometheus" "http://localhost:9090/-/healthy" "Prometheus"

echo ""
echo "🧠💓 Life System Components:"
check_service "Brain Engine" "http://localhost:3015/health" "healthy"
check_service "Heart Engine" "http://localhost:3018/health" "healthy"
check_service "Heartbeat Engine" "http://localhost:3020/health" "healthy"
check_service "Consciousness" "http://localhost:3010/health" "healthy"

echo ""
echo "🔗 System Connectivity:"
check_service "Brain-Consciousness" "http://localhost:3015/api/consciousness/status" "connected"
check_service "Heart-Brain" "http://localhost:3018/api/brain/status" "connected"
check_service "Heartbeat-All" "http://localhost:3020/api/system/status" "monitoring"
