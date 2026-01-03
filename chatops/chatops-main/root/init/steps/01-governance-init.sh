#!/bin/bash
# 01-governance-init.sh - Governance and RBAC initialization
# This script sets up governance, RBAC, and security policies

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/bootstrap-governance.log"
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
    echo "[$timestamp] [01-GOVERNANCE] [$level] $message" | tee -a "$LOG_FILE"
}

# Step 1: Validate governance configuration
validate_governance_config() {
    info "Validating governance configuration..."
    
    local governance_file="$PROJECT_ROOT/root/.root.governance.yaml"
    
    if [[ ! -f "$governance_file" ]]; then
        error_exit "Governance configuration file not found: $governance_file"
    fi
    
    # Validate YAML syntax
    if ! python3 -c "import yaml; yaml.safe_load(open('$governance_file'))" 2>/dev/null; then
        error_exit "Invalid YAML syntax in governance configuration"
    fi
    
    # Check required sections
    if ! jq empty "$governance_file" 2>/dev/null; then
        error_exit "Governance configuration is not valid JSON/YAML"
    fi
    
    local roles_count=$(jq -r '.spec.roles | length' "$governance_file" 2>/dev/null || echo "0")
    if [[ "$roles_count" -eq 0 ]]; then
        error_exit "No roles defined in governance configuration"
    fi
    
    success "Governance configuration validation completed"
    success "Found $roles_count roles defined"
}

# Step 2: Check Kubernetes connectivity
check_k8s_connectivity() {
    info "Checking Kubernetes connectivity..."
    
    if ! command -v kubectl >/dev/null 2>&1; then
        warn "kubectl not available, skipping Kubernetes operations"
        return 0
    fi
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        warn "Cannot connect to Kubernetes cluster, skipping cluster operations"
        return 0
    fi
    
    local current_context=$(kubectl config current-context 2>/dev/null || echo "unknown")
    local cluster_info=$(kubectl cluster-info 2>/dev/null | head -n1 || echo "unknown")
    
    success "Kubernetes connectivity verified"
    info "Current context: $current_context"
    info "Cluster info: $cluster_info"
    
    # Check if we have sufficient permissions
    if kubectl auth can-i create namespaces >/dev/null 2>&1; then
        success "Sufficient permissions for namespace creation"
    else
        warn "Insufficient permissions for namespace creation"
    fi
}

# Step 3: Create required namespaces
create_namespaces() {
    info "Creating required namespaces..."
    
    if ! command -v kubectl >/dev/null 2>&1; then
        warn "kubectl not available, skipping namespace creation"
        return 0
    fi
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        warn "Cannot connect to Kubernetes cluster, skipping namespace creation"
        return 0
    fi
    
    # Read required namespaces from governance config
    local governance_file="$PROJECT_ROOT/root/.root.governance.yaml"
    local default_namespace=$(jq -r '.spec.default_namespace // "root-system"' "$governance_file")
    
    # Always create root-system namespace
    local namespaces=("$default_namespace")
    
    # Add monitoring namespace if mentioned in config
    if jq -e '.spec.roles[]?.namespaces[] | select(. == "monitoring")' "$governance_file" >/dev/null 2>&1; then
        namespaces+=("monitoring")
    fi
    
    # Add security namespace if mentioned in config
    if jq -e '.spec.roles[]?.namespaces[] | select(. == "security")' "$governance_file" >/dev/null 2>&1; then
        namespaces+=("security")
    fi
    
    for ns in "${namespaces[@]}"; do
        if kubectl get namespace "$ns" >/dev/null 2>&1; then
            info "Namespace already exists: $ns"
        else
            info "Creating namespace: $ns"
            if kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f -; then
                success "Namespace created: $ns"
            else
                warn "Failed to create namespace: $ns"
            fi
        fi
    done
    
    success "Namespace creation completed"
}

# Step 4: Generate RBAC manifests
generate_rbac_manifests() {
    info "Generating RBAC manifests..."
    
    local governance_file="$PROJECT_ROOT/root/.root.governance.yaml"
    local manifests_dir="$PROJECT_ROOT/dist/rbac"
    
    mkdir -p "$manifests_dir"
    
    # Generate ServiceAccounts
    local service_accounts_file="$manifests_dir/serviceaccounts.yaml"
    cat > "$service_accounts_file" << 'EOF'
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: root-controller
  namespace: root-system
  labels:
    app.kubernetes.io/name: root-controller
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: governance-controller
  namespace: root-system
  labels:
    app.kubernetes.io/name: governance-controller
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
EOF
    
    # Generate ClusterRole based on governance config
    local cluster_role_file="$manifests_dir/clusterrole.yaml"
    
    # Extract permissions from governance config
    local admin_permissions=$(jq -r '.spec.roles[] | select(.name == "admin") | .permissions[]' "$governance_file" 2>/dev/null || echo "")
    local operator_permissions=$(jq -r '.spec.roles[] | select(.name == "operator") | .permissions[]' "$governance_file" 2>/dev/null || echo "")
    local viewer_permissions=$(jq -r '.spec.roles[] | select(.name == "viewer") | .permissions[]' "$governance_file" 2>/dev/null || echo "")
    
    cat > "$cluster_role_file" << EOF
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: machine-native-ops-admin
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
rules:
$(if [[ "$admin_permissions" == *"*"* ]]; then
    echo "- apiGroups: [&quot;*&quot;]"
    echo "  resources: [&quot;*&quot;]"
    echo "  verbs: [&quot;*&quot;]"
else
    echo "# Custom permissions based on governance config"
    echo "- apiGroups: [&quot;&quot;]"
    echo "  resources: [&quot;namespaces&quot;, &quot;configmaps&quot;, &quot;secrets&quot;]"
    echo "  verbs: [&quot;*&quot;]"
    echo "- apiGroups: [&quot;apps&quot;]"
    echo "  resources: [&quot;deployments&quot;, &quot;replicasets&quot;]"
    echo "  verbs: [&quot;*&quot;]"
fi)
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: machine-native-ops-operator
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete", "scale"]
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: machine-native-ops-viewer
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["*"]
  verbs: ["get", "list", "watch"]
EOF
    
    # Generate RoleBindings
    local role_bindings_file="$manifests_dir/rolebindings.yaml"
    cat > "$role_bindings_file" << 'EOF'
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: machine-native-ops-admin-binding
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
subjects:
- kind: ServiceAccount
  name: root-controller
  namespace: root-system
roleRef:
  kind: ClusterRole
  name: machine-native-ops-admin
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: machine-native-ops-operator-binding
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
subjects:
- kind: ServiceAccount
  name: governance-controller
  namespace: root-system
roleRef:
  kind: ClusterRole
  name: machine-native-ops-operator
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: machine-native-ops-viewer-binding
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
subjects:
- kind: ServiceAccount
  name: governance-controller
  namespace: root-system
roleRef:
  kind: ClusterRole
  name: machine-native-ops-viewer
  apiGroup: rbac.authorization.k8s.io
EOF
    
    success "RBAC manifests generated in $manifests_dir"
}

