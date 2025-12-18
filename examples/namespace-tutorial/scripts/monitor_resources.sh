#!/bin/bash
# monitor_resources.sh - 監控命名空間資源使用腳本
# Namespace Resource Monitoring Script
#
# 用途：即時監控 Kubernetes 命名空間的資源使用情況
# Purpose: Real-time monitoring of Kubernetes namespace resource usage
#
# 使用方法：
#   ./monitor_resources.sh [OPTIONS] <namespace>
#
# 選項：
#   -i, --interval    更新間隔（秒），預設 10
#   -a, --all         監控所有命名空間
#   -o, --output      輸出格式 (table/json/csv)
#   -w, --watch       持續監控模式
#   -h, --help        顯示幫助訊息

set -euo pipefail

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 預設值
NAMESPACE=""
INTERVAL=10
MONITOR_ALL=false
OUTPUT_FORMAT="table"
WATCH_MODE=false
WARNING_THRESHOLD=80

# 顯示幫助
show_help() {
    cat << EOF
命名空間資源監控腳本 - Namespace Resource Monitor

用法：
    ./monitor_resources.sh [OPTIONS] <namespace>

選項：
    -i, --interval SECONDS  更新間隔（秒），預設 10
    -a, --all               監控所有命名空間
    -o, --output FORMAT     輸出格式 (table/json/csv)
    -w, --watch             持續監控模式
    -t, --threshold PCT     資源使用警告閾值（百分比），預設 80
    -h, --help              顯示此幫助訊息

範例：
    # 監控特定命名空間
    ./monitor_resources.sh production

    # 持續監控所有命名空間，每 30 秒更新
    ./monitor_resources.sh -w -a -i 30

    # 輸出 JSON 格式
    ./monitor_resources.sh -o json production

EOF
}

# 解析命令列參數
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--interval)
                INTERVAL="$2"
                shift 2
                ;;
            -a|--all)
                MONITOR_ALL=true
                shift
                ;;
            -o|--output)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            -w|--watch)
                WATCH_MODE=true
                shift
                ;;
            -t|--threshold)
                WARNING_THRESHOLD="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                echo "未知選項: $1"
                show_help
                exit 1
                ;;
            *)
                NAMESPACE="$1"
                shift
                ;;
        esac
    done
    
    if [[ -z "$NAMESPACE" ]] && [[ "$MONITOR_ALL" == "false" ]]; then
        echo "錯誤：請指定命名空間或使用 -a 選項監控所有命名空間"
        show_help
        exit 1
    fi
}

# 檢查 kubectl 和 metrics-server
check_prerequisites() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}錯誤：kubectl 未安裝${NC}"
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}錯誤：無法連接到 Kubernetes 叢集${NC}"
        exit 1
    fi
}

# 獲取命名空間列表
get_namespaces() {
    if $MONITOR_ALL; then
        kubectl get namespaces -o jsonpath='{.items[*].metadata.name}'
    else
        echo "$NAMESPACE"
    fi
}

# 獲取資源配額使用情況
get_quota_usage() {
    local ns=$1
    local quota_info
    
    quota_info=$(kubectl get resourcequota -n "$ns" -o json 2>/dev/null || echo '{"items":[]}')
    
    if [[ $(echo "$quota_info" | jq '.items | length') -eq 0 ]]; then
        echo "無配額設定"
        return
    fi
    
    echo "$quota_info" | jq -r '.items[] | 
        "配額: \(.metadata.name)\n" +
        "  Pods: \(.status.used.pods // "0")/\(.status.hard.pods // "無限制")\n" +
        "  CPU 請求: \(.status.used["requests.cpu"] // "0")/\(.status.hard["requests.cpu"] // "無限制")\n" +
        "  記憶體請求: \(.status.used["requests.memory"] // "0")/\(.status.hard["requests.memory"] // "無限制")"'
}

# 獲取 Pod 資源使用情況
get_pod_metrics() {
    local ns=$1
    
    if ! kubectl top pods -n "$ns" 2>/dev/null; then
        echo "Metrics Server 未啟用或無資料"
    fi
}

