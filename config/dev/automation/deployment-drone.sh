#!/bin/bash

# SynergyMesh 部署無人機 (Deployment Drone)
# 作者: SynergyMesh Team
# 版本: 2.0.0
#
# 此腳本負責自動化部署流程:
# - 環境準備
# - 建置應用
# - 部署到目標環境
# - 健康檢查

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 配置
DEPLOY_ENV="${DEPLOY_ENV:-development}"
DEPLOY_TAG="${DEPLOY_TAG:-latest}"
HEALTH_CHECK_RETRIES=5
HEALTH_CHECK_INTERVAL=10

# Docker Compose 命令封裝 (解決 v1/v2 版本差異)
docker_compose() {
    if docker compose version &> /dev/null 2>&1; then
        docker compose "$@"
    else
        docker-compose "$@"
    fi
}

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 顯示標題
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════╗
║   SynergyMesh 部署無人機 v2.0         ║
║        Deployment Drone               ║
╚═══════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 檢查先決條件
check_prerequisites() {
    log_info "🔍 檢查部署先決條件..."
    
    local missing=0
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝"
        missing=1
    fi
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        log_error "Docker Compose 未安裝"
        missing=1
    fi
    
    if [ $missing -eq 1 ]; then
        log_error "缺少必要工具，無法繼續部署"
        exit 1
    fi
    
    log_success "所有先決條件已滿足"
}

# 準備環境
prepare_environment() {
    log_info "🔧 準備部署環境: $DEPLOY_ENV"
    
    local env_file="$PROJECT_ROOT/config/dev/environments/${DEPLOY_ENV}.env"
    
    if [ -f "$env_file" ]; then
        log_info "  載入環境配置: $env_file"
        # shellcheck source=/dev/null
        source "$env_file"
        log_success "環境配置已載入"
    else
        log_warn "環境配置檔案不存在: $env_file"
        log_info "  使用預設配置"
    fi
    
    # 創建必要目錄
    mkdir -p "$PROJECT_ROOT/generated"
    mkdir -p "$PROJECT_ROOT/logs"
}

# 建置應用
build_application() {
    log_info "🔨 建置應用..."
    
    cd "$PROJECT_ROOT"
    
    # 安裝依賴
    if [ -f "package.json" ]; then
        log_info "  安裝 Node.js 依賴..."
        npm ci --prefer-offline --no-audit 2>/dev/null || npm install 2>/dev/null || true
    fi
    
    # 執行建置
    if npm run build --if-present 2>/dev/null; then
        log_success "應用建置完成"
    else
        log_warn "建置步驟跳過或有警告"
    fi
}

# 建置 Docker 映像
build_docker_images() {
    log_info "🐳 建置 Docker 映像..."
    
    cd "$PROJECT_ROOT/config/dev"
    
    docker_compose build --parallel 2>/dev/null || docker_compose build
    
    log_success "Docker 映像建置完成"
}

# 部署服務
deploy_services() {
    log_info "🚀 部署服務到 $DEPLOY_ENV 環境..."
    
    cd "$PROJECT_ROOT/config/dev"
    
    # 停止現有服務
    log_info "  停止現有服務..."
    docker_compose down --remove-orphans 2>/dev/null || true
    
    # 啟動服務
    log_info "  啟動新服務..."
    docker_compose up -d
    
    log_success "服務部署完成"
}

# 健康檢查
health_check() {
    log_info "🏥 執行健康檢查..."
    
    local retries=$HEALTH_CHECK_RETRIES
    local interval=$HEALTH_CHECK_INTERVAL
    local healthy=false
    
    for ((i=1; i<=retries; i++)); do
        log_info "  健康檢查 ($i/$retries)..."
        
        # 檢查容器狀態
        cd "$PROJECT_ROOT/config/dev"
        
        local unhealthy=0
        if docker_compose ps | grep -q "unhealthy\|Exit"; then
            unhealthy=1
        fi
        
        if [ $unhealthy -eq 0 ]; then
            healthy=true
            break
        fi
        
        if [ $i -lt $retries ]; then
            log_warn "  部分服務尚未就緒，等待 ${interval}s..."
            sleep $interval
        fi
    done
    
    if [ "$healthy" = true ]; then
        log_success "所有服務健康檢查通過"
        return 0
    else
        log_error "健康檢查失敗"
        return 1
    fi
}

# 顯示部署資訊
show_deployment_info() {
    log_info "📊 部署資訊:"
    echo ""
    echo "  環境: $DEPLOY_ENV"
    echo "  標籤: $DEPLOY_TAG"
    echo "  時間: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    log_info "🔗 服務端點:"
    echo "  開發環境: http://localhost:8080"
    echo "  監控面板: http://localhost:9090"
    echo "  Grafana:  http://localhost:3000"
    echo ""
}

# 回滾部署
rollback() {
    log_warn "🔄 執行回滾..."
    
    cd "$PROJECT_ROOT/config/dev"
    
    docker_compose down
    
    log_info "回滾完成，請手動重新部署上一個版本"
}

# 顯示狀態
show_status() {
    log_info "📊 服務狀態:"
    
    cd "$PROJECT_ROOT/config/dev"
    
    docker_compose ps
}

# 顯示日誌
show_logs() {
    local service=$1
    
    cd "$PROJECT_ROOT/config/dev"
    
    if [ -n "$service" ]; then
        log_info "📋 顯示 $service 日誌:"
        docker_compose logs --tail=50 "$service"
    else
        log_info "📋 顯示所有服務日誌:"
        docker_compose logs --tail=20
    fi
}

# 完整部署流程
full_deploy() {
    show_banner
    
    log_info "🚀 開始完整部署流程..."
    echo ""
    
    check_prerequisites
    prepare_environment
    build_application
    build_docker_images
    deploy_services
    
    # 等待服務啟動
    log_info "⏳ 等待服務啟動..."
    sleep 5
    
    if health_check; then
        echo ""
        show_deployment_info
        log_success "🎉 部署成功完成！"
    else
        log_error "部署過程中發現問題"
        log_info "您可以執行 '$0 rollback' 來回滾"
        exit 1
    fi
}

# 顯示幫助
show_help() {
    cat << EOF
SynergyMesh 部署無人機

用法: $0 [命令] [選項]

命令:
  deploy              執行完整部署流程 (預設)
  build               僅建置應用和映像
  start               啟動服務
  stop                停止服務
  restart             重啟服務
  status              顯示服務狀態
  logs [服務]         顯示日誌
  health              執行健康檢查
  rollback            回滾部署
  help                顯示此幫助訊息

環境變數:
  DEPLOY_ENV          部署環境 (development/staging/production)
  DEPLOY_TAG          部署標籤

範例:
  $0 deploy                    # 執行完整部署
  DEPLOY_ENV=staging $0 deploy # 部署到 staging 環境
  $0 logs devcontainer         # 查看特定服務日誌
  $0 status                    # 查看服務狀態

EOF
}

# 主程式
main() {
    local command=${1:-deploy}
    
    case $command in
        deploy)
            full_deploy
            ;;
        build)
            show_banner
            check_prerequisites
            prepare_environment
            build_application
            build_docker_images
            ;;
        start)
            deploy_services
            ;;
        stop)
            cd "$PROJECT_ROOT/config/dev"
            docker_compose down
            log_success "服務已停止"
            ;;
        restart)
            cd "$PROJECT_ROOT/config/dev"
            docker_compose restart
            log_success "服務已重啟"
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        health)
            health_check
            ;;
        rollback)
            rollback
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 執行主程式
main "$@"
