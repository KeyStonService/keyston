# 多倉庫整合快速入門 | Multi-Repo Integration Quick Start

**5分鐘將100個倉庫整合到 keystone-ai**

---

## 🚀 快速開始

### 步驟 1: 準備配置文件

```bash
# 複製配置模板
cp config/external_repos.yaml.example config/external_repos.yaml

# 編輯配置文件，添加你的倉庫
vim config/external_repos.yaml
# 或使用你喜歡的編輯器
```

### 步驟 2: 填寫倉庫信息

在 `config/external_repos.yaml` 中添加你的倉庫：

```yaml
sync_repositories:
  - name: my-repo-1
    url: https://github.com/your-org/repo1.git
    branch: main
    priority: medium
    description: "Repository 1 description"

  - name: my-repo-2
    url: https://github.com/your-org/repo2.git
    branch: main
    priority: medium
    description: "Repository 2 description"

  # ... 添加所有100個倉庫
```

### 步驟 3: 執行同步

```bash
# 首次同步（推薦先 dry-run）
python tools/sync_external_repos.py --dry-run

# 確認無誤後，執行實際同步
python tools/sync_external_repos.py
```

### 步驟 4: 提交到 Git

```bash
# 查看變更
git status

# 添加並提交
git add external/
git commit -m "feat: integrate 100 external repositories"

# 推送
git push
```

---

## 📊 結果

同步完成後，你的目錄結構：

```
keystone-ai/
├── external/              # 新增：所有外部倉庫
│   ├── my-repo-1/        # 來自 repo1
│   │   ├── src/
│   │   ├── lib/
│   │   └── .sync_metadata.json  # 同步元數據
│   ├── my-repo-2/        # 來自 repo2
│   ├── my-repo-3/
│   └── ...               # 100個倉庫
├── core/                  # 原有代碼
├── services/
└── tools/
```

---

## 🔄 定期更新

### 手動更新

```bash
# 更新所有倉庫
python tools/sync_external_repos.py

# 只更新特定倉庫
python tools/sync_external_repos.py --repo my-repo-1

# 只更新核心倉庫
python tools/sync_external_repos.py --core-only
```

### 自動更新（CI/CD）

創建 `.github/workflows/sync-repos.yml`:

```yaml
name: Sync External Repos

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2點
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install pyyaml
      - name: Sync repositories
        run: python tools/sync_external_repos.py
      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add external/
          git commit -m "chore: auto-sync external repos" || exit 0
          git push
```

---

## 💡 常見問題

### Q: 如何添加新倉庫？

**A**: 編輯 `config/external_repos.yaml`，添加新倉庫，然後運行：

```bash
python tools/sync_external_repos.py --repo new-repo-name
```

### Q: 如何排除某些文件？

**A**: 在 `config/external_repos.yaml` 的 `exclude_patterns` 中添加：

```yaml
sync_options:
  exclude_patterns:
    - "*.log"
    - "node_modules"
    - "my-secret-file"
```

### Q: 同步失敗怎麼辦？

**A**: 查看錯誤信息，常見原因：

- 倉庫 URL 錯誤
- 分支不存在
- 網絡問題
- 權限不足（私有倉庫需要認證）

### Q: 如何處理私有倉庫？

**A**: 使用 SSH URL 或配置 Git 憑證：

```yaml
- name: private-repo
  url: git@github.com:your-org/private-repo.git
  # 或使用 personal access token
  # url: https://YOUR_TOKEN@github.com/your-org/private-repo.git
```

### Q: 可以選擇性同步子目錄嗎？

**A**: 是的，使用 `include_paths`:

```yaml
sync_options:
  include_paths:
    - "src/"
    - "lib/"
    # 只同步這些目錄
```

---

## 🎯 進階使用

### 批量導入倉庫

如果你有倉庫列表文件：

```bash
# repos.txt 格式：
# name,url,branch
# repo1,https://github.com/org/repo1.git,main
# repo2,https://github.com/org/repo2.git,main

# 轉換為 YAML（需要自定義腳本）
python tools/convert_repos_to_yaml.py repos.txt
```

### 監控同步狀態

```bash
# 查看最後同步時間
find external/ -name ".sync_metadata.json" -exec jq -r '.synced_at' {} \;

# 生成同步報告
python tools/sync_external_repos.py --dry-run > sync_report.txt
```

---

## ✅ 驗證

確認整合成功：

```bash
# 1. 檢查目錄數量
ls -l external/ | wc -l
# 應該接近你配置的倉庫數量

# 2. 檢查元數據
cat external/my-repo-1/.sync_metadata.json

# 3. 驗證內容
ls external/my-repo-1/
```

---

## 📚 相關文檔

- 完整指南：`docs/MULTI_REPO_INTEGRATION_GUIDE.md`
- 工具文檔：`tools/sync_external_repos.py --help`
- 配置範例：`config/external_repos.yaml.example`

---

**準備好了嗎？開始整合你的100個倉庫！** 🚀
