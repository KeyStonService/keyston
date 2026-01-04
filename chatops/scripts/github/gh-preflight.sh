#!/bin/bash

# GitHub Repository Preflight Check Script
# Performs comprehensive pre-flight checks before repository operations

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
ERROR_COUNT=0
WARNING_COUNT=0
INFO_COUNT=0

# Logging functions
log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    ((ERROR_COUNT++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNING_COUNT++))
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    ((INFO_COUNT++))
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Helper functions
check_command() {
    local cmd="$1"
    if command -v "$cmd" &> /dev/null; then
        log_success "$cmd is available"
        return 0
    else
        log_error "$cmd is not available"
        return 1
    fi
}

check_file() {
    local file="$1"
    local description="${2:-File}"
    
    if [[ -f "$file" ]]; then
        log_success "$description exists: $file"
        return 0
    else
        log_error "$description missing: $file"
        return 1
    fi
}

check_directory() {
    local dir="$1"
    local description="${2:-Directory}"
    
    if [[ -d "$dir" ]]; then
        log_success "$description exists: $dir"
        return 0
    else
        log_error "$description missing: $dir"
        return 1
    fi
}

# Main check functions
check_git_environment() {
    log_info "Checking Git environment..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        log_error "Not in a Git repository"
        return 1
    fi
    
    log_success "Git repository detected"
    
    # Check git configuration
    local git_user_name
    git_user_name=$(git config user.name || echo "")
    if [[ -z "$git_user_name" ]]; then
        log_warning "Git user.name not configured"
    else
        log_success "Git user.name: $git_user_name"
    fi
    
    local git_user_email
    git_user_email=$(git config user.email || echo "")
    if [[ -z "$git_user_email" ]]; then
        log_warning "Git user.email not configured"
    else
        log_success "Git user.email: $git_user_email"
    fi
    
    # Check remote configuration
    if git remote get-url origin &> /dev/null; then
        local remote_url
        remote_url=$(git remote get-url origin)
        log_success "Remote origin: $remote_url"
        
        # Check if token is in URL (security issue)
        if [[ "$remote_url" =~ github_pat_ ]]; then
            log_warning "GitHub token detected in remote URL - consider using environment variable"
        fi
    else
        log_warning "No remote origin configured"
    fi
}

check_required_commands() {
    log_info "Checking required commands..."
    
    local required_commands=(
        "git"
        "gh"
        "jq"
        "yq"
        "curl"
        "wget"
    )
    
    local missing_commands=0
    
    for cmd in "${required_commands[@]}"; do
        if ! check_command "$cmd"; then
            ((missing_commands++))
        fi
    done
    
    if [[ $missing_commands -gt 0 ]]; then
        log_error "$missing_commands required commands are missing"
        return 1
    fi
    
    return 0
}

check_repository_structure() {
    log_info "Checking repository structure..."
    
    # Required directories
    local required_dirs=(
        ".github/workflows"
        "ops/github"
        "scripts/github"
        ".config/policy"
        ".config/conftest/policies"
    )
    
    for dir in "${required_dirs[@]}"; do
        check_directory "$dir"
    done
    
    # Required files
    local required_files=(
        "README.md"
        "LICENSE"
        "VERSION"
        "SECURITY.md"
        "CONTRIBUTING.md"
        "Makefile"
        ".gitignore"
        ".github/workflows/ci.yaml"
        ".github/workflows/auto-fix-bot.yaml"
        ".github/workflows/conftest-naming.yaml"
        ".github/workflows/trivy-scan.yaml"
        ".github/workflows/slsa-provenance.yaml"
        ".github/workflows/sbom-upload.yaml"
        ".github/workflows/docx-artifact-build.yaml"
        "ops/github/actions-pinned-sha.yaml"
        "ops/github/workflow-permissions-matrix.yaml"
        "scripts/github/gh-preflight.sh"
        "scripts/github/apply-repo-hardening.sh"
        "scripts/github/pin-actions-sha.sh"
    )
    
    for file in "${required_files[@]}"; do
        check_file "$file"
    done
}

