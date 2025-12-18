# 從零開始架構命名空間教學 | Namespace From-Scratch Guide

## 目的
- 提供治理一致的命名空間設計教學，對齊 canonical 命名規範與 URN/labels。
- 配合 `governance/34-config/naming/canonical-naming-machine-spec.yaml` 與 `governance/34-config/naming/namespace-mapping.yaml` 做落地。

## 命名空間基礎概念

### 什麼是命名空間？
命名空間提供邏輯隔離，讓同名資源可在不同作用域並存。

### 核心特性
- **隔離性**：跨命名空間互不干擾。
- **作用域**：名稱在命名空間內唯一，可跨命名空間重複。
- **資源配額**：可為命名空間設定資源上限。
- **存取控制**：細粒度 RBAC/政策綁定。

### 技術棧體現
- Kubernetes：資源組織與多租戶隔離。
- Docker：PID/網路/檔案系統等 Linux namespaces。
- 語言層：C++/Python/C# 等程式碼命名空間避免衝突。
- 雲端：AWS/Azure/GCP 提供資源組織命名空間。

### 層次結構示意
```
公司
├── 部門
│   ├── 專案
│   │   ├── 環境
│   │   │   └── 服務
│   │   └── 測試環境
│   └── 另一個專案
└── 另一個部門
```

## 為什麼需要命名空間？
- **避免命名衝突**：環境/租戶隔離後可重用簡潔名稱。
- **支援多租戶**：每租戶獨立命名空間與治理政策。

## 範例
```yaml
# 同名服務分別部署於 dev / prod
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: development
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: production
```

## 與 SynergyMesh 治理對齊
- **Canonical regex / labels**：參見 `governance/34-config/naming/canonical-naming-machine-spec.yaml`。
- **舊→新映射**：參見 `governance/34-config/naming/namespace-mapping.yaml`（含 unmanned-island-system、axiom-system/axiom、island-ai、uav/ad production 等）。
- **政策驗證**：`governance/23-policies/conftest/naming_policy.rego` 會使用 machine-spec regex 並強制環境標籤對齊。

## 推薦放置與使用
- 教學文件：本檔 `governance/29-docs/namespace-from-zero.md`。
- 模板/實例：可結合 `templates/yaml-patterns/` 或基於 machine-spec 生成具體 namespace/label 範本。***
