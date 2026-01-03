# Phase 1 Setup Guide | Phase 1 設置指南

Complete setup guide for Phase 1 (Q1 2026) components.

Phase 1 (Q1 2026) 組件的完整設置指南。

---

## 📋 Prerequisites | 先決條件

### Required Software

- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- **Redis**: v7.0 or higher (for Scheduler)
- **Docker** (optional): For containerized deployment
- **Git**: For version control

### System Requirements

- **Memory**: Minimum 4GB RAM
- **Disk**: Minimum 2GB free space
- **OS**: macOS, Linux, or Windows with WSL2

---

## 🚀 Quick Start | 快速開始

### 1. Clone Repository

```bash
git clone https://github.com/keystone-api/keystone-ai.git
cd keystone-ai
```

### 2. Install Dependencies

```bash
# Install root dependencies
npm install

# Install workspace dependencies
npm install --workspaces
```

### 3. Configure Environment Variables

#### API Gateway

```bash
cd services/api-gateway
cp .env.example .env
# Edit .env with your configuration
```

#### Scheduler

```bash
cd services/scheduler
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start Redis (Required for Scheduler)

#### Option A: Using Docker

```bash
docker run -d --name phase1-redis -p 6379:6379 redis:7-alpine
```

#### Option B: Using local Redis

```bash
# macOS (with Homebrew)
brew install redis
brew services start redis

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 5. Start Services

#### Terminal 1: API Gateway

```bash
cd services/api-gateway
npm run dev
```

Access at: <http://localhost:8000>

#### Terminal 2: Scheduler

```bash
cd services/scheduler
npm run dev
```

#### Terminal 3: Web Dashboard

```bash
cd apps/web
npm run dev
```

Access at: <http://localhost:5173>

---

## 🐳 Docker Deployment | Docker 部署

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose -f docker-compose.phase1.yml up -d

# View logs
docker-compose -f docker-compose.phase1.yml logs -f

# Stop all services
docker-compose -f docker-compose.phase1.yml down
```

### Services & Ports

| Service | Port | URL |
|---------|------|-----|
| API Gateway | 8000 | <http://localhost:8000> |
| Dashboard | 3000 | <http://localhost:3000> |
| Redis | 6379 | redis://localhost:6379 |

---

## 🧪 Testing | 測試

### API Gateway Tests

```bash
cd services/api-gateway

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Test Coverage Goals

- Unit tests: 80%+ coverage
- Integration tests: Key endpoints covered
- E2E tests: Critical user flows

---

## 📚 API Documentation | API 文檔

### Swagger UI (Interactive)

Once API Gateway is running, access:

```
http://localhost:8000/api/docs/ui
```

Features:

- Interactive API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

### OpenAPI JSON

```
http://localhost:8000/api/docs
```

Use this URL to import into:

- Postman
- Insomnia
- API testing tools

---

## 🔧 Configuration Guide | 配置指南

### API Gateway Configuration

**File**: `services/api-gateway/.env`

```env
# Server
PORT=8000
NODE_ENV=development

# JWT Authentication
JWT_SECRET=<generate-secure-secret>
JWT_EXPIRES_IN=1h

# Rate Limiting
API_RATE_LIMIT=100
RATE_LIMIT_WINDOW_MS=900000

# CORS
CORS_ORIGIN=*

# Logging
LOG_LEVEL=info
```

#### Generate Secure JWT Secret

```bash
# Using OpenSSL
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Scheduler Configuration

**File**: `services/scheduler/.env`

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Job Queue
MAX_CONCURRENT_JOBS=10
JOB_TIMEOUT=300000
HISTORY_RETENTION_DAYS=90

# Logging
LOG_LEVEL=info
```

---

## 📊 Monitoring & Health Checks | 監控與健康檢查

### Health Endpoints

#### Basic Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-16T23:00:00.000Z",
  "uptime": 123.456,
  "version": "1.0.0"
}
```

#### Detailed Health Check

```bash
curl http://localhost:8000/api/v1/system/health
```

#### System Metrics

```bash
curl http://localhost:8000/api/v1/system/metrics
```

### Dashboard Monitoring

Access the dashboard at <http://localhost:5173/dashboard>

Features:

- Real-time metrics
- System health status
- Resource usage
- Activity feed
- Log viewer

---

## 🔐 Authentication Setup | 認證設置

### Default Admin User

For development, a default admin user is available:

```
Email: admin@example.com
Password: password
```

⚠️ **Important**: Change or disable this in production!

### Login Example

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password"
  }'
```

