# 從零開始架構命名空間教學

## Namespace Architecture Tutorial from Scratch

歡迎來到命名空間架構教學！本教學將帶領您從基礎概念到進階應用，全面了解命名空間在現代雲原生架構中的重要性和實踐方法。

Welcome to the Namespace Architecture Tutorial! This tutorial will guide you from basic concepts to advanced applications, providing a comprehensive understanding of namespaces in modern cloud-native architecture.

## 📚 目錄結構

```
NamespaceTutorial/
├── docs/                              # 學習手冊
│   ├── introduction.md                # 命名空間基礎概念介紹
│   ├── core_features.md               # 命名空間的核心特性
│   ├── technology_stacks.md           # 命名空間在不同技術棧中的體現
│   ├── design_principles.md           # 命名空間設計原則
│   ├── use_cases.md                   # 實際應用場景與案例研究
│   └── troubleshooting.md             # 故障排除與診斷
├── examples/                          # 範例配置
│   ├── kubernetes_namespaces.yaml     # Kubernetes 命名空間範例
│   ├── docker_namespaces.yaml         # Docker 命名空間範例
│   └── rbac_roles.yaml                # RBAC 設定範例
├── scripts/                           # 輔助腳本
│   ├── cleanup_namespaces.sh          # 自動化命名空間清理腳本
│   └── monitor_resources.sh           # 監控資源使用的腳本
├── tests/                             # 測試檔案
│   ├── test_namespace_creation.py     # 命名空間創建測試
│   ├── test_network_policy.py         # 網路策略測試
│   └── test_resource_quota.py         # 資源配額測試
├── README.md                          # 本文件
└── .gitignore                         # Git 忽略檔案
```

## 🎯 學習目標

完成本教學後，您將能夠：

1. **理解命名空間的基本概念**
   - 命名空間的定義和用途
   - 不同類型命名空間的區別
   - 命名空間在雲原生架構中的角色

2. **掌握 Kubernetes 命名空間管理**
   - 創建和管理命名空間
   - 配置資源配額和限制範圍
   - 實施網路策略

3. **應用 RBAC 存取控制**
   - 設計角色和角色綁定
   - 實現最小權限原則
   - 跨命名空間權限管理

4. **處理常見問題**
   - 診斷命名空間相關問題
   - 解決資源配額超限
   - 修復網路連通性問題

## 🚀 快速開始

### 前置需求

- Kubernetes 叢集 (minikube, kind, 或雲端叢集)
- kubectl 命令列工具
- Python 3.8+ (用於測試)
- Docker (可選)

### 安裝步驟

```bash
# 1. 克隆專案
git clone <repository-url>
cd NamespaceTutorial

# 2. 驗證 kubectl 連接
kubectl cluster-info

# 3. 創建測試命名空間
kubectl apply -f examples/kubernetes_namespaces.yaml

# 4. 安裝 Python 測試依賴
pip install pytest

# 5. 運行測試
pytest tests/ -v
```

### 使用腳本

```bash
# 賦予腳本執行權限
chmod +x scripts/*.sh

# 監控命名空間資源
./scripts/monitor_resources.sh production

# 清理測試命名空間（預覽模式）
./scripts/cleanup_namespaces.sh -d -l "env=test"
```

## 📖 學習路線

### 第一階段：基礎概念

1. 閱讀 [命名空間基礎概念介紹](docs/introduction.md)
2. 了解 [命名空間的核心特性](docs/core_features.md)

### 第二階段：技術實踐

3. 學習 [命名空間在不同技術棧中的體現](docs/technology_stacks.md)
4. 應用 [Kubernetes 命名空間範例](examples/kubernetes_namespaces.yaml)
5. 配置 [RBAC 角色和權限](examples/rbac_roles.yaml)

### 第三階段：設計與優化

6. 掌握 [命名空間設計原則](docs/design_principles.md)
7. 研究 [實際應用場景與案例](docs/use_cases.md)

### 第四階段：運維管理

8. 學習 [故障排除與診斷](docs/troubleshooting.md)
9. 使用監控和清理腳本

## 🧪 運行測試

```bash
# 運行所有測試
pytest tests/ -v

# 運行特定測試文件
pytest tests/test_namespace_creation.py -v

# 運行帶標記的測試
pytest tests/ -v -m "not slow"

# 生成測試報告
pytest tests/ --html=report.html
```

## 📋 範例用法

### 創建命名空間

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-app-production
  labels:
    environment: production
    team: backend
```

### 配置資源配額

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: my-app-production
spec:
  hard:
    pods: "50"
    requests.cpu: "20"
    requests.memory: "40Gi"
```

### 設定網路策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: my-app-production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

## 🔧 常用命令

| 命令 | 說明 |
|-----|------|
| `kubectl get namespaces` | 列出所有命名空間 |
| `kubectl create namespace <name>` | 創建命名空間 |
| `kubectl delete namespace <name>` | 刪除命名空間 |
| `kubectl describe namespace <name>` | 查看命名空間詳情 |
| `kubectl get resourcequota -n <namespace>` | 查看資源配額 |
| `kubectl get networkpolicy -n <namespace>` | 查看網路策略 |

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 此專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本教學內容採用 MIT 授權條款。詳見 [LICENSE](../LICENSE) 文件。

## 📞 聯繫方式

如有問題或建議，請：

- 開啟 GitHub Issue
- 發送郵件至專案維護者

## 🙏 致謝

感謝所有貢獻者和 Kubernetes 社群的支持！

---

**開始您的命名空間學習之旅吧！** 🚀
