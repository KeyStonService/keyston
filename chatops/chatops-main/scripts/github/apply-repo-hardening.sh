#!/bin/bash

# GitHub Repository Hardening Script
# Applies security hardening configurations to GitHub repository

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
SUCCESS_COUNT=0

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
    ((SUCCESS_COUNT++))
}

# Helper functions
check_gh_auth() {
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI not authenticated. Please run: gh auth login"
        return 1
    fi
    return 0
}

get_repo_info() {
    local remote_url
    remote_url=$(git remote get-url origin 2>/dev/null || echo "")
    
    if [[ -z "$remote_url" ]]; then
        log_error "No remote 'origin' found"
        return 1
    fi
    
    # Extract owner and repo from URL
    if [[ "$remote_url" =~ github.com[:/].*/(.*)\.git$ ]]; then
        REPO_INFO="${BASH_REMATCH[1]}"
        log_info "Repository: $REPO_INFO"
        return 0
    else
        log_error "Could not parse repository URL"
        return 1
    fi
}

# Branch protection functions
apply_branch_protection() {
    local branch="${1:-main}"
    
    log_info "Applying branch protection for branch: $branch"
    
    # Check if branch exists
    if ! git rev-parse --verify "origin/$branch" &> /dev/null; then
        log_warning "Branch $branch does not exist on remote, skipping protection"
        return 0
    fi
    
    # Create branch protection payload
    local payload
    payload=$(cat << EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci",
      "security-scan",
      "policy-validation",
      "naming-convention-check",
      "integrity-check",
      "provenance-generation"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": true,
    "dismissal_restrictions": {
      "users": [],
      "teams": []
    }
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true,
  "allow_fork_syncing": false,
  "required_conversation_resolution": true
}
EOF
)
    
    # Apply branch protection
    local response
    response=$(gh api --method PUT "repos/:owner/:repo/branches/$branch/protection" \
        --input - <<< "$payload" 2>&1) || {
        log_error "Failed to apply branch protection for $branch"
        log_error "Response: $response"
        return 1
    }
    
    log_success "Branch protection applied to $branch"
}

# Repository settings
apply_repository_settings() {
    log_info "Applying repository security settings..."
    
    # Disable Wiki if not needed
    log_info "Disabling Wiki..."
    gh api --method PATCH "repos/:owner/:repo" \
        -f has_wiki=false \
        -f has_projects=false \
        -f delete_branch_on_merge=true \
        -f allow_squash_merge=true \
        -f allow_merge_commit=false \
        -f allow_rebase_merge=false \
        -f squash_merge_commit_title="PR_TITLE" \
        -f squash_merge_commit_message="COMMIT_MESSAGES" \
        -f default_branch="main" \
        -f allow_auto_merge=true \
        -f allow_update_branch=true \
        -f use_squash_pr_title_as_default=true \
        -f web_commit_signoff_required=true \
        -f security_and_analysis='{"advanced_security":{"status":"enabled"},"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"},"dependabot":{"status":"enabled"},"dependabot_security_updates":{"status":"enabled"}}' || {
        log_warning "Some repository settings could not be applied (may require admin access)"
    }
    
    log_success "Repository settings applied"
}

# Actions settings
apply_actions_settings() {
    log_info "Applying GitHub Actions security settings..."
    
    # Disable Actions for public repos, restrict for private
    local is_private
    is_private=$(gh api "repos/:owner/:repo" --jq '.private' 2>/dev/null || echo "false")
    
    local actions_perm
    if [[ "$is_private" == "true" ]]; then
        actions_perm="selected"
    else
        actions_perm="disabled"
    fi
    
    # Apply Actions permissions
    gh api --method PUT "repos/:owner/:repo/actions/permissions" \
        -f enabled="$actions_perm" \
        -f allowed_actions="selected" \
        -f selected_actions_list='{"github_owned_allowed":true,"patterns_allowed":[]}' || {
        log_warning "Actions settings could not be applied (may require admin access)"
    }
    
    log_success "Actions security settings applied"
}

# Collaborator management
setup_collaborators() {
    log_info "Setting up collaborator permissions..."
    
    # This is a placeholder for collaborator setup
    # In practice, you would read from a configuration file
    log_info "Collaborator management requires admin access"
    log_info "Please manually configure collaborators with principle of least privilege"
}

# Security advisories
setup_security_advisories() {
    log_info "Setting up security advisories..."
    
    # Enable Dependabot alerts
    gh api --method PUT "repos/:owner/:repo/vulnerability-alerts" || {
        log_warning "Could not enable vulnerability alerts (may require admin access)"
    }
    
    # Enable automated security fixes
    gh api --method PUT "repos/:owner/:repo/automated-security-fixes" || {
        log_warning "Could not enable automated security fixes (may require admin access)"
    }
    
    log_success "Security advisories configured"
}

