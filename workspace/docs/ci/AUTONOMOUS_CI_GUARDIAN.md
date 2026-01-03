# 🤖 Autonomous CI Guardian

## 概述

Autonomous CI Guardian 是一個智能 CI/CD 工作流程，提供預測性失敗檢測和自動修復能力，幫助提早發現和解決潛在的 CI 失敗問題。

## 功能特性

### 1. 預測性失敗檢測 (Predictive Failure Detection)

自動分析 Pull Request 中的變更，評估潛在的 CI 失敗風險。

**檢測指標：**

- YAML 檔案變更數量
- Python 檔案變更數量
- Shell 腳本變更數量
- 配置檔案變更數量
- 工作流程檔案變更數量
- 總變更檔案數量

**風險等級：**

- 🟢 **低風險** (分數 < 3)：標準審查流程即可
- 🟡 **中等風險** (分數 3-4)：建議仔細檢查所有測試結果
- 🔴 **高風險** (分數 ≥ 5)：建議進行額外的人工審查和分批提交

### 2. 自動修復系統 (Auto-Remediation)

自動檢測常見的 CI 失敗原因並提供修復建議。

**檢測項目：**

- ✅ YAML 語法錯誤
- ✅ Shell 腳本語法錯誤
- ✅ Python 語法錯誤

**輸出：**

- 詳細的問題檢測報告
- 具體的修復步驟建議
- 問題統計和摘要

### 3. Guardian 報告 (Guardian Report)

綜合所有檢測結果，生成完整的報告並在需要時自動評論 PR。

**報告內容：**

- 風險評估結果
- 檢測到的問題詳情
- 修復建議
- 工作流程執行狀態

## 工作流程架構

```yaml
🤖 Autonomous CI Guardian
│
├── 📊 predictive-failure-detection
│   ├── 分析變更檔案模式
│   ├── 計算風險分數
│   ├── 生成風險報告
│   └── 上傳報告 (artifact)
│
├── 🔧 auto-remediation
│   ├── 檢測 YAML 語法問題
│   ├── 檢測 Shell 腳本問題
│   ├── 檢測 Python 語法問題
│   ├── 生成修復報告
│   └── 上傳報告 (artifact)
│
└── 📋 guardian-report
    ├── 下載所有報告
    ├── 生成綜合報告
    └── 評論 PR (如果有問題)
```

## 觸發條件

```yaml
on:
  pull_request:
    branches: [main, develop]
    types: [opened, synchronize, reopened]
```

**重要說明：**

- ✅ **僅在 PR 事件時觸發**
- ❌ **不使用排程觸發** (避免創建"幽靈"狀態檢查)
- ✅ **包含並發控制** (防止重複執行)

## 並發控制

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

確保同一 PR 的新提交會自動取消舊的工作流程執行，避免資源浪費。

## 權限設置

```yaml
permissions:
  contents: read        # 讀取代碼
  issues: write         # 創建評論
  pull-requests: write  # 更新 PR
```

最小權限原則，僅授予必要的權限。

## 使用方式

### 自動執行

工作流程會在以下情況自動執行：

1. 創建新的 Pull Request
2. 更新 Pull Request (push 新的 commit)
3. 重新打開已關閉的 Pull Request

### 查看報告

1. **在 Actions 頁面查看**
   - 導航到 Repository → Actions → 🤖 Autonomous CI Guardian
   - 選擇相應的工作流程執行
   - 查看各個 job 的執行結果

2. **下載 Artifacts**
   - 在工作流程執行詳情頁面底部
   - 下載 `predictive-failure-report` 和 `auto-remediation-report`
   - 報告保留 30 天

3. **PR 評論**
   - 如果檢測到問題，Guardian 會自動在 PR 中添加評論
   - 評論包含完整的風險評估和修復建議

## 最佳實踐

### 1. 關注風險警告

當收到高風險警告時：

- 仔細審查變更內容
- 考慮將大型變更拆分為多個小 PR
- 增加測試覆蓋率
- 進行更詳細的本地測試

### 2. 及時修復語法錯誤

Guardian 檢測到的語法錯誤應立即修復：

```bash
# YAML 語法檢查
yamllint <file>

# Shell 腳本語法檢查
bash -n <script>

# Python 語法檢查
python3 -m py_compile <file>
```

### 3. 監控 Guardian 健康狀態

定期檢查 Guardian 的執行狀態：

- 成功率應保持在 95% 以上
- 平均執行時間應在 10 分鐘以內
- 檢測準確率應持續優化

## 問題排查

### Guardian 工作流程失敗

1. 檢查工作流程日誌
2. 確認所需的工具已正確安裝
3. 驗證權限設置是否正確
4. 檢查是否有網路連接問題

### 誤報問題

如果 Guardian 報告誤報：

1. 在 Issue 中報告誤報案例
2. 包含相關的 PR 連結和日誌
3. 說明預期行為和實際行為的差異

### 性能問題

如果 Guardian 執行時間過長：

1. 檢查變更檔案數量
2. 考慮調整檢測範圍
3. 優化 find 命令的搜索路徑

## 配置選項

可以通過環境變數調整 Guardian 的行為：

```yaml
env:
  FAILURE_THRESHOLD: 3      # 失敗風險閾值
  DETECTION_WINDOW: "24h"   # 檢測時間窗口
```

## 相關文件

- [MERGE_STATUS_LOADING_FIX.md](../MERGE_STATUS_LOADING_FIX.md) - 合併狀態載入問題修復
- [CI 故障排除](../troubleshooting/ci-troubleshooting.md) - CI/CD 問題診斷指南
- [工作流程最佳實踐](./WORKFLOW_BEST_PRACTICES.md) - GitHub Actions 最佳實踐

## 版本歷史

| 版本 | 日期 | 變更內容 |
|------|------|---------|
| 1.0.0 | 2025-12-19 | 初始版本，包含預測性檢測和自動修復功能 |

## 維護者

- SynergyMesh DevOps Team
- GitHub: @MachineNativeOps

## 授權

本工作流程遵循專案的開源授權條款。

---

**狀態：** 🟢 生產就緒
**最後更新：** 2025-12-19
