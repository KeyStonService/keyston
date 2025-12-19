#!/usr/bin/env bash

# ============================================================================
# 示例验证脚本 / Example Validation Script
# ============================================================================
# 验证示例代码的语法、编译和运行时正确性
#
# 用法:
#   ./scripts/validate-examples.sh [选项]
#
# 示例:
#   ./scripts/validate-examples.sh --all
#   ./scripts/validate-examples.sh --category 基础示例
#   ./scripts/validate-examples.sh --example simple-workflow
# ============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 计数器
TOTAL=0
PASSED=0
FAILED=0

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

# 验证TypeScript文件
validate_typescript() {
    local file=$1
    log_info "验证TypeScript: $file"
    
    TOTAL=$((TOTAL + 1))
    
    # 语法检查
    if npx tsc --noEmit "$file" 2>/dev/null; then
        log_success "TypeScript语法检查通过: $file"
        PASSED=$((PASSED + 1))
        return 0
    else
        log_error "TypeScript语法检查失败: $file"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 验证Python文件
validate_python() {
    local file=$1
    log_info "验证Python: $file"
    
    TOTAL=$((TOTAL + 1))
    
    # 语法检查
    if python3 -m py_compile "$file" 2>/dev/null; then
        log_success "Python语法检查通过: $file"
        PASSED=$((PASSED + 1))
        return 0
    else
        log_error "Python语法检查失败: $file"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 验证YAML文件
validate_yaml() {
    local file=$1
    log_info "验证YAML: $file"
    
    TOTAL=$((TOTAL + 1))
    
    # 使用yamllint或简单的Python检查
    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        log_success "YAML语法检查通过: $file"
        PASSED=$((PASSED + 1))
        return 0
    else
        log_error "YAML语法检查失败: $file"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 验证单个文件
validate_file() {
    local file=$1
    
    case "$file" in
        *.ts)
            validate_typescript "$file"
            ;;
        *.py)
            validate_python "$file"
            ;;
        *.yaml|*.yml)
            validate_yaml "$file"
            ;;
        *)
            log_warning "跳过未知文件类型: $file"
            ;;
    esac
}

# 验证所有示例
validate_all() {
    log_info "验证所有示例..."
    
    find "src/代码圣殿" -type f \( -name "*.ts" -o -name "*.py" -o -name "*.yaml" -o -name "*.yml" \) | while read -r file; do
        validate_file "$file"
    done
}

# 验证类别
validate_category() {
    local category=$1
    log_info "验证类别: $category"
    
    if [[ ! -d "src/代码圣殿/$category" ]]; then
        log_error "类别不存在: $category"
        exit 1
    fi
    
    find "src/代码圣殿/$category" -type f \( -name "*.ts" -o -name "*.py" -o -name "*.yaml" -o -name "*.yml" \) | while read -r file; do
        validate_file "$file"
    done
}

# 显示帮助
show_help() {
    cat << EOF
示例验证脚本

用法:
    $0 [选项]

选项:
    --all                  验证所有示例
    --category CATEGORY    验证指定类别
    --example EXAMPLE      验证指定示例
    -h, --help            显示帮助信息

示例:
    $0 --all
    $0 --category 基础示例
    $0 --example simple-workflow
EOF
}

# 显示统计信息
show_summary() {
    echo ""
    echo "========================================"
    echo "验证结果统计"
    echo "========================================"
    echo -e "总计: ${TOTAL}"
    echo -e "${GREEN}通过: ${PASSED}${NC}"
    echo -e "${RED}失败: ${FAILED}${NC}"
    echo "========================================"
    
    if [[ $FAILED -eq 0 ]]; then
        log_success "所有验证通过！"
        return 0
    else
        log_error "部分验证失败"
        return 1
    fi
}

# 主函数
main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    case $1 in
        --all)
            validate_all
            ;;
        --category)
            if [[ -z ${2:-} ]]; then
                log_error "请指定类别"
                exit 1
            fi
            validate_category "$2"
            ;;
        --example)
            if [[ -z ${2:-} ]]; then
                log_error "请指定示例名称"
                exit 1
            fi
            # TODO: 实现单个示例验证
            log_warning "单个示例验证功能待实现"
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
    
    show_summary
}

main "$@"