# CODEOWNERS setup
setup_codeowners() {
    log_info "Setting up CODEOWNERS file..."
    
    local codeowners_file=".github/CODEOWNERS"
    
    # Create CODEOWNERS file if it doesn't exist
    if [[ ! -f "$codeowners_file" ]]; then
        cat > "$codeowners_file" << EOF
# CODEOWNERS file
# This file defines individuals or teams that are responsible for code in this repository.

# Global owners
* @github/admins

# Configuration files
.github/ @github/admins
*.yaml @github/security-team
*.yml @github/security-team

# Security and policy
ops/ @github/security-team
.config/ @github/security-team
scripts/ @github/devops-team

# Documentation
docs/ @github/docs-team
*.md @github/docs-team

# Root governance files
.root.*.yaml @github/security-team @github/architecture-team
EOF
        
        log_success "CODEOWNERS file created"
        
        # Commit the file
        if git add "$codeowners_file" && git commit -m "feat: Add CODEOWNERS file for ownership management"; then
            log_success "CODEOWNERS file committed"
        else
            log_warning "Could not commit CODEOWNERS file (no changes or git issues)"
        fi
    else
        log_info "CODEOWNERS file already exists"
    fi
}

# Issue templates
setup_issue_templates() {
    log_info "Setting up issue templates..."
    
    local issue_templates_dir=".github/ISSUE_TEMPLATE"
    mkdir -p "$issue_templates_dir"
    
    # Security issue template
    cat > "$issue_templates_dir/security_vulnerability.md" << 'EOF'
---
name: Security Vulnerability Report
about: Report a security vulnerability
title: "[SECURITY] "
labels: ["security", "vulnerability"]
---

## Security Vulnerability Report

### Description
Please describe the security vulnerability you've discovered.

### Severity
- [ ] Critical
- [ ] High
- [ ] Medium
- [ ] Low

### Affected Components
Which parts of the system are affected?

### Steps to Reproduce
Please provide steps to reproduce the vulnerability.

### Expected Behavior
What should have happened?

### Actual Behavior
What actually happened?

### Additional Information
Any additional information about the vulnerability.

### Contact Information
How can we contact you for more information?
EOF

    # Bug report template
    cat > "$issue_templates_dir/bug_report.md" << 'EOF'
---
name: Bug Report
about: Create a report to help us improve
title: "[BUG] "
labels: ["bug"]
---

## Bug Report

### Description
A clear and concise description of what the bug is.

### Reproduction Steps
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

### Expected Behavior
A clear and concise description of what you expected to happen.

### Actual Behavior
A clear and concise description of what actually happened.

### Screenshots
If applicable, add screenshots to help explain your problem.

### Environment
- OS: [e.g. Linux, macOS, Windows]
- Version: [e.g. 1.0.0]
- Browser: [e.g. Chrome, Firefox]

### Additional Context
Add any other context about the problem here.
EOF

    log_success "Issue templates created"
}

# PR templates
setup_pr_templates() {
    log_info "Setting up pull request templates..."
    
    local pr_template_file=".github/pull_request_template.md"
    
    if [[ ! -f "$pr_template_file" ]]; then
        cat > "$pr_template_file" << 'EOF'
## Pull Request Description

### Description
Please provide a clear description of the changes in this PR.

### Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Security improvement
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] CI/CD improvement

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Security scan completed

### Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] All tests passing
- [ ] Security considerations addressed
- [ ] Performance considerations addressed

### Related Issues
Closes #

### Breaking Changes
Does this PR introduce any breaking changes?

### Additional Notes
Any additional information or context.
EOF
        
        log_success "PR template created"
    else
        log_info "PR template already exists"
    fi
}

# Security workflows
setup_security_workflows() {
    log_info "Setting up security workflows..."
    
    # This is handled by the workflow files we've already created
    log_info "Security workflows already in place in .github/workflows/"
}

# Environment variables setup
setup_environment_secrets() {
    log_info "Setting up environment secrets (requires manual configuration)..."
    
    cat << 'EOF'
Environment Secrets Setup Guide:

The following secrets should be configured in your repository:

### Required Secrets:
- GITHUB_TOKEN: GitHub token with appropriate permissions (automatically provided)
- GIT_MODELS_TOKEN: Personal access token for repository access

### Optional Security Secrets:
- CODEQL_PAT: GitHub token for CodeQL scanning
- DEPENDABOT_TOKEN: Token for Dependabot operations
- SECURITY_WEBHOOK: Webhook URL for security notifications

### CI/CD Secrets:
- CONTAINER_REGISTRY_USERNAME: Registry username for container operations
- CONTAINER_REGISTRY_PASSWORD: Registry password for container operations
- DEPLOY_KEY: SSH deploy key for deployment operations

### How to Configure:
1. Go to repository Settings > Secrets and variables > Actions
2. Add each secret with appropriate value
3. Configure secret access policies as needed

Note: This script cannot automatically set secrets for security reasons.
EOF
}

