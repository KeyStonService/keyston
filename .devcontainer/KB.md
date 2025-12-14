# .devcontainer 知识库文档

## 目录概述

`.devcontainer` 目录包含开发容器配置，定义了一个完整的企业级开发环境。它使用 VS Code Remote Container 功能和 Docker Compose，为开发者提供一致的、隔离的开发环境，包含所有必需的工具链、依赖和服务。

**核心目标：**

- 提供一致的开发环境（不同机器、不同OS保持一致）
- 自动化开发环境初始化
- 集成企业级工具链（安全扫描、策略引擎等）
- 支持本地多服务编排和监控

---

## 目录结构树

```
.devcontainer/
├── devcontainer.json          # VS Code 开发容器配置（主配置文件）
├── Dockerfile                 # Docker 镜像定义（开发环境镜像 - 已优化）
├── docker-compose.dev.yml     # Docker Compose 本地编排配置
├── prometheus.yml             # Prometheus 监控配置
├── requirements.txt           # Python 依赖列表
├── setup.sh                   # 初始化脚本（入口点 - 已优化）
└── install-optional-tools.sh  # 可选工具安装脚本（按需执行）

总计：7 个文件
```

---

## 详细文件说明

### 1. devcontainer.json

**功能：** VS Code 开发容器主配置文件

**主要职责：**

- 定义容器运行时配置
- 配置端口转发和自动打开
- 指定 VSCode 扩展和编辑器设置
- 定义初始化命令和启动命令

**关键配置详解：**

| 配置项            | 值                                                        | 说明                                     |
| ----------------- | --------------------------------------------------------- | ---------------------------------------- |
| name              | Keystone Platform - Enterprise Governance Base            | 容器名称标识                             |
| image             | mcr.microsoft.com/vscode/devcontainers/typescript-node:18 | 基础镜像（微软官方Node18镜像）           |
| forwardPorts      | [3000, 8080, 9090]                                        | 转发端口到本地（Web应用、API网关、监控） |
| postCreateCommand | bash .devcontainer/setup.sh                               | 容器创建后执行初始化脚本                 |
| postStartCommand  | npm run dev &                                             | 容器启动后在后台运行开发服务器           |
| remoteUser        | node                                                      | 容器内运行用户                           |

**Feature 功能配置：**

- `docker-in-docker:2` - 在容器内运行Docker（用于构建镜像）
- `kubectl-helm-minikube:1` - Kubernetes 工具链
- `git:1` - Git 版本控制工具
- `python:1` - Python 运行时

**端口转发配置：**

```json
"3000": { "label": "Web Application", "onAutoForward": "openPreview" }
"8080": { "label": "API Gateway", "onAutoForward": "notify" }
"9090": { "label": "Monitoring", "onAutoForward": "notify" }
```

**扩展和编辑器设置：**

- TypeScript Next、TailwindCSS、Kubernetes Tools、YAML、Prettier
- 启用自动格式化、ESLint 自动修复、自动保存

**Docker 挂载：**

- `/var/run/docker.sock` - 允许容器访问宿主机 Docker daemon

**依赖关系：**

- 依赖 Dockerfile（定义镜像）
- 依赖 setup.sh（初始化脚本）
- 依赖 requirements.txt（Python 依赖）

---

### 2. Dockerfile

**功能：** 定義開發環境 Docker 鏡像（已優化以加快構建速度）

**主要職責：**

- 基於 Node.js 18 基礎鏡像擴展
- 安裝核心開發工具鏈（最小化安裝）
- 配置關鍵雲原生工具（kubectl、helm）
- 設置工作目錄和 Python 環境

**工具鏈安裝清單（已優化）：**

