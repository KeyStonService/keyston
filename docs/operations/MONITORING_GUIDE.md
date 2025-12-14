# SynergyMesh 監控系統設定指引

# SynergyMesh Monitoring System Setup Guide

## 📋 文件目的 | Document Purpose

本文件提供詳細的監控系統部署指引與工作人員提示詞範本，確保 SynergyMesh 專案的關鍵目錄與檔案能被有效監控。

This document provides detailed monitoring system deployment guidelines and worker prompt templates to ensure effective monitoring of critical directories and files in the SynergyMesh project.

---

## 🎯 監控架構概覽 | Monitoring Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    監控層級 | Monitoring Layers              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   FIM        │  │   auditd     │  │   inotify    │      │
│  │  (基線監控)   │  │  (稽核日誌)   │  │  (即時測試)   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │     SIEM       │                        │
│                    │  (日誌聚合分析)  │                        │
│                    └───────┬────────┘                        │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │   Alerting     │                        │
│                    │  (告警與通知)    │                        │
│                    └────────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 部署方式一：FIM (File Integrity Monitoring)

### 什麼是 FIM？ | What is FIM?

FIM 透過建立檔案基線並定期比對，偵測未授權的檔案變更。適合用於靜態檔案監控。

FIM detects unauthorized file changes by creating file baselines and performing periodic comparisons. Suitable for static file monitoring.

### 支援工具 | Supported Tools

1. **OSSEC** - 開源 HIDS (Host-based Intrusion Detection System)
2. **Tripwire** - 商業/開源 FIM 工具
3. **AIDE** - Advanced Intrusion Detection Environment

---

### 📝 工作人員提示詞：部署 FIM 與建立基線

### Worker Prompt: Deploy FIM and Create Baseline

```
任務：部署 FIM 並建立基線

請在以下主機安裝並啟用 FIM 工具（建議使用 OSSEC 或 Tripwire）：
- 主機列表：[請列出目標主機名稱或 IP]

1. 安裝步驟：
   # OSSEC 安裝範例（Ubuntu/Debian）
   wget -q -O - https://updates.atomicorp.com/installers/atomic | sudo bash
   sudo apt-get install ossec-hids-server -y
   
   # 或 Tripwire 安裝範例
   sudo apt-get install tripwire -y

2. 建立基線監控清單，優先監控以下路徑：
   - /srv/repo/config
   - /srv/repo/core/contract_service
   - /srv/repo/advanced-system-src
   - /srv/repo/advanced-system-dist
   - /srv/repo/mcp-servers
   - /srv/repo/scripts
   - /srv/repo/.config/conftest/policies
   - /srv/repo/schemas

3. 設定雜湊演算法：
   - 建議使用：SHA-256
   - 備選方案：SHA-512

4. 執行首次基線掃描

5. 回報要求：
   - 安裝版本號
   - 已加入監控的完整路徑清單
   - 基線雜湊演算法
   - 基線檔案儲存位置
   - 測試變更的 alert 截圖或日誌片段

回報格式：
主機：[hostname/IP]
任務：安裝 FIM
執行指令：[實際執行的命令]
結果摘要：成功/失敗 + [重要日誌片段]
證據：[日誌行或截圖連結]
下一步建議：[例如：調整監控頻率、擴展監控範圍]
```

### FIM 設定範例 | FIM Configuration Example

#### OSSEC 設定檔範例 (`/var/ossec/etc/ossec.conf`)

```xml
<ossec_config>
  <syscheck>
    <!-- 設定掃描頻率：每 6 小時 -->
    <frequency>21600</frequency>
    
    <!-- 監控目錄設定 -->
    <directories check_all="yes" realtime="yes" report_changes="yes">
      /srv/repo/config
    </directories>
    <directories check_all="yes" realtime="yes" report_changes="yes">
      /srv/repo/core/contract_service
    </directories>
    <directories check_all="yes" realtime="yes" report_changes="yes">
      /srv/repo/advanced-system-src
    </directories>
    <directories check_all="yes" realtime="yes" report_changes="yes">
      /srv/repo/mcp-servers
    </directories>
    <directories check_all="yes" realtime="yes" report_changes="yes">
      /srv/repo/scripts
    </directories>
    
    <!-- 忽略特定檔案類型 -->
    <ignore>/srv/repo/node_modules</ignore>
    <ignore>/srv/repo/.git</ignore>
    <ignore type="sregex">\.log$|\.tmp$</ignore>
  </syscheck>
</ossec_config>
```

---

