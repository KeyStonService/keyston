# 📚 Apps - 應用層 / Application Layer

## 概述 / Overview

`apps/` 目錄包含所有面向用戶的應用程式，包括 Web 前端、移動應用和各種客戶端。

The `apps/` directory contains all user-facing applications, including web
frontend, mobile applications, and various client applications.

---

## 📁 目錄結構 / Directory Structure

```
apps/
├── README.md                           # 應用層說明
│
├── 🌐 web/                             # Web 應用 (主應用)
│   ├── README.md
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js              # Tailwind CSS 配置
│   ├── vite.config.ts                  # Vite 配置
│   ├── pytest.ini
│   ├── requirements.txt                # Python 依賴
│   │
│   ├── src/
│   │   ├── main.tsx                    # React 入口
│   │   ├── App.tsx                     # 主應用組件
│   │   ├── shadcn.css                  # Shadcn UI 樣式
│   │   │
│   │   ├── components/                 # React 組件
│   │   │   ├── layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── ui/                     # Shadcn UI 組件
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   └── ...
│   │   │   ├── dashboard/
│   │   │   └── analysis/
│   │   │
│   │   ├── pages/                      # 頁面組件
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Analysis.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── NotFound.tsx
│   │   │
│   │   ├── hooks/                      # React Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useData.ts
│   │   │   └── useTheme.ts
│   │   │
│   │   ├── services/                   # API 服務
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── analytics.ts
│   │   │
│   │   ├── store/                      # 狀態管理
│   │   │   ├── index.ts
│   │   │   ├── authSlice.ts
│   │   │   └── dataSlice.ts
│   │   │
│   │   └── utils/                      # 工具函式
│   │       ├── formatters.ts
│   │       └── validators.ts
│   │
│   ├── public/                         # 靜態資源
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── assets/
│   │
│   ├── Dockerfile                      # Docker 配置
│   ├── Dockerfile.api                  # API Docker 配置
│   ├── docker-compose.api.yml
│   ├── k8s/                            # Kubernetes 配置
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   │
│   ├── services/                       # 後端服務
│   │   ├── api.py                      # FastAPI 伺服器
│   │   ├── code_analyzer.py            # 程式碼分析服務
│   │   ├── models.py                   # 資料模型
│   │   └── auth.py                     # 認證服務
│   │
│   ├── tests/                          # 測試
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   └── deploy/                         # 部署配置
│       ├── nginx.conf
│       └── docker-entrypoint.sh
│
├── 📱 mobile/                          # 移動應用 (可選)
│   ├── README.md
│   ├── ios/                            # iOS 應用
│   │   └── ...
│   └── android/                        # Android 應用
│       └── ...
│
└── 🖥️ desktop/                         # 桌面應用 (可選)
    ├── README.md
    └── ...
```

---

## 🌐 Web 應用 / Web Application

### 技術棧 / Tech Stack

- **前端**: React 18 + TypeScript + Vite
- **UI 框架**: Shadcn UI + Tailwind CSS
- **狀態管理**: Redux Toolkit
- **HTTP**: Axios
- **後端**: FastAPI + Python 3.10+
- **資料庫**: PostgreSQL
- **部署**: Docker + Kubernetes

### 功能特性 / Features

- ✅ 即時代碼分析儀表板
- ✅ 自動修復建議
- ✅ 系統監控可視化
- ✅ API 管理界面
- ✅ 用戶認證和授權
- ✅ 深色/淺色主題切換
- ✅ 多語言支持

---

## 🚀 快速開始 / Quick Start

### 開發環境 / Development

```bash
cd apps/web

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev

# 訪問應用
# 前端: http://localhost:5173
# API: http://localhost:8000
```

### 構建生產版本 / Production Build

```bash
# 前端構建
npm run build

# API 部署
python3 services/api.py --prod

# 或 Docker 構建
docker build -t web-app:latest .
docker run -p 80:3000 web-app:latest
```

---

## 📱 前端開發 / Frontend Development

### 添加新頁面 / Adding New Page

```typescript
// src/pages/NewPage.tsx
import React from 'react';

export const NewPage: React.FC = () => {
  return (
    <div>
      <h1>New Page</h1>
    </div>
  );
};
```

