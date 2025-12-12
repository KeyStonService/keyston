# Recovery Playbook | 恢復操作手冊

**SynergyMesh Self-Healing Recovery System**

## 🎯 Quick Reference | 快速參考

### Emergency Contacts | 緊急聯絡

| Scenario                | Action                   | Command                                                  |
| ----------------------- | ------------------------ | -------------------------------------------------------- |
| Launcher crashed        | Auto-recovery by Phoenix | `python emergency_recovery.py`                           |
| Phoenix not responding  | Manual restart           | `python services/agents/recovery/phoenix_agent.py start` |
| Watchdog not running    | Start watchdog           | `python services/watchdog/system_watchdog.py start`      |
| Complete system failure | Emergency bootstrap      | `python emergency_recovery.py`                           |

## 🔥 Emergency Procedures | 緊急程序

### Level 1: Launcher Failure | 啟動器故障

**Automatic Response:**

1. Watchdog detects failure within 30s
2. Phoenix Agent triggered
3. Quick restart attempted
4. System restored

**Manual Override:**

```bash
# If automatic recovery fails
python emergency_recovery.py

# Or restart launcher manually
python automation_launcher.py start
```

### Level 2: Phoenix Agent Failure | Phoenix 代理故障

**Steps:**

1. Check if watchdog is running: `ps aux | grep system_watchdog`
2. Restart watchdog: `python services/watchdog/system_watchdog.py start`
3. Watchdog will restart Phoenix automatically
4. Verify: `tail -f .automation_logs/phoenix.log`

### Level 3: Complete System Failure | 完全系統故障

**Emergency Recovery:**

```bash
# Run emergency recovery system
python emergency_recovery.py

# This will:
# 1. Diagnose all components
# 2. Repair missing directories
# 3. Install missing dependencies
# 4. Restart services
# 5. Verify system health
```

## 📋 Recovery Strategies | 恢復策略

### Strategy 1: Quick Restart (30s)

**When:** First attempt, simple process crash

**Steps:**

1. Terminate failed process
2. Wait 5 seconds
3. Restart process
4. Verify startup
5. Monitor for 1 minute

**Command:**

```bash
# Manual execution
pkill -f automation_launcher.py
sleep 5
python automation_launcher.py start &
```

### Strategy 2: Safe Mode Restart (2m)

**When:** Configuration suspected, quick restart failed

**Steps:**

1. Backup current configuration
2. Load minimal configuration
3. Restart with safe settings
4. Verify basic functionality
5. Gradually restore features

**Files:**

- Backup: `.automation_logs/config_backup_TIMESTAMP.tar.gz`
- Minimal config: `config/minimal-config.yaml`

### Strategy 3: Configuration Rollback (5m)

**When:** Recent configuration change caused failure

**Steps:**

1. Identify last known good configuration
2. Stop all affected services
3. Restore previous configuration
4. Restart services
5. Full system verification

**Command:**

```bash
# Manual rollback
cp config/.backup/TIMESTAMP/synergymesh.yaml config/
python automation_launcher.py start
```

### Strategy 4: Dependency Restart (10m)

**When:** Service dependency issues

**Steps:**

1. Map service dependencies
2. Stop services in reverse dependency order
3. Restart in correct dependency order
4. Verify each service after start
5. Health check all services

### Strategy 5: Backup Restore (30m)

**When:** Data corruption, major failure

**Steps:**

1. Stop all services
2. Identify latest valid backup
3. Restore backup data
4. Verify data integrity
5. Restart all services
6. Full system verification

**Requires:** Human approval

### Strategy 6: Full System Bootstrap (2h)

**When:** All other strategies failed

**Steps:**

1. Emergency system shutdown
2. Run `emergency_recovery.py`
3. Bootstrap core components
4. Restore configurations from backup
5. Restart system incrementally
6. Comprehensive verification

**Requires:** Human approval

## 🔍 Diagnostic Procedures | 診斷程序

### Check System Health | 檢查系統健康

```bash
# Phoenix Agent status
python services/agents/recovery/phoenix_agent.py status

# Watchdog status
python services/watchdog/system_watchdog.py status

# Launcher status
python automation_launcher.py status

# Check all logs
tail -f .automation_logs/*.log
```

### Identify Failure Root Cause | 識別故障根本原因

1. **Check recent changes:**

   ```bash
   git log --oneline -10
   grep -r "ERROR" .automation_logs/
   ```

2. **Review incident history:**

   ```bash
   cat .automation_logs/incidents.log
   python -c "import json; print(json.dumps(json.load(open('.phoenix_state.json')), indent=2))"
   ```

3. **Analyze patterns:**
   - Frequency of failures
   - Time of day patterns
   - Component correlation
   - Resource usage trends

