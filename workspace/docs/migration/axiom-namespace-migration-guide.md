# AXIOM 到 MachineNativeOps 命名空間遷移指南

## 🎯 概述

本指南提供詳細的步驟說明，幫助開發者將 AXIOM 命名空間順利遷移到 MachineNativeOps。

## 📝 遷移步驟

### 步驟 1：環境檢查

```bash
git status
git checkout -b feature/machinenativeops-namespace-migration
```

### 步驟 2：試運行驗證

```bash
python scripts/migration/namespace-converter.py --dry-run .
```

### 步驟 3：正式轉換

```bash
python scripts/migration/namespace-converter.py .
```

### 步驟 4：驗證轉換

```bash
# 檢查 YAML 語法
find . -name "*.yaml" -exec python -c "import yaml; yaml.safe_load(open('{}'))" \;

# 驗證轉換完成度
python scripts/migration/namespace-converter.py --verify .
```

### 步驟 5：提交變更

```bash
git add .
git commit -m "feat: migrate AXIOM namespace to MachineNativeOps"
```

## 🔍 故障排除

### 常見問題

#### 1. 轉換工具執行失敗

```bash
# 檢查 Python 版本
python --version
```

#### 2. YAML 語法錯誤

```bash
# 手動檢查
python -c "import yaml; yaml.safe_load(open('problem-file.yaml'))"
```

## 📊 驗證清單

- [ ] 所有 YAML 檔案語法正確
- [ ] 轉換報告顯示 0 個遺漏引用
- [ ] 專案功能測試通過
- [ ] Git 提交訊息清晰完整

---

*最後更新：2025-12-20*
