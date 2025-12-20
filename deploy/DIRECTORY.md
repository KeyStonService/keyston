# deploy

## 目錄職責

此目錄為 MachineNativeOps 的**部署配置中心**，包含多種部署工具的配置骨架，支援 Docker、Kubernetes、Ansible、Terraform 等部署方式。

> **目前狀態**：骨架結構已建立，子目錄內容待填充。

## 子目錄說明

| 子目錄 | 用途 | 目前狀態 |
|--------|------|----------|
| `ansible/` | Ansible playbooks 與 roles | 骨架（空） |
| `docker/` | Dockerfile 與 Compose 配置 | 骨架（空） |
| `kubernetes/` | K8s manifests 與 Helm charts | 骨架（空） |
| `terraform/` | IaC 模組與環境配置 | 骨架（空） |

## 目錄結構

```
deploy/
├── ansible/
│   ├── playbooks/    # Ansible playbooks
│   └── roles/        # 可重用的 Ansible roles
├── docker/
│   ├── compose-files/ # Docker Compose 配置
│   └── dockerfiles/   # 各服務的 Dockerfile
├── kubernetes/
│   ├── helm-charts/   # Helm Chart 定義
│   └── manifests/     # 原生 K8s YAML
└── terraform/
    ├── environments/  # 環境特定配置（dev/staging/prod）
    └── modules/       # 可重用的 Terraform 模組
```

## 與其他目錄的關係

- **config/**：環境變數與應用配置來源
- **ops/**：部署後的運維與監控
- **scripts/deployment/**：部署相關的自動化腳本
- **archive/infrastructure/**：舊版部署配置（已歸檔）

## 使用建議

1. 新增部署配置前，先確認 `config/` 中是否已有對應的環境配置
2. Docker Compose 配置應支援 dev/staging/prod 三種環境
3. Kubernetes 配置應使用 Kustomize 或 Helm 管理環境差異
4. Terraform 模組應設計為可重用，環境差異透過 variables 處理