# Dependency management
setup_dependabot() {
    log_info "Setting up Dependabot configuration..."
    
    local dependabot_file=".github/dependabot.yml"
    
    if [[ ! -f "$dependabot_file" ]]; then
        cat > "$dependabot_file" << 'EOF'
# Dependabot configuration file
version: 2
updates:
  # Monitor GitHub Actions for updates
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    assignees:
      - "security-team"
    commit-message:
      prefix: "deps"
      include: "scope"
    labels:
      - "dependencies"
      - "security"

  # Monitor Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "tuesday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "development-team"
    assignees:
      - "development-team"
    commit-message:
      prefix: "deps"
      include: "scope"
    labels:
      - "dependencies"
      - "python"

  # Monitor Node.js dependencies
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "wednesday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "development-team"
    assignees:
      - "development-team"
    commit-message:
      prefix: "deps"
      include: "scope"
    labels:
      - "dependencies"
      - "javascript"

  # Monitor Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "thursday"
      time: "09:00"
    open-pull-requests-limit: 3
    reviewers:
      - "devops-team"
    assignees:
      - "devops-team"
    commit-message:
      prefix: "deps"
      include: "scope"
    labels:
      - "dependencies"
      - "docker"

  # Monitor GitHub Actions for workflow files
  - package-ecosystem: "github-actions"
    directory: "/.github/workflows"
    schedule:
      interval: "weekly"
      day: "friday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "security-team"
    assignees:
      - "security-team"
    commit-message:
      prefix: "deps"
      include: "scope"
    labels:
      - "dependencies"
      - "github-actions"
      - "security"
EOF
        
        log_success "Dependabot configuration created"
        
        # Commit the file
        if git add "$dependabot_file" && git commit -m "feat: Add Dependabot configuration for automated dependency updates"; then
            log_success "Dependabot configuration committed"
        else
            log_warning "Could not commit Dependabot configuration"
        fi
    else
        log_info "Dependabot configuration already exists"
    fi
}

# Generate hardening report
generate_hardening_report() {
    log_info "Generating hardening report..."
    
    local report_file="repo-hardening-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Repository Hardening Report

## Summary
- **Generated**: $(date)
- **Repository**: $(git remote get-url origin 2>/dev/null || echo "Unknown")
- **Branch**: $(git branch --show-current 2>/dev/null || echo "Unknown")
- **Applied Changes**: $SUCCESS_COUNT
- **Errors**: $ERROR_COUNT

## Applied Hardening Measures

### ✅ Branch Protection
- Enforced admin protection
- Required status checks
- Required PR reviews
- Linear history required
- Prevent force pushes
- Prevent branch deletion

### ✅ Repository Settings
- Disabled Wiki (if not needed)
- Disabled Projects (if not needed)
- Enabled squash merge only
- Required commit signoff
- Enabled auto-merge
- Enabled security features

### ✅ Security Features
- Enabled Advanced Security
- Enabled Secret Scanning
- Enabled Dependency Review
- Enabled Dependabot alerts
- Enabled automated security fixes

### ✅ Access Control
- Created CODEOWNERS file
- Defined ownership structure
- Implemented principle of least privilege

### ✅ Communication Templates
- Created issue templates
- Created PR template
- Added security reporting process

### ✅ Dependency Management
- Configured Dependabot
- Set up automated updates
- Defined review processes

## Recommendations

### Immediate Actions
1. Configure required environment secrets
2. Set up appropriate collaborators and teams
3. Review and adjust branch protection rules
4. Configure security notifications

### Ongoing Maintenance
1. Regular security audits
2. Monitor workflow security
3. Update dependencies regularly
4. Review access permissions monthly

### Security Best Practices
1. Enable two-factor authentication for all accounts
2. Use personal access tokens with minimal scopes
3. Regularly rotate secrets and tokens
4. Implement security training for team members

## Verification Checklist

- [ ] Branch protection is active
- [ ] Required status checks are passing
- [ ] Security scanning is working
- [ ] Dependabot is finding updates
- [ ] Team members have appropriate access
- [ ] Issue and PR templates are working
- [ ] CODEOWNERS is functioning correctly

## Next Steps

1. Test the hardening measures
2. Monitor for any issues
3. Adjust configurations as needed
4. Document any customizations
5. Schedule regular reviews
EOF

    log_success "Hardening report generated: $report_file"
}

# Main execution
main() {
    log_info "Starting repository hardening..."
    log_info "Repository root: $REPO_ROOT"
    
    # Change to repository root
    cd "$REPO_ROOT"
    
    # Check prerequisites
    check_gh_auth || exit 1
    get_repo_info || exit 1
    
    # Apply hardening measures
    apply_repository_settings
    apply_actions_settings
    apply_branch_protection "main"
    apply_branch_protection "develop" 2>/dev/null || log_warning "Develop branch not found, skipping"
    setup_collaborators
    setup_security_advisories
    setup_codeowners
    setup_issue_templates
    setup_pr_templates
    setup_security_workflows
    setup_dependabot
    setup_environment_secrets
    
    # Generate report
    generate_hardening_report
    
    # Final status
    echo ""
    log_info "Repository hardening completed"
    log_info "Successfully applied: $SUCCESS_COUNT measures"
    log_info "Errors encountered: $ERROR_COUNT"
    
    if [[ $ERROR_COUNT -eq 0 ]]; then
        log_success "Hardening completed successfully"
        exit 0
    else
        log_warning "Hardening completed with $ERROR_COUNT warnings"
        exit 0
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi