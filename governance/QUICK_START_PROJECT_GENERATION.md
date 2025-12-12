# 🚀 Project Factory 快速開始指南

# Quick Start Guide: Project Generation

> **10 分鐘內生成完整專案** | **Generate Complete Project in 10 Minutes**

---

## 📋 目標 Goal

使用 **SynergyMesh Project Factory**，一鍵生成包含以下所有內容的生產級專案：

✅ 完整源代碼 (Python/TypeScript/Go)  
✅ 測試套件 (Unit + Integration + E2E)  
✅ Docker 配置 (Multi-stage Dockerfile + docker-compose)  
✅ Kubernetes 清單 (Deployment + Service + Ingress + HPA)  
✅ CI/CD Pipeline (GitHub Actions / GitLab CI)  
✅ 治理文檔 (Architecture + API + Compliance)  
✅ 安全報告 (SBOM + Vulnerability Scan)

**所有內容自動通過 5 層治理驗證，即刻可部署！**

---

## 🎯 三種生成方式

### 方法 1: 使用範例 YAML（推薦新手）

```bash
# 1. 使用預設範例規格
python -m core.project_factory.cli generate project \
  --spec examples/project-factory-demo.yaml \
  --output ./my-first-project

# 2. 等待 3-5 秒

# 3. 完成！
# ✅ Generated 29 files
# ✅ Governance validation: PASSED (5/5)
# ✅ Project ready at: ./my-first-project
```

**輸出結果預覽**:

```
my-first-project/
├── src/demo_payment_service/
│   ├── main.py (FastAPI app)
│   ├── api/routes.py (REST endpoints)
│   ├── application/services.py (Business logic)
│   ├── domain/models.py (Domain models)
│   └── infrastructure/database.py (DB config)
├── tests/ (Unit + Integration + E2E)
├── kubernetes/ (All K8s manifests)
├── Dockerfile (Multi-stage)
├── .github/workflows/ci-cd.yml
├── README.md (Comprehensive)
└── governance/ (SBOM + Reports)
```

---

### 方法 2: CLI 快速命令（最快速）

```bash
# 生成簡單的 Python FastAPI 微服務
python -m core.project_factory.cli generate project \
  --type microservice \
  --name my-service \
  --language python \
  --framework fastapi \
  --database postgresql \
  --cache redis \
  --docker \
  --kubernetes \
  --cicd-platform github-actions \
  --output ./projects/my-service

# 一行搞定！
```

**完整參數說明**:

```bash
python -m core.project_factory.cli generate project \
  --type microservice              # 專案類型: microservice, frontend, ai-agent
  --name user-service              # 專案名稱
  --language python                # 語言: python, typescript, go, rust
  --framework fastapi              # 框架: fastapi, nestjs, gin, actix
  --database postgresql            # 資料庫: postgresql, mysql, mongodb
  --orm sqlalchemy                 # ORM: sqlalchemy, typeorm, gorm
  --migrations alembic             # 遷移工具: alembic, flyway
  --cache redis                    # 快取: redis, memcached
  --messaging kafka                # 訊息佇列: kafka, rabbitmq, nats
  --messaging-topics "user.created,user.updated"  # Kafka topics
  --docker                         # 啟用 Docker
  --kubernetes                     # 啟用 Kubernetes
  --cicd-platform github-actions   # CI/CD: github-actions, gitlab-ci, drone
  --compliance "ISO-42001,NIST-AI-RMF"  # 合規標準
  --security-level high            # 安全等級: low, medium, high
  --tests-unit                     # 生成單元測試
  --tests-integration              # 生成集成測試
  --tests-e2e                      # 生成 E2E 測試
  --coverage-threshold 80          # 測試覆蓋率閾值
  --license MIT                    # 授權協議
  --output ./projects/user-service # 輸出路徑
```

---

### 方法 3: Python API（用於自動化）

```python
from pathlib import Path
from core.project_factory import ProjectFactory, ProjectSpec
from core.project_factory.spec import ProjectType, Language

# 1. 創建規格
spec = ProjectSpec(
    name="my-awesome-service",
    type=ProjectType.MICROSERVICE,
    language=Language.PYTHON,
    framework="fastapi"
)

# 2. 配置功能（可選）
spec.features.database.type = "postgresql"
spec.features.cache.type = "redis"
spec.deliverables.docker.multi_stage = True
spec.deliverables.kubernetes.deployment = True
spec.governance.compliance = ["ISO-42001", "NIST-AI-RMF"]

# 3. 生成專案
factory = ProjectFactory()
project = factory.generate(spec)

# 4. 驗證治理
validation = project.validate_governance()
print(f"✅ Compliance: {validation['overall_status']}")

# 5. 導出專案
project.export(Path("./my-awesome-service"))
```

---

## 📖 範例：生成高安全性支付微服務

### Step 1: 準備 YAML 規格

創建 `payment-service-spec.yaml`:

```yaml
apiVersion: factory.synergymesh.io/v1
kind: ProjectSpec
metadata:
  name: payment-gateway
  description: '高安全性支付網關微服務'
  version: '1.0.0'

spec:
  type: microservice
  language: python
  framework: fastapi

  features:
    database:
      type: postgresql
    cache:
      type: redis
    messaging:
      type: kafka
      topics:
        - payment.initiated
        - payment.completed

  deliverables:
    tests:
      unit: true
      integration: true
      coverage_threshold: 85
    docker:
      multi_stage: true
    kubernetes:
      deployment: true
      hpa: true
    ci_cd:
      platform: github-actions

  governance:
    compliance:
      - ISO-42001
      - PCI-DSS
    security_level: high
    sbom: true
```

### Step 2: 生成專案

```bash
python -m core.project_factory.cli generate project \
  --spec payment-service-spec.yaml \
  --output ./payment-gateway
```

### Step 3: 驗證結果

```bash
cd payment-gateway

# 查看生成的檔案
tree -L 2

# 驗證治理標準
cat .project-factory-metadata.json

# 查看驗證報告
cat governance/validation-report.json
```

### Step 4: 立即運行

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行測試
pytest tests/ --cov

# 啟動服務
uvicorn src.payment_gateway.main:app --reload

# 查看 API 文檔
# 瀏覽器訪問: http://localhost:8000/docs
```

### Step 5: 部署到 Kubernetes

```bash
# 構建 Docker 映像
docker build -t payment-gateway:latest .

# 部署到 K8s
kubectl apply -f kubernetes/

# 查看部署狀態
kubectl get pods -l app=payment-gateway
```

---

## 🎨 生成不同類型的專案

### 1. Python FastAPI 微服務

```bash
python -m core.project_factory.cli generate project \
  --type microservice \
  --name user-service \
  --language python \
  --framework fastapi \
  --database postgresql \
  --docker --kubernetes \
  --output ./user-service
```

### 2. TypeScript NestJS 微服務

```bash
python -m core.project_factory.cli generate project \
  --type microservice \
  --name product-service \
  --language typescript \
  --framework nestjs \
  --database mongodb \
  --docker --kubernetes \
  --output ./product-service
```

### 3. Go Gin 微服務

```bash
python -m core.project_factory.cli generate project \
  --type microservice \
  --name inventory-service \
  --language go \
  --framework gin \
  --database postgresql \
  --docker --kubernetes \
  --output ./inventory-service
```

### 4. React + TypeScript 前端

```bash
python -m core.project_factory.cli generate project \
  --type frontend \
  --name admin-dashboard \
  --language typescript \
  --framework react \
  --docker --kubernetes \
  --output ./admin-dashboard
```

### 5. AI Agent 專案

```bash
python -m core.project_factory.cli generate project \
  --type ai-agent \
  --name code-reviewer \
  --language python \
  --framework openai \
  --docker --kubernetes \
  --output ./code-reviewer
```

---

## 🔍 驗證生成的專案

### 自動驗證報告

```bash
# 查看驗證報告
cat ./my-service/.project-factory-metadata.json
```

**報告範例**:

```json
{
  "project": "my-service",
  "generation": {
    "timestamp": "2025-12-12T16:00:00Z",
    "factory_version": "1.0.0",
    "duration_seconds": 3.2
  },
  "validation": {
    "overall_status": "PASSED",
    "checks_passed": 5,
    "checks_failed": 0
  },
  "deliverables": {
    "files_generated": 29,
    "lines_of_code": 1247,
    "test_coverage": 85
  }
}
```

### 手動驗證步驟

```bash
# 1. 檢查代碼風格
pylint src/

# 2. 運行測試
pytest tests/ --cov --cov-report=html

# 3. 安全掃描
bandit -r src/
safety check

# 4. Docker 構建測試
docker build -t my-service:test .