Response:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": "1h",
  "user": {
    "id": "1",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### Using the Token

```bash
curl http://localhost:8000/api/v1/resources \
  -H "Authorization: Bearer <your-token-here>"
```

---

## 📝 Scheduler Usage | 調度器使用

### Schedule a Cron Job

```typescript
import { scheduler } from '@synergymesh/scheduler';

// Daily backup at 2 AM UTC
scheduler.schedule('daily-backup', '0 2 * * *', async () => {
  await performBackup();
}, {
  timezone: 'UTC',
  priority: 'high',
  maxRetries: 3,
  timeout: 300000
});
```

### Schedule a One-Time Task

```typescript
scheduler.scheduleOnce('cleanup', new Date('2026-01-01T00:00:00Z'), async () => {
  await cleanupOldData();
});
```

### Schedule an Interval Task

```typescript
// Health check every minute
scheduler.scheduleInterval('health-check', 60000, async () => {
  await checkSystemHealth();
});
```

### Manage Jobs

```typescript
// Pause a job
scheduler.pauseJob('daily-backup');

// Resume a job
scheduler.resumeJob('daily-backup');

// Delete a job
scheduler.deleteJob('daily-backup');

// Get job details
const job = scheduler.getJob('daily-backup');

// List all jobs
const jobs = scheduler.listJobs();

// Get execution history
const history = scheduler.getJobHistory('daily-backup', { limit: 10 });
```

---

## 🐛 Troubleshooting | 故障排除

### Issue: Redis Connection Failed

**Error**: `Error: Redis connection refused`

**Solution**:

```bash
# Check if Redis is running
redis-cli ping

# Start Redis if not running
docker start phase1-redis
# OR
brew services start redis
```

### Issue: Port Already in Use

**Error**: `EADDRINUSE: address already in use :::8000`

**Solution**:

```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=8001 npm run dev
```

### Issue: Module Not Found

**Error**: `Cannot find module '@synergymesh/...'`

**Solution**:

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Issue: JWT Secret Error

**Error**: `JWT_SECRET is required in production`

**Solution**:

```bash
# Set environment variable
export JWT_SECRET=$(openssl rand -base64 32)

# Or add to .env file
echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
```

---

## 🔄 Development Workflow | 開發流程

### 1. Make Changes

Edit files in `src/` directories

### 2. Auto-Reload

Services will auto-reload on file changes (dev mode)

### 3. Run Tests

```bash
npm test
```

### 4. Build for Production

```bash
# Build specific service
cd services/api-gateway
npm run build

# Or build all workspaces
npm run build --workspaces
```

### 5. Run Production Build

```bash
npm start
```

---

## 📦 Production Deployment | 生產部署

### Environment Configuration

1. Set `NODE_ENV=production`
2. Configure secure JWT_SECRET
3. Set appropriate CORS_ORIGIN
4. Configure Redis password
5. Use TLS/SSL certificates

### Docker Production Build

```bash
# Build images
docker-compose -f docker-compose.phase1.yml build

# Push to registry
docker tag phase1-api-gateway:latest your-registry/api-gateway:1.0.0
docker push your-registry/api-gateway:1.0.0
```

### Kubernetes Deployment (Phase 2)

Phase 2 will include complete Kubernetes deployment with:

- Helm charts
- Horizontal Pod Autoscaling
- Service mesh integration
- Observability stack

---

## 📖 Additional Resources | 其他資源

### Documentation

- [Phase 1 Architecture](./PHASE1_ARCHITECTURE.md)
- [Phase 1 Implementation Summary](./PHASE1_IMPLEMENTATION_SUMMARY.md)
- [Phase 1 Completion Report](../PHASE1_COMPLETION.md)
- [2026 Roadmap](./roadmap-2026.yaml)

### API Documentation

- Swagger UI: <http://localhost:8000/api/docs/ui>
- OpenAPI JSON: <http://localhost:8000/api/docs>
- API README: `services/api-gateway/README.md`

### Support

- GitHub Issues: <https://github.com/keystone-api/keystone-ai/issues>
- Email: <support@synergymesh.io>

---

## ✅ Verification Checklist | 驗證清單

### Development Setup

- [ ] Node.js v18+ installed
- [ ] Redis running on port 6379
- [ ] Dependencies installed (`npm install`)
- [ ] Environment files configured (.env)
- [ ] API Gateway running on port 8000
- [ ] Scheduler service running
- [ ] Dashboard accessible at localhost:5173

### API Testing

- [ ] Health endpoint responds
- [ ] Can login with default credentials
- [ ] Can create/read resources
- [ ] Can create/list tasks
- [ ] Swagger UI accessible

### Scheduler Testing

- [ ] Can schedule a cron job
- [ ] Can schedule one-time task
- [ ] Can list scheduled jobs
- [ ] Job execution history tracked

### Production Readiness

- [ ] JWT_SECRET configured
- [ ] CORS_ORIGIN set to specific domains
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Health checks passing
- [ ] Docker images build successfully
- [ ] All tests passing

---

**Setup Guide Version**: 1.0.0  
**Last Updated**: 2025-12-16  
**Maintained By**: SynergyMesh Team
