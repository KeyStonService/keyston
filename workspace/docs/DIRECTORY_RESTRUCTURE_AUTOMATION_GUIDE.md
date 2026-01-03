# MachineNativeOps 目錄重構自動化指南

## 概述

本文檔提供了完整的目錄重構自動化解決方案，包括所有必要的工具、腳本和操作指南。即使沒有 AI 助手的協助，項目也能獨立完成這些重構任務。

## 🛠️ 自動化工具套件

### 1. 主要重構工具

#### `tools/automated_directory_restructure.py`

**功能**: 執行完整的目錄重構流程

**使用方法**:

```bash
# 試運行模式（不實際修改文件）
python tools/automated_directory_restructure.py --dry-run

# 執行完整重構
python tools/automated_directory_restructure.py

# 只重構 src 目錄
python tools/automated_directory_restructure.py --phase src

# 只重構 config 目錄
python tools/automated_directory_restructure.py --phase config
```

**特性**:

- 🔍 自動分析現有目錄結構
- 📦 自動創建備份
- 🔄 智能文件移動和重組
- ✅ 自動驗證重構結果
- 📊 生成詳細報告

### 2. 驗證工具

#### `tools/validate_restructure.py`

**功能**: 驗證重構的完整性和正確性

**使用方法**:

```bash
# 基本驗證
python tools/validate_restructure.py

# 詳細驗證
python tools/validate_restructure.py --detailed

# 自動修復導入路徑
python tools/validate_restructure.py --fix-imports
```

**驗證項目**:

- ✅ 目錄結構完整性
- ✅ 文件完整性檢查
- ✅ Python 導入路徑驗證
- ✅ 配置文件驗證
- ✅ Web 應用結構驗證

## 📋 重構規則配置

### 目標目錄結構

#### `src/` 目錄結構

```
src/
├── core/
│   ├── plugins/          # 核心插件模塊
│   ├── safety/           # 安全機制
│   └── services/         # 核心服務
├── platform/
│   ├── agents/           # 智能代理
│   ├── automation/       # 自動化工具
│   └── integrations/     # 第三方集成
├── services/
│   ├── api/              # API 服務
│   ├── data/             # 數據服務
│   └── monitoring/       # 監控服務
├── shared/
│   ├── types/            # 類型定義
│   ├── utils/            # 工具函數
│   └── constants/        # 常量定義
└── web/
    ├── admin/            # 管理後台
    ├── client/           # 客戶端應用
    └── api/              # Web API
```

#### `config/` 目錄結構

```
config/
├── ci-cd/                # CI/CD 配置
├── deployment/           # 部署配置
├── monitoring/           # 監控配置
├── environments/         # 環境配置
├── security/             # 安全配置
├── build-tools/          # 構建工具配置
└── governance/           # 治理配置
```

### 路徑映射規則

```python
path_mappings = {
    "src/core/modules": "src/core/plugins",
    "src/core/safety_mechanisms": "src/core/safety",
    "src/apps/web": "src/web/admin",
    "src/apps/cli": "src/platform/cli",
    "src/apps/api": "src/services/api"
}
```

## 🚀 快速開始

### 1. 準備工作

```bash
# 確保在項目根目錄
cd MachineNativeOps

# 檢查 Python 環境
python --version  # 需要 Python 3.8+

# 安裝依賴（如果需要）
pip install pyyaml
```

### 2. 執行重構

```bash
# 步驟 1: 試運行檢查
python tools/automated_directory_restructure.py --dry-run

# 步驟 2: 執行實際重構
python tools/automated_directory_restructure.py

# 步驟 3: 驗證結果
python tools/validate_restructure.py --detailed
```

### 3. 修復問題（如有）

```bash
# 自動修復導入路徑
python tools/validate_restructure.py --fix-imports

# 重新驗證
python tools/validate_restructure.py
```

## 📊 報告和日誌

### 生成的報告文件

1. **`restructure_report.json`** - 重構執行報告
2. **`validation_report.json`** - 驗證結果報告
3. **`restructure.log`** - 詳細執行日誌

### 報告內容

#### 重構報告結構

```json
{
  "timestamp": "2025-12-18T07:30:00",
  "project_root": "/path/to/MachineNativeOps",
  "operations": [
    {
      "type": "backup",
      "source": "/path/to/project",
      "target": "/path/to/backup",
      "status": "completed"
    }
  ],
  "errors": [],
  "warnings": [],
  "statistics": {
    "total_operations": 10,
    "total_errors": 0,
    "total_warnings": 2
  }
}
```

#### 驗證報告結構

