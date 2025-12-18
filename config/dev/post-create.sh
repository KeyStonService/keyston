#!/bin/bash
set -e

echo "🚀 Setting up 01-core Life System Development Environment..."

# Ensure Node.js and npm are installed (Alpine Linux)
echo "🔧 Ensuring Node.js and npm are installed..."
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "📦 Installing Node.js and npm..."
    if command -v apk >/dev/null 2>&1; then
        sudo apk add --no-cache nodejs npm
    elif command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update && sudo apt-get install -y nodejs npm
    fi
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Ensure Replit CLI is installed
echo "🔧 Ensuring Replit CLI (replit) is installed..."
if ! command -v replit >/dev/null 2>&1; then
  echo "📦 Installing Replit CLI (npm -g replit)..."
  npm install -g replit
fi
echo "✅ replit: $(command -v replit 2>/dev/null || echo 'not found')"

# Ensure GitHub CLI is installed
echo "🔧 Ensuring GitHub CLI (gh) is installed..."
if ! command -v gh >/dev/null 2>&1; then
  echo "📦 Installing GitHub CLI..."
  if command -v apk >/dev/null 2>&1; then
    sudo apk add --no-cache github-cli
  elif command -v apt-get >/dev/null 2>&1; then
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y gh
  else
    echo "❌ No supported package manager found (apk/apt-get). Cannot install gh automatically." >&2
    exit 1
  fi
fi
echo "✅ gh: $(gh --version 2>/dev/null | head -n 1 || echo 'not found')"

# Navigate to workspace
cd /workspace

# Install workspace dependencies with npm (not pnpm)
echo "📦 Installing workspace dependencies with npm..."
if [ -f "package.json" ]; then
    npm install
else
    echo "No workspace package.json found, skipping npm install"
fi

# Set up database initialization scripts
echo "🗄️ Setting up database initialization..."
mkdir -p config/dev/init-db
cat > config/dev/init-db/01-init-life-system.sql << 'EOF'
-- Life System Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Brain Engine Tables
CREATE TABLE IF NOT EXISTS brain_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context JSONB NOT NULL,
    decision JSONB NOT NULL,
    confidence DECIMAL(3,2),
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP,
    success BOOLEAN
);

CREATE TABLE IF NOT EXISTS brain_learning_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type VARCHAR(100) NOT NULL,
    pattern_data JSONB NOT NULL,
    effectiveness_score DECIMAL(3,2),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Heart Engine Tables
CREATE TABLE IF NOT EXISTS heart_orchestrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(100) NOT NULL,
    orchestration_data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    brain_decision_id UUID REFERENCES brain_decisions(id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS heart_resource_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_id VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    health_status VARCHAR(50) NOT NULL,
    health_data JSONB,
    last_check TIMESTAMP DEFAULT NOW()
);

-- Heartbeat Engine Tables
CREATE TABLE IF NOT EXISTS heartbeat_vitals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component VARCHAR(100) NOT NULL,
    vital_signs JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS heartbeat_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    severity VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    alert_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Consciousness Integration Tables
CREATE TABLE IF NOT EXISTS consciousness_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consciousness_level INTEGER NOT NULL,
    system_health JSONB NOT NULL,
    brain_activity JSONB,
    heart_rhythm JSONB,
    vital_signs JSONB,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_brain_decisions_created_at ON brain_decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_brain_learning_patterns_type ON brain_learning_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_heart_orchestrations_status ON heart_orchestrations(status);
CREATE INDEX IF NOT EXISTS idx_heart_resource_health_type ON heart_resource_health(resource_type);
CREATE INDEX IF NOT EXISTS idx_heartbeat_vitals_component ON heartbeat_vitals(component);
CREATE INDEX IF NOT EXISTS idx_heartbeat_alerts_severity ON heartbeat_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_consciousness_states_recorded_at ON consciousness_states(recorded_at);

COMMIT;
EOF

# Set up Prometheus configuration
echo "📊 Setting up Prometheus configuration..."
cat > config/dev/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'life-system-consciousness'
    static_configs:
      - targets: ['fixops-slageist:3010']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'life-system-brain'
    static_configs:
      - targets: ['brain-engine:3015']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'life-system-heart'
    static_configs:
      - targets: ['heart-engine:3018']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'life-system-heartbeat'
    static_configs:
      - targets: ['heartbeat-engine:9091']
    metrics_path: '/metrics'
    scrape_interval: 5s
EOF

# Set up Grafana configuration
echo "📈 Setting up Grafana dashboards..."
mkdir -p config/dev/grafana/{dashboards,provisioning/{dashboards,datasources}}

cat > config/dev/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

cat > config/dev/grafana/provisioning/dashboards/life-system.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'life-system'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# Create development scripts
echo "🔧 Creating development scripts..."
mkdir -p config/dev/scripts

cat > config/dev/scripts/start-life-system.sh << 'EOF'
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
EOF

chmod +x config/dev/scripts/start-life-system.sh

cat > config/dev/scripts/health-check.sh << 'EOF'
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
EOF

chmod +x config/dev/scripts/health-check.sh

# Set up Kind cluster with Podman
echo "🚀 Setting up Kind cluster with Podman..."
if [ -f "config/dev/scripts/setup-kind-cluster.sh" ]; then
    chmod +x config/dev/scripts/setup-kind-cluster.sh
    if ! bash config/dev/scripts/setup-kind-cluster.sh; then
        echo "⚠️  Kind cluster setup failed. Troubleshooting steps:"
        echo "   1. Check Podman status: podman ps -a"
        echo "   2. View logs: podman logs <container_name>"
        echo "   3. Manual retry: config/dev/scripts/setup-kind-cluster.sh"
        echo "   4. See: config/dev/VALIDATION_CHECKLIST.md for more help"
    fi
else
    echo "⚠️  Kind cluster setup script not found at config/dev/scripts/setup-kind-cluster.sh"
fi

# Set up environment variables for development
echo "🌍 Setting up development environment..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "📝 Created .env from template"
fi

# Install life system dependencies
echo "📦 Installing life system component dependencies..."
for component in brain heart heartbeat; do
    component_dir="01-core/$component/$component-L1"
    if [ -f "$component_dir/package.json" ]; then
        echo "📦 Installing $component dependencies..."
        cd "/workspace/$component_dir"
        npm install
        cd /workspace
    fi
done

# Install FixOps SLAgeist dependencies
if [ -f "01-core/lifecycle/fixops-slageist/fixops-slageist-L1/package.json" ]; then
    echo "📦 Installing FixOps SLAgeist dependencies..."
    cd /workspace/01-core/lifecycle/fixops-slageist/fixops-slageist-L1
    npm install
    cd /workspace
fi

echo "✅ Post-create setup completed!"
echo ""
echo "🚀 Quick Start Commands:"
echo "  • Start Life System: config/dev/scripts/start-life-system.sh"
echo "  • Health Check: config/dev/scripts/health-check.sh"
echo "  • Manual Start: bash start-life-system.sh"
echo ""
echo "☸️  Kubernetes Kind Cluster:"
echo "  • Cluster Name: governance-test"
echo "  • Check Status: kubectl get nodes"
echo "  • List Clusters: kind get clusters"
echo "  • Delete Cluster: kind delete cluster --name governance-test"
echo ""
echo "🔗 Service URLs (after startup):"
echo "  • Consciousness: http://localhost:3010"
echo "  • Brain Engine: http://localhost:3015"
echo "  • Heart Engine: http://localhost:3018"
echo "  • Heartbeat Engine: http://localhost:3020"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3000"