| 工具類別     | 工具名稱         | 功能說明                               | 安裝方式                  |
| ------------ | ---------------- | -------------------------------------- | ------------------------- |
| 基礎工具     | apt-get 依賴     | jq、curl、wget、git、unzip（系統工具） | Dockerfile                |
| K8s 工具     | kubectl          | Kubernetes 集群管理                    | Dockerfile                |
| K8s 工具     | Helm             | Kubernetes 包管理器                    | Dockerfile                |
| Python 依賴  | requirements.txt | Python 開發庫                          | Dockerfile                |
| **可選工具** | Trivy            | 容器鏡像漏洞掃描                       | install-optional-tools.sh |
| **可選工具** | Cosign           | 制品數字簽名和驗證                     | install-optional-tools.sh |
| **可選工具** | Syft             | 軟件物料清單生成                       | install-optional-tools.sh |
| **可選工具** | OPA              | Open Policy Agent 策略評估             | install-optional-tools.sh |
| **可選工具** | Conftest         | 策略配置測試                           | install-optional-tools.sh |

**優化說明：**

- 移除了 Trivy、Cosign、Syft、OPA、Conftest 的自動安裝
- 這些工具已移至 `install-optional-tools.sh` 腳本，可按需安裝
- 減少了初始化時間，避免在 93% 卡住的問題

**关键步骤：**

1. **基础镜像**（第1行）

   ```dockerfile
   FROM mcr.microsoft.com/vscode/devcontainers/typescript-node:18
   ```

   - 包含 Node.js 18、npm、git 等

2. **系统工具安装**（第4-11行）

   ```dockerfile
   apt-get install -y python3-pip jq curl wget git unzip
   ```

3. **云原生工具链**（第14-38行）
   - kubectl、Helm、Trivy、Cosign、Syft、OPA、Conftest

4. **用户配置**（第44-45行）

   ```dockerfile
   useradd -m -s /bin/bash developer
   usermod -aG docker developer
   ```

   - 创建 developer 用户，添加 docker 权限

5. **Python 依赖**（第48-49行）
   - 从 requirements.txt 安装 Python 包

6. **健康检查**（第58-59行）
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
       CMD curl -f http://localhost:3000/health || exit 1
   ```

   - 每 30 秒检查应用健康状态

**依赖关系：**

- 依赖 requirements.txt（Python 包）
- 被 devcontainer.json 引用
- 被 docker-compose.dev.yml 引用

**安全考虑：**

- 使用非 root 用户（developer）运行
- Docker group 权限受限
- 健康检查确保服务可用

---

### 3. docker-compose.dev.yml

**功能：** 本地开发环境多容器编排

**主要职责：**

- 定义完整的微服务栈（应用、数据库、缓存、监控）
- 配置服务间通信和网络
- 管理数据持久化
- 配置开发相关的调试和环境变量

**服务架构图：**

```
keystone-network (bridge)
├── keystone-platform (主应用)
│   ├── Port: 3000 (HTTP)
│   └── Port: 9229 (Node.js 调试)
├── postgres-dev (数据库)
│   ├── Port: 5432
│   └── 数据卷: postgres_data
├── redis-dev (缓存)
│   └── Port: 6379
├── prometheus-dev (指标收集)
│   └── Port: 9090
└── grafana-dev (可视化)
    └── Port: 3001
