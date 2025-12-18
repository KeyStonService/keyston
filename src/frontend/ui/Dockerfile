# 多階段構建 - Advanced System Frontend
# Stage 1: Builder
FROM node:18-slim AS builder

# 安全：建立非 root 使用者
RUN groupadd -g 1001 nodejs && \
    useradd -r -u 1001 -g nodejs nodejs

# 安裝必要的構建工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製套件定義檔
COPY --chown=nodejs:nodejs package*.json ./

# 建立 nodejs 使用者的家目錄並設定權限
RUN chown -R nodejs:nodejs /app && \
    mkdir -p /home/nodejs/.npm && \
    chown -R nodejs:nodejs /home/nodejs

# 切換到非 root 使用者
USER nodejs

# 設定 npm 快取目錄環境變數
ENV NPM_CONFIG_CACHE=/home/nodejs/.npm

# 安裝依賴
RUN npm ci && \
    npm cache clean --force

# 複製原始碼
COPY --chown=nodejs:nodejs . .

# 構建生產版本
RUN npm run build

# Stage 2: Nginx Server
FROM nginx:1.25-alpine AS runner

# 複製自定義 nginx 配置
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf || \
    echo 'server { listen 3002; root /usr/share/nginx/html; index index.html; location / { try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf

# 複製構建產物
COPY --from=builder /app/dist /usr/share/nginx/html

# 使用非特權端口
EXPOSE 3002

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3002/ || exit 1

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]
