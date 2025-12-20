"""
Deployment Agent
部署代理

負責自動化部署、環境配置和監控設置
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from . import BaseAgent, AgentTask, AgentResult, AgentType

class DeploymentAgent(BaseAgent):
    """部署代理 - 第五階段處理"""
    
    def __init__(self, agent_type: AgentType, config: Dict[str, Any] = None):
        super().__init__(agent_type, config)
        self.deployment_strategies = {
            "docker": self._generate_docker_deployment,
            "kubernetes": self._generate_kubernetes_deployment,
            "serverless": self._generate_serverless_deployment,
            "hybrid": self._generate_hybrid_deployment
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據格式"""
        required_fields = ["code_generation", "testing", "architecture_design"]
        return all(field in input_data for field in required_fields)
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """處理部署任務"""
        start_time = datetime.now()
        
        try:
            # 提取相關數據
            code_generation = task.input_data.get("code_generation", {}).get("output_data", {})
            testing = task.input_data.get("testing", {}).get("output_data", {})
            architecture_design = task.input_data.get("architecture_design", {}).get("output_data", {})
            
            # 確定部署策略
            deployment_strategy = self._determine_deployment_strategy(architecture_design)
            
            # 生成部署配置
            deployment_config = await self.deployment_strategies[deployment_strategy](
                code_generation, architecture_design
            )
            
            # 生成環境配置
            environment_configs = await self._generate_environment_configs(code_generation, architecture_design)
            
            # 設置監控和日誌
            monitoring_setup = await self._setup_monitoring(deployment_config, architecture_design)
            
            # 配置CI/CD管道
            cicd_pipeline = await self._configure_cicd_pipeline(deployment_config, testing)
            
            # 生成部署腳本
            deployment_scripts = await self._generate_deployment_scripts(deployment_config)
            
            # 創建部署清單
            deployment_manifest = await self._create_deployment_manifest(
                deployment_config, environment_configs, monitoring_setup
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=True,
                output_data={
                    "deployment_strategy": deployment_strategy,
                    "deployment_config": deployment_config,
                    "environment_configs": environment_configs,
                    "monitoring_setup": monitoring_setup,
                    "cicd_pipeline": cicd_pipeline,
                    "deployment_scripts": deployment_scripts,
                    "deployment_manifest": deployment_manifest,
                    "estimated_deployment_time": self._estimate_deployment_time(deployment_config),
                    "resource_requirements": self._calculate_resource_requirements(deployment_config)
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_type=self.agent_type,
                success=False,
                output_data={},
                execution_time=0,
                error_message=str(e)
            )
    
    def _determine_deployment_strategy(self, architecture: Dict[str, Any]) -> str:
        """確定部署策略"""
        deployment_arch = architecture.get("deployment_architecture", {})
        deployment_method = deployment_arch.get("deployment_method", "docker")
        orchestration = deployment_arch.get("orchestration", "none")
        
        if orchestration == "kubernetes":
            return "kubernetes"
        elif deployment_method == "serverless":
            return "serverless"
        elif deployment_method == "docker":
            return "docker"
        else:
            return "hybrid"
    
    async def _generate_docker_deployment(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成Docker部署配置"""
        components = code.get("code_components", {})
        
        return {
            "dockerfiles": self._generate_dockerfiles(components),
            "docker_compose": self._generate_docker_compose(components),
            "docker_networks": ["app-network", "db-network"],
            "docker_volumes": {
                "postgres_data": {},
                "redis_data": {}
            },
            "environment_variables": self._generate_env_variables(components),
            "health_checks": self._generate_health_checks(components)
        }
    
    async def _generate_kubernetes_deployment(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成Kubernetes部署配置"""
        components = code.get("code_components", {})
        
        return {
            "namespaces": ["default", "monitoring"],
            "deployments": self._generate_k8s_deployments(components),
            "services": self._generate_k8s_services(components),
            "configmaps": self._generate_k8s_configmaps(components),
            "secrets": self._generate_k8s_secrets(components),
            "ingress": self._generate_k8s_ingress(components),
            "persistent_volumes": self._generate_k8s_persistent_volumes(),
            "hpa": self._generate_k8s_hpa(components)
        }
    
    async def _generate_serverless_deployment(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成無服務器部署配置"""
        return {
            "framework": "AWS Lambda",
            "functions": self._generate_lambda_functions(code),
            "api_gateway": self._generate_api_gateway_config(),
            "iam_roles": self._generate_iam_roles(),
            "environment_variables": self._generate_lambda_env_vars(),
            "triggers": ["api_gateway", "s3", "schedule"]
        }
    
    async def _generate_hybrid_deployment(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """生成混合部署配置"""
        return {
            "frontend": {
                "deployment": "static_hosting",
                "provider": "Netlify/Vercel",
                "config": self._generate_static_hosting_config()
            },
            "backend": {
                "deployment": "docker",
                "config": await self._generate_docker_deployment(code, architecture)
            },
            "database": {
                "deployment": "managed_service",
                "provider": "AWS RDS/Heroku Postgres",
                "config": self._generate_database_config()
            }
        }
    
    async def _generate_environment_configs(self, code: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, str]:
        """生成環境配置"""
        return {
            ".env.development": self._generate_dev_env(),
            ".env.staging": self._generate_staging_env(),
            ".env.production": self._generate_prod_env(),
            ".env.example": self._generate_env_example()
        }
    
    async def _setup_monitoring(self, deployment_config: Dict[str, Any], architecture: Dict[str, Any]) -> Dict[str, Any]:
        """設置監控"""
        return {
            "metrics": {
                "system": "Prometheus",
                "application": "Custom metrics",
                "infrastructure": "Node Exporter"
            },
            "logging": {
                "framework": "ELK Stack",
                "log_level": "INFO",
                "retention": "30 days"
            },
            "alerting": {
                "tool": "Grafana + Alertmanager",
                "channels": ["email", "slack"],
                "thresholds": self._generate_alert_thresholds()
            },
            "dashboards": self._generate_monitoring_dashboards()
        }
    
    async def _configure_cicd_pipeline(self, deployment_config: Dict[str, Any], testing: Dict[str, Any]) -> Dict[str, Any]:
        """配置CI/CD管道"""
        return {
            "platform": "GitHub Actions",
            "triggers": ["push", "pull_request"],
            "stages": [
                {
                    "name": "lint",
                    "commands": ["npm run lint", "flake8 ."]
                },
                {
                    "name": "test",
                    "commands": ["npm test", "pytest"]
                },
                {
                    "name": "build",
                    "commands": ["npm run build", "docker build -t app ."]
                },
                {
                    "name": "deploy",
                    "commands": ["docker-compose up -d"],
                    "environment": "staging"
                }
            ],
            "artifacts": ["build/", "dist/", "coverage/"],
            "notifications": ["slack", "email"]
        }
    
    async def _generate_deployment_scripts(self, deployment_config: Dict[str, Any]) -> Dict[str, str]:
        """生成部署腳本"""
        return {
            "deploy.sh": self._generate_deploy_script(),
            "rollback.sh": self._generate_rollback_script(),
            "health-check.sh": self._generate_health_check_script(),
            "backup.sh": self._generate_backup_script(),
            "cleanup.sh": self._generate_cleanup_script()
        }
    
    async def _create_deployment_manifest(self, config: Dict[str, Any], env_configs: Dict[str, str], monitoring: Dict[str, Any]) -> Dict[str, Any]:
        """創建部署清單"""
        return {
            "version": "1.0",
            "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "configuration": config,
            "environments": list(env_configs.keys()),
            "monitoring": monitoring,
            "deployment_order": ["database", "backend", "frontend"],
            "health_endpoints": {
                "backend": "/health",
                "frontend": "/",
                "database": "connection_check"
            },
            "rollback_plan": {
                "enabled": True,
                "retention": "3_versions",
                "automatic": False
            },
            "scaling": {
                "min_replicas": 2,
                "max_replicas": 10,
                "target_cpu": 70
            }
        }
    
    # 輔助方法
    def _generate_dockerfiles(self, components: Dict[str, Any]) -> Dict[str, str]:
        """生成Dockerfile"""
        dockerfiles = {}
        
        # 前端Dockerfile
        if "frontend" in components:
            dockerfiles["frontend"] = '''
# Frontend Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
'''
        
        # 後端Dockerfile
        if "backend" in components:
            dockerfiles["backend"] = '''
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        
        return dockerfiles
    
    def _generate_docker_compose(self, components: Dict[str, Any]) -> str:
        """生成docker-compose.yml"""
        return f'''
version: '3.8'

services:
{"  frontend:" if "frontend" in components else ""}
{"    build: ./frontend" if "frontend" in components else ""}
{"    ports:" if "frontend" in components else ""}
{"      - '3000:80'" if "frontend" in components else ""}
{"    depends_on:" if "frontend" in components else ""}
{"      - backend" if "frontend" in components else ""}
{"    networks:" if "frontend" in components else ""}
{"      - app-network" if "frontend" in components else ""}

{"  backend:" if "backend" in components else ""}
{"    build: ./backend" if "backend" in components else ""}
{"    ports:" if "backend" in components else ""}
{"      - '8000:8000'" if "backend" in components else ""}
{"    environment:" if "backend" in components else ""}
{"      - DATABASE_URL=postgresql://user:password@db:5432/app" if "backend" in components else ""}
{"      - REDIS_URL=redis://redis:6379" if "backend" in components else ""}
{"    depends_on:" if "backend" in components else ""}
{"      - db" if "backend" in components else ""}
{"      - redis" if "backend" in components else ""}
{"    networks:" if "frontend" in components else ""}
{"      - app-network" if "frontend" in components else ""}

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - '5432:5432'
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - '6379:6379'
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
'''
    
    def _generate_env_variables(self, components: Dict[str, Any]) -> Dict[str, str]:
        """生成環境變量"""
        return {
            "DATABASE_URL": "postgresql://user:password@localhost:5432/app",
            "REDIS_URL": "redis://localhost:6379",
            "JWT_SECRET": "your-secret-key",
            "NODE_ENV": "production",
            "PORT": "8000"
        }
    
    def _generate_health_checks(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """生成健康檢查"""
        return {
            "backend": {
                "endpoint": "/health",
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            },
            "frontend": {
                "endpoint": "/",
                "interval": "30s",
                "timeout": "5s",
                "retries": 3
            }
        }
    
    def _estimate_deployment_time(self, config: Dict[str, Any]) -> Dict[str, int]:
        """估算部署時間"""
        return {
            "build_time_minutes": 3,
            "deployment_time_minutes": 2,
            "health_check_minutes": 1,
            "total_time_minutes": 6
        }
    
    def _calculate_resource_requirements(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """計算資源需求"""
        return {
            "cpu": "2 cores",
            "memory": "4GB RAM",
            "storage": "20GB SSD",
            "network": "100Mbps"
        }
    
    # 配置文件生成方法
    def _generate_dev_env(self) -> str:
        return '''
# Development Environment
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/app_dev
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-key
NODE_ENV=development
DEBUG=true
LOG_LEVEL=debug
'''
    
    def _generate_staging_env(self) -> str:
        return '''
# Staging Environment
DATABASE_URL=postgresql://staging_user:staging_password@db:5432/app_staging
REDIS_URL=redis://redis:6379
JWT_SECRET=staging-secret-key
NODE_ENV=staging
DEBUG=false
LOG_LEVEL=info
'''
    
    def _generate_prod_env(self) -> str:
        return '''
# Production Environment
DATABASE_URL=postgresql://prod_user:prod_password@db:5432/app_prod
REDIS_URL=redis://redis:6379
JWT_SECRET=super-secure-production-secret-key
NODE_ENV=production
DEBUG=false
LOG_LEVEL=error
'''
    
    def _generate_env_example(self) -> str:
        return '''
# Environment Variables Example
DATABASE_URL=postgresql://user:password@localhost:5432/app
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
NODE_ENV=development
DEBUG=false
LOG_LEVEL=info
'''
    
    def _generate_deploy_script(self) -> str:
        return '''#!/bin/bash

# Deployment Script
set -e

echo "Starting deployment..."

# Pull latest code
git pull origin main

# Build and deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
sleep 30

# Health check
./health-check.sh

echo "Deployment completed successfully!"
'''
    
    def _generate_rollback_script(self) -> str:
        return '''#!/bin/bash

# Rollback Script
set -e

echo "Starting rollback..."

# Get previous version
PREVIOUS_VERSION=$(git rev-parse HEAD~1)

# Rollback to previous version
git checkout $PREVIOUS_VERSION
docker-compose down
docker-compose up -d

echo "Rollback to $PREVIOUS_VERSION completed!"
'''
    
    def _generate_health_check_script(self) -> str:
        return '''#!/bin/bash

# Health Check Script
set -e

echo "Performing health checks..."

# Check backend health
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $BACKEND_HEALTH -ne 200 ]; then
    echo "Backend health check failed!"
    exit 1
fi

# Check frontend health
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ $FRONTEND_HEALTH -ne 200 ]; then
    echo "Frontend health check failed!"
    exit 1
fi

echo "All health checks passed!"
'''
    
    def _generate_backup_script(self) -> str:
        return '''#!/bin/bash

# Backup Script
set -e

echo "Creating backup..."

# Backup database
docker exec db pg_dump -U user app > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup application data
tar -czf app_backup_$(date +%Y%m%d_%H%M%S).tar.gz .

echo "Backup completed!"
'''
    
    def _generate_cleanup_script(self) -> str:
        return '''#!/bin/bash

# Cleanup Script
set -e

echo "Cleaning up..."

# Remove unused Docker images
docker image prune -f

# Remove unused volumes
docker volume prune -f

# Remove old backups (keep last 5)
find . -name "backup_*.sql" -type f | sort -r | tail -n +6 | xargs rm -f
find . -name "app_backup_*.tar.gz" -type f | sort -r | tail -n +6 | xargs rm -f

echo "Cleanup completed!"
'''

__all__ = ["DeploymentAgent"]