```

**服务详解：**

| 服务名            | 镜像            | 端口       | 环境变量                                       | 目的                  |
| ----------------- | --------------- | ---------- | ---------------------------------------------- | --------------------- |
| keystone-platform | 本地 Dockerfile | 3000, 9229 | NODE_ENV=development, CHOKIDAR_USEPOLLING=true | 主应用 + Node.js 调试 |
| postgres-dev      | postgres:15     | 5432       | POSTGRES_DB=keystone_platform                  | 开发数据库            |
| redis-dev         | redis:7-alpine  | 6379       | -                                              | 缓存和会话存储        |
| prometheus-dev    | prom/prometheus | 9090       | -                                              | 指标收集              |
| grafana-dev       | grafana/grafana | 3001       | GF_SECURITY_ADMIN_PASSWORD=admin               | 监控仪表板            |

**关键配置：**

1. **应用服务**

   ```yaml
   volumes:
     - ..:/workspace # 挂载项目根目录
     - /var/run/docker.sock:/... # Docker socket
   environment:
     - NODE_ENV=development
     - CHOKIDAR_USEPOLLING=true # 文件变动监听（WSL2 兼容）
   ```

2. **数据库服务**

   ```yaml
   volumes:
     - postgres_data:/var/lib/postgresql/data # 持久化数据
   ```

3. **网络配置**
   ```yaml
   networks:
     - keystone-network # 自定义桥接网络，服务可通过名称互相访问
   ```

**依赖关系：**

- 依赖 Dockerfile（keystone-platform 服务）
- 依赖 prometheus.yml（Prometheus 配置）
- 被 devcontainer.json 的 postCreateCommand 可能调用

**启动方式：**

```bash
docker-compose -f .devcontainer/docker-compose.dev.yml up -d
```

**调试支持：**

- Node.js 调试端口：9229
- Prometheus 指标：http://localhost:9090
- Grafana 仪表板：http://localhost:3001

---

### 4. requirements.txt

**功能：** Python 依赖包声明

**主要职责：**

- 声明企业级开发所需的 Python 包
- 指定包版本范围

**依赖清单：**

| 包名           | 版本     | 用途                     |
| -------------- | -------- | ------------------------ |
| requests       | >=2.28.0 | HTTP 客户端库            |
| pyyaml         | >=6.0    | YAML 文件处理            |
| kubernetes     | >=24.0   | Kubernetes Python 客户端 |
| docker         | >=6.0    | Docker Python 客户端     |
| jsonschema     | >=4.0    | JSON Schema 验证         |
| cryptography   | >=38.0   | 加密和签名操作           |
| python-dotenv  | >=0.19.0 | .env 环境变量加载        |
| pytest         | >=7.0    | 单元测试框架             |
| pytest-asyncio | >=0.18.0 | 异步测试支持             |
| black          | >=22.0   | Python 代码格式化        |
| flake8         | >=5.0    | Python 代码风格检查      |
| mypy           | >=0.982  | Python 静态类型检查      |

**分类说明：**

1. **云原生交互**（Kubernetes、Docker 管理）
   - kubernetes、docker

2. **数据处理**（配置、序列化）
   - requests、pyyaml、jsonschema

3. **安全和加密**
   - cryptography

4. **开发工具**（测试、格式化、类型检查）
   - pytest、pytest-asyncio、black、flake8、mypy

5. **配置管理**
   - python-dotenv

**依赖关系：**

- 被 Dockerfile 引用（第 48-49 行）

---

### 5. setup.sh

**功能：** 開發環境初始化腳本（入口點）- 已優化以避免卡在 93%

**主要職責：**

- 驗證開發環境工具鏈完整性
- 自動化初始化流程（輕量化版本）
- 配置環境變數和必要目錄
- 優化的 npm 安裝流程

**執行流程（5個步驟 - 已優化）：**

| 步驟 | 操作     | 說明                                                                      |
| ---- | -------- | ------------------------------------------------------------------------- |
| 1    | 工具驗證 | 快速檢查 node、npm 可用性（移除 docker/kubectl 檢查以加快速度）           |
| 2    | 目錄創建 | 創建 .vscode、scripts、tests 等目錄                                       |
| 3    | 環境變數 | 從 .env.example 複製到 .env.local（如不存在）                             |
| 4    | 依賴安裝 | 優化的 `npm ci/install` 使用 --prefer-offline --no-audit --loglevel=error |
| 5    | 完成提示 | 顯示下一步操作提示                                                        |

**關鍵優化：**

1. **移除重量級操作**
   - 不再在初始化時運行 `npm run build`
   - 不再全局安裝開發工具（@types/node, typescript 等）
   - 不再配置 Git hooks（可按需配置）

2. **優化的 npm 安裝**

   ```bash
   # 配置 npm 超時和重試
   npm config set fetch-retry-mintimeout 20000
   npm config set fetch-retry-maxtimeout 120000
   npm config set fetch-retries 3

   # 優先使用 npm ci（更快、更可靠）
   npm ci --prefer-offline --no-audit --loglevel=error
   ```

3. **錯誤容錯**
   - 如果 npm ci 失敗，自動降級到 npm install
   - 使用 --prefer-offline 優先使用本地緩存
   - --no-audit 跳過審計以節省時間

**关键代码块：**

1. **工具验证**

   ```bash
   command -v node >/dev/null 2>&1 || { echo "Node.js 未安装"; exit 1; }
   ```

2. **Git 全局配置**

   ```bash
   git config --global user.name "Keystone Platform Developer"
   git config --global user.email "developer@keystone-platform.com"
   ```

3. **预提交钩子**

   ```bash
   cat > .git/hooks/pre-commit << 'EOF'
   #!/bin/bash
   npm run lint
   npm run type-check
   EOF
   ```

4. **错误处理**
   ```bash
   set -e  # 任何命令失败即退出
   ```

**依赖关系：**

- 被 devcontainer.json 的 postCreateCommand 调用
- 可能依赖 scripts/health-check.sh（可选）
- 可能依赖 scripts/install-hooks.sh（可选）

**执行上下文：**

- 运行环境：Docker 容器内
- 运行用户：node（devcontainer.json 配置）
- 工作目录：/workspace

**错误处理：**

- `set -e` 确保任何失败的命令会导致脚本停止
- 每个工具验证步骤都有清晰的错误提示

---

### 6. prometheus.yml

**功能：** Prometheus 监控服务配置

**主要职责：**

- 定义全局监控参数
- 配置数据抓取任务
- 指定监控目标和端点

**全局配置：**

```yaml
global:
  scrape_interval: 15s # 默认抓取间隔
  evaluation_interval: 15s # 规则评估间隔
