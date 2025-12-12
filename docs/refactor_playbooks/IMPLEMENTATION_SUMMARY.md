# AI Refactor Playbook Generator - Implementation Summary

**實作摘要：AI 重構 Playbook 生成器**

---

## 📋 概覽

本實作建立了一個完整的 AI 驅動重構計畫生成系統，針對 Unmanned Island
System 的各個目錄群集（cluster）自動生成結構化、可執行的重構 playbook。

## ✅ 已完成功能

### 1. 核心生成器 (`tools/generate-refactor-playbook.py`)

**特色：**

- ✅ 完整的 System Prompt（定義 AI 角色為架構師 + 語言治理負責人 + 安全顧問）
- ✅ 動態 User Prompt 模板（整合所有治理數據）
- ✅ 支援單一 cluster 或批量生成
- ✅ LLM 整合模式（生成 prompts 供 ChatGPT/Claude 使用）
- ✅ Stub 模式（無需 LLM 即可生成基本 playbook）

**System Prompt 設計：**

```
角色定義：
- 首席軟體架構師（負責整體架構與模組邊界）
- 語言治理負責人（Language Governance Owner）
- 安全與品質顧問（整合 Semgrep / 靜態分析結果）

專案背景：
- 專案名稱：Unmanned Island System
- 語言策略：TypeScript + Python（高層）/ Go + C++ + ROS2（低層）
- 治理系統：Language Governance / Hotspot / Cluster Heatmap / Migration Flow / Auto-Fix Bot
```

**User Prompt 結構：**

1. Cluster 基本資訊（名稱、分數）
2. 語言治理違規列表
3. Hotspot 檔案分析
4. Semgrep 安全問題
5. Migration Flow 流向
6. 全局 AI 建議摘要

**輸出格式：**

```markdown
## 1. Cluster 概覽

## 2. 問題盤點

## 3. 語言與結構重構策略

## 4. 分級重構計畫（P0 / P1 / P2）

## 5. 適合交給 Auto-Fix Bot 的項目

## 6. 驗收條件與成功指標

## 7. 檔案與目錄結構（交付視圖）⭐ NEW
```

### 2. 資料整合系統

**整合的數據源：**

| 資料來源        | 路徑                                        | 用途           |
| --------------- | ------------------------------------------- | -------------- |
| 語言治理報告    | `governance/language-governance-report.md`  | 違規檔案與原因 |
| Hotspot 分析    | `apps/web/public/data/hotspot.json`         | 高風險檔案列表 |
| Cluster Heatmap | `apps/web/public/data/cluster-heatmap.json` | 群集健康分數   |
| Migration Flow  | `apps/web/public/data/migration-flow.json`  | 語言遷移建議   |
| Semgrep 報告    | `governance/semgrep-report.json`            | 安全問題       |
| AI 建議         | `governance/ai-refactor-suggestions.md`     | 全局重構策略   |

**資料解析能力：**

- ✅ Markdown 報告解析（提取違規項目）
- ✅ JSON 數據過濾（按 cluster 篩選）
- ✅ 分數計算與排序
- ✅ 流向分析（incoming/outgoing flows）

### 3. 生成的 Playbooks

**8 個 Cluster Playbooks：**

1. `core__playbook.md` - 核心平台層（Score: 75）
2. `services__playbook.md` - 服務層（Score: 82）
3. `automation__playbook.md` - 自動化層（Score: 60）
4. `autonomous__playbook.md` - 自主系統層（Score: 45）
5. `governance__playbook.md` - 治理層（Score: 55）
6. `apps__playbook.md` - 應用層（Score: 68）
7. `tools__playbook.md` - 工具層（Score: 50）
8. `infrastructure__playbook.md` - 基礎設施層（Score: 40）

**每個 Playbook 包含：**

