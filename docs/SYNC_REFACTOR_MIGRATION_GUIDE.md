# Migration Guide: Sync & Refactor System Optimization

**For:** Developers & DevOps Engineers  
**Version:** 1.0.0  
**Date:** 2025-12-07

---

## Overview

This guide helps you migrate from the old sync/refactor system to the optimized
version.

## What Changed?

### Removed Files

| File                   | Status        | Action Required                               |
| ---------------------- | ------------- | --------------------------------------------- |
| `watch_sync_script.sh` | ❌ Deleted    | Use `scripts/sync/watch-and-sync.sh` directly |
| `post_commit_hook.sh`  | ⚠️ Deprecated | Disable to avoid conflicts with watch script  |

### New Files

| File                                 | Purpose                                   |
| ------------------------------------ | ----------------------------------------- |
| `config/sync-refactor-config.yaml`   | Unified configuration for sync & refactor |
| `docs/SYNC_REFACTOR_OPTIMIZATION.md` | Complete optimization documentation       |
| `.cache/refactor/`                   | Cache directory for playbook generation   |

### Modified Files

| File                                              | Changes                                        |
| ------------------------------------------------- | ---------------------------------------------- |
| `.github/workflows/08-sync-subdirs.yml`           | Added validation, metrics, integration trigger |
| `.github/workflows/update-refactor-playbooks.yml` | Added caching support, workflow_call           |
| `tools/generate-refactor-playbook.py`             | Added intelligent caching system               |

## Migration Steps

### Step 1: Update Local Repository

```bash
# Pull latest changes
git checkout copilot/optimize-project-sync-refactor
git pull origin copilot/optimize-project-sync-refactor

# Verify new config exists
ls -l config/sync-refactor-config.yaml
```

### Step 2: Disable Post-commit Hook (If Active)

```bash
# Check if post-commit hook exists
ls -l .git/hooks/post-commit

# If it exists, disable it
mv .git/hooks/post-commit .git/hooks/post-commit.disabled

# Or edit config to disable
# In config/sync-refactor-config.yaml:
# features:
#   post_commit_hook_enabled: false
```

**Why?** The post-commit hook can conflict with the watch script, causing
duplicate commits.

### Step 3: Update Script References

If you have any scripts or documentation referencing the old files:

**Replace:**

```bash
./watch_sync_script.sh
```

**With:**

```bash
./scripts/sync/watch-and-sync.sh --once
# or
./scripts/sync/watch-and-sync.sh --watch
```

### Step 4: Configure Cache (Optional)

Cache is enabled by default. To customize:

```bash
# Edit config
nano config/sync-refactor-config.yaml

# Find the cache section:
refactor:
  cache:
    enabled: true          # Set to false to disable
    directory: ".cache/refactor"
    ttl_hours: 24         # Adjust as needed
```

### Step 5: Test the New System

#### Test Sync Workflow

```bash
# Make a test change
echo "# Test" > test_sync.md

# Run sync once
./scripts/sync/watch-and-sync.sh --once

# Verify commit
git log -1
```

#### Test Refactor Generation

```bash
# Generate playbooks (should use cache after first run)
python3 tools/generate-refactor-playbook.py --repo-root .

# Check cache stats in output
# Look for: "📊 Stats: X generated, Y from cache"
```

#### Test Integration

```bash
# Make a governance file change
echo "# Test" >> governance/language-governance-report.md

# Commit and push
git add governance/language-governance-report.md
git commit -m "test: governance update"
git push

# Check GitHub Actions
# Sync workflow should auto-trigger refactor workflow
```

### Step 6: Clean Up Old Cache (If Exists)

```bash
# Remove old cache locations (if any)
rm -rf .git/sync-cache
rm -rf .git/refactor-cache

# New cache location is: .cache/refactor/
```

## Breaking Changes

### 1. Configuration Source

**Before:**

- Directories hardcoded in `scripts/sync/watch-and-sync.sh`
- Debounce time hardcoded

**After:**

- Everything configurable in `config/sync-refactor-config.yaml`
- Update config, not code

**Migration:** If you modified directories in the old script, now update:

```yaml
sync:
  monitored_directories:
    - 'core/'
    - 'your-custom-dir/'
```

### 2. Watch Script Usage

**Before:**

```bash
./watch_sync_script.sh
```

**After:**

```bash
./scripts/sync/watch-and-sync.sh --once   # One-time sync
./scripts/sync/watch-and-sync.sh --watch  # Continuous watch
```