check_workflow_security() {
    log_info "Checking workflow security..."
    
    local workflows_dir=".github/workflows"
    
    if [[ ! -d "$workflows_dir" ]]; then
        log_error "Workflows directory not found"
        return 1
    fi
    
    # Check each workflow file
    local workflow_files=("$workflows_dir"/*.yaml "$workflows_dir"/*.yml)
    
    for workflow in "${workflow_files[@]}"; do
        if [[ -f "$workflow" ]]; then
            local workflow_name
            workflow_name=$(basename "$workflow")
            
            log_info "Checking workflow: $workflow_name"
            
            # Check for pinned SHA usage
            if grep -q "uses.*@" "$workflow"; then
                # Check if any uses statements don't have SHA
                local unpinned_actions
                unpinned_actions=$(grep "uses.*@" "$workflow" | grep -v "^[[:space:]]*#" | grep -v "@" | wc -l || echo "0")
                
                if [[ "$unpinned_actions" -gt 0 ]]; then
                    log_warning "Found $unpinned_actions unpinned actions in $workflow_name"
                else
                    log_success "All actions appear to be pinned in $workflow_name"
                fi
            fi
            
            # Check for excessive permissions
            if grep -q "permissions: write-all" "$workflow"; then
                log_error "write-all permissions found in $workflow_name"
            fi
            
            # Check for proper permissions
            if grep -q "permissions:" "$workflow"; then
                log_success "Permissions defined in $workflow_name"
            else
                log_warning "No permissions defined in $workflow_name"
            fi
        fi
    done
}

check_github_token() {
    log_info "Checking GitHub token configuration..."
    
    # Check for environment variable
    if [[ -n "${GITHUB_TOKEN:-}" ]]; then
        log_success "GITHUB_TOKEN is set"
        
        # Test token validity
        if gh auth status &> /dev/null; then
            log_success "GitHub token is valid"
            
            # Get token scopes
            local auth_info
            auth_info=$(gh auth status 2>&1 || echo "Authentication failed")
            if [[ "$auth_info" =~ "Logged in to" ]]; then
                log_success "GitHub authentication successful"
            else
                log_warning "GitHub authentication may have issues"
            fi
        else
            log_error "GitHub token validation failed"
        fi
    else
        log_warning "GITHUB_TOKEN not set in environment"
        log_info "Set GITHUB_TOKEN environment variable for full functionality"
    fi
}

check_policy_files() {
    log_info "Checking policy files..."
    
    # Check OPA policies
    local policy_dir=".config/policy"
    if [[ -d "$policy_dir" ]]; then
        local policy_files=("$policy_dir"/*.rego)
        for policy_file in "${policy_files[@]}"; do
            if [[ -f "$policy_file" ]]; then
                log_success "OPA policy found: $(basename "$policy_file")"
                
                # Basic Rego syntax check
                if grep -q "package.*{" "$policy_file"; then
                    log_success "Valid Rego package declaration in $(basename "$policy_file")"
                else
                    log_warning "Missing package declaration in $(basename "$policy_file")"
                fi
            fi
        done
    else
        log_warning "Policy directory not found: $policy_dir"
    fi
    
    # Check Conftest policies
    local conftest_dir=".config/conftest/policies"
    if [[ -d "$conftest_dir" ]]; then
        local conftest_files=("$conftest_dir"/*.rego)
        for conftest_file in "${conftest_files[@]}"; do
            if [[ -f "$conftest_file" ]]; then
                log_success "Conftest policy found: $(basename "$conftest_file")"
            fi
        done
    else
        log_warning "Conftest policy directory not found: $conftest_dir"
    fi
}

check_security_configuration() {
    log_info "Checking security configuration..."
    
    # Check actions-pinned-sha.yaml
    local pinned_sha_file="ops/github/actions-pinned-sha.yaml"
    if [[ -f "$pinned_sha_file" ]]; then
        log_success "Actions pinned SHA configuration found"
        
        # Check for required sections
        if grep -q "actions:" "$pinned_sha_file"; then
            log_success "Actions section found in pinned SHA config"
        else
            log_warning "Actions section missing in pinned SHA config"
        fi
        
        if grep -q "permissions:" "$pinned_sha_file"; then
            log_success "Permissions section found in pinned SHA config"
        else
            log_warning "Permissions section missing in pinned SHA config"
        fi
    fi
    
    # Check workflow-permissions-matrix.yaml
    local permissions_file="ops/github/workflow-permissions-matrix.yaml"
    if [[ -f "$permissions_file" ]]; then
        log_success "Workflow permissions matrix found"
        
        if grep -q "workflow_permissions:" "$permissions_file"; then
            log_success "Workflow permissions section found"
        else
            log_warning "Workflow permissions section missing"
        fi
    fi
}

check_branch_protection() {
    log_info "Checking branch protection settings..."
    
    # Only check if gh is authenticated
    if gh auth status &> /dev/null; then
        local repo_name
        repo_name=$(git remote get-url origin 2>/dev/null | sed 's|.*github.com[:/].*/||' | sed 's/\.git$//' || echo "")
        
        if [[ -n "$repo_name" ]]; then
            log_info "Checking branch protection for: $repo_name"
            
            # Check main branch protection
            local main_protection
            main_protection=$(gh api "repos/:owner/:repo/branches/main/protection" 2>/dev/null || echo "404")
            
            if [[ "$main_protection" == "404" ]]; then
                log_warning "Main branch protection not configured"
            else
                log_success "Main branch protection is configured"
                
                # Check for required status checks
                if echo "$main_protection" | jq -e '.required_status_checks' &> /dev/null; then
                    log_success "Required status checks configured"
                else
                    log_warning "Required status checks not configured"
                fi
                
                # Check for PR reviews
                if echo "$main_protection" | jq -e '.required_pull_request_reviews' &> /dev/null; then
                    log_success "PR reviews required"
                else
                    log_warning "PR reviews not required"
                fi
            fi
        else
            log_warning "Could not determine repository name"
        fi
    else
        log_warning "GitHub CLI not authenticated - skipping branch protection check"
    fi
}

generate_report() {
    log_info "Generating pre-flight check report..."
    
    local report_file="preflight-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# GitHub Repository Preflight Check Report

## Summary
- **Generated**: $(date)
- **Repository**: $(git remote get-url origin 2>/dev/null || echo "Unknown")
- **Branch**: $(git branch --show-current 2>/dev/null || echo "Unknown")
- **Commit**: $(git rev-parse HEAD 2>/dev/null || echo "Unknown")

## Results
- **Errors**: $ERROR_COUNT
- **Warnings**: $WARNING_COUNT
- **Info Messages**: $INFO_COUNT

## Status
EOF

    if [[ $ERROR_COUNT -eq 0 ]]; then
        echo "✅ **PASSED** - All critical checks passed" >> "$report_file"
    else
        echo "❌ **FAILED** - $ERROR_COUNT error(s) found" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## Recommendations" >> "$report_file"
    echo "" >> "$report_file"
    
    if [[ $ERROR_COUNT -gt 0 ]]; then
        echo "### Critical Issues (Must Fix)" >> "$report_file"
        echo "- Address all errors before proceeding" >> "$report_file"
        echo "- Ensure all required files and directories exist" >> "$report_file"
        echo "- Fix workflow security issues" >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    if [[ $WARNING_COUNT -gt 0 ]]; then
        echo "### Warnings (Should Fix)" >> "$report_file"
        echo "- Review and address warnings" >> "$report_file"
        echo "- Configure Git user settings" >> "$report_file"
        echo "- Set up branch protection" >> "$report_file"
        echo "- Review workflow permissions" >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    echo "### Best Practices" >> "$report_file"
    echo "- Regular security audits" >> "$report_file"
    echo "- Keep dependencies updated" >> "$report_file"
    echo "- Monitor workflow runs" >> "$report_file"
    echo "- Document all changes" >> "$report_file"
    
    log_success "Report generated: $report_file"
}

# Main execution
main() {
    log_info "Starting GitHub repository pre-flight check..."
    log_info "Repository root: $REPO_ROOT"
    
    # Change to repository root
    cd "$REPO_ROOT"
    
    # Run all checks
    check_git_environment
    check_required_commands
    check_repository_structure
    check_workflow_security
    check_github_token
    check_policy_files
    check_security_configuration
    check_branch_protection
    
    # Generate report
    generate_report
    
    # Final status
    echo ""
    log_info "Pre-flight check completed"
    log_info "Errors: $ERROR_COUNT, Warnings: $WARNING_COUNT, Info: $INFO_COUNT"
    
    if [[ $ERROR_COUNT -eq 0 ]]; then
        log_success "All checks passed - repository is ready for operations"
        exit 0
    else
        log_error "Found $ERROR_COUNT errors - please address before proceeding"
        exit 1
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi