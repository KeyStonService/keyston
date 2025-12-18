# Life System Development Environment - README

## 🧠💓 01-core Life System DevContainer

這個開發容器專為 01-core 生命系統設計，提供完整的開發、測試和監控環境。

### 系統架構

```
01-core Life System Architecture:
┌─────────────────────────────────────────┐
│  🧠 Brain Engine (AI Reasoning)        │ :3015-3017
├─────────────────────────────────────────┤
│  💓 Heart Engine (Resource Orchestr.)  │ :3018-3019
├─────────────────────────────────────────┤
│  💗 Heartbeat (Vital Signs Monitor)    │ :3020-3021
├─────────────────────────────────────────┤
│  🧘 FixOps SLAgeist (Consciousness)    │ :3010
└─────────────────────────────────────────┘
           Supporting Services:
         🗄️ PostgreSQL :5432
         🔄 Redis :6379
         📊 Prometheus :9090
         📈 Grafana :3000
```

### 快速開始

1. **自動啟動生命系統**:

   ```bash
   bash start-life-system.sh
   ```

2. **檢查系統健康**:

   ```bash
   .devcontainer/scripts/health-check.sh
   ```

3. **手動啟動支援服務**:
   ```bash
   docker-compose -f .devcontainer/docker-compose.yml up -d
   ```

### 服務端點

#### 🧠💓 生命系統組件

- **意識系統 (Consciousness)**: http://localhost:3010
  - `/consciousness` - 意識狀態
  - `/health` - 健康檢查
  - `/metrics` - Prometheus 指標

- **大腦引擎 (Brain Engine)**: http://localhost:3015
  - `/api/reasoning` - AI 推理
  - `/api/decisions` - 決策記錄
  - `/api/consciousness` - 意識集成

- **心臟引擎 (Heart Engine)**: http://localhost:3018
  - `/api/orchestration` - 資源編排
  - `/api/deployments` - 部署管理
  - `/api/health` - 資源健康

- **心跳引擎 (Heartbeat Engine)**: http://localhost:3020
  - `/api/vitals` - 生命體徵
  - `/api/alerts` - 告警系統
  - `/dashboard` - 實時儀表板 (:3021)

#### 📊 監控與觀測

- **Prometheus**: http://localhost:9090
  - 指標收集與查詢
  - 生命系統專用指標

- **Grafana**: http://localhost:3000
  - 用戶名: admin
  - 密碼: consciousness_2024
  - 生命系統儀表板

#### 🗄️ 數據服務

- **PostgreSQL**: localhost:5432
  - 數據庫: life_system
  - 用戶名: life_admin
  - 密碼: consciousness_2024

- **Redis**: localhost:6379
  - 緩存與事件總線
  - 用於組件間通訊

### 開發工作流程

1. **開發前準備**:

   ```bash
   # 啟動支援服務
   docker-compose -f .devcontainer/docker-compose.yml up -d postgres redis

   # 等待服務就緒
   sleep 10
   ```

2. **啟動生命系統**:

   ```bash
   # 自動啟動所有組件
   bash start-life-system.sh

   # 或者手動啟動每個組件
   cd 01-core/brain/brain-L1 && npm start &
   cd 01-core/heart/heart-L1 && npm start &
   cd 01-core/heartbeat/heartbeat-L1 && npm start &
   cd 01-core/lifecycle/fixops-slageist/fixops-slageist-L1 && npm start &
   ```

3. **測試與驗證**:

   ```bash
   # 健康檢查
   .devcontainer/scripts/health-check.sh

   # API 測試
   curl http://localhost:3010/consciousness | jq
   curl http://localhost:3015/api/reasoning/status | jq
   curl http://localhost:3018/api/health | jq
   curl http://localhost:3020/api/vitals | jq
   ```

### 數據庫結構

生命系統使用專用的數據庫表結構：

```sql
-- 大腦引擎
brain_decisions           -- AI 決策記錄
brain_learning_patterns   -- 學習模式

-- 心臟引擎
heart_orchestrations      -- 編排操作
heart_resource_health     -- 資源健康

-- 心跳引擎
heartbeat_vitals          -- 生命體徵
heartbeat_alerts          -- 告警記錄

-- 意識集成
consciousness_states      -- 意識狀態
```

### 環境變量

重要的環境變量配置：

```bash
# 生命系統端口
BRAIN_PORT=3015
HEART_PORT=3018
HEARTBEAT_PORT=3020
FIXOPS_SLAGEIST_PORT=3010

# 數據庫連接
POSTGRES_HOST=postgres
REDIS_HOST=redis

# 開發模式
NODE_ENV=development
LOG_LEVEL=debug
```

### 故障排查

#### 常見問題

1. **服務無法連接**:

   ```bash
   # 檢查容器狀態
   docker-compose -f .devcontainer/docker-compose.yml ps

   # 檢查網絡
   docker network ls | grep life-system
   ```

2. **數據庫連接失敗**:

   ```bash
   # 測試數據庫連接
   docker-compose -f .devcontainer/docker-compose.yml exec postgres \
     pg_isready -U life_admin -d life_system
   ```

3. **Redis 連接問題**:
   ```bash
   # 測試 Redis
   docker-compose -f .devcontainer/docker-compose.yml exec redis redis-cli ping
   ```

#### 重置環境

```bash
# 停止所有服務
docker-compose -f .devcontainer/docker-compose.yml down -v

# 清理數據
docker volume prune

# 重新啟動
docker-compose -f .devcontainer/docker-compose.yml up -d
```

### 開發注意事項

1. **生命系統組件相互依賴**:
   - Brain 需要 Consciousness 狀態
   - Heart 需要 Brain 決策
   - Heartbeat 監控所有組件

2. **啟動順序重要**:
   - 先啟動支援服務 (DB, Redis)
   - 再啟動 FixOps SLAgeist (Consciousness)
   - 然後啟動 Brain, Heart, Heartbeat

3. **性能監控**:
   - 使用 Prometheus 指標監控性能
   - Grafana 儀表板提供可視化
   - Heartbeat 提供實時健康狀態

### 擴展開發

要添加新的生命系統組件：

1. 在 `01-core/` 下創建新組件目錄
2. 實現標準生命系統接口
3. 更新 docker-compose.yml
4. 添加 Prometheus 指標
5. 更新啟動腳本

### 參考文檔

- [生命系統完整文檔](../01-core/LIFE_SYSTEM_COMPLETE.md)
- [啟動腳本](../start-life-system.sh)
- [模組目錄](../MODULE_CATALOG.md)
- [操作手冊](../OPERATIONS_MANUAL.md)
