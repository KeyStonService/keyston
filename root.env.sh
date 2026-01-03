#!/bin/bash
# 🌍 Root 使用者殼層環境配置
# MachineNativeOps Root Layer Environment Configuration
# Version: 1.0.0
# Last Modified: 2025-12-20T22:00:00Z

# =============================================================================
# MachineNativeOps Root Environment Configuration
# =============================================================================
# This script sets up the environment for the root user running MachineNativeOps
# It includes all necessary environment variables, PATH configurations, and
# utility functions for system administration and operations.
# =============================================================================

# === 基本系統資訊 ===
export MACHINENATIVEOPS_VERSION="1.0.0"
export MACHINENATIVEOPS_HOME="/opt/machinenativenops"
export MACHINENATIVEOPS_ROOT="${MACHINENATIVEOPS_HOME}"
export MACHINENATIVEOPS_USER="root"
export MACHINENATIVEOPS_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

# === 目錄結構定義 ===
export MACHINENATIVEOPS_CONFIG="/etc/machinenativenops"
export MACHINENATIVEOPS_LOGS="/var/log/machinenativenops"
export MACHINENATIVEOPS_DATA="/var/lib/machinenativenops"
export MACHINENATIVEOPS_RUN="/var/run/machinenativenops"
export MACHINENATIVEOPS_TMP="/tmp/machinenativenops"
export MACHINENATIVEOPS_BACKUP="/var/backups/machinenativenops"
export MACHINENATIVEOPS_CACHE="/var/cache/machinenativenops"

# === 安全性配置目錄 ===
export MACHINENATIVEOPS_TRUST="${MACHINENATIVEOPS_CONFIG}/trust"
export MACHINENATIVEOPS_CERTS="${MACHINENATIVEOPS_CONFIG}/certs"
export MACHINENATIVEOPS_KEYS="${MACHINENATIVEOPS_CONFIG}/keys"
export MACHINENATIVEOPS_SECRETS="${MACHINENATIVEOPS_CONFIG}/secrets"

# === 模組與執行環境 ===
export MACHINENATIVEOPS_MODULES="${MACHINENATIVEOPS_HOME}/modules"
export MACHINENATIVEOPS_WORKFLOWS="${MACHINENATIVEOPS_CONFIG}/workflows"
export MACHINENATIVEOPS_POLICIES="${MACHINENATIVEOPS_CONFIG}/policies"
export MACHINENATIVEOPS_BASELINES="${MACHINENATIVEOPS_CONFIG}/baselines"

# === Controlplane 架構環境變數 ===
export MACHINENATIVEOPS_CONTROLPLANE="${MACHINENATIVEOPS_SCRIPT_DIR}/controlplane"
export MACHINENATIVEOPS_BASELINE="${MACHINENATIVEOPS_CONTROLPLANE}/baseline"
export MACHINENATIVEOPS_OVERLAY="${MACHINENATIVEOPS_CONTROLPLANE}/overlay"
export MACHINENATIVEOPS_ACTIVE="${MACHINENATIVEOPS_CONTROLPLANE}/active"

# Baseline 子目錄
export MACHINENATIVEOPS_BASELINE_CONFIG="${MACHINENATIVEOPS_BASELINE}/config"
export MACHINENATIVEOPS_BASELINE_SPECS="${MACHINENATIVEOPS_BASELINE}/specifications"
export MACHINENATIVEOPS_BASELINE_REGISTRIES="${MACHINENATIVEOPS_BASELINE}/registries"
export MACHINENATIVEOPS_BASELINE_INTEGRATION="${MACHINENATIVEOPS_BASELINE}/integration"
export MACHINENATIVEOPS_BASELINE_VALIDATION="${MACHINENATIVEOPS_BASELINE}/validation"
export MACHINENATIVEOPS_BASELINE_DOCS="${MACHINENATIVEOPS_BASELINE}/documentation"