## 🔧 部署方式二：auditd (Linux Audit Daemon)

### 什麼是 auditd？ | What is auditd?

auditd 是 Linux 核心層級的稽核工具，能記錄所有檔案存取與系統呼叫，提供更細緻的追蹤能力。

auditd is a kernel-level Linux audit tool that records all file access and system calls, providing more granular tracking capabilities.

---

### 📝 工作人員提示詞：啟用 auditd 規則並驗證日誌上報

### Worker Prompt: Enable auditd Rules and Verify Log Forwarding

```
任務：設定 auditd 規則並驗證日誌上報

請在目標主機執行以下操作：

1. 確認 auditd 已安裝並執行：
   sudo systemctl status auditd

2. 新增監控規則：
   # 監控 config 目錄的寫入與屬性變更
   sudo auditctl -w /srv/repo/config -p wa -k repoconfig_watch
   
   # 監控 scripts 目錄
   sudo auditctl -w /srv/repo/scripts -p wa -k reposcripts_watch
   
   # 監控核心程式碼目錄
   sudo auditctl -w /srv/repo/core/contract_service -p wa -k repocore_watch
   
   # 監控進階系統原始碼
   sudo auditctl -w /srv/repo/advanced-system-src -p wa -k reposrc_watch
   
   # 監控 MCP servers
   sudo auditctl -w /srv/repo/mcp-servers -p wa -k repomcp_watch
   
   # 監控政策檔案
   sudo auditctl -w /srv/repo/.config/conftest/policies -p wa -k repopolicy_watch
   
   # 監控 schemas
   sudo auditctl -w /srv/repo/schemas -p wa -k reposchema_watch

3. 將規則永久保存到設定檔（以便重啟後保留）：
   # 方法 1：手動寫入規則檔案
   sudo tee /etc/audit/rules.d/synergymesh-monitoring.rules << 'EOF'
   -w /srv/repo/config -p wa -k repoconfig_watch
   -w /srv/repo/scripts -p wa -k reposcripts_watch
   -w /srv/repo/core/contract_service -p wa -k repocore_watch
   -w /srv/repo/advanced-system-src -p wa -k reposrc_watch
   -w /srv/repo/mcp-servers -p wa -k repomcp_watch
   -w /srv/repo/.config/conftest/policies -p wa -k repopolicy_watch
   -w /srv/repo/schemas -p wa -k reposchema_watch
   EOF
   
   # 方法 2：備份當前規則到檔案
   sudo sh -c 'auditctl -l > /etc/audit/rules.d/synergymesh-monitoring-backup.txt'

4. 重啟 auditd：
   sudo service auditd restart

5. 驗證規則已生效：
   sudo auditctl -l | grep repo

6. 測試觸發 alert：
   touch /srv/repo/config/test-change-$(date +%s)
   sudo ausearch -k repoconfig_watch -ts recent

7. 確認 Filebeat/Fluentd 或其他 agent 已將日誌送到 SIEM

回報要求：
- 主機資訊
- auditd 版本
- 已新增的規則清單
- /var/log/audit/audit.log 範例日誌行
- SIEM 事件 ID 或範例事件
- 測試變更的稽核日誌輸出

回報格式：
主機：[hostname/IP]
任務：設定 auditd 規則
執行指令：[實際執行的命令]
結果摘要：成功/失敗 + [重要日誌片段]
證據：[SIEM 事件 ID 或日誌行]
下一步建議：[例如：調整規則敏感度、新增更多路徑]
```

### auditd 規則說明 | auditd Rule Explanation

```bash
# 規則格式：
# auditctl -w <path> -p <permissions> -k <key_name>

# 參數說明：
# -w : 監控的路徑
# -p : 監控的操作類型
#      r = read (讀取)
#      w = write (寫入)
#      x = execute (執行)
#      a = attribute change (屬性變更)
# -k : 關鍵字標籤（用於搜尋與分類）
```

### 查詢 auditd 日誌 | Querying auditd Logs

```bash
# 查詢特定 key 的事件
sudo ausearch -k repoconfig_watch

# 查詢特定時間範圍
sudo ausearch -k repoconfig_watch -ts 10:00 -te 11:00

# 查詢特定使用者的操作
sudo ausearch -ua developer123 -k repoconfig_watch

# 產生統計報告
sudo aureport -f -i

# 查詢特定檔案的變更歷史
sudo ausearch -f /srv/repo/config/prometheus-config.yml
```

---

## 🔧 部署方式三：inotify (即時監控測試)

