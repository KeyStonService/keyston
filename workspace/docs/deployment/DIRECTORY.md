# deployment

## 目錄職責

此目錄包含 MachineNativeOps 平台的部署配置、指南和腳本，涵蓋 Cloudflare Workers、本地開發環境和生產部署流程。

## 檔案說明

### CLOUDFLARE_GITHUB_INTEGRATION.md

- **職責**：Cloudflare 與 GitHub 整合指南
- **功能**：說明如何設置 Cloudflare Workers、Pages 與 GitHub 的完整整合
- **涵蓋內容**：Worker 部署、KV/D1/R2 資源創建、Webhook 設置、環境配置

### DEPLOYMENT_CHECKLIST.md

- **職責**：部署前檢查清單
- **功能**：確保所有必要的配置和驗證步驟都已完成
- **依賴**：部署指南、驗證報告

### DEPLOYMENT_GUIDE.md

- **職責**：SynergyMesh 平台部署指南
- **功能**：提供完整的部署流程，包括三大核心子系統的部署步驟
- **涵蓋內容**：環境檢查、依賴安裝、配置驗證、服務部署

### DEPLOYMENT_INTEGRATION_SUMMARY.md

- **職責**：部署整合摘要
- **功能**：總結部署整合狀態和關鍵配置
- **依賴**：部署指南

### DEPLOYMENT_MANIFEST.md

- **職責**：部署清單文檔
- **功能**：記錄部署的組件、版本和配置資訊
- **依賴**：部署指南

### DEPLOYMENT_VALIDATION_REPORT.md

- **職責**：部署驗證報告
- **功能**：記錄部署後的驗證結果和系統健康檢查
- **依賴**：部署指南、檢查清單

### WRANGLER_INSTALL_UPDATE.md

- **職責**：Wrangler CLI 安裝與更新指南
- **功能**：提供 Wrangler（Cloudflare Workers CLI 工具）的完整安裝、更新和故障排除指南
- **涵蓋內容**：系統要求、安裝方法（npm/yarn/pnpm）、版本管理、更新程序、驗證步驟
- **依賴**：Node.js >= 18.0.0, npm >= 8.0.0

## 職責分離說明

- 不同環境的部署配置分離
- 部署腳本與配置文件分離
- 基礎設施代碼與應用配置分離

## 設計原則

部署配置標準化，支持多環境部署，確保部署的可重複性和可靠性。

---

*此文檔由 directory_doc_generator.py 自動生成，請根據實際情況補充和完善內容。*