# Overlay 子目錄
export MACHINENATIVEOPS_OVERLAY_CONFIG="${MACHINENATIVEOPS_OVERLAY}/config"
export MACHINENATIVEOPS_OVERLAY_EVIDENCE="${MACHINENATIVEOPS_OVERLAY}/evidence"
export MACHINENATIVEOPS_OVERLAY_RUNTIME="${MACHINENATIVEOPS_OVERLAY}/runtime"
export MACHINENATIVEOPS_OVERLAY_LOGS="${MACHINENATIVEOPS_OVERLAY}/logs"

# Validation 配置
export MACHINENATIVEOPS_VALIDATOR="${MACHINENATIVEOPS_BASELINE_VALIDATION}/validate-root-specs.py"
export MACHINENATIVEOPS_VALIDATION_GATE="${MACHINENATIVEOPS_BASELINE_VALIDATION}/gate-root-specs.yml"
export MACHINENATIVEOPS_VALIDATION_VECTORS="${MACHINENATIVEOPS_BASELINE_VALIDATION}/vectors/root.validation.vectors.yaml"

# === 資料庫與快取配置 ===
export MACHINENATIVEOPS_DB_HOST="postgres.machinenativenops.svc.cluster.local"
export MACHINENATIVEOPS_DB_PORT="5432"
export MACHINENATIVEOPS_DB_NAME="machinenativenops_root"
export MACHINENATIVEOPS_REDIS_HOST="redis.machinenativenops.svc.cluster.local"
export MACHINENATIVEOPS_REDIS_PORT="6379"

# === 監控與可觀測性 ===
export MACHINENATIVEOPS_PROMETHEUS_PORT="9090"
export MACHINENATIVEOPS_HEALTH_CHECK_PORT="8080"
export MACHINENATIVEOPS_JAEGER_ENDPOINT="http://jaeger:14268/api/traces"

# === PATH 配置 ===
# 核心 MachineNativeOps 路徑
export PATH="${MACHINENATIVEOPS_HOME}/bin:${MACHINENATIVEOPS_HOME}/sbin:${PATH}"

# 模組執行路徑
export PATH="${MACHINENATIVEOPS_MODULES}/bin:${PATH}"

# 工具與腳本路徑
export PATH="${MACHINENATIVEOPS_HOME}/tools:${MACHINENATIVEOPS_HOME}/scripts:${PATH}"

# Python 路徑（如果使用 Python 模組）
if [ -d "${MACHINENATIVEOPS_MODULES}/python" ]; then
    export PYTHONPATH="${MACHINENATIVEOPS_MODULES}/python:${PYTHONPATH}"
    export PATH="${MACHINENATIVEOPS_MODULES}/python/bin:${PATH}"
fi

# === 環境變數設定 ===
# 運行模式
export MACHINENATIVEOPS_ENVIRONMENT="${MACHINENATIVEOPS_ENVIRONMENT:-production}"
export MACHINENATIVEOPS_DEPLOYMENT_MODE="${MACHINENATIVEOPS_DEPLOYMENT_MODE:-production}"
export MACHINENATIVEOPS_DEBUG="${MACHINENATIVEOPS_DEBUG:-false}"

# 安全性設定
export MACHINENATIVEOPS_SECURITY_LEVEL="${MACHINENATIVEOPS_SECURITY_LEVEL:-high}"
export MACHINENATIVEOPS_HSM_ENABLED="${MACHINENATIVEOPS_HSM_ENABLED:-true}"
export MACHINENATIVEOPS_MUTUAL_TLS="${MACHINENATIVEOPS_MUTUAL_TLS:-true}"
export MACHINENATIVEOPS_INTEGRITY_CHECK="${MACHINENATIVEOPS_INTEGRITY_CHECK:-true}"

# 效能設定
export MACHINENATIVEOPS_MAX_WORKERS="${MACHINENATIVEOPS_MAX_WORKERS:-10}"
export MACHINENATIVEOPS_CACHE_SIZE="${MACHINENATIVEOPS_CACHE_SIZE:-1Gi}"
export MACHINENATIVEOPS_CONNECTION_POOL_SIZE="${MACHINENATIVEOPS_CONNECTION_POOL_SIZE:-20}"
export MACHINENATIVEOPS_QUEUE_SIZE="${MACHINENATIVEOPS_QUEUE_SIZE:-1000}"

