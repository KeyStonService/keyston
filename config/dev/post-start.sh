#!/bin/bash
set -e

echo "🌅 Starting Life System Development Session..."

# Ensure Node.js and npm are installed (Alpine Linux / Debian)
echo "🔧 Checking Node.js and npm..."
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "📦 Installing Node.js and npm..."
    if command -v apk >/dev/null 2>&1; then
        sudo apk add --no-cache nodejs npm
    elif command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y nodejs npm
    fi
fi
echo "✅ Node.js: $(node --version 2>/dev/null || echo 'not installed')"
echo "✅ npm: $(npm --version 2>/dev/null || echo 'not installed')"

# Start supporting services (if not already running)
# Check PostgreSQL
if docker-compose -f config/dev/docker-compose.yml exec -T postgres pg_isready -U life_admin -d life_system >/dev/null 2>&1; then
    echo "✅ PostgreSQL: Ready"
else
    echo "⏳ PostgreSQL: Starting up..."
fi

# Check Redis
if docker-compose -f config/dev/docker-compose.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis: Ready"
else
    echo "⏳ Redis: Starting up..."
fi

# Show connection information
echo ""
echo "🌐 Development Environment Ready!"
echo "================================="
echo ""
echo "☸️  Kubernetes Kind Cluster:"
echo "  • Cluster Name:   governance-test"
echo "  • Provider:       Podman"
echo "  • Check Status:   kubectl get nodes"
echo "  • List Clusters:  kind get clusters"
echo ""
echo "📊 Monitoring & Observability:"
echo "  • Prometheus:     http://localhost:9090"
echo "  • Grafana:        http://localhost:3000 (admin/consciousness_2024)"
echo ""
echo "🗄️ Data Services:"
echo "  • PostgreSQL:     localhost:5432 (life_admin/consciousness_2024)"
echo "  • Redis:          localhost:6379"
echo ""
echo "🧠💓 Life System APIs (will be available after startup):"
echo "  • Consciousness:  http://localhost:3010"
echo "  • Brain Engine:   http://localhost:3015"
echo "  • Heart Engine:   http://localhost:3018"
echo "  • Heartbeat:      http://localhost:3020"
echo ""
echo "🚀 Quick Commands:"
echo "  • Start Life System:    bash start-life-system.sh"
echo "  • Health Check:         config/dev/scripts/health-check.sh"
echo "  • Stop Services:        docker-compose -f config/dev/docker-compose.yml down"
echo "  • Setup Kind Cluster:   config/dev/scripts/setup-kind-cluster.sh"
echo ""
echo "📚 Key Files:"
echo "  • Life System Start:    ./start-life-system.sh"
echo "  • Component Scripts:    ./01-core/*/start-*.sh"
echo "  • Configuration:        ./.env"
echo ""

# Optional: Auto-start life system (uncomment if desired)
# echo "🤖 Auto-starting life system..."
# bash start-life-system.sh

echo "✨ Development session initialized. Ready for life system development!"