```json
{
  "timestamp": "2025-12-18T07:35:00",
  "validation_results": {
    "directory_structure": {
      "valid": true,
      "missing_directories": []
    },
    "file_integrity": {
      "valid": true,
      "missing_files": []
    },
    "import_paths": {
      "valid": true,
      "broken_imports": []
    }
  },
  "summary": {
    "total_issues": 0,
    "overall_valid": true
  }
}
```

## 🔧 高級配置

### 自定義重構規則

可以通過修改 `automated_directory_restructure.py` 中的 `restructure_rules` 來自定義重構規則：

```python
self.restructure_rules = {
    "src": {
        "target_structure": {
            # 自定義目錄結構
        }
    }
}
```

### 擴展驗證規則

可以通過修改 `validate_restructure.py` 中的驗證邏輯來添加自定義驗證規則：

```python
def custom_validation(self):
    # 自定義驗證邏輯
    pass
```

## 🛡️ 安全措施

### 1. 自動備份

- 重構前自動創建完整備份
- 備份位置：`backup_before_restructure/`
- 排除不必要的文件（`.git`, `node_modules` 等）

### 2. 試運行模式

- `--dry-run` 參數可以在不實際修改文件的情況下預覽變更
- 安全檢查所有操作

### 3. 回滾機制

如果重構出現問題，可以從備份恢復：

```bash
# 刪除當前目錄（謹慎操作）
rm -rf src config

# 從備份恢復
cp -r backup_before_restructure/src .
cp -r backup_before_restructure/config .
```

## 🔄 維護和更新

### 定期維護任務

1. **更新重構規則**

   ```bash
   # 檢查是否有新的目錄需要重構
   find . -type d -name "*" | head -20
   ```

2. **驗證項目健康狀態**

   ```bash
   # 定期運行驗證
   python tools/validate_restructure.py --detailed
   ```

3. **清理備份**

   ```bash
   # 清理舊備份（保留最近一次）
   rm -rf backup_before_restructure_*
   ```

### 擴展功能

可以根據需要添加新功能：

1. **新的重構規則**
2. **額外的驗證檢查**
3. **自動化測試集成**
4. **CI/CD 管道集成**

## 📝 故障排除

### 常見問題

#### 1. 權限錯誤

```bash
# 確保有足夠權限
chmod +x tools/automated_directory_restructure.py
chmod +x tools/validate_restructure.py
```

#### 2. Python 模組缺失

```bash
# 安裝必要模組
pip install pyyaml
```

#### 3. 文件被鎖定

```bash
# 檢查是否有進程在使用文件
lsof | grep "src/"
```

#### 4. 導入路徑錯誤

```bash
# 自動修復
python tools/validate_restructure.py --fix-imports
```

### 調試模式

啟用詳細日誌輸出：

```bash
# 設置日誌級別
export PYTHONPATH=.
python -v tools/automated_directory_restructure.py --dry-run
```

## 📚 API 參考

### DirectoryRestructureTool 類

#### 主要方法

- `create_backup()` - 創建項目備份
- `analyze_current_structure()` - 分析當前結構
- `restructure_src_directory()` - 重構 src 目錄
- `restructure_config_directory()` - 重構 config 目錄
- `validate_restructure()` - 驗證重構結果
- `generate_report()` - 生成報告

### RestructureValidator 類

#### 主要方法

- `validate_directory_structure()` - 驗證目錄結構
- `validate_file_integrity()` - 驗證文件完整性
- `validate_import_paths()` - 驗證導入路徑
- `validate_config_files()` - 驗證配置文件
- `generate_validation_report()` - 生成驗證報告

## 🎯 最佳實踐

### 1. 執行前檢查清單

- [ ] 確認所有更改已提交到 Git
- [ ] 運行試運行模式檢查
- [ ] 檢查磁盤空間是否足夠
- [ ] 確認 Python 環境正常

### 2. 執行後驗證

- [ ] 運行完整驗證
- [ ] 檢查所有測試是否通過
- [ ] 驗證應用程序正常啟動
- [ ] 提交更改到 Git

### 3. 文檔更新

- [ ] 更新 README.md
- [ ] 記錄重大變更
- [ ] 更新 API 文檔
- [ ] 通知團隊成員

## 📞 支持和反饋

如果在使用過程中遇到問題：

1. 檢查日誌文件 `restructure.log`
2. 查看生成的報告文件
3. 參考故障排除部分
4. 提交 Issue 到項目倉庫

---

**注意**: 本自動化工具設計為獨立運行，不需要外部 AI 協助。所有必要的邏輯和規則都已內建在工具中。