# 日誌設定
export MACHINENATIVEOPS_LOG_LEVEL="${MACHINENATIVEOPS_LOG_LEVEL:-INFO}"
export MACHINENATIVEOPS_LOG_FORMAT="${MACHINENATIVEOPS_LOG_FORMAT:-structured}"
export MACHINENATIVEOPS_LOG_RETENTION="${MACHINENATIVEOPS_LOG_RETENTION:-30d}"

# === 函式庫設定 ===
# OpenSSL 設定
export OPENSSL_CONF="${MACHINENATIVEOPS_CONFIG}/openssl.cnf"
export SSL_CERT_FILE="${MACHINENATIVEOPS_CERTS}/ca-bundle.crt"

# Python 設定
export PYTHONUNBUFFERED=1
export PYTHONFAULTHANDLER=1
export PYTHONDONTWRITEBYTECODE=1

# Java 設定（如果使用 Java 模組）
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/default-java}"
export JAVA_OPTS="-Xmx2g -Xms512m -XX:+UseG1GC"

# Node.js 設定（如果使用 Node.js 模組）
export NODE_PATH="${MACHINENATIVEOPS_MODULES}/node_modules:${NODE_PATH}"
export NODE_ENV="${MACHINENATIVEOPS_ENVIRONMENT}"

# === 顏色與提示設定 ===
# 顏色定義
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export PURPLE='\033[0;35m'
export CYAN='\033[0;36m'
export WHITE='\033[1;37m'
export NC='\033[0m' # No Color

# 自定義提示符
function machinenativenops_prompt() {
    local exit_code=$?
    local prompt_color="${GREEN}"
    
    if [ $exit_code -ne 0 ]; then
        prompt_color="${RED}"
    fi
    
    echo -n "${prompt_color}[MNO-${MACHINENATIVEOPS_ENVIRONMENT}]${NC} "
    echo -n "${BLUE}\u${NC}@${PURPLE}\h${NC}:"
    echo -n "${YELLOW}\w${NC}"
    echo -n "${prompt_color}\$${NC} "
}

export PS1='$(machinenativenops_prompt)'

# === 實用函數定義 ===

# 日誌函數
function mno_log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "${timestamp} [${level}] ${message}" | tee -a "${MACHINENATIVEOPS_LOGS}/root-env.log"
}

function mno_debug() { mno_log "DEBUG" "$@"; }
function mno_info() { mno_log "INFO" "$@"; }
function mno_warn() { mno_log "WARN" "$@"; }
function mno_error() { mno_log "ERROR" "$@"; }

# 系統狀態檢查函數
function mno_status() {
    echo "${CYAN}=== MachineNativeOps System Status ===${NC}"
    
    # 檢查核心服務
    local services=("config-manager" "logging-service" "trust-manager" "governance-engine")
    for service in "${services[@]}"; do
        if pgrep -f "$service" > /dev/null; then
            echo "${GREEN}✓${NC} $service is ${GREEN}running${NC}"
        else
            echo "${RED}✗${NC} $service is ${RED}not running${NC}"
        fi
    done
    
    # 檢查目錄
    local directories=("${MACHINENATIVEOPS_CONFIG}" "${MACHINENATIVEOPS_LOGS}" "${MACHINENATIVEOPS_DATA}")
    for dir in "${directories[@]}"; do
        if [ -d "$dir" ]; then
            echo "${GREEN}✓${NC} Directory $dir exists"
        else
            echo "${RED}✗${NC} Directory $dir missing"
        fi
    done
    
    # 檢查磁碟空間
    echo "${CYAN}Disk Usage:${NC}"
    df -h "${MACHINENATIVEOPS_HOME}" "${MACHINENATIVEOPS_DATA}" "${MACHINENATIVEOPS_LOGS}"
}

