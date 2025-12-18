# Task Scheduler Service

Advanced task scheduler with cron-like capabilities for the Unmanned Island System.

## Features

- ✅ Cron expression support (standard + extended)
- ✅ One-time scheduled tasks
- ✅ Recurring tasks with intervals
- ✅ Job dependencies and chaining
- ✅ Timezone support
- ✅ Job prioritization
- ✅ Concurrent job execution limits
- ✅ Job timeout configuration
- ✅ Automatic retry on failure
- ✅ Job execution history
- ✅ Real-time job monitoring

## Installation

```bash
npm install
```

## Configuration

Environment variables:

```env
REDIS_HOST=localhost
REDIS_PORT=6379
MAX_CONCURRENT_JOBS=10
JOB_TIMEOUT=300000
HISTORY_RETENTION_DAYS=90
```

## Cron Expression Examples

```
* * * * *      # Every minute
0 * * * *      # Every hour
30 2 * * *     # Every day at 2:30 AM
0 9 * * 1      # Every Monday at 9:00 AM
*/15 * * * *   # Every 15 minutes
0 0 1 * *      # First day of every month
```

## License

MIT
