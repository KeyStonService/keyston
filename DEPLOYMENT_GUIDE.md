# 🚀 SynergyMesh 部署指南

# Deployment Guide

**文档版本**: 1.0.0  
**最后更新**: 2025-12-09  
**适用系统**: Unmanned Island System / SynergyMesh Platform

---

## 📋 目录

1. [部署概述](#部署概述)
2. [前置要求](#前置要求)
3. [快速部署](#快速部署)
4. [自动化引擎](#自动化引擎)
5. [架构集成](#架构集成)
6. [服务部署](#服务部署)
7. [验证与测试](#验证与测试)
8. [故障排查](#故障排查)

> **🤖 AI 模型部署**: 关于 AI 模型（LLM）的详细部署要求和配置，请参阅 [AI 模型部署指南](docs/AI_MODEL_DEPLOYMENT.md)

---

## 🎯 部署概述

本指南涵盖 SynergyMesh/Unmanned Island System 的完整部署流程，包括：

### 三大核心子系统

```
┌─────────────────────────────────────────────────────────────┐
│               🏝️ Unmanned Island System                     │
├─────────────────────────────────────────────────────────────┤
│  1️⃣ SynergyMesh Core Engine    - AI 决策 + 服务注册       │
│  2️⃣ Structural Governance       - Schema + SLSA 溯源       │
│  3️⃣ Autonomous Framework        - 五骨架 + 无人机控制      │
└─────────────────────────────────────────────────────────────┘
```

### 部署阶段

1. **环境检查** - 验证 Node.js, Python, Docker
2. **依赖安装** - npm workspaces + Python packages
3. **配置验证** - YAML 配置 + 骨架结构
4. **引擎启动** - automation_launcher.py
5. **服务部署** - Docker Compose
6. **系统验证** - 健康检查 + 集成测试

---

## 🔧 前置要求

### 必需环境

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Node.js | >= 18.0.0 | TypeScript 项目构建 |
| npm | >= 8.0.0 | 工作空间管理 |
| Python | >= 3.10 | 自动化脚本执行 |

### 可选环境（完整功能）

| 组件 | 版本要求 | 用途 |
|------|----------|------|
| Docker | >= 20.10 | 容器化部署 |
| Docker Compose | >= 2.0 | 服务编排 |
| ROS 2 | Humble | 无人机/自驾车组件 |
| Go | >= 1.20 | Go 服务（未来） |
| C++ | GCC 11+ / Clang 14+ | ROS/C++ 组件 |

### 系统要求

- **操作系统**: Linux (Ubuntu 22.04 推荐), macOS, Windows (WSL2)
- **内存**: 最低 4GB, 推荐 8GB+
- **磁盘**: 最低 10GB 可用空间
- **网络**: 互联网连接（依赖下载）

---

## ⚡ 快速部署

### 方法 1: 一键部署脚本（推荐）

```bash
# 完整部署（包含 Docker）
bash scripts/comprehensive-deploy.sh

# 仅本地服务（跳过 Docker）
bash scripts/comprehensive-deploy.sh --skip-docker

# 开发模式
bash scripts/comprehensive-deploy.sh --dev

# 跳过依赖安装（已安装过）
bash scripts/comprehensive-deploy.sh --skip-deps
```

### 方法 2: 传统部署脚本

```bash
# 使用传统 deploy.sh
bash deploy.sh deploy

# 查看状态
bash deploy.sh status

# 停止服务
bash deploy.sh stop
```

### 方法 3: 手动分步部署

```bash
# 1. 安装依赖
npm install
python3 -m pip install -e .

# 2. 构建项目
npm run build

# 3. 验证配置
python3 tools/docs/validate_index.py --verbose

# 4. 启动服务
docker compose up -d

# 5. 启动自动化引擎
python3 automation_launcher.py start
```

---

## 🤖 自动化引擎

### automation_launcher.py

全自动化引擎启动器，负责：

- 🎯 主控协调器（Master Orchestrator）
- 🔍 自动发现并注册引擎
- 🚀 自动启动所有引擎
- 📊 管理引擎生命周期
- 🔗 执行管道工作流
- 💓 系统健康监控

### 启动命令

```bash
# 启动全自动化引擎
python3 automation_launcher.py start

# 查看系统状态
python3 automation_launcher.py status

# 列出所有引擎
python3 automation_launcher.py list-engines

# 列出所有管道
python3 automation_launcher.py list-pipelines

# 启动特定引擎
python3 automation_launcher.py start-engine <engine_id>

# 执行任务
python3 automation_launcher.py task <engine_id> --operation scan

# 执行管道
python3 automation_launcher.py pipeline <pipeline_id> --input '{"key":"value"}'

# 停止系统
python3 automation_launcher.py stop
```

### 配置文件

- `DEFAULT_CONFIG` - 在 automation_launcher.py 中
- `engine_paths` - 引擎搜索路径
  - `tools/automation/engines`
  - `tools/refactor`

### 运行模式

| 模式 | 说明 | 使用场景 |
|------|------|----------|
| `autonomous` | 100% 自动 | 生产环境 |
| `supervised` | 需人工批准 | 测试环境 |
| `interactive` | 交互式 | 开发调试 |

```bash
# 指定运行模式
python3 automation_launcher.py start --mode supervised
```

---

## 🏗️ 架构集成

### 配置文件验证

```bash
# 验证所有核心配置
python3 tools/docs/validate_index.py --verbose

# 验证治理矩阵
make validate-governance

# 检查 YAML 语法
python3 -c "import yaml; yaml.safe_load(open('machinenativeops.yaml'))"
```

### 关键配置文件

| 文件 | 用途 |
|------|------|
| `machinenativeops.yaml` | 统一主配置入口 |
| `config/system-manifest.yaml` | 系统宣告清单 |
| `config/unified-config-index.yaml` | 统一配置索引 v3.0.0 |
| `config/system-module-map.yaml` | 模块映射 |
| `config/drone-config.yml` | 无人机编队配置 |
| `config/ai-constitution.yaml` | AI 最高指导宪章 |

### 五骨架架构验证

```bash
# 检查骨架目录
ls -la automation/autonomous/

# 输出应包含:
# - architecture-stability (C++ + ROS 2)
# - api-governance (Python)
# - security-observability (Go)
# - testing-compatibility (Python + YAML)
# - docs-examples (Markdown + YAML)
```

### Go 模块状态

`go.work` 文件中的 Go 模块当前处于**占位符状态**（已注释）：

```go
go 1.21

// NOTE: The following Go modules have been commented out because they do not exist
// in the repository. Uncomment and restore when the services are implemented.
// use (
//   ./services/api-gateway
//   ./services/agent-service
//   ./services/workflow-service
//   ./services/auth-service
//   ./services/notification-service
//   ./services/shared
// )
```

这些模块将在实质实现完成后重新启用。

### ROS/C++ 组件占位符

基础 C/C++ 文件已就位：

```
automation/autonomous/architecture-stability/
├── ros2_flight_control.hpp      # ROS 2 飞控头文件
├── CMakeLists.txt               # CMake 配置（占位符）
├── package.xml                  # ROS 2 包配置（占位符）
└── README.md                    # 架构文档
```

待实现功能：

- 100Hz 控制循环
- IMU 传感器融合
- PID 控制器
- ROS 2 Humble 集成

---

## 🐳 服务部署

### Docker Compose 部署

#### 核心服务（生产）

```bash
# 构建并启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止并移除
docker compose down
```

#### 开发环境

```bash
# 使用开发配置
docker compose -f docker-compose.dev.yml up -d

# 或使用 npm 脚本
npm run dev:stack
```

#### 工作流系统（可选）

```bash
# 启动完整工作流栈（包含 PostgreSQL, Redis, Prometheus, Grafana）
docker compose --profile workflow up -d

# 仅启动核心服务
docker compose up -d
```

### 服务端点

| 服务 | 端口 | 健康检查 | 用途 |
|------|------|----------|------|
| Contracts L1 API | 3000 | `/healthz` | 合约管理服务 |
| MCP Servers | 3001 | `/health` | MCP 协议服务器 |
| Dashboard | 8080 | N/A | 管理仪表板 |
| Workflow System | 8081 | N/A | 工作流引擎（可选）|
| Prometheus | 9090 | N/A | 监控指标（可选）|
| Grafana | 3010 | N/A | 可视化（可选）|

### 健康检查

```bash
# 检查 Contracts L1
curl http://localhost:3000/healthz

# 检查 MCP Servers
curl http://localhost:3001/health

# 检查 Dashboard
curl http://localhost:8080
```

---

## ✅ 验证与测试

### 自动验证脚本

```bash
# 生成并验证知识图谱
make all-kg

# 检查配置漂移
make check-drift

# 验证治理矩阵
make validate-governance

# 运行 linting
npm run lint

# 运行测试套件
npm run test
```

### 手动验证清单

- [ ] **环境检查**
  - [ ] Node.js 版本 >= 18.0.0
  - [ ] Python 版本 >= 3.10
  - [ ] Docker 和 Compose 可用
  
- [ ] **依赖安装**
  - [ ] npm 工作空间依赖已安装
  - [ ] Python 包已安装
  - [ ] TypeScript 项目已构建
  
- [ ] **配置验证**
  - [ ] machinenativeops.yaml 语法正确
  - [ ] 所有骨架目录存在
  - [ ] go.work 占位符确认
  
- [ ] **服务部署**
  - [ ] Docker 容器运行中
  - [ ] 健康检查通过
  - [ ] 端口可访问
  
- [ ] **自动化引擎**
  - [ ] automation_launcher.py 可执行
  - [ ] 主控协调器启动成功
  - [ ] 引擎注册正常

### 系统集成测试

```bash
# 端到端测试（如果可用）
npm run test:e2e

# 集成测试
npm run test:integration

# 单元测试
npm run test:unit
```

---

## 🔍 故障排查

### 常见问题

#### 1. npm install 失败

**症状**: `npm install` 报错或超时

**解决方案**:

```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 和 lock 文件
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 如果仍然失败，尝试使用不同的 registry
npm install --registry=https://registry.npmmirror.com
```

#### 2. Python 依赖安装失败

**症状**: `pip install` 报错

**解决方案**:

```bash
# 升级 pip
python3 -m pip install --upgrade pip

# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 重新安装
python3 -m pip install -e .
```

#### 3. Docker 构建失败

**症状**: `docker compose build` 失败

**解决方案**:

```bash
# 清理 Docker 资源
docker system prune -af

# 重新构建（不使用缓存）
docker compose build --no-cache

# 检查 Dockerfile 语法
docker compose config
```

#### 4. automation_launcher.py 导入错误

**症状**: `ImportError: No module named 'master_orchestrator'`

**解决方案**:

```bash
# 确保在正确的目录
cd /path/to/SynergyMesh

# 检查 Python 路径
export PYTHONPATH="${PYTHONPATH}:$(pwd)/tools/automation"

# 或使用完整路径
python3 -c "import sys; sys.path.insert(0, 'tools/automation'); import automation_launcher"
```

#### 5. 端口冲突

**症状**: 服务无法启动，端口已被占用

**解决方案**:

```bash
# 检查端口占用
lsof -i :3000
lsof -i :3001
lsof -i :8080

# 停止占用端口的进程
kill -9 <PID>

# 或修改 docker-compose.yml 中的端口映射
```

### 日志查看

```bash
# 查看部署脚本日志
cat .deployment_logs/npm-install.log
cat .deployment_logs/pip-install.log
cat .deployment_logs/npm-build.log

# 查看 Docker 日志
docker compose logs contracts-l1
docker compose logs mcp-servers
docker compose logs dashboard

# 实时跟踪日志
docker compose logs -f --tail=100
```

### 调试模式

```bash
# 启用详细输出
bash scripts/comprehensive-deploy.sh --dev

# Python 调试模式
python3 -m pdb automation_launcher.py start

# Node.js 调试模式
NODE_ENV=development npm run dev:stack
```

---

## 📚 相关文档

- **主文档**: [README.md](README.md)
- **快速开始**: [QUICK_START.md](QUICK_START.md)
- **部署清单**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **验证报告**: [DEPLOYMENT_VALIDATION_REPORT.md](DEPLOYMENT_VALIDATION_REPORT.md)
- **架构文档**: [docs/architecture/](docs/architecture/)
- **API 文档**: [docs/AUTO_ASSIGNMENT_API.md](docs/AUTO_ASSIGNMENT_API.md)

---

## 🆘 获取支持

- **GitHub Issues**: <https://github.com/SynergyMesh/SynergyMesh/issues>
- **Discussions**: <https://github.com/SynergyMesh/SynergyMesh/discussions>
- **Email**: <admin@synergymesh.io>

---

**文档维护**: SynergyMesh Team  
**许可证**: MIT License  
**版本**: 1.0.0 (2025-12-09)