# 配置重新載入函數
function mno_reload() {
    mno_info "Reloading MachineNativeOps configuration..."
    
    # 重新載入環境變數
    source "${MACHINENATIVEOPS_CONFIG}/.root.env.sh"
    
    # 重新載入服務配置
    if command -v systemctl > /dev/null; then
        systemctl reload machinenativenops-* 2>/dev/null || true
    fi
    
    mno_info "Configuration reloaded successfully"
}

# 模組管理函數
function mno_module() {
    local action="$1"
    local module="$2"
    
    case "$action" in
        "start")
            mno_info "Starting module: $module"
            "${MACHINENATIVEOPS_MODULES}/bin/$module" start
            ;;
        "stop")
            mno_info "Stopping module: $module"
            "${MACHINENATIVEOPS_MODULES}/bin/$module" stop
            ;;
        "restart")
            mno_info "Restarting module: $module"
            "${MACHINENATIVEOPS_MODULES}/bin/$module" restart
            ;;
        "status")
            "${MACHINENATIVEOPS_MODULES}/bin/$module" status
            ;;
        "list")
            ls -la "${MACHINENATIVEOPS_MODULES}/bin/"
            ;;
        *)
            echo "Usage: mno_module {start|stop|restart|status|list} [module_name]"
            return 1
            ;;
    esac
}

# 日誌檢視函數
function mno_logs() {
    local service="$1"
    local lines="${2:-100}"
    
    if [ -z "$service" ]; then
        echo "Available logs:"
        ls -la "${MACHINENATIVEOPS_LOGS}/"
        return 0
    fi
    
    if [ -f "${MACHINENATIVEOPS_LOGS}/${service}.log" ]; then
        tail -n "$lines" "${MACHINENATIVEOPS_LOGS}/${service}.log"
    else
        mno_error "Log file for $service not found"
        return 1
    fi
}

# 健康檢查函數
function mno_health() {
    echo "${CYAN}=== MachineNativeOps Health Check ===${NC}"
    
    # 檢查 HTTP 健康檢查端點
    if curl -f -s "http://localhost:${MACHINENATIVEOPS_HEALTH_CHECK_PORT}/health" > /dev/null; then
        echo "${GREEN}✓${NC} HTTP health check passing"
    else
        echo "${RED}✗${NC} HTTP health check failing"
    fi
    
    # 檢查 Prometheus 指標
    if curl -f -s "http://localhost:${MACHINENATIVEOPS_PROMETHEUS_PORT}/metrics" > /dev/null; then
        echo "${GREEN}✓${NC} Prometheus metrics available"
    else
        echo "${RED}✗${NC} Prometheus metrics unavailable"
    fi
    
    # 檢查資料庫連接
    if pg_isready -h "${MACHINENATIVEOPS_DB_HOST}" -p "${MACHINENATIVEOPS_DB_PORT}" > /dev/null; then
        echo "${GREEN}✓${NC} Database connection available"
    else
        echo "${RED}✗${NC} Database connection unavailable"
    fi
}

# 備份函數
function mno_backup() {
    local backup_name
    backup_name="machinenativenops-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_dir="${MACHINENATIVEOPS_BACKUP}/${backup_name}"
    
    mno_info "Creating backup: $backup_name"
    
    mkdir -p "$backup_dir"
    
    # 備份配置
    cp -r "${MACHINENATIVEOPS_CONFIG}" "$backup_dir/"
    
    # 備份資料
    cp -r "${MACHINENATIVEOPS_DATA}" "$backup_dir/"
    
    # 壓縮備份
    cd "${MACHINENATIVEOPS_BACKUP}" || return 1
    tar -czf "${backup_name}.tar.gz" "$backup_name"
    rm -rf "$backup_name"
    
    mno_info "Backup completed: ${backup_name}.tar.gz"
}

