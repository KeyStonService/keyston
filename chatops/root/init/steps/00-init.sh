#!/bin/bash
# 00-init.sh - Environment initialization
# This script initializes the environment for Machine Native Ops bootstrap

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/bootstrap-init.log"
EVIDENCE_DIR="${PROJECT_ROOT}/dist/evidence"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$EVIDENCE_DIR"

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Success message
success() {
    log "INFO" "✅ $1"
}

# Warning message
warn() {
    log "WARN" "⚠️  $1"
}

# Info message
info() {
    log "INFO" "ℹ️  $1"
}

# Step 1: Validate environment
validate_environment() {
    info "Validating environment..."
    
    # Check if we're in a Git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        error_exit "Not in a Git repository"
    fi
    
    # Check if required directories exist
    local required_dirs=("root" "root/schemas" "root/scripts" "root/jobs")
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$PROJECT_ROOT/$dir" ]]; then
            error_exit "Required directory not found: $dir"
        fi
    done
    
    # Check if required files exist
    local required_files=(
        "root/.root.config.yaml"
        "root/.root.governance.yaml"
        "root/.root.modules.yaml"
        "Makefile"
        "VERSION"
    )
    for file in "${required_files[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
            error_exit "Required file not found: $file"
        fi
    done
    
    success "Environment validation completed"
}

# Step 2: Check tools availability
check_tools() {
    info "Checking tool availability..."
    
    local tools_with_versions=(
        "kubectl:client"
        "kustomize:version"
        "git:version"
        "jq:version"
        "python3:--version"
    )
    
    local missing_tools=()
    
    for tool_version in "${tools_with_versions[@]}"; do
        local tool="${tool_version%%:*}"
        local version_flag="${tool_version##*:}"
        
        if command -v "$tool" >/dev/null 2>&1; then
            local version_output=$("$tool" "$version_flag" 2>/dev/null | head -n1 || echo "version unknown")
            success "$tool available: $version_output"
        else
            warn "$tool not found"
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        warn "Some tools are missing: ${missing_tools[*]}"
        warn "Bootstrap will continue but some features may not work"
    else
        success "All required tools are available"
    fi
}

