#!/bin/bash
# 02-modules-init.sh - Core modules initialization
# This script initializes and configures core platform modules

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/bootstrap-modules.log"
EVIDENCE_DIR="${PROJECT_ROOT}/dist/evidence"

# Source environment and logging functions
source "$SCRIPT_DIR/00-init.sh" 2>/dev/null || {
    echo "ERROR: Could not source 00-init.sh" >&2
    exit 1
}

# Step-specific logging
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[$timestamp] [02-MODULES] [$level] $message" | tee -a "$LOG_FILE"
}

# Step 1: Validate modules configuration
validate_modules_config() {
    info "Validating modules configuration..."
    
    local modules_file="$PROJECT_ROOT/root/.root.modules.yaml"
    
    if [[ ! -f "$modules_file" ]]; then
        error_exit "Modules configuration file not found: $modules_file"
    fi
    
    # Validate YAML syntax
    if ! python3 -c "import yaml; yaml.safe_load(open('$modules_file'))" 2>/dev/null; then
        error_exit "Invalid YAML syntax in modules configuration"
    fi
    
    # Check required sections
    local modules_count=$(jq -r '.spec.modules | length' "$modules_file" 2>/dev/null || echo "0")
    if [[ "$modules_count" -eq 0 ]]; then
        error_exit "No modules defined in modules configuration"
    fi
    
    success "Modules configuration validation completed"
    success "Found $modules_count modules defined"
}

# Step 2: Check module dependencies
check_module_dependencies() {
    info "Checking module dependencies..."
    
    local modules_file="$PROJECT_ROOT/root/.root.modules.yaml"
    
    # Extract all modules and their dependencies
    jq -r '.spec.modules[] | "\(.name):\(.dependencies[]? // empty)"' "$modules_file" 2>/dev/null | while IFS=: read -r module dep; do
        if [[ -n "$dep" ]]; then
            # Check if dependency module exists
            if jq -e ".spec.modules[] | select(.name == &quot;$dep&quot;)" "$modules_file" >/dev/null 2>&1; then
                success "Dependency found: $module -> $dep"
            else
                warn "Dependency not found: $module -> $dep"
            fi
        fi
    done
    
    # Check for circular dependencies (simple check)
    info "Checking for circular dependencies..."
    local circular_deps=$(jq -r '.spec.modules[] | "\(.name):\(.dependencies[]? // empty)"' "$modules_file" 2>/dev/null | while IFS=: read -r module dep; do
        if [[ -n "$dep" ]]; then
            # Check if dependency depends on this module
            if jq -e ".spec.modules[] | select(.name == &quot;$dep&quot; and .dependencies[] == &quot;$module&quot;)" "$modules_file" >/dev/null 2>&1; then
                echo "$module <-> $dep"
            fi
        fi
    done)
    
    if [[ -n "$circular_deps" ]]; then
        warn "Circular dependencies detected: $circular_deps"
    else
        success "No circular dependencies found"
    fi
}

# Step 3: Generate module manifests
generate_module_manifests() {
    info "Generating module manifests..."
    
    local modules_file="$PROJECT_ROOT/root/.root.modules.yaml"
    local manifests_dir="$PROJECT_ROOT/dist/modules"
    
    mkdir -p "$manifests_dir"
    
    # Generate ConfigMap with module configurations
    local configmap_file="$manifests_dir/modules-configmap.yaml"
    
    cat > "$configmap_file" << EOF
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: machine-native-ops-modules
  namespace: root-system
  labels:
    app.kubernetes.io/name: machine-native-ops-modules
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
data:
  modules.yaml: |
$(cat "$modules_file" | sed 's/^/    /')
  version: "$(cat "$PROJECT_ROOT/VERSION" 2>/dev/null || echo "unknown")"
  generated_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EOF
    
    # Generate module registry
    local registry_file="$manifests_dir/module-registry.yaml"
    
    cat > "$registry_file" << 'EOF'
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: module-registry
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
data:
  registry.json: |
EOF
    
    # Add module registry JSON
    jq -c '.spec.modules' "$modules_file" >> "$registry_file"
    
    # Generate module deployment placeholders
    local deployments_file="$manifests_dir/module-deployments.yaml"
    
    cat > "$deployments_file" << 'EOF'
---
# Module deployment placeholders
# These should be replaced with actual module deployments
apiVersion: apps/v1
kind: Deployment
metadata:
  name: governance-module
  namespace: root-system
  labels:
    app.kubernetes.io/name: governance-module
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: governance-module
  template:
    metadata:
      labels:
        app.kubernetes.io/name: governance-module
        app.kubernetes.io/part-of: machine-native-ops
    spec:
      serviceAccountName: governance-controller
      containers:
      - name: governance-module
        image: nginx:alpine  # Placeholder
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: governance-module
  namespace: root-system
  labels:
    app.kubernetes.io/name: governance-module
    app.kubernetes.io/part-of: machine-native-ops
spec:
  selector:
    app.kubernetes.io/name: governance-module
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  type: ClusterIP
EOF
    
    success "Module manifests generated in $manifests_dir"
}

