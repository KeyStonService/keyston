#!/bin/bash

# GitHub Actions SHA Pinning Script
# Pins all GitHub Actions to specific SHA values for supply chain security

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")"
PINNED_SHA_FILE="$REPO_ROOT/ops/github/actions-pinned-sha.yaml"
WORKFLOW_DIR="$REPO_ROOT/.github/workflows"
ERROR_COUNT=0
PINNED_COUNT=0
UNPINNED_COUNT=0

# Logging functions
log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    ((ERROR_COUNT++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Helper functions
get_latest_sha() {
    local action="$1"
    local version="${2:-latest}"
    
    log_info "Getting SHA for $action@$version"
    
    # Use GitHub API to get latest SHA
    local api_url="https://api.github.com/repos/$action/commits/$version"
    local response
    response=$(curl -s -H "Accept: application/vnd.github.v3+json" "$api_url" 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        log_error "Failed to fetch SHA for $action@$version"
        return 1
    fi
    
    local sha
    sha=$(echo "$response" | jq -r '.sha' 2>/dev/null)
    
    if [[ "$sha" == "null" || -z "$sha" ]]; then
        log_error "Invalid SHA response for $action@$version"
        return 1
    fi
    
    echo "$sha"
}

get_action_version() {
    local action="$1"
    
    # Try to determine the version from the action name
    case "$action" in
        "actions/checkout")
            echo "v4"
            ;;
        "actions/setup-python")
            echo "v4"
            ;;
        "actions/setup-node")
            echo "v4"
            ;;
        "actions/upload-artifact")
            echo "v3"
            ;;
        "actions/download-artifact")
            echo "v3"
            ;;
        "github/codeql-action/upload-sarif")
            echo "v2"
            ;;
        "actions/attest-build-provenance")
            echo "v1"
            ;;
        "aquasecurity/trivy-action")
            echo "0.16.1"
            ;;
        "Anchore/scan-action")
            echo "v3"
            ;;
        "slsa-framework/slsa-github-generator")
            echo "v1.9.0"
            ;;
        "instrumenta/conftest-action")
            echo "master"
            ;;
        *)
            echo "latest"
            ;;
    esac
}

parse_workflow_actions() {
    local workflow_file="$1"
    local actions=()
    
    # Extract all uses statements from the workflow file
    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*uses:[[:space:]]*([^@]+)@?([^[:space:]]*)[[:space:]]*$ ]]; then
            local action="${BASH_REMATCH[1]}"
            local version="${BASH_REMATCH[2]}"
            
            # Skip local actions
            if [[ "$action" == "./"* || "$action" == "."* ]]; then
                continue
            fi
            
            actions+=("$action|$version")
        fi
    done < "$workflow_file"
    
    echo "${actions[@]}"
}

update_pinned_sha_file() {
    local action="$1"
    local version="$2"
    local sha="$3"
    local url="$4"
    
    log_info "Updating pinned SHA file for $action"
    
    # Check if action already exists in the file
    if grep -q "name: $action" "$PINNED_SHA_FILE" 2>/dev/null; then
        # Update existing entry
        local temp_file
        temp_file=$(mktemp)
        
        # Use yq to update the YAML (if available) or use sed as fallback
        if command -v yq &> /dev/null; then
            yq eval ".actions.$action.sha = &quot;$sha&quot;" "$PINNED_SHA_FILE" > "$temp_file"
            mv "$temp_file" "$PINNED_SHA_FILE"
        else
            # Fallback: use sed to update the SHA
            sed -i.bak "/name: $action/,/url:/s/sha: .*/sha: $sha/" "$PINNED_SHA_FILE"
            rm -f "${PINNED_SHA_FILE}.bak"
        fi
    else
        # Add new entry
        cat >> "$PINNED_SHA_FILE" << EOF

  $action:
    name: $action
    version: $version
    sha: $sha
    url: https://github.com/$action
EOF
    fi
    
    log_success "Updated SHA for $action: $sha"
}

