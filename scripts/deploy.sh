#!/bin/bash
# MachineNativeOps 生產環境部署腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 檢查依賴
check_dependencies() {
    log_info "檢查部署依賴..."
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝"
        exit 1
    fi
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安裝"
        exit 1
    fi
    
    # 檢查環境變量文件
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，將從示例創建"
        cp .env.example .env
        log_warning "請編輯 .env 文件設置正確的環境變量"
        exit 1
    fi
    
    log_success "依賴檢查通過"
}

# 加載環境變量
load_env() {
    log_info "加載環境變量..."
    set -a
    source .env
    set +a
    log_success "環境變量加載完成"
}

# 創建必要的目錄
create_directories() {
    log_info "創建必要的目錄..."
    
    directories=(
        "config/prod/postgres"
        "config/prod/redis"
        "config/prod/nginx/ssl"
        "config/prod/prometheus"
        "config/prod/grafana/dashboards"
        "config/prod/grafana/datasources"
        "config/prod/rabbitmq"
        "config/prod/consul"
        "logs"
        "backups"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    log_success "目錄創建完成"
}

# 生成配置文件
generate_configs() {
    log_info "生成配置文件..."
    
    # PostgreSQL 配置
    cat > config/prod/postgres/postgresql.conf << EOF
# PostgreSQL 生產配置
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
log_autovacuum_min_duration = 0
EOF

    # Redis 配置
    cat > config/prod/redis/redis.conf << EOF
# Redis 生產配置
bind 0.0.0.0
port 6379
requirepass ${REDIS_PASSWORD}
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
slowlog-log-slower-than 10000
slowlog-max-len 128
timeout 0
tcp-keepalive 300
EOF

    # Nginx 配置
    cat > config/prod/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream mno_app {
        server mno-business:8000;
    }

    server {
        listen 80;
        server_name ${FRONTEND_URL:-localhost};
        
        # 重定向到 HTTPS
        return 301 https://\$server_name\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name ${FRONTEND_URL:-localhost};

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # API 路由
        location /api/ {
            proxy_pass http://mno_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # 健康檢查
        location /health {
            proxy_pass http://mno_app;
            access_log off;
        }

        # 靜態文件
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

    # Prometheus 配置
    cat > config/prod/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'mno-business'
    static_configs:
      - targets: ['mno-business:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
EOF

    # Grafana 數據源配置
    cat > config/prod/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    # Consul 配置
    cat > config/prod/consul/consul.json << EOF
{
  "datacenter": "dc1",
  "data_dir": "/consul/data",
  "log_level": "INFO",
  "server": true,
  "bootstrap_expect": 1,
  "ui_config": {
    "enabled": true
  },
  "connect": {
    "enabled": true
  }
}
EOF

    log_success "配置文件生成完成"
}

# 生成 SSL 證書（開發用，生產環境應使用正式證書）
generate_ssl_certs() {
    log_info "生成 SSL 證書..."
    
    if [ ! -f "config/prod/nginx/ssl/cert.pem" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout config/prod/nginx/ssl/key.pem \
            -out config/prod/nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=MachineNativeOps/CN=${FRONTEND_URL:-localhost}"
        log_success "SSL 證書生成完成"
    else
        log_info "SSL 證書已存在，跳過生成"
    fi
}

# 構建和部署
deploy() {
    log_info "開始部署 MachineNativeOps..."
    
    # 拉取最新鏡像
    log_info "拉取 Docker 鏡像..."
    docker-compose -f docker-compose.prod.yml pull
    
    # 構建應用鏡像
    log_info "構建應用鏡像..."
    docker-compose -f docker-compose.prod.yml build
    
    # 啟動數據庫服務
    log_info "啟動數據庫服務..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis
    
    # 等待數據庫就緒
    log_info "等待數據庫就緒..."
    sleep 30
    
    # 運行數據庫遷移
    log_info "運行數據庫遷移..."
    docker-compose -f docker-compose.prod.yml run --rm mno-business python -m scripts.migrate
    
    # 啟動所有服務
    log_info "啟動所有服務..."
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "部署完成！"
}

# 健康檢查
health_check() {
    log_info "執行健康檢查..."
    
    services=("mno-business:8000" "postgres:5432" "redis:6379")
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d':' -f1)
        port=$(echo $service | cut -d':' -f2)
        
        log_info "檢查服務 $service_name..."
        
        max_attempts=30
        attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f "http://localhost:$port/health" &> /dev/null || \
               [ "$service_name" = "postgres" ] && \
               docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U mno_user &> /dev/null || \
               [ "$service_name" = "redis" ] && \
               docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping &> /dev/null; then
                log_success "服務 $service_name 健康"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "服務 $service_name 健康檢查失敗"
                return 1
            fi
            
            log_info "等待服務 $service_name... ($attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        done
    done
    
    log_success "所有服務健康檢查通過"
}

# 顯示部署信息
show_deployment_info() {
    log_success "🎉 MachineNativeOps 部署成功！"
    echo
    echo "服務訪問地址："
    echo "  • API 服務: http://${FRONTEND_URL:-localhost}/api/v1/"
    echo "  • API 文檔: http://${FRONTEND_URL:-localhost}/docs"
    echo "  • Grafana: http://localhost:3000 (admin/${GRAFANA_PASSWORD})"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Kibana: http://localhost:5601"
    echo "  • Consul: http://localhost:8500"
    echo "  • RabbitMQ: http://localhost:15672 (${RABBITMQ_USER}/${RABBITMQ_PASSWORD})"
    echo
    echo "管理命令："
    echo "  • 查看日誌: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  • 重啟服務: docker-compose -f docker-compose.prod.yml restart"
    echo "  • 停止服務: docker-compose -f docker-compose.prod.yml down"
    echo "  • 更新服務: ./scripts/update.sh"
    echo
    echo "監控指標："
    echo "  • CPU/內存使用率監控"
    echo "  • 業務指標實時追蹤"
    echo "  • 錯誤日誌聚合分析"
    echo "  • 性能瓶頸識別"
}

# 主函數
main() {
    echo "🚀 MachineNativeOps 生產環境部署開始..."
    echo "================================="
    
    check_dependencies
    load_env
    create_directories
    generate_configs
    generate_ssl_certs
    deploy
    health_check
    show_deployment_info
    
    echo "================================="
    log_success "部署完成！MachineNativeOps 已成功運行。"
}

# 執行主函數
main "$@"