# 獲取命名空間摘要
get_namespace_summary() {
    local ns=$1
    
    local pod_count running_pods pending_pods failed_pods
    pod_count=$(kubectl get pods -n "$ns" --no-headers 2>/dev/null | wc -l)
    running_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    pending_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)
    failed_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l)
    
    local service_count deployment_count
    service_count=$(kubectl get services -n "$ns" --no-headers 2>/dev/null | wc -l)
    deployment_count=$(kubectl get deployments -n "$ns" --no-headers 2>/dev/null | wc -l)
    
    echo "Pods: $pod_count (運行中: $running_pods, 等待中: $pending_pods, 失敗: $failed_pods)"
    echo "Services: $service_count"
    echo "Deployments: $deployment_count"
}

# 獲取最近事件
get_recent_events() {
    local ns=$1
    local limit=${2:-5}
    
    kubectl get events -n "$ns" --sort-by='.lastTimestamp' 2>/dev/null | tail -n "$limit"
}

# 計算資源使用百分比
calculate_usage_percentage() {
    local used=$1
    local hard=$2
    
    if [[ -z "$hard" ]] || [[ "$hard" == "0" ]]; then
        echo "N/A"
        return
    fi
    
    # 處理帶單位的值
    local used_val hard_val
    used_val=$(echo "$used" | sed 's/[^0-9.]//g')
    hard_val=$(echo "$hard" | sed 's/[^0-9.]//g')
    
    if [[ -z "$used_val" ]] || [[ -z "$hard_val" ]]; then
        echo "N/A"
        return
    fi
    
    # 使用 awk 進行浮點數計算（更可移植）
    awk "BEGIN {printf \"%.1f\", ($used_val / $hard_val) * 100}" 2>/dev/null || echo "N/A"
}

# 輸出表格格式
output_table() {
    local ns=$1
    
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  命名空間: ${YELLOW}$ns${NC}"
    echo -e "${CYAN}  時間: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    
    echo -e "${BLUE}--- 資源摘要 ---${NC}"
    get_namespace_summary "$ns"
    echo ""
    
    echo -e "${BLUE}--- 資源配額 ---${NC}"
    get_quota_usage "$ns"
    echo ""
    
    echo -e "${BLUE}--- Pod 資源使用 ---${NC}"
    get_pod_metrics "$ns"
    echo ""
    
    echo -e "${BLUE}--- 最近事件 ---${NC}"
    get_recent_events "$ns" 5
}

# 輸出 JSON 格式
output_json() {
    local ns=$1
    
    local summary quota_info pod_info events
    
    # 獲取基本資訊
    local pod_count running_pods
    pod_count=$(kubectl get pods -n "$ns" --no-headers 2>/dev/null | wc -l)
    running_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    
    # 構建 JSON
    cat << EOF
{
  "namespace": "$ns",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "summary": {
    "total_pods": $pod_count,
    "running_pods": $running_pods
  },
  "quota": $(kubectl get resourcequota -n "$ns" -o json 2>/dev/null || echo '{"items":[]}'),
  "pods": $(kubectl get pods -n "$ns" -o json 2>/dev/null || echo '{"items":[]}')
}
EOF
}

# 輸出 CSV 格式
output_csv() {
    local ns=$1
    
    echo "timestamp,namespace,total_pods,running_pods,pending_pods,failed_pods"
    
    local pod_count running_pods pending_pods failed_pods
    pod_count=$(kubectl get pods -n "$ns" --no-headers 2>/dev/null | wc -l)
    running_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
    pending_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)
    failed_pods=$(kubectl get pods -n "$ns" --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l)
    
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ),$ns,$pod_count,$running_pods,$pending_pods,$failed_pods"
}

# 監控單個命名空間
monitor_namespace() {
    local ns=$1
    
    case $OUTPUT_FORMAT in
        table)
            output_table "$ns"
            ;;
        json)
            output_json "$ns"
            ;;
        csv)
            output_csv "$ns"
            ;;
        *)
            output_table "$ns"
            ;;
    esac
}

# 持續監控
watch_namespaces() {
    local namespaces
    namespaces=$(get_namespaces)
    
    while true; do
        clear
        echo -e "${GREEN}命名空間資源監控 - 每 ${INTERVAL} 秒更新${NC}"
        echo -e "${GREEN}按 Ctrl+C 停止${NC}"
        echo ""
        
        for ns in $namespaces; do
            monitor_namespace "$ns"
        done
        
        sleep "$INTERVAL"
    done
}

# 主函數
main() {
    parse_args "$@"
    check_prerequisites
    
    if $WATCH_MODE; then
        watch_namespaces
    else
        local namespaces
        namespaces=$(get_namespaces)
        
        for ns in $namespaces; do
            monitor_namespace "$ns"
        done
    fi
}

# 執行主函數
main "$@"
