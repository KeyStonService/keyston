#!/bin/bash
set -e

echo "🏝️ Starting v2-multi-islands Development Session..."

# Check if we're in the right directory
cd /workspace

# Start supporting services (if not already running)
echo "🔄 Ensuring supporting services are running..."
docker-compose -f config/dev/docker-compose.yml up -d postgres redis prometheus grafana 2>/dev/null || true

# Wait a moment for services to initialize
sleep 5

# Check if we can connect to essential services
echo "🔍 Checking essential service connectivity..."

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
echo "🏝️ v2-multi-islands Development Environment Ready!"
echo "=================================================="
echo ""
echo "📊 Monitoring & Observability:"
echo "  • Prometheus:     http://localhost:9090"
echo "  • Grafana:        http://localhost:3000 (admin/consciousness_2024)"
echo ""
echo "🗄️ Data Services:"
echo "  • PostgreSQL:     localhost:5432 (life_admin/consciousness_2024)"
echo "  • Redis:          localhost:6379"
echo ""
echo "🏝️ v2-multi-islands Quick Start:"
echo "  • Run v2 (auto mode):    python3 main.py --mode=auto"
echo "  • Run Python island:     python3 main.py --island=python"
echo "  • Run Rust island:       python3 main.py --island=rust"
echo "  • Run Go island:         python3 main.py --island=go"
echo "  • Run TypeScript island: python3 main.py --island=typescript"
echo "  • Run Java island:       python3 main.py --island=java"
echo "  • Run all islands:       python3 main.py --all"
echo ""
echo "🌐 Available Islands:"
echo "  • 🦀 Rust: Performance core (性能核心島)"
echo "  • 🌊 Go: Cloud-native services (雲原生服務島)"
echo "  • ⚡ TypeScript: Full-stack development (全棧開發島)"
echo "  • 🐍 Python: AI & data (AI 數據島)"
echo "  • ☕ Java: Enterprise services (企業服務島)"
echo ""
echo "📚 Key Files:"
echo "  • Main entry:     ./main.py"
echo "  • Configuration:  ./config/island_config.py"
echo "  • Orchestrator:   ./orchestrator/island_orchestrator.py"
echo "  • Islands:        ./islands/"
echo ""
echo "🔗 From repo root, you can also run:"
echo "  • /workspace/tools/scripts/run-v2.sh"
echo ""

# Optional: Auto-start v2 system (uncomment if desired)
# echo "🤖 Auto-starting v2 system..."
# python3 main.py --mode=auto

echo "✨ v2-multi-islands development session initialized!"