# 清理函數
function mno_cleanup() {
    mno_info "Cleaning up temporary files and logs"
    
    # 清理臨時檔案
    if [ -n "${MACHINENATIVEOPS_TMP}" ]; then
        rm -rf "${MACHINENATIVEOPS_TMP:?}"/*
    fi
    
    # 清理舊日誌（超過 30 天）
    find "${MACHINENATIVEOPS_LOGS}" -name "*.log" -mtime +30 -delete
    
    # 清理快取
    find "${MACHINENATIVEOPS_CACHE}" -type f -mtime +7 -delete
    
    mno_info "Cleanup completed"
}

# === 初始化檢查 ===
function _mno_init_check() {
    # 確保必要目錄存在
    local directories=(
        "${MACHINENATIVEOPS_CONFIG}"
        "${MACHINENATIVEOPS_LOGS}"
        "${MACHINENATIVEOPS_DATA}"
        "${MACHINENATIVEOPS_RUN}"
        "${MACHINENATIVEOPS_TRUST}"
        "${MACHINENATIVEOPS_CERTS}"
        "${MACHINENATIVEOPS_KEYS}"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            chmod 755 "$dir"
            mno_debug "Created directory: $dir"
        fi
    done
    
    # 檢查配置檔案
    if [ ! -f "${MACHINENATIVEOPS_CONFIG}/.root.config.yaml" ]; then
        mno_warn "Root configuration file not found: ${MACHINENATIVEOPS_CONFIG}/.root.config.yaml"
    fi
    
    # 設定適當的權限
    chmod 600 "${MACHINENATIVEOPS_KEYS}"/* 2>/dev/null || true
    chmod 644 "${MACHINENATIVEOPS_CERTS}"/* 2>/dev/null || true
}

# === 自動完成設定 ===
function _mno_complete() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    case "${prev}" in
        mno_module)
            opts="start stop restart status list"
            COMPREPLY=($(compgen -W "${opts}" -- "${cur}"))
            return 0
            ;;
        mno_logs)
            opts=$(ls "${MACHINENATIVEOPS_LOGS}"/*.log 2>/dev/null | xargs -n1 basename | sed 's/.log$//')
            COMPREPLY=($(compgen -W "${opts}" -- "${cur}"))
            return 0
            ;;
    esac
}

# 註冊自動完成
complete -F _mno_complete mno_module
complete -F _mno_complete mno_logs

# === 環境載入完成訊息 ===
if [ -n "$BASH_VERSION" ] && [ "${-#i}" -eq 0 ]; then
    _mno_init_check
    mno_info "MachineNativeOps root environment loaded (Version ${MACHINENATIVEOPS_VERSION})"
    mno_info "Type 'mno_status' for system status, 'mno_help' for available commands"
fi

# === 別名定義 ===
alias mno-status='mno_status'
alias mno-reload='mno_reload'
alias mno-health='mno_health'
alias mno-backup='mno_backup'
alias mno-cleanup='mno_cleanup'
alias mno-logs='mno_logs'
alias mno-module='mno_module'

# 快捷別名
alias cd-mno='cd ${MACHINENATIVEOPS_HOME}'
alias cd-config='cd ${MACHINENATIVEOPS_CONFIG}'
alias cd-logs='cd ${MACHINENATIVEOPS_LOGS}'
alias cd-modules='cd ${MACHINENATIVEOPS_MODULES}'
alias cd-data='cd ${MACHINENATIVEOPS_DATA}'

# === 導出環境變數給子程序 ===
export MACHINENATIVEOPS_VERSION \
       MACHINENATIVEOPS_HOME \
       MACHINENATIVEOPS_CONFIG \
       MACHINENATIVEOPS_LOGS \
       MACHINENATIVEOPS_DATA \
       MACHINENATIVEOPS_RUN \
       MACHINENATIVEOPS_TRUST \
       MACHINENATIVEOPS_CERTS \
       MACHINENATIVEOPS_KEYS \
       MACHINENATIVEOPS_MODULES \
       MACHINENATIVEOPS_DB_HOST \
       MACHINENATIVEOPS_DB_PORT \
       MACHINENATIVEOPS_DB_NAME \
       MACHINENATIVEOPS_REDIS_HOST \
       MACHINENATIVEOPS_REDIS_PORT \
       MACHINENATIVEOPS_PROMETHEUS_PORT \
       MACHINENATIVEOPS_HEALTH_CHECK_PORT