pin_workflow_actions() {
    local workflow_file="$1"
    local workflow_name
    workflow_name=$(basename "$workflow_file")
    
    log_info "Processing workflow: $workflow_name"
    
    # Parse actions from workflow
    local actions_array
    read -ra actions_array <<< "$(parse_workflow_actions "$workflow_file")"
    
    if [[ ${#actions_array[@]} -eq 0 ]]; then
        log_info "No actions found in $workflow_name"
        return 0
    fi
    
    local temp_file
    temp_file=$(mktemp)
    local updated=false
    
    # Copy the file to temp
    cp "$workflow_file" "$temp_file"
    
    # Process each action
    for action_info in "${actions_array[@]}"; do
        local action="${action_info%|*}"
        local current_version="${action_info#*|}"
        
        log_info "Found action: $action@$current_version"
        
        # Skip if already pinned with SHA
        if [[ "$current_version" =~ ^[0-9a-f]{40}$ ]]; then
            log_info "Action $action already pinned with SHA"
            ((PINNED_COUNT++))
            continue
        fi
        
        # Determine the version to use
        local target_version
        if [[ -n "$current_version" && "$current_version" != "" ]]; then
            target_version="$current_version"
        else
            target_version=$(get_action_version "$action")
        fi
        
        # Get the latest SHA
        local sha
        sha=$(get_latest_sha "$action" "$target_version")
        
        if [[ $? -eq 0 && -n "$sha" ]]; then
            # Update the workflow file to use the SHA
            sed -i "s|uses: $action@$current_version|uses: $action@$sha|g" "$temp_file"
            
            # Update the pinned SHA file
            update_pinned_sha_file "$action" "$target_version" "$sha" "https://github.com/$action"
            
            log_success "Pinned $action to SHA: $sha"
            ((PINNED_COUNT++))
            updated=true
        else
            log_error "Failed to get SHA for $action@$target_version"
            ((UNPINNED_COUNT++))
        fi
    done
    
    # Replace the original file if updates were made
    if [[ "$updated" == true ]]; then
        mv "$temp_file" "$workflow_file"
        log_success "Updated $workflow_name with pinned SHAs"
    else
        rm -f "$temp_file"
        log_info "No updates needed for $workflow_name"
    fi
}

validate_pinned_actions() {
    log_info "Validating pinned actions..."
    
    local validation_errors=0
    
    # Check each workflow file
    local workflow_files=("$WORKFLOW_DIR"/*.yaml "$WORKFLOW_DIR"/*.yml)
    
    for workflow_file in "${workflow_files[@]}"; do
        if [[ -f "$workflow_file" ]]; then
            local workflow_name
            workflow_name=$(basename "$workflow_file")
            
            # Check for unpinned actions
            local unpinned_count
            unpinned_count=$(grep -c "uses.*@" "$workflow_file" | grep -v "uses.*@[0-9a-f]\{40\}" || echo "0")
            
            if [[ "$unpinned_count" -gt 0 ]]; then
                log_warning "Found $unpinned_count unpinned actions in $workflow_name"
                grep "uses.*@" "$workflow_file" | grep -v "uses.*@[0-9a-f]\{40\}" | while read -r line; do
                    log_warning "Unpinned: $line"
                done
                ((validation_errors++))
            else
                log_success "All actions pinned in $workflow_name"
            fi
        fi
    done
    
    if [[ $validation_errors -gt 0 ]]; then
        log_error "Validation found $validation_errors issues"
        return 1
    else
        log_success "All actions are properly pinned"
        return 0
    fi
}

update_actions_from_config() {
    log_info "Updating pinned SHAs from configuration file..."
    
    if [[ ! -f "$PINNED_SHA_FILE" ]]; then
        log_error "Pinned SHA configuration file not found: $PINNED_SHA_FILE"
        return 1
    fi
    
    # Parse actions from the config file and update if needed
    local temp_file
    temp_file=$(mktemp)
    
    # Read the configuration and update SHAs if they're outdated
    if command -v yq &> /dev/null; then
        # Use yq if available
        yq eval '.actions | to_entries[] | select(.value.sha) | .key' "$PINNED_SHA_FILE" | while read -r action; do
            if [[ -n "$action" ]]; then
                local current_sha
                current_sha=$(yq eval ".actions.$action.sha" "$PINNED_SHA_FILE")
                local version
                version=$(yq eval ".actions.$action.version" "$PINNED_SHA_FILE")
                
                log_info "Checking if SHA is current for $action@$version"
                
                # Get latest SHA
                local latest_sha
                latest_sha=$(get_latest_sha "$action" "$version")
                
                if [[ "$latest_sha" != "$current_sha" ]]; then
                    log_warning "SHA updated for $action: $current_sha -> $latest_sha"
                    update_pinned_sha_file "$action" "$version" "$latest_sha" "https://github.com/$action"
                else
                    log_info "SHA is current for $action"
                fi
            fi
        done
    else
        log_warning "yq not available, skipping automatic SHA updates"
    fi
    
    rm -f "$temp_file"
}

generate_pinning_report() {
    log_info "Generating SHA pinning report..."
    
    local report_file="action-pinning-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# GitHub Actions SHA Pinning Report

## Summary
- **Generated**: $(date)
- **Repository**: $(git remote get-url origin 2>/dev/null || echo "Unknown")
- **Workflows Processed**: $(find "$WORKFLOW_DIR" -name "*.yaml" -o -name "*.yml" | wc -l)
- **Actions Pinned**: $PINNED_COUNT
- **Actions Unpinned**: $UNPINNED_COUNT
- **Errors**: $ERROR_COUNT

## Pinned Actions
EOF

    # Add details of pinned actions
    if [[ -f "$PINNED_SHA_FILE" ]]; then
        if command -v yq &> /dev/null; then
            echo "| Action | Version | SHA | URL |" >> "$report_file"
            echo "|--------|---------|-----|-----|" >> "$report_file"
            
            yq eval '.actions | to_entries[] | [.key, .value.version, .value.sha, .value.url] | @tsv' "$PINNED_SHA_FILE" | while IFS=$'\t' read -r action version sha url; do
                echo "| $action | $version | \`${sha:0:8}...\` | [$action]($url) |" >> "$report_file"
            done
        else
            echo "Details available in: $PINNED_SHA_FILE" >> "$report_file"
        fi
    fi
    
    echo "" >> "$report_file"
    echo "## Workflow Analysis" >> "$report_file"
    echo "" >> "$report_file"
    
    # Analyze each workflow
    local workflow_files=("$WORKFLOW_DIR"/*.yaml "$WORKFLOW_DIR"/*.yml)
    for workflow_file in "${workflow_files[@]}"; do
        if [[ -f "$workflow_file" ]]; then
            local workflow_name
            workflow_name=$(basename "$workflow_file")
            
            echo "### $workflow_name" >> "$report_file"
            
            local total_actions
            total_actions=$(grep -c "uses.*@" "$workflow_file" || echo "0")
            
            local pinned_actions
            pinned_actions=$(grep -c "uses.*@[0-9a-f]\{40\}" "$workflow_file" || echo "0")
            
            local unpinned_actions
            unpinned_actions=$((total_actions - pinned_actions))
            
            echo "- Total actions: $total_actions" >> "$report_file"
            echo "- Pinned actions: $pinned_actions" >> "$report_file"
            echo "- Unpinned actions: $unpinned_actions" >> "$report_file"
            
            if [[ $unpinned_actions -gt 0 ]]; then
                echo "" >> "$report_file"
                echo "Unpinned actions:" >> "$report_file"
                grep "uses.*@" "$workflow_file" | grep -v "uses.*@[0-9a-f]\{40\}" | sed 's/^[[:space:]]*/- /' >> "$report_file"
            fi
            
            echo "" >> "$report_file"
        fi
    done
    
    echo "## Security Benefits" >> "$report_file"
    echo "" >> "$report_file"
    echo "Pinning GitHub Actions to specific SHA values provides:" >> "$report_file"
    echo "- **Supply Chain Security**: Prevents malicious code injection" >> "$report_file"
    echo "- **Reproducible Builds**: Ensures consistent behavior" >> "$report_file"
    echo "- **Version Control**: Tracks exact versions used" >> "$report_file"
    echo "- **Compliance**: Meets security audit requirements" >> "$report_file"
    echo "- **Change Detection**: Alerts on unexpected updates" >> "$report_file"
    echo "" >> "$report_file"
    echo "## Recommendations" >> "$report_file"
    echo "" >> "$report_file"
    echo "1. **Regular Updates**: Review and update SHAs monthly" >> "$report_file"
    echo "2. **Security Monitoring**: Monitor for action vulnerabilities" >> "$report_file"
    echo "3. **Automated Validation**: Include SHA validation in CI/CD" >> "$report_file"
    echo "4. **Documentation**: Document update procedures" >> "$report_file"
    echo "5. **Testing**: Test action updates before deployment" >> "$report_file"
    
    log_success "Pinning report generated: $report_file"
}

# Main execution
main() {
    local mode="${1:-pin}"
    
    log_info "GitHub Actions SHA Pinning Script"
    log_info "Repository root: $REPO_ROOT"
    log_info "Mode: $mode"
    
    # Change to repository root
    cd "$REPO_ROOT"
    
    case "$mode" in
        "pin")
            log_info "Pinning actions in workflow files..."
            
            if [[ ! -d "$WORKFLOW_DIR" ]]; then
                log_error "Workflows directory not found: $WORKFLOW_DIR"
                exit 1
            fi
            
            # Process each workflow file
            local workflow_files=("$WORKFLOW_DIR"/*.yaml "$WORKFLOW_DIR"/*.yml)
            for workflow_file in "${workflow_files[@]}"; do
                if [[ -f "$workflow_file" ]]; then
                    pin_workflow_actions "$workflow_file"
                fi
            done
            
            log_info "Action pinning completed"
            ;;
            
        "validate")
            log_info "Validating pinned actions..."
            validate_pinned_actions
            ;;
            
        "update")
            log_info "Updating SHAs from configuration..."
            update_actions_from_config
            ;;
            
        "report")
            log_info "Generating pinning report..."
            generate_pinning_report
            ;;
            
        *)
            log_error "Unknown mode: $mode"
            log_info "Usage: $0 {pin|validate|update|report}"
            exit 1
            ;;
    esac
    
    # Generate report
    generate_pinning_report
    
    # Final status
    echo ""
    log_info "SHA pinning completed"
    log_info "Actions pinned: $PINNED_COUNT"
    log_info "Actions unpinned: $UNPINNED_COUNT"
    log_info "Errors: $ERROR_COUNT"
    
    if [[ $ERROR_COUNT -eq 0 && $UNPINNED_COUNT -eq 0 ]]; then
        log_success "All actions are properly pinned"
        exit 0
    else
        log_warning "Some issues encountered during pinning"
        exit 0
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi