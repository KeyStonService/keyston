# CI 自動評論與錯誤導航系統

## 概述

此系統為 SynergyMesh 專案提供智能化的 CI 錯誤診斷和自動評論功能，協助開發者快速定位和修復 CI 失敗問題。

## 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Actions Workflow                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ 環境檢查         │  │ 構建 & 測試      │  │ 自動評論   │ │
│  │ (environment-    │→ │ (build-and-test) │→ │ (auto-    │ │
│  │  check)          │  │                   │  │  comment) │ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
│         ↓                      ↓                     ↓        │
│    Annotation          Annotation              動態標籤      │
│    (Runner log)        (構建日誌)             (ci-failed)    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────┐
│              知識庫 & 故障排除 Runbook                        │
├─────────────────────────────────────────────────────────────┤
│  • ci-troubleshooting.md（常見錯誤與解決方案）               │
│  • check-env.sh（環境檢查腳本）                              │
│  • setup-ci-env.yml（自動初始化）                            │
└─────────────────────────────────────────────────────────────┘
```

## 核心功能

### 1. 三階段流程

#### 階段一：環境檢查 (environment-check)

**目的**：驗證 CI 環境的基本依賴是否正確安裝

**檢查項目**：

- Docker 安裝狀態
- Docker Compose 安裝狀態（支援 `docker-compose` 和 `docker compose` 兩種形式）

**輸出**：

- `docker_status`: Docker 安裝狀態（success/failed）
- `compose_status`: Docker Compose 安裝狀態（success/failed）
- `error_message`: 錯誤訊息
- `error_type`: 錯誤類型（DOCKER_NOT_INSTALLED/DOCKER_COMPOSE_NOT_INSTALLED）
- `solution`: 建議的解決方案

**特點**：

- 使用 `continue-on-error: true` 確保即使失敗也能繼續執行
- 使用 GitHub Annotation (`::error` 和 `::notice`) 在 Runner log 中標記錯誤
- 自動生成 GITHUB_STEP_SUMMARY

#### 階段二：構建與測試 (build-and-test)

**目的**：執行實際的構建和測試流程

**依賴**：僅在環境檢查成功時執行

**步驟**：

1. 構建 Docker 鏡像
2. 運行測試（使用主機環境而非容器，避免已知的 npm ci 問題）

**特點**：

- 使用 `set -o pipefail` 確保管道命令的錯誤能被正確捕捉
- 明確指定 `shell: bash` 確保 Bash 特性可用
- 將構建和測試日誌保存到檔案，供後續步驟使用

#### 階段三：自動評論 (auto-comment)

**目的**：根據前面階段的結果，自動生成有針對性的 PR 評論

**執行條件**：`always()` - 無論前面階段成功或失敗都執行

**評論類型**：

1. **環境檢查失敗**
   - 觸發條件：Docker 或 Docker Compose 未安裝
   - 評論內容：安裝指南、驗證命令、相關文檔連結
   - 標籤：`ci-failed`, `env-error`

2. **構建失敗**
   - 觸發條件：Docker 鏡像構建失敗
   - 評論內容：常見原因、本地調試命令、修正建議
   - 標籤：`ci-failed`, `build-failed`

3. **測試失敗**
   - 觸發條件：測試執行失敗
   - 評論內容：測試調試步驟、覆蓋率檢查、相關資源
   - 標籤：`ci-failed`

4. **CI 通過**
   - 觸發條件：所有檢查成功
   - 評論內容：成功訊息、檢查項目清單
   - 動作：移除所有失敗標籤

### 2. 動態標籤管理

系統會自動管理以下標籤：

| 標籤           | 說明        | 添加時機     | 移除時機     |
| -------------- | ----------- | ------------ | ------------ |
| `ci-failed`    | CI 整體失敗 | 任何階段失敗 | 所有檢查通過 |
| `env-error`    | 環境錯誤    | 環境檢查失敗 | 環境檢查通過 |
| `build-failed` | 構建失敗    | 構建失敗     | 構建成功     |

**特點**：

- 避免重複添加標籤（先檢查現有標籤）
- 優雅處理標籤不存在的情況

### 3. 環境檢查腳本 (check-env.sh)

**位置**：`scripts/check-env.sh`

**功能**：

- 檢查 Docker、Docker Compose、Node.js、Git 安裝
- 驗證 Node.js 版本（需要 >= 18）
- 檢查磁盤空間使用率
- 提供彩色輸出和詳細的安裝指南

**使用方式**：

```bash
bash scripts/check-env.sh
```

**輸出範例**：

```
╔════════════════════════════════════════╗
║     CI 環境檢查與自動修復工具          ║
╚════════════════════════════════════════╝

[1/4] 檢查 Docker...
✓ docker 已安裝：Docker version 24.0.0

[2/4] 檢查 Docker Compose...
✓ docker compose (plugin) 已安裝：Docker Compose version v2.20.0

[3/4] 檢查 Node.js...
✓ node 已安裝：v18.17.0

[4/4] 檢查 Git...
✓ git 已安裝：git version 2.41.0

[磁盤空間]
✓ 磁盤空間充足：45%

╔════════════════════════════════════════╗
║     環境檢查通過 - 準備就緒！        ║
╚════════════════════════════════════════╝
```

### 4. CI 故障排除文檔 (ci-troubleshooting.md)

**位置**：`docs/ci-troubleshooting.md`

**內容**：

- 快速診斷流程圖（Mermaid 格式）
- 6 種常見錯誤的詳細解決方案
- 調試命令參考（Docker、Docker Compose、npm/Node.js）
- 自動化修復清單
- 聯繫支持資訊

**涵蓋錯誤類型**：

1. Docker Compose 未安裝
2. 磁盤空間不足
3. Dockerfile 語法錯誤
4. 測試超時
5. npm ci 在 Docker 容器中失敗
6. Node.js 版本不符

### 5. 環境初始化 Workflow (setup-ci-env.yml)

**位置**：`.github/workflows/setup-ci-env.yml`

**類型**：可重用 workflow (`workflow_call`)

**功能**：

- 自動安裝缺失的 Docker Compose
- 清理磁盤空間
- 驗證環境就緒狀態

**輸出**：

- `env_ready`: 環境是否準備就緒（true/false）

**使用方式**：

```yaml
jobs:
  setup:
    uses: ./.github/workflows/setup-ci-env.yml

  main-job:
    needs: setup
    if: needs.setup.outputs.env_ready == 'true'
    runs-on: ubuntu-latest
    steps:
      - name: Run main job
        run: echo "Environment is ready"