# 5. K8s 配置驗證
kubectl apply --dry-run=client -f kubernetes/
```

---

## 💡 常見問題 FAQ

### Q1: 生成的專案可以直接部署嗎？

✅ **是的！**
所有生成的專案都經過完整驗證，包含所有必要配置，可以直接部署到 Kubernetes。

### Q2: 如何自定義生成的代碼？

📝 有三種方式：

1. 修改 YAML 規格文件中的參數
2. 使用 Python API 自定義 ProjectSpec
3. 創建自定義模板（高級用法）

### Q3: 支援哪些語言和框架？

🔧 目前支援：

- **Python**: FastAPI, Flask, Django
- **TypeScript**: NestJS, Express
- **Go**: Gin, Echo
- **Rust**: Actix (規劃中)

### Q4: 生成的測試覆蓋率如何？

✅ 預設生成的測試覆蓋率 ≥ 80%，可通過 `--coverage-threshold` 參數調整。

### Q5: 如何符合特定的合規標準？

📋 使用 `--compliance` 參數指定：

```bash
--compliance "ISO-42001,NIST-AI-RMF,PCI-DSS,GDPR"
```

### Q6: 生成速度有多快？

⚡ 生成時間：

- 簡單專案: < 2 秒
- 標準專案: < 3 秒
- 完整專案: < 5 秒

### Q7: 如何更新已生成的專案？

🔄 有兩種方式：

1. 重新生成並手動合併變更
2. 使用專案演化功能（規劃中）

### Q8: 是否支援多專案生態系統生成？

🏗️ 規劃中！未來將支援一次生成整個微服務生態系統。

---

## 🎓 進階主題

### 自定義 YAML 規格模板

創建可重用的規格模板：

```yaml
# templates/microservice-base.yaml
apiVersion: factory.synergymesh.io/v1
kind: ProjectSpec
metadata:
  name: '{{PROJECT_NAME}}'
  description: '{{PROJECT_DESCRIPTION}}'

spec:
  type: microservice
  language: python
  framework: fastapi

  # 標準配置
  deliverables:
    tests:
      unit: true
      integration: true
      coverage_threshold: 80
    docker:
      multi_stage: true
    kubernetes:
      deployment: true

  # 標準治理
  governance:
    compliance:
      - ISO-42001
      - NIST-AI-RMF
    security_level: medium
```

使用模板：

```bash
# 替換變數並生成
sed 's/{{PROJECT_NAME}}/my-service/g' templates/microservice-base.yaml | \
sed 's/{{PROJECT_DESCRIPTION}}/My awesome service/g' | \
python -m core.project_factory.cli generate project --spec -
```

### 批量生成專案

```python
from core.project_factory import ProjectFactory
from core.project_factory.spec import ProjectSpec, ProjectType, Language

factory = ProjectFactory()

# 定義多個微服務
services = [
    {"name": "user-service", "database": "postgresql"},
    {"name": "product-service", "database": "mongodb"},
    {"name": "order-service", "database": "postgresql"},
]

# 批量生成
for service_spec in services:
    spec = ProjectSpec(
        name=service_spec["name"],
        type=ProjectType.MICROSERVICE,
        language=Language.PYTHON,
        framework="fastapi"
    )
    spec.features.database.type = service_spec["database"]

    project = factory.generate(spec)
    project.export(f"./microservices/{service_spec['name']}")
    print(f"✅ Generated: {service_spec['name']}")
```

### 整合到 CI/CD

在 GitHub Actions 中自動生成專案：

```yaml
# .github/workflows/generate-service.yml
name: Generate Microservice

on:
  workflow_dispatch:
    inputs:
      service_name:
        description: 'Service name'
        required: true
      spec_file:
        description: 'Spec file path'
        required: true

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Generate project
        run: |
          python -m core.project_factory.cli generate project \
            --spec ${{ github.event.inputs.spec_file }} \
            --output ./generated/${{ github.event.inputs.service_name }}

      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message:
            'feat: Generate ${{ github.event.inputs.service_name }}'
          branch: 'generate/${{ github.event.inputs.service_name }}'
          title: 'New Service: ${{ github.event.inputs.service_name }}'
```

---

## 📚 下一步

1. ✅ **探索範例**: 查看 `examples/project-factory-demo.yaml`
2. ✅ **閱讀完整文檔**:
   [Project Factory README](../core/project_factory/README.md)
3. ✅ **了解治理整合**:
   [Governance Integration Guide](./PROJECT_FACTORY_INTEGRATION.md)
4. ✅ **學習模板系統**:
   [Template Customization](../core/project_factory/templates/README.md)
5. ✅ **查看插件開發**:
   [Plugin Development Guide](../core/project_factory/plugins/README.md)

---

## 🆘 獲取幫助

### 文檔資源

- [Project Factory README](../core/project_factory/README.md)
- [Governance Deep Analysis](./DEEP_ANALYSIS_GOVERNANCE_STRUCTURE.md)
- [Project Factory Integration](./PROJECT_FACTORY_INTEGRATION.md)

### 社群支援

- GitHub Issues:
  [提交問題](https://github.com/SynergyMesh-master/SynergyMesh/issues)
- Slack Channel: #project-factory
- Email: <platform@synergymesh.io>

---

**開始生成你的第一個專案吧！** 🚀

```bash
python -m core.project_factory.cli generate project \
  --spec examples/project-factory-demo.yaml \
  --output ./my-first-project
```

---

**文檔版本**: 1.0.0  
**最後更新**: 2025-12-12  
**作者**: SynergyMesh Platform Team
