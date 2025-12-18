#!/bin/bash
# cleanup_namespaces.sh - 自動化命名空間清理腳本
# Automated Namespace Cleanup Script
#
# 用途：清理過期、空閒或測試用的 Kubernetes 命名空間
# Purpose: Clean up expired, idle, or test Kubernetes namespaces
#
# 使用方法：
#   ./cleanup_namespaces.sh [OPTIONS]
#
# 選項：
#   -d, --dry-run     僅顯示將要刪除的命名空間，不實際刪除
#   -f, --force       強制刪除（跳過確認）
#   -l, --label       按標籤篩選命名空間
#   -a, --age         清理超過指定天數的命名空間
#   -h, --help        顯示幫助訊息

set -euo pipefail

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設值
DRY_RUN=false
FORCE=false
LABEL_SELECTOR=""
MAX_AGE_DAYS=7
PROTECTED_NAMESPACES="default kube-system kube-public kube-node-lease"

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 顯示幫助
show_help() {
    cat << EOF
命名空間清理腳本 - Namespace Cleanup Script

用法：
    ./cleanup_namespaces.sh [OPTIONS]

選項：
    -d, --dry-run           僅顯示將要刪除的命名空間，不實際刪除
    -f, --force             強制刪除（跳過確認）
    -l, --label SELECTOR    按標籤篩選命名空間 (例如: "env=test")
    -a, --age DAYS          清理超過指定天數的命名空間 (預設: 7)
    -p, --pattern PATTERN   按名稱模式匹配命名空間 (例如: "ci-*")
    -h, --help              顯示此幫助訊息

範例：
    # 預覽清理超過 7 天的測試命名空間
    ./cleanup_namespaces.sh -d -l "env=test" -a 7

    # 強制清理所有 CI 管道命名空間
    ./cleanup_namespaces.sh -f -p "ci-pipeline-*"

    # 清理空閒命名空間
    ./cleanup_namespaces.sh --pattern "temp-*" --age 1

EOF
}

# 解析命令列參數
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -l|--label)
                LABEL_SELECTOR="$2"
                shift 2
                ;;
            -a|--age)
                MAX_AGE_DAYS="$2"
                shift 2
                ;;
            -p|--pattern)
                NAME_PATTERN="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知參數: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 檢查 kubectl 是否可用
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安裝或不在 PATH 中"
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_error "無法連接到 Kubernetes 叢集"
        exit 1
    fi

    log_success "已連接到 Kubernetes 叢集"
}

# 檢查命名空間是否受保護
is_protected() {
    local ns=$1
    for protected in $PROTECTED_NAMESPACES; do
        if [[ "$ns" == "$protected" ]]; then
            return 0
        fi
    done
    return 1
}

# 獲取命名空間創建時間
get_namespace_age() {
    local ns=$1
    local creation_time
    creation_time=$(kubectl get namespace "$ns" -o jsonpath='{.metadata.creationTimestamp}')
    
    if [[ -z "$creation_time" ]]; then
        echo "0"
        return
    fi
    
    local creation_epoch
    local current_epoch
    creation_epoch=$(date -d "$creation_time" +%s 2>/dev/null || date -jf "%Y-%m-%dT%H:%M:%SZ" "$creation_time" +%s 2>/dev/null || echo "0")
    current_epoch=$(date +%s)
    
    echo $(( (current_epoch - creation_epoch) / 86400 ))
}

# 檢查命名空間是否為空
is_namespace_empty() {
    local ns=$1
    local pod_count
    pod_count=$(kubectl get pods -n "$ns" --no-headers 2>/dev/null | wc -l)
    
    if [[ "$pod_count" -eq 0 ]]; then
        return 0
    fi
    return 1
}

