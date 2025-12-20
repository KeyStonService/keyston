# MachineNativeOps Production Dockerfile
# 多階段構建生產環境鏡像

# 構建階段
FROM python:3.11-slim as builder

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# 生產階段
FROM python:3.11-slim as production

# 創建非特權用戶
RUN groupadd -r mno && useradd -r -g mno mno

# 安裝運行時依賴
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 設置工作目錄
WORKDIR /app

# 從構建階段複製 Python 包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 複製應用程式代碼
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY requirements.txt ./
COPY setup.py ./
COPY README.md ./

# 創建必要的目錄
RUN mkdir -p /var/log/machinenativeops /var/lib/machinenativeops /tmp/mno

# 設置目錄權限
RUN chown -R mno:mno /app /var/log/machinenativeops /var/lib/machinenativeops /tmp/mno

# 切換到非特權用戶
USER mno

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 設置環境變量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MNO_CONFIG_PATH=/app/config/prod/config.yaml

# 啟動命令
CMD ["python", "-m", "src.business.api"]