### 什麼是 inotify？ | What is inotify?

inotify 是 Linux 核心的檔案系統事件監控機制，能提供即時的檔案變更通知。適合用於開發與測試環境的快速驗證。

inotify is a Linux kernel filesystem event monitoring mechanism that provides real-time file change notifications. Suitable for quick validation in development and testing environments.

---

### 📝 工作人員提示詞：使用 inotify 做即時測試

### Worker Prompt: Real-time Testing with inotify

```
任務：使用 inotify 進行即時監控測試

這是臨時驗證用途，確認檔案變更能被正確偵測：

1. 安裝 inotify-tools：
   # Ubuntu/Debian
   sudo apt-get install inotify-tools -y
   
   # CentOS/RHEL
   sudo yum install inotify-tools -y

2. 監看單一目錄的即時事件（開啟終端機 1）：
   inotifywait -m -r -e modify,create,delete,move /srv/repo/config

3. 在另一個終端機執行測試變更（終端機 2）：
   touch /srv/repo/config/test-change-$(date +%s)
   echo "test content" >> /srv/repo/config/test-file.txt
   rm /srv/repo/config/test-file.txt

4. 觀察終端機 1 的輸出，應該能看到即時事件

5. 驗證 SIEM 是否收到相同事件（可能有延遲）

回報要求：
- inotifywait 輸出截圖或文字
- 測試變更的時間戳記
- SIEM 中對應事件的時間戳記與內容
- 事件延遲時間（從變更發生到 SIEM 收到）

回報格式：
主機：[hostname/IP]
任務：inotify 即時監控測試
執行指令：[實際執行的命令]
結果摘要：成功/失敗 + [inotify 輸出]
證據：[截圖或日誌]
下一步建議：[例如：調整 SIEM 收集延遲、增加緩衝區大小]
```

### inotify 進階用法 | Advanced inotify Usage

```bash
# 監控多個事件類型
inotifywait -m -r \
  -e modify,create,delete,move,attrib \
  /srv/repo/config /srv/repo/scripts

# 輸出到日誌檔案
inotifywait -m -r -o /var/log/inotify-monitor.log \
  -e modify,create,delete \
  /srv/repo/config

# 使用 --format 自訂輸出格式
inotifywait -m -r --format '%T %w%f %e' --timefmt '%Y-%m-%d %H:%M:%S' \
  /srv/repo/config

# 結合其他工具處理事件
inotifywait -m -r /srv/repo/config | while read path action file; do
    echo "$(date): $action on $path$file"
    # 可以在這裡加入自訂處理邏輯
done
```

---

## 🔧 部署方式四：SIEM 整合與自動化

### SIEM 角色 | SIEM Role

SIEM 負責聚合來自各監控工具的日誌，執行關聯分析，並觸發自動化回應。

SIEM aggregates logs from various monitoring tools, performs correlation analysis, and triggers automated responses.

---

### 📝 工作人員提示詞：SIEM 規則與自動化 Playbook

### Worker Prompt: SIEM Rules and Automation Playbook

```
任務：在 SIEM 建立關聯規則與自動化 playbook

請依照以下步驟設定 SIEM 自動化回應：

1. 建立關聯規則（Correlation Rule）：
   名稱：SynergyMesh Repo Unauthorized Change
   
   觸發條件：
   - 事件來源：FIM alert 或 auditd (key: repo*_watch)
   - 觸發者帳號：不在白名單中
   - 變更路徑：監控目錄列表
   - 變更類型：modify, delete, permission
   
   白名單帳號範例：
   - jenkins-deploy
   - github-actions
   - approved-devops-team

2. 執行 Playbook 步驟：
   
   步驟 1：隔離主機
   - 將該主機標記為 quarantine
   - 更新防火牆規則，限制該主機的網路存取
   
   步驟 2：暫停帳號
   - 暫時停用觸發 alert 的帳號
   - 撤銷該帳號的 SSH 金鑰
   
   步驟 3：通知相關人員
   - 發送通知到 Slack #security-alerts
   - 發送郵件給 security@synergymesh.example.com
   - 觸發 PagerDuty alert（如為高嚴重性）
   
   步驟 4：收集證據
   - 收集完整稽核日誌
   - 擷取變更前後的檔案內容差異
   - 記錄帳號最近的所有活動
   
   步驟 5：建立事件工單
   - 在 ITSM 系統建立事件工單
   - 包含：時間、帳號、變更路徑、變更內容

3. 測試 Playbook：
   - 在測試環境模擬未授權變更
   - 驗證每個步驟都正確執行
   - 確認通知有正確發送

回報要求：
- SIEM 規則 ID 與名稱
- Playbook 步驟詳細說明
- 測試結果（包含截圖或日誌）
- 白名單帳號清單
- 通知渠道設定狀態

回報格式：
主機：[SIEM hostname/IP]
任務：建立 SIEM 規則與 playbook
執行指令：[實際設定的規則與 playbook]
結果摘要：成功/失敗 + [測試結果]
證據：[SIEM 規則 ID、測試截圖]
下一步建議：[例如：調整閾值、新增更多條件]
```

