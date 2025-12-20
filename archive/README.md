# Archive

此目錄存放 MachineNativeOps 專案的歸檔資產，包含已棄用的舊版系統、歷史基礎設施配置，以及參考用的知識庫。

## 目錄結構

```
archive/
├── experiments/           # 實驗性代碼歸檔（目前為空）
├── infrastructure/        # 舊版 Kubernetes/監控配置
├── legacy/                # 舊版系統代碼
│   ├── v1-python-drones/  # 第一版 Python 無人機系統
│   └── v2-multi-islands/  # 第二版多島嶼架構
└── unmanned-engineer-ceo/ # 工程師能力模型知識庫
```

## 使用說明

### 何時參考此目錄

- 需要了解系統演進歷史
- 尋找舊版實作作為參考
- 遷移或重構時需對照原始設計

### 注意事項

1. **不建議直接使用**：此目錄內容已不再維護，可能存在過時的依賴或配置
2. **僅供參考**：若需使用任何內容，請複製到適當的工作目錄後再修改
3. **現行配置位置**：
   - 基礎設施配置：`deploy/`
   - 運維監控：`ops/`
   - 核心代碼：`src/`

## 各子目錄簡介

| 目錄 | 說明 | 詳細文檔 |
|------|------|----------|
| experiments | 預留的實驗歸檔區 | - |
| infrastructure | K8s、Prometheus、Grafana 等舊配置 | [README](./infrastructure/README.md) |
| legacy | v1/v2 版本的系統代碼 | [v1](./legacy/v1-python-drones/README.md), [v2](./legacy/v2-multi-islands/README.md) |
| unmanned-engineer-ceo | 14 層工程師能力模型 | [README](./unmanned-engineer-ceo/README.md) |

## 相關文檔

- [DIRECTORY.md](./DIRECTORY.md) - 本目錄的詳細結構說明
