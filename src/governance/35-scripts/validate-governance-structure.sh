#!/bin/bash

# SynergyMesh Governance Structure Validation Script
# 治理結構驗證腳本

set -e

GOVERNANCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="${GOVERNANCE_DIR}/scripts"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 計數器
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((CHECKS_PASSED++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((CHECKS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((CHECKS_WARNING++))
}

# 檢查 1: 驗證所有 14 個維度目錄存在
check_directories() {
    log_info "Checking for 14 governance dimension directories..."

    local dimensions=(
        "governance-architecture"
        "decision-governance"
        "change-governance"
        "risk-governance"
        "compliance-governance"
        "security-governance"
        "audit-governance"
        "process-governance"
        "performance-governance"
        "stakeholder-governance"
        "governance-tools"
        "governance-culture"
        "governance-metrics"
        "governance-improvement"
    )

    local missing=0
    for dim in "${dimensions[@]}"; do
        if [ -d "${GOVERNANCE_DIR}/${dim}" ]; then
            log_success "Directory exists: ${dim}"
        else
            log_error "Missing directory: ${dim}"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -eq 0 ]; then
        log_success "All 14 governance dimension directories exist"
    else
        log_error "Found $missing missing directories"
    fi
}

# 檢查 2: 驗證每個維度都有 README.md
check_readmes() {
    log_info "Checking for README.md in each dimension..."

    local dimensions=(
        "governance-architecture"
        "decision-governance"
        "change-governance"
        "risk-governance"
        "compliance-governance"
        "security-governance"
        "audit-governance"
        "process-governance"
        "performance-governance"
        "stakeholder-governance"
        "governance-tools"
        "governance-culture"
        "governance-metrics"
        "governance-improvement"
    )

    local missing=0
    for dim in "${dimensions[@]}"; do
        if [ -f "${GOVERNANCE_DIR}/${dim}/README.md" ]; then
            log_success "README.md exists: ${dim}/README.md"
        else
            log_error "Missing README.md: ${dim}/README.md"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -eq 0 ]; then
        log_success "All dimensions have README.md"
    else
        log_error "Found $missing missing README.md files"
    fi
}

# 檢查 3: 驗證核心索引文件存在
check_index_files() {
    log_info "Checking for governance index and mapping files..."

    if [ -f "${GOVERNANCE_DIR}/GOVERNANCE_STRUCTURE_INDEX.md" ]; then
        log_success "GOVERNANCE_STRUCTURE_INDEX.md exists"
    else
        log_error "Missing GOVERNANCE_STRUCTURE_INDEX.md"
    fi

    if [ -f "${GOVERNANCE_DIR}/GOVERNANCE_DEPENDENCY_MAP.yaml" ]; then
        log_success "GOVERNANCE_DEPENDENCY_MAP.yaml exists"
    else
        log_error "Missing GOVERNANCE_DEPENDENCY_MAP.yaml"
    fi
}

# 檢查 4: 驗證配置文件格式
check_yaml_format() {
    log_info "Checking YAML file format validity..."

    local invalid=0
    local yaml_file_list

    if command -v yq &> /dev/null; then
        # Store file list in array to avoid subshell issues
        mapfile -t yaml_file_list < <(find "${GOVERNANCE_DIR}" -name "*.yaml" -type f ! -path "*_scratch*")
        
        for file in "${yaml_file_list[@]}"; do
            if yq eval . "$file" > /dev/null 2>&1; then
                log_success "Valid YAML: $(basename "$file")"
            else
                log_error "Invalid YAML: $(basename "$file")"
                invalid=$((invalid + 1))
            fi
        done
        
        if [ $invalid -eq 0 ]; then
            log_success "All YAML files are valid"
        else
            log_error "Found $invalid invalid YAML files"
        fi
    else
        log_warning "yq not installed, skipping YAML validation"
        return
    fi
}

# 檢查 5: 驗證 README 內容引用
check_readme_references() {
    log_info "Checking README.md for proper structure..."

    local dimensions=(
        "governance-architecture"
        "decision-governance"
        "change-governance"
        "risk-governance"
        "compliance-governance"
        "security-governance"
        "audit-governance"
        "process-governance"
        "performance-governance"
        "stakeholder-governance"
        "governance-tools"
        "governance-culture"
        "governance-metrics"
        "governance-improvement"
    )

    for dim in "${dimensions[@]}"; do
        local readme="${GOVERNANCE_DIR}/${dim}/README.md"

        # 檢查必要的部分
        if grep -q "# " "$readme"; then
            log_success "Has proper header: ${dim}"
        else
            log_warning "Missing proper header: ${dim}"
        fi

        if grep -q "📁 目錄結構" "$readme" || grep -q "📁 Directory Structure" "$readme"; then
            log_success "Has directory structure: ${dim}"
        else
            log_warning "Missing directory structure documentation: ${dim}"
        fi
    done
}

# 檢查 6: 驗證依賴關係圖的完整性
check_dependency_completeness() {
    log_info "Checking dependency map completeness..."

    if [ ! -f "${GOVERNANCE_DIR}/GOVERNANCE_DEPENDENCY_MAP.yaml" ]; then
        log_error "Cannot check dependencies: GOVERNANCE_DEPENDENCY_MAP.yaml not found"
        return
    fi

    # 檢查是否定義了所有 14 個維度
    # Match dimension keys like governance_architecture, decision_governance, governance_tools, etc.
    # Only count keys under the dependencies section (before the next top-level comment)
    local dimension_count
    dimension_count=$(awk '/^dependencies:/,/^# / {if (/^  [a-z_]+:/) print}' "${GOVERNANCE_DIR}/GOVERNANCE_DEPENDENCY_MAP.yaml" | wc -l || true)

    if [ "$dimension_count" -ge 14 ]; then
        log_success "All 14 dimensions defined in dependency map"
    else
        log_error "Only found $dimension_count dimensions in dependency map (expected 14)"
    fi
}

# 檢查 7: 驗證文件交叉引用
check_cross_references() {
    log_info "Checking cross-references in documentation..."

    # 檢查 GOVERNANCE_STRUCTURE_INDEX.md 中的所有維度都被提到
    if [ -f "${GOVERNANCE_DIR}/GOVERNANCE_STRUCTURE_INDEX.md" ]; then
        local index_file="${GOVERNANCE_DIR}/GOVERNANCE_STRUCTURE_INDEX.md"

        local dimensions_in_index=$(grep -o "governance-[a-z-]*" "$index_file" | sort | uniq | wc -l)

        if [ "$dimensions_in_index" -ge 14 ]; then
            log_success "All dimensions referenced in index file"
        else
            log_warning "Only $dimensions_in_index dimensions referenced in index (expected 14)"
        fi
    fi
}

# 檢查 8: 驗證配置文件存在性
check_config_files() {
    log_info "Checking for main configuration files..."

    local config_files=(
        "governance-architecture/governance-model.yaml"
        "decision-governance/decision-framework.yaml"
        "change-governance/change-policy.yaml"
        "risk-governance/risk-policy.yaml"
        "compliance-governance/compliance-policy.yaml"
        "security-governance/security-policy.yaml"
        "audit-governance/audit-policy.yaml"
        "process-governance/process-policy.yaml"
        "performance-governance/performance-policy.yaml"
        "stakeholder-governance/stakeholder-policy.yaml"
        "governance-tools/tools-inventory.yaml"
        "governance-culture/culture-strategy.yaml"
        "governance-metrics/metrics-framework.yaml"
        "governance-improvement/improvement-policy.yaml"
    )

    local missing=0
    for config in "${config_files[@]}"; do
        if [ -f "${GOVERNANCE_DIR}/${config}" ]; then
            log_success "Config exists: ${config}"
        else
            log_warning "Config file missing: ${config} (may need to be created)"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -gt 0 ]; then
        log_warning "Found $missing missing configuration files"
    fi
}

# 主函數
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  SynergyMesh Governance Structure Validation                   ║"
    echo "║  治理結構驗證                                                   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""

    # 執行所有檢查
    check_directories
    echo ""

    check_readmes
    echo ""

    check_index_files
    echo ""

    check_yaml_format
    echo ""

    check_readme_references
    echo ""

    check_dependency_completeness
    echo ""

    check_cross_references
    echo ""

    check_config_files
    echo ""

    # 摘要
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  Validation Summary 驗證摘要                                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}Passed:${NC}   $CHECKS_PASSED"
    echo -e "${RED}Failed:${NC}   $CHECKS_FAILED"
    echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARNING"
    echo ""

    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All critical checks passed!${NC}"
        return 0
    else
        echo -e "${RED}✗ Some checks failed. Please review and fix.${NC}"
        return 1
    fi
}

# 運行主函數
main