```

**抓取任务配置：**

| 任务名            | 目标              | 端口 | 指标路径 | 自定义间隔  |
| ----------------- | ----------------- | ---- | -------- | ----------- |
| keystone-platform | keystone-platform | 3000 | /metrics | 10s         |
| prometheus        | localhost         | 9090 | /metrics | 15s（默认） |
| node-exporter     | node-exporter     | 9100 | /metrics | 15s（默认） |

**关键配置详解：**

1. **主应用监控**

   ```yaml
   - job_name: 'keystone-platform'
     static_configs:
       - targets: ['keystone-platform:3000']
     metrics_path: /metrics
     scrape_interval: 10s
   ```

   - 更快的抓取间隔（10s）用于应用监控

2. **Prometheus 自身**

   ```yaml
   - job_name: 'prometheus'
     static_configs:
       - targets: ['localhost:9090']
   ```

   - 监控 Prometheus 自身

3. **Node Exporter**
   ```yaml
   - job_name: 'node-exporter'
     static_configs:
       - targets: ['node-exporter:9100']
   ```

   - 收集主机级别的系统指标

**规则文件占位符：**

```yaml
rule_files:
  # - "first_rules.yml"      # 告警规则文件（待配置）
  # - "second_rules.yml"     # 告警规则文件（待配置）
```

**依赖关系：**

- 被 docker-compose.dev.yml 的 prometheus-dev 服务引用
- 需要应用 /metrics 端点可用

**监控指标用途：**

- 性能监控（响应时间、吞吐量）
- 资源使用（CPU、内存）
- 业务指标（用户数、请求数）

---

### 7. install-optional-tools.sh

**功能：** 可選安全和治理工具安裝腳本

**主要職責：**

- 安裝非必需的開發工具（按需安裝）
- 避免初始化時安裝過多工具導致超時
- 提供靈活的工具鏈配置

**可安裝的工具：**

| 工具     | 用途             | 安裝時間 |
| -------- | ---------------- | -------- |
| Trivy    | 容器鏡像漏洞掃描 | ~30秒    |
| Cosign   | 容器簽名和驗證   | ~10秒    |
| Syft     | SBOM 生成工具    | ~20秒    |
| OPA      | 策略引擎         | ~15秒    |
| Conftest | 策略測試工具     | ~10秒    |

**使用方法：**

```bash
# 在 codespace 或容器內執行
bash .devcontainer/install-optional-tools.sh
```

**設計理念：**

- 分離核心工具和可選工具
- 讓用戶根據實際需求安裝
- 加快初始 codespace 創建速度
- 避免在 93% 處卡住的問題

---

## 关键配置说明

### 开发环境初始化流程

```
1. VS Code 启动远程容器
   ↓
