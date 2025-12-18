# 多階段構建 - 企業級生產 Dockerfile
# 使用 Debian-based 映像以避免 Alpine 網路問題
# Stage 1: Builder
FROM node:18-slim AS builder

# 安全：建立非 root 使用者
RUN groupadd -g 1001 nodejs && \
    useradd -r -u 1001 -g nodejs nodejs

# 安裝必要的構建工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    dumb-init && \
    rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 確保 /app 目錄和 nodejs 家目錄屬於 nodejs 使用者
RUN chown -R nodejs:nodejs /app && \
    mkdir -p /home/nodejs/.npm && \
    chown -R nodejs:nodejs /home/nodejs

# 複製套件定義檔（利用 Docker layer cache）
COPY --chown=nodejs:nodejs package*.json ./
COPY --chown=nodejs:nodejs tsconfig.json ./

# 複製原始碼
COPY --chown=nodejs:nodejs src ./src

# 以非 root 使用者安裝依賴並構建，符合最小權限原則
USER nodejs
ENV NPM_CONFIG_CACHE=/home/nodejs/.npm

# 配置 npm 以處理潛在的證書問題（僅在構建階段）
RUN npm config set strict-ssl false

# 升級 npm 以修復 "Exit handler never called" 問題  
RUN npm install -g npm@10 && npm --version || \
    (echo "Warning: npm upgrade failed, using system version: $(npm --version)" && true)

# 安裝所有依賴（包括 devDependencies 用於構建）
# 然後構建，最後移除 devDependencies
RUN npm ci && \
    npm run build && \
    npm prune --production && \
    npm cache clean --force

# Stage 2: Runner (最小生產映像)
FROM node:18-slim AS runner

# 安裝運行時必要工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    dumb-init && \
    rm -rf /var/lib/apt/lists/*

# 安全加固：建立非 root 使用者
RUN groupadd -g 1001 nodejs && \
    useradd -r -u 1001 -g nodejs nodejs

# 設定工作目錄
WORKDIR /app

# 建立必要的臨時目錄
RUN mkdir -p /tmp /app/.npm && \
    chown -R nodejs:nodejs /tmp /app/.npm

# 從 builder 階段複製必要產物
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

# 切換到非 root 使用者
USER nodejs

# 環境變數
ENV NODE_ENV=production \
    PORT=3000 \
    LOG_LEVEL=info \
    NODE_OPTIONS="--max-old-space-size=512"

# 暴露端口
EXPOSE 3000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/healthz', (r) => { process.exit(r.statusCode === 200 ? 0 : 1); })"

# 使用 dumb-init 作為 init 處理程序（正確處理信號和殭屍進程）
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# 啟動應用
CMD ["node", "dist/server.js"]