- 📊 當前狀態概覽（違規數、hotspot 數、安全問題數）
- 🔍 詳細問題盤點（分類、排序、附風險說明）
- 🎯 重構策略建議（語言層級、目錄結構、遷移路徑）
- 📅 分級執行計畫（P0 = 24-48h / P1 = 1週 / P2 = 持續）
- 🤖 自動化範圍定義（Auto-Fix Bot vs 人工審查）
- ✅ 驗收條件與成功指標
- 🗂️ **檔案與目錄結構（交付視圖）** ⭐ **NEW**
  - 受影響目錄清單
  - 完整檔案/目錄樹狀結構圖（3 層深度）
  - 主要檔案與目錄的註解說明

**Section 7: 檔案與目錄結構（交付視圖）**

這是新增的強制交付要求，確保每個重構計畫都包含清晰的結構視圖：

1. **自動生成目錄樹**
   - 使用 `_generate_directory_tree()` 方法
   - Tree 風格縮排顯示（最多 3 層深度）
   - 自動過濾 `.git`、`node_modules`、`__pycache__` 等
   - 每個目錄限制顯示 20 個項目（防止過長）

2. **智能檔案註解**
   - 使用 `_generate_file_annotations()` 方法
   - 自動識別重要檔案（README.md、package.json、tsconfig.json 等）
   - 提供標準化描述（例如："Node.js 專案配置"、"TypeScript 編譯配置"）
   - 最多顯示 10 個重要檔案

3. **實務價值**
   - 變更範圍一目了然
   - 方便未來維護人員理解重構
   - 適合交給第三方平台或其他 Agent
   - 提供每次重構的「前後快照」

### 4. CI/CD 自動化

**GitHub Actions Workflow:** `.github/workflows/update-refactor-playbooks.yml`

**觸發條件：**

- ⏰ 每日自動執行（00:00 UTC）
- 🔄 治理數據變更時
- 🖱️ 手動觸發（workflow_dispatch）

**執行流程：**

```yaml
1. Checkout repository 2. Setup Python 3.10 3. Install dependencies (pyyaml) 4.
Generate refactor playbooks 5. Check for changes 6. Commit and push (if changes
detected) 7. Create workflow summary
```

### 5. 文檔系統

**主要文檔：**

- ✅ `docs/refactor_playbooks/README.md` - 使用指南（3.5KB）
- ✅ `docs/refactor_playbooks/IMPLEMENTATION_SUMMARY.md` - 本文件
- ✅ 更新 `DOCUMENTATION_INDEX.md` - 新增重構 Playbooks 章節

**README 涵蓋內容：**

- 📚 什麼是 Refactor Playbook
- 🚀 如何使用（生成、執行、整合）
- 📊 資料來源說明
- 🤖 LLM 整合方式
- 📁 檔案命名規則
- 🔄 更新流程建議
- 🎯 成功指標定義

## 📊 實作統計

**程式碼規模：**

- `generate-refactor-playbook.py`: 600+ 行
- System/User Prompt 模板: 完整 Markdown 格式
- 支援功能：資料載入、解析、過濾、生成、LLM 整合

**生成檔案：**

- 8 個 cluster playbooks
- 1 個 README
- 1 個 CI workflow
- 6 個示範資料檔案

**文檔更新：**

- `DOCUMENTATION_INDEX.md`: 新增 2 個章節
- 新增完整使用範例與指令

## 🎯 使用方式

### 基本使用

```bash
# 生成所有 clusters 的 playbooks
python3 tools/generate-refactor-playbook.py

# 生成特定 cluster
python3 tools/generate-refactor-playbook.py --cluster "core/"

# 生成 LLM prompts（供外部 LLM 使用）
python3 tools/generate-refactor-playbook.py --use-llm

# 指定 repo 路徑
python3 tools/generate-refactor-playbook.py --repo-root /path/to/repo
```

### 進階使用（LLM 整合）

```bash
# 1. 生成 LLM prompt
python3 tools/generate-refactor-playbook.py --use-llm --cluster "services/"

# 2. Prompt 會輸出到 console 或儲存為 .txt 檔
# 3. 複製到 ChatGPT/Claude
# 4. 將 LLM 回應保存為 playbook.md
```

### CI 整合

```yaml
# .github/workflows/your-workflow.yml
- name: Generate Refactor Playbooks
  run: python3 tools/generate-refactor-playbook.py

- name: Commit Changes
  run: |
    git add docs/refactor_playbooks/
    git commit -m "chore: update refactor playbooks"
    git push
```

