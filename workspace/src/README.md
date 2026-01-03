# Source Code

MachineNativeOps 核心源代碼目錄，包含所有業務邏輯和系統實作。

## 目錄結構概覽

```
src/
├── core/           # 核心引擎（AI 決策、編排器、Phase 4）
├── ai/             # AI 代理與模型
├── autonomous/     # 自主系統框架
├── automation/     # 自動化引擎
├── services/       # 微服務實作
├── api/            # API 端點
├── apps/           # 應用程式
├── governance/     # 治理系統
├── models/         # 資料模型
└── ...             # 更多模組
```

## 核心模組

### core/

系統核心引擎，包含：

- AI 決策引擎
- 合約引擎
- 編排器（Orchestrators）
- Phase 4 智能自動化系統
- 即時生成引擎

### autonomous/

自主系統框架（8 個已實現骨架）：

- 架構穩定性
- 測試兼容性
- 安全可觀測性
- 身份與租戶管理
- 成本管理
- 性能與可靠性
- 知識庫
- 核心編排器

### ai/

AI 相關模組：

- 代理系統（Agents）
- 模型定義
- 訓練系統

## 演示腳本

```bash
# 核心功能演示
python src/demo_core.py

# 即時生成演示
python src/demo_instant_generation.py
```

## 模組依賴關係

```
core/ ──► services/ ──► api/
  │           │
  ▼           ▼
models/    autonomous/
```

## 開發指南

1. 新增功能應放置於對應的模組目錄
2. 共享代碼放置於 `shared/` 或 `utils/`
3. 遵循現有的命名規範和目錄結構
4. 確保有對應的測試在 `tests/` 目錄

## 相關資源

- [DIRECTORY.md](./DIRECTORY.md) - 詳細目錄說明
- [core/README.md](./core/README.md) - 核心引擎文檔
- [tests/](../tests/) - 測試代碼
