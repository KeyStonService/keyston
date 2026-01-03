# Quick Start: Autonomous Cleanup Toolkit | 快速入門：自主清理工具包

**5分鐘讓儲存庫擁有 Claude Code 的清理能力**
**Give your repository Claude Code cleanup capabilities in 5 minutes**

---

## 🚀 Instant Start | 立即開始

### Option 1: One-Command Full Analysis | 一鍵完整分析

```bash
# Run comprehensive analysis (dry-run, safe)
./tools/run_full_cleanup.sh

# Review the reports, then execute cleanups
./tools/run_full_cleanup.sh --execute
```

### Option 2: Individual Tools | 個別工具

```bash
# 1. Find duplicates
python tools/find_duplicate_scripts.py

# 2. Scan technical debt
python tools/scan_tech_debt.py

# 3. Verify P0 safety
python tools/verify_p0_safety.py

# 4. Generate comprehensive report
python tools/autonomous_cleanup_toolkit.py analyze
```

---

## 📋 What You Get | 你會得到什麼

After running the toolkit, you'll have:

### 1. Duplicate Analysis

- File: `duplicate_analysis.txt`
- Shows: All duplicate files grouped by content (MD5)
- Action: Review and run `cleanup_duplicates.py --execute` to remove

### 2. Technical Debt Report

- File: `TECH_DEBT_SCAN_REPORT.json`
- Shows: TODOs, FIXMEs, complex functions
- Action: Prioritize and implement based on severity

### 3. P0 Safety Report

- File: `P0_SAFETY_VERIFICATION_REPORT.json`
- Shows: Critical safety mechanism status
- Action: Fix any failing checks immediately

### 4. Cleanup Analysis

- File: `.automation_logs/cleanup_analysis_TIMESTAMP.json`
- Shows: Comprehensive metrics and recommendations
- Action: Use as roadmap for ongoing cleanup

---

## 🎯 Common Workflows | 常見工作流程

### Workflow 1: Weekly Cleanup | 每週清理

```bash
# Monday morning routine
./tools/run_full_cleanup.sh > weekly_report.txt

# Review report
cat weekly_report.txt

# Execute safe cleanups
python tools/cleanup_duplicates.py --execute

# Commit improvements
git add -A
git commit -m "chore: weekly automated cleanup"
git push
```

### Workflow 2: Pre-Release Audit | 發布前審查

```bash
# Complete technical debt audit
python tools/scan_tech_debt.py

# Verify safety
python tools/verify_p0_safety.py

# Check for critical TODOs
grep -r "TODO.*critical" --include="*.py"

# Generate release report
python tools/autonomous_cleanup_toolkit.py report \
    --output RELEASE_CLEANUP_REPORT.json
```

### Workflow 3: Continuous Monitoring | 持續監控

```bash
# Add to CI/CD pipeline (.github/workflows/cleanup.yml)
name: Tech Debt Monitoring
on: [push, pull_request]

jobs:
  debt-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Scan Technical Debt
        run: python tools/scan_tech_debt.py
      - name: Check Duplicates
        run: python tools/find_duplicate_scripts.py
      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: cleanup-reports
          path: "*_REPORT.json"
```

---

## 🛠️ Tool Reference | 工具參考

### autonomous_cleanup_toolkit.py

**Purpose**: Main orchestrator, comprehensive analysis

**Commands**:

```bash
# Full analysis
python tools/autonomous_cleanup_toolkit.py analyze

# Generate report only
python tools/autonomous_cleanup_toolkit.py report

# Execute cleanup (future capability)
python tools/autonomous_cleanup_toolkit.py cleanup --phase duplicates
```

**Output**: JSON report with all metrics

### find_duplicate_scripts.py

**Purpose**: Detect duplicate files via MD5 hashing

**Logic**:

- Scans .py, .sh, .js, .ts files
- Computes MD5 hash of contents
- Groups by hash
- Suggests removable duplicates

**Output**: Console summary + groups listed

### cleanup_duplicates.py

**Purpose**: Safe duplicate file removal

**Strategies**:

1. Remove legacy/ copies
2. Remove agent/ when services/agents/ exists
3. Remove empty **init**.py duplicates

**Usage**:

```bash
# Dry run (default)
python tools/cleanup_duplicates.py

# Execute (with confirmation)
python tools/cleanup_duplicates.py --execute
```

### scan_tech_debt.py

**Purpose**: Technical debt inventory

**Scans For**:

- TODO comments
- FIXME comments
- HACK comments
- DEPRECATED markers
- Complex functions (>100 lines)

**Output**: `TECH_DEBT_SCAN_REPORT.json`

### verify_p0_safety.py

**Purpose**: Critical safety verification

**Checks**:

- Emergency stop mechanisms
- Safety configurations
- Monitoring setup
- Test coverage (80% target)
- CI/CD workflows

**Output**: `P0_SAFETY_VERIFICATION_REPORT.json`

---

## 📊 Understanding Reports | 理解報告

### Duplicate Analysis Format

```
Group 1: 3 files (MD5: abc123...)
  - legacy/old_script.py
  - agent/script.py
  → services/agents/script.py (canonical)

Removable: 2 files
```