```

## 使用指南

### 開發者使用

1. **本地開發前檢查環境**

   ```bash
   bash scripts/check-env.sh
   ```

2. **CI 失敗時**
   - 查看 PR 中的自動評論
   - 根據評論中的建議執行修正步驟
   - 參考 [CI 故障排除文檔](ci-troubleshooting.md)

3. **提交 PR 前**
   - 確保本地環境通過檢查
   - 本地運行測試：`npm test`
   - 本地構建 Docker 鏡像：`docker-compose build`

### 維護者使用

1. **監控 CI 狀態**
   - 關注帶有 `ci-failed` 標籤的 PR
   - 檢查自動評論是否提供了有用的資訊

2. **更新故障排除文檔**
   - 發現新的常見問題時，更新 `docs/ci-troubleshooting.md`
   - 添加具體的解決步驟和命令

3. **調整 workflow**
   - 根據實際使用情況調整評論內容
   - 添加新的檢查項目或錯誤類型

## 技術細節

### 安全考量

1. **固定版本的 Actions**
   - 使用 SHA 固定 GitHub Actions 版本
   - 例如：`actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`

2. **權限管理**

   ```yaml
   permissions:
     contents: read
     pull-requests: write
     issues: write
   ```

   - 僅授予必要的權限
   - `contents: read` - 讀取代碼
   - `pull-requests: write` - 添加評論
   - `issues: write` - 管理標籤

3. **環境腳本安全**
   - 使用 `set -e` 確保錯誤即停止
   - 避免執行不安全的命令
   - 驗證用戶輸入（如有）

### 性能優化

1. **條件執行**
   - `build-and-test` 僅在環境檢查成功時執行
   - 避免不必要的資源浪費

2. **並行執行**
   - 各階段的檢查步驟可以並行執行
   - 使用 `continue-on-error: true` 確保所有檢查都執行

3. **日誌管理**
   - 僅保留最後 20-30 行日誌
   - 使用 `tail` 命令減少輸出大小

### 相容性

1. **Docker Compose**
   - 支援 `docker-compose` 命令
   - 支援 `docker compose` plugin
   - 自動檢測並使用可用的命令

2. **Node.js 版本**
   - 檢查版本是否 >= 18
   - 提供多種安裝方式（nvm、套件管理器、官方下載）

3. **磁盤空間檢查**
   - 使用 `df` 不帶 `-h` 選項以獲得更可靠的輸出
   - 計算百分比而非依賴格式化輸出

## 已知限制

1. **Docker npm ci 問題**
   - 目前測試在主機環境運行，而非 Docker 容器內
   - 原因：Docker 容器內 npm ci 存在 "Exit handler never called" 已知問題
   - 參考：與 `core-services-ci.yml` 保持一致

2. **僅支援 PR 事件**
   - 自動評論僅在 PR 事件中生效
   - Push 到主分支不會生成評論（僅生成 step summary）

3. **標籤管理**
   - 需要 PR 存在才能添加標籤
   - 標籤不存在時移除操作會被忽略

## 未來改進方向

1. **AI 輔助診斷**
   - 使用 AI 分析錯誤日誌
   - 提供更智能的解決方案建議

2. **錯誤統計**
   - 收集 CI 失敗統計數據
   - 識別最常見的問題
   - 自動優化檢查流程

3. **自動修復**
   - 對某些常見問題自動提交修復 commit
   - 例如：更新依賴版本、修復格式問題

4. **整合現有 CI**
   - 與 `core-services-ci.yml` 整合
   - 避免重複的檢查步驟

5. **通知機制**
   - Slack 通知
   - Email 通知
   - 自定義 webhook

## 參考資源

- [GitHub Actions 文檔](https://docs.github.com/en/actions)
- [GitHub Script Action](https://github.com/actions/github-script)
- [Docker 文檔](https://docs.docker.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)

## 貢獻指南

### 添加新的錯誤類型

1. 在 `environment-check` job 中添加新的檢查步驟
2. 在 `error-handler` step 中添加錯誤類型判斷
3. 在 `auto-comment` job 中添加對應的評論步驟
4. 更新 `docs/ci-troubleshooting.md` 添加解決方案
5. 更新本文檔說明新的錯誤類型

### 改進評論內容

1. 編輯 `.github/workflows/ci-auto-comment.yml`
2. 找到對應的 `github-script` step
3. 修改 `comment` 變數的內容
4. 測試評論格式和連結

### 更新環境檢查腳本

1. 編輯 `scripts/check-env.sh`
2. 添加新的檢查函數或修改現有函數
3. 測試腳本在不同環境下的行為
4. 更新 `docs/ci-troubleshooting.md` 中的相關內容

## 版本歷史

### v1.0.0 (2024-11-26)

- 初始版本發布
- 三階段 CI 流程
- 自動評論功能
- 動態標籤管理
- 環境檢查腳本
- CI 故障排除文檔
- 可重用環境初始化 workflow

## 授權

MIT License - 詳見專案根目錄的 LICENSE 檔案