## 📊 Incident Response | 事件響應

### Incident Classification | 事件分類

| Level | Description         | Response Time | Escalation   |
| ----- | ------------------- | ------------- | ------------ |
| P1    | System down         | Immediate     | Auto + Human |
| P2    | Critical degraded   | < 5 min       | Auto         |
| P3    | Non-critical issues | < 30 min      | Auto         |
| P4    | Minor issues        | < 2 hours     | Log only     |

### Response Workflow | 響應工作流程

```
Incident Detected
    ↓
Phoenix Auto-Response (0-5 min)
    ↓
Success? → Yes → Monitor → Close
    ↓ No
Escalate to Level 3 (5-15 min)
    ↓
Manual Review Required? → No → Retry
    ↓ Yes
Page On-Call Engineer
    ↓
Human Intervention
    ↓
Resolution
    ↓
Post-Mortem
```

## 🛠️ Manual Intervention Procedures | 手動介入程序

### When to Intervene | 何時介入

1. Phoenix escalation level 4 or 5
2. Multiple recovery failures (>3 attempts)
3. Data integrity concerns
4. Security incidents
5. Manual request from stakeholders

### Intervention Steps | 介入步驟

1. **Assess Situation:**

   ```bash
   # Check Phoenix status
   python services/agents/recovery/phoenix_agent.py status

   # Review recent incidents
   tail -100 .automation_logs/incidents.log

   # Check system resources
   htop
   df -h
   ```

2. **Stabilize System:**

   ```bash
   # Stop auto-recovery temporarily
   pkill -f phoenix_agent.py

   # Stop problematic services
   pkill -f automation_launcher.py
   ```

3. **Diagnose:**
   - Review logs
   - Check configurations
   - Verify dependencies
   - Test components individually

4. **Fix:**
   - Apply manual fixes
   - Update configurations
   - Restore from backup if needed

5. **Verify:**
   - Start services one by one
   - Run health checks
   - Monitor for 30 minutes

6. **Resume Auto-Recovery:**

   ```bash
   python services/watchdog/system_watchdog.py start
   ```

7. **Document:**
   - Update incident report
   - Add to knowledge base
   - Update recovery procedures if needed

## 📝 Post-Incident Procedures | 事後程序

### Immediate (Within 1 hour) | 立即處理

1. Verify system stability
2. Document timeline of events
3. Identify immediate cause
4. Communicate status to stakeholders

### Short-term (Within 24 hours) | 短期處理

1. Detailed root cause analysis
2. Review Phoenix's response
3. Identify improvements
4. Update monitoring if needed

### Long-term (Within 1 week) | 長期處理

1. Conduct post-mortem meeting
2. Implement preventive measures
3. Update playbook with learnings
4. Train team on new procedures
5. Update Phoenix recovery strategies

## 🔐 Security Incident Response | 安全事件響應

### If Security Breach Suspected | 如果懷疑安全漏洞

1. **STOP** all auto-recovery
2. Isolate affected systems
3. Preserve evidence
4. Contact security team
5. Follow security incident procedures
6. Do NOT restart services until cleared

## 📚 Knowledge Base | 知識庫

### Common Issues | 常見問題

**Issue:** Launcher keeps crashing

- **Cause:** Memory leak or resource exhaustion
- **Solution:** Check resource usage, restart with clean state
- **Prevention:** Monitor memory usage, implement memory limits

**Issue:** Phoenix not detecting failures

- **Cause:** Health check interval too long
- **Solution:** Reduce `health_check_interval` in config
- **Prevention:** Verify monitoring configuration regularly

**Issue:** Configuration rollback fails

- **Cause:** No valid backup available
- **Solution:** Use emergency recovery, rebuild config
- **Prevention:** Ensure regular backups are created

### Recovery Success Patterns | 恢復成功模式

Based on historical data:

- Quick restart: 85% success rate
- Configuration rollback: 70% success rate
- Full bootstrap: 95% success rate (when reached)

## 🔄 Continuous Improvement | 持續改進

### Review Cycles | 審查週期

- **Daily:** Review incident logs
- **Weekly:** Analyze recovery patterns
- **Monthly:** Update recovery strategies
- **Quarterly:** Full system review

### Metrics to Track | 追蹤指標

1. Mean Time To Detect (MTTD)
2. Mean Time To Recover (MTTR)
3. Recovery success rate
4. Escalation frequency
5. Manual intervention rate

---

**Remember | 記住:** This playbook is a living document. Update it based on
actual incidents and learnings. Phoenix learns from every recovery - so should
we.

**Emergency Hotline | 緊急熱線:** `python emergency_recovery.py`
