# /docs/ 目錄結構檢查 - 快速總結

> **檢查日期**: 2025-12-10  
> **狀態**: ✅ 分析完成，等待執行授權

---

## 📝 一句話總結

**`docs/GOVERNANCE/` 目錄違反了「治理統一管理」原則，應立即遷移到 `governance/29-docs/`，同時需修復7組大小寫目錄衝突。**

---

## 🚨 關鍵發現

### 問題 1: 治理目錄重複（P0 最嚴重）⭐

```
❌ 當前: docs/GOVERNANCE/ (6個治理文檔)
✅ 正確: governance/29-docs/ (23維度治理矩陣的一部分)
```

**為什麼是嚴重問題？**

- 您提到：「治理已經全部遷移至 ./governance 並且統一映射引用依賴執行操作統一管理」
- 但 `docs/GOVERNANCE/` 仍然存在，造成矛盾和混淆
- 影響 24 處引用需要更新

### 問題 2: 大小寫目錄衝突（P1）

7 組重複目錄：

- `ARCHITECTURE/` vs `architecture/`
- `AGENTS/` vs `agents/`
- 及其他 5 個 UPPERCASE 目錄

### 問題 3: 其他組織問題

- 106 個 .md 文件散落根目錄
- 1.1MB 生成文件未隔離

---

## ⚡ 快速執行

### 選項 A: 一鍵修復（推薦）

```bash
# 預覽變更（安全，不會修改文件）
cd /home/runner/work/SynergyMesh/SynergyMesh
./docs/_fix_structure.sh --dry-run

# 確認無誤後執行
./docs/_fix_structure.sh --execute

# 驗證
python3 tools/docs/validate_index.py --verbose
make all-kg
```

**修復內容**:

1. ✅ 治理目錄: docs/GOVERNANCE/ → governance/29-docs/
2. ✅ 大小寫統一: UPPERCASE → lowercase
3. ✅ 生成文件: 移至 docs/generated/
4. ✅ 更新引用: 自動更新所有路徑

### 選項 B: 僅修復治理問題（最小變更）

```bash
# 手動執行
mkdir -p governance/29-docs
mv docs/GOVERNANCE/* governance/29-docs/
rmdir docs/GOVERNANCE

# 更新引用
sed -i 's|docs/GOVERNANCE/|governance/29-docs/|g' tools/cli/README.md

# 重新生成索引
python3 tools/docs/scan_repo_generate_index.py
```

### 選項 C: 暫不修復

保留現狀，待未來處理。  
參考文檔: `docs/STRUCTURE_ANALYSIS_REPORT.md`

---

## 📊 影響範圍

| 項目 | 數量 | 風險 |
|------|------|------|
| 移動文件 | ~25 | 低（有腳本） |
| 刪除目錄 | 7 | 低（空目錄） |
| 更新引用 | 2 檔案 | 中（自動化） |
| 破壞性 | - | 中（可Git回滾） |

---

## 📚 相關文檔

1. **完整分析**: [docs/STRUCTURE_ANALYSIS_REPORT.md](./STRUCTURE_ANALYSIS_REPORT.md) (5.7KB)
2. **修復腳本**: [docs/_fix_structure.sh](./_fix_structure.sh) (7.3KB，可執行)
3. **PR 描述**: 查看本 Pull Request 的完整描述

---

## 🤔 Q&A

### Q: 為什麼 docs/GOVERNANCE/ 不應該存在？


### Q: 執行修復會破壞什麼嗎？

**A**: 主要影響是路徑變更。腳本會自動更新已知引用，但可能有少數手動引用需要檢查。**建議先 dry-run 預覽**。

### Q: 可以部分執行嗎？

**A**: 可以。腳本分4個階段，您可以編輯腳本註解掉不需要的階段。或直接手動執行選項B（僅修復治理問題）。

### Q: 如果執行後有問題怎麼辦？

**A**: Git 可以完全回滾：`git reset --hard HEAD^`

---

## ✅ 建議行動

**推薦流程**:

```bash
# 1. 預覽變更
./docs/_fix_structure.sh --dry-run

# 2. 仔細檢查輸出，確認符合預期

# 3. 執行修復
./docs/_fix_structure.sh --execute

# 4. 驗證結果
git status
git diff
python3 tools/docs/validate_index.py --verbose

# 5. 提交（如果滿意）
git add .
git commit -m "修復 /docs/ 目錄結構：治理統一到 governance/"
git push
```

---

**最後更新**: 2025-12-10  
**維護者**: GitHub Copilot  
**遵循**: [AI Behavior Contract](../.github/AI-BEHAVIOR-CONTRACT.md)
