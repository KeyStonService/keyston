# System Watchdog | 系統看門狗

Independent monitoring service that watches critical processes and triggers Phoenix Agent when needed.

## Files

- `system_watchdog.py` - Watchdog service implementation
- `__init__.py` - Module initialization

## Usage

```bash
# Start watchdog
python system_watchdog.py start

# Check status
python system_watchdog.py status

# Stop watchdog
python system_watchdog.py stop
```

## Features

- Monitors automation_launcher.py every 30 seconds
- Checks heartbeats (90 second timeout)
- Triggers Phoenix Agent on failures
- Automatic process restart (up to 5 attempts)
- Cannot be disabled by launcher
- Independent process lifecycle

## Documentation

See:

- `docs/IMPROVED_ARCHITECTURE.md` - System architecture
- `docs/RECOVERY_PLAYBOOK.md` - Recovery procedures
- `config/recovery-system.yaml` - Configuration
