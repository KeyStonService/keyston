# Examples

MachineNativeOps 範例代碼與專案模板集合。

## 快速導覽

| 類別 | 目錄 | 適合對象 |
|------|------|----------|
| 基礎範例 | [basic/](./basic/) | 初次接觸的開發者 |
| 進階範例 | [advanced/](./advanced/) | 有經驗的開發者 |
| 專案模板 | [templates/](./templates/) | 快速啟動新專案 |
| 調試範例 | [debug-examples/](./debug-examples/) | 問題排查參考 |

## 基礎範例

### hello-world
最簡單的入門範例，展示基本的系統呼叫方式。

```bash
cd examples/basic/hello-world
# 依照目錄內 README 執行
```

### simple-service
簡單服務範例，展示基礎的服務建立流程。

## 進階範例

### microservices

微服務架構範例，展示多服務協作的模式。

## 專案模板

使用模板快速建立新專案：

```bash
# 複製 API 服務模板
cp -r examples/templates/api-service my-new-service

# 複製 Web 應用模板
cp -r examples/templates/web-app my-new-webapp

# 複製批次作業模板
cp -r examples/templates/batch-job my-new-job
```

## 企業編排器範例

`enterprise-orchestrator-example.py` 展示企業級功能：

- 多租戶管理
- 依賴解析
- 容錯機制
- 資源配額
- 審計日誌

執行方式：

```bash
python examples/enterprise-orchestrator-example.py
```

## 相關資源

- [DIRECTORY.md](./DIRECTORY.md) - 詳細目錄說明
- [docs/tutorials/](../docs/tutorials/) - 教學文檔
- [docs/QUICK_START.md](../docs/QUICK_START.md) - 快速開始指南
