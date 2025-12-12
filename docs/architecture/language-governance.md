# Language Governance Policy

## 語言治理政策實施指南

---

## 目錄

1. [治理目標](#治理目標)
2. [治理原則](#治理原則)
3. [審查流程](#審查流程)
4. [自動化檢查](#自動化檢查)
5. [違規處理](#違規處理)
6. [例外申請](#例外申請)

---

## 治理目標

語言治理的核心目標是：

1. **技術一致性**：確保整個系統使用一致的技術堆疊
2. **可維護性**：降低認知負擔，提高代碼可維護性
3. **性能優化**：在適當的層級使用適當的語言
4. **團隊效率**：減少上下文切換，提高開發效率
5. **自動化治理**：通過 CI/CD 自動檢查和執行策略

---

## 治理原則

### 原則 1：層級隔離（Layer Isolation）

每個架構層級有明確的語言範圍：

- **Layer 0 (OS/Hardware)**：C++, Rust, C
- **Layer 1 (Core Engine)**：TypeScript, Python
- **Layer 2 (Governance)**：Python, Rego
- **Layer 3 (AI/Automation)**：Python, TypeScript
- **Layer 4 (Services)**：Go, TypeScript
- **Layer 5 (Applications)**：TypeScript, Python (API only)

### 原則 2：最小語言集（Minimum Language Set）

只使用必要的語言，避免過度多樣化：

- **主要語言**：TypeScript, Python, C++
- **特殊用途**：Go (高並發服務), Rust (系統級), Rego (策略)
- **禁止引入**：PHP, Ruby, Lua, Perl, 等非標準語言

### 原則 3：API 優先（API-First）

不同語言間的互動必須通過明確的 API：

- REST API
- gRPC
- MCP (Model Context Protocol)
- ROS Topics/Services

### 原則 4：文檔齊全（Documentation Required）

引入新語言或技術必須：

1. 更新語言堆疊文檔
2. 提供使用指南
3. 說明選擇理由
4. 定義邊界範圍

---

## 審查流程

### Pull Request 檢查清單

當 PR 包含新的語言或技術時，必須通過以下檢查：

#### 1. 語言合規性檢查

- [ ] 新語言在 `language-policy.yaml` 的允許列表中
- [ ] 語言使用在正確的目錄/層級
- [ ] 沒有違反禁止規則

#### 2. 架構一致性檢查

- [ ] 符合分層架構原則
- [ ] API 邊界清晰
- [ ] 沒有跨層級的直接依賴

#### 3. 文檔完整性檢查

- [ ] 更新了 `language-stack.md`
- [ ] 提供了使用範例
- [ ] 說明了選擇理由

#### 4. 測試覆蓋率檢查

- [ ] 新代碼有相應的測試
- [ ] 測試使用相同語言或允許的測試框架

---

## 自動化檢查

### CI/CD 整合

語言治理通過以下 CI 步驟自動執行：

#### 1. 語言掃描 (Language Scanner)

```yaml
# .github/workflows/language-governance.yml
name: Language Governance Check

on: [pull_request]

jobs:
  language-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Language Policy Check
        run: |
          python tools/governance/check-language-policy.py
```

#### 2. 目錄語言映射驗證

檢查每個目錄是否符合語言策略：

```bash
# 範例：檢查 core/ 只包含 TS/Python/C++
find core/ -type f \( -name "*.php" -o -name "*.rb" -o -name "*.lua" \)
```

#### 3. 依賴分析

分析跨語言依賴是否符合規範：

```bash
# 檢查是否有非法的跨語言直接調用
grep -r "import.*php" core/
grep -r "require.*ruby" governance/
```

### 自動化工具

#### 語言策略檢查器

```python
# tools/governance/check-language-policy.py
import os
import yaml
from pathlib import Path

def check_language_policy():
    """檢查語言使用是否符合策略"""

    # 載入語言策略
    with open('config/language-policy.yaml') as f:
        policy = yaml.safe_load(f)

    violations = []

    # 檢查每個目錄
    for directory, rules in policy['directory_rules'].items():
        allowed = rules['allowed_languages']
        forbidden = rules.get('forbidden_patterns', [])

        # 掃描檔案
        for file in Path(directory).rglob('*'):
            if file.is_file():
                # 檢查檔案類型
                ext = file.suffix
                if not is_allowed_extension(ext, allowed):
                    violations.append({
                        'file': str(file),
                        'violation': f'Not allowed in {directory}',
                        'extension': ext
                    })

    return violations

def is_allowed_extension(ext, allowed_languages):
    """檢查檔案副檔名是否在允許的語言中"""
    language_extensions = {
        'TypeScript': ['.ts', '.tsx'],
        'Python': ['.py'],
        'C++': ['.cpp', '.hpp', '.h'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'Rego': ['.rego'],
    }

    for lang in allowed_languages:
        if ext in language_extensions.get(lang, []):
            return True
    return False
```

---

## 違規處理

### 違規等級

#### Level 1: 警告 (Warning)

不阻止 PR，但需要說明：

- 在允許的目錄使用次選語言
- 測試代碼使用非主要語言

**處理方式**：PR 註解，需要 reviewer 確認

#### Level 2: 錯誤 (Error)

阻止 PR 合併：

- 在錯誤的目錄使用語言
- 使用禁止的語言
- 缺少必要的文檔更新

**處理方式**：CI 失敗，必須修正

#### Level 3: 嚴重違規 (Critical)

需要架構師審查：

- 引入新的主要語言
- 改變核心架構的語言策略
- 大規模重構語言使用

**處理方式**：需要架構委員會批准

---

## 例外申請

### 何時需要例外

在以下情況可以申請例外：

1. **性能需求**：現有語言無法滿足性能要求
2. **生態系統**：特定功能只有某語言生態支持
3. **遺留系統**：整合既有系統必須使用特定語言
4. **實驗性質**：概念驗證或研究項目

### 例外申請流程

1. **提交申請**：在 PR 中創建 `language-exception-request.md`
2. **說明理由**：詳細說明為何需要例外
3. **評估影響**：分析對系統的影響範圍
4. **架構審查**：架構師或技術委員會審查
5. **記錄決策**：在 `docs/architecture/language-exceptions.md` 記錄

### 例外申請模板

```markdown
# Language Exception Request

## 基本資訊

- **申請者**：[姓名]
- **日期**：[YYYY-MM-DD]
- **PR**：[PR 連結]

## 例外請求

- **語言**：[要使用的語言]
- **位置**：[目錄路徑]
- **範圍**：[影響的檔案/模組]

## 理由說明

[詳細說明為何需要這個例外]

## 替代方案

[說明為何現有語言無法滿足需求]

## 影響評估

- **技術影響**：[對系統架構的影響]
- **維護影響**：[對團隊維護的影響]
- **性能影響**：[性能相關的考量]

## 時間範圍

- [ ] 永久例外
- [ ] 臨時例外（預計移除時間：[YYYY-MM-DD]）

## 審查意見

[架構師或委員會的審查意見]
```

---

## 定期審查

### 季度審查

每季度進行語言使用審查：

1. **使用統計**：各語言的代碼行數、檔案數
2. **違規統計**：違規次數和類型
3. **例外審查**：檢討臨時例外是否可以移除
4. **策略更新**：根據實際情況調整策略

### 年度審查

每年進行深度審查：

1. **技術債評估**：語言多樣性帶來的技術債
2. **生態系統評估**：各語言生態的發展
3. **團隊能力評估**：團隊對各語言的掌握程度
4. **策略重構**：必要時進行策略重大調整

---

## 工具與資源

### 檢查工具

1. **語言掃描器**：`tools/governance/check-language-policy.py`
2. **依賴分析器**：`tools/governance/analyze-dependencies.py`
3. **報告生成器**：`tools/governance/generate-language-report.py`
4. **AI Refactor Playbook Generator** ⭐
   **NEW**：`tools/generate-refactor-playbook.py`
   - 自動生成每個 cluster 的重構 playbook
   - 包含 P0/P1/P2 優先級計畫
   - 提供檔案與目錄結構交付視圖

### Refactor Playbooks ⭐ **NEW**

**AI 驅動的重構計畫生成系統**

為每個目錄群集（cluster）自動生成結構化、可執行的重構 playbook：

- **自動化生成**：整合語言治理報告、Semgrep 掃描、Hotspot 分析
- **分級計畫**：P0 (24-48h) / P1 (1週) / P2 (持續) 優先級
- **結構視圖**：自動生成目錄樹與檔案註解
- **Auto-Fix 整合**：明確標註可自動修復項目

**生成的 Playbooks：**

- `docs/refactor_playbooks/core__playbook.md` - 核心平台層
- `docs/refactor_playbooks/services__playbook.md` - 服務層
- `docs/refactor_playbooks/automation__playbook.md` - 自動化層
- `docs/refactor_playbooks/autonomous__playbook.md` - 自主系統層
- `docs/refactor_playbooks/governance__playbook.md` - 治理層
- `docs/refactor_playbooks/apps__playbook.md` - 應用層
- `docs/refactor_playbooks/tools__playbook.md` - 工具層
- `docs/refactor_playbooks/infrastructure__playbook.md` - 基礎設施層

**使用方式：**

```bash
# 生成所有 cluster playbooks
python3 tools/generate-refactor-playbook.py

# 生成特定 cluster playbook
python3 tools/generate-refactor-playbook.py --cluster "core/"

# 生成 LLM prompts
python3 tools/generate-refactor-playbook.py --use-llm
```

**詳細文檔：**

- [Refactor Playbooks README](../refactor_playbooks/README.md)
- [Implementation Summary](../refactor_playbooks/IMPLEMENTATION_SUMMARY.md)
- [Architecture](../refactor_playbooks/ARCHITECTURE.md)
- [Next Steps Plan](../REFACTOR_PLAYBOOK_NEXT_STEPS.md)

### 參考文件

- [Language Stack](./language-stack.md) - 語言堆疊文檔
- [Language Policy Config](../../config/language-policy.yaml) - 策略配置
- [System Architecture](./SYSTEM_ARCHITECTURE.md) - 系統架構
- [Refactor Playbooks](../refactor_playbooks/README.md) - 重構 Playbook 系統 ⭐
  **NEW**

### 相關連結

- [TypeScript Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [Python Style Guide (PEP 8)](https://peps.python.org/pep-0008/)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)

---

## 結論

語言治理不是限制創新，而是：

1. **建立秩序**：在混沌中建立可預測的結構
2. **提升效率**：減少認知負擔和上下文切換
3. **確保品質**：通過一致性提高代碼品質
4. **支持擴展**：為未來擴展建立堅實基礎

遵循這些策略，我們可以建立一個技術一致、可維護、可擴展的系統。

---

**文件版本：** v1.0  
**最後更新：** 2025-12-06  
**維護者：** Unmanned Island System Team
