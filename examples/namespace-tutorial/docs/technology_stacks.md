# 命名空間在不同技術棧中的體現

## Namespaces Across Technology Stacks

本章節探討命名空間在 Kubernetes、Docker、Linux 和其他技術棧中的實現和應用。

## 1. Kubernetes 命名空間

### 1.1 概述

Kubernetes 命名空間是虛擬叢集的概念，用於在單一物理叢集中創建多個邏輯叢集。

### 1.2 預設命名空間

Kubernetes 預設提供以下命名空間：

| 命名空間 | 用途 |
|---------|------|
| `default` | 未指定命名空間時的預設位置 |
| `kube-system` | Kubernetes 系統元件 |
| `kube-public` | 公開可讀的資源 |
| `kube-node-lease` | 節點心跳租約 |

### 1.3 常用操作

```bash
# 列出所有命名空間
kubectl get namespaces

# 創建命名空間
kubectl create namespace my-namespace

# 在特定命名空間執行命令
kubectl get pods -n my-namespace

# 設定預設命名空間
kubectl config set-context --current --namespace=my-namespace

# 查看命名空間詳細資訊
kubectl describe namespace my-namespace
```

### 1.4 命名空間範例

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: production
    team: platform
  annotations:
    description: "Production environment namespace"
spec:
  finalizers:
    - kubernetes
```

## 2. Docker 命名空間

### 2.1 Linux 命名空間在 Docker 中的應用

Docker 使用 Linux 命名空間來提供容器隔離：

```bash
# 查看容器使用的命名空間
docker inspect --format '{{.State.Pid}}' <container_id>
ls -la /proc/<pid>/ns/

# 進入容器的命名空間
nsenter -t <pid> -n ip addr
```

### 2.2 命名空間類型

Docker 使用的 Linux 命名空間：

| 命名空間 | 功能 | Docker 應用 |
|---------|------|------------|
| pid | 進程隔離 | 每個容器有獨立的 PID 樹 |
| net | 網路隔離 | 每個容器有獨立的網路棧 |
| mnt | 掛載隔離 | 每個容器有獨立的檔案系統視圖 |
| uts | 主機名隔離 | 每個容器可設定獨立主機名 |
| ipc | IPC 隔離 | 每個容器有獨立的 IPC 資源 |
| user | 用戶隔離 | 容器內外的用戶 ID 映射 |

### 2.3 Docker Compose 網路命名空間

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx:latest
    networks:
      - frontend
      - backend

  api:
    image: api-server:latest
    networks:
      - backend

  db:
    image: postgres:latest
    networks:
      - backend

networks:
  frontend:
    driver: bridge
    name: frontend-network
  backend:
    driver: bridge
    name: backend-network
    internal: true  # 隔離外部存取
```

## 3. Linux 核心命名空間

### 3.1 命名空間類型詳解

```bash
# 創建新的命名空間
unshare --pid --net --mount --uts --ipc --fork bash

# 查看當前命名空間
ls -la /proc/self/ns/

# 比較不同進程的命名空間
readlink /proc/1/ns/pid
readlink /proc/$$/ns/pid
```

### 3.2 PID 命名空間

```bash
# 創建 PID 命名空間
unshare --pid --fork --mount-proc bash

# 在新命名空間中查看進程
ps aux
# 只會看到 bash 和 ps 進程
```

### 3.3 網路命名空間

```bash
# 創建網路命名空間
ip netns add my-netns

# 在命名空間中執行命令
ip netns exec my-netns ip addr

# 創建 veth 對連接命名空間
ip link add veth0 type veth peer name veth1
ip link set veth1 netns my-netns

# 配置 IP
ip addr add 10.0.0.1/24 dev veth0
ip netns exec my-netns ip addr add 10.0.0.2/24 dev veth1

# 啟用介面
ip link set veth0 up
ip netns exec my-netns ip link set veth1 up
ip netns exec my-netns ip link set lo up
```

### 3.4 User 命名空間

```bash
# 創建 user 命名空間（允許非 root 用戶創建）
unshare --user --map-root-user bash

# 在新命名空間中以 root 身份運行
whoami  # 顯示 root
```

## 4. 程式語言中的命名空間

### 4.1 C++ 命名空間

```cpp
// 定義命名空間
namespace MyProject {
    namespace Utils {
        void helper() {
            // 實現
        }
    }
    
    class MyClass {
    public:
        void method();
    };
}

// 使用命名空間
using namespace MyProject;
Utils::helper();
```

### 4.2 Python 模組命名空間

```python
# my_package/__init__.py
from .module1 import Class1
from .module2 import Class2

__all__ = ['Class1', 'Class2']

# 使用
import my_package
obj = my_package.Class1()

# 或者
from my_package import Class1
obj = Class1()
```

### 4.3 Go 套件命名空間

```go
// package declaration
package mypackage

// Import with alias
import (
    "fmt"
    myalias "github.com/example/package"
)

func MyFunction() {
    fmt.Println("Hello")
    myalias.DoSomething()
}
```

## 5. 雲端服務中的命名空間

### 5.1 AWS 資源組織

```yaml
# AWS Resource Groups 和標籤命名
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      Tags:
        - Key: Namespace
          Value: production
        - Key: Team
          Value: platform
```

### 5.2 Azure 資源群組

```json
{
  "name": "production-resources",
  "location": "eastus",
  "tags": {
    "namespace": "production",
    "team": "platform"
  }
}
```

### 5.3 GCP 專案和標籤

```yaml
# GCP 專案作為命名空間
project_id: my-project-production
labels:
  namespace: production
  team: platform
```

## 6. 比較總結

| 技術 | 命名空間用途 | 隔離級別 |
|-----|-------------|---------|
| Kubernetes | 邏輯資源隔離 | 應用層 |
| Docker | 進程和資源隔離 | 作業系統層 |
| Linux | 核心資源隔離 | 核心層 |
| 程式語言 | 程式碼組織 | 編譯/執行時 |
| 雲端服務 | 帳戶和資源組織 | 服務層 |

---

**上一章節**: [命名空間的核心特性](./core_features.md)
**下一章節**: [命名空間設計原則](./design_principles.md)
