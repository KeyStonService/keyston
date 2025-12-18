# 多階段構建 - MCP Servers
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
RUN npm install && \
    npm cache clean --force

# 複製原始碼
COPY --chown=nodejs:nodejs *.js ./
COPY --chown=nodejs:nodejs README.md ./

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
COPY --from=builder --chown=nodejs:nodejs /app/*.js ./
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./
COPY --from=builder --chown=nodejs:nodejs /app/README.md ./

# 切換到非 root 使用者
USER nodejs

# 環境變數
ENV NODE_ENV=production \
    PORT=3001 \
    LOG_LEVEL=info

# 暴露端口
EXPOSE 3001

# 健康檢查（如果有 HTTP 端點）
# HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
#     CMD node -e "require('http').get('http://localhost:3001/healthz', (r) => { process.exit(r.statusCode === 200 ? 0 : 1); })"

# 使用 dumb-init 作為 init 處理程序
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# 啟動應用
CMD ["node", "index.js"]