# 獲取要清理的命名空間列表
get_namespaces_to_cleanup() {
    local namespaces=""
    
    # 構建 kubectl 命令
    local kubectl_cmd="kubectl get namespaces -o jsonpath='{.items[*].metadata.name}'"
    
    if [[ -n "${LABEL_SELECTOR:-}" ]]; then
        kubectl_cmd="kubectl get namespaces -l $LABEL_SELECTOR -o jsonpath='{.items[*].metadata.name}'"
    fi
    
    namespaces=$(eval "$kubectl_cmd")
    
    local filtered_namespaces=""
    for ns in $namespaces; do
        # 跳過受保護的命名空間
        if is_protected "$ns"; then
            log_info "跳過受保護的命名空間: $ns"
            continue
        fi
        
        # 按名稱模式過濾
        if [[ -n "${NAME_PATTERN:-}" ]]; then
            if [[ ! "$ns" == $NAME_PATTERN ]]; then
                continue
            fi
        fi
        
        # 按年齡過濾
        local age
        age=$(get_namespace_age "$ns")
        if [[ "$age" -lt "$MAX_AGE_DAYS" ]]; then
            log_info "跳過較新的命名空間: $ns (${age} 天)"
            continue
        fi
        
        filtered_namespaces="$filtered_namespaces $ns"
    done
    
    echo "$filtered_namespaces"
}

# 刪除單個命名空間
delete_namespace() {
    local ns=$1
    
    log_info "正在刪除命名空間: $ns"
    
    if $DRY_RUN; then
        log_warning "[DRY RUN] 將刪除命名空間: $ns"
        return 0
    fi
    
    # 先刪除命名空間中的所有資源
    kubectl delete all --all -n "$ns" --grace-period=30 2>/dev/null || true
    
    # 刪除命名空間
    if kubectl delete namespace "$ns" --grace-period=60 --timeout=120s; then
        log_success "成功刪除命名空間: $ns"
        return 0
    else
        log_error "刪除命名空間失敗: $ns"
        return 1
    fi
}

# 處理卡住的命名空間
handle_stuck_namespace() {
    local ns=$1
    
    log_warning "命名空間 $ns 可能卡住，嘗試強制清理..."
    
    if $DRY_RUN; then
        log_warning "[DRY RUN] 將強制清理命名空間: $ns"
        return 0
    fi
    
    # 移除 finalizers
    kubectl get namespace "$ns" -o json | \
        jq '.spec.finalizers = []' | \
        kubectl replace --raw "/api/v1/namespaces/$ns/finalize" -f - 2>/dev/null || true
}

# 主函數
main() {
    parse_args "$@"
    
    echo "========================================"
    echo "  命名空間清理腳本"
    echo "  Namespace Cleanup Script"
    echo "========================================"
    echo ""
    
    check_kubectl
    
    log_info "配置:"
    log_info "  - Dry Run: $DRY_RUN"
    log_info "  - Force: $FORCE"
    log_info "  - Label Selector: ${LABEL_SELECTOR:-無}"
    log_info "  - Max Age: ${MAX_AGE_DAYS} 天"
    log_info "  - Name Pattern: ${NAME_PATTERN:-無}"
    echo ""
    
    # 獲取要清理的命名空間
    local namespaces
    namespaces=$(get_namespaces_to_cleanup)
    
    if [[ -z "$namespaces" ]]; then
        log_info "沒有找到需要清理的命名空間"
        exit 0
    fi
    
    log_info "找到以下命名空間需要清理:"
    for ns in $namespaces; do
        local age
        age=$(get_namespace_age "$ns")
        local empty_status="非空"
        if is_namespace_empty "$ns"; then
            empty_status="空"
        fi
        echo "  - $ns (${age} 天, $empty_status)"
    done
    echo ""
    
    # 確認刪除
    if ! $FORCE && ! $DRY_RUN; then
        read -r -p "確定要刪除這些命名空間嗎？ (y/N): " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            log_info "操作已取消"
            exit 0
        fi
    fi
    
    # 執行刪除
    local success_count=0
    local fail_count=0
    
    for ns in $namespaces; do
        if delete_namespace "$ns"; then
            ((success_count++))
        else
            ((fail_count++))
            handle_stuck_namespace "$ns"
        fi
    done
    
    echo ""
    echo "========================================"
    log_info "清理完成"
    log_success "成功: $success_count"
    if [[ $fail_count -gt 0 ]]; then
        log_error "失敗: $fail_count"
    fi
    echo "========================================"
}

# 執行主函數
main "$@"