# Step 3: Initialize directories
initialize_directories() {
    info "Initializing directories..."
    
    local dirs=(
        "dist"
        "dist/evidence"
        "dist/manifests"
        "logs"
        "tmp"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$PROJECT_ROOT/$dir" ]]; then
            mkdir -p "$PROJECT_ROOT/$dir"
            info "Created directory: $dir"
        else
            info "Directory already exists: $dir"
        fi
    done
    
    success "Directory initialization completed"
}

# Step 4: Set up environment variables
setup_environment() {
    info "Setting up environment variables..."
    
    # Export project-specific environment variables
    export MACHINE_NATIVE_OPS_ROOT="$PROJECT_ROOT"
    export MACHINE_NATIVE_OPS_VERSION="$(cat "$PROJECT_ROOT/VERSION" 2>/dev/null || echo "unknown")"
    export MACHINE_NATIVE_OPS_LOG_LEVEL="${MACHINE_NATIVE_OPS_LOG_LEVEL:-info}"
    export MACHINE_NATIVE_OPS_NAMESPACE="${MACHINE_NATIVE_OPS_NAMESPACE:-root-system}"
    
    # Add project root to PATH if not already there
    if [[ ":$PATH:" != *":$PROJECT_ROOT/scripts:"* ]]; then
        export PATH="$PROJECT_ROOT/scripts:$PATH"
        info "Added scripts directory to PATH"
    fi
    
    # Create environment file for evidence
    cat > "$EVIDENCE_DIR/environment.json" << EOF
    {
        "machine_native_ops": {
            "root": "$PROJECT_ROOT",
            "version": "$MACHINE_NATIVE_OPS_VERSION",
            "log_level": "$MACHINE_NATIVE_OPS_LOG_LEVEL",
            "namespace": "$MACHINE_NATIVE_OPS_NAMESPACE"
        },
        "environment": {
            "user": "$(whoami)",
            "home": "$HOME",
            "shell": "$SHELL",
            "path": "$PATH"
        },
        "git": {
            "commit": "$(git rev-parse HEAD 2>/dev/null || echo "unknown")",
            "branch": "$(git branch --show-current 2>/dev/null || echo "unknown")",
            "remote": "$(git remote get-url origin 2>/dev/null || echo "unknown")",
            "is_clean": "$(git diff-index --quiet HEAD -- && echo "true" || echo "false")"
        },
        "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    }
EOF
    
    success "Environment variables setup completed"
}

# Step 5: Validate configuration files
validate_configurations() {
    info "Validating configuration files..."
    
    # Check YAML syntax for root configuration files
    local yaml_files=(
        "root/.root.config.yaml"
        "root/.root.governance.yaml"
        "root/.root.modules.yaml"
        "root/.root.super-execution.yaml"
        "root/.root.trust.yaml"
        "root/.root.provenance.yaml"
        "root/.root.integrity.yaml"
        "root/.root.bootstrap.yaml"
        "root/.root.gates.map.yaml"
    )
    
    local yaml_errors=()
    
    for file in "${yaml_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            if command -v python3 >/dev/null 2>&1; then
                if python3 -c "import yaml; yaml.safe_load(open('$PROJECT_ROOT/$file'))" 2>/dev/null; then
                    success "YAML syntax valid: $file"
                else
                    yaml_errors+=("$file")
                    error_exit "YAML syntax error in: $file"
                fi
            elif command -v yq >/dev/null 2>&1; then
                if yq eval '.' "$PROJECT_ROOT/$file" >/dev/null 2>&1; then
                    success "YAML syntax valid: $file"
                else
                    yaml_errors+=("$file")
                    error_exit "YAML syntax error in: $file"
                fi
            else
                warn "No YAML validator available, skipping syntax check for $file"
            fi
        else
            warn "Configuration file not found: $file"
        fi
    done
    
    if [[ ${#yaml_errors[@]} -eq 0 ]]; then
        success "Configuration validation completed"
    else
        error_exit "Configuration validation failed with ${#yaml_errors[@]} errors"
    fi
}

# Step 6: Generate initial evidence
generate_initial_evidence() {
    info "Generating initial evidence..."
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Create initialization evidence
    cat > "$EVIDENCE_DIR/init-evidence.json" << EOF
    {
        "step": "00-init",
        "status": "completed",
        "timestamp": "$timestamp",
        "environment": {
            "project_root": "$PROJECT_ROOT",
            "version": "$MACHINE_NATIVE_OPS_VERSION",
            "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo "unknown")",
            "git_branch": "$(git branch --show-current 2>/dev/null || echo "unknown")"
        },
        "validation": {
            "environment": "passed",
            "tools": "$( [[ ${#missing_tools[@]} -eq 0 ]] && echo "passed" || echo "warning" )",
            "directories": "passed",
            "configurations": "passed"
        },
        "next_steps": [
            "01-governance-init.sh",
            "02-modules-init.sh",
            "03-super-execution-init.sh",
            "04-trust-init.sh",
            "05-provenance-init.sh",
            "99-finalize.sh"
        ]
    }
EOF
    
    success "Initial evidence generated"
}

# Step 7: Create bootstrap state
create_bootstrap_state() {
    info "Creating bootstrap state..."
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$PROJECT_ROOT/.bootstrap-state.json" << EOF
    {
        "bootstrap_version": "v1.0.0",
        "started_at": "$timestamp",
        "current_step": "00-init",
        "status": "in_progress",
        "completed_steps": [],
        "failed_steps": [],
        "environment": {
            "project_root": "$PROJECT_ROOT",
            "version": "$MACHINE_NATIVE_OPS_VERSION"
        }
    }
EOF
    
    success "Bootstrap state created"
}

# Main execution
main() {
    info "Starting environment initialization (00-init)..."
    
    # Create evidence directory if it doesn't exist
    mkdir -p "$EVIDENCE_DIR"
    
    # Execute initialization steps
    validate_environment
    check_tools
    initialize_directories
    setup_environment
    validate_configurations
    generate_initial_evidence
    create_bootstrap_state
    
    success "Environment initialization completed successfully"
    info "Ready to proceed to next bootstrap step: 01-governance-init.sh"
    
    # Update bootstrap state
    if [[ -f "$PROJECT_ROOT/.bootstrap-state.json" ]]; then
        jq --arg step "00-init" \
           --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
           '.current_step = $step | .completed_steps += [$step] | .last_updated = $timestamp' \
           "$PROJECT_ROOT/.bootstrap-state.json" > "$PROJECT_ROOT/.bootstrap-state.json.tmp" && \
        mv "$PROJECT_ROOT/.bootstrap-state.json.tmp" "$PROJECT_ROOT/.bootstrap-state.json"
    fi
}

# Execute main function
main "$@"