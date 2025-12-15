#!/usr/bin/env python3
"""
Generate consolidated CI comment for PR
Reads job summaries and creates a unified report following Chinese template
"""

import os
import json
import sys
from datetime import datetime, timezone


def main():
    # Parse inputs from environment
    ci_name = os.getenv("CI_NAME", "CI Pipeline")
    job_summaries_json = os.getenv("JOB_SUMMARIES", "{}")
    workflow_run_id = os.getenv("WORKFLOW_RUN_ID", "unknown")
    commit_sha = os.getenv("COMMIT_SHA", "unknown")
    overall_status = os.getenv("OVERALL_STATUS", "unknown")
    
    try:
        job_summaries = json.loads(job_summaries_json)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in job-summaries", file=sys.stderr)
        job_summaries = {}
    
    # Determine status emoji and text
    if overall_status == "success":
        status_emoji = "✅"
        status_text = "執行成功"
        status_color = "🟢"
    elif overall_status == "warning":
        status_emoji = "⚠️"
        status_text = "執行有警告"
        status_color = "🟡"
    else:
        status_emoji = "❌"
        status_text = "執行失敗"
        status_color = "🔴"
    
    # Build error summary table
    error_summary_lines = []
    failed_jobs = []
    warning_jobs = []
    success_jobs = []
    
    for job_name, job_data in job_summaries.items():
        status = job_data.get("status", "unknown")
        message = job_data.get("message", "無詳細訊息")
        
        if status == "failure":
            failed_jobs.append(f"- ❌ **{job_name}**: {message}")
        elif status == "warning":
            warning_jobs.append(f"- ⚠️ **{job_name}**: {message}")
        elif status == "success":
            success_jobs.append(f"- ✅ **{job_name}**: {message}")
        else:
            error_summary_lines.append(f"- ❔ **{job_name}**: {message}")
    
    # Consolidate summaries
    all_summaries = failed_jobs + warning_jobs + success_jobs + error_summary_lines
    error_summary = "\n".join(all_summaries) if all_summaries else "無詳細錯誤資訊"
    
    # Determine error type and suggestions
    error_type = "未知錯誤"
    fix_suggestions = []
    quick_fix_commands = []
    
    if failed_jobs:
        # Analyze failed jobs to determine error type
        all_messages = " ".join([job_summaries[job]["message"] 
                                for job in job_summaries 
                                if job_summaries[job].get("status") == "failure"])
        
        if "type" in all_messages.lower() or "typescript" in all_messages.lower():
            error_type = "TypeScript 型別錯誤"
            fix_suggestions = [
                "本地執行 `npm run typecheck` 重現錯誤",
                "根據錯誤訊息修復型別定義",
                "確認相關 interface/type 定義是否正確",
                "推送修復分支，CI 將自動重跑"
            ]
            quick_fix_commands.append("npm run typecheck")
        elif "test" in all_messages.lower() or "jest" in all_messages.lower():
            error_type = "測試失敗"
            fix_suggestions = [
                "本地執行 `npm test` 重現測試失敗",
                "檢查測試案例與實際程式碼的差異",
                "確認測試資料與預期結果是否正確",
                "推送修復分支，CI 將自動重跑"
            ]
            quick_fix_commands.append("npm test")
        elif "lint" in all_messages.lower() or "eslint" in all_messages.lower():
            error_type = "Lint 錯誤"
            fix_suggestions = [
                "本地執行 `npm run lint:fix` 自動修復",
                "檢查 .eslintrc 配置是否正確",
                "對於無法自動修復的問題，手動修改程式碼",
                "推送修復分支，CI 將自動重跑"
            ]
            quick_fix_commands.append("npm run lint:fix")
        elif "build" in all_messages.lower():
            error_type = "建置失敗"
            fix_suggestions = [
                "本地執行 `npm run build` 重現建置錯誤",
                "檢查依賴是否完整安裝",
                "確認環境變數配置正確",
                "推送修復分支，CI 將自動重跑"
            ]
            quick_fix_commands.append("npm run build")
        else:
            error_type = "CI 執行錯誤"
            fix_suggestions = [
                "查看完整日誌以了解具體錯誤",
                "檢查最近的代碼變更",
                "參考 CI 故障排除文檔",
                "推送修復分支，CI 將自動重跑"
            ]
            quick_fix_commands.append("bash scripts/check-env.sh")
    else:
        fix_suggestions = [
            "所有檢查已通過",
            "可以安全地合併此 PR"
        ]
    
    # Build quick fix commands section
    quick_fix_section = ""
    if quick_fix_commands:
        quick_fix_section = "\n".join([f"```bash\n{cmd}\n```" for cmd in quick_fix_commands])
    else:
        quick_fix_section = "```bash\nbash scripts/check-env.sh\n```"
    
    # Build fix suggestions section
    fix_suggestions_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(fix_suggestions)])
    
    # Generate timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Build the consolidated comment using the Chinese template
    ci_name_tag = ci_name.replace(' ', '-').lower()
    comment_body = f"""<!-- CI_REPORT:{ci_name_tag} -->

## {status_emoji} {ci_name} - 客服報告

{status_color} **狀態**：{status_text}

**執行 ID**：`{workflow_run_id}`  
**Commit**：`{commit_sha[:7]}`  
**時間戳**：{timestamp}

---

### 🔍 問題診斷

**錯誤類型**：{error_type}

---

### 💡 修復建議

{fix_suggestions_text}

---

### ⚡ 快速修復命令

**檢查環境**
{quick_fix_section}

---

### 📊 錯誤摘要

```
{error_summary}
```

---

### 🤝 互動式客服

需要更多協助？使用以下命令：
- `@copilot analyze {ci_name}` - 深度分析此錯誤
- `@copilot fix {ci_name}` - 獲取自動修復建議
- `@copilot help {ci_name}` - 查看此 CI 的完整文檔
- `@copilot similar {ci_name}` - 查找相似問題的解決方案

---

### 📚 相關資源

- [CI 故障排除文檔](./docs/ci-troubleshooting.md)
- [{ci_name} 特定文檔](./docs/README.md)
- [環境檢查工具](./scripts/check-env.sh)

---

_此評論由 {ci_name} 互動式客服自動生成_
"""
    
    # Write to file for GitHub Action to read
    with open("comment_body.md", "w", encoding="utf-8") as f:
        f.write(comment_body)
    
    print("✅ Consolidated comment generated successfully")
    print(f"Status: {overall_status}")
    print(f"Jobs analyzed: {len(job_summaries)}")


if __name__ == "__main__":
    main()
