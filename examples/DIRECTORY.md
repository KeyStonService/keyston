# examples

## 目錄職責

此目錄包含 MachineNativeOps 平台的**範例代碼與專案模板**，供開發者學習和快速啟動新專案。

## 子目錄說明

| 子目錄 | 說明 | 內容 |
|--------|------|------|
| `basic/` | 基礎入門範例 | hello-world, simple-service |
| `advanced/` | 進階使用範例 | microservices 架構範例 |
| `templates/` | 專案模板 | api-service, batch-job, web-app |
| `debug-examples/` | 調試與問題排查範例 | 調試技巧示範 |

## 檔案說明

### enterprise-orchestrator-example.py

- **職責**：企業級 SynergyMesh Orchestrator 使用示例
- **功能**：
  - 多租戶設置和管理
  - 依賴解析和優化
  - 容錯和重試機制
  - 資源配額管理
  - 審計日誌
  - 監控和指標
- **依賴**：`src/core/orchestrators` 模組

## 目錄結構

```
examples/
├── basic/                    # 基礎範例
│   ├── hello-world/         # 最簡單的入門範例
│   └── simple-service/      # 簡單服務範例
├── advanced/                 # 進階範例
│   └── microservices/       # 微服務架構範例
├── templates/                # 專案模板
│   ├── api-service/         # API 服務模板
│   ├── batch-job/           # 批次作業模板
│   └── web-app/             # Web 應用模板
├── debug-examples/           # 調試範例
└── enterprise-orchestrator-example.py  # 企業編排器範例
```

## 使用方式

1. **學習基礎**：從 `basic/hello-world` 開始
2. **建立新專案**：複製 `templates/` 下的適當模板
3. **進階學習**：參考 `advanced/` 和企業編排器範例

## 與其他目錄的關係

- **src/**：範例中引用的核心模組來源
- **docs/tutorials/**：對應的教學文檔
- **config/dev/templates/**：更多開發模板
