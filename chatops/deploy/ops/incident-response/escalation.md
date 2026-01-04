# 事件升級流程

## 升級矩陣

```
時間線                 P0          P1          P2          P3
─────────────────────────────────────────────────────────────
0-15 分鐘             On-Call     On-Call     -           -
15-30 分鐘            Tech Lead   On-Call     On-Call     -
30-60 分鐘            Eng Manager Tech Lead   On-Call     On-Call
1-2 小時              Director    Eng Manager Tech Lead   On-Call
2+ 小時               VP/CTO      Director    Eng Manager Tech Lead
```

## 聯繫人列表

### 一級響應 (On-Call)
- **值班工程師**: 查看 PagerDuty
- **Slack**: #chatops-oncall
- **電話**: 參考 PagerDuty 輪值表

### 二級響應 (Tech Lead)
| 領域 | 負責人 | Slack |
|------|--------|-------|
| Platform | @platform-lead | #platform-team |
| Backend | @backend-lead | #backend-team |
| Frontend | @frontend-lead | #frontend-team |
| Infra | @infra-lead | #infra-team |
| Security | @security-lead | #security-team |

### 三級響應 (Management)
| 角色 | 聯繫方式 |
|------|----------|
| Engineering Manager | @eng-manager |
| Director of Engineering | @eng-director |
| VP of Engineering | @vp-eng |
| CTO | @cto |

## 升級觸發條件

### 自動升級
1. **無響應**: On-Call 15 分鐘未響應
2. **超時**: 事件超出預期恢復時間
3. **擴大**: 影響範圍持續擴大

### 手動升級
1. 需要跨團隊協調
2. 需要外部供應商介入
3. 需要業務決策
4. 發現安全問題

## 升級流程

### Step 1: 評估升級必要性
```
□ 當前資源是否足夠？
□ 是否需要額外專業知識？
□ 是否需要管理層決策？
□ 客戶影響是否需要溝通？
```

### Step 2: 發起升級
1. 在 Slack #chatops-incidents 發布升級通知
2. 使用模板:
   ```
   🔺 ESCALATION
   Incident: [INC-XXXX]
   Current Severity: [P0/P1/P2/P3]
   Escalating to: [@person or @team]
   Reason: [簡述原因]
   Current Status: [當前狀態]
   ```

### Step 3: 升級後行動
1. 確認升級對象已收到通知
2. 進行正式交接
3. 更新事件文檔
4. 繼續監控和協助

## 升級通知模板

### PagerDuty 升級
```
Subject: [P0/P1] Escalation - [Brief Description]

Incident ID: INC-XXXX
Started: YYYY-MM-DD HH:MM UTC
Duration: X hours Y minutes
Current Status: [Investigating/Mitigating/Resolved]

Impact:
- Users affected: X
- Services affected: [list]
- Business impact: [description]

Current Actions:
- [Action 1]
- [Action 2]

Escalation Reason:
[Why escalating]

Immediate Needs:
- [Need 1]
- [Need 2]
```

### Slack 升級
```
🚨 *INCIDENT ESCALATION*

*Incident:* INC-XXXX
*Severity:* P0/P1/P2/P3
*Status:* Investigating/Mitigating

*Escalating to:* @person
*Reason:* [簡述]

*Current Bridge:* [Zoom/Meet link]
*War Room:* #inc-xxxx-warroom
```

## De-Escalation (降級)

### 降級條件
- 服務已恢復穩定
- 根本原因已確定
- 剩餘工作為非緊急
- 可轉為正常工作流程

### 降級流程
1. 確認穩定至少 30 分鐘
2. 通知所有相關方
3. 更新事件狀態
4. 安排後續 Post-Mortem
