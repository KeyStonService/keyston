#!/bin/bash
set -e

echo "🧠💓 Starting 01-core Life System..."

# Start supporting services first
echo "🗄️ Starting supporting services..."
cd /workspace
docker-compose -f config/dev/docker-compose.yml up -d postgres redis prometheus

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose -f config/dev/docker-compose.yml exec postgres pg_isready -U life_admin -d life_system
docker-compose -f config/dev/docker-compose.yml exec redis redis-cli ping

# Start life system components
echo "🧠 Starting Brain Engine..."
cd /workspace/01-core/brain/brain-L1
npm start &

echo "💓 Starting Heart Engine..."
cd /workspace/01-core/heart/heart-L1  
npm start &

echo "💗 Starting Heartbeat Engine..."
cd /workspace/01-core/heartbeat/heartbeat-L1
npm start &

echo "🧘 Starting FixOps SLAgeist Consciousness..."
cd /workspace/01-core/lifecycle/fixops-slageist/fixops-slageist-L1
npm start &

echo "✅ Life System startup initiated. Services starting in background..."
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3000 (admin/consciousness_2024)"
echo "🧠 Brain API: http://localhost:3015"
echo "💓 Heart API: http://localhost:3018"
echo "💗 Heartbeat API: http://localhost:3020"
echo "🧘 Consciousness API: http://localhost:3010"