### 添加新組件 / Adding New Component

```typescript
// src/components/NewComponent.tsx
import React from 'react';
import { Button } from '@/components/ui/button';

interface NewComponentProps {
  title: string;
}

export const NewComponent: React.FC<NewComponentProps> = ({ title }) => {
  return (
    <div>
      <h2>{title}</h2>
      <Button>Click me</Button>
    </div>
  );
};
```

### 使用 Hooks / Using Hooks

```typescript
import { useAuth } from '@/hooks/useAuth';
import { useData } from '@/hooks/useData';

export const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const { data, loading, error } = useData('/api/data');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{/* Render data */}</div>;
};
```

---

## 🔧 後端服務 / Backend Services

### FastAPI 伺服器 / FastAPI Server

```bash
# 安裝依賴
pip install -r requirements.txt

# 開發模式
python3 services/api.py --dev

# 生產模式
gunicorn -w 4 -b 0.0.0.0:8000 services.api:app
```

### API 端點 / API Endpoints

```
GET    /api/v1/health          健康檢查
POST   /api/v1/analyze         代碼分析
GET    /api/v1/analysis/:id    獲取分析結果
POST   /api/v1/auth/login      登錄
POST   /api/v1/auth/logout     登出
GET    /api/v1/user/profile    用戶資料
```

---

## 🐳 Docker 部署 / Docker Deployment

### 開發環境

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 生產環境

```bash
docker-compose up -d

# 查看日誌
docker-compose logs -f web
```

---

## ☸️ Kubernetes 部署 / Kubernetes Deployment

### 部署應用

```bash
kubectl apply -f apps/web/k8s/

# 驗證部署
kubectl get pods
kubectl get svc
```

### 檢查狀態

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

---

## 🧪 測試 / Testing

### 前端測試 / Frontend Tests

```bash
# 單元測試
npm run test:unit

# 整合測試
npm run test:integration

# E2E 測試
npm run test:e2e

# 覆蓋率
npm run test:coverage
```

### 後端測試 / Backend Tests

```bash
# 單元測試
pytest tests/unit

# 整合測試
pytest tests/integration

# 覆蓋率
pytest --cov=services tests/
```

---

## 📊 效能優化 / Performance Optimization

### 前端優化

- 代碼分割 (Code Splitting)
- 懶加載 (Lazy Loading)
- 圖像優化 (Image Optimization)
- 緩存策略 (Caching Strategy)

### 後端優化

- 資料庫查詢優化
- 快取策略 (Redis)
- API 限速 (Rate Limiting)
- 非同步處理 (Async Processing)

---

## 🔐 安全 / Security

### 前端安全

- XSS 防護 (XSS Protection)
- CSRF 防護 (CSRF Protection)
- CSP 策略 (Content Security Policy)
- HTTPS 強制 (Enforce HTTPS)

### 後端安全

- 輸入驗證 (Input Validation)
- SQL 注入防護 (SQL Injection Protection)
- 認證授權 (Authentication & Authorization)
- 速率限制 (Rate Limiting)

---

## 📈 監控與告警 / Monitoring & Alerting

### 應用監控

```bash
# 查看 Grafana 儀表板
kubectl port-forward svc/grafana 3000:3000 -n synergymesh
# 訪問: http://localhost:3000
```

### 日誌查看

```bash
# Docker
docker logs -f <container-id>

# Kubernetes
kubectl logs -f deployment/web -n synergymesh
```

---

## 📖 詳細文檔 / Detailed Documentation

- [Web 應用詳細文檔](./web/README.md)
- [API 文檔](./web/API.md)
- [部署指南](./web/DEPLOYMENT.md)
- [故障排除](./web/TROUBLESHOOTING.md)

---

## 🤝 貢獻指南 / Contributing

在開發應用時：

1. 遵循代碼風格指南
2. 編寫相應測試
3. 更新文檔
4. 運行本地驗證

```bash
npm run lint
npm run test
npm run build
```

---

## 📞 支援 / Support

- 📖 [應用文檔](./README.md)
- 🐛 [報告問題](https://github.com/SynergyMesh-admin/Unmanned-Island/issues)
- 💬 [討論](https://github.com/SynergyMesh-admin/Unmanned-Island/discussions)