# Step 4: Generate module health checks
generate_module_health_checks() {
    info "Generating module health checks..."
    
    local modules_file="$PROJECT_ROOT/root/.root.modules.yaml"
    local health_checks_dir="$PROJECT_ROOT/dist/health-checks"
    
    mkdir -p "$health_checks_dir"
    
    # Generate health check script
    local health_check_script="$health_checks_dir/check-modules.sh"
    
    cat > "$health_check_script" << 'EOF'
#!/bin/bash
# Module health check script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

MODULES_FILE="$PROJECT_ROOT/root/.root.modules.yaml"
NAMESPACE="root-system"

check_module_health() {
    local module_name="$1"
    local deployment_name="${module_name}-module"
    
    echo "Checking health for module: $module_name"
    
    # Check if deployment exists
    if kubectl get deployment "$deployment_name" -n "$NAMESPACE" >/dev/null 2>&1; then
        # Check deployment status
        local replicas=$(kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
        local ready_replicas=$(kubectl get deployment "$deployment_name" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        
        if [[ "$ready_replicas" == "$replicas" ]]; then
            echo "✅ $module_name: Ready ($ready_replicas/$replicas replicas)"
            return 0
        else
            echo "❌ $module_name: Not ready ($ready_replicas/$replicas replicas)"
            return 1
        fi
    else
        echo "⚠️  $module_name: Deployment not found"
        return 1
    fi
}

# Main health check
echo "Performing module health checks..."

if [[ ! -f "$MODULES_FILE" ]]; then
    echo "❌ Modules configuration file not found"
    exit 1
fi

# Get list of modules
modules=($(jq -r '.spec.modules[].name' "$MODULES_FILE"))

all_healthy=true

for module in "${modules[@]}"; do
    if ! check_module_health "$module"; then
        all_healthy=false
    fi
done

echo ""
if [[ "$all_healthy" == "true" ]]; then
    echo "✅ All modules are healthy"
    exit 0
else
    echo "❌ Some modules are not healthy"
    exit 1
fi
EOF
    
    chmod +x "$health_check_script"
    
    # Generate health check configuration
    local health_config_file="$health_checks_dir/health-config.yaml"
    
    cat > "$health_config_file" << EOF
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: module-health-config
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
data:
  health-check-interval: "30s"
  health-check-timeout: "10s"
  failure-threshold: "3"
  success-threshold: "1"
  modules.yaml: |
$(jq -r '.spec.modules[] | "- name: \(.name)\n  health_check:\n    endpoint: \(.health_check.endpoint // "/healthz")\n    initial_delay: \(.health_check.initial_delay // "30s")\n    timeout: \(.health_check.timeout // "10s")"' "$modules_file" 2>/dev/null | sed 's/^/    /')
EOF
    
    success "Module health checks generated in $health_checks_dir"
}

# Step 5: Generate module lifecycle configuration
generate_module_lifecycle() {
    info "Generating module lifecycle configuration..."
    
    local modules_file="$PROJECT_ROOT/root/.root.modules.yaml"
    local lifecycle_dir="$PROJECT_ROOT/dist/lifecycle"
    
    mkdir -p "$lifecycle_dir"
    
    # Generate lifecycle configuration
    local lifecycle_config_file="$lifecycle_dir/module-lifecycle.yaml"
    
    cat > "$lifecycle_config_file" << EOF
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: module-lifecycle-config
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
data:
  lifecycle.yaml: |
$(jq -r '.spec.lifecycle // {}' "$modules_file" | sed 's/^/    /')
  phases.yaml: |
$(jq -r '.spec.lifecycle.phases[]? | "- name: \(.name)\n  description: \(.description)\n  duration: \(.duration // "unspecified")\n  gates: \(.gates // [])"' "$modules_file" 2>/dev/null | sed 's/^/    /')
EOF
    
    success "Module lifecycle configuration generated in $lifecycle_dir"
}

# Step 6: Generate modules evidence
generate_modules_evidence() {
    info "Generating modules evidence..."
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local modules_file="$PROJECT_ROOT/root/.root.modules.yaml"
    
    # Extract modules information
    local modules_count=$(jq -r '.spec.modules | length' "$modules_file" 2>/dev/null || echo "0")
    local groups_count=$(jq -r '.spec.groups | length' "$modules_file" 2>/dev/null || echo "0")
    
    cat > "$EVIDENCE_DIR/modules-evidence.json" << EOF
    {
        "step": "02-modules-init",
        "status": "completed",
        "timestamp": "$timestamp",
        "modules": {
            "configuration_validated": true,
            "modules_defined": $modules_count,
            "groups_defined": $groups_count,
            "dependencies_checked": true,
            "manifests_generated": true,
            "health_checks_generated": true,
            "lifecycle_configured": true
        },
        "outputs": {
            "module_manifests": "dist/modules/",
            "health_checks": "dist/health-checks/",
            "lifecycle_config": "dist/lifecycle/"
        },
        "ready_modules": [
$(jq -r '.spec.modules[] | select(.entrypoint.type == "kustomize") | "      &quot;\(.name)&quot;"' "$modules_file" 2>/dev/null | paste -sd ',' -)
        ],
        "next_steps": [
            "03-super-execution-init.sh",
            "04-trust-init.sh",
            "05-provenance-init.sh"
        ]
    }
EOF
    
    success "Modules evidence generated"
}

# Main execution
main() {
    info "Starting modules initialization (02-modules-init)..."
    
    # Validate prerequisite
    if [[ ! -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        error_exit "Bootstrap state not found. Run 00-init.sh first."
    fi
    
    # Execute modules initialization steps
    validate_modules_config
    check_module_dependencies
    generate_module_manifests
    generate_module_health_checks
    generate_module_lifecycle
    generate_modules_evidence
    
    success "Modules initialization completed successfully"
    info "Ready to proceed to next bootstrap step: 03-super-execution-init.sh"
    
    # Update bootstrap state
    if [[ -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        jq --arg step "02-modules-init" \
           --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
           '.current_step = $step | .completed_steps += [$step] | .last_updated = $timestamp' \
           "$PROJECT_ROOT/.bootstrap-state.json" > "$PROJECT_ROOT/.bootstrap-state.json.tmp" && \
        mv "$PROJECT_ROOT/.bootstrap-state.json.tmp" "$PROJECT_ROOT/.bootstrap-state.json"
    fi
}

# Execute main function
main "$@"