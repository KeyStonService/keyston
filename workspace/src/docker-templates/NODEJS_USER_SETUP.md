# Node.js Docker 使用者權限標準配置

## 問題描述


## 標準解決方案

**在所有 Node.js Dockerfile 中，必須在 `USER nodejs` 之前加入以下配置：**

```dockerfile
# 建立 nodejs 使用者的家目錄並設定權限
RUN chown -R nodejs:nodejs /app && \
    mkdir -p /home/nodejs/.npm && \
    chown -R nodejs:nodejs /home/nodejs

# 切換到非 root 使用者
USER nodejs

# 設定 npm 快取目錄環境變數
ENV NPM_CONFIG_CACHE=/home/nodejs/.npm
```

## 應用位置

此配置必須應用於所有包含 Node.js 構建步驟的 Dockerfile：

- ✅ `core/contract_service/contracts-L1/contracts/Dockerfile`
- ✅ `mcp-servers/Dockerfile`
- ✅ `advanced-system-src/Dockerfile`
- ⚠️  未來任何新的 Node.js 服務 Dockerfile

## 檢查清單

在創建新的 Node.js Dockerfile 時，請確認：

1. [ ] 在 `USER nodejs` 之前創建 `/home/nodejs/.npm` 目錄
2. [ ] 設置正確的目錄所有權 `chown -R nodejs:nodejs /home/nodejs`
3. [ ] 設置 `ENV NPM_CONFIG_CACHE=/home/nodejs/.npm`
4. [ ] 在多階段構建中，每個使用 npm 的階段都要配置

## 參考

- Issue: #81 (持續整合高階應用程式)
- PR: #82
- Commits: 255ee243, 9f525357, [current]
