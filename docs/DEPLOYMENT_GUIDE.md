# Deployment Guide | 部署指南

## Overview | 概述

This guide provides step-by-step instructions for deploying the SynergyMesh Workflow System in various environments.

本指南提供了在各種環境中部署 SynergyMesh 工作流程系統的分步說明。

## Prerequisites | 先決條件

### System Requirements | 系統要求

- **CPU:** 2+ cores (4+ recommended for production)
- **Memory:** 4GB minimum (8GB+ recommended)
- **Storage:** 20GB minimum
- **OS:** Linux (Ubuntu 22.04+, RHEL 8+, or similar)

### Software Requirements | 軟件要求

```bash
# Python
python3 --version  # 3.10+

# Docker (optional)
docker --version  # 24.0+

# Kubernetes (optional)
kubectl version  # 1.28+
```

## Deployment Options | 部署選項

### Option 1: Local Development | 本地開發

```bash
# Clone repository
git clone https://github.com/synergymesh/SynergyMesh.git
cd SynergyMesh

# Install dependencies
pip install -r requirements-workflow.txt

# Configure
cp config/main-configuration.yaml config/local-configuration.yaml

# Run
./scripts/run-instant-execution.sh
```

### Option 2: Docker | Docker 部署

```bash
# Build image
docker build -f Dockerfile.workflow -t synergymesh/workflow:latest .

# Run container
docker run -d \
  --name workflow-system \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config:ro \
  synergymesh/workflow:latest

# Check health
curl http://localhost:8080/health
```

### Option 3: Docker Compose | Docker Compose 部署

```bash
# Start full stack
docker-compose -f docker-compose.workflow.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f workflow-system

# Stop
docker-compose down
```

### Option 4: Kubernetes | Kubernetes 部署

```bash
# Create namespace
kubectl create namespace synergymesh

# Apply deployment
kubectl apply -f deployment/kubernetes/workflow-deployment.yaml

# Check status
kubectl get pods -n synergymesh

# Port forward for testing
kubectl port-forward -n synergymesh svc/workflow-system 8080:80
```

## Configuration | 配置

### Environment Variables | 環境變量

```bash
# Core settings
export LOG_LEVEL=info
export EXECUTION_MODE=strict

# Database
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=workflow
export POSTGRES_USER=workflow
export POSTGRES_PASSWORD=changeme

# Redis
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Security
export SECRET_KEY=your-secret-key
export JWT_SECRET=your-jwt-secret
```

### Configuration Files | 配置文件

Main configuration file: `config/main-configuration.yaml`

Key sections:
- `core_engine`: Engine settings
- `ai_governance`: AI configuration
- `validation_system`: Validation rules
- `deployment`: Deployment strategy
- `observability`: Monitoring settings

## Health Checks | 健康檢查

```bash
# Liveness check
curl http://localhost:8080/health/live

# Readiness check
curl http://localhost:8080/health/ready

# Detailed status
curl http://localhost:8080/health/status
```

## Monitoring | 監控

### Prometheus Metrics

Access metrics:
```bash
curl http://localhost:8080/metrics
```

### Grafana Dashboard

1. Access Grafana: http://localhost:3000
2. Login (default: admin/admin)
3. Import dashboard from `config/grafana-dashboard.json`

### Log Aggregation

Logs are output to:
- Console (stdout/stderr)
- File: `logs/workflow.log`
- Elasticsearch (if configured)

## Troubleshooting | 故障排除

### Common Issues | 常見問題

**Issue:** Port already in use
```bash
# Find and kill process
lsof -i :8080
kill -9 <PID>
```

**Issue:** Permission denied
```bash
# Fix permissions
chmod +x scripts/run-instant-execution.sh
chown -R $USER:$USER config/
```

**Issue:** Database connection failed
```bash
# Check database
psql -h localhost -U workflow -d workflow

# Reset database
dropdb workflow
createdb workflow
```

## Security Considerations | 安全注意事項

1. **Secrets Management**
   - Never commit secrets to version control
   - Use environment variables or secret management tools
   - Rotate secrets regularly (30-day cycle)

2. **Network Security**
   - Enable TLS for production
   - Use firewalls to restrict access
   - Implement mTLS for service-to-service communication

3. **Access Control**
   - Configure RBAC properly
   - Use strong authentication (OAuth2)
   - Enable audit logging

4. **Container Security**
   - Run as non-root user
   - Scan images regularly
   - Keep base images updated

## Performance Tuning | 性能調優

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_executions_timestamp ON executions(timestamp);

-- Analyze tables
ANALYZE contracts;
ANALYZE executions;
```

### Application Tuning

```yaml
# config/main-configuration.yaml
core_engine:
  contract_engine:
    registry:
      cache_enabled: true
      cache_ttl_seconds: 600  # Increase for better performance

pipeline:
  execution:
    concurrency: 20  # Increase for higher throughput
```

## Backup & Recovery | 備份與恢復

### Database Backup

```bash
# Backup
pg_dump -h localhost -U workflow workflow > backup.sql

# Restore
psql -h localhost -U workflow workflow < backup.sql
```

### Configuration Backup

```bash
# Backup configs
tar czf config-backup.tar.gz config/

# Restore
tar xzf config-backup.tar.gz
```

## Scaling | 擴展

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale workflow-system=3

# Kubernetes
kubectl scale deployment workflow-system -n synergymesh --replicas=5
```

### Vertical Scaling

Update resource limits in deployment configuration.

## Maintenance | 維護

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild
docker-compose build

# Rolling restart
docker-compose up -d --no-deps --build workflow-system
```

### Log Rotation

Configure logrotate:
```bash
/app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 workflow workflow
}
```

## Support | 支持

For deployment issues:
- Documentation: [docs/](../docs/)
- Issues: [GitHub Issues](https://github.com/synergymesh/issues)
- Community: [Discussions](https://github.com/synergymesh/discussions)