### SIEM 查詢範例 | SIEM Query Examples

#### Splunk 查詢語法

```spl
# 查詢所有 repo 監控事件
index=linux_audit key=repo*_watch

# 查詢非白名單帳號的變更
index=linux_audit key=repo*_watch
| search NOT [| inputlookup whitelist_accounts.csv | fields user | format]

# 統計每個目錄的變更次數
index=linux_audit key=repo*_watch
| stats count by file_path
| sort -count

# 查詢特定時間範圍的異常變更
index=linux_audit key=repo*_watch earliest=-24h
| where hour >= 22 OR hour <= 6  # 非工作時間
```

#### ELK 查詢語法 (Kibana)

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "key": "repo*_watch" } }
      ],
      "must_not": [
        { "terms": { "user": ["jenkins-deploy", "github-actions"] } }
      ],
      "filter": [
        { "range": { "@timestamp": { "gte": "now-24h" } } }
      ]
    }
  }
}
```

---

## 📊 監控儀表板設計 | Monitoring Dashboard Design

### 建議的儀表板元件 | Recommended Dashboard Components

1. **即時事件流** (Real-time Event Stream)
   - 最近 100 筆檔案變更事件
   - 顏色標示風險等級

2. **變更統計圖表** (Change Statistics)
   - 每日變更次數趨勢圖
   - 每個目錄的變更分佈圓餅圖
   - 每個使用者的變更次數長條圖

3. **異常告警** (Anomaly Alerts)
   - 未授權帳號的變更
   - 非工作時間的批次變更
   - 短時間內大量變更

4. **合規狀態** (Compliance Status)
   - 基線驗證狀態
   - 政策違規事件數量
   - 待審核的變更清單

---

## 📝 工作人員提示詞：建立參照文件

### Worker Prompt: Create Reference Documentation

```
任務：建立 repo 參照庫 README 與 CHANGELOG

請在專案根目錄建立或更新以下檔案：

1. ROOT_README.md
   包含內容：
   - 可信基線說明（什麼是基線、如何建立、如何更新）
   - 變更流程（誰可以變更、需要幾位 reviewer、審核標準）
   - 緊急聯絡人清單（資安團隊、DevOps、On-call）
   - 監控目錄清單與風險等級
   - 異常行為偵測規則

2. CHANGELOG.md
   格式範例：
   YYYY-MM-DD | username | path | change_type | reason
   
   範例記錄：
   2025-11-24 | john.doe | config/prometheus-config.yml | modify | Update retention policy
   2025-11-24 | jane.smith | scripts/build-matrix.sh | add | Add new build target for ARM64

3. 完成後執行 git 操作：
   git add ROOT_README.md CHANGELOG.md
   git commit -m "docs: Add monitoring reference documentation"
   git push origin main

回報要求：
- 檔案建立的 commit hash
- 檔案的 GitHub 連結
- 檔案內容摘要

回報格式：
主機：本地開發環境
任務：建立 ROOT_README 與 CHANGELOG
執行指令：[git 命令]
結果摘要：成功/失敗
證據：[commit hash 與 GitHub 連結]
下一步建議：[例如：設定 pre-commit hook 自動驗證 CHANGELOG 格式]
```

---

## 🔄 短期優先行動清單 | Short-term Priority Action List

以下行動項目可直接分派給工作人員：

The following action items can be directly assigned to workers:

### 1. 建立參照文件 (Documentation)

- **負責人**: Ops Team / Technical Writer
- **時程**: 1-2 天
- **產出**: ROOT_README.md, CHANGELOG.md, MONITORING_GUIDE.md

### 2. 部署 FIM Agent (FIM Deployment)

- **負責人**: Infrastructure Team
- **目標主機**: 3-5 台關鍵主機（production, staging）
- **時程**: 3-5 天
- **產出**: FIM 安裝報告、基線檔案

### 3. 設定 auditd 規則 (auditd Configuration)

- **負責人**: SecOps Team
- **目標主機**: 所有主機
- **時程**: 2-3 天
- **產出**: auditd 規則清單、測試日誌

### 4. SIEM 整合與規則建立 (SIEM Integration)

- **負責人**: SecOps Team
- **時程**: 5-7 天
- **產出**: SIEM 規則 ID、Playbook 文件、測試報告

### 5. 代理/智能體上線演練 (Agent Onboarding Drill)

- **負責人**: SRE Team
- **時程**: 1 天
- **產出**: 演練報告、流程改進建議

---

## 📋 回報格式範本 | Report Format Template

所有工作人員的回報應遵循以下統一格式：

All worker reports should follow this unified format:

```
═══════════════════════════════════════════════════
任務回報 | Task Report
═══════════════════════════════════════════════════