2. devcontainer.json 定义容器规格
   ↓
3. Dockerfile 构建镜像
   ↓
4. docker-compose.dev.yml 启动服务栈
   ↓
5. setup.sh 执行初始化（postCreateCommand）
   ↓
6. npm run dev 启动应用（postStartCommand）
```

### 网络和通信

- **容器间通信**：通过 `keystone-network` 桥接网络，服务可通过名称访问
  - 应用可通过 `postgres-dev:5432` 连接数据库
  - 应用可通过 `redis-dev:6379` 连接缓存
- **本地宿主机访问**：通过端口转发
  - http://localhost:3000 → 应用
  - http://localhost:5432 → 数据库
  - http://localhost:9090 → Prometheus
  - http://localhost:3001 → Grafana

### 工具链层次结构

```
Level 1: 系统基础
  └─ Node.js 18 基础镜像 (msft devcontainer)

Level 2: 系统工具
  └─ jq, curl, wget, git, unzip, python3-pip

Level 3: 云原生工具
  ├─ kubectl + Helm（Kubernetes 管理）
  └─ Trivy, Cosign, Syft, OPA, Conftest（安全和策略）

Level 4: 应用依赖
  ├─ Node.js: npm 包（TypeScript、框架等）
  └─ Python: requirements.txt 包

Level 5: 开发服务
  ├─ PostgreSQL（数据库）
  ├─ Redis（缓存）
  ├─ Prometheus（监控）
  └─ Grafana（可视化）
```

### 文件系统和卷挂载

```
主机宿主机文件系统
├── /home/user/ArchitectSparkPrototypeDev/ (项目目录)
│   └── 挂载到容器 /workspace
│       └── 所有源代码和配置同步
└── /var/run/docker.sock
    └── 挂载到容器允许访问 Docker daemon

容器内持久化存储
└── postgres_data (Docker Volume)
    └── PostgreSQL 数据持久化
```

### 调试支持

1. **Node.js 调试**
   - 端口：9229
   - 在 VS Code 中可配置 launch.json 连接
   - Docker Compose 暴露了此端口

2. **日志查看**

   ```bash
   docker-compose -f .devcontainer/docker-compose.dev.yml logs -f keystone-platform
   ```

3. **交互式调试**
   ```bash
   docker-compose -f .devcontainer/docker-compose.dev.yml exec keystone-platform bash
   ```

---

## 使用指南

### 快速启动

```bash
# 方式1：在 VS Code 中使用 Remote Container 扩展
# 1. 打开项目
# 2. 点击左下角 "Open in Container"
# 3. VS Code 自动初始化

# 方式2：使用 Docker Compose 直接启动
cd .devcontainer
docker-compose -f docker-compose.dev.yml up -d
```

### 常用命令

```bash
# 查看所有运行的容器
docker-compose -f .devcontainer/docker-compose.dev.yml ps

# 查看应用日志
docker-compose -f .devcontainer/docker-compose.dev.yml logs -f keystone-platform

# 连接到应用容器
docker-compose -f .devcontainer/docker-compose.dev.yml exec keystone-platform bash

# 停止所有服务
docker-compose -f .devcontainer/docker-compose.dev.yml down

