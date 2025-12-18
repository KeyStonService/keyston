# Dockerfile for Automation Architect
# 企業級自動化代碼分析與修復系統

FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製需求文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建必要的目錄
RUN mkdir -p /app/logs /app/reports /app/cache

# 設置環境變量
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=production

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 暴露端口（如果需要 API 服務）
EXPOSE 8000

# 默認命令
CMD ["python", "-m", "core.orchestration.pipeline"]