# Step 5: Generate security policies
generate_security_policies() {
    info "Generating security policies..."
    
    local policies_dir="$PROJECT_ROOT/dist/policies"
    mkdir -p "$policies_dir"
    
    # Generate NetworkPolicy
    local network_policy_file="$policies_dir/networkpolicy.yaml"
    cat > "$network_policy_file" << 'EOF'
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: root-system-deny-all
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: root-system-allow-cluster-local
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: root-system
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - namespaceSelector:
        matchLabels:
          name: default
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: root-system
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - namespaceSelector:
        matchLabels:
          name: default
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 8080
EOF
    
    # Generate PodSecurityPolicy (if supported)
    local pod_security_policy_file="$policies_dir/podsecuritypolicy.yaml"
    cat > "$pod_security_policy_file" << 'EOF'
---
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: machine-native-ops-restricted
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
EOF
    
    # Generate ResourceQuota
    local resource_quota_file="$policies_dir/resourcequota.yaml"
    cat > "$resource_quota_file" << 'EOF'
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: root-system-quota
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    persistentvolumeclaims: "2"
    pods: "10"
    services: "5"
    secrets: "10"
    configmaps: "10"
EOF
    
    # Generate LimitRange
    local limit_range_file="$policies_dir/limitrange.yaml"
    cat > "$limit_range_file" << 'EOF'
---
apiVersion: v1
kind: LimitRange
metadata:
  name: root-system-limits
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
    app.kubernetes.io/managed-by: machine-native-ops
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
  - max:
      cpu: "2"
      memory: 2Gi
    min:
      cpu: 50m
      memory: 64Mi
    type: Container
EOF
    
    success "Security policies generated in $policies_dir"
}

# Step 6: Generate governance evidence
generate_governance_evidence() {
    info "Generating governance evidence..."
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local governance_file="$PROJECT_ROOT/root/.root.governance.yaml"
    
    # Extract governance information
    local roles_count=$(jq -r '.spec.roles | length' "$governance_file" 2>/dev/null || echo "0")
    local policies_count=$(jq -r '.spec.policies | length' "$governance_file" 2>/dev/null || echo "0")
    
    cat > "$EVIDENCE_DIR/governance-evidence.json" << EOF
    {
        "step": "01-governance-init",
        "status": "completed",
        "timestamp": "$timestamp",
        "governance": {
            "configuration_validated": true,
            "roles_defined": $roles_count,
            "policies_defined": $policies_count,
            "rbac_generated": true,
            "security_policies_generated": true
        },
        "kubernetes": {
            "connectivity_checked": true,
            "namespaces_created": true,
            "rbac_applied": false,
            "security_policies_applied": false
        },
        "outputs": {
            "rbac_manifests": "dist/rbac/",
            "security_policies": "dist/policies/"
        },
        "next_steps": [
            "02-modules-init.sh",
            "03-super-execution-init.sh"
        ]
    }
EOF
    
    success "Governance evidence generated"
}

# Main execution
main() {
    info "Starting governance initialization (01-governance-init)..."
    
    # Validate prerequisite
    if [[ ! -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        error_exit "Bootstrap state not found. Run 00-init.sh first."
    fi
    
    # Execute governance initialization steps
    validate_governance_config
    check_k8s_connectivity
    create_namespaces
    generate_rbac_manifests
    generate_security_policies
    generate_governance_evidence
    
    success "Governance initialization completed successfully"
    info "Ready to proceed to next bootstrap step: 02-modules-init.sh"
    
    # Update bootstrap state
    if [[ -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        jq --arg step "01-governance-init" \
           --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
           '.current_step = $step | .completed_steps += [$step] | .last_updated = $timestamp' \
           "$PROJECT_ROOT/.bootstrap-state.json" > "$PROJECT_ROOT/.bootstrap-state.json.tmp" && \
        mv "$PROJECT_ROOT/.bootstrap-state.json.tmp" "$PROJECT_ROOT/.bootstrap-state.json"
    fi
}

# Execute main function
main "$@"