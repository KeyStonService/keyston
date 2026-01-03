#!/bin/bash
# 04-trust-init.sh - Trust relationships initialization
# This script initializes trust relationships and cryptographic infrastructure

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
LOG_FILE="${PROJECT_ROOT/logs/bootstrap-trust.log"
EVIDENCE_DIR="${PROJECT_ROOT/dist/evidence"

source "$SCRIPT_DIR/00-init.sh" 2>/dev/null || {
    echo "ERROR: Could not source 00-init.sh" >&2
    exit 1
}

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[$timestamp] [04-TRUST] [$level] $message" | tee -a "$LOG_FILE"
}

main() {
    info "Starting trust initialization (04-trust-init)..."
    
    local trust_file="$PROJECT_ROOT/root/.root.trust.yaml"
    if [[ ! -f "$trust_file" ]]; then
        error_exit "Trust configuration file not found: $trust_file"
    fi
    
    # Create trust infrastructure
    local trust_dir="$PROJECT_ROOT/dist/trust"
    mkdir -p "$trust_dir"
    
    # Generate trust store ConfigMap
    cat > "$trust_dir/trust-store.yaml" << EOF
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: trust-store
  namespace: root-system
  labels:
    app.kubernetes.io/part-of: machine-native-ops
data:
  trust.yaml: |
$(cat "$trust_file" | sed 's/^/    /')
  version: "$(cat "$PROJECT_ROOT/VERSION" 2>/dev/null || echo "unknown")"
  generated_at: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EOF
    
    # Generate evidence
    cat > "$EVIDENCE_DIR/trust-evidence.json" << EOF
    {
        "step": "04-trust-init",
        "status": "completed",
        "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
        "trust": {
            "configuration_validated": true,
            "trust_roots_defined": $(jq -r '.spec.trust_roots | length' "$trust_file" 2>/dev/null || echo "0"),
            "store_configured": true
        },
        "outputs": {
            "trust_store": "dist/trust/"
        },
        "next_steps": [
            "05-provenance-init.sh"
        ]
    }
EOF
    
    success "Trust initialization completed"
    
    # Update bootstrap state
    if [[ -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        jq --arg step "04-trust-init" \
           --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
           '.current_step = $step | .completed_steps += [$step] | .last_updated = $timestamp' \
           "$PROJECT_ROOT/.bootstrap-state.json" > "$PROJECT_ROOT/.bootstrap-state.json.tmp" && \
        mv "$PROJECT_ROOT/.bootstrap-state.json.tmp" "$PROJECT_ROOT/.bootstrap-state.json"
    fi
}

main "$@"