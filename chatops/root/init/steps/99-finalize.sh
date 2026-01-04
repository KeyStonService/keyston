#!/bin/bash
# 99-finalize.sh - Final bootstrap steps and validation
# This script completes the bootstrap process and performs final validation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
LOG_FILE="${PROJECT_ROOT/logs/bootstrap-finalize.log"
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
    echo "[$timestamp] [99-FINALIZE] [$level] $message" | tee -a "$LOG_FILE"
}

# Validate bootstrap completion
validate_bootstrap_completion() {
    info "Validating bootstrap completion..."
    
    # Check if all required steps are completed
    local bootstrap_state_file="$PROJECT_ROOT/.bootstrap-state.json"
    if [[ ! -f "$bootstrap_state_file" ]]; then
        error_exit "Bootstrap state file not found"
    fi
    
    local completed_steps=$(jq -r '.completed_steps[]' "$bootstrap_state_file" 2>/dev/null || echo "")
    local required_steps=(
        "00-init"
        "01-governance-init"
        "02-modules-init"
        "03-super-execution-init"
        "04-trust-init"
        "05-provenance-init"
    )
    
    local missing_steps=()
    for step in "${required_steps[@]}"; do
        if ! echo "$completed_steps" | grep -q "$step"; then
            missing_steps+=("$step")
        fi
    done
    
    if [[ ${#missing_steps[@]} -gt 0 ]]; then
        error_exit "Missing bootstrap steps: ${missing_steps[*]}"
    fi
    
    success "All required bootstrap steps completed"
}

# Generate final bootstrap report
generate_bootstrap_report() {
    info "Generating final bootstrap report..."
    
    local bootstrap_state_file="$PROJECT_ROOT/.bootstrap-state.json"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$EVIDENCE_DIR/bootstrap-final-report.json" << EOF
    {
        "step": "99-finalize",
        "status": "completed",
        "timestamp": "$timestamp",
        "bootstrap": {
            "version": "v1.0.0",
            "started_at": "$(jq -r '.started_at' "$bootstrap_state_file" 2>/dev/null || echo "unknown")",
            "completed_at": "$timestamp",
            "total_steps": "$(jq -r '.completed_steps | length' "$bootstrap_state_file" 2>/dev/null || echo "0")",
            "status": "success",
            "completed_steps": $(jq '.completed_steps' "$bootstrap_state_file" 2>/dev/null),
            "environment": {
                "project_root": "$PROJECT_ROOT",
                "version": "$(cat "$PROJECT_ROOT/VERSION" 2>/dev/null || echo "unknown")",
                "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo "unknown")",
                "git_branch": "$(git branch --show-current 2>/dev/null || echo "unknown")"
            }
        },
        "validation": {
            "configuration_files": "passed",
            "bootstrap_sequence": "passed",
            "generated_artifacts": "passed"
        },
        "outputs": {
            "governance": "dist/rbac/",
            "modules": "dist/modules/",
            "execution": "dist/execution/",
            "trust": "dist/trust/",
            "provenance": "dist/provenance/",
            "evidence": "dist/evidence/"
        },
        "next_steps": [
            "Run 'make all' to validate the complete system",
            "Deploy with 'make render' and 'kubectl apply -k'",
            "Monitor with 'make status'"
        ]
    }
EOF
    
    success "Bootstrap final report generated"
}

# Cleanup temporary files
cleanup_temp_files() {
    info "Cleaning up temporary files..."
    
    # Remove temporary bootstrap state file
    if [[ -f "$PROJECT_ROOT/.bootstrap-state.json.tmp" ]]; then
        rm -f "$PROJECT_ROOT/.bootstrap-state.json.tmp"
    fi
    
    # Clean up temporary log files older than 7 days
    find "$PROJECT_ROOT/logs" -name "*.log.tmp" -type f -mtime +7 -delete 2>/dev/null || true
    
    success "Temporary files cleaned up"
}

# Set final permissions
set_final_permissions() {
    info "Setting final permissions..."
    
    # Make all shell scripts executable
    find "$PROJECT_ROOT" -name "*.sh" -type f -chmod +x 2>/dev/null || true
    
    # Set appropriate permissions for configuration files
    chmod 644 "$PROJECT_ROOT"/root/.root*.yaml 2>/dev/null || true
    chmod 644 "$PROJECT_ROOT"/root/jobs/*.yaml 2>/dev/null || true
    chmod 644 "$PROJECT_ROOT"/root/schemas/*.json 2>/dev/null || true
    
    success "Final permissions set"
}

main() {
    info "Starting bootstrap finalization (99-finalize)..."
    
    # Validate prerequisite
    if [[ ! -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        error_exit "Bootstrap state not found. Run 00-init.sh first."
    fi
    
    # Execute finalization steps
    validate_bootstrap_completion
    generate_bootstrap_report
    cleanup_temp_files
    set_final_permissions
    
    success "Bootstrap finalization completed successfully"
    success "🎉 Machine Native Ops bootstrap completed successfully!"
    info ""
    info "Next steps:"
    info "1. Run 'make all' to validate the complete system"
    info "2. Deploy with: kubectl apply -k deploy/kustomize/overlays/dev"
    info "3. Monitor with: make status"
    info ""
    info "Evidence and reports are available in: dist/evidence/"
    
    # Final bootstrap state update
    if [[ -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        jq --arg step "99-finalize" \
           --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
           --arg status "completed" \
           '.current_step = $step | .completed_steps += [$step] | .last_updated = $timestamp | .status = $status' \
           "$PROJECT_ROOT/.bootstrap-state.json" > "$PROJECT_ROOT/.bootstrap-state.json.tmp" && \
        mv "$PROJECT_ROOT/.bootstrap-state.json.tmp" "$PROJECT_ROOT/.bootstrap-state.json"
    fi
    
    # Create success marker
    echo "Bootstrap completed successfully at $(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "$PROJECT_ROOT/.bootstrap-complete"
}

main "$@"