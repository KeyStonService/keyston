# Docker 部署

## 開發環境

```bash
cp .env.example .env
npm run docker:dev
```

## 生產映像

```bash
docker build -t island-ai/platform:latest .
docker run -d --name island-ai \
  -p 8080:8080 \
  -e ISLAND_ENV=production \
  island-ai/platform:latest
```

## Compose

```yaml
services:
  control-plane:
    build: .
    ports:
      - "8080:8080"
    env_file: .env
  workflow:
    image: island-ai/workflow:latest
    depends_on:
      - control-plane
```

## 最佳實踐

- 使用多階段建置縮小映像
- 啟用 cosign 簽章
- 搭配 `docker-compose.dev.yml` 進行本地測試