### 3. Cache Location

**Before:**

- No caching (or undocumented cache)

**After:**

- Cache in `.cache/refactor/`
- Add to `.gitignore` if not already present

```bash
# Add to .gitignore
echo ".cache/" >> .gitignore
```

## Verification Checklist

After migration, verify:

- [ ] `config/sync-refactor-config.yaml` exists and is valid
- [ ] Post-commit hook disabled (if was active)
- [ ] Watch script works: `./scripts/sync/watch-and-sync.sh --once`
- [ ] Playbook generation works with caching
- [ ] GitHub Actions workflows pass
- [ ] Integration trigger works (governance → refactor)
- [ ] No conflicts or duplicate commits
- [ ] Cache directory excluded from git (`.gitignore`)

## Rollback Procedure

If you need to rollback to the old system:

```bash
# 1. Checkout previous commit
git checkout <previous-commit-hash>

# 2. Re-enable post-commit hook (if needed)
mv .git/hooks/post-commit.disabled .git/hooks/post-commit

# 3. Clear new cache
rm -rf .cache/refactor/

# 4. Notify team
```

**Note:** Rollback is not recommended as the new system has significant
improvements.

## Common Issues & Solutions

### Issue 1: "Config file not found"

**Symptom:**

```
⚠️ Could not load cache settings: [Errno 2] No such file or directory
```

**Solution:**

```bash
# Ensure you're on the correct branch
git checkout copilot/optimize-project-sync-refactor

# Ensure config exists
ls -l config/sync-refactor-config.yaml

# If missing, restore it
git restore config/sync-refactor-config.yaml
```

### Issue 2: Duplicate Commits

**Symptom:** Multiple commits for the same changes

**Solution:**

```bash
# Disable post-commit hook
mv .git/hooks/post-commit .git/hooks/post-commit.disabled

# Set in config
# features.post_commit_hook_enabled: false
```

### Issue 3: Cache Not Working

**Symptom:** "0% cache hit rate" every time

**Solution:**

```bash
# Check cache directory exists
ls -la .cache/refactor/

# Check cache is enabled
grep -A5 "cache:" config/sync-refactor-config.yaml

# Verify data source files exist
ls -l governance/language-governance-report.md
```

### Issue 4: Validation Blocking Commits

**Symptom:** "YAML validation failed"

**Solution:**

```bash
# Identify broken file
python3 -c "import yaml; yaml.safe_load(open('your-file.yaml'))"

# Fix syntax errors

# Or temporarily disable validation
# In config:
# sync:
#   validation:
#     enabled: false
```

### Issue 5: Integration Not Triggering

**Symptom:** Refactor workflow doesn't run after governance changes

**Solution:**

```bash
# Check config
grep -A10 "integration:" config/sync-refactor-config.yaml

# Ensure sync_triggers_refactor: true

# Check GitHub Actions permissions
# May need to enable workflow permissions in repo settings
```

## Performance Expectations

After migration, you should see:

- **Playbook generation:** 50-90% faster (with cache)
- **Sync workflow:** Similar or slightly faster
- **Developer experience:** Fewer failures, clearer errors
- **Maintenance:** 80% less configuration editing

## Support & Feedback

### Getting Help

1. **Documentation:**
   - [SYNC_REFACTOR_OPTIMIZATION.md](SYNC_REFACTOR_OPTIMIZATION.md)
   - [sync-refactor-config.yaml](../config/sync-refactor-config.yaml)

2. **Logs:**
   - GitHub Actions: Check workflow run logs
   - Local: `.git/watch-sync-log.txt`

3. **Team:**
   - DevOps team for workflow issues
   - Tech lead for configuration questions

### Reporting Issues

When reporting issues, include:

1. What you were trying to do
2. What happened (error messages, logs)
3. What you expected to happen
4. Your environment (OS, branch, config settings)
5. Steps to reproduce

### Providing Feedback

We want to know:

- What works well?
- What's confusing?
- What could be better?
- What features are missing?

---

**Migration Status:** In Progress  
**Target Completion:** 2025-12-10  
**Point of Contact:** DevOps Team

## Next Steps

After successful migration:

1. ✅ Mark this migration as complete
2. 📚 Update team documentation
3. 🎓 Schedule training session (optional)
4. 🔄 Monitor for issues
5. 📊 Collect performance metrics
6. 🎉 Celebrate the improvement!

---

**Last Updated:** 2025-12-07  
**Version:** 1.0.0  
**Status:** Ready for Use
