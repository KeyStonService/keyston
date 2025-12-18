# Integration Template

此目錄包含整合模板，用於建立系統整合。

## 使用方式

```bash
cd .devcontainer/automation
ts-node code-generator.ts integration <名稱> <來源服務> <目標服務>
```

## 模板變數

- `name`: 整合名稱
- `sourceService`: 來源服務
- `targetService`: 目標服務

## 生成的檔案

- `src/`: 主要程式碼
- `tests/`: 測試檔案
- `config/`: 配置檔案

## 範例

```bash
ts-node code-generator.ts integration user-payment user-service payment-service
```
