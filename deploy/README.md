# Deploy

MachineNativeOps 部署配置目錄，提供多種部署方式的配置骨架。

## 目錄結構

```
deploy/
├── ansible/        # Ansible 自動化部署
│   ├── playbooks/  # 部署劇本
│   └── roles/      # 可重用角色
├── docker/         # Docker 容器化部署
│   ├── compose-files/  # Compose 配置
│   └── dockerfiles/    # 映像檔定義
├── kubernetes/     # Kubernetes 編排
│   ├── helm-charts/    # Helm 圖表
│   └── manifests/      # 原生清單
└── terraform/      # 基礎設施即代碼
    ├── environments/   # 環境配置
    └── modules/        # 可重用模組
```

## 目前狀態

此目錄為**骨架結構**，各子目錄已建立但尚未填入實際配置文件。

## 支援的部署方式

| 方式 | 工具 | 適用場景 |
|------|------|----------|
| 容器化 | Docker / Compose | 開發環境、單機部署 |
| 編排 | Kubernetes / Helm | 生產環境、多節點叢集 |
| 自動化 | Ansible | 伺服器配置、應用部署 |
| IaC | Terraform | 雲端基礎設施佈建 |

## 快速開始

### Docker Compose（開發環境）

```bash
# 待配置完成後使用
docker-compose -f deploy/docker/compose-files/dev.yml up -d
```

### Kubernetes（生產環境）

```bash
# 待配置完成後使用
kubectl apply -f deploy/kubernetes/manifests/
# 或使用 Helm
helm install machinenativeops deploy/kubernetes/helm-charts/
```

## 相關資源

- [DIRECTORY.md](./DIRECTORY.md) - 詳細目錄說明
- [config/](../config/) - 環境配置
- [ops/](../ops/) - 運維與監控
- [docs/deployment/](../docs/deployment/) - 部署文檔
