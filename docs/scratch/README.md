# Scratch Space - 全域草稿與設計空間

> **用途**：此目錄用於存放跨子系統的架構草稿、流程設計、方案比較、設計日誌等非正式文件。

---

## 📝 這裡適合放什麼？

✅ **適合的內容**：

- 跨子系統的架構設計草稿
- 多方案比較與決策記錄
- 系統整體流程的探索與實驗
- 重構計畫的早期草稿（未成熟前）
- 設計會議的筆記與討論紀錄
- 臨時的 Mermaid 圖、架構圖
- 研究筆記與技術調研

❌ **不適合的內容**：

- 正式的架構文件（應放 `docs/architecture/`）
- 已確定的重構劇本（應放 `docs/refactor_playbooks/03_refactor/`）
- 可執行程式碼（應放各 domain 主目錄）
- 舊程式碼資產（應放 `docs/refactor_playbooks/_legacy_scratch/`）

---

## 🏗️ 建議的檔案命名

使用描述性前綴或後綴，便於識別與清理：

- `scratch-{topic}.md` - 草稿筆記
- `notes-{meeting-date}.md` - 會議筆記
- `compare-{options}.md` - 方案比較
- `design-{feature}.md` - 設計探索
- `{topic}.scratch.md` - 後綴風格

**範例**：
- `scratch-three-layer-architecture.md`
- `notes-2025-12-06-refactor-discussion.md`
- `compare-typescript-vs-go-for-gateway.md`
- `design-autonomous-safety-mechanism.md`

---

## 🔄 生命週期管理

### Scratch → 正式文件

當 scratch 內容成熟後，應該：

1. **評估升級路徑**：
   - 移到 `docs/architecture/` 作為正式架構文件？
   - 整合到 `refactor_playbooks/` 的劇本中？
   - 寫成 RFC 或 ADR（Architecture Decision Record）？
   - 更新到相關 README？

2. **執行升級**：
   - 複製內容到目標位置
   - 進行必要的格式調整與完善
   - 刪除或移動原 scratch 檔案到 `docs/archive/`

3. **清理**：
   - 標記為 🗄️ 已歸檔
   - 移到 `docs/archive/scratch/`
   - 或直接刪除（如已完全整合）

### 定期清理

建議每 1-2 個月檢視此目錄：

```bash
# 找出超過 60 天未更新的檔案
find docs/scratch -name "*.md" -mtime +60 -type f

# 檢視並決定：升級、歸檔或刪除
```

---

## 📋 模板使用

使用標準模板保持一致性：

```bash
cp docs/refactor_playbooks/03_refactor/templates/SCRATCH_NOTES_TEMPLATE.md \
   docs/scratch/scratch-your-topic.md
```

然後編輯填入你的內容。

---

## 🎯 原則

1. **不是垃圾桶**：Scratch 是「創作空間」，不是隨意堆放的地方
2. **記錄思考過程**：保留設計演化的痕跡，對未來有價值
3. **定期整理**：成熟的內容要升級，過時的要清理
4. **可以進 git**：這些是設計資產，可以 commit（與 `_legacy_scratch/` 不同）

---

最後更新：2025-12-06