**Action**: Remove first 2, keep canonical version

### Tech Debt Report Structure

```json
{
  "summary": {
    "total_debt_items": 690,
    "by_category": {
      "high_complexity": 619,
      "todos": 60,
      "fixmes": 5,
      "deprecated": 6
    },
    "by_severity": {
      "HIGH": 30,
      "MEDIUM": 250,
      "LOW": 410
    }
  },
  "items": [...]
}
```

**Action**: Focus on HIGH severity first

### P0 Safety Report Format

```json
{
  "checks": [
    {
      "name": "emergency_stop",
      "status": "PASS",
      "evidence": ["Path: config/safety-mechanisms.yaml"]
    }
  ],
  "summary": {
    "total_checks": 5,
    "passed": 5,
    "failed": 0
  }
}
```

**Action**: Fix any failed checks immediately

---

## 🔄 Integration with Development | 與開發流程整合

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run quick cleanup checks before commit

echo "🔍 Running cleanup checks..."

# Check for new TODOs (warn only)
NEW_TODOS=$(git diff --cached | grep -c "+.*TODO" || true)
if [ "$NEW_TODOS" -gt 0 ]; then
    echo "⚠️  Warning: $NEW_TODOS new TODO(s) added"
fi

# Check for NotImplementedError (block)
NEW_NOT_IMPL=$(git diff --cached | grep -c "+.*NotImplementedError" || true)
if [ "$NEW_NOT_IMPL" -gt 0 ]; then
    echo "❌ Error: New NotImplementedError found"
    echo "   Please implement or use graceful degradation"
    exit 1
fi

echo "✅ Checks passed"
```

### GitHub Actions Workflow

`.github/workflows/tech-debt.yml`:

```yaml
name: Technical Debt Monitoring

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Run Tech Debt Scan
        run: python tools/scan_tech_debt.py

      - name: Check Duplicates
        run: python tools/find_duplicate_scripts.py

      - name: Verify P0 Safety
        run: python tools/verify_p0_safety.py

      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: cleanup-reports
          path: '*_REPORT.json'

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('TECH_DEBT_SCAN_REPORT.json'));
            const summary = report.summary;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 📊 Technical Debt Report\n\n- Total Items: ${summary.total_debt_items}\n- HIGH Severity: ${summary.by_severity.HIGH}\n- MEDIUM Severity: ${summary.by_severity.MEDIUM}`
            });
```

---

## 💡 Tips & Best Practices | 提示與最佳實踐

### 1. Start with Analysis | 從分析開始

```bash
# Always run analysis first (safe, no changes)
./tools/run_full_cleanup.sh
```

### 2. Review Before Execute | 執行前審查

```bash
# Review what will be removed
python tools/cleanup_duplicates.py
# Then execute after confirmation
python tools/cleanup_duplicates.py --execute
```

### 3. Track Progress | 追蹤進度

```bash
# Save reports for comparison
cp TECH_DEBT_SCAN_REPORT.json reports/$(date +%Y%m%d)_debt.json
```

### 4. Automate Regular Scans | 自動化定期掃描

```bash
# Add to crontab (weekly Monday 9 AM)
0 9 * * 1 cd /path/to/repo && ./tools/run_full_cleanup.sh --auto
```

### 5. Integrate with PR Reviews | 整合到 PR 審查

```bash
# In PR description, include:
- [ ] Ran cleanup scan: `./tools/run_full_cleanup.sh`
- [ ] No new HIGH severity TODOs added
- [ ] P0 safety checks pass
```

---

## 🐛 Troubleshooting | 故障排除

### Issue: Permission Denied

```bash
chmod +x tools/run_full_cleanup.sh
chmod +x tools/*.py
```

### Issue: Python Module Not Found

```bash
pip install -r requirements.txt
# Or for specific tools:
pip install psutil pyyaml
```

### Issue: No Duplicates Found (But They Exist)

- Check excluded directories in `find_duplicate_scripts.py`
- Verify file extensions are included
- Check if files are actually identical (MD5 must match)

### Issue: Report Not Generated

```bash
# Check logs
tail -f .automation_logs/autonomous_cleanup.log

# Ensure write permissions
chmod 755 .automation_logs
```

---

## 📚 Learn More | 了解更多

- **Full Capabilities**: See `AUTONOMOUS_CAPABILITIES.md`
- **Session Summary**: See `SESSION_CONTINUATION_SUMMARY.md`
- **Phase Reports**: See `PHASE_1_6_COMPLETION_REPORT.md`

---

## ✅ Quick Verification | 快速驗證

Test that everything works:

```bash
# 1. Check tools exist
ls tools/*.py tools/*.sh

# 2. Run analysis (safe)
./tools/run_full_cleanup.sh

# 3. Verify reports generated
ls *_REPORT.json .automation_logs/

# 4. Success!
echo "✅ Autonomous toolkit is ready!"
```

---

**Ready to clean your repository like Claude Code does! 🚀**

**Generated**: 2025-12-16
**Version**: 1.0.0