# 完整清理（包括数据卷）
docker-compose -f .devcontainer/docker-compose.dev.yml down -v
```

### 访问服务

| 服务       | 访问地址              |
| ---------- | --------------------- |
| 应用       | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| Grafana    | http://localhost:3001 |
| PostgreSQL | localhost:5432        |
| Redis      | localhost:6379        |

---

## 环境变量和秘密管理

### 开发环境变量

设置位置：.env.local（由 setup.sh 创建）

```bash
NODE_ENV=development
# 数据库配置
DATABASE_URL=postgresql://developer:development@postgres-dev:5432/keystone_platform
REDIS_URL=redis://redis-dev:6379
# API 和服务端点
PROMETHEUS_URL=http://prometheus-dev:9090
```

### 敏感信息处理

- **本地开发**：使用 .env.local（git 忽略）
- **容器内**：通过 docker-compose.dev.yml 的 environment 传递
- **生产环境**：应该通过 Kubernetes Secrets 或密钥管理服务

---

## 故障排除

### 常见问题

| 问题                   | 原因                       | 解决方案                                                  |
| ---------------------- | -------------------------- | --------------------------------------------------------- |
| Docker socket 权限错误 | developer 用户 docker 权限 | 检查 Dockerfile 中 `usermod -aG docker developer`         |
| 无法连接数据库         | 容器网络隔离               | 确保在 keystone-network 中，使用 postgres-dev 作为主机名  |
| 文件变化不被检测       | WSL2 文件系统兼容性        | CHOKIDAR_USEPOLLING=true 已在 docker-compose.dev.yml 配置 |
| 端口冲突               | 本地已有服务占用           | 修改 docker-compose.dev.yml 中的端口映射                  |

### 日志和调试

```bash
# 查看 Dockerfile 构建日志
docker-compose -f .devcontainer/docker-compose.dev.yml build --no-cache

# 查看 setup.sh 执行日志
docker-compose -f .devcontainer/docker-compose.dev.yml logs keystone-platform | grep -i error

# 验证容器网络连接
docker network inspect devcontainer_keystone-network
```

---

## 安全考虑

### 已实施的安全措施

1. **非 root 用户**：developer 用户运行容器，减少特权
2. **最小权限**：docker group 权限受限
3. **网络隔离**：自定义桥接网络，服务只通过网络访问
4. **工具链**：包含安全扫描工具（Trivy、Cosign、Syft、OPA）
5. **健康检查**：Dockerfile 包含健康检查确保应用可用
6. **版本固定**：requirements.txt 指定最低版本确保兼容性

### 环境特定的安全

- **开发**：使用简单密码（POSTGRES_PASSWORD=development）
- **生产**：必须使用强密码和密钥管理服务

---

## 维护和更新

### 更新工具链

```bash
# 更新 Node 基础镜像版本（devcontainer.json）
# 修改 image: 版本号

# 更新 Python 依赖
pip install --upgrade -r requirements.txt

# 更新 npm 依赖
npm update
```

### 版本管理

- Node.js：18 LTS（在 devcontainer.json 中固定）
- Python：3.x（在 Dockerfile 中使用 python:1 feature）
- PostgreSQL：15（在 docker-compose.dev.yml 中固定）
- Redis：7-alpine（在 docker-compose.dev.yml 中固定）

---

## 扩展和定制

### 添加新的开发工具

1. **添加系统工具**：修改 Dockerfile apt-get 命令
2. **添加 Python 包**：添加到 requirements.txt
3. **添加 npm 包**：运行 `npm install <package>`
4. **添加新服务**：在 docker-compose.dev.yml 添加新 service

### 添加新的开发端口

1. 在 docker-compose.dev.yml 中添加端口映射
2. 在 devcontainer.json 中添加到 forwardPorts 数组
3. 在 portsAttributes 中配置端口行为

---

## 相关文档和资源

- **VSCode Remote 容器官方文档**：https://code.visualstudio.com/docs/devcontainers/containers
- **Docker Compose 文档**：https://docs.docker.com/compose/
- **Prometheus 文档**：https://prometheus.io/docs/
- **Kubernetes 部署**：见 /ARCHITECTURE.md

---

## 更新历史

| 日期       | 版本 | 改动     |
| ---------- | ---- | -------- |
| 2025-11-01 | 1.0  | 初始创建 |

---

_本知识库文档提供详细的 .devcontainer 配置说明、工具链说明和使用指南。如有更新，请同步修改此文档。_
