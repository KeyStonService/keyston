#!/bin/bash

# SynergyMesh Governance Configuration Initializer
# 治理配置初始化腳本

set -e

GOVERNANCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  SynergyMesh Governance Configuration Initializer               ║"
echo "║  治理配置初始化                                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 生成配置模板內容的輔助函數
generate_template() {
    local config_type=$1
    local name_field=$2
    local description=$3
    
    # Validate parameters
    if [ -z "$config_type" ] || [ -z "$name_field" ] || [ -z "$description" ]; then
        echo "Error: generate_template requires all three parameters" >&2
        return 1
    fi
    
    cat << EOF
---
# PLACEHOLDER: ${config_type} Configuration
# 此文件是自動生成的佔位符，需要根據實際需求填充

version: "1.0"
lastUpdated: "2025-12-09"
status: "draft"

${name_field}:
  name: "${config_type} Name"
  description: "${description}"
EOF
    
    case "$config_type" in
        "Policy")
            cat << 'EOF'
  owner: "Policy Owner"
  approval_required: true

# TODO: Add policy details
EOF
            ;;
        "Framework")
            cat << 'EOF'
  components: []

# TODO: Add framework components
EOF
            ;;
        "System")
            cat << 'EOF'
  components: []

# TODO: Add system specifications
EOF
            ;;
        *)
            cat << 'EOF'

# TODO: Add configuration details
EOF
            ;;
    esac
}

# 為缺失的維度創建基本配置文件
create_config_if_missing() {
    local dim=$1
    local config_file=$2
    local config_type=$3

    local full_path="${GOVERNANCE_DIR}/${dim}/${config_file}"

    if [ ! -f "$full_path" ]; then
        echo "Creating $config_file for $dim..."

        case "$config_type" in
            "policy")
                generate_template "Policy" "policy" "Policy description goes here" > "$full_path"
                ;;
            "framework")
                generate_template "Framework" "framework" "Framework description goes here" > "$full_path"
                ;;
            "system")
                generate_template "System" "system" "System description goes here" > "$full_path"
                ;;
            *)
                generate_template "Configuration" "config" "Configuration description goes here" > "$full_path"
                ;;
        esac

        echo "  ✓ Created: $config_file"
    else
        echo "  → Exists: $config_file"
    fi
}

# 創建缺失的配置文件
echo "Creating main configuration files for each dimension..."
echo ""

# 維度 1
create_config_if_missing "governance-architecture" "organizational-structure.yaml" "system"
create_config_if_missing "governance-architecture" "governance-principles.yaml" "policy"

# 維度 2
create_config_if_missing "decision-governance" "decision-processes.yaml" "framework"
create_config_if_missing "decision-governance" "decision-authority-matrix.yaml" "system"

# 維度 3
create_config_if_missing "change-governance" "change-processes.yaml" "framework"
create_config_if_missing "change-governance" "change-control-matrix.yaml" "system"

# 維度 4
create_config_if_missing "risk-governance" "risk-assessment-framework.yaml" "framework"
create_config_if_missing "risk-governance" "risk-register.yaml" "system"

# 維度 5
create_config_if_missing "compliance-governance" "compliance-standards.yaml" "system"
create_config_if_missing "compliance-governance" "compliance-check-rules.yaml" "policy"

# 維度 6
create_config_if_missing "security-governance" "access-control-policy.yaml" "policy"
create_config_if_missing "security-governance" "security-audit-framework.yaml" "framework"

# 維度 7
create_config_if_missing "audit-governance" "audit-framework.yaml" "framework"
create_config_if_missing "audit-governance" "audit-plan-annual.yaml" "system"

# 維度 8
create_config_if_missing "process-governance" "process-inventory.yaml" "system"
create_config_if_missing "process-governance" "process-design-standards.yaml" "framework"

# 維度 9
create_config_if_missing "performance-governance" "kpi-framework.yaml" "framework"
create_config_if_missing "performance-governance" "performance-targets.yaml" "system"

# 維度 10
create_config_if_missing "stakeholder-governance" "stakeholder-identification.yaml" "system"
create_config_if_missing "stakeholder-governance" "stakeholder-analysis.yaml" "framework"

# 維度 11
create_config_if_missing "governance-tools" "decision-support-system.yaml" "system"
create_config_if_missing "governance-tools" "system-integration-guide.yaml" "framework"

# 維度 12
create_config_if_missing "governance-culture" "governance-values.yaml" "policy"
create_config_if_missing "governance-culture" "capability-model.yaml" "framework"

# 維度 13
create_config_if_missing "governance-metrics" "kpi-definitions.yaml" "system"
create_config_if_missing "governance-metrics" "dashboard-specification.yaml" "framework"

# 維度 14
create_config_if_missing "governance-improvement" "improvement-identification.yaml" "system"
create_config_if_missing "governance-improvement" "improvement-planning.yaml" "framework"

echo ""
echo "✓ Configuration initialization complete"
echo ""
echo "Next steps:"
echo "1. Review all generated configuration files"
echo "2. Update PLACEHOLDER configurations with actual content"
echo "3. Validate structure: ./governance/scripts/validate-governance-structure.sh"
echo "4. Commit changes: git add governance && git commit -m 'governance: Initialize 14-dimension governance structure'"