主機 | Host：
  [hostname 或 IP address]

任務 | Task：
  [任務簡述，例如：安裝 FIM、設定 auditd、建立 SIEM 規則]

執行時間 | Execution Time：
  開始：[YYYY-MM-DD HH:MM:SS]
  結束：[YYYY-MM-DD HH:MM:SS]
  耗時：[duration]

執行指令 | Commands Executed：
  [貼上實際執行的命令，每行一個]
  
  例如：
  sudo apt-get install ossec-hids-server -y
  sudo systemctl start ossec
  sudo systemctl enable ossec

結果摘要 | Result Summary：
  狀態：✅ 成功 / ❌ 失敗 / ⚠️ 部分成功
  
  [簡述執行結果，包含關鍵輸出或錯誤訊息]

證據 | Evidence：
  - 日誌檔案：[路徑或片段]
  - SIEM 事件 ID：[ID]
  - Commit Hash：[hash]
  - 截圖連結：[URL]
  - 其他證據：[說明]

遭遇問題 | Issues Encountered：
  [如有問題，詳細描述]
  [如無問題，填寫：無]

解決方案 | Solutions Applied：
  [如有問題，說明如何解決]
  [如無問題，填寫：不適用]

下一步建議 | Next Steps Recommendations：
  1. [建議項目 1]
  2. [建議項目 2]
  3. [建議項目 3]

回報人 | Reporter：
  [姓名 或 帳號]

回報時間 | Report Time：
  [YYYY-MM-DD HH:MM:SS]

═══════════════════════════════════════════════════
```

---

## 🔐 安全注意事項 | Security Considerations

### 日誌安全 | Log Security

1. **敏感資訊過濾**: 確保日誌不包含密碼、API 金鑰等敏感資訊
2. **日誌加密**: 傳輸過程使用 TLS，儲存時考慮加密
3. **存取控制**: 限制誰可以查看稽核日誌
4. **保留期限**: 遵循法規要求的日誌保留期限（通常 1-2 年）

### 監控工具本身的安全 | Security of Monitoring Tools

1. **權限最小化**: 監控工具只需要唯讀權限
2. **獨立帳號**: 使用專用的服務帳號，避免與一般使用者混用
3. **定期更新**: 保持監控工具為最新版本，修補已知漏洞
4. **監控監控者**: 對監控工具本身的設定變更也要記錄

---

## 📚 相關資源與參考文件 | Related Resources

### 內部文件 | Internal Documentation

- [ROOT_README.md](./ROOT_README.md) - 監控系統參照文件
- [CHANGELOG.md](./CHANGELOG.md) - 變更記錄
- [SECURITY.md](./SECURITY.md) - 安全政策

### 外部參考 | External References

- [OSSEC Documentation](https://www.ossec.net/docs/)
- [Linux Audit Documentation](https://linux-audit.com/)
- [inotify Man Page](https://man7.org/linux/man-pages/man7/inotify.7.html)
- [NIST SP 800-92: Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [CIS Controls: Log Management](https://www.cisecurity.org/controls/)

---

## 🔄 文件維護 | Document Maintenance

### 版本歷史 | Version History

- **v1.0** (Initial Release): 初始版本，包含 FIM、auditd、inotify、SIEM 整合指引

### 預計更新 | Planned Updates

- 新增容器環境監控指引（Docker, Kubernetes）
- 新增雲端環境整合（AWS CloudTrail, Azure Monitor）
- 新增自動化腳本範例
- 新增監控儀表板模板

---

**維護者 | Maintainer**: SynergyMesh Team  
**最後更新 | Last Updated**: [Document Creation Date]  
**版本 | Version**: 1.0