## 🔧 技術架構

### 類別設計

```python
class RefactorPlaybookGenerator:
    # 屬性
    - repo_root: Path
    - clusters: Dict
    - violations: List[Dict]
    - hotspots: List[Dict]
    - semgrep_results: List[Dict]
    - migration_flows: Dict
    - global_suggestions: str

    # 主要方法
    - load_governance_data()           # 載入所有治理數據
    - generate_cluster_prompt()        # 生成 LLM prompt
    - generate_playbook_stub()         # 生成 stub playbook
    - generate_all_playbooks()         # 批量生成

    # 輔助方法
    - _get_cluster_violations()        # 過濾 cluster 違規
    - _get_cluster_hotspots()          # 過濾 cluster hotspots
    - _get_cluster_semgrep()           # 過濾 cluster 安全問題
    - _get_migration_flows()           # 取得遷移流向
```

### 資料流

```
治理數據檔案
    ↓
load_governance_data()
    ↓
cluster 過濾與分組
    ↓
generate_cluster_prompt() / generate_playbook_stub()
    ↓
格式化為 Markdown
    ↓
輸出到 docs/refactor_playbooks/
```

## 🎉 成果展示

### 範例輸出（services/ cluster）

```markdown
# Refactor Playbook: services/

**Generated:** 2025-12-06T17:03:15 **Cluster Score:** 82 **Status:** Draft

## 1. Cluster 概覽

- 違規數量：0
- Hotspot 檔案：2
- 安全問題：2

## 2. 問題盤點

### Hotspot 檔案 (2)

- **services/gateway/router.lua** (score: 88)
- **services/api/handler.cpp** (score: 70)

### Semgrep 安全問題 (2)

- [MEDIUM] **services/gateway/router.lua**: Use of eval-like function detected
- [MEDIUM] **services/api/handler.cpp**: Potential buffer overflow

...（後續章節）
```

## 🚀 未來擴展方向

### 可能的改進

1. **完整 LLM 整合**
   - 直接呼叫 OpenAI/Anthropic API
   - 自動生成完整 playbook（非 stub）
   - 支援多輪對話改進

2. **更豐富的分析**
   - 整合 CodeQL 結果
   - 依賴分析（dependency graph）
   - 測試覆蓋率數據
   - 技術債統計

3. **互動式 Web 介面**
   - 視覺化 cluster 關係
   - 互動式編輯 playbook
   - 進度追蹤儀表板

4. **自動執行能力**
   - 與 Auto-Fix Bot 深度整合
   - P0 項目自動產生 PR
   - 追蹤執行狀態

5. **多語言支援**
   - 英文版 playbooks
   - 其他語系支援

## 📚 相關文件

- [Refactor Playbooks README](./README.md)
- [Language Governance](../../governance/README.md)
- [AI Refactor Suggestions](../../governance/ai-refactor-suggestions.md)
- [DOCUMENTATION_INDEX.md](../../DOCUMENTATION_INDEX.md)

## 🤝 維護指南

### 更新 Prompt 模板

編輯 `tools/generate-refactor-playbook.py`:

```python
SYSTEM_PROMPT = """..."""  # 更新 System Prompt
USER_PROMPT_TEMPLATE = """..."""  # 更新 User Prompt
```

### 新增資料源

```python
def load_governance_data(self):
    # 新增資料載入邏輯
    new_data_path = self.repo_root / "path/to/new_data.json"
    if new_data_path.exists():
        with open(new_data_path, 'r') as f:
            self.new_data = json.load(f)
```

### 修改輸出格式

```python
def generate_playbook_stub(self, cluster_name: str, cluster_score: float = 0) -> str:
    # 修改 Markdown 模板
    playbook = f"""# Refactor Playbook: {cluster_name}

    ... 自訂章節 ...
    """
    return playbook
```

---

**版本:** 1.0.0  
**日期:** 2025-12-06  
**作者:** Copilot Agent  
**狀態:** ✅ Production Ready
