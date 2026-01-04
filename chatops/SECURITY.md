# Security Policy

## 安全政策

本專案致力於維護安全的開發和部署環境。以下是我們的安全政策和流程。

## 漏洞回報

如果您發現安全漏洞，請不要公開回報。請遵循以下流程：

### 回報方式
- **電子郵件**：security@machine-native-ops.org
- **私用 Issue**：使用 GitHub 的私有安全回報功能

### 回報資訊
請包含以下資訊：
- 漏洞類型和嚴重程度
- 受影響的版本
- 重現步驟
- 潛在影響
- 建議修復方案（如有）

### 回應時間
我們承諾在 **48 小時內** 回應安全回報，並在 **7 個工作天**內提供修復計畫。

## 安全要求

### 密鑰管理
- ❌ **絕對禁止**提交任何真實密鑰、Token 或憑證
- ✅ 使用範例檔案或環境變數
- ✅ 所有敏感資料必須在 `examples/` 或 `templates/` 目錄
- ✅ 使用 `.gitignore` 防止意外提交

### 程式碼安全
- ✅ 所有 YAML 檔案必須通過 Schema 驗證
- ✅ 政策閘門（Policy Gates）必須阻止不安全配置
- ✅ 依賴項定期更新和安全掃描
- ✅ 供應鏈安全證據鏈完整性

### 部署安全
- ✅ 最小權限原則（Least Privilege）
- ✅ 網路隔離和存取控制
- ✅ 資源配額和限制
- ✅ 映像檔簽章驗證

## 供應鏈安全

### Evidence Chain
本專案實施完整的供應鏈證據鏈：

```
dist/evidence/
├── gate-report.json          # 閘門執行報告
├── digests.json              # 檔案雜湊清單
├── repo-fingerprint.json     # 倉庫指紋
├── toolchain.json            # 工具鏈版本
├── provenance.intoto.json    # 來源證明
├── attestation.intoto.json   # 證明聲明
└── merkle-root.json          # Merkle 根雜湊
```

### 驗證流程
1. **Schema 驗證**：確保所有 YAML 檔案符合規範
2. **政策檢查**：Kyverno 政策驗證
3. **完整性檢查**：檔案雜湊和 Merkle 樹驗證
4. **來源追蹤**：Git commit 和工具鏈版本記錄
5. **簽章驗證**：映像檔和工件簽名檢查

## 版本支援

### 安全更新
- 我們為最新兩個主要版本提供安全更新
- 舊版本可能不會收到安全修復
- 建議定期升級到最新版本

### CVE 處理
- 監控相關 CVE 漏洞
- 評估影響和風險等級
- 及時發布安全修復版本

## 安全最佳實踐

### 開發環境
- 使用受信任的開發環境
- 定期更新開發工具
- 啟用防火牆和防毒軟體
- 使用 VPN 存取內部資源

### 程式碼審查
- 所有變更必須經過程式碼審查
- 安全相關變更需要額外審查
- 自動化安全檢查整合到 CI/CD

### 部署環境
- 使用最新的 Kubernetes 版本
- 定期更新依賴套件
- 監控異常行為和安全事件
- 定期備份和災難恢復測試

## 聯絡資訊

### 安全團隊
- **電子郵件**：security@machine-native-ops.org
- **PGP 金鑰**：可從 our security page 取得

### 一般問題
- **GitHub Issues**：報告非安全相關問題
- **討論區**：一般技術討論
- **文件**：查閱線上文件

## 安全資源

- [Kubernetes 安全最佳實踐](https://kubernetes.io/docs/concepts/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SLSA Framework](https://slsa.dev/)
- [in-toto 規範](https://in-toto.io/)

---

感謝您協助我們維護專案的安全性！