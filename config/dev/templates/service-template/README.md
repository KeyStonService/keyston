# Service Template

此目錄包含服務模板，用於建立微服務。

## 使用方式

```bash
cd .devcontainer/automation
ts-node code-generator.ts service <名稱> [端口]
```

## 模板變數

- `name`: 服務名稱
- `port`: 服務端口
- `database`: 資料庫類型 (可選)

## 生成的檔案

- `src/`: 主要程式碼
- `tests/`: 測試檔案
- `docker/`: Docker 配置

## 範例

```bash
ts-node code-generator.ts service user-service 3001
```
