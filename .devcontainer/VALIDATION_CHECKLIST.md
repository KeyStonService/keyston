# Kind Cluster Devcontainer - 驗證清單

## 🔍 手動驗證步驟

由於 devcontainer 配置需要在實際的 GitHub Codespaces 或本地 devcontainer 環境中測試，以下是驗證清單：

### ✅ 驗證項目

#### 1. 環境準備檢查
- [ ] Dockerfile 正確安裝 Kind v0.20.0
- [ ] devcontainer.json 包含 Podman feature
- [ ] devcontainer.json 包含 Azure CLI feature
- [ ] 環境變數正確設定

#### 2. 腳本語法檢查
- [x] setup-kind-cluster.sh 語法驗證通過
- [x] post-create.sh 語法驗證通過
- [x] post-start.sh 語法驗證通過
- [x] devcontainer.json 為有效的 JSONC 格式

#### 3. 功能測試（需在 Codespaces 中執行）

##### 3.1 自動啟動測試
```bash
# 在 Codespaces 啟動後，自動執行的項目：
# 1. post-create.sh 應該自動執行
# 2. setup-kind-cluster.sh 應該自動被調用
# 3. Kind cluster "governance-test" 應該被建立
```

驗證命令：
```bash
# 檢查 Kind 是否安裝
kind version

# 檢查 Podman 是否安裝
podman --version

# 檢查 kubectl 是否安裝
kubectl version --client

# 檢查 Azure CLI 是否安裝
az version

# 檢查 cluster 是否建立
kind get clusters

# 檢查節點狀態
kubectl get nodes

# 檢查 cluster 資訊
kubectl cluster-info --context kind-governance-test
```

##### 3.2 手動重建測試
```bash
# 刪除 cluster
kind delete cluster --name governance-test

# 重新執行腳本
bash .devcontainer/scripts/setup-kind-cluster.sh

# 驗證成功建立
kind get clusters
kubectl get nodes
```

##### 3.3 錯誤處理測試
```bash
# 測試重複執行（應該偵測到已存在的 cluster）
bash .devcontainer/scripts/setup-kind-cluster.sh
# 預期輸出：✅ Kind cluster 'governance-test' already exists
```

#### 4. 環境變數測試
```bash
# 檢查環境變數
echo $KIND_EXPERIMENTAL_PROVIDER  # 應輸出: podman
echo $KIND_CLUSTER_NAME           # 應輸出: governance-test
```

#### 5. 整合測試
```bash
# 部署測試應用
kubectl create deployment nginx --image=nginx
kubectl get deployments

# 清理
kubectl delete deployment nginx
```

## 📊 預期結果

### 成功指標
1. ✅ Codespaces 啟動後 60 秒內 Kind cluster 可用
2. ✅ `kind get clusters` 顯示 "governance-test"
3. ✅ `kubectl get nodes` 顯示至少一個 Ready 節點
4. ✅ Podman 作為容器引擎正常運作
5. ✅ 所有工具（kubectl, kind, podman, az）可正常執行

### 效能指標
- Kind cluster 建立時間：< 60 秒
- 總記憶體使用：< 2GB
- CPU 使用率：< 50%

## 🐛 常見問題排查

### 問題 1：Podman 服務未啟動
```bash
# 解決方案
sudo systemctl start podman
# 或
podman system service --time=0
```

### 問題 2：權限問題
```bash
# 解決方案
sudo usermod -aG podman $USER
newgrp podman
```

### 問題 3：Kind cluster 建立失敗
```bash
# 檢查 logs
podman ps -a
podman logs <container_id>

# 清理後重試
kind delete cluster --name governance-test
podman system prune -a -f
bash .devcontainer/scripts/setup-kind-cluster.sh
```

## 📝 驗證報告模板

完成驗證後，請填寫以下報告：

```markdown
### Kind Cluster Devcontainer 驗證報告

**日期**: YYYY-MM-DD
**環境**: [ ] GitHub Codespaces / [ ] Local Devcontainer
**驗證人員**: 

#### 結果摘要
- [ ] 所有自動化腳本執行成功
- [ ] Kind cluster 正常啟動
- [ ] 所有工具可用

#### 詳細測試結果
1. Kind 安裝: [ ] 通過 / [ ] 失敗
2. Podman 安裝: [ ] 通過 / [ ] 失敗
3. kubectl 安裝: [ ] 通過 / [ ] 失敗
4. Azure CLI 安裝: [ ] 通過 / [ ] 失敗
5. Cluster 自動建立: [ ] 通過 / [ ] 失敗
6. 節點狀態: [ ] Ready / [ ] NotReady

#### 效能數據
- Cluster 建立時間: ___ 秒
- 記憶體使用: ___ MB
- CPU 使用率: ___ %

#### 問題與建議
（如有問題，請詳細描述）

```

## ✅ 自動化驗證（未來改進）

可考慮加入以下自動化測試：

```bash
#!/bin/bash
# test-kind-setup.sh (未來可實作)

# 1. 測試 Kind 安裝
test_kind_installation() {
    if command -v kind &> /dev/null; then
        echo "✅ Kind installed"
        return 0
    else
        echo "❌ Kind not installed"
        return 1
    fi
}

# 2. 測試 Podman 安裝
test_podman_installation() {
    if command -v podman &> /dev/null; then
        echo "✅ Podman installed"
        return 0
    else
        echo "❌ Podman not installed"
        return 1
    fi
}

# 3. 測試 Cluster 建立
test_cluster_creation() {
    if kind get clusters | grep -q "governance-test"; then
        echo "✅ Cluster exists"
        return 0
    else
        echo "❌ Cluster not found"
        return 1
    fi
}

# 執行所有測試
test_kind_installation
test_podman_installation
test_cluster_creation
```

---

**注意**: 此驗證清單應在實際的 GitHub Codespaces 或本地 devcontainer 環境中執行。
