# 命名空間基礎概念介紹

## Introduction to Namespaces

命名空間（Namespace）是一種在系統中組織和隔離資源的機制，廣泛應用於作業系統、容器化技術和程式設計領域。

## 什麼是命名空間？

命名空間是一種邏輯隔離機制，它允許：

- **資源隔離**：不同命名空間中的資源互不干擾
- **名稱重用**：相同名稱可以在不同命名空間中使用
- **存取控制**：基於命名空間實施細粒度的權限管理

## 命名空間的重要性

### 1. 資源組織

命名空間提供了一種清晰的方式來組織和分類資源：

```yaml
# 範例：按環境分類
namespaces:
  - development
  - staging
  - production
```

### 2. 安全隔離

通過命名空間實現安全邊界：

```yaml
# 範例：按團隊隔離
namespaces:
  - team-frontend
  - team-backend
  - team-data
```

### 3. 資源配額管理

每個命名空間可以設定獨立的資源限制：

```yaml
# 範例：資源配額
resourceQuota:
  namespace: production
  limits:
    cpu: "10"
    memory: "20Gi"
```

## 命名空間的類型

### 作業系統級別

Linux 核心提供多種命名空間類型：

| 命名空間類型 | 功能說明 |
|-------------|---------|
| PID | 進程 ID 隔離 |
| Network | 網路隔離 |
| Mount | 檔案系統隔離 |
| UTS | 主機名稱隔離 |
| IPC | 進程間通訊隔離 |
| User | 用戶 ID 隔離 |
| Cgroup | 控制群組隔離 |

### 容器編排級別

Kubernetes 命名空間用於：

- 多租戶隔離
- 環境分離（dev/staging/prod）
- 團隊資源隔離
- 資源配額管理

## 學習路線圖

1. **基礎概念** → 本章節
2. **核心特性** → [core_features.md](./core_features.md)
3. **技術棧應用** → [technology_stacks.md](./technology_stacks.md)
4. **設計原則** → [design_principles.md](./design_principles.md)
5. **實際案例** → [use_cases.md](./use_cases.md)
6. **故障排除** → [troubleshooting.md](./troubleshooting.md)

## 相關資源

- [Kubernetes 官方文檔 - Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
- [Docker 官方文檔 - Namespaces](https://docs.docker.com/engine/security/namespaces/)
- [Linux Manual - namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html)

---

**下一章節**: [命名空間的核心特性](./core_